"""Lane A: adaptive research runs, challenge investigations, interrupt/resume.

Every assertion here is checked by executing the loop — not by reading the code.
"""
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from clearance import cases, research, research_run, instruments
from clearance.mcp_server import handle_tool

SUPPORT = 'https://example.org/fresh-sessions-help'
CONTRARY = 'https://example.net/fresh-sessions-fail'
SUPPORT_TEXT = (
    'Fresh agent sessions reduced the number of repeated errors in our maintenance experiment. '
    'Limitation: the result may not generalize beyond Python repair tasks.'
)
CONTRARY_TEXT = (
    'Fresh agent sessions increased repeated errors on the evaluated maintenance tasks. '
    'The replication failed to confirm the original benefit.'
)
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
            'cache_hit': True,
        }
    return snapshot


@pytest.fixture
def db(tmp_path):
    return tmp_path / 'cases.db'


def _supported_case(db):
    with patch.object(instruments, 'document_snapshot', side_effect=seed_docs({SUPPORT: SUPPORT_TEXT})):
        data = cases.create(QUESTION, sources=[SUPPORT], db=db)
    eid = data['evidence'][0]['id']
    quote = data['evidence'][0]['quote']
    assert quote and quote in SUPPORT_TEXT
    data = research.assess(
        data['id'], data['version'], statement='Fresh sessions reduce repeated errors.',
        relation='supports', rationale='Primary study measured fewer repeated errors.',
        evidence_id=eid, quote=quote, db=db,
    )
    assert research.brief(data)['claims'][0]['state'] == 'SUPPORTED_AS_ASSESSED'
    return data


def test_challenge_is_new_investigation_against_pinned_version(db):
    data = _supported_case(db)
    pinned = data['version']
    queries = []

    def discover(provider, query, **kwargs):
        queries.append(query)
        return [cases.search.Candidate(CONTRARY, 'Replication failure', CONTRARY_TEXT[:120])]

    with patch.object(research_run.discovery, 'find', side_effect=discover), \
            patch.object(instruments, 'document_snapshot', side_effect=seed_docs({
                SUPPORT: SUPPORT_TEXT, CONTRARY: CONTRARY_TEXT,
            })):
        run = research_run.start_challenge(
            data['id'], version=pinned, db=db, live=False,
            limits={'max_rounds': 2, 'max_discovery_calls': 4, 'max_document_reads': 6},
        )

    assert run['kind'] == 'challenge'
    assert run['base_case_version'] == pinned
    assert run['pinned_answer']['case_version'] == pinned
    choose = [s for s in run['steps'] if s['op'] == 'choose_gap']
    assert choose, 'challenge must choose a gap from the pinned answer'
    assert any(n['intent'] == 'challenge' for n in run['question_map'])
    challenge_searches = [n['proposed_search'] for n in run['question_map'] if n['intent'] == 'challenge']
    assert challenge_searches
    assert all(QUESTION != s for s in challenge_searches)
    assert queries, 'challenge must issue at least one discovery query'
    assert any(
        any(token in q.lower() for token in ('contradict', 'failure', 'against', 'overturn'))
        for q in queries
    ), queries

    after = cases.get(data['id'], db=db)
    assert after['version'] > pinned
    urls = {e['url'] for e in after['evidence']}
    assert CONTRARY in urls
    brief = research.brief(after)
    assert 'CONTESTED' in {c['state'] for c in brief['claims']} or any(
        a['relation'] == 'contradicts' and a['state'] == 'CURRENT'
        for c in brief['claims'] for a in c['assessments']
    ), brief
    assert cases.get(data['id'], version=pinned, db=db)['version'] == pinned


def test_followup_query_comes_from_prior_source_gap(db):
    with patch.object(instruments, 'document_snapshot', side_effect=seed_docs({SUPPORT: SUPPORT_TEXT})):
        run = research_run.start_research(
            QUESTION, sources=[SUPPORT], db=db, execute=False,
        )
    data = cases.get(run['case_id'], db=db)
    # Gaps derived at start are already merged into the persisted map.
    sourced = [n for n in run['question_map'] if n.get('source_evidence_id')]
    assert sourced, run['question_map']
    assert any(n['source_evidence_id'] == data['evidence'][0]['id'] for n in sourced)
    assert any(n['intent'] == 'replication' for n in sourced)
    assert all(n['proposed_search'] != QUESTION for n in sourced)
    # Fresh derivation against only the initial template still yields the source-linked gap.
    fresh = research_run.gaps_from_evidence(data, research_run.initial_question_map(QUESTION))
    assert any(g.get('source_evidence_id') == data['evidence'][0]['id'] for g in fresh)


def test_interrupt_resume_preserves_evidence_and_skips_completed_discovery(db):
    data = _supported_case(db)
    calls = []

    def discover(provider, query, **kwargs):
        calls.append((provider, query))
        return [cases.search.Candidate(CONTRARY, 'Replication', CONTRARY_TEXT[:80])]

    docs = seed_docs({SUPPORT: SUPPORT_TEXT, CONTRARY: CONTRARY_TEXT})
    with patch.object(research_run.discovery, 'find', side_effect=discover), \
            patch.object(instruments, 'document_snapshot', side_effect=docs):
        paused = research_run.start_challenge(
            data['id'], version=data['version'], db=db, live=False, max_steps=3,
            limits={'max_rounds': 3, 'max_discovery_calls': 5, 'max_document_reads': 8},
        )
    assert paused['status'] == 'paused'
    assert paused['stop_reason'] == 'max_steps'
    mid = cases.get(data['id'], db=db)
    mid_urls = {e['url'] for e in mid['evidence']}
    mid_version = mid['version']
    completed_discovers = [s for s in paused['steps'] if s['op'] == 'discover' and s['state'] == 'completed']
    first_calls = list(calls)

    with patch.object(research_run.discovery, 'find', side_effect=discover), \
            patch.object(instruments, 'document_snapshot', side_effect=docs):
        resumed = research_run.resume(paused['id'], db=db, live=False,
                                      max_steps=20)

    after = cases.get(data['id'], db=db)
    assert {e['url'] for e in after['evidence']} >= mid_urls
    assert after['version'] >= mid_version
    assert completed_discovers, paused['steps']
    # The paused discovery fingerprint must be skipped — not re-issued to the provider.
    skipped = [s for s in resumed['steps'] if s['op'] == 'discover' and s['state'] == 'skipped']
    assert skipped, resumed['steps']
    assert skipped[0].get('response_ref'), 'skipped discover must reuse prior candidate URLs'
    # Provider may still be called for *different* gap queries; the first fingerprint must not repeat.
    first_fp = (completed_discovers[0].get('provider'), completed_discovers[0].get('proposed_query'))
    later_same = [c for c in calls[len(first_calls):] if c == first_fp]
    assert later_same == [], f'repeated paid/public discovery for {first_fp}: {calls}'
    assert SUPPORT in {e['url'] for e in after['evidence']}


def test_naive_baseline_arm_does_not_challenge(db):
    """Always-silent / fixed-search baseline: create only, no overturn investigation."""
    with patch.object(instruments, 'document_snapshot', side_effect=seed_docs({SUPPORT: SUPPORT_TEXT})):
        naive = research_run.naive_fixed_search_arm(QUESTION, sources=[SUPPORT], db=db)
    assert naive['evidence']
    assert 'claims' not in naive or not any(
        a.get('relation') == 'contradicts'
        for c in naive.get('claims', []) for a in c.get('assessments', [])
    )
    # Adaptive challenge against a supported case with contrary discovery finds contest.
    data = _supported_case(db)

    def discover(provider, query, **kwargs):
        return [cases.search.Candidate(CONTRARY, 'Fail', CONTRARY_TEXT[:80])]

    with patch.object(research_run.discovery, 'find', side_effect=discover), \
            patch.object(instruments, 'document_snapshot', side_effect=seed_docs({
                SUPPORT: SUPPORT_TEXT, CONTRARY: CONTRARY_TEXT,
            })):
        challenged = research_run.start_challenge(data['id'], db=db, live=False,
                                                  limits={'max_rounds': 2, 'max_discovery_calls': 3, 'max_document_reads': 5})
    after = cases.get(data['id'], db=db)
    adaptive_contradicts = sum(
        1 for c in research.brief(after)['claims']
        for a in c['assessments'] if a['relation'] == 'contradicts' and a['state'] == 'CURRENT'
    )
    naive_contradicts = 0
    assert adaptive_contradicts > naive_contradicts
    assert challenged['kind'] == 'challenge'


def test_cli_research_challenge_resume_exit_zero(db, tmp_path):
    data = _supported_case(db)
    env = {**dict(**{k: v for k, v in __import__('os').environ.items()}), 'AGENT_SCIENCE_CASES_DB': str(db)}
    root = Path(__file__).resolve().parents[1]

    def discover(provider, query, **kwargs):
        return [cases.search.Candidate(CONTRARY, 'Fail', CONTRARY_TEXT[:80])]

    # Drive through the public CLI for the stranger path.
    with patch.object(research_run.discovery, 'find', side_effect=discover), \
            patch.object(instruments, 'document_snapshot', side_effect=seed_docs({
                SUPPORT: SUPPORT_TEXT, CONTRARY: CONTRARY_TEXT,
            })):
        from clearance.stack_cli import main
        code = main(['research', 'challenge', data['id'], '--db', str(db), '--max-steps', '4', '--json'])
        assert code == 0
        shown = research_run.list_runs(case_id=data['id'], db=db, limit=5)
        assert shown
        run_id = shown[0]['id']
        if shown[0]['status'] == 'paused':
            code = main(['research', 'resume', run_id, '--db', str(db), '--json'])
            assert code == 0
        code = main(['research', 'show', run_id, '--db', str(db)])
        assert code == 0


def test_mcp_science_research_challenge(db):
    data = _supported_case(db)

    def discover(provider, query, **kwargs):
        return [cases.search.Candidate(CONTRARY, 'Fail', CONTRARY_TEXT[:80])]

    with patch.object(research_run.discovery, 'find', side_effect=discover), \
            patch.object(instruments, 'document_snapshot', side_effect=seed_docs({
                SUPPORT: SUPPORT_TEXT, CONTRARY: CONTRARY_TEXT,
            })):
        raw = handle_tool('science_research', {
            'action': 'challenge', 'case_id': data['id'], 'db': str(db),
            'max_steps': 6,
        })
    payload = json.loads(raw)
    assert 'error' not in payload, payload
    assert payload['kind'] == 'challenge'
    assert payload['base_case_version'] == data['version']


def test_plan_only_does_not_claim_autonomous_completion(db):
    run = research_run.start_research(QUESTION, db=db, execute=False)
    assert run['status'] == 'planned'
    assert run['stop_reason'] is None
    assert run['steps'] == []
    assert run['question_map']
