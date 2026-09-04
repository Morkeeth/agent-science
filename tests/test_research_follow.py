"""Lane C: follow / updates / experiment-plan — executed controls only."""
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from clearance import cases, experiment_protocol, follow, instruments, research, updates
from clearance.mcp_server import handle_tool
from clearance.stack_cli import main

SUPPORT = 'https://example.org/fresh-sessions-help'
NOISE = 'https://example.org/sidebar-noise'
SUPPORT_TEXT = (
    'Fresh agent sessions reduced the number of repeated errors in our maintenance experiment. '
    'Limitation: the result may not generalize beyond Python repair tasks.'
)
SUPPORT_TEXT_CHANGED = (
    'Fresh agent sessions increased the number of repeated errors in our maintenance experiment. '
    'Limitation: the result may not generalize beyond Python repair tasks.'
)
NOISE_TEXT = 'Sidebar promo: unrelated archival newsletter signup form for museum visitors only.'
NOISE_TEXT_CHANGED = 'Sidebar promo UPDATED: still unrelated archival newsletter signup form.'
QUESTION = 'Do fresh agent sessions reduce repeated errors?'


def seed_docs(mapping):
    def snapshot(url, **kwargs):
        if url not in mapping:
            return None
        text = mapping[url]
        return {
            'text': text,
            'sha256': cases.digest(text),
            'fetched_at': '2026-09-05T00:00:00Z',
            'cache_hit': kwargs.get('refresh') is not True,
        }
    return snapshot


@pytest.fixture
def db(tmp_path):
    return tmp_path / 'cases.db'


def _case_with_decision(db, *, extra_urls=()):
    urls = [SUPPORT, *extra_urls]
    mapping = {SUPPORT: SUPPORT_TEXT, NOISE: NOISE_TEXT}
    with patch.object(instruments, 'document_snapshot', side_effect=seed_docs(mapping)):
        data = cases.create(QUESTION, sources=urls, db=db)
    eid = next(e['id'] for e in data['evidence'] if e['url'] == SUPPORT)
    quote = next(e['quote'] for e in data['evidence'] if e['url'] == SUPPORT)
    data = research.assess(
        data['id'], data['version'], statement='Fresh sessions reduce repeated errors.',
        relation='supports', rationale='Primary study measured fewer repeated errors.',
        evidence_id=eid, quote=quote, db=db,
    )
    data = cases.decide(
        data['id'],
        statement='Prefer fresh sessions for maintenance repair tasks.',
        rationale='Supported by the verified quote in the primary study.',
        evidence_ids=[eid],
        expected_version=data['version'],
        db=db,
    )
    return data


def test_follow_persists_and_lists(db):
    data = _case_with_decision(db)
    row = follow.follow(data['id'], db=db, note='day-two watch')
    assert row['case_id'] == data['id']
    assert row['active'] is True
    assert row['last_checked_online'] is False
    listed = follow.list_followed(db=db)
    assert len(listed) == 1
    assert listed[0]['id'] == row['id']
    again = follow.follow(data['id'], db=db, note='updated note')
    assert again['id'] == row['id']
    assert again['note'] == 'updated note'
    inactive = follow.unfollow(data['id'], db=db)
    assert inactive['active'] is False
    assert follow.list_followed(db=db) == []


def test_updates_ranks_decision_effect_over_uncited_noise(db):
    """Material change report must prefer decision impact over sidebar noise.

    Fixture: cited support text changes AND an uncited noise URL changes.
    Ranked arm surfaces the decision; naive arm floods with both.
    """
    data = _case_with_decision(db, extra_urls=[NOISE])
    follow.follow(data['id'], db=db)
    before = cases.get(data['id'], db=db)

    mapping = {SUPPORT: SUPPORT_TEXT_CHANGED, NOISE: NOISE_TEXT_CHANGED}
    with patch.object(instruments, 'document_snapshot', side_effect=seed_docs(mapping)):
        after = cases.refresh(data['id'], live=False, db=db)

    ranked = updates.score_case_change(before, after)
    naive = updates.naive_any_change(before, after)

    assert ranked['material'] is True
    assert any(e['kind'] == 'decision_review_required' for e in ranked['material_effects'])
    assert ranked['material_effects'][0]['rank'] == updates.RANK_DECISION
    # Uncited noise must not headline the material list when a decision is affected
    assert ranked['material_effects'][0]['kind'] != 'uncited_evidence_changed'
    uncited = [e for e in ranked['effects'] if e['kind'] == 'uncited_evidence_changed']
    assert uncited, 'noise change should still be recorded at low rank'
    assert all(e['rank'] < updates.MATERIAL_THRESHOLD for e in uncited)

    assert naive['material'] is True
    assert naive['material_count'] >= 2, naive
    # Naive cannot distinguish decision impact from sidebar churn
    assert all(e['kind'] == 'any_change' for e in naive['effects'])


def test_updates_empty_when_only_uncited_noise_changes(db):
    data = _case_with_decision(db, extra_urls=[NOISE])
    follow.follow(data['id'], db=db)
    before = cases.get(data['id'], db=db)

    # Only noise changes; cited support text identical
    mapping = {SUPPORT: SUPPORT_TEXT, NOISE: NOISE_TEXT_CHANGED}
    with patch.object(instruments, 'document_snapshot', side_effect=seed_docs(mapping)):
        after = cases.refresh(data['id'], live=False, db=db)

    ranked = updates.score_case_change(before, after)
    naive = updates.naive_any_change(before, after)

    assert ranked['material'] is False
    assert ranked['effect_count'] >= 1
    assert naive['material'] is True  # naive still screams
    assert naive['material_count'] >= 1


def test_updates_run_fixture_day_two_path(db):
    data = _case_with_decision(db)
    follow.follow(data['id'], db=db)
    # First check — no change yet
    with patch.object(instruments, 'document_snapshot', side_effect=seed_docs({SUPPORT: SUPPORT_TEXT})):
        quiet = updates.run_updates(db=db, live=False, refresh=True)
    assert quiet['summary']['empty'] is True
    assert 'No material change' in quiet['summary']['meaning']
    assert quiet['items'][0]['checked_online'] is False  # live=false → no online claim

    # Day-two: cited source changes
    with patch.object(instruments, 'document_snapshot', side_effect=seed_docs({SUPPORT: SUPPORT_TEXT_CHANGED})):
        changed = updates.run_updates(db=db, live=False, refresh=True)
    assert changed['summary']['empty'] is False
    assert changed['summary']['material_changes'] == 1
    assert changed['items'][0]['score']['material'] is True
    assert 'What would change' not in ''  # render checked below
    text = updates.render_run(changed)
    assert 'MATERIAL' in text
    assert 'What would change this answer?' in text
    tracked = follow.get_by_case(data['id'], db=db)
    assert tracked['last_update_run_id'] == changed['id']
    assert tracked['last_checked_online'] is False


def test_checked_online_only_when_live_fetches(db):
    data = _case_with_decision(db)
    follow.follow(data['id'], db=db)

    def snap(url, **kwargs):
        return {
            'text': SUPPORT_TEXT,
            'sha256': cases.digest(SUPPORT_TEXT),
            'fetched_at': '2026-09-05T12:00:00Z',
            'cache_hit': False,  # actual fetch
        }

    with patch.object(instruments, 'document_snapshot', side_effect=snap):
        run = updates.run_updates(db=db, live=True, refresh=True)
    assert run['items'][0]['checked_online'] is True
    assert follow.get_by_case(data['id'], db=db)['last_checked_online'] is True


def test_experiment_plan_is_not_a_result(db):
    data = _case_with_decision(db)
    claim_id = data['claims'][0]['id']
    protocol = experiment_protocol.create(
        data['id'],
        hypothesis='Fresh sessions beat warm sessions on the acceptance check.',
        kind='code_change',
        claim_ids=[claim_id],
        tasks=['Run acceptance on both pins'],
        db=db,
    )
    assert protocol['status'] == 'planned'
    assert protocol['execution'] is None
    assert protocol['executable'] is False
    assert 'not a result' in experiment_protocol.render(protocol).lower() or 'planned' in experiment_protocol.render(protocol)

    with pytest.raises(ValueError, match='plan, not a result'):
        experiment_protocol.mark_as_result(protocol['id'], db=db)

    with pytest.raises(ValueError, match='not executable'):
        experiment_protocol.execute(protocol['id'], db=db)


def test_experiment_plan_execute_links_measured_experiment(db, tmp_path):
    data = _case_with_decision(db)
    # Tiny git repo with two commits and a constant acceptance script
    repo = tmp_path / 'repo'
    repo.mkdir()
    check = tmp_path / 'accept.py'
    check.write_text('raise SystemExit(0)\n')
    import subprocess, os
    env = {**os.environ, 'GIT_AUTHOR_NAME': 't', 'GIT_AUTHOR_EMAIL': 't@t',
           'GIT_COMMITTER_NAME': 't', 'GIT_COMMITTER_EMAIL': 't@t'}
    subprocess.run(['git', 'init'], cwd=repo, check=True, capture_output=True)
    (repo / 'a.txt').write_text('base\n')
    subprocess.run(['git', 'add', 'a.txt'], cwd=repo, check=True, capture_output=True, env=env)
    subprocess.run(['git', 'commit', '-m', 'base'], cwd=repo, check=True, capture_output=True, env=env)
    base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
    (repo / 'a.txt').write_text('cand\n')
    subprocess.run(['git', 'add', 'a.txt'], cwd=repo, check=True, capture_output=True, env=env)
    subprocess.run(['git', 'commit', '-m', 'cand'], cwd=repo, check=True, capture_output=True, env=env)
    cand = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()

    # Attach repo to case via refresh path: create with root
    with patch.object(instruments, 'document_snapshot', side_effect=seed_docs({SUPPORT: SUPPORT_TEXT})):
        cased = cases.create(QUESTION, sources=[SUPPORT], root=str(repo), db=db)
    protocol = experiment_protocol.create(
        cased['id'],
        hypothesis='Candidate does not break the acceptance check.',
        kind='code_change',
        repo=str(repo),
        baseline_ref=base,
        intervention_ref=cand,
        acceptance_check=str(check),
        comparison_budget={'paired_runs': 1, 'timeout_seconds': 30},
        db=db,
    )
    assert protocol['executable'] is True
    linked = experiment_protocol.execute(protocol['id'], db=db)
    assert linked['status'] == 'linked'
    assert linked['version'] == 2
    assert linked['execution']['experiment_id']
    assert linked['execution']['valid'] is True
    # Prior version remains a plan
    v1 = experiment_protocol.get(protocol['id'], version=1, db=db)
    assert v1['status'] == 'planned'
    assert v1['execution'] is None


def test_cli_follow_updates_experiment_plan(db):
    data = _case_with_decision(db)
    assert main(['research', 'follow', data['id'], '--db', str(db)]) == 0
    with patch.object(instruments, 'document_snapshot', side_effect=seed_docs({SUPPORT: SUPPORT_TEXT_CHANGED})):
        assert main(['research', 'updates', '--db', str(db)]) == 0
    assert main([
        'research', 'experiment-plan', data['id'],
        '--hypothesis', 'Intervention preserves acceptance.',
        '--kind', 'observation',
        '--db', str(db),
    ]) == 0
    assert main(['research', 'follow', '--list', '--db', str(db)]) == 0


def test_mcp_follow_updates_experiment_plan(db):
    data = _case_with_decision(db)
    out = json.loads(handle_tool('science_research', {'action': 'follow', 'case_id': data['id'], 'db': str(db)}))
    assert out['case_id'] == data['id']
    with patch.object(instruments, 'document_snapshot', side_effect=seed_docs({SUPPORT: SUPPORT_TEXT})):
        upd = json.loads(handle_tool('science_research', {
            'action': 'updates', 'db': str(db), 'live': False, 'refresh': True,
        }))
    assert upd['summary']['followed'] == 1
    plan = json.loads(handle_tool('science_research', {
        'action': 'experiment-plan',
        'case_id': data['id'],
        'hypothesis': 'A local observation plan stays planned.',
        'kind': 'observation',
        'db': str(db),
    }))
    assert plan['status'] == 'planned'
    assert plan['execution'] is None
