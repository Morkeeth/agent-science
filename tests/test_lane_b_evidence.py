"""Lane B — study identity, claim scope, synthesis. Watch RED before GREEN.

Acceptance (NIGHTPLAN Lane B):
  1. Five reports repeating one paper remain one study
  2. Two papers about different tasks are not automatically a contradiction
  3. A fabricated quotation is rejected by an exercised control

Every assertion here is checked by executing the object — not by reading code.
Run: python3 -m pytest -q tests/test_lane_b_evidence.py
"""
from __future__ import annotations

import pytest

from clearance import cases, claim_graph, conditions, research, research_run, study, synthesis
from clearance import instruments
from unittest.mock import patch


# --- fixtures: one real paper, five mirror URLs; two different-task papers ---

PAPER_A_TEXT = """
Title: Persistent memory for coding agents on repository repair.
Abstract: We study whether a persistent memory store improves coding-agent outcomes.
Task: SWE-bench verified repository repair (Python).
Population: 50 repository issues from the SWE-bench verified split.
Model: Claude 3.5 Sonnet (20241022) with a 32k context window.
Comparator: identical agent without persistent memory (fresh session each trial).
Dataset: SWE-bench verified (n=50).
Metric: resolve rate (% of issues with passing tests).
Resource budget: 8 agent turns and at most 120 seconds wall time per issue.
Study design: randomized controlled comparison with matched prompts.
Limitation: results may not generalize beyond Python repair tasks under the stated budget.
Result: Persistent memory increased resolve rate from 24% to 38% under the stated budget.
"""

PAPER_B_TEXT = """
Title: Persistent memory for coding agents on multi-hop QA.
Abstract: We study whether a persistent memory store improves multi-hop question answering.
Task: HotpotQA multi-hop question answering (English).
Population: 200 HotpotQA development questions.
Model: GPT-4o-mini with retrieval tools.
Comparator: identical agent without persistent memory.
Dataset: HotpotQA distractor setting.
Metric: exact match accuracy.
Resource budget: 4 retrieval calls and 2k tokens per question.
Study design: within-subject comparison on fixed questions.
Limitation: qualitative interview follow-ups are exploratory; this is not a causal claim about coding effectiveness.
Result: Persistent memory did not improve exact match on HotpotQA under the stated budget.
"""

MIRROR_URLS = [
    'https://arxiv.org/abs/2401.11111',
    'https://arxiv.org/pdf/2401.11111.pdf',
    'https://arxiv.org/html/2401.11111',
    'https://ar5iv.labs.arxiv.org/html/2401.11111v2',
    'https://doi.org/10.48550/arXiv.2401.11111',
]

PAPER_B_URL = 'https://arxiv.org/abs/2402.22222'
QUAL_URL = 'https://example.org/interview-memory-agents'


def test_five_mirrors_of_one_paper_are_one_study():
    """Done-when: five reports repeating one paper remain one study."""
    groups = study.group_documents(MIRROR_URLS)
    assert len(groups) == 1, f'expected 1 study, got {len(groups)}: {groups}'
    studies = study.build_studies([
        {'id': f'e{i}', 'url': u, 'snapshot_text': PAPER_A_TEXT if i == 0 else PAPER_A_TEXT,
         'title': 'Persistent memory for coding agents on repository repair.',
         'kind': 'research_repository', 'status': 'QUOTE_VERIFIED'}
        for i, u in enumerate(MIRROR_URLS)
    ])
    assert len(studies) == 1
    assert studies[0]['identity'] in ('arxiv', 'doi')
    assert len(studies[0]['document_refs']) == 5


def test_title_only_merge_is_refused():
    """Title resemblance is never enough — explicit refuse path."""
    result = study.merge_by_title(
        'Persistent memory for coding agents on repository repair',
        'Persistent memory for coding agents on multi-hop QA',
    )
    assert result['merged'] is False
    assert result['reason'] == 'title_resemblance_refused'
    # Different URLs with similar titles stay separate studies.
    groups = study.group_documents([
        'https://example.org/paper-about-memory-repair',
        'https://example.org/paper-about-memory-qa',
    ])
    assert len(groups) == 2


def test_conditions_extracted_with_spans_missing_unknown():
    cond = conditions.extract(PAPER_A_TEXT, url=MIRROR_URLS[0])
    assert cond['task']['status'] == 'known'
    assert cond['task']['span'] and cond['task']['span'] in PAPER_A_TEXT
    assert 'SWE-bench' in (cond['task']['value'] or '')
    assert cond['population']['status'] == 'known'
    assert cond['metric']['status'] == 'known'
    assert cond['resource_budget']['status'] == 'known'
    # Field absent from a sparse abstract stays unknown — never invented.
    sparse = 'We discuss agent memory in general terms without reporting a trial.'
    sparse_cond = conditions.extract(sparse)
    assert sparse_cond['task']['status'] == 'unknown'
    assert sparse_cond['task']['value'] is None
    assert sparse_cond['task']['span'] is None


def test_different_task_papers_are_not_auto_contradiction():
    """Two papers about different tasks are not automatically a contradiction."""
    a = conditions.extract(PAPER_A_TEXT)
    b = conditions.extract(PAPER_B_TEXT)
    rel = claim_graph.relate_findings(
        statement_a='Persistent memory improves coding-agent resolve rate.',
        conditions_a=a,
        statement_b='Persistent memory does not improve HotpotQA exact match.',
        conditions_b=b,
        direction_conflict=True,
    )
    assert rel['relation'] == 'different_scope'
    assert rel['relation'] != 'contradicts'
    assert 'task' in rel['scope_fields']


def test_qualitative_interview_cannot_become_causal_effectiveness():
    interview = (
        'We conducted qualitative interviews with twelve engineers about persistent memory. '
        'Study design: semi-structured qualitative interview study. '
        'Limitation: exploratory; not a causal claim about effectiveness.'
    )
    cond = conditions.extract(interview)
    assert cond['study_design']['status'] == 'known'
    gate = claim_graph.causal_claim_gate(
        statement='Persistent memory causally improves coding-agent effectiveness.',
        conditions=cond,
    )
    assert gate['allowed'] is False
    assert gate['reason'] == 'qualitative_design_not_causal'


def test_fabricated_quote_rejected_in_lane_b_path(tmp_path):
    """Fabricated quotation rejected by an exercised control on the Lane B path."""
    db = tmp_path / 'cases.db'
    url = MIRROR_URLS[0]

    def snap(u, **kwargs):
        if u != url:
            return None
        return {
            'text': PAPER_A_TEXT,
            'sha256': cases.digest(PAPER_A_TEXT),
            'fetched_at': '2026-09-05T00:00:00Z',
            'cache_hit': True,
        }

    with patch.object(instruments, 'document_snapshot', side_effect=snap):
        data = cases.create('When does persistent memory help?', sources=[url], db=db)
    eid = data['evidence'][0]['id']
    fabricated = 'Persistent memory guaranteed a 90% resolve rate in all domains.'
    assert fabricated not in PAPER_A_TEXT
    with pytest.raises(ValueError, match='exact'):
        research.assess(
            data['id'], data['version'],
            statement='Persistent memory always helps.',
            relation='supports',
            rationale='Fabricated span must be refused.',
            evidence_id=eid, quote=fabricated, db=db,
        )
    # Lane B synthesis also refuses to treat an unanchored numeric as material support.
    syn = synthesis.synthesize(data)
    for conclusion in syn['material_conclusions']:
        assert '90%' not in conclusion.get('statement', '')


def test_synthesis_separates_evidence_kinds_and_names_falsification(tmp_path):
    db = tmp_path / 'cases.db'
    urls = {
        MIRROR_URLS[0]: PAPER_A_TEXT,
        'https://docs.example.com/memory-policy': (
            'Official documentation: persistent memory must be scoped per repository; '
            'cross-repo memory is unsupported.'
        ),
        'https://news.ycombinator.com/item?id=1': (
            'Practitioners report using repo-local NOTES.md as persistent memory; '
            'adoption is common on long-running coding agents.'
        ),
    }

    def snap(u, **kwargs):
        text = urls.get(u)
        if not text:
            return None
        return {'text': text, 'sha256': cases.digest(text), 'fetched_at': '2026-09-05T00:00:00Z', 'cache_hit': True}

    with patch.object(instruments, 'document_snapshot', side_effect=snap):
        data = cases.create(
            'When does persistent memory help coding agents?',
            sources=list(urls),
            official_domains=['docs.example.com'],
            db=db,
        )
    emp = next(e for e in data['evidence'] if e['url'] == MIRROR_URLS[0])
    data = research.assess(
        data['id'], data['version'],
        statement='Persistent memory increased resolve rate on SWE-bench verified under an 8-turn budget.',
        relation='supports',
        rationale='Primary empirical study reports the resolve-rate increase under stated conditions.',
        evidence_id=emp['id'], quote=emp['quote'], db=db,
    )
    run = {
        'kind': 'investigate', 'stop_reason': 'evidence_sufficient',
        'question_map': [{
            'id': 'g1', 'status': 'open', 'intent': 'challenge',
            'subquestion': 'Would the effect reverse without the 8-turn budget?',
            'proposed_search': 'persistent memory SWE-bench budget ablation failure',
            'gap': 'No budget ablation inspected',
        }],
    }
    syn = synthesis.synthesize(data, run=run)
    assert set(syn['by_kind']) >= {'empirical', 'official', 'adoption', 'local_measurement'}
    assert syn['by_kind']['empirical']
    assert syn['by_kind']['official']
    assert syn['by_kind']['adoption']
    assert syn['material_conclusions']
    for c in syn['material_conclusions']:
        assert c.get('strongest_challenge')
        assert c.get('falsification_condition')
        assert c.get('conditions')


def test_answer_version_diff_distinguishes_change_kinds(tmp_path):
    db = tmp_path / 'cases.db'
    url = MIRROR_URLS[0]
    text_v1 = PAPER_A_TEXT
    text_v2 = PAPER_A_TEXT.replace('38%', '41%') + '\nErratum: resolve rate corrected to 41%.'

    def snap1(u, **kwargs):
        return {'text': text_v1, 'sha256': cases.digest(text_v1),
                'fetched_at': '2026-09-05T00:00:00Z', 'cache_hit': True}

    with patch.object(instruments, 'document_snapshot', side_effect=snap1):
        v1 = cases.create('When does memory help?', sources=[url], db=db)
    eid = v1['evidence'][0]['id']
    quote = v1['evidence'][0]['quote']
    v1 = research.assess(
        v1['id'], v1['version'], statement='Persistent memory helps on SWE-bench repair.',
        relation='supports', rationale='Measured resolve-rate increase.',
        evidence_id=eid, quote=quote, db=db,
    )

    # Newly available source
    other = PAPER_B_URL

    def snap2(u, **kwargs):
        mapping = {url: text_v2, other: PAPER_B_TEXT}
        text = mapping.get(u)
        if not text:
            return None
        return {'text': text, 'sha256': cases.digest(text),
                'fetched_at': '2026-09-05T01:00:00Z', 'cache_hit': False}

    with patch.object(instruments, 'document_snapshot', side_effect=snap2):
        v2 = research.investigate(v1['id'], v1['version'], sources=[other], live=False, db=db)
    # Reinterpretation on same claim
    new_eid = next(e['id'] for e in v2['evidence'] if e['url'] == other)
    new_quote = next(e['quote'] for e in v2['evidence'] if e['url'] == other)
    claim_id = v2['claims'][0]['id']
    v3 = research.assess(
        v2['id'], v2['version'], claim_id=claim_id, statement=None,
        relation='different_scope',
        rationale='HotpotQA finding does not share the SWE-bench task scope.',
        evidence_id=new_eid, quote=new_quote, db=db,
    )
    # Also refresh original URL content to produce source_changed
    with patch.object(instruments, 'document_snapshot', side_effect=snap2):
        v4 = cases.refresh(v3['id'], live=False, db=db)

    diff = synthesis.diff_answers(v1, v4)
    kinds = {c['kind'] for c in diff['changes']}
    assert 'newly_available' in kinds or 'source_newly_available' in kinds
    assert 'reinterpretation' in kinds
    # source_changed when snapshot hash moved
    assert 'source_changed' in kinds or any(
        c['kind'] == 'changed_source' for c in diff['changes']
    )
    assert diff['meaning']


def test_challenge_synthesis_uses_lane_b_graph(tmp_path):
    """Challenge wiring: different-scope evidence must not force CONTESTED."""
    db = tmp_path / 'cases.db'
    support = MIRROR_URLS[0]
    other = PAPER_B_URL

    def snap(u, **kwargs):
        text = {support: PAPER_A_TEXT, other: PAPER_B_TEXT}.get(u)
        if not text:
            return None
        return {'text': text, 'sha256': cases.digest(text),
                'fetched_at': '2026-09-05T00:00:00Z', 'cache_hit': True}

    with patch.object(instruments, 'document_snapshot', side_effect=snap):
        data = cases.create('When does persistent memory help coding agents?',
                            sources=[support], db=db)
    eid = data['evidence'][0]['id']
    quote = data['evidence'][0]['quote']
    data = research.assess(
        data['id'], data['version'],
        statement='Persistent memory improves resolve rate on SWE-bench verified repair.',
        relation='supports', rationale='Empirical study under stated budget.',
        evidence_id=eid, quote=quote, db=db,
    )

    def discover(provider, query, **kwargs):
        return [cases.search.Candidate(other, 'HotpotQA memory study', PAPER_B_TEXT[:100])]

    with patch.object(instruments, 'document_snapshot', side_effect=snap), \
            patch.object(research_run.discovery, 'find', side_effect=discover):
        run = research_run.start_challenge(
            data['id'], version=data['version'], db=db, live=False,
            limits={'max_rounds': 2, 'max_discovery_calls': 4, 'max_document_reads': 6},
        )
    after = cases.get(data['id'], db=db)
    answer = run.get('answer') or {}
    assert 'by_kind' in answer
    assert answer.get('material_conclusions')
    # Graph must expose different_scope when challenge finds the QA paper
    graph = answer.get('claim_graph') or claim_graph.from_case(after)
    relations = {e['relation'] for e in graph.get('edges', [])}
    # Either explicit different_scope edge, or claim remains supported (not auto-contested)
    brief = research.brief(after)
    states = {c['state'] for c in brief['claims']}
    if 'CONTESTED' in states:
        # If contested, there must be a same-scope contradicts — not only different_scope auto-fire
        assert 'contradicts' in {
            a['relation'] for c in brief['claims'] for a in c['assessments'] if a['state'] == 'CURRENT'
        }
    assert 'different_scope' in relations or 'CONTESTED' not in states or answer.get('scope_guard') is True
