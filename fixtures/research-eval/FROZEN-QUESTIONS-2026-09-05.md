# Frozen evaluation questions — NIGHTPLAN 2026-09-05

Frozen before adaptive-loop tuning on this branch. These are question texts and
family labels only — **not** measured performance claims. Do not edit in place;
append a new dated file if the set must change.

Development set (12) · Acceptance holdout (6) — one holdout per family.

## Memory / context

- DEV: When do repository context files help, and when do they reduce task success?
- DEV: When does persistent memory across agent turns change coding outcomes under a fixed token budget?
- HOLD: When should an agent discard prior session state rather than summarize it?

## Retrieval

- DEV: When does hybrid retrieval earn its extra context cost?
- DEV: When does keyword search outperform embedding retrieval on repository Q&A?
- HOLD: When does retrieval augmentation harm answer faithfulness on grounded coding questions?

## Coding workflows

- DEV: Does test feedback improve coding outcomes on tasks unlike the benchmark?
- DEV: When do repository-local acceptance scripts predict merge readiness better than unit tests alone?
- HOLD: When does tool-using code generation fail relative to single-shot generation on the same task?

## UX / design

- DEV: What evidence supports when an agent should ask a human to intervene?
- DEV: When do confirmation prompts reduce irreversible mistakes without blocking throughput?
- HOLD: When does showing intermediate plans improve human acceptance of agent edits?

## Coordination

- DEV: When do delegated agents improve outcomes under matched resource budgets?
- DEV: When does a shared scratchpad beat message-passing between agents on multi-file tasks?
- HOLD: When does multi-agent debate change decision quality versus a single agent with equal tokens?

## Evaluation

- DEV: Which evaluation metrics predict accepted changes rather than plausible output?
- DEV: When does pass@k misrank coding agents relative to human review outcomes?
- HOLD: When do offline static evals disagree with live repository acceptance checks?

## Arms (for later measurement — not run live this session)

1. **Naive fixed search** — `research_run.naive_fixed_search_arm` / `cases.create` three angles
2. **Adaptive challenge** — `research_run.start_challenge` against a pinned answer
3. **Always-silent null** — no investigation; contradict count stays 0

Fixture offline comparison for (1) vs (2) was executed:
`python3 scripts/eval_research_challenge_baseline.py` → naive 0, adaptive 1.
Live six-family field pass requires Oscar-authorized providers.
