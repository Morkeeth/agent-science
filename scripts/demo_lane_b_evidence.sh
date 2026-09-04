#!/usr/bin/env bash
# Stranger path — Lane B study identity, scope guard, synthesis, answer diff.
# No API key, no network. Usage: bash scripts/demo_lane_b_evidence.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
DB="${TMPDIR:-/tmp}/agent-science-lane-b-demo-$$.db"
export AGENT_SCIENCE_CASES_DB="$DB"
cleanup() { rm -f "$DB"; }
trap cleanup EXIT

python3 - <<'PY'
"""Offline Lane B demo: mirrors→one study, different-scope, synthesis, diff."""
import os
from unittest.mock import patch
from clearance import cases, instruments, research, research_run, study, synthesis, claim_graph
from clearance.stack_cli import main

PAPER_A = '''
Title: Persistent memory for coding agents on repository repair.
Task: SWE-bench verified repository repair (Python).
Population: 50 repository issues from the SWE-bench verified split.
Model: Claude 3.5 Sonnet (20241022).
Comparator: identical agent without persistent memory.
Dataset: SWE-bench verified (n=50).
Metric: resolve rate (% of issues with passing tests).
Resource budget: 8 agent turns and at most 120 seconds wall time per issue.
Study design: randomized controlled comparison with matched prompts.
Limitation: results may not generalize beyond Python repair tasks under the stated budget.
Result: Persistent memory increased resolve rate from 24% to 38% under the stated budget.
'''
PAPER_B = '''
Title: Persistent memory for coding agents on multi-hop QA.
Task: HotpotQA multi-hop question answering (English).
Population: 200 HotpotQA development questions.
Metric: exact match accuracy.
Study design: within-subject comparison on fixed questions.
Limitation: not a causal claim about coding effectiveness.
Result: Persistent memory did not improve exact match on HotpotQA under the stated budget.
'''
MIRRORS = [
    'https://arxiv.org/abs/2401.11111',
    'https://arxiv.org/pdf/2401.11111.pdf',
    'https://doi.org/10.48550/arXiv.2401.11111',
]
OTHER = 'https://arxiv.org/abs/2402.22222'
OFFICIAL = 'https://docs.example.com/memory-policy'
ADOPTION = 'https://news.ycombinator.com/item?id=99'
OFFICIAL_TEXT = 'Official documentation: persistent memory must be scoped per repository.'
ADOPTION_TEXT = 'Practitioners report using repo-local NOTES.md as persistent memory; adoption is common.'

db = os.environ['AGENT_SCIENCE_CASES_DB']
docs = {
    MIRRORS[0]: PAPER_A, MIRRORS[1]: PAPER_A, MIRRORS[2]: PAPER_A,
    OTHER: PAPER_B, OFFICIAL: OFFICIAL_TEXT, ADOPTION: ADOPTION_TEXT,
}

def snap(url, **kwargs):
    text = docs.get(url)
    if not text:
        return None
    return {'text': text, 'sha256': cases.digest(text), 'fetched_at': '2026-09-05T00:00:00Z', 'cache_hit': True}

# 1) Study identity
groups = study.group_documents(MIRRORS)
assert len(groups) == 1 and groups[0]['id'] == '2401.11111', groups
assert study.merge_by_title('repair memory', 'qa memory')['merged'] is False

# 2) Seed case with empirical + official + adoption
with patch.object(instruments, 'document_snapshot', side_effect=snap):
    code = main(['research', 'start',
                 'When does persistent memory help coding agents?',
                 '--source', MIRRORS[0], '--source', OFFICIAL, '--source', ADOPTION,
                 '--official-domain', 'docs.example.com',
                 '--db', db, '--plan-only'])
    assert code == 0
    run0 = research_run.list_runs(db=db)[0]
    case_id = run0['case_id']
    data = cases.get(case_id, db=db)
    emp = next(e for e in data['evidence'] if e['url'] == MIRRORS[0])
    data = research.assess(
        case_id, data['version'],
        statement='Persistent memory increased resolve rate on SWE-bench verified under an 8-turn budget.',
        relation='supports',
        rationale='Primary empirical study under stated conditions.',
        evidence_id=emp['id'], quote=emp['quote'], db=db,
    )
    v_supported = data['version']

# 3) Challenge finds different-task paper → different_scope, not auto-contradiction
def discover(provider, query, **kwargs):
    return [cases.search.Candidate(OTHER, 'HotpotQA memory', PAPER_B[:80])]

with patch.object(instruments, 'document_snapshot', side_effect=snap), \
        patch.object(research_run.discovery, 'find', side_effect=discover):
    code = main(['research', 'challenge', case_id, '--db', db, '--max-steps', '8'])
    assert code == 0
    run = research_run.list_runs(case_id=case_id, db=db)[0]
    if run['status'] == 'paused':
        assert main(['research', 'resume', run['id'], '--db', db]) == 0
    run = research_run.get_run(run['id'], db=db)

after = cases.get(case_id, db=db)
answer = run.get('answer') or synthesis.synthesize(after, run=run)
assert 'by_kind' in answer
assert answer['by_kind']['empirical']
assert answer['by_kind']['official']
assert answer['by_kind']['adoption']
assert answer['material_conclusions']
for c in answer['material_conclusions']:
    assert c['strongest_challenge'] and c['falsification_condition']

# Scope: HotpotQA must not force CONTESTED via auto-contradict
rels = {
    a['relation']
    for c in research.brief(after)['claims']
    for a in c['assessments'] if a['state'] == 'CURRENT'
}
graph = claim_graph.from_case(after)
graph_rels = {e['relation'] for e in graph['edges']}
assert 'different_scope' in rels or 'different_scope' in graph_rels or 'CONTESTED' not in {
    c['state'] for c in research.brief(after)['claims']
}

# 4) Answer diff
diff = synthesis.diff_answers(cases.get(case_id, version=v_supported, db=db), after)
kinds = {c['kind'] for c in diff['changes']}
assert 'newly_available' in kinds or 'reinterpretation' in kinds, kinds

# 5) CLI synthesize + compare
assert main(['research', 'synthesize', case_id, '--db', db]) == 0
assert main(['research', 'compare', case_id, '--from-version', str(v_supported), '--db', db]) == 0

# 6) Fabricated quote still refused
try:
    research.assess(
        case_id, after['version'], statement='Always helps.',
        relation='supports', rationale='Fabricated.',
        evidence_id=after['evidence'][0]['id'],
        quote='Guaranteed 90% resolve rate in all domains forever.',
        db=db,
    )
    raise SystemExit('fabricated quote was accepted')
except ValueError as exc:
    assert 'exact' in str(exc)

print('DEMO LANE B OK')
print(f"case={case_id} run={run['id']} studies={len(answer.get('studies') or [])}")
print('by_kind=' + str({k: len(v) for k, v in answer['by_kind'].items()}))
print(f"relations={sorted(rels)} graph_relations={sorted(graph_rels)}")
print(f"diff_kinds={sorted(kinds)}")
print(f"strongest_challenge={answer['material_conclusions'][0]['strongest_challenge'][:100]}")
PY
