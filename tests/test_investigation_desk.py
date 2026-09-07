"""Explicit synthetic source-change scenarios; no scientific findings or external calls."""
import copy
import json
import shlex
import subprocess
import sys

import pytest
from clearance import cases, research, research_cli, research_workflow as workflow
from clearance import investigation_desk as desk

TEXT = 'Synthetic test source. Memory helped on the fixed task only. Other tasks were not evaluated.'
QUOTE = 'Memory helped on the fixed task only.'


@pytest.fixture
def saved(tmp_path, monkeypatch):
    monkeypatch.setenv('AGENT_SCIENCE_SEARCH_DIR', str(tmp_path / 'search'))
    db = tmp_path / 'case store.sqlite'
    data = {'id': 'synthetic-case', 'version': 1, 'question': 'Does memory help coding, and where does that break?',
        'created_at': cases.now(), 'checked_at': 'saved-test-time', 'repo': None,
        'official_domains': [], 'provided_sources': [], 'trace': [], 'limits': [], 'changes': [],
        'evidence': [{'id': 'source-test', 'url': 'https://example.invalid/synthetic', 'kind': 'research_repository',
            'status': 'NO_MATCHED_QUOTE', 'snapshot_text': TEXT, 'snapshot_hash': cases.digest(TEXT)}], 'claims': []}
    cases._save(data, db=db)
    data = research.assess(data['id'], 1, statement='Memory helps on this fixed task.', relation='supports',
        rationale='Synthetic fixture supports only this task.', evidence_id='source-test', quote=QUOTE, db=db)
    return db, data, data['claims'][0]['id']


def change(db, data, *, metadata=False):
    value = copy.deepcopy(data); value['version'] += 1
    if metadata:
        value['evidence'][0]['retracted'] = True
    else:
        value['evidence'][0]['snapshot_text'] = 'Synthetic correction: the measured benefit was withdrawn.'
        value['evidence'][0]['snapshot_hash'] = cases.digest(value['evidence'][0]['snapshot_text'])
    return cases._save(value, db=db)


def test_return_opens_exact_original_support_and_current_break(saved):
    db, data, claim = saved
    desk.save(data['id'], db=db)
    before = desk.open_case(data['id'], claim_id=claim, db=db)
    assert before['claims'][0]['assessments'][0]['passages'][0]['original']['matches_anchor']
    changed = change(db, data)
    row = desk.desk(query='memory', db=db)['cases'][0]
    assert row['unseen_versions'] == 1 and row['claim_review_required'] == 1
    opened = desk.open_case(data['id'], claim_id=claim, db=db)
    card = opened['claims'][0]
    assert card['state'] == 'REVIEW_REQUIRED' and card['changed_since_seen']
    passage = card['assessments'][0]['passages'][0]
    assert passage['original']['excerpt'] == TEXT
    assert passage['original']['version'] == 1
    assert not passage['current']['quote_present']
    text = desk.render(opened, db=db)
    assert 'ORIGINAL v1:' in text and 'quoted passage unavailable' in text
    # The displayed full-source action must execute against the exact original version.
    command = next(line.split(': ', 1)[1] for line in text.splitlines() if 'Inspect full original:' in line)
    proc = subprocess.run([sys.executable, '-m', 'clearance', *shlex.split(command)[1:]], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    assert TEXT in proc.stdout
    # Reopening and repeated saving cannot clear changes; inspected v2 cannot acknowledge v3.
    desk.open_case(data['id'], db=db); desk.save(data['id'], db=db)
    desk.save(data['id'], version=data['version'], db=db)
    assert desk.desk(db=db)['cases'][0]['unseen_versions'] == 1
    desk.save(data['id'], version=changed['version'], db=db)
    assert desk.desk(db=db)['cases'][0]['unseen_versions'] == 0
    assert research.brief(cases.get(data['id'], db=db))['claims'][0]['state'] == 'REVIEW_REQUIRED'
    assert cases.get(data['id'], version=1, db=db)['evidence'][0]['snapshot_text'] == TEXT


def test_withdrawal_notice_is_visible_even_when_quote_did_not_change(saved):
    db, data, claim = saved
    desk.save(data['id'], db=db)
    change(db, data, metadata=True)
    result = desk.open_case(data['id'], claim_id=claim, db=db)
    assert result['claims'][0]['state'] == 'REVIEW_REQUIRED'
    assert 'SOURCE NOTICE' in desk.render(result, db=db)


def test_conflicting_assessments_stay_contested_and_unknown_is_honest(saved):
    db, data, claim = saved
    data = research.assess(data['id'], data['version'], statement=None,
        claim_id=claim, relation='contradicts', rationale='Deliberately opposing authored test reading.',
        evidence_id='source-test', quote=QUOTE, db=db)
    assert desk.open_case(data['id'], claim_id=claim, db=db)['claims'][0]['state'] == 'CONTESTED'
    with pytest.raises(ValueError, match='claim not found'):
        desk.open_case(data['id'], claim_id='missing', db=db)
    with pytest.raises(ValueError):
        desk.save(data['id'], version=999, db=db)


def test_cli_and_mcp_reopen_across_processes(saved):
    db, data, claim = saved
    def cli(*args):
        p = subprocess.run([sys.executable, '-m', 'clearance', 'research', *args, '--db', str(db), '--json'], capture_output=True, text=True)
        assert p.returncode == 0, p.stderr
        return json.loads(p.stdout)
    assert cli('save', data['id'])['version'] == data['version']
    change(db, data)
    assert cli('desk', '--query', 'memory')['cases'][0]['unseen_versions'] == 1
    assert cli('open', data['id'], '--claim', claim)['claims'][0]['state'] == 'REVIEW_REQUIRED'
    message = {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {'name': 'science_research',
        'arguments': {'action': 'open', 'case_id': data['id'], 'claim_id': claim, 'db': str(db)}}}
    p = subprocess.run([sys.executable, '-m', 'clearance.mcp_server'], input=json.dumps(message)+'\n', capture_output=True, text=True)
    result = json.loads(p.stdout)['result']; assert not result.get('isError'), result
    assert json.loads(result['content'][0]['text'])['claims'][0]['state'] == 'REVIEW_REQUIRED'
    assert cli('seen', data['id'], '--version', str(data['version']))['version'] == data['version']
    assert cli('desk')['cases'][0]['unseen_versions'] == 1


def test_empty_desk_and_missing_version_do_not_invent_answers(tmp_path):
    db = tmp_path / 'empty.db'
    result = workflow.handle({'action': 'desk', 'db': db})
    assert result['cases'] == []
    assert 'No matching saved investigations' in research_cli.render(result, db=db)
    with pytest.raises(ValueError, match='exact inspected version'):
        workflow.handle({'action': 'seen', 'case_id': 'missing', 'db': db})


def test_unavailable_source_preserves_original_and_refuses_current_support(saved):
    db, data, claim = saved
    data = copy.deepcopy(data); data['version'] += 1
    data['evidence'] = []
    cases._save(data, db=db)
    opened = desk.open_case(data['id'], claim_id=claim, db=db)
    assert opened['claims'][0]['state'] == 'REVIEW_REQUIRED'
    passage = opened['claims'][0]['assessments'][0]['passages'][0]
    assert passage['original']['matches_anchor'] is True
    assert passage['current']['status'] == 'MISSING'
    assert passage['current']['excerpt'] is None
    assert 'quoted passage unavailable' in desk.render(opened, db=db)
