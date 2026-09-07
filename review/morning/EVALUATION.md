# Frozen research evaluation campaign

Lane base: `ea05a10`. Branch: `build/science-evaluation-20260905`.

The new local module freezes the questions, independently authored expected distinctions, rubric, arms, resource limits and repetition denominator before evaluated runs. It records reviewed outcomes by exact case version and completed run. It does not execute research, call providers, or expose expected answers through engine context.

## Callable contract

`create(spec, *, db=None)`, `get(campaign_id, *, db=None)`, `record(campaign_id, observation, *, db=None)`.

Spec fields:
- `title`, `authored_by`, `rubric_provenance`: explicit text identifying authorship and independent preparation.
- `questions`: objects with `id`, `topic`, `question`, `expected_distinctions` (nonempty text list). The module adds exact question hashes.
- `arms`: objects with `id`, `kind` (`synthesis` or `retrieval`), `mode` (`snapshot_replay` or `fresh_web`), `resource_limits` (named nonnegative integer ceilings), and exactly one `code_ref` (full lowercase 40-character commit hash) or `baseline_policy` (authored procedure).
- `repetitions`: integer 1–100.
- `rubric`: independent text for each of `original_sources`, `citation_correctness`, `scope_errors`, `contrary_evidence`, `unresolved_gaps`, `experiment_specificity`.

Observation fields:
- `arm_id`, `question_id`, `repetition`, exact `question_hash`, `mode`, `resource_limits` matching the frozen arm.
- `case_id`, exact positive `case_version`, `run_id`. Only an explicitly authored baseline may omit the run. An empty retrieval plan cannot be recorded as a baseline.
- `reviewer`, `judgments`: all six criteria with `status` (`pass`, `fail`, `unknown`), explanatory `rationale`, and `anchors` list containing `evidence_id` and exact `quote`.
- Optional `errors`: list of objects with named `kind` and `detail`.

A source-dependent pass for original evidence, citations or contrary evidence requires an inspected anchor. Quote occurrence is checked against the pinned source bytes; this does not prove semantic support. Unknown criteria stay unknown, without numeric substitution. Caller-supplied calls, costs and latency are rejected. Observed usage and available billing are copied from the completed run; absent latency and tokens remain null. Recording time is separate from runtime latency.

`get` returns the immutable manifest/hash, recorded observations, denominator, missing slots, named errors and paired design comparability. It reports output-task, mode and limit mismatches, plus differing source exposure in observed pairs. Retrieval versus synthesis is explicitly incomparable. Matching designs do not prove causal attribution or research quality.

## Provenance limits

A full commit hash freezes intended code, but existing research runs do not attest their executing code revision. The receipt states this explicitly. Execution provenance still needs an independent pinned-run launcher or reviewer evidence before a scientific quality comparison. Existing baseline cases can be preserved through an authored baseline policy; evaluated runs must be created after the campaign freeze. A completed run cannot fill multiple arms or repetitions. Source snapshots are retained by exact hashes, without copying private source text into campaign output.

Fresh-web observations require a recorded online document fetch in that run. Saved snapshots cannot be relabeled fresh web. This proves a fetch event occurred, not that all sources were fetched online or that the scientific claims are correct. Real live field evaluation remains outstanding.

## Verification

Actual command:

```text
python3 -m pytest -q tests/test_research_evaluation.py tests/test_night_runs.py tests/test_studies_synthesis.py
91 passed in 1.26s
```

The evaluation suite contains 21 controls with actual SQLite cases and completed host-proposal runs. Controls fired for fabricated quotations, changed snapshot bytes, planned runs, mismatched questions/versions/limits/modes, mutable commit aliases, unknown metric injection, duplicate slots, reuse of completed runs, retrospective campaign freezes, empty baseline plans and false fresh-web declarations. Cases contain explicitly artificial source content and are not scientific findings. `git diff --check` passed.

## Runtime provenance follow-up

Observations now inspect the run and every operation's stored runtime provenance. A known clean commit that differs from the frozen arm is rejected. Missing or dirty provenance remains recordable with explicit limitations and cannot produce `comparable_execution: true`. Code pins, clean source hashes, matching output tasks, modes, limits and source exposure must all hold for observed paired executions to pass the structural comparison. This does not establish scientific correctness or causal attribution beyond those controls.

`operational.engine_elapsed_seconds` sums measured monotonic operation durations only when every step has a finite nonnegative measurement. It excludes host waiting and separately issued tools. Missing measurements remain null; total investigation latency and model tokens are still unknown. Recording time remains independent.

Actual follow-up verification: `python3 -m pytest -q tests/test_research_evaluation.py` — **27 passed**. Added controls exercise clean commit mismatch, changed commit between steps, dirty provenance, missing duration, measured operation summation and source-exposure differences. Runtime instrumentation inputs are artificial effects attached to real persisted completed runs; they are not scientific results or real clean-build attestations.

## Independent review after recording

`review(campaign_id, review_object, *, db=None)` appends an immutable review to a recorded outcome. Fields are `arm_id`, `question_id`, `repetition`, `expected_review_version` (0 for the first review), `reviewer`, all six `judgments` using the same anchor validator, and optional `errors`. Evidence identifiers, case version, manifest hash and content hash are selected from the original observation; callers cannot replace them. Later case revisions cannot supply quotations to a review of an earlier observed answer.

The original observation remains unchanged. `get` adds `review_version`, `reviews` and `current_review` to each observation; historical reviews remain readable. `review_coverage` reports observed outcomes with appended reviews and criteria still unknown in the current review (or original judgments when no review exists). `error_inventory` distinguishes original observation errors from each historical review's errors by source and review version. It is an inventory, not a count of currently unresolved errors.

Actual verification: **35 evaluation tests passed**. Additional exercised controls cover optimistic stale/concurrent review rejection, fabricated or later-version quotations, tampered historical evidence, exact integer versions, preservation of original observation bytes and readable review history. No provider calls were made.
