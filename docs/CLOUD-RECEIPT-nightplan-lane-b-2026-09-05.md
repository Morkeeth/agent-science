# Cloud receipt — NIGHTPLAN 2026-09-05 · Lane B

**Branch:** `cursor/nightplan-lane-b-evidence-0a46`  
**Base (Lane A):** `cursor/nightplan-research-engine-b1eb` @ `f550893`  
**HEAD at receipt write:** run `git rev-parse HEAD` on this branch (do not trust a stale hardcoded SHA)  
**Session:** cloud agent · 2026-09-05 overnight Lane B

## Status

Lane B (evidence + conditional conclusions) landed on top of Lane A. Study identity collapses DOI/arXiv HTML/PDF mirrors and refuses title-only merges. Conditions carry source spans; missing stays unknown. Claim graph adds `different_scope`. Challenge synthesis separates empirical / official / adoption / local measurement and names strongest challenge + falsification per material conclusion. Answer diffs distinguish changed source vs newly available vs reinterpretation.

## Commands (stranger / offline)

```bash
bash scripts/demo_lane_b_evidence.sh
# → DEMO LANE B OK · different_scope · by_kind populated · diff newly_available+reinterpretation

python3 scripts/eval_lane_b_baseline.py
# → shipping identity 2 > naive title-merge 1 (false-positive merge of paper B) · null 1
# → shipping scope different_scope · naive auto-contradict contradicts

python3 -m pytest -q tests/test_lane_b_evidence.py
# → 9 passed

agent-science research synthesize CASE_ID
agent-science research compare CASE_ID --from-version N
```

## Verified at object (commands run this session)

| Claim | Command | Result |
|-------|---------|--------|
| Five mirrors → one study | `pytest …::test_five_mirrors_of_one_paper_are_one_study` | passed |
| Title-only merge refused | `pytest …::test_title_only_merge_is_refused` | passed |
| Conditions + unknown | `pytest …::test_conditions_extracted_with_spans_missing_unknown` | passed |
| Different tasks ≠ auto-contradiction | `pytest …::test_different_task_papers_are_not_auto_contradiction` | passed · relation=`different_scope` |
| Qualitative ≠ causal supports | `pytest …::test_qualitative_interview_cannot_become_causal_effectiveness` | passed |
| Fabricated quote rejected | `pytest …::test_fabricated_quote_rejected_in_lane_b_path` | passed · ValueError `exact` |
| Synthesis kinds + falsification | `pytest …::test_synthesis_separates_evidence_kinds_and_names_falsification` | passed |
| Answer version diff kinds | `pytest …::test_answer_version_diff_distinguishes_change_kinds` | passed |
| Challenge uses Lane B graph | `pytest …::test_challenge_synthesis_uses_lane_b_graph` | passed |
| Full Lane B suite | `python3 -m pytest -q tests/test_lane_b_evidence.py` | **9 passed** |
| Stranger demo | `bash scripts/demo_lane_b_evidence.sh` | exit 0 · DEMO LANE B OK |
| Baseline arms (re-derived) | `python3 scripts/eval_lane_b_baseline.py` | shipping 2 · naive 1 · null 1 · naive_title_merge_false_positive=true |
| Lane A still green | `bash scripts/demo_research_challenge.sh` · `pytest tests/test_research_run.py` | DEMO OK CONTESTED · passed |
| Lane A baseline still green | `python3 scripts/eval_research_challenge_baseline.py` | adaptive_wins=true |

**Red-then-green:** first collection of `tests/test_lane_b_evidence.py` raised `ImportError: cannot import name 'claim_graph'` before modules existed. That was the observed red. After implementation, 9/9 passed.

## What landed

- `clearance/study.py` — Study objects, arXiv/DOI/PMC identity, `merge_by_title` refuse, mirror grouping
- `clearance/conditions.py` — structured conditions with verbatim spans; unknown when absent
- `clearance/claim_graph.py` — relations including `different_scope`; causal gate for qualitative designs
- `clearance/synthesis.py` — separated by_kind synthesis; per-conclusion challenge/falsification; `diff_answers`
- `clearance/research.py` — `different_scope` relation; causal gate on supports
- `clearance/research_run.py` — challenge assessments use scope guard; `_synthesize` → Lane B synthesis
- CLI/MCP — `research synthesize` · `research compare` · MCP actions match
- `scripts/demo_lane_b_evidence.sh` · `scripts/eval_lane_b_baseline.py`
- `tests/test_lane_b_evidence.py` — 9 executed controls

## Finding that can embarrass us (kept)

`eval_lane_b_baseline.py` shows the naive title-merge arm **wrongly merges** the HotpotQA paper into the SWE-bench study (Jaccard ≥ 0.4 on shared “persistent memory for coding agents” tokens). Shipping refuses that merge. The naive auto-contradict arm labels the pair `contradicts`; shipping labels `different_scope`. If shipping ever scores ≤ naive/null on identity, the eval prints it in `verdict.embarrassing`.

## Oscar-only leftovers (stop at the door)

- Film / Devpost / key rotation / hosted redeploy with secrets
- Live Parallel/Perplexity six-topic field pass (`parallel_configured` not assumed on this VM)
- Lane C followed-question store, update ranking, experiment protocols
- Public push of release candidate — Oscar reviews
- Frozen 18-question eval set with held-out acceptance (not run live)

## Known limits (honest)

- Condition extraction is pattern/label-led, not a model reasoner; sparse abstracts leave fields unknown by design
- Dataset extractor can latch onto the same SWE-bench span as task when labels share tokens
- `different_scope` requires a *known* task mismatch; unknown+unknown with a contrary cue still records `contradicts` (Lane A challenge path preserved)
- No live provider validation on this VM; demos use fixtures
- `tests/test_research_expansion.py` PDF/httpx cases need optional deps (`pypdf`, `httpx`) — pre-existing env gap, not introduced here
