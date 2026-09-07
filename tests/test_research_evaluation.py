"""Synthetic persisted cases exercise controls; no scientific measurements."""
import copy
import json
import pytest
from clearance import cases, night_runs, research_evaluation as evaluation

QUESTION = 'Under which tasks does artificial memory help?'
TEXT = 'Artificial fixture reports repository tasks and explicitly does not establish general effectiveness.'
LIMITS = {'discovery_calls': 8, 'document_reads': 20, 'reasoning_calls': 12, 'rounds': 3}


def spec():
    return {'title': 'Control campaign', 'authored_by': 'Independent fixture author',
            'rubric_provenance': 'Authored independently before generated answers; artificial control inputs.',
            'questions': [{'id': 'q1', 'topic': 'memory', 'question': QUESTION,
                           'expected_distinctions': ['Task specificity is not general effectiveness.']}],
            'arms': [{'id': 'candidate', 'kind': 'synthesis', 'code_ref': 'a' * 40,
                      'mode': 'snapshot_replay', 'resource_limits': LIMITS},
                     {'id': 'baseline', 'kind': 'retrieval', 'baseline_policy': 'Only retrieve original saved sources.',
                      'mode': 'snapshot_replay', 'resource_limits': LIMITS}],
            'repetitions': 2, 'rubric': {k: 'Inspect independently: ' + k for k in evaluation.CRITERIA}}


@pytest.fixture
def saved(tmp_path, monkeypatch):
    # Filesystem provenance is an instrumentation effect; controls below attach
    # explicit clean/dirty captures to real completed runs when testing that rule.
    monkeypatch.setattr(night_runs.execution_provenance, 'capture', lambda: {
        'code_ref': None, 'source_sha256': None, 'dirty': None,
        'basis': 'Artificial fixture; executable provenance unmeasured'})
    db = tmp_path / 'isolated-evaluation.db'
    campaign = evaluation.create(spec(), db=db)
    case = cases.create(QUESTION, db=db)
    case['evidence'] = [{'id': 'e1', 'url': 'https://example.org/artificial', 'status': 'NO_MATCHED_QUOTE', 'kind': 'research_repository', 'quote': None,
                         'snapshot_text': TEXT, 'snapshot_hash': cases.digest(TEXT)}]
    case['version'] += 1
    cases._save(case, db=db)
    run = night_runs.start(QUESTION, case_id=case['id'], db=db)
    proposal = {'case_version': case['version'], 'next_action': {'kind': 'finish', 'reason': 'Fixture source cannot establish an effect.'},
                'findings': [{'statement': 'General memory effectiveness remains unresolved.', 'relation': 'unresolved',
                              'rationale': 'The artificial fixture cannot establish a general result.'}]}
    run = night_runs.resume(run['id'], proposal=proposal, db=db)
    obs = {'arm_id': 'candidate', 'question_id': 'q1', 'repetition': 1, 'case_id': case['id'],
           'case_version': run['case_version'], 'run_id': run['id'], 'question_hash': cases.digest(QUESTION),
           'mode': 'snapshot_replay', 'resource_limits': LIMITS, 'reviewer': 'Independent fixture reviewer',
           'judgments': {k: {'status': 'unknown', 'rationale': 'Not measured by artificial control.', 'anchors': []}
                         for k in evaluation.CRITERIA}}
    return db, campaign, obs


def test_persisted_completed_run_and_unknowns(saved):
    db, campaign, obs = saved
    result = evaluation.record(campaign['id'], obs, db=db)
    assert result['coverage']['recorded'] == 1
    assert len(result['coverage']['missing_slots']) == 3
    assert result['manifest_hash'] == campaign['manifest_hash']
    recorded = result['observations'][0]
    assert recorded['operational']['billing'] is None
    assert recorded['operational']['latency_seconds'] is None
    assert recorded['judgments']['scope_errors']['status'] == 'unknown'
    assert recorded['source_snapshots'][0]['snapshot_hash'] == cases.digest(TEXT)
    assert result['paired_comparability'][0]['comparable_design'] is False
    assert 'retrieval is not synthesis' in result['paired_comparability'][0]['reasons'][0]
    with pytest.raises(ValueError, match='duplicate'):
        evaluation.record(campaign['id'], obs, db=db)


@pytest.mark.parametrize('field,value,message', [
    ('question_hash', 'wrong', 'question hash'), ('arm_id', 'unknown', 'unknown arm'),
    ('repetition', True, 'repetition'), ('case_version', 1, 'exact observed'),
    ('mode', 'fresh_web', 'mode or resource'), ('resource_limits', {'calls': 2}, 'mode or resource'),
    ('usage', {'calls': 0}, 'unknown observation'),
])
def test_invalid_observation_controls(saved, field, value, message):
    db, campaign, obs = saved
    obs[field] = value
    with pytest.raises(ValueError, match=message):
        evaluation.record(campaign['id'], obs, db=db)
    assert evaluation.get(campaign['id'], db=db)['coverage']['recorded'] == 0


def test_planned_run_and_reused_question_rejected(saved):
    db, campaign, obs = saved
    planned = night_runs.start(QUESTION, case_id=obs['case_id'], db=db)
    obs['run_id'] = planned['id']
    with pytest.raises(ValueError, match='completed'):
        evaluation.record(campaign['id'], obs, db=db)
    different = night_runs.start('Different question', db=db)
    obs.update(case_id=different['case_id'], case_version=1)
    with pytest.raises(ValueError, match='case question mismatch'):
        evaluation.record(campaign['id'], obs, db=db)


def test_anchor_and_snapshot_failure_controls(saved):
    db, campaign, obs = saved
    judgment = obs['judgments']['citation_correctness']
    judgment['status'] = 'pass'
    with pytest.raises(ValueError, match='requires inspected'):
        evaluation.record(campaign['id'], obs, db=db)
    judgment['anchors'] = [{'evidence_id': 'e1', 'quote': 'Fabricated quotation'}]
    with pytest.raises(ValueError, match='does not occur'):
        evaluation.record(campaign['id'], obs, db=db)
    judgment['anchors'][0]['quote'] = TEXT
    result = evaluation.record(campaign['id'], obs, db=db)
    assert result['observations'][0]['judgments']['citation_correctness']['anchors'][0]['snapshot_hash'] == cases.digest(TEXT)
    case = cases.get(obs['case_id'], version=obs['case_version'], db=db)
    case['evidence'][0]['snapshot_text'] = 'Tampered snapshot'
    with cases.connect(db) as con:
        con.execute('UPDATE revisions SET body=? WHERE case_id=? AND version=?', (json.dumps(case), case['id'], case['version']))
    obs['repetition'] = 2
    with pytest.raises(ValueError, match='snapshot integrity'):
        evaluation.record(campaign['id'], obs, db=db)


def test_prepared_campaign_rejects_unsupported_experiment_pass(saved):
    db, _, obs = saved
    value = spec()
    value.update(operational_rubric={
        'source_recovery': 'Missing original source stays unknown.',
        'counterevidence': 'Missing contrary evidence stays unknown.',
        'experiment_executability': 'A pass requires completed frozen protocol evidence.'},
        unknown_resources=['protocol execution'], protocol=None)
    campaign = evaluation.prepare(value, db=db)
    run = night_runs.get(obs['run_id'], db=db)
    run['created_at'] = cases.now()
    night_runs._save(run, db)
    obs['judgments']['experiment_specificity'].update(
        status='pass', rationale='No protocol or experiment exists for this negative control.')
    with pytest.raises(ValueError, match='completed frozen protocol execution'):
        evaluation.record(campaign['id'], obs, db=db)
    assert evaluation.get(campaign['id'], db=db)['coverage']['recorded'] == 0


@pytest.mark.parametrize('alias', ['HEAD', 'main', 'a12345', 'evaluated-head', 'a'*39])
def test_mutable_baseline_rejected(tmp_path, alias):
    value = spec(); value['arms'][0]['code_ref'] = alias
    with pytest.raises(ValueError, match='immutable commit'):
        evaluation.create(value, db=tmp_path / 'new.db')


def test_baseline_case_record_and_manifest_integrity(saved):
    db, campaign, obs = saved
    obs.pop('run_id'); obs['arm_id'] = 'baseline'
    result = evaluation.record(campaign['id'], obs, db=db)
    assert result['observations'][0]['operational']['observed_usage'] is None
    assert result['coverage']['denominator'] == 4
    with cases.connect(db) as con:
        row = json.loads(con.execute('SELECT body FROM research_campaigns').fetchone()[0])
        row['manifest']['repetitions'] = 100
        con.execute('UPDATE research_campaigns SET body=?', (json.dumps(row),))
    with pytest.raises(ValueError, match='manifest integrity'):
        evaluation.get(campaign['id'], db=db)


def test_real_repetition_may_not_reuse_same_completed_run(saved):
    db, campaign, obs = saved
    evaluation.record(campaign['id'], obs, db=db)
    obs['repetition'] = 2
    with pytest.raises(ValueError, match='already recorded'):
        evaluation.record(campaign['id'], obs, db=db)


def test_fresh_web_cannot_be_declared_from_replay(saved):
    db, _, obs = saved
    fresh_spec = spec()
    fresh_spec['arms'][0]['mode'] = 'fresh_web'
    campaign = evaluation.create(fresh_spec, db=db)
    run = night_runs.start(QUESTION, case_id=obs['case_id'], db=db)
    run = night_runs.resume(run['id'], proposal={'case_version': run['case_version'], 'findings': [],
        'next_action': {'kind': 'finish', 'reason': 'No live source was read in this artificial run.'}}, db=db)
    obs.update(run_id=run['id'], case_version=run['case_version'], mode='fresh_web')
    with pytest.raises(ValueError, match='observed online fetch'):
        evaluation.record(campaign['id'], obs, db=db)


def test_campaign_cannot_be_frozen_after_run(saved):
    db, _, obs = saved
    late_campaign = evaluation.create(spec(), db=db)
    with pytest.raises(ValueError, match='predates frozen campaign'):
        evaluation.record(late_campaign['id'], obs, db=db)


def test_same_design_keeps_pairing_and_error_inventory(saved):
    db, _, obs = saved
    value = spec()
    value['arms'][1] = dict(value['arms'][0], id='other', code_ref='b'*40)
    campaign = evaluation.create(value, db=db)
    for arm in ['candidate', 'other']:
        run = night_runs.start(QUESTION, case_id=obs['case_id'], db=db)
        run = night_runs.resume(run['id'], proposal={'case_version': run['case_version'], 'findings': [],
            'next_action': {'kind': 'finish', 'reason': 'Fixture comparison has no measured scientific result.'}}, db=db)
        changed = copy.deepcopy(obs)
        changed.update(arm_id=arm, run_id=run['id'], case_version=run['case_version'],
                       errors=[{'kind': 'missing evidence', 'detail': 'Artificial fixture is not real scientific evidence.'}])
        result = evaluation.record(campaign['id'], changed, db=db)
    assert result['paired_comparability'][0]['comparable_design'] is True
    assert result['paired_comparability'][0]['paired_observations'] == 1
    assert len(result['error_inventory']) == 2
    assert result['paired_comparability'][0]['different_source_exposure'] == []


def test_retrieval_plan_cannot_be_recorded_as_baseline(saved):
    db, campaign, obs = saved
    case = cases.create(QUESTION, db=db)
    obs.pop('run_id')
    obs.update(arm_id='baseline', case_id=case['id'], case_version=case['version'])
    with pytest.raises(ValueError, match='empty plan'):
        evaluation.record(campaign['id'], obs, db=db)


def instrument_run(db, obs, *, dirty=False, code_ref='a'*40, missing_duration=False, step_ref=None):
    """Substitute measured filesystem/timer effects in a real persisted completed run."""
    run = night_runs.get(obs['run_id'], db=db)
    run['runtime'] = {'code_ref': code_ref, 'source_sha256': 'd'*64, 'dirty': dirty, 'basis': 'Artificial instrumentation control'}
    for step in run['steps']:
        step['runtime'] = dict(run['runtime'], code_ref=step_ref or code_ref)
        if missing_duration:
            step.pop('elapsed_seconds', None)
        else:
            step['elapsed_seconds'] = 0.25
    night_runs._save(run, db)
    return run


def test_clean_runtime_wrong_code_rejected(saved):
    db, campaign, obs = saved
    instrument_run(db, obs, code_ref='b'*40)
    with pytest.raises(ValueError, match='clean runtime code_ref differs'):
        evaluation.record(campaign['id'], obs, db=db)


def test_mixed_step_runtime_wrong_code_rejected(saved):
    db, campaign, obs = saved
    instrument_run(db, obs, step_ref='b'*40)
    with pytest.raises(ValueError, match='step.*code_ref differs'):
        evaluation.record(campaign['id'], obs, db=db)


def test_dirty_provenance_retains_unknown_execution(saved):
    db, campaign, obs = saved
    instrument_run(db, obs, dirty=True, code_ref='b'*40, missing_duration=True)
    result = evaluation.record(campaign['id'], obs, db=db)
    row = result['observations'][0]
    assert row['execution_provenance']['attested'] is False
    assert row['operational']['engine_elapsed_seconds'] is None
    assert result['paired_comparability'][0]['comparable_execution'] is False


def test_clean_runtime_copies_observed_operation_duration(saved):
    db, campaign, obs = saved
    run = instrument_run(db, obs)
    result = evaluation.record(campaign['id'], obs, db=db)
    row = result['observations'][0]
    assert row['execution_provenance']['attested'] is True
    assert row['operational']['engine_elapsed_seconds'] == len(run['steps']) * 0.25
    assert row['operational']['latency_seconds'] is None


@pytest.mark.parametrize('changed_source', [False, True])
def test_paired_clean_runtime_executions_and_source_exposure(saved, changed_source):
    db, _, obs = saved
    value = spec()
    value['arms'][1] = dict(value['arms'][0], id='other', code_ref='b'*40)
    campaign = evaluation.create(value, db=db)
    for arm, pin in [('candidate', 'a'*40), ('other', 'b'*40)]:
        if arm == 'other' and changed_source:
            case = cases.get(obs['case_id'], db=db)
            case['version'] += 1
            case['evidence'][0]['snapshot_text'] += ' Extra source material.'
            case['evidence'][0]['snapshot_hash'] = cases.digest(case['evidence'][0]['snapshot_text'])
            cases._save(case, db=db)
        run = night_runs.start(QUESTION, case_id=obs['case_id'], db=db)
        run = night_runs.resume(run['id'], proposal={'case_version': run['case_version'], 'findings': [],
            'next_action': {'kind': 'finish', 'reason': 'Artificial paired runtime control.'}}, db=db)
        changed = copy.deepcopy(obs)
        changed.update(arm_id=arm, run_id=run['id'], case_version=run['case_version'])
        instrument_run(db, changed, code_ref=pin)
        result = evaluation.record(campaign['id'], changed, db=db)
    pair = result['paired_comparability'][0]
    assert pair['comparable_execution'] is (not changed_source)
    assert bool(pair['different_source_exposure']) is changed_source
    assert bool(pair['execution_limitations']) is changed_source


def review_input(obs):
    return {'arm_id': obs['arm_id'], 'question_id': obs['question_id'], 'repetition': obs['repetition'],
            'expected_review_version': 0, 'reviewer': 'Independent reviewer', 'judgments': copy.deepcopy(obs['judgments']),
            'errors': [{'kind': 'missing contrary evidence', 'detail': 'Independent fixture review found no contrary paper.'}]}


def test_review_appends_history_and_preserves_original(saved):
    db, campaign, obs = saved
    evaluation.record(campaign['id'], obs, db=db)
    with cases.connect(db) as con:
        original_bytes = con.execute('SELECT body FROM research_observations').fetchone()[0]
    request = review_input(obs)
    request['judgments']['citation_correctness'].update(status='pass', rationale='Inspected the actual pinned quotation.',
        anchors=[{'evidence_id': 'e1', 'quote': TEXT}])
    result = evaluation.review(campaign['id'], request, db=db)
    reviewed = result['observations'][0]
    assert reviewed['review_version'] == 1
    assert reviewed['judgments']['citation_correctness']['status'] == 'unknown'
    assert reviewed['current_review']['judgments']['citation_correctness']['status'] == 'pass'
    assert reviewed['current_review']['case_version'] == obs['case_version']
    assert reviewed['current_review']['case_content_hash'] == reviewed['case_content_hash']
    assert result['review_coverage']['observations_with_reviews'] == 1
    assert 'citation_correctness' not in result['review_coverage']['unknown_remaining'][0]['criteria']
    assert result['error_inventory'][0]['source'] == 'review'
    request['expected_review_version'] = 1
    request['judgments']['citation_correctness']['status'] = 'unknown'
    result = evaluation.review(campaign['id'], request, db=db)
    assert [r['version'] for r in result['observations'][0]['reviews']] == [1, 2]
    with cases.connect(db) as con:
        assert con.execute('SELECT body FROM research_observations').fetchone()[0] == original_bytes


def test_review_rejects_fabrication_and_uses_original_case_version(saved):
    db, campaign, obs = saved
    evaluation.record(campaign['id'], obs, db=db)
    newer = cases.get(obs['case_id'], db=db)
    newer['version'] += 1
    newer['evidence'][0]['snapshot_text'] += ' Later-only statement.'
    newer['evidence'][0]['snapshot_hash'] = cases.digest(newer['evidence'][0]['snapshot_text'])
    cases._save(newer, db=db)
    request = review_input(obs)
    request['judgments']['citation_correctness'].update(status='pass',
        anchors=[{'evidence_id': 'e1', 'quote': 'Later-only statement.'}])
    with pytest.raises(ValueError, match='does not occur'):
        evaluation.review(campaign['id'], request, db=db)
    request['judgments']['citation_correctness']['anchors'][0]['quote'] = TEXT
    result = evaluation.review(campaign['id'], request, db=db)
    assert result['observations'][0]['current_review']['case_version'] == obs['case_version']


def test_review_stale_and_concurrent_guard(saved):
    from concurrent.futures import ThreadPoolExecutor
    db, campaign, obs = saved
    evaluation.record(campaign['id'], obs, db=db)
    request = review_input(obs)
    def attempt(_):
        try:
            evaluation.review(campaign['id'], request, db=db)
            return 'saved'
        except ValueError as exc:
            return str(exc)
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(attempt, range(2)))
    assert outcomes.count('saved') == 1
    assert sum('review version changed' in x for x in outcomes) == 1
    with pytest.raises(ValueError, match='review version changed'):
        evaluation.review(campaign['id'], request, db=db)
    assert len(evaluation.get(campaign['id'], db=db)['observations'][0]['reviews']) == 1


def test_review_refuses_changed_original_evidence(saved):
    db, campaign, obs = saved
    evaluation.record(campaign['id'], obs, db=db)
    case = cases.get(obs['case_id'], version=obs['case_version'], db=db)
    case['evidence'][0]['snapshot_text'] = 'Replaced historical source bytes.'
    case['evidence'][0]['snapshot_hash'] = cases.digest(case['evidence'][0]['snapshot_text'])
    with cases.connect(db) as con:
        con.execute('UPDATE revisions SET body=? WHERE case_id=? AND version=?', (json.dumps(case), case['id'], case['version']))
    with pytest.raises(ValueError, match='integrity check'):
        evaluation.review(campaign['id'], review_input(obs), db=db)


@pytest.mark.parametrize('value', [-1, True, '0', None])
def test_review_expected_version_requires_exact_integer(saved, value):
    db, campaign, obs = saved
    evaluation.record(campaign['id'], obs, db=db)
    request = review_input(obs); request['expected_review_version'] = value
    with pytest.raises(ValueError, match='nonnegative integer'):
        evaluation.review(campaign['id'], request, db=db)


@pytest.mark.parametrize('events,counter', [
    ([], 1),
    ([{'route': 'source_metadata', 'outcome': 'failed', 'url': 'https://api.crossref.org/works/10.1234/test'}], 0),
    ([{'route': 'source_metadata', 'outcome': 'checked', 'response_hash': 'd'*64}], 0),
])
def test_replay_rejects_registry_activity_including_failed_requests(saved, events, counter):
    db, campaign, obs = saved
    run = night_runs.get(obs['run_id'], db=db)
    run['observed_usage']['metadata_responses'] = counter
    run['steps'][0]['observed_events'] = events
    night_runs._save(run, db)
    with pytest.raises(ValueError, match='registry requests'):
        evaluation.record(campaign['id'], obs, db=db)


def test_bare_imported_claim_does_not_count_as_synthesis(saved):
    db, campaign, obs = saved
    case = cases.get(obs['case_id'], db=db)
    for claim in case['claims']:
        claim['assessments'] = []
    with cases.connect(db) as con:
        con.execute('UPDATE revisions SET body=? WHERE case_id=? AND version=?', (json.dumps(case), case['id'], case['version']))
    with pytest.raises(ValueError, match='active assessment'):
        evaluation.record(campaign['id'], obs, db=db)


def test_baseline_noop_version_bump_does_not_fill_repetition(saved):
    db, campaign, obs = saved
    obs.pop('run_id'); obs['arm_id'] = 'baseline'
    evaluation.record(campaign['id'], obs, db=db)
    case = cases.get(obs['case_id'], db=db)
    case['version'] += 1
    cases._save(case, db=db)
    obs.update(case_version=case['version'], repetition=2)
    with pytest.raises(ValueError, match='already recorded'):
        evaluation.record(campaign['id'], obs, db=db)


def test_unknown_run_limit_key_rejected_before_freeze(tmp_path):
    value = spec(); value['arms'][0]['resource_limits'] = dict(LIMITS, metadata_checks=2)
    with pytest.raises(ValueError, match='supported run limit keys'):
        evaluation.create(value, db=tmp_path / 'new.db')


def test_same_sources_for_distinct_questions_are_not_duplicate_baselines(saved):
    db, _, obs = saved
    value = spec()
    value['questions'].append(dict(value['questions'][0], id='q2', question='A distinct artificial question?'))
    campaign = evaluation.create(value, db=db)
    obs.pop('run_id'); obs['arm_id'] = 'baseline'
    evaluation.record(campaign['id'], obs, db=db)
    case = cases.get(obs['case_id'], db=db)
    case.update(id='distinct-question-case', version=1, question=value['questions'][1]['question'])
    cases._save(case, db=db)
    obs.update(case_id=case['id'], case_version=1, question_id='q2', question_hash=cases.digest(case['question']))
    assert evaluation.record(campaign['id'], obs, db=db)['coverage']['recorded'] == 2


def test_offline_registry_noop_remains_snapshot_replay(saved):
    db, campaign, obs = saved
    run = night_runs.get(obs['run_id'], db=db)
    run['steps'][0]['observed_events'] = [{'route': 'source_metadata', 'outcome': 'not_checked'}]
    night_runs._save(run, db)
    assert evaluation.record(campaign['id'], obs, db=db)['coverage']['recorded'] == 1
