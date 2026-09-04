"""Local fixture tests: no personal store, provider requests or model calls."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import pytest
from clearance import cases, research_cli, research_protocols as protocols, research_workflow as workflow


@pytest.fixture
def case_store(tmp_path):
    db = tmp_path / 'cases.sqlite'
    data = {'id': 'case-local', 'version': 1, 'question': 'Does the change pass the fixed acceptance task?',
            'created_at': cases.now(), 'checked_at': 'baseline-marker', 'repo': None,
            'official_domains': [], 'provided_sources': [], 'evidence': [], 'trace': [], 'limits': [],
            'claims': [{'id': 'claim-local', 'statement': 'Candidate should produce the expected output.', 'assessments': [], 'source_urls': []}]}
    return db, cases._save(data, db=db)


def test_follow_reads_do_not_acknowledge_or_check_web(case_store):
    db, case = case_store
    assert workflow.follow(case['id'], db=db)['version'] == 1
    from clearance import synthesis
    assert workflow.updates(db=db)['updates'] == []
    synthesis.apply(case['id'], 1, {'findings': [{'statement': 'The claim remains unresolved.', 'relation': 'unresolved', 'rationale': 'No primary evidence inspected yet.'}]}, db=db)
    first = workflow.updates(db=db)
    assert first == workflow.updates(db=db)
    assert first['checked_online'] is False
    assert first['updates'][0]['from_version'] == 1
    assert cases.get(case['id'], db=db)['checked_at'] == 'baseline-marker'
    workflow.follow(case['id'], db=db)
    assert workflow.updates(db=db)['updates'] == []


def test_draft_and_execution_boundaries(case_store):
    db, case = case_store
    draft = workflow.handle({'action': 'experiment-plan', 'case_id': case['id'], 'db': db})
    assert draft['status'] == 'DRAFT'
    assert 'tasks' in draft['missing']
    revised = protocols.create(case['id'], {'hypothesis': 'A fixed check passes'}, protocol_id=draft['id'], db=db)
    assert revised['version'] == 2
    assert 'hypothesis' in protocols.get(draft['id'], version=1, db=db)['missing']
    with pytest.raises(ValueError, match='CLI-only'):
        workflow.handle({'action': 'execute-protocol', 'protocol_id': draft['id'], 'trusted': True})
    with pytest.raises(ValueError, match='READY'):
        protocols.execute(draft['id'], check='unused', trusted=True, db=db)
    with pytest.raises(ValueError, match='claim not found'):
        protocols.create(case['id'], {'claim_refs': [{'claim_id': 'fabricated', 'version': 1}]}, db=db)


def test_cli_parses_host_proposal_and_db():
    parser = argparse.ArgumentParser()
    research_cli.add_parser(parser.add_subparsers(dest='command'))
    args = parser.parse_args(['research', '--db', '/tmp/private.sqlite', 'resume', 'r1', '--proposal', '{"case_version":1}', '--json'])
    assert args.db == '/tmp/private.sqlite'
    assert args.proposal == {'case_version': 1}
    with pytest.raises(SystemExit):
        parser.parse_args(['research', 'resume', 'r1', '--proposal', '[]'])


def test_real_protocol_executes_frozen_git_comparison(case_store, tmp_path, capsys, monkeypatch):
    db, case = case_store
    repo = tmp_path / 'repo'
    repo.mkdir()
    def git(*args):
        return subprocess.check_output(['git', '-C', str(repo), *args], text=True, stderr=subprocess.PIPE).strip()
    git('init')
    git('config', 'user.name', 'Fixture')
    git('config', 'user.email', 'fixture@example.invalid')
    (repo / 'value.txt').write_text('wrong')
    git('add', '.')
    git('commit', '-m', 'baseline')
    baseline = git('rev-parse', 'HEAD')
    (repo / 'value.txt').write_text('expected')
    git('commit', '-am', 'intervention')
    intervention = git('rev-parse', 'HEAD')
    check = tmp_path / 'acceptance.py'
    check.write_text('from pathlib import Path\nassert Path("value.txt").read_text() == "expected"\n')
    fields = {'hypothesis': 'The candidate fixes the output.', 'claim_refs': [{'claim_id': 'claim-local', 'version': 1}],
              'repo': str(repo), 'tasks': ['Read the value file and match expected output'], 'baseline': baseline,
              'intervention': intervention, 'outcomes': ['Acceptance exit code: zero means expected output'],
              'budget': {'runs': 1, 'timeout': 10, 'basis': 'One fixed task on each of two pinned commits'},
              'stopping_rule': 'Stop after one paired run, including failures.',
              'check_sha256': hashlib.sha256(check.read_bytes()).hexdigest()}
    plan = protocols.create(case['id'], fields, db=db)
    assert plan['status'] == 'READY'
    with pytest.raises(ValueError, match='acknowledgement'):
        protocols.execute(plan['id'], check=check, db=db)
    check.write_text('raise RuntimeError("changed check")')
    with pytest.raises(ValueError, match='differs'):
        protocols.execute(plan['id'], check=check, trusted=True, db=db)
    check.write_text('from pathlib import Path\nassert Path("value.txt").read_text() == "expected"\n')
    parser = argparse.ArgumentParser()
    research_cli.add_parser(parser.add_subparsers(dest='command'))
    args = parser.parse_args(['research', 'execute-protocol', plan['id'], '--db', str(db), '--check', str(check), '--trusted', '--json'])
    from clearance import experiments
    original_compare = experiments.compare
    def change_caller_path_after_capture(*args, **kwargs):
        check.write_text('raise RuntimeError("caller path changed after capture")')
        assert Path(kwargs['check']) != check
        return original_compare(*args, **kwargs)
    monkeypatch.setattr(experiments, 'compare', change_caller_path_after_capture)
    assert args.func(args) == 0
    monkeypatch.setattr(experiments, 'compare', original_compare)
    check.write_text('from pathlib import Path\nassert Path("value.txt").read_text() == "expected"\n')
    receipt = json.loads(capsys.readouterr().out)
    assert receipt['state'] == 'COMPLETED'
    assert 'acceptance_source' not in receipt['result']
    assert all('output_tail' not in row for row in receipt['result']['runs'])
    repeated = protocols.execute(plan['id'], check=check, trusted=True, db=db)
    assert repeated['experiment_id'] == receipt['experiment_id']
    assert len(cases.get(case['id'], db=db)['experiments']) == 1
    assert receipt['result']['aggregate']['baseline']['passed'] == 0
    assert receipt['result']['aggregate']['candidate']['passed'] == 1
    assert receipt['result']['pins'] == {'baseline': baseline, 'candidate': intervention}
    saved = cases.get(case['id'], db=db)['experiments']
    assert receipt['experiment_id'] == saved[0]['id']
    assert protocols.get(plan['id'], db=db)['executions'][0]['experiment_id'] == saved[0]['id']
    from clearance import experiments
    original_compare = experiments.compare
    racing_plan = protocols.create(case['id'], fields, db=db)
    def race_before_runner(*args, **kwargs):
        case['version'] = 2
        cases._save(case, db=db)
        # Changing the original script after capture must not affect execution.
        check.write_text('raise RuntimeError("caller path changed after capture")')
        assert Path(kwargs['check']) != check
        return original_compare(*args, **kwargs)
    monkeypatch.setattr(experiments, 'compare', race_before_runner)
    with pytest.raises(ValueError, match='case changed'):
        protocols.execute(racing_plan['id'], check=check, trusted=True, db=db)
    assert protocols.get(racing_plan['id'], db=db)['executions'][0]['state'] == 'FAILED'
    assert len(cases.get(case['id'], db=db)['experiments']) == 1
    check.write_text('from pathlib import Path\nassert Path("value.txt").read_text() == "expected"\n')
    interrupted_plan = protocols.create(case['id'], fields, db=db)
    def interrupt(*args, **kwargs):
        raise KeyboardInterrupt('fixture process interruption')
    monkeypatch.setattr(experiments, 'compare', interrupt)
    with pytest.raises(KeyboardInterrupt):
        protocols.execute(interrupted_plan['id'], check=check, trusted=True, db=db)
    unfinished = protocols.get(interrupted_plan['id'], db=db)['executions'][0]
    assert unfinished['state'] == 'RUNNING'
    assert 'interrupted_at' in unfinished and 'finished_at' not in unfinished
    with pytest.raises(ValueError, match='unfinished'):
        protocols.execute(interrupted_plan['id'], check=check, trusted=True, db=db)
    with pytest.raises(ValueError, match='case changed'):
        protocols.execute(plan['id'], check=check, trusted=True, db=db)


@pytest.mark.parametrize('field,value', [('tasks', [None]), ('outcomes', ['']), ('tasks', [{}]), ('claim_refs', None), ('budget', {'runs': True, 'timeout': 1, 'basis': 'invalid boolean'})])
def test_malformed_protocol_fields_rejected(case_store, field, value):
    db, case = case_store
    with pytest.raises(ValueError):
        protocols.create(case['id'], {field: value}, db=db)


def test_non_code_protocol_does_not_resolve_git_revisions(case_store, tmp_path):
    db, case = case_store
    plan = protocols.create(case['id'], {
        'kind': 'human_review', 'hypothesis': 'Review clarity changes with context.',
        'claim_refs': [{'claim_id': 'claim-local', 'version': 1}], 'repo': str(tmp_path),
        'tasks': ['Review the fixed task'], 'baseline': 'No context', 'intervention': 'Context shown',
        'outcomes': ['Count misunderstood instructions'],
        'budget': {'runs': 1, 'timeout': 60, 'basis': 'One review per arm'},
        'stopping_rule': 'Stop after both reviews',
    }, db=db)
    assert plan['status'] == 'READY'
    assert plan['baseline'] == 'No context'
    with pytest.raises(ValueError, match='compatible runner'):
        protocols.execute(plan['id'], check='not-used', trusted=True, db=db)


def test_no_material_change_does_not_report_an_update(case_store):
    db, case = case_store
    workflow.follow(case['id'], db=db)
    case['version'] = 2
    case['checked_at'] = 'different-local-marker'
    cases._save(case, db=db)
    result = workflow.updates(db=db)
    assert result['updates'] == []
    assert result['checked_online'] is False


@pytest.mark.parametrize('arguments', [
    {'action': 'show'}, {'action': 'follow'}, {'action': 'compare', 'case_id': 'x'},
    {'action': 'compare', 'case_id': 'x', 'from_version': None},
    {'action': 'compare', 'case_id': 'x', 'from_version': 1.5},
    {'action': 'compare', 'case_id': 'x', 'from_version': True},
    {'action': 'resume', 'run_id': 'x', 'live': 'false'},
    {'action': 'show', 'case_id': 'x', 'run_id': 'y'},
])
def test_malformed_action_inputs_rejected_before_dispatch(arguments):
    with pytest.raises(ValueError):
        workflow.handle(arguments)


def test_renderer_keeps_contested_state_scope_and_reversal():
    text = research_cli.render({'question': 'Example', 'version': 1, 'gaps': [], 'conclusions': [{
        'state': 'CURRENT', 'claim_state': 'CONTESTED', 'statement': 'A bounded interpretation',
        'relation': 'different_scope', 'rationale': 'Different tasks used in each study',
        'conditions': [{'field': 'task', 'value': 'review'}], 'anchor': {},
        'strongest_challenge': 'No coding task evidence', 'what_would_change': 'A coding task comparison'}]})
    assert '[CONTESTED; different_scope]' in text
    assert 'task: review' in text
    assert text.index('No coding task evidence') < text.index('A coding task comparison')
