# Lane A receipt — 2026-09-05

Worktree: `/Users/morkeeth/CODE/agent-science-night-a`.
Branch: `build/night-investigation-20260905`.
Base: `007705c` (product baseline `e12ca6f` plus plan/contract).
Owned files: `clearance/night_runs.py`, `clearance/reasoning.py`, `tests/test_night_runs.py`.
Initial slices: `137b6af`, `60e1b3b`. This receipt accompanies the final validation/recovery slice.
B dependencies used for cross-component tests: `a744ba9`, `a1f14b3`; their local cherry-pick copies are not additional A changes.

## Built

- No-network start, local prior-research retrieval, durable question maps, versioned case references, run revisions and operation IDs.
- Host proposal stepping and autonomous callable loop. Search/read actions invoke the existing investigation path. The next reasoning context contains actual stored source snapshots and provider/access outcomes.
- Separate explicitly configured Gemini structured reasoner. No change to the Gemini source locator; no model or source shell execution. Configuration uses `AGENT_SCIENCE_REASONER_MODEL` and `AGENT_SCIENCE_REASONER_API_KEY`; adapter construction alone makes no call.
- Challenge pins the answer version and its strongest challenges. Current authored synthesis and related anchored prior claims appear in context. Original imported prose, repository paths/content and decisions are excluded.
- Per-case serial writer lock and current-version checks. Durable cancel request takes effect after an in-flight operation; its result and reservations remain recorded.
- Atomic per-run and shared policy reservation. Shared policy lives in the selected cases database, is keyed by an explicit ID and has immutable limits. Every resource limit is required in the shared policy. Live or external model calls without this policy stop before invocation.
- `usage` explicitly means conservative reserved capacity, including offline work. `observed_usage` records completed responses, document reads and explicit cache/fetch events. Costs remain unknown, never inferred from counts.
- Started or interrupted uncertain operations stop in `needs_reconciliation`; resume never blindly repeats them. Confirmed no-effect local finding validation is recorded as rejected, releases its action reservation and permits a corrected proposal.
- Per-source truncation metadata and follow-up source offsets. Repeating an identical investigation action stops with a diminishing-evidence reason. Missing sources and provider access remain visible to the next reasoning step.

## Verified

Actual command in this worktree:

```text
python3 -m pytest tests/test_night_runs.py tests/test_studies_synthesis.py tests/test_research_expansion.py tests/test_evidence_cases.py tests/test_research_search.py -q
........................................................................ [ 80%]
..................                                                       [100%]
90 passed in 4.31s
```

All databases were temporary test fixtures. Provider/document/adapter effects were substituted with explicitly labelled controlled fixtures. Tests did not query the personal case database or call paid providers.

Exercised controls include:

- A follow-up query chosen from the previous stored source's untested repository-scale gap, followed by inspection of the actual returned failure fixture.
- A challenge reading a new source and changing the authored answer's scope while preserving the original version.
- Two runs against one case: one investigation commits, the stale run is rejected before another provider invocation.
- Cancellation while a provider is blocked: completed in-flight evidence retained and no next provider invocation.
- Shared aggregate exhaustion, missing shared live policy, restarted `started` operation, and interrupted invocation; unknown outcomes cannot replay.
- Fabricated quotation: no case mutation or provider call; corrected same-version proposal succeeds afterward.
- Source-selected shell action rejected; private-network URL rejected before invocation.
- Real configured-adapter serialization and JSON parsing exercised through a substituted HTTP response; this is a transport fixture, not a live model result.
- Prior anchored claims and source truncation visible; inaccessible provider reported; cached read never counted as an online fetch.

## Limits

No live scientific investigation, live provider/model validation, measured research quality comparison or spend occurred in lane A. Fixtures prove controls and workflow behavior, not scientific conclusions.

The shared resource ceiling is scoped to one selected cases database. There is no cross-database/global billing service or dollar-cost estimator. Reserved capacity is conservative and is not generally refunded after calls, even if a provider was unavailable.

Unknown operations intentionally have no automatic resolution/retry action in the revision-1 public API. They preserve their saved response/case references when available and require inspection; cancelled runs are terminal. A new run does not establish that an unknown prior request was free.

Cancellation cannot revoke a request already in flight; it prevents the next operation. Version checks also detect writers outside the night-run lock, but do not make those other modules participate in the lock.

Source context contains bounded excerpts; it does not claim that omitted source text was inspected. Model-selected queries remain explicitly authored public queries; this module does not infer scientific truth or make a claim that every material research gap was exhausted.
