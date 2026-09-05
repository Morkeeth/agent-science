"""Immutable local research campaigns. Judgments are authored, never truth scores."""
import copy
import itertools
import json
import re
import sqlite3
import uuid
from contextlib import closing
from clearance import cases, night_runs

CRITERIA = ('original_sources', 'citation_correctness', 'scope_errors', 'contrary_evidence',
            'unresolved_gaps', 'experiment_specificity')
MODES = ('snapshot_replay', 'fresh_web')


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def _hash(value):
    return cases.digest(_json(value))


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(name + ' must be nonempty text')
    return value


def _connect(db):
    con = cases.connect(db)
    con.executescript('''CREATE TABLE IF NOT EXISTS research_campaigns(
        id TEXT PRIMARY KEY, body TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS research_observations(
        campaign_id TEXT NOT NULL, arm_id TEXT NOT NULL, question_id TEXT NOT NULL,
        repetition INTEGER NOT NULL, body TEXT NOT NULL,
        PRIMARY KEY(campaign_id,arm_id,question_id,repetition));''')
    return con


def create(spec, *, db=None):
    """Freeze a denominator and independently authored rubric before recording results."""
    if not isinstance(spec, dict):
        raise ValueError('spec must be an object')
    manifest = copy.deepcopy(spec)
    for key in ('title', 'authored_by', 'rubric_provenance'):
        _text(manifest.get(key), key)
    repetitions = manifest.get('repetitions')
    if type(repetitions) is not int or not 1 <= repetitions <= 100:
        raise ValueError('repetitions must be an integer from 1 to 100')
    rubric = manifest.get('rubric')
    if not isinstance(rubric, dict) or set(rubric) != set(CRITERIA):
        raise ValueError('rubric must define all six criteria')
    for key, value in rubric.items():
        _text(value, key)
    for field in ('questions', 'arms'):
        values = manifest.get(field)
        if not isinstance(values, list) or not 1 <= len(values) <= 100:
            raise ValueError(field + ' must contain 1–100 entries')
        ids = []
        for value in values:
            if not isinstance(value, dict):
                raise ValueError(field + ' entries must be objects')
            ids.append(_text(value.get('id'), field + ' id'))
        if len(ids) != len(set(ids)):
            raise ValueError('duplicate ' + field + ' id')
    for question in manifest['questions']:
        for key in ('topic', 'question'):
            _text(question.get(key), key)
        distinctions = question.get('expected_distinctions')
        if not isinstance(distinctions, list) or not distinctions:
            raise ValueError('expected_distinctions must be independently authored')
        for value in distinctions:
            _text(value, 'expected distinction')
        question['question_hash'] = cases.digest(question['question'])
    for arm in manifest['arms']:
        if arm.get('kind') not in ('synthesis', 'retrieval') or arm.get('mode') not in MODES:
            raise ValueError('arm requires kind synthesis/retrieval and explicit mode')
        if ('code_ref' in arm) == ('baseline_policy' in arm):
            raise ValueError('arm requires exactly one pinned code_ref or authored baseline_policy')
        if 'code_ref' in arm and not re.fullmatch('[0-9a-f]{40}', str(arm['code_ref'])):
            raise ValueError('code_ref must be a full immutable commit hash, never HEAD or branch')
        if 'baseline_policy' in arm:
            _text(arm['baseline_policy'], 'baseline_policy')
        limits = arm.get('resource_limits')
        if not isinstance(limits, dict) or not limits:
            raise ValueError('resource_limits must be explicit')
        if any(type(v) is not int or v < 0 for v in limits.values()):
            raise ValueError('resource limits must be nonnegative integers')
    manifest['denominator'] = len(manifest['questions']) * len(manifest['arms']) * repetitions
    result = {'id': uuid.uuid4().hex[:16], 'created_at': cases.now(), 'manifest': manifest,
              'manifest_hash': _hash(manifest)}
    with closing(_connect(db)) as con, con:
        con.execute('INSERT INTO research_campaigns VALUES(?,?)', (result['id'], _json(result)))
    return get(result['id'], db=db)


def _load(con, campaign_id):
    row = con.execute('SELECT body FROM research_campaigns WHERE id=?', (campaign_id,)).fetchone()
    if row is None:
        raise ValueError('evaluation campaign not found')
    result = json.loads(row[0])
    if result['manifest_hash'] != _hash(result['manifest']):
        raise ValueError('frozen manifest integrity check failed')
    return result


def record(campaign_id, observation, *, db=None):
    """Append one reviewed completed outcome; caller metrics are never accepted."""
    if not isinstance(observation, dict):
        raise ValueError('observation must be an object')
    allowed = {'arm_id', 'question_id', 'repetition', 'case_id', 'case_version', 'run_id',
               'question_hash', 'mode', 'resource_limits', 'reviewer', 'judgments', 'errors'}
    if set(observation) - allowed:
        raise ValueError('unknown observation fields; usage and costs come only from persisted records')
    obs = copy.deepcopy(observation)
    with closing(_connect(db)) as con:
        campaign = _load(con, campaign_id)
    manifest = campaign['manifest']
    arm = next((a for a in manifest['arms'] if a['id'] == obs.get('arm_id')), None)
    question = next((q for q in manifest['questions'] if q['id'] == obs.get('question_id')), None)
    if not arm or not question:
        raise ValueError('unknown arm or question')
    if type(obs.get('repetition')) is not int or not 1 <= obs['repetition'] <= manifest['repetitions']:
        raise ValueError('repetition outside frozen denominator')
    if obs.get('question_hash') != question['question_hash']:
        raise ValueError('question hash mismatch')
    if obs.get('mode') != arm['mode'] or obs.get('resource_limits') != arm['resource_limits']:
        raise ValueError('mode or resource limits differ from frozen arm')
    if type(obs.get('case_version')) is not int or obs['case_version'] < 1:
        raise ValueError('exact positive case_version required')
    case = cases.get(_text(obs.get('case_id'), 'case_id'), version=obs['case_version'], db=db)
    if cases.digest(case['question']) != question['question_hash']:
        raise ValueError('persisted case question mismatch')
    run = None
    if obs.get('run_id'):
        run = night_runs.get(obs['run_id'], db=db)
        if run['status'] != 'completed':
            raise ValueError('run must be completed, not planned or interrupted')
        if run['case_id'] != case['id'] or run['case_version'] != case['version']:
            raise ValueError('run must reference exact observed case version')
        if cases.digest(run['question']) != question['question_hash']:
            raise ValueError('persisted run question mismatch')
        if run['limits'] != arm['resource_limits']:
            raise ValueError('actual run resource limits mismatch')
        if run['created_at'] < campaign['created_at']:
            raise ValueError('run predates frozen campaign')
        online = run.get('observed_usage', {}).get('online_fetches', 0)
        if obs['mode'] == 'fresh_web' and not online:
            raise ValueError('fresh_web requires an observed online fetch in this run')
        if obs['mode'] == 'snapshot_replay' and online:
            raise ValueError('snapshot_replay cannot contain online fetches')
    elif 'baseline_policy' not in arm:
        raise ValueError('candidate requires a completed persisted run')
    elif arm['mode'] == 'fresh_web':
        raise ValueError('fresh_web baseline requires a persisted run with observed fetches')
    if arm['kind'] == 'synthesis' and not case.get('claims'):
        raise ValueError('synthesis arm requires a saved interpreted answer, not retrieval')
    snapshots = {}
    for evidence in case['evidence']:
        text = evidence.get('snapshot_text')
        if text is not None:
            if not isinstance(text, str) or cases.digest(text) != evidence.get('snapshot_hash'):
                raise ValueError('source snapshot integrity check failed')
            snapshots[evidence['id']] = evidence
    if arm['kind'] == 'retrieval' and not snapshots:
        raise ValueError('retrieval outcome requires saved source snapshots; an empty plan is not a completed baseline')
    judgments = obs.get('judgments')
    if not isinstance(judgments, dict) or set(judgments) != set(CRITERIA):
        raise ValueError('all six manual judgments are required; use unknown when unmeasured')
    _text(obs.get('reviewer'), 'reviewer')
    for name, judgment in judgments.items():
        if not isinstance(judgment, dict) or judgment.get('status') not in ('pass', 'fail', 'unknown'):
            raise ValueError('judgment status must be pass, fail or unknown')
        _text(judgment.get('rationale'), name + ' rationale')
        anchors = judgment.get('anchors')
        if not isinstance(anchors, list):
            raise ValueError('judgment anchors must be a list')
        if judgment['status'] == 'pass' and name in ('original_sources', 'citation_correctness', 'contrary_evidence') and not anchors:
            raise ValueError(name + ' pass requires inspected source anchors')
        for anchor in anchors:
            if not isinstance(anchor, dict):
                raise ValueError('anchor must be an object')
            source = snapshots.get(anchor.get('evidence_id'))
            quote = _text(anchor.get('quote'), 'anchor quote')
            if not source or source.get('status') == 'UNAVAILABLE' or quote not in source['snapshot_text']:
                raise ValueError('review anchor does not occur in pinned source snapshot')
            anchor['snapshot_hash'] = source['snapshot_hash']
        judgment['basis'] = 'manual_judgment; anchor occurrence does not establish entailment'
    errors = obs.setdefault('errors', [])
    if not isinstance(errors, list):
        raise ValueError('errors must be a list')
    for error in errors:
        if not isinstance(error, dict):
            raise ValueError('error must be an object')
        _text(error.get('kind'), 'error kind'); _text(error.get('detail'), 'error detail')
    obs.update(recorded_at=cases.now(), manifest_hash=campaign['manifest_hash'],
               case_content_hash=_hash({k: case.get(k) for k in ('id', 'version', 'question', 'claims', 'evidence')}),
               source_snapshots=[{'evidence_id': e['id'], 'url': e['url'], 'snapshot_hash': e['snapshot_hash']} for e in snapshots.values()],
               operational={'observed_usage': run.get('observed_usage') if run else None,
                            'usage_basis': run.get('usage_basis') if run else 'baseline case; no instrumented run',
                            'latency_seconds': None, 'tokens': None, 'billing': run.get('billing') if run else None},
               execution_provenance='Code pin is the frozen intended arm; this store does not attest which executable produced a run.')
    with closing(_connect(db)) as con, con:
        con.execute('BEGIN IMMEDIATE')
        previous = [json.loads(row[0]) for row in con.execute('SELECT body FROM research_observations WHERE campaign_id=?', (campaign_id,))]
        for old in previous:
            if (old['arm_id'], old['question_id'], old['repetition']) == (obs['arm_id'], obs['question_id'], obs['repetition']):
                raise ValueError('duplicate frozen evaluation slot')
            if obs.get('run_id') and old.get('run_id') == obs['run_id']:
                raise ValueError('completed run already recorded; repetitions require distinct executions')
            if not obs.get('run_id') and (old['case_id'], old['case_version']) == (obs['case_id'], obs['case_version']):
                raise ValueError('baseline case outcome already recorded; repetitions require distinct outcomes')
        try:
            con.execute('INSERT INTO research_observations VALUES(?,?,?,?,?)',
                        (campaign_id, obs['arm_id'], obs['question_id'], obs['repetition'], _json(obs)))
        except sqlite3.IntegrityError as exc:
            raise ValueError('duplicate frozen evaluation slot') from exc
    return get(campaign_id, db=db)


def get(campaign_id, *, db=None):
    with closing(_connect(db)) as con:
        result = _load(con, campaign_id)
        observations = [json.loads(r[0]) for r in con.execute(
            'SELECT body FROM research_observations WHERE campaign_id=? ORDER BY question_id,repetition,arm_id', (campaign_id,))]
    manifest = result['manifest']
    slots = {(o['arm_id'], o['question_id'], o['repetition']): o for o in observations}
    missing = [{'arm_id': a['id'], 'question_id': q['id'], 'repetition': r}
               for a, q, r in itertools.product(manifest['arms'], manifest['questions'], range(1, manifest['repetitions'] + 1))
               if (a['id'], q['id'], r) not in slots]
    pairs = []
    for a, b in itertools.combinations(manifest['arms'], 2):
        reasons = [label for key, label in (('kind', 'different output tasks; retrieval is not synthesis'),
                   ('mode', 'different evidence modes'), ('resource_limits', 'different resource limits')) if a[key] != b[key]]
        paired = sum((a['id'], q['id'], r) in slots and (b['id'], q['id'], r) in slots
                     for q, r in itertools.product(manifest['questions'], range(1, manifest['repetitions'] + 1)))
        source_differences = []
        for q, r in itertools.product(manifest['questions'], range(1, manifest['repetitions'] + 1)):
            left, right = slots.get((a['id'], q['id'], r)), slots.get((b['id'], q['id'], r))
            if left and right:
                hashes = lambda item: sorted((s['url'], s['snapshot_hash']) for s in item['source_snapshots'])
                if hashes(left) != hashes(right):
                    source_differences.append({'question_id': q['id'], 'repetition': r})
        pairs.append({'arms': [a['id'], b['id']], 'comparable_design': not reasons,
                      'paired_observations': paired, 'reasons': reasons, 'different_source_exposure': source_differences,
                      'limit': 'Recorded design comparability only; executable provenance and judgment quality require independent review.'})
    result.update(observations=observations, coverage={'recorded': len(observations), 'denominator': manifest['denominator'], 'missing_slots': missing},
                  error_inventory=[dict(e, arm_id=o['arm_id'], question_id=o['question_id'], repetition=o['repetition']) for o in observations for e in o['errors']],
                  paired_comparability=pairs, quality_summary='Manual criteria are retained separately. No automatic truth score or confidence percentage.')
    return result
