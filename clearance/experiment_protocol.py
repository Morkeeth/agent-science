"""Versioned experiment protocols — plan before execution.

A protocol records its denominator (hypothesis, claim pins, tasks, budget,
stopping rule) before any runner executes. Compatible code-change protocols may
invoke the existing trusted acceptance runner. Other protocols remain planned
until a real runner exists. Never relabel a plan as a result.
"""
from __future__ import annotations

from contextlib import closing
import copy
import json
import uuid
from pathlib import Path

from clearance import cases, research

PROTOCOL_KINDS = frozenset({'code_change', 'observation', 'manual'})
PROTOCOL_STATUSES = frozenset({'planned', 'linked'})  # never 'result' / 'passed'


def _ensure(con):
    con.executescript('''
        CREATE TABLE IF NOT EXISTS experiment_protocols(
            id TEXT NOT NULL,
            case_id TEXT NOT NULL,
            version INTEGER NOT NULL,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY(id, version)
        );
        CREATE INDEX IF NOT EXISTS experiment_protocols_case ON experiment_protocols(case_id);
    ''')


def connect(db=None):
    con = cases.connect(db)
    try:
        _ensure(con)
        con.commit()
    except Exception:
        con.close()
        raise
    return con


def _require_text(value, name, *, max_len=8000, min_len=1):
    if not isinstance(value, str) or not min_len <= len(value.strip()) <= max_len:
        raise ValueError(f'{name} must be text of length {min_len}–{max_len}')
    return value.strip()


def create(
    case_id,
    *,
    hypothesis,
    kind='code_change',
    claim_ids=(),
    claim_versions=None,
    repo=None,
    baseline_ref=None,
    intervention_ref=None,
    tasks=(),
    outcome_definition='',
    comparison_budget=None,
    stopping_rule='',
    acceptance_check=None,
    db=None,
):
    """Create an immutable protocol v1. Does not execute anything."""
    data = cases.get(case_id, db=db)
    hypothesis = _require_text(hypothesis, 'hypothesis', max_len=4000)
    kind = kind if isinstance(kind, str) else ''
    if kind not in PROTOCOL_KINDS:
        raise ValueError(f'kind must be one of {sorted(PROTOCOL_KINDS)}')
    outcome_definition = _require_text(
        outcome_definition or 'Pass/fail of the named acceptance check on both pins.',
        'outcome_definition', max_len=4000,
    )
    stopping_rule = _require_text(
        stopping_rule or 'Stop after the configured paired runs; do not reinterpret failures as success.',
        'stopping_rule', max_len=4000,
    )
    if not isinstance(tasks, (list, tuple)) or any(not isinstance(t, str) or not t.strip() for t in tasks):
        raise ValueError('tasks must be a list of non-empty strings')
    tasks = [t.strip() for t in tasks]
    if not tasks:
        tasks = ['Run the pinned acceptance check on baseline and intervention commits.']

    claim_ids = list(claim_ids or ())
    known = {c['id'] for c in data.get('claims', [])}
    if claim_ids and not set(claim_ids) <= known:
        raise ValueError('each claim_id must exist on this case')
    brief = research.brief(data)
    claim_pins = []
    for c in brief['claims']:
        if claim_ids and c['id'] not in claim_ids:
            continue
        claim_pins.append({
            'claim_id': c['id'],
            'statement': c['statement'],
            'state_at_plan': c['state'],
            'case_version': data['version'],
        })
    if claim_versions is not None:
        if type(claim_versions) is not int or claim_versions < 1:
            raise ValueError('claim_versions must be a positive case version integer when set')
        # Optional explicit pin of the case version used for claim statements.
        for pin in claim_pins:
            pin['case_version'] = claim_versions

    budget = {
        'paired_runs': 3,
        'timeout_seconds': 60,
        'basis': 'Denominator recorded before execution. Billing is not inferred from run counts.',
    }
    if comparison_budget:
        if not isinstance(comparison_budget, dict):
            raise ValueError('comparison_budget must be an object')
        for key in ('paired_runs', 'timeout_seconds'):
            if key in comparison_budget:
                val = comparison_budget[key]
                if type(val) is not int or val < 1:
                    raise ValueError(f'comparison_budget.{key} must be a positive integer')
                budget[key] = val
        if 'basis' in comparison_budget and isinstance(comparison_budget['basis'], str):
            budget['basis'] = comparison_budget['basis'].strip()

    repo_path = None
    if repo is not None:
        repo_path = str(Path(repo).resolve())
        case_repo = (data.get('repo') or {}).get('root')
        if case_repo and Path(case_repo).resolve() != Path(repo_path):
            raise ValueError('protocol repo must match the case repo when the case has one')

    if acceptance_check is not None:
        check = Path(acceptance_check).resolve()
        if not check.is_file() or check.suffix != '.py':
            raise ValueError('acceptance_check must be an existing .py file')
        acceptance_check = str(check)

    if kind == 'code_change':
        if not (baseline_ref and intervention_ref and acceptance_check and repo_path):
            # Still allow a plan that names the missing pieces explicitly.
            pass

    protocol = {
        'id': uuid.uuid4().hex[:12],
        'version': 1,
        'case_id': case_id,
        'case_version_at_plan': data['version'],
        'kind': kind,
        'status': 'planned',
        'hypothesis': hypothesis,
        'claim_pins': claim_pins,
        'repository': repo_path,
        'baseline_ref': baseline_ref,
        'intervention_ref': intervention_ref,
        'tasks': tasks,
        'outcome_definition': outcome_definition,
        'comparison_budget': budget,
        'stopping_rule': stopping_rule,
        'acceptance_check': acceptance_check,
        'executable': bool(
            kind == 'code_change'
            and repo_path and baseline_ref and intervention_ref and acceptance_check
        ),
        'execution': None,  # filled only by execute(); never fabricated
        'created_at': cases.now(),
        'limits': [
            'This record is a plan, not a result.',
            'Only an explicit trusted runner may attach an experiment outcome.',
            'Search pages and models cannot choose arbitrary executable code.',
        ],
        'what_would_change_this_answer': (
            f'If the intervention fails the acceptance check relative to baseline under '
            f'{budget["paired_runs"]} paired runs, revise the cited claim(s).'
            if claim_pins else
            'Define claim pins before treating a measured outcome as answer-changing.'
        ),
    }
    return _save(protocol, db=db)


def _save(protocol, *, db=None):
    protocol = copy.deepcopy(protocol)
    with closing(connect(db)) as con, con:
        con.execute(
            'INSERT INTO experiment_protocols(id,case_id,version,body,created_at) VALUES(?,?,?,?,?)',
            (protocol['id'], protocol['case_id'], protocol['version'], json.dumps(protocol), protocol['created_at']),
        )
    return get(protocol['id'], version=protocol['version'], db=db)


def get(protocol_id, *, version=None, db=None):
    with closing(connect(db)) as con, con:
        if version is None:
            row = con.execute(
                'SELECT body FROM experiment_protocols WHERE id=? ORDER BY version DESC LIMIT 1',
                (protocol_id,),
            ).fetchone()
        else:
            row = con.execute(
                'SELECT body FROM experiment_protocols WHERE id=? AND version=?',
                (protocol_id, version),
            ).fetchone()
        if row is None:
            raise ValueError('experiment protocol not found')
        return json.loads(row['body'])


def list_protocols(*, case_id=None, db=None, limit=20):
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError('limit must be 1–100')
    with closing(connect(db)) as con, con:
        if case_id:
            rows = con.execute(
                'SELECT body FROM experiment_protocols WHERE case_id=? ORDER BY created_at DESC',
                (case_id,),
            ).fetchall()
        else:
            rows = con.execute(
                'SELECT body FROM experiment_protocols ORDER BY created_at DESC'
            ).fetchall()
    # Latest version per id
    latest = {}
    for r in rows:
        body = json.loads(r['body'])
        cur = latest.get(body['id'])
        if cur is None or body['version'] > cur['version']:
            latest[body['id']] = body
    out = sorted(latest.values(), key=lambda p: p['created_at'], reverse=True)
    return out[:limit]


def revise(protocol_id, *, db=None, **fields):
    """Append an immutable new version. Does not mutate prior versions."""
    old = get(protocol_id, db=db)
    allowed = {
        'hypothesis', 'kind', 'claim_ids', 'repo', 'baseline_ref', 'intervention_ref',
        'tasks', 'outcome_definition', 'comparison_budget', 'stopping_rule', 'acceptance_check',
    }
    unknown = set(fields) - allowed
    if unknown:
        raise ValueError(f'unknown protocol fields: {sorted(unknown)}')
    # Rebuild via create semantics but keep id and bump version.
    merged = {
        'hypothesis': fields.get('hypothesis', old['hypothesis']),
        'kind': fields.get('kind', old['kind']),
        'claim_ids': fields.get('claim_ids', [p['claim_id'] for p in old.get('claim_pins', [])]),
        'repo': fields.get('repo', old.get('repository')),
        'baseline_ref': fields.get('baseline_ref', old.get('baseline_ref')),
        'intervention_ref': fields.get('intervention_ref', old.get('intervention_ref')),
        'tasks': fields.get('tasks', old.get('tasks') or ()),
        'outcome_definition': fields.get('outcome_definition', old.get('outcome_definition')),
        'comparison_budget': fields.get('comparison_budget', old.get('comparison_budget')),
        'stopping_rule': fields.get('stopping_rule', old.get('stopping_rule')),
        'acceptance_check': fields.get('acceptance_check', old.get('acceptance_check')),
    }
    draft = create(old['case_id'], db=db, **merged)
    # create() allocated a new id — rewrite as next version of old id.
    with closing(connect(db)) as con, con:
        con.execute('DELETE FROM experiment_protocols WHERE id=? AND version=?', (draft['id'], draft['version']))
    protocol = draft
    protocol['id'] = old['id']
    protocol['version'] = old['version'] + 1
    protocol['supersedes_version'] = old['version']
    protocol['execution'] = None
    protocol['status'] = 'planned'
    return _save(protocol, db=db)


def mark_as_result(protocol_id, *, db=None):
    """Control that must stay RED: plans cannot become results by renaming."""
    raise ValueError(
        'refused: an experiment protocol is a plan, not a result. '
        'Run execute() with a trusted acceptance script to attach a measured experiment_id.'
    )


def execute(protocol_id, *, db=None, version=None):
    """Execute a compatible code_change protocol via the trusted experiments runner.

    Returns the protocol with execution metadata. The measured experiment remains
    a separate cases.experiments row linked by experiment_id.
    """
    protocol = get(protocol_id, version=version, db=db)
    if protocol['kind'] != 'code_change':
        raise ValueError(
            f"protocol kind {protocol['kind']!r} has no runner yet; remains status=planned"
        )
    if not protocol.get('executable'):
        missing = [name for name, ok in (
            ('repository', protocol.get('repository')),
            ('baseline_ref', protocol.get('baseline_ref')),
            ('intervention_ref', protocol.get('intervention_ref')),
            ('acceptance_check', protocol.get('acceptance_check')),
        ) if not ok]
        raise ValueError(
            'protocol is not executable until these are set: ' + ', '.join(missing)
        )
    from clearance.experiments import compare
    budget = protocol['comparison_budget']
    result = compare(
        protocol['case_id'],
        repo=protocol['repository'],
        baseline=protocol['baseline_ref'],
        candidate=protocol['intervention_ref'],
        check=protocol['acceptance_check'],
        runs=budget.get('paired_runs', 3),
        timeout=budget.get('timeout_seconds', 60),
        db=db,
    )
    # Append a new protocol version that links the experiment — still not "the result".
    linked = copy.deepcopy(protocol)
    linked['version'] = protocol['version'] + 1
    linked['supersedes_version'] = protocol['version']
    linked['status'] = 'linked'
    linked['execution'] = {
        'experiment_id': result['id'],
        'valid': result.get('valid'),
        'summary': result.get('summary'),
        'executed_at': cases.now(),
        'meaning': (
            'Measured experiment attached. The protocol remains the plan/denominator; '
            'the experiment record is the outcome. Do not collapse them.'
        ),
    }
    linked['created_at'] = cases.now()
    return _save(linked, db=db)


def public_protocol(protocol):
    return copy.deepcopy(protocol)


def render(protocol):
    lines = [
        f"Experiment protocol {protocol['id']} · v{protocol['version']} · {protocol['status']}",
        f"Case {protocol['case_id']} · kind={protocol['kind']} · executable={protocol.get('executable')}",
        f"Hypothesis: {protocol['hypothesis']}",
        f"Outcome: {protocol['outcome_definition']}",
        f"Budget: {protocol['comparison_budget']}",
        f"Stopping rule: {protocol['stopping_rule']}",
        f"What would change this answer? {protocol['what_would_change_this_answer']}",
        '',
        'Tasks:',
    ]
    for t in protocol.get('tasks') or []:
        lines.append(f'  - {t}')
    if protocol.get('claim_pins'):
        lines.append('Claim pins:')
        for pin in protocol['claim_pins']:
            lines.append(
                f"  - {pin['claim_id']} @ case v{pin['case_version']} [{pin['state_at_plan']}]: "
                f"{pin['statement'][:120]}"
            )
    if protocol.get('repository'):
        lines.append(f"Repo: {protocol['repository']}")
        lines.append(f"Baseline: {protocol.get('baseline_ref')} → Intervention: {protocol.get('intervention_ref')}")
        lines.append(f"Check: {protocol.get('acceptance_check')}")
    if protocol.get('execution'):
        ex = protocol['execution']
        lines += [
            '',
            f"Linked experiment: {ex['experiment_id']} · valid={ex.get('valid')}",
            ex.get('summary') or '',
            ex.get('meaning') or '',
        ]
    else:
        lines += ['', 'Status: planned — not a result.']
    lines.extend([''] + protocol.get('limits', []))
    return '\n'.join(lines).rstrip() + '\n'
