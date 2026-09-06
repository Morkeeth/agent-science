"""Real local acceptance runs; deliberately corrupted temporary storage is a negative control."""
import copy
import json

import pytest

from clearance import cases, night_runs, research_evaluation as evaluation, research_protocols
from test_evaluation_prepare import ready_protocol, prepared_spec, LIMITS


@pytest.fixture
def flow(tmp_path, monkeypatch):
    monkeypatch.setattr(night_runs.execution_provenance, 'capture', lambda: {
        'code_ref': None, 'source_sha256': None, 'dirty': None,
        'basis': 'Local synthetic fixture; runtime identity not measured'})
    db = tmp_path / 'binding.db'
    protocol = ready_protocol(tmp_path, db)
    case = cases.get(protocol['case_id'], db=db)
    case['version'] += 1
    text = 'Synthetic fixture, not a scientific result.'
    case['evidence'] = [{'id': 'fixture', 'url': 'https://example.invalid/fixture',
        'kind': 'research_repository', 'status': 'NO_MATCHED_QUOTE', 'snapshot_text': text, 'snapshot_hash': cases.digest(text)}]
    cases._save(case, db=db)
    fields = {k: protocol[k] for k in research_protocols.REQUIRED + ('kind', 'check_sha256')}
    protocol = research_protocols.create(case['id'], fields, protocol_id=protocol['id'], db=db)
    spec = prepared_spec({'id': protocol['id'], 'version': protocol['version']})
    for arm in spec['arms']:
        arm['code_ref'] = protocol['baseline' if arm['id'] == 'baseline' else 'intervention']
        arm['kind'] = 'retrieval'
    campaign = evaluation.prepare(spec, db=db)
    run = night_runs.start(case['question'], case_id=case['id'], policy=LIMITS, db=db)
    run = night_runs.resume(run['id'], proposal={'case_version': case['version'], 'findings': [],
        'next_action': {'kind': 'finish', 'reason': 'Synthetic source inspection complete.'}}, db=db)
    assert run['status'] == 'completed'
    check = tmp_path / 'acceptance.py'
    check.write_text('print("fixture")\n')
    execution = research_protocols.execute(protocol['id'], version=protocol['version'], check=check,
                                           trusted=True, db=db)
    assert execution['state'] == 'COMPLETED'
    obs = {'arm_id': 'baseline', 'question_id': 'q1', 'repetition': 1, 'case_id': case['id'],
        'case_version': case['version'], 'run_id': run['id'], 'question_hash': cases.digest(case['question']),
        'mode': 'snapshot_replay', 'resource_limits': LIMITS, 'reviewer': 'Fixture reviewer',
        'judgments': {k: {'status': 'unknown', 'rationale': 'Synthetic control only.', 'anchors': []}
                      for k in evaluation.CRITERIA}}
    obs['judgments']['experiment_specificity']['status'] = 'pass'
    review = {k: copy.deepcopy(obs[k]) for k in ('arm_id', 'question_id', 'repetition', 'reviewer', 'judgments')}
    review['expected_review_version'] = 0
    return db, protocol, spec, campaign, execution, obs, review


def corrupt(db, execution, fault):
    with cases.connect(db) as con:
        result = json.loads(con.execute('SELECT body FROM experiments WHERE id=?',
                                       (execution['experiment_id'],)).fetchone()[0])
        receipt = copy.deepcopy(execution)
        if fault == 'missing':
            con.execute('DELETE FROM experiments WHERE id=?', (result['id'],))
            return
        if fault == 'invalid': result['valid'] = False
        if fault == 'digest': result['acceptance_sha256'] = '0' * 64
        if fault == 'acceptance_source': result['acceptance_source'] = 'print(\"changed\")\n'
        if fault == 'pins': result['pins']['candidate'] = '0' * 40
        if fault == 'case': result['case_id'] = 'other-case'
        if fault == 'version': result['case_version'] += 1
        if fault == 'result_id': result['id'] = 'other-result'
        if fault == 'repo': result['repo'] = '/synthetic/different-repo'
        if fault == 'malformed_runs': result['runs'] = [None]
        if fault == 'summary': result['summary'] = 'Changed after execution'
        if fault == 'execution_identity': receipt['protocol_id'] = 'other-protocol'
        if fault == 'old_execution': receipt['started_at'] = '2000-01-01T00:00:00+00:00'
        if fault == 'old_result': result['recorded_at'] = '2000-01-01T00:00:00+00:00'
        if fault == 'naive_time': receipt['started_at'] = '2026-01-01T00:00:00'
        if fault == 'missing_time': receipt.pop('started_at')
        if fault == 'coherent_changed_result':
            result['summary'] = 'Replaced after observation'
            receipt['result'] = cases.experiment_summary(result)
        con.execute('UPDATE experiments SET body=? WHERE id=?', (json.dumps(result), execution['experiment_id']))
        con.execute('UPDATE night_protocol_executions SET body=? WHERE id=?', (json.dumps(receipt), execution['id']))


def test_actual_execution_record_and_independent_review(flow):
    db, protocol, spec, campaign, execution, obs, review = flow
    before = json.dumps(evaluation.get(campaign['id'], db=db)['manifest'], sort_keys=True)
    recorded = evaluation.record(campaign['id'], obs, db=db)
    evidence = recorded['observations'][0]['experiment_evidence']
    assert evidence['experiment_id'] == execution['experiment_id']
    assert evidence['acceptance_sha256'] == protocol['check_sha256']
    assert len(evidence['experiment_sha256']) == len(evidence['execution_sha256']) == 64
    reviewed = evaluation.review(campaign['id'], review, db=db)
    assert reviewed['observations'][0]['current_review']['experiment_evidence'] == evidence
    assert json.dumps(reviewed['manifest'], sort_keys=True) == before
    assert reviewed['observations'][0]['judgments']['experiment_specificity']['status'] == 'pass'


@pytest.mark.parametrize('stage', ['record', 'review'])
@pytest.mark.parametrize('fault', ['missing', 'invalid', 'digest', 'pins', 'case', 'version', 'result_id',
    'repo', 'summary', 'malformed_runs', 'acceptance_source', 'execution_identity', 'old_execution', 'old_result', 'naive_time', 'missing_time'])
def test_unresolved_or_mismatched_result_cannot_authorize_pass(flow, stage, fault):
    db, _, _, campaign, execution, obs, review = flow
    if stage == 'review':
        evaluation.record(campaign['id'], obs, db=db)
    before = evaluation.get(campaign['id'], db=db)
    corrupt(db, execution, fault)
    with pytest.raises(ValueError):
        if stage == 'record': evaluation.record(campaign['id'], obs, db=db)
        else: evaluation.review(campaign['id'], review, db=db)
    assert evaluation.get(campaign['id'], db=db) == before


def test_review_rejects_coherent_result_replacement_after_observation(flow):
    db, _, _, campaign, execution, obs, review = flow
    evaluation.record(campaign['id'], obs, db=db)
    corrupt(db, execution, 'coherent_changed_result')
    with pytest.raises(ValueError, match='original experiment evidence'):
        evaluation.review(campaign['id'], review, db=db)


def test_existing_execution_cannot_be_prepared_as_unrun(flow):
    db, _, spec, _, _, _, _ = flow
    with pytest.raises(ValueError, match='already has execution history'):
        evaluation.prepare(spec, db=db)
