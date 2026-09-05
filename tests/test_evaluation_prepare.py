"""Preparation is a local protocol boundary, not a scientific result."""
import json
import subprocess
import sys

import pytest

from clearance import cases, research_evaluation as evaluation


LIMITS = {'discovery_calls': 0, 'document_reads': 2, 'reasoning_calls': 0, 'rounds': 1}


def prepared_spec():
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
        'protocol': {'baseline': 'Saved-source recovery policy', 'candidate': 'Candidate research workflow'},
        'questions': [{'id': 'q1', 'topic': 'memory', 'question': 'When does memory help coding agents?',
                       'expected_distinctions': ['Task-specific evidence is not general effectiveness.']}],
        'arms': [
            {'id': 'baseline', 'kind': 'retrieval', 'baseline_policy': 'Recover original saved sources only.',
             'mode': 'snapshot_replay', 'resource_limits': LIMITS},
            {'id': 'candidate', 'kind': 'synthesis', 'code_ref': 'a' * 40,
             'mode': 'snapshot_replay', 'resource_limits': LIMITS},
        ],
        'repetitions': 1,
        'rubric': {key: 'Independently inspect ' + key for key in evaluation.CRITERIA},
    }


def test_prepare_freezes_unrun_manifest_and_preserves_existing_campaign(tmp_path):
    db = tmp_path / 'prepare.db'
    old = evaluation.create({
        'title': 'Historical campaign', 'authored_by': 'old author',
        'rubric_provenance': 'Historical rubric.', 'questions': prepared_spec()['questions'],
        'arms': prepared_spec()['arms'], 'repetitions': 1,
        'rubric': prepared_spec()['rubric']}, db=db)
    old_bytes = json.dumps(old['manifest'], sort_keys=True)
    result = evaluation.prepare(prepared_spec(), db=db)
    assert result['preparation']['status'] == 'FROZEN_UNRUN'
    assert result['coverage']['recorded'] == 0
    assert result['coverage']['denominator'] == 2
    assert result['manifest']['preparation']['unknown_resources'] == prepared_spec()['unknown_resources']
    assert result['manifest_hash'] == evaluation.get(result['id'], db=db)['manifest_hash']
    assert json.dumps(evaluation.get(old['id'], db=db)['manifest'], sort_keys=True) == old_bytes


@pytest.mark.parametrize('field', ['operational_rubric', 'unknown_resources'])
def test_prepare_requires_explicit_operational_unknowns(tmp_path, field):
    spec = prepared_spec()
    spec.pop(field)
    with pytest.raises(ValueError):
        evaluation.prepare(spec, db=tmp_path / 'invalid.db')


def test_prepare_cli_and_mcp_expose_same_frozen_campaign(tmp_path):
    db = str(tmp_path / 'cli-mcp.db')
    spec_file = tmp_path / 'spec.json'
    spec_file.write_text(json.dumps(prepared_spec()))
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
