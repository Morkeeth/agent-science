"""Local fixture tests: no personal store, provider requests or model calls."""
import argparse
import hashlib
import json
import subprocess
import sys
import types
from copy import deepcopy

import pytest
from clearance import cases, research_cli, research_protocols as protocols, research_workflow as workflow


@pytest.fixture
def case_store(tmp_path):
    db = tmp_path / 'cases.sqlite'
    data = {'id': 'case-local', 'version': 1, 'question': 'Does the change pass the fixed acceptance task?',
            'created_at': cases.now(), 'checked_at': 'baseline-marker', 'repo': None,
            'official_domains': [], 'provided_sources': [], 'evidence': [], 'trace': [], 'limits': [],
            'claims': [{'id': 'claim-local', 'statement': 'Candidate should produce the expected output.'}]}
    return db, cases._save(data, db=db)


def test_follow_reads_do_not_acknowledge_or_check_web(case_store, monkeypatch):
    db, case = case_store
    assert workflow.follow(case['id'], db=db)['version'] == 1
    monkeypatch.setitem(sys.modules, 'clearance.synthesis', types.SimpleNamespace(compare=lambda *a, **kw: {'conclusions_changed': ['new condition']}))
    assert workflow.updates(db=db)['updates'] == []
    case['version'] = 2
    cases._save(case, db=db)
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


def test_real_protocol_executes_frozen_git_comparison(case_store, tmp_path):
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
    receipt = protocols.execute(plan['id'], check=check, trusted=True, db=db)
    assert receipt['state'] == 'COMPLETED'
    assert receipt['result']['aggregate']['baseline']['passed'] == 0
    assert receipt['result']['aggregate']['candidate']['passed'] == 1
    assert receipt['result']['pins'] == {'baseline': baseline, 'candidate': intervention}
    saved = cases.get(case['id'], db=db)['experiments']
    assert receipt['experiment_id'] == saved[0]['id']
    assert protocols.get(plan['id'], db=db)['executions'][0]['experiment_id'] == saved[0]['id']
    case['version'] = 2
    cases._save(case, db=db)
    with pytest.raises(ValueError, match='case changed'):
        protocols.execute(plan['id'], check=check, trusted=True, db=db)
