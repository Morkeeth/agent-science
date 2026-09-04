"""Explicit update runs for followed questions.

Ranks changes by effect on saved conclusions and decisions — not by title or
raw URL count. Snapshot reuse does not claim the web was checked; only actual
fetches advance `checked_online`. A meaningful empty result is a feature.
"""
from __future__ import annotations

from contextlib import closing
import copy
import json
import uuid

from clearance import cases, follow, research

# Effect ranks — higher = more material to a saved answer or decision.
RANK_DECISION = 100
RANK_CLAIM_STATE = 80
RANK_CLAIM_STALE = 60
RANK_CITED_EVIDENCE = 40
RANK_UNCITED_EVIDENCE = 10
RANK_NONE = 0

MATERIAL_THRESHOLD = RANK_CITED_EVIDENCE  # uncited-only changes are noise for day-two


def _ensure(con):
    con.executescript('''
        CREATE TABLE IF NOT EXISTS update_runs(
            id TEXT PRIMARY KEY,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    ''')


def connect(db=None):
    con = follow.connect(db)
    try:
        _ensure(con)
        con.commit()
    except Exception:
        con.close()
        raise
    return con


def _save_run(run, *, db=None):
    run = copy.deepcopy(run)
    with closing(connect(db)) as con, con:
        con.execute(
            'INSERT INTO update_runs(id,body,created_at) VALUES(?,?,?) '
            'ON CONFLICT(id) DO UPDATE SET body=excluded.body',
            (run['id'], json.dumps(run), run['created_at']),
        )
    return get_run(run['id'], db=db)


def get_run(run_id, *, db=None):
    with closing(connect(db)) as con, con:
        row = con.execute('SELECT body FROM update_runs WHERE id=?', (run_id,)).fetchone()
        if row is None:
            raise ValueError('update run not found')
        return json.loads(row['body'])


def list_runs(*, db=None, limit=20):
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError('limit must be 1–100')
    with closing(connect(db)) as con, con:
        rows = [
            json.loads(r['body'])
            for r in con.execute('SELECT body FROM update_runs ORDER BY created_at DESC')
        ]
    return rows[:limit]


def _claim_state_map(data):
    brief = research.brief(data)
    return {c['id']: c['state'] for c in brief['claims']}


def _cited_evidence_ids(data):
    cited = set()
    for d in data.get('decisions', []):
        if d.get('superseded_by'):
            continue
        cited.update(d.get('evidence_ids') or [])
    for c in data.get('claims', []):
        for a in c.get('assessments', []):
            eid = (a.get('anchor') or {}).get('evidence_id')
            if eid:
                cited.add(eid)
    return cited


def score_case_change(before, after):
    """Score and explain effects of a version delta. Pure — no I/O.

    Only *new* effects in this delta count as material. A decision that was
    already REVIEW_REQUIRED and stays that way with no fresh source change is
    not a new day-two event.
    """
    effects = []
    before_states = _claim_state_map(before)
    after_brief = research.brief(after)
    after_states = {c['id']: c['state'] for c in after_brief['claims']}
    delta = after.get('changes') or cases.changes(before, after)
    delta_eids = {c.get('evidence_id') for c in delta if c.get('evidence_id')}

    before_decisions = {d['id']: d for d in before.get('decisions', [])}
    for d in after.get('decisions', []):
        if d.get('superseded_by'):
            continue
        review = d.get('review') or {}
        if review.get('state') != 'REVIEW_REQUIRED':
            continue
        prior = before_decisions.get(d['id']) or {}
        prior_state = (prior.get('review') or {}).get('state')
        fresh = bool(delta_eids & set(d.get('evidence_ids') or [])) or any(
            c.get('kind') == 'repo_changed' for c in delta
        )
        newly = prior_state != 'REVIEW_REQUIRED'
        if not (fresh or newly):
            continue
        effects.append({
            'kind': 'decision_review_required',
            'rank': RANK_DECISION,
            'decision_id': d['id'],
            'statement': d['statement'],
            'changes': [c for c in (review.get('changes') or []) if c.get('evidence_id') in delta_eids or c.get('kind') == 'repo_changed']
                       or review.get('changes') or [],
            'why': 'Cited evidence for this decision changed or became unavailable.',
        })

    # Claim state transitions (answer changed)
    for cid, after_state in after_states.items():
        before_state = before_states.get(cid)
        if before_state and before_state != after_state:
            effects.append({
                'kind': 'claim_state_changed',
                'rank': RANK_CLAIM_STATE,
                'claim_id': cid,
                'before': before_state,
                'after': after_state,
                'statement': next(c['statement'] for c in after_brief['claims'] if c['id'] == cid),
                'why': f'Claim moved {before_state} → {after_state}.',
            })

    cited = _cited_evidence_ids(before) | _cited_evidence_ids(after)
    decision_covered = {
        c.get('evidence_id')
        for e in effects if e.get('kind') == 'decision_review_required'
        for c in (e.get('changes') or [])
        if c.get('evidence_id')
    }
    for change in delta:
        eid = change.get('evidence_id')
        if not eid:
            if change.get('kind') == 'repo_changed':
                effects.append({
                    'kind': 'repo_changed',
                    'rank': RANK_CITED_EVIDENCE,
                    'why': change.get('reason') or 'Tracked repo context changed.',
                    'change': change,
                })
            continue
        if eid in decision_covered:
            continue
        if eid in cited:
            effects.append({
                'kind': 'cited_evidence_changed',
                'rank': RANK_CITED_EVIDENCE,
                'evidence_id': eid,
                'change': change,
                'why': 'Evidence cited by a claim or decision changed.',
            })
        else:
            effects.append({
                'kind': 'uncited_evidence_changed',
                'rank': RANK_UNCITED_EVIDENCE,
                'evidence_id': eid,
                'change': change,
                'why': 'An uncited source changed; no saved conclusion cites it yet.',
            })

    effects.sort(key=lambda e: (-e['rank'], e['kind'], e.get('decision_id') or e.get('claim_id') or e.get('evidence_id') or ''))
    top = effects[0]['rank'] if effects else RANK_NONE
    material = [e for e in effects if e['rank'] >= MATERIAL_THRESHOLD]
    return {
        'effects': effects,
        'material_effects': material,
        'top_rank': top,
        'material': bool(material),
        'effect_count': len(effects),
        'material_count': len(material),
    }


def naive_any_change(before, after):
    """Baseline arm: report every evidence delta without ranking by effect.

    Competent-in-two-hours version. Useful as a comparison — not the product.
    """
    delta = after.get('changes') or cases.changes(before, after)
    return {
        'effects': [{'kind': 'any_change', 'rank': 1, 'change': c, 'why': 'Something in the case changed.'} for c in delta],
        'material_effects': [{'kind': 'any_change', 'rank': 1, 'change': c, 'why': 'Something in the case changed.'} for c in delta],
        'top_rank': 1 if delta else 0,
        'material': bool(delta),
        'effect_count': len(delta),
        'material_count': len(delta),
        'arm': 'naive_any_change',
    }


def run_updates(*, db=None, case_id=None, live=False, refresh=True, limit=50):
    """Explicit update pass over followed questions.

    `refresh=True` re-collects sources for each followed case (live controls web).
    `refresh=False` compares the current saved version to the version recorded at
    last check — local only, no fetch claim.
    """
    if type(live) is not bool or type(refresh) is not bool:
        raise ValueError('live and refresh must be booleans')
    followed = follow.list_followed(db=db, active_only=True, limit=limit)
    if case_id:
        followed = [f for f in followed if f['case_id'] == case_id]
        if not followed:
            # Allow one-shot follow+update by requiring an existing follow.
            raise ValueError('case is not followed; run research follow CASE_ID first')

    run = {
        'id': uuid.uuid4().hex[:12],
        'created_at': cases.now(),
        'live': live,
        'refresh': refresh,
        'status': 'completed',
        'items': [],
        'summary': {},
    }

    for item in followed:
        current = cases.get(item['case_id'], db=db)
        checked_online = False
        if refresh:
            before = current
            after = cases.refresh(item['case_id'], live=live, db=db)
            checked_online = bool(live and after.get('freshness', {}).get('new_fetches', 0) > 0)
            before_version = before['version']
        else:
            # Local compare: last recorded follow version → current saved version.
            after = current
            pin = item.get('last_case_version') or item.get('case_version_at_follow') or current['version']
            before_version = pin
            before = cases.get(item['case_id'], version=pin, db=db) if pin != current['version'] else current

        scored = score_case_change(before, after)
        follow.record_check(
            item['id'],
            case_version=after['version'],
            checked_online=checked_online,
            update_run_id=run['id'],
            db=db,
        )
        run['items'].append({
            'follow_id': item['id'],
            'case_id': item['case_id'],
            'question': after['question'],
            'before_version': before_version,
            'after_version': after['version'],
            'checked_online': checked_online,
            'freshness': after.get('freshness'),
            'score': scored,
            'what_would_change_this_answer': _strongest_challenge_line(after, scored),
        })

    run['items'].sort(key=lambda i: (-i['score']['top_rank'], i['case_id']))
    material_items = [i for i in run['items'] if i['score']['material']]
    run['summary'] = {
        'followed': len(run['items']),
        'material_changes': len(material_items),
        'empty': len(material_items) == 0,
        'checked_online_count': sum(1 for i in run['items'] if i['checked_online']),
        'meaning': (
            'No material change to a saved conclusion or decision.'
            if not material_items else
            f"{len(material_items)} followed question(s) have changes that affect a conclusion or decision."
        ),
    }
    return _save_run(run, db=db)


def _strongest_challenge_line(data, scored):
    material = scored.get('material_effects') or []
    if material:
        top = material[0]
        return top.get('why') or top.get('kind')
    # Fall back to brief next action — still names what would change the answer.
    brief = research.brief(data)
    contested = [c for c in brief['claims'] if c['state'] == 'CONTESTED']
    if contested:
        return f"Contested claim remains: {contested[0]['statement'][:160]}"
    return brief.get('next_action') or 'No material change; strongest challenge unchanged.'


def public_run(run):
    return copy.deepcopy(run)


def render_run(run):
    lines = [
        f"Update run {run['id']} · live={run['live']} · refresh={run['refresh']}",
        run['summary']['meaning'],
        f"Followed: {run['summary']['followed']} · material: {run['summary']['material_changes']} · "
        f"checked online: {run['summary']['checked_online_count']}",
        '',
    ]
    if run['summary']['empty']:
        lines += [
            'NOTHING MATERIAL CHANGED',
            'Saved conclusions and decisions still match their cited evidence in this check.',
            'Uncited source noise is omitted from the day-two report (see score.effects for full list).',
            'This does not prove the web is unchanged unless checked_online is true on an item.',
            '',
        ]
    for item in run['items']:
        flag = 'MATERIAL' if item['score']['material'] else 'quiet'
        online = 'online' if item['checked_online'] else 'snapshot'
        lines.append(
            f"[{flag}] {item['case_id']} · v{item.get('before_version')}→v{item['after_version']} · {online}"
        )
        lines.append(f"  {item['question']}")
        lines.append(f"  What would change this answer? {item['what_would_change_this_answer']}")
        for effect in item['score']['material_effects'][:5]:
            lines.append(f"  · ({effect['rank']}) {effect['kind']}: {effect['why']}")
        if not item['score']['material'] and item['score']['effect_count']:
            lines.append(
                f"  · {item['score']['effect_count']} non-material effect(s) omitted from the headline"
            )
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'
