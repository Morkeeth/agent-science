"""Versioned synthesis: separated evidence kinds, challenges, answer diffs.

Empirical findings, official constraints, field adoption and local measurements
stay in separate buckets. Each material conclusion names its strongest challenge
and a falsification condition. Answer diffs distinguish changed sources, newly
available sources and reinterpretations.
"""
from __future__ import annotations

from clearance import cases, claim_graph, conditions, research, study


KIND_BUCKETS = ('empirical', 'official', 'adoption', 'local_measurement')


def _bucket_for_evidence(entry):
    kind = entry.get('kind')
    angle = entry.get('angle')
    host = ''
    try:
        from urllib.parse import urlsplit
        host = (urlsplit(entry.get('url', '')).hostname or '').lower()
    except Exception:
        host = ''
    if entry.get('origin') == 'local_experiment' or kind == 'local_measurement':
        return 'local_measurement'
    if kind == 'research_repository' or angle == 'research':
        return 'empirical'
    if kind == 'declared_official' or angle == 'official_docs':
        return 'official'
    if any(h in host for h in ('news.ycombinator', 'reddit.com', 'stackoverflow.com',
                               'dev.to', 'medium.com', 'github.com')):
        return 'adoption'
    if angle == 'practice':
        return 'adoption'
    if kind == 'web_source':
        return 'adoption'
    return 'adoption'


def _support_conditions_for_claim(claim, evidence_by_id):
    """Conditions from the first supporting assessment's source, else empty unknowns."""
    for a in claim.get('assessments', []):
        if a.get('relation') != 'supports':
            continue
        if a.get('state') == 'SUPERSEDED':
            continue
        eid = (a.get('anchor') or {}).get('evidence_id')
        if eid and eid in evidence_by_id:
            e = evidence_by_id[eid]
            return conditions.extract(e.get('snapshot_text') or '', url=e.get('url'))
    return conditions.extract('')


def _falsification_for(claim, cond, run=None):
    """Name an observation that would reverse the conclusion."""
    task = (cond.get('task') or {}).get('value') or 'the stated task'
    metric = (cond.get('metric') or {}).get('value') or 'the reported metric'
    budget = (cond.get('resource_budget') or {}).get('value')
    if run:
        for node in run.get('question_map') or []:
            if node.get('intent') == 'challenge' and node.get('status') == 'open':
                return {
                    'strongest_challenge': node.get('subquestion'),
                    'falsification_condition': node.get('proposed_search') or node.get('gap'),
                }
            if node.get('intent') in ('challenge', 'replication') and node.get('target_claim_id') == claim.get('id'):
                return {
                    'strongest_challenge': node.get('subquestion'),
                    'falsification_condition': node.get('proposed_search') or node.get('gap'),
                }
    budget_bit = f' under a different resource budget than ({budget})' if budget else ''
    return {
        'strongest_challenge': (
            f'A same-task replication on {task} where {metric} moves in the opposite direction'
            f'{budget_bit} would overturn this conclusion.'
        ),
        'falsification_condition': (
            f'Observe a controlled comparison on the same task ({task}) with the same metric '
            f'({metric}) showing no benefit or harm under a matched budget.'
        ),
    }


def synthesize(data, *, run=None):
    """Produce a Synthesis bound to this case version."""
    brief = research.brief(data)
    evidence_by_id = {e['id']: e for e in data.get('evidence', [])}
    studies = study.build_studies(data.get('evidence', []))
    graph = claim_graph.from_case(data)

    by_kind = {k: [] for k in KIND_BUCKETS}
    for e in data.get('evidence', []):
        bucket = _bucket_for_evidence(e)
        by_kind[bucket].append({
            'evidence_id': e['id'],
            'url': e.get('url'),
            'kind': e.get('kind'),
            'status': e.get('status'),
            'quote': e.get('quote'),
            'study_key': study.study_key(e.get('url', '')),
        })

    # Local measurements from recorded experiments
    for exp in data.get('experiments') or []:
        by_kind['local_measurement'].append({
            'experiment_id': exp.get('id'),
            'valid': exp.get('valid'),
            'summary': {k: exp.get(k) for k in ('hypothesis', 'outcome', 'baseline', 'intervention')
                        if k in exp},
        })

    material = [c for c in brief['claims'] if c['state'] != 'UNRESOLVED'] or list(brief['claims'])
    conclusions = []
    for claim in material:
        cond = _support_conditions_for_claim(claim, evidence_by_id)
        # Prefer study-level conditions when the supporting evidence belongs to a study.
        for a in claim.get('assessments', []):
            if a.get('relation') == 'supports' and a.get('state') != 'SUPERSEDED':
                eid = (a.get('anchor') or {}).get('evidence_id')
                for s in studies:
                    if any(r.get('evidence_id') == eid for r in s['document_refs']):
                        if s.get('conditions'):
                            cond = s['conditions']
                        break
        fals = _falsification_for(claim, cond, run=run)
        conclusions.append({
            'claim_id': claim['id'],
            'statement': claim['statement'],
            'state': claim['state'],
            'conditions': {f: cond.get(f) for f in conditions.FIELDS},
            'strongest_challenge': fals['strongest_challenge'],
            'falsification_condition': fals['falsification_condition'],
            'assessments': [
                {'id': a['id'], 'relation': a['relation'], 'state': a['state']}
                for a in claim.get('assessments', []) if a.get('state') != 'SUPERSEDED'
            ],
        })

    contested = [c for c in brief['claims'] if c['state'] == 'CONTESTED']
    supported = [c for c in brief['claims'] if c['state'] == 'SUPPORTED_AS_ASSESSED']
    if contested:
        headline = 'Material claims are contested after challenge/investigation.'
    elif supported:
        headline = 'Some claims are supported as assessed; contrary same-scope evidence may still reverse them.'
    else:
        headline = 'No claim is settled; evidence was collected under explicit limits.'

    unresolved = []
    if run:
        unresolved = [n['gap'] for n in run.get('question_map', []) if n.get('status') == 'open']
    for c in brief['claims']:
        if c['state'] == 'UNRESOLVED':
            unresolved.append(f'Claim {c["id"]} remains unresolved: {c["statement"][:160]}')

    return {
        'case_version': data['version'],
        'case_id': data['id'],
        'conclusion': headline,
        'material_conclusions': conclusions,
        'by_kind': by_kind,
        'conditions': [
            'Quote occurrence is verified; entailment is authored.',
            'Empirical, official, adoption and local measurement stay separated.',
            f"Run kind={((run or {}).get('kind'))}; stop_reason={((run or {}).get('stop_reason'))}",
        ],
        'evidence_for': [c['id'] for c in supported],
        'evidence_against': [c['id'] for c in contested],
        'unresolved_gaps': unresolved,
        'strongest_challenge': (conclusions[0]['strongest_challenge'] if conclusions else None),
        'falsification_condition': (conclusions[0]['falsification_condition'] if conclusions else None),
        'studies': [
            {'identity': s['identity'], 'id': s['id'], 'urls': [r['url'] for r in s['document_refs']],
             'versions': s.get('versions', []), 'conditions': s.get('conditions')}
            for s in studies
        ],
        'claim_graph': {
            'nodes': graph['nodes'],
            'edges': graph['edges'],
            'meaning': graph['meaning'],
        },
        'scope_guard': True,
        'meaning': (
            'Synthesis summarizes this case version with separated evidence kinds. '
            'It is not an automatic scientific verdict. Model agreement is not a measure of truth.'
        ),
    }


def diff_answers(old_data, new_data):
    """Diff two case versions: changed source vs newly available vs reinterpretation."""
    old_ev = {e['id']: e for e in old_data.get('evidence', [])}
    new_ev = {e['id']: e for e in new_data.get('evidence', [])}
    changes = []

    for eid in sorted(set(old_ev) | set(new_ev)):
        a, b = old_ev.get(eid), new_ev.get(eid)
        if not a and b:
            changes.append({
                'kind': 'newly_available',
                'evidence_id': eid,
                'url': b.get('url'),
                'meaning': 'Source was not present in the earlier answer version.',
            })
        elif a and not b:
            changes.append({
                'kind': 'source_absent',
                'evidence_id': eid,
                'url': a.get('url'),
                'meaning': 'Source not returned in the later version; absence is not a retraction.',
            })
        elif a and b:
            if a.get('snapshot_hash') != b.get('snapshot_hash'):
                changes.append({
                    'kind': 'source_changed',
                    'evidence_id': eid,
                    'url': b.get('url'),
                    'before_hash': a.get('snapshot_hash'),
                    'after_hash': b.get('snapshot_hash'),
                    'meaning': 'The saved snapshot content changed between answer versions.',
                })
            elif a.get('status') != b.get('status'):
                changes.append({
                    'kind': 'source_status_changed',
                    'evidence_id': eid,
                    'url': b.get('url'),
                    'before': a.get('status'),
                    'after': b.get('status'),
                })

    # Reinterpretations: assessments that differ while citing the same snapshot hash.
    old_claims = {c['id']: c for c in old_data.get('claims', [])}
    new_claims = {c['id']: c for c in new_data.get('claims', [])}
    for cid in sorted(set(old_claims) | set(new_claims)):
        oc, nc = old_claims.get(cid), new_claims.get(cid)
        if not oc or not nc:
            if nc and not oc:
                changes.append({
                    'kind': 'reinterpretation',
                    'claim_id': cid,
                    'meaning': 'New claim authored in the later answer version.',
                    'statement': nc.get('statement'),
                })
            continue
        old_active = {
            (a.get('relation'), (a.get('anchor') or {}).get('evidence_id'),
             (a.get('anchor') or {}).get('snapshot_hash'))
            for a in oc.get('assessments', [])
        }
        new_active = {
            (a.get('relation'), (a.get('anchor') or {}).get('evidence_id'),
             (a.get('anchor') or {}).get('snapshot_hash'))
            for a in nc.get('assessments', [])
        }
        added = new_active - old_active
        for relation, eid, snap in added:
            # If the evidence snapshot is unchanged (or new evidence), this is reinterpretation
            # when the relation is new relative to prior assessments on this claim.
            prior_relations = {r for r, e, s in old_active if e == eid}
            if relation not in prior_relations:
                changes.append({
                    'kind': 'reinterpretation',
                    'claim_id': cid,
                    'evidence_id': eid,
                    'relation': relation,
                    'snapshot_hash': snap,
                    'meaning': (
                        'Assessment relation changed or was newly authored without requiring a '
                        'source-content change (reinterpretation).'
                    ),
                })

    # Also surface case.changes when present on new_data
    for c in new_data.get('changes') or []:
        if c.get('kind') == 'source_changed' and not any(
            x['kind'] == 'source_changed' and x.get('evidence_id') == c.get('evidence_id')
            for x in changes
        ):
            changes.append({
                'kind': 'source_changed',
                'evidence_id': c.get('evidence_id'),
                'url': c.get('url'),
                'meaning': 'Recorded by case refresh as a changed snapshot.',
            })
        if c.get('kind') == 'source_added' and not any(
            x['kind'] == 'newly_available' and x.get('evidence_id') == c.get('evidence_id')
            for x in changes
        ):
            changes.append({
                'kind': 'newly_available',
                'evidence_id': c.get('evidence_id'),
                'url': c.get('url'),
                'meaning': 'Recorded by investigation as a newly available source.',
            })

    return {
        'from_version': old_data.get('version'),
        'to_version': new_data.get('version'),
        'case_id': new_data.get('id') or old_data.get('id'),
        'changes': changes,
        'counts': {
            'source_changed': sum(1 for c in changes if c['kind'] == 'source_changed'),
            'newly_available': sum(1 for c in changes if c['kind'] == 'newly_available'),
            'reinterpretation': sum(1 for c in changes if c['kind'] == 'reinterpretation'),
        },
        'meaning': (
            'changed source = snapshot hash moved; newly available = source absent before; '
            'reinterpretation = assessment/relation changed without requiring source-content change.'
        ),
    }


def render_synthesis(syn):
    lines = [
        f"Synthesis · case {syn.get('case_id')} · version {syn.get('case_version')}",
        syn.get('conclusion', ''),
        '',
        'By evidence kind:',
    ]
    for kind in KIND_BUCKETS:
        rows = syn.get('by_kind', {}).get(kind) or []
        lines.append(f'  {kind}: {len(rows)}')
        for row in rows[:5]:
            lines.append(f"    - {row.get('url') or row.get('experiment_id')}")
    lines.append('')
    lines.append('Material conclusions:')
    for c in syn.get('material_conclusions') or []:
        lines.append(f"  [{c['state']}] {c['statement'][:200]}")
        lines.append(f"    strongest challenge: {c.get('strongest_challenge')}")
        lines.append(f"    falsification: {c.get('falsification_condition')}")
    if syn.get('unresolved_gaps'):
        lines.append('')
        lines.append('Unresolved:')
        for g in syn['unresolved_gaps'][:8]:
            lines.append(f'  - {g}')
    lines.append('')
    lines.append(syn.get('meaning', ''))
    return '\n'.join(lines) + '\n'


def render_diff(diff):
    lines = [
        f"Answer diff · case {diff.get('case_id')} · v{diff.get('from_version')} → v{diff.get('to_version')}",
        f"counts: {diff.get('counts')}",
        '',
    ]
    for c in diff.get('changes') or []:
        lines.append(f"  [{c['kind']}] {c.get('url') or c.get('claim_id') or c.get('evidence_id')}")
        if c.get('meaning'):
            lines.append(f"    {c['meaning']}")
    lines.append('')
    lines.append(diff.get('meaning', ''))
    return '\n'.join(lines) + '\n'
