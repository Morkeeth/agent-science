"""Immutable local research campaigns. Judgments are authored, never truth scores."""
import copy
import itertools
import json
import math
import re
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime
from clearance import cases, night_runs, research_protocols

CRITERIA = ('original_sources', 'citation_correctness', 'scope_errors', 'contrary_evidence',
            'unresolved_gaps', 'experiment_specificity')
PREPARATION_CRITERIA = ('source_recovery', 'counterevidence', 'experiment_executability')
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
        PRIMARY KEY(campaign_id,arm_id,question_id,repetition));
        CREATE TABLE IF NOT EXISTS research_evaluation_reviews(
        campaign_id TEXT NOT NULL, arm_id TEXT NOT NULL, question_id TEXT NOT NULL,
        repetition INTEGER NOT NULL, version INTEGER NOT NULL, body TEXT NOT NULL,
        PRIMARY KEY(campaign_id,arm_id,question_id,repetition,version));''')
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
        if 'code_ref' in arm and set(limits) != set(night_runs.DEFAULTS):
            raise ValueError('code-pinned resource limits must match the supported run limit keys')
        if any(type(v) is not int or v < 0 for v in limits.values()):
            raise ValueError('resource limits must be nonnegative integers')
    manifest['denominator'] = len(manifest['questions']) * len(manifest['arms']) * repetitions
    result = {'id': uuid.uuid4().hex[:16], 'created_at': cases.now(), 'manifest': manifest,
              'manifest_hash': _hash(manifest)}
    with closing(_connect(db)) as con, con:
        con.execute('INSERT INTO research_campaigns VALUES(?,?)', (result['id'], _json(result)))
    return get(result['id'], db=db)


def prepare(spec, *, db=None):
    """Freeze a matched evaluation after validating its operational rubric.

    This is a thin preparation layer over the existing immutable campaign
    table. It records what will be checked and what is still unknown; it does
    not search, call a model, execute an experiment, or create an observation.
    ``create`` remains available for historical campaigns whose manifests must
    not be rewritten.
    """
    if not isinstance(spec, dict):
        raise ValueError('spec must be an object')
    prepared = copy.deepcopy(spec)
    rubric = prepared.get('operational_rubric')
    if not isinstance(rubric, dict) or set(rubric) != set(PREPARATION_CRITERIA):
        raise ValueError('operational_rubric must define source_recovery, counterevidence and experiment_executability')
    for key, value in rubric.items():
        _text(value, 'operational rubric ' + key)
    unknown = prepared.get('unknown_resources')
    if not isinstance(unknown, list) or not unknown:
        raise ValueError('unknown_resources must be a nonempty list; name unavailable costs or resources explicitly')
    for value in unknown:
        _text(value, 'unknown resource')
    questions = prepared.get('questions')
    if not isinstance(questions, list) or not questions:
        raise ValueError('questions must be nonempty')
    arms = prepared.get('arms')
    if not isinstance(arms, list) or len(arms) != 2:
        raise ValueError('prepared campaign requires exactly two matched arms: baseline and candidate')
    arm_ids = {arm.get('id') for arm in arms if isinstance(arm, dict)}
    if arm_ids != {'baseline', 'candidate'}:
        raise ValueError('prepared campaign arms must be named baseline and candidate')
    supplied_protocol = prepared.get('protocol')
    if supplied_protocol is not None and not isinstance(supplied_protocol, dict):
        raise ValueError('protocol must be an object when provided')
    protocol = {'state': 'UNRESOLVED', 'reason': 'No immutable protocol ID and version were supplied.'}
    if supplied_protocol:
        if set(supplied_protocol) != {'id', 'version'}:
            raise ValueError('protocol reference requires exactly id and version')
        protocol_id = _text(supplied_protocol.get('id'), 'protocol id')
        protocol_version = supplied_protocol.get('version')
        if type(protocol_version) is not int or protocol_version < 1:
            raise ValueError('protocol version must be a positive integer')
        saved = research_protocols.get(protocol_id, version=protocol_version, db=db)
        if saved.get('status') != 'READY':
            raise ValueError('prepared campaign requires a READY immutable protocol')
        if saved.get('executions'):
            raise ValueError('protocol already has execution history; create a fresh protocol version before preparing a held-out campaign')
        if saved.get('kind') != 'code_change':
            raise ValueError('prepared evaluation requires a code_change protocol')
        pins = {arm['id']: arm.get('code_ref') for arm in arms}
        if pins != {'baseline': saved.get('baseline'), 'candidate': saved.get('intervention')}:
            raise ValueError('campaign arm pins must equal the frozen protocol baseline and intervention')
        protocol_snapshot = {key: saved.get(key) for key in (
            'id', 'version', 'case_id', 'case_version', 'kind', 'status', 'repo',
            'baseline', 'intervention', 'check_sha256', 'budget', 'stopping_rule')}
        protocol = {'state': 'READY_UNRUN', 'id': protocol_id, 'version': protocol_version,
                    'snapshot': protocol_snapshot, 'snapshot_hash': _hash(protocol_snapshot)}
    prepared['preparation'] = {
        'status': 'FROZEN_UNRUN',
        'operational_rubric': rubric,
        'unknown_resources': unknown,
        'protocol': protocol,
        'result_policy': 'Only completed persisted runs or explicitly authored baseline policies can be recorded; a plan is not evidence.',
    }
    result = create(prepared, db=db)
    result['preparation'] = copy.deepcopy(result['manifest']['preparation'])
    result['next_action'] = ('Run protocol ' + protocol['id'] + ' v' + str(protocol['version']) +
        ' with the trusted CLI acceptance script, then record results with exact provenance.'
        if protocol['state'] == 'READY_UNRUN' else
        'Create a READY immutable experiment protocol, then prepare a new campaign version before recording results.')
    return result


def _protocol_evidence(campaign, observation, *, db=None):
    """Resolve a prepared campaign's frozen protocol without rewriting its manifest."""
    preparation = campaign['manifest'].get('preparation')
    if not isinstance(preparation, dict):
        return None
    reference = preparation.get('protocol')
    if not isinstance(reference, dict) or reference.get('state') != 'READY_UNRUN':
        return None
    saved = research_protocols.get(reference.get('id'), version=reference.get('version'), db=db)
    snapshot = reference.get('snapshot')
    if not isinstance(snapshot, dict) or reference.get('snapshot_hash') != _hash(snapshot):
        raise ValueError('frozen protocol reference integrity check failed')
    current_snapshot = {key: saved.get(key) for key in snapshot}
    if current_snapshot != snapshot:
        raise ValueError('stored protocol no longer matches the frozen campaign reference')
    completed = [execution for execution in saved.get('executions', [])
                 if execution.get('state') == 'COMPLETED' and execution.get('experiment_id')]
    if not completed:
        return None
    if len(completed) != 1:
        raise ValueError('frozen protocol has ambiguous completed executions')
    execution = completed[0]
    if (execution.get('protocol_id') != saved['id']
            or execution.get('protocol_version') != saved['version']):
        raise ValueError('execution identity differs from frozen protocol')
    with closing(cases.connect(db)) as con:
        row = con.execute('SELECT case_id,body FROM experiments WHERE id=?',
                          (execution['experiment_id'],)).fetchone()
    if row is None:
        raise ValueError('completed protocol execution refers to a missing experiment')
    result = json.loads(row['body'])
    if not isinstance(result, dict):
        raise ValueError('persisted experiment result must be an object')
    if (result.get('id') != execution['experiment_id'] or row['case_id'] != saved['case_id']
            or result.get('case_id') != saved['case_id']
            or result.get('case_version') != saved['case_version']
            or observation.get('case_id') != saved['case_id']
            or observation.get('case_version') != saved['case_version']
            or result.get('repo') != saved['repo']):
        raise ValueError('experiment identity differs from frozen protocol or observed case')
    if (result.get('valid') is not True
            or result.get('pins') != {'baseline': saved['baseline'], 'candidate': saved['intervention']}
            or result.get('acceptance_sha256') != saved['check_sha256']
            or not isinstance(result.get('acceptance_source'), str)
            or cases.digest(result['acceptance_source']) != result['acceptance_sha256']):
        raise ValueError('experiment validity, pins or acceptance digest differ from frozen protocol')
    if (not isinstance(result.get('runs'), list) or not result['runs']
            or not all(isinstance(run, dict) for run in result['runs'])
            or execution.get('result') != cases.experiment_summary(result)):
        raise ValueError('persisted experiment differs from the completed execution result')
    try:
        frozen, started, recorded, finished = [datetime.fromisoformat(value) for value in (
            campaign['created_at'], execution.get('started_at'), result.get('recorded_at'),
            execution.get('finished_at'))]
        if any(value.tzinfo is None for value in (frozen, started, recorded, finished)):
            raise ValueError('timezone missing')
        ordered = frozen < started <= recorded <= finished
    except (TypeError, ValueError):
        raise ValueError('experiment execution requires valid timezone-aware timestamps') from None
    if not ordered:
        raise ValueError('experiment execution must start after campaign freeze and finish after its result')
    return {'protocol_id': saved['id'], 'protocol_version': saved['version'],
            'protocol_snapshot_hash': reference['snapshot_hash'],
            'acceptance_sha256': result['acceptance_sha256'], 'experiment_id': result['id'],
            'experiment_sha256': _hash(result), 'execution_sha256': _hash(execution),
            'case_id': result['case_id'], 'case_version': result['case_version'],
            'pins': copy.deepcopy(result['pins']), 'recorded_at': result['recorded_at'],
            'execution_id': execution['id'], 'execution_state': execution['state']}


def _load(con, campaign_id):
    row = con.execute('SELECT body FROM research_campaigns WHERE id=?', (campaign_id,)).fetchone()
    if row is None:
        raise ValueError('evaluation campaign not found')
    result = json.loads(row[0])
    if result['manifest_hash'] != _hash(result['manifest']):
        raise ValueError('frozen manifest integrity check failed')
    return result


def _runtime_observation(run, arm):
    """Validate persisted execution attestations without treating missing data as success."""
    limitations = []
    if run is None:
        return {'attested': False, 'engine_elapsed_seconds': None,
                'limitations': ['No instrumented run; executable and engine duration unknown.']}
    steps = run.get('steps', [])
    runtimes = [('run', run.get('runtime'))] + [
        ('step ' + str(i), step.get('runtime')) for i, step in enumerate(steps)]
    expected = arm.get('code_ref')
    for label, runtime in runtimes:
        clean = (isinstance(runtime, dict) and runtime.get('dirty') is False
                 and isinstance(runtime.get('code_ref'), str)
                 and re.fullmatch('[0-9a-f]{40}', runtime['code_ref'])
                 and isinstance(runtime.get('source_sha256'), str)
                 and re.fullmatch('[0-9a-f]{64}', runtime['source_sha256']))
        if clean and expected and runtime['code_ref'] != expected:
            raise ValueError(label + ' clean runtime code_ref differs from frozen arm')
        if not clean:
            limitations.append(label + ' has missing or dirty runtime provenance.')
    if not expected:
        limitations.append('Authored baseline policy has no executable code pin.')
    if not steps:
        limitations.append('No persisted operation steps.')
    hashes = {runtime['source_sha256'] for _, runtime in runtimes
              if isinstance(runtime, dict) and runtime.get('source_sha256')}
    if len(hashes) > 1:
        limitations.append('Source bytes changed between run creation and operation steps.')
    durations = [step.get('elapsed_seconds') for step in steps]
    duration_known = bool(steps) and all(type(value) in (int, float) and math.isfinite(value)
                                          and value >= 0 for value in durations)
    return {'attested': not limitations, 'runtime': run.get('runtime'),
            'step_runtimes': [step.get('runtime') for step in steps],
            'engine_elapsed_seconds': sum(durations) if duration_known else None,
            'duration_basis': 'Measured engine operations only; excludes host waiting and separately issued tools.',
            'limitations': limitations,
            'duration_limitations': [] if duration_known else ['One or more operation durations are unobserved.']}


def _validate_review_content(obs, snapshots, *, experiment_evidence=None, require_experiment_evidence=False):
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
        if (judgment['status'] == 'pass' and name == 'experiment_specificity'
                and require_experiment_evidence and not experiment_evidence):
            raise ValueError('experiment_specificity pass requires a completed frozen protocol execution')
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
        metadata_activity = run.get('observed_usage', {}).get('metadata_responses', 0) or any(
            event.get('route') == 'source_metadata' and event.get('outcome') not in ('not_checked', 'unsupported', 'skipped')
            and (event.get('url') or event.get('checked_at') or event.get('response_hash'))
            for step in run.get('steps', []) for event in step.get('observed_events', []))
        if obs['mode'] == 'snapshot_replay' and (online or metadata_activity):
            raise ValueError('snapshot_replay cannot contain online fetches or registry requests')
    elif 'baseline_policy' not in arm:
        raise ValueError('candidate requires a completed persisted run')
    elif arm['mode'] == 'fresh_web':
        raise ValueError('fresh_web baseline requires a persisted run with observed fetches')
    if arm['kind'] == 'synthesis':
        from clearance import synthesis
        if not synthesis.build(case)['conclusions']:
            raise ValueError('synthesis arm requires a saved active assessment, not bare imported claims')
    snapshots = {}
    for evidence in case['evidence']:
        text = evidence.get('snapshot_text')
        if text is not None:
            if not isinstance(text, str) or cases.digest(text) != evidence.get('snapshot_hash'):
                raise ValueError('source snapshot integrity check failed')
            snapshots[evidence['id']] = evidence
    if arm['kind'] == 'retrieval' and not snapshots:
        raise ValueError('retrieval outcome requires saved source snapshots; an empty plan is not a completed baseline')
    experiment_evidence = _protocol_evidence(campaign, obs, db=db)
    _validate_review_content(obs, snapshots, experiment_evidence=experiment_evidence,
                             require_experiment_evidence='preparation' in manifest)
    runtime_observation = _runtime_observation(run, arm)
    baseline_content_hash = _hash({'question_hash': question['question_hash'],
        'sources': sorted((e['url'], e['snapshot_hash']) for e in snapshots.values()),
        'interpretations': [{'statement': c.get('statement'), 'assessments': c.get('assessments', [])} for c in case.get('claims', [])]})
    obs.update(baseline_content_hash=baseline_content_hash, recorded_at=cases.now(), manifest_hash=campaign['manifest_hash'],
               case_content_hash=_hash({k: case.get(k) for k in ('id', 'version', 'question', 'claims', 'evidence')}),
               source_snapshots=[{'evidence_id': e['id'], 'url': e['url'], 'snapshot_hash': e['snapshot_hash']} for e in snapshots.values()],
               operational={'observed_usage': run.get('observed_usage') if run else None,
                            'usage_basis': run.get('usage_basis') if run else 'baseline case; no instrumented run',
                            'engine_elapsed_seconds': runtime_observation['engine_elapsed_seconds'],
                            'latency_seconds': None, 'tokens': None, 'billing': run.get('billing') if run else None},
               execution_provenance=runtime_observation, experiment_evidence=experiment_evidence)
    with closing(_connect(db)) as con, con:
        con.execute('BEGIN IMMEDIATE')
        previous = [json.loads(row[0]) for row in con.execute('SELECT body FROM research_observations WHERE campaign_id=?', (campaign_id,))]
        for old in previous:
            if (old['arm_id'], old['question_id'], old['repetition']) == (obs['arm_id'], obs['question_id'], obs['repetition']):
                raise ValueError('duplicate frozen evaluation slot')
            if obs.get('run_id') and old.get('run_id') == obs['run_id']:
                raise ValueError('completed run already recorded; repetitions require distinct executions')
            same_baseline = old.get('baseline_content_hash') == obs['baseline_content_hash'] and old['question_id'] == obs['question_id']
            if not obs.get('run_id') and ((old['case_id'], old['case_version']) == (obs['case_id'], obs['case_version']) or same_baseline):
                raise ValueError('baseline case outcome already recorded; repetitions require distinct outcomes')
        try:
            con.execute('INSERT INTO research_observations VALUES(?,?,?,?,?)',
                        (campaign_id, obs['arm_id'], obs['question_id'], obs['repetition'], _json(obs)))
        except sqlite3.IntegrityError as exc:
            raise ValueError('duplicate frozen evaluation slot') from exc
    return get(campaign_id, db=db)


def review(campaign_id, review_object, *, db=None):
    """Append an independent authored review of an immutable observed outcome."""
    if not isinstance(review_object, dict):
        raise ValueError('review must be an object')
    allowed = {'arm_id', 'question_id', 'repetition', 'expected_review_version',
               'reviewer', 'judgments', 'errors'}
    if set(review_object) - allowed:
        raise ValueError('unknown review fields; evidence binding is selected from the original observation')
    item = copy.deepcopy(review_object)
    expected = item.get('expected_review_version')
    if type(expected) is not int or expected < 0:
        raise ValueError('expected_review_version must be a nonnegative integer')
    if type(item.get('repetition')) is not int or item['repetition'] < 1:
        raise ValueError('repetition must be a positive integer')
    slot = (campaign_id, _text(item.get('arm_id'), 'arm_id'),
            _text(item.get('question_id'), 'question_id'), item['repetition'])
    with closing(_connect(db)) as con:
        campaign = _load(con, campaign_id)
        row = con.execute('SELECT body FROM research_observations WHERE campaign_id=? AND arm_id=? AND question_id=? AND repetition=?', slot).fetchone()
        if row is None:
            raise ValueError('completed observation not found for review')
        original = json.loads(row[0])
    case = cases.get(original['case_id'], version=original['case_version'], db=db)
    content_hash = _hash({k: case.get(k) for k in ('id', 'version', 'question', 'claims', 'evidence')})
    if content_hash != original['case_content_hash'] or original['manifest_hash'] != campaign['manifest_hash']:
        raise ValueError('original observation evidence or manifest integrity check failed')
    snapshots = {}
    for evidence in case['evidence']:
        text = evidence.get('snapshot_text')
        if text is not None:
            if not isinstance(text, str) or cases.digest(text) != evidence.get('snapshot_hash'):
                raise ValueError('source snapshot integrity check failed')
            snapshots[evidence['id']] = evidence
    experiment_evidence = original.get('experiment_evidence')
    if experiment_evidence is not None:
        resolved = _protocol_evidence(campaign, original, db=db)
        if resolved != experiment_evidence:
            raise ValueError('original experiment evidence no longer matches the persisted result')
    _validate_review_content(item, snapshots, experiment_evidence=experiment_evidence,
                             require_experiment_evidence='preparation' in campaign['manifest'])
    item.update(version=expected + 1, recorded_at=cases.now(), case_id=original['case_id'],
                case_version=original['case_version'], case_content_hash=original['case_content_hash'],
                manifest_hash=original['manifest_hash'], observation_hash=_hash(original),
                experiment_evidence=copy.deepcopy(original.get('experiment_evidence')),
                basis='Independent authored review; source occurrence is not semantic proof.')
    with closing(_connect(db)) as con, con:
        con.execute('BEGIN IMMEDIATE')
        current = con.execute('SELECT COALESCE(MAX(version),0) FROM research_evaluation_reviews WHERE campaign_id=? AND arm_id=? AND question_id=? AND repetition=?', slot).fetchone()[0]
        if current != expected:
            raise ValueError('review version changed; inspect the current review before appending')
        con.execute('INSERT INTO research_evaluation_reviews VALUES(?,?,?,?,?,?)', (*slot, item['version'], _json(item)))
    return get(campaign_id, db=db)


def get(campaign_id, *, db=None):
    with closing(_connect(db)) as con:
        result = _load(con, campaign_id)
        observations = [json.loads(r[0]) for r in con.execute(
            'SELECT body FROM research_observations WHERE campaign_id=? ORDER BY question_id,repetition,arm_id', (campaign_id,))]
        reviews = [json.loads(r[0]) for r in con.execute(
            'SELECT body FROM research_evaluation_reviews WHERE campaign_id=? ORDER BY version', (campaign_id,))]
    for observation in observations:
        observation['reviews'] = [r for r in reviews if (r['arm_id'], r['question_id'], r['repetition']) ==
                                  (observation['arm_id'], observation['question_id'], observation['repetition'])]
        observation['current_review'] = observation['reviews'][-1] if observation['reviews'] else None
        observation['review_version'] = observation['current_review']['version'] if observation['current_review'] else 0
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
        execution_limits = list(reasons)
        if not paired:
            execution_limits.append('No paired completed observations.')
        if source_differences:
            execution_limits.append('Paired observations have different source exposure; effects cannot be attributed to code alone.')
        paired_rows = [slots[(arm_id, q['id'], r)] for q, r in itertools.product(manifest['questions'], range(1, manifest['repetitions'] + 1))
                       if (a['id'], q['id'], r) in slots and (b['id'], q['id'], r) in slots for arm_id in (a['id'], b['id'])]
        if any(not row['execution_provenance'].get('attested') for row in paired_rows):
            execution_limits.append('One or more paired executions lack clean provenance matching the frozen code pin.')
        pairs.append({'arms': [a['id'], b['id']], 'comparable_design': not reasons,
                      'paired_observations': paired, 'reasons': reasons,
                      'comparable_execution': not execution_limits, 'execution_limitations': execution_limits, 'different_source_exposure': source_differences,
                      'limit': 'Recorded design comparability only; executable provenance and judgment quality require independent review.'})
    unknown_remaining = [{'arm_id': o['arm_id'], 'question_id': o['question_id'], 'repetition': o['repetition'],
                          'criteria': [key for key, judgment in (o['current_review'] or o)['judgments'].items() if judgment['status'] == 'unknown']}
                         for o in observations]
    result.update(review_coverage={'observations_with_reviews': sum(bool(o['reviews']) for o in observations),
                  'recorded_observations': len(observations), 'unknown_remaining': [item for item in unknown_remaining if item['criteria']]},
                  observations=observations, coverage={'recorded': len(observations), 'denominator': manifest['denominator'], 'missing_slots': missing},
                  error_inventory=[dict(e, source='observation', arm_id=o['arm_id'], question_id=o['question_id'], repetition=o['repetition']) for o in observations for e in o['errors']] +
                      [dict(e, source='review', review_version=r['version'], arm_id=r['arm_id'], question_id=r['question_id'], repetition=r['repetition']) for r in reviews for e in r['errors']],
                  paired_comparability=pairs, quality_summary='Manual criteria are retained separately. No automatic truth score or confidence percentage.')
    return result
