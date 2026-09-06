"""Preparation is a local protocol boundary, not a scientific result."""
import json
import hashlib
import subprocess
import sys

import pytest

from clearance import cases, research_evaluation as evaluation, research_protocols


LIMITS = {'discovery_calls': 0, 'document_reads': 2, 'reasoning_calls': 0, 'rounds': 1}


def prepared_spec(protocol=None):
    return {
        'title': 'Held-out operational campaign',
        'authored_by': 'fixture author',
        'rubric_provenance': 'Written before any fixture outcome.',
        'operational_rubric': {
            'source_recovery': 'Recover and inspect the original source, not a search snippet.',
            'counterevidence': 'Record strong contrary evidence and unresolved absence separately.',
            'experiment_executability': 'Require a pinned executable check, inputs, and observed result.',
        },
        'unknown_resources': ['provider billing', 'host model identity', 'human review time'],
        'protocol': protocol,
        'questions': [{'id': 'q1', 'topic': 'memory', 'question': 'When does memory help coding agents?',
                       'expected_distinctions': ['Task-specific evidence is not general effectiveness.']}],
        'arms': [
            {'id': 'baseline', 'kind': 'retrieval', 'code_ref': 'b' * 40,
             'mode': 'snapshot_replay', 'resource_limits': LIMITS},
            {'id': 'candidate', 'kind': 'synthesis', 'code_ref': 'a' * 40,
             'mode': 'snapshot_replay', 'resource_limits': LIMITS},
        ],
        'repetitions': 1,
        'rubric': {key: 'Independently inspect ' + key for key in evaluation.CRITERIA},
    }


def ready_protocol(tmp_path, db):
    repo = tmp_path / 'repo'; repo.mkdir()
    subprocess.run(['git', 'init', '-q', str(repo)], check=True)
    subprocess.run(['git', '-C', str(repo), 'config', 'user.email', 'fixture@example.invalid'], check=True)
    subprocess.run(['git', '-C', str(repo), 'config', 'user.name', 'Fixture'], check=True)
    (repo / 'value').write_text('baseline')
    subprocess.run(['git', '-C', str(repo), 'add', 'value'], check=True)
    subprocess.run(['git', '-C', str(repo), 'commit', '-qm', 'baseline'], check=True)
    baseline = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
    (repo / 'value').write_text('candidate')
    subprocess.run(['git', '-C', str(repo), 'commit', '-qam', 'candidate'], check=True)
    candidate = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip()
    case = cases.create('When does memory help coding agents?', root=str(repo), db=db)
    case['version'] += 1
    case['claims'] = [{'id': 'fixture-claim', 'statement': 'The candidate should satisfy the fixed check.',
                       'assessments': [], 'source_urls': []}]
    cases._save(case, db=db)
    check = b'print("fixture")\n'
    fields = {'hypothesis': 'Synthetic software acceptance only',
              'claim_refs': [{'claim_id': 'fixture-claim', 'version': case['version']}], 'repo': str(repo),
              'tasks': ['Run the fixture check'], 'baseline': baseline, 'intervention': candidate,
              'outcomes': ['Acceptance result'], 'budget': {'runs': 1, 'timeout': 10, 'basis': 'One fixture pair'},
              'stopping_rule': 'Stop after one pair', 'check_sha256': hashlib.sha256(check).hexdigest()}
    protocol = research_protocols.create(case['id'], fields, db=db)
    return protocol


def test_prepare_freezes_unrun_manifest_and_preserves_existing_campaign(tmp_path):
    db = tmp_path / 'prepare.db'
    protocol = ready_protocol(tmp_path, db)
    value = prepared_spec({'id': protocol['id'], 'version': protocol['version']})
    value['arms'][0]['code_ref'] = protocol['baseline']; value['arms'][1]['code_ref'] = protocol['intervention']
    old = evaluation.create({
        'title': 'Historical campaign', 'authored_by': 'old author',
        'rubric_provenance': 'Historical rubric.', 'questions': prepared_spec()['questions'],
        'arms': value['arms'], 'repetitions': 1,
        'rubric': prepared_spec()['rubric']}, db=db)
    old_bytes = json.dumps(old['manifest'], sort_keys=True)
    result = evaluation.prepare(value, db=db)
    assert result['preparation']['status'] == 'FROZEN_UNRUN'
    assert result['coverage']['recorded'] == 0
    assert result['coverage']['denominator'] == 2
    assert result['manifest']['preparation']['unknown_resources'] == prepared_spec()['unknown_resources']
    assert result['manifest_hash'] == evaluation.get(result['id'], db=db)['manifest_hash']
    assert result['preparation']['protocol']['state'] == 'READY_UNRUN'
    assert json.dumps(evaluation.get(old['id'], db=db)['manifest'], sort_keys=True) == old_bytes


@pytest.mark.parametrize('field', ['operational_rubric', 'unknown_resources'])
def test_prepare_requires_explicit_operational_unknowns(tmp_path, field):
    spec = prepared_spec()
    spec.pop(field)
    with pytest.raises(ValueError):
        evaluation.prepare(spec, db=tmp_path / 'invalid.db')


def test_prepare_cli_and_mcp_expose_same_frozen_campaign(tmp_path):
    db = str(tmp_path / 'cli-mcp.db')
    protocol = ready_protocol(tmp_path, db)
    value = prepared_spec({'id': protocol['id'], 'version': protocol['version']})
    value['arms'][0]['code_ref'] = protocol['baseline']; value['arms'][1]['code_ref'] = protocol['intervention']
    spec_file = tmp_path / 'spec.json'
    spec_file.write_text(json.dumps(value))
    command = [sys.executable, '-m', 'clearance', 'research', 'evaluation-prepare',
               '--spec-file', str(spec_file), '--db', db, '--json']
    completed = subprocess.run(command, capture_output=True, text=True, timeout=30)
    assert completed.returncode == 0, completed.stderr
    campaign = json.loads(completed.stdout)
    assert campaign['preparation']['status'] == 'FROZEN_UNRUN'
    message = {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {
        'name': 'science_research', 'arguments': {
            'action': 'evaluation-show', 'evaluation_id': campaign['id'], 'db': db}}}
    mcp = subprocess.run([sys.executable, '-m', 'clearance.mcp_server'], input=json.dumps(message) + '\n',
                         capture_output=True, text=True, timeout=30)
    assert mcp.returncode == 0, mcp.stderr
    envelope = json.loads(mcp.stdout)['result']
    assert not envelope.get('isError')
    inspected = json.loads(envelope['content'][0]['text'])
    assert inspected['manifest_hash'] == campaign['manifest_hash']
    assert inspected['coverage']['recorded'] == 0
    assert inspected['manifest']['preparation']['status'] == 'FROZEN_UNRUN'


def test_prepare_rejects_disconnected_protocol_text(tmp_path):
    value = prepared_spec({'baseline': 'HEAD', 'candidate': 'nonexistent protocol'})
    with pytest.raises(ValueError, match='exactly id and version'):
        evaluation.prepare(value, db=tmp_path / 'invalid.db')


def test_prepare_without_protocol_is_explicitly_unresolved(tmp_path):
    result = evaluation.prepare(prepared_spec(), db=tmp_path / 'unresolved.db')
    assert result['preparation']['protocol']['state'] == 'UNRESOLVED'
    assert 'Create a READY' in result['next_action']
