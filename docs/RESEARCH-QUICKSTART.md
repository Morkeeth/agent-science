# Research from the terminal or an MCP agent

Start with a public research question. The first command saves a local plan; it does not call a paid model or search provider.

## Install and make an empty local store

From this checkout:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 scripts/install-cli.py
export PATH="$HOME/.local/bin:$PATH"
export AGENT_SCIENCE_CASES_DB="$HOME/.agent-science/research-cases.db"
agent-science research start "When does persistent memory help coding agents?" --root .
```

`python3 -m clearance` is equivalent to `agent-science`. `--db PATH` selects a separate local store for any research command. Keep case stores outside Git. A new empty store requires no registry bootstrap. The installer refuses to replace an unrelated existing command.

The output includes a run ID, a case ID, the current question map and its missing reasoning capability. `awaiting_reasoning` is a saved plan, not a completed investigation. Read full structured objects with `--json`.

## Inspect, continue and challenge

Use the IDs returned by start. To continue from existing evidence, use `research start "question" --case-id CASE_ID`:

```text
agent-science research show RUN_ID
agent-science research context RUN_ID --json
agent-science research resume RUN_ID
agent-science research cancel RUN_ID
agent-science research show --case-id CASE_ID --json
agent-science research challenge CASE_ID
agent-science research compare CASE_ID --from-version 1
```

Plain resume preserves the host reasoning workflow. The MCP tool `science_research` accepts `start`, `show`, `context`, `resume`, `cancel`, `challenge`, `compare`, `follow`, `updates`, `update`, `experiment-plan` and `protocol` actions. Start takes `question`; run operations take `run_id`; case operations take `case_id`. `show` takes either. Use `case source` / `science_case` source to page through saved source text before making an assessment.

An MCP host reads `context`, then passes one structured JSON object as `proposal` to `resume`. The proposal must include the inspected `case_version` and `next_action`. The host can supply a question map and anchored findings. The same validator checks host and configured-model proposals. An example finish shape is:

```json
{
  "case_version": 1,
  "next_action": {"kind": "finish", "reason": "No primary evidence has been inspected; retain the question as unresolved."},
  "stop_reason": "No primary evidence inspected."
}
```

This example records a limit; it is not a researched answer. Use the actual version and inspected evidence in an investigation. To page through an already saved source, propose `next_action: {"kind":"read","reason":"Inspect the methods after the introduction","urls":["https://example.org/paper"],"offset":12000,"limit":12000}`. This reads local saved text, reserves one document read and makes no external call. The next context shows that window; ordinary read without offset retrieves the URL. Each source reports truncation and its next offset. CLI proposals use `--proposal 'JSON_OBJECT'`. `--proposal` and `--reasoner` are mutually exclusive.

## Explicit live investigation

Live discovery needs a configured provider, a reasoning source, and an explicit aggregate policy. Provider configuration alone does not authorize calls. Parallel uses `PARALLEL_API_KEY`; the optional Perplexity adapter uses `PERPLEXITY_API_KEY`. Missing access must remain visible. The separate reasoning adapter uses `AGENT_SCIENCE_REASONER_MODEL` and `AGENT_SCIENCE_REASONER_API_KEY`; it does not reuse the passage locator's configuration.

Save a bounded policy to `policy.json`, then explicitly approve its shared limits with `agent-science research policy --policy-file policy.json --approve`. Approval is a CLI-only local operation and makes no provider call. MCP cannot approve or increase its own capacity. Supply that same policy on `research start --policy 'JSON_OBJECT'` (or challenge/update). The policy shape is:

```json
{
  "discovery_calls": 8,
  "document_reads": 20,
  "reasoning_calls": 12,
  "rounds": 3,
  "aggregate": {
    "id": "operator-approved-group",
    "limits": {"discovery_calls": 8, "document_reads": 20, "reasoning_calls": 12, "rounds": 3}
  }
}
```

Keep the policy ID and limits identical between approval and start, and use the same case store. These are example ceilings, not measured quality thresholds or spending approval. Reuse the aggregate ID for runs sharing one allowance. The allowance is shared within the selected cases database. Dollar costs can remain unknown. Engine usage counts exclude host reasoning and separate `science_case` source reads; they are not the total cost of an MCP session. Once configured and authorized, the explicit terminal command is `research resume RUN_ID --reasoner gemini --live`. Without those environment values it reports the missing configuration. Supplying `--reasoner` can call the model even when discovery is offline; it still requires the aggregate policy. No paid calls were made for the overnight implementation checks.

MCP hosts can reason themselves and supply proposals. They cannot use `science_research` to execute repository scripts. Explicit `live:true` applies to source work requested in the proposal and still requires the policy.

## Recover an interrupted run

A request interrupted before its result was recorded remains unknown, and its capacity stays reserved. Inspect the run, operation ID and current case first. To continue without asserting that the unknown call failed or was free:

```text
agent-science research reconcile RUN_ID --operation-id OPERATION_ID --case-version VERSION --acknowledgement retain-reservation-and-do-not-retry
```

MCP exposes the same `reconcile` action and fields. Reconciliation preserves the unknown outcome and question map. It requires a fresh host proposal before further model-driven work and does not replay the unknown source request. A completed saved model response is reused after a restart. A run stopped by its resource limit can still accept an explicit local finish proposal with bounded conclusions and gaps; this does not authorize another external call.

## Return to a followed question

```text
agent-science research follow CASE_ID
agent-science research updates
agent-science research update CASE_ID
```

Follow records the current case version. Updates compares saved revisions, ranks changed decisions before other material conclusion changes, and does not consume that baseline. Reading cached snapshots does not check the web. New unassessed documents alone do not count as a changed conclusion. Follow again explicitly acknowledges the current version.

`update` creates an explicit new run against the case. It does not install a scheduler or spend money. Inspect and resume that run under an approved policy to check new evidence.

## Freeze a local experiment before executing it

`research experiment-plan CASE_ID --root .` saves a draft with a list of missing inputs. Required inputs must come from the experiment design, not guessed defaults. To save a complete plan, provide `--protocol-file PATH` containing:

- `hypothesis`: a nonempty statement.
- `claim_refs`: existing `{ "claim_id": "…", "version": 2 }` references from that case.
- `repo`: the selected repository path.
- `tasks`: a fixed list of nonempty task descriptions; the denominator stays fixed.
- `baseline`, `intervention`: commit references for `kind: "code_change"`; saved as immutable commit hashes. Other kinds retain their authored comparison definitions.
- `outcomes`: a list of nonempty acceptance definitions. The selected script must implement these definitions and tasks.
- `budget`: `{ "runs": 1, "timeout": 10, "basis": "one fixed task, one run per arm" }`, with runs 1–10 and timeout 1–300 seconds.
- `stopping_rule`: the planned stopping rule. The code runner performs the fixed number of paired checks, each bounded by the timeout.
- `check_sha256`: for code changes, the SHA256 digest of the selected trusted Python acceptance script, available with `shasum -a 256 PATH`.

The result is `DRAFT` while required fields are missing and `READY` when populated and validated. READY is a plan status, never a result. Non-code experiments have no compatible runner and remain planned.

```text
agent-science research experiment-plan CASE_ID --protocol-file protocol.json
agent-science research protocol PROTOCOL_ID --version 1 --json
agent-science research execute-protocol PROTOCOL_ID --version 1 --check /absolute/path/acceptance.py --trusted
```

The CLI captures the trusted script once, checks its digest, and gives the runner a private captured copy. Both arms run that script on pinned commits. Run only trusted repository code: temporary Git worktrees are not an operating-system sandbox.

Each protocol version has one execution attempt. Repeating a completed execution retrieves its stored result. An interrupted or failed attempt is visible and cannot silently rerun; inspect the case's experiments, then create a new protocol version with `experiment-plan ... --protocol-id PROTOCOL_ID` and a complete replacement protocol file if another attempt is needed. A changed case requires a new protocol version too.

The execution result includes its actual experiment ID and links back to the protocol version. `research protocol` retains those links, and `case show CASE_ID` retrieves the experiment through its case. Raw script source and process output are omitted from protocol responses. A passing check establishes only its named acceptance criteria. It does not establish a general research finding.

## Check corrections and source versions

After inspecting the source ID, a host can submit `next_action: {"kind":"metadata","evidence_id":"SOURCE_ID","reason":"Check for registry corrections or newer versions"}` with the current `case_version`. Explicit live execution under the approved policy checks at most two fixed primary-registry endpoints (Crossref and arXiv), reserving one document read per planned endpoint and one round. Offline execution does not query a registry. Registry response hashes and check times remain separate from source-body freshness.

An incoming retraction, correction or explicitly newer pinned version can flag the conclusion and its decisions for review. A retraction notice is not automatically retracted itself. Missing metadata does not clear earlier flags or prove that no correction exists. Source-body refresh preserves known registry status.

## Freeze and review a repeated evaluation

Prepare a new matched held-out campaign before any result exists. This freezes
the questions, baseline/candidate arms, rubric and explicit unknown resources in
the existing campaign store. It makes no web, model or experiment call:

```text
agent-science research evaluation-prepare --spec-file heldout.json --json
agent-science research evaluation-show CAMPAIGN_ID --json
```

The preparation spec must include `operational_rubric` with
`source_recovery`, `counterevidence` and `experiment_executability`, a
non-empty `unknown_resources` list, and exactly two arms named `baseline` and
`candidate`. Bind executable work with `"protocol": {"id": "...", "version":
1}`. That exact existing protocol must be `READY`, and its baseline and
intervention commits must equal the two campaign arm pins. The manifest freezes
the protocol version, case version, commits, acceptance digest, budget and
stopping rule. Free-form protocol descriptions are rejected. If `protocol` is
absent, preparation succeeds only as explicitly `UNRESOLVED`; create a protocol
and prepare a new campaign before claiming experiment adequacy.

A prepared campaign is `FROZEN_UNRUN`; its manifest hash is the provenance
anchor. Import later results with `evaluation-record` only after an exact case
version and, for executable work, a completed persisted run have been checked.
`experiment_specificity: pass` also requires a completed execution of the exact
frozen protocol version. The saved observation and each review expose its
protocol ID/version, acceptance digest, execution ID and experiment ID. A saved
plan is never an observation. Preparation rejects a protocol with any execution
history: create a fresh protocol version before freezing a held-out campaign.
Execution must start after the campaign freeze. The saved experiment must exist,
be valid, and match the protocol and observation's exact case/version, repository,
commit pins and acceptance-script digest. Record and review reject dangling or
mismatched result references. Observations freeze hashes of the actual result and
execution; later reviews re-resolve those exact bytes. Older observations without
this result binding remain readable but cannot authorize a new experiment pass.
These are local integrity checks, not tamper-proof storage or proof that the
acceptance criterion measures scientific benefit.

Use `pass`, `fail` or `unknown` for each criterion;
missing protocol, source or rubric evidence stays unknown.

```text
agent-science research evaluation-create --spec-file evaluation.json
agent-science research evaluation-show EVALUATION_ID
agent-science research evaluation-record EVALUATION_ID --observation-file observation.json
agent-science research evaluation-review EVALUATION_ID --review-file review.json
```

MCP exposes these four actions with `evaluation_spec`, `evaluation_id`, `observation` and `evaluation_review`. The specification fixes question IDs and expected distinctions, independently authored rubric, arms, resource limits, evidence modes and repetitions before runs begin. See `review/morning/EVALUATION.md` for the complete schema. This operation makes no provider call.

Each observation binds manual judgments and source anchors to an actual case version and completed run. Duplicate runs cannot fill additional repetitions. Saved-source replay cannot be marked fresh web. The report lists missing slots, errors and paired comparability; retrieval and synthesis are different tasks. Runtime source hashes and clean local Git pins provide bounded provenance; they do not attest dependencies, hardware, loaded-module state or models. Engine-operation duration excludes host waiting and separately issued tools. Unknown latency, tokens and billing stay unknown.

Practical consequences are explicitly authored inferences. Answers group empirical findings, official constraints and field adoption; reports of use never become measured effectiveness merely through grouping.

An independent review appends a version to the original observation; it does not replace the run or the original judgments. Supply `arm_id`, `question_id`, `repetition`, `expected_review_version` (zero for the first review), `reviewer`, all six `judgments` and optional `errors`. Concurrent or stale writers are rejected. Historical case and source hashes bind every review to the evidence actually observed.

Metadata requests use public registry GETs without a paid search provider. The CLI still requires an approved aggregate capacity policy for live requests; a free-only policy can set discovery and reasoning limits to zero. An offline check can be followed by a live check. Failed registry checks retain their receipts on the run without creating an evidence revision. Correction flags make conclusions and decisions require review; they do not assert that every passage in a corrected paper is false. New interpretations of those passages remain explicitly flagged. Retractions and superseded sources cannot supply new synthesis anchors.

## Inspect local experiments and corrected sources

Retrieve a host context trial through its case with `research context-trials CASE_ID`.
See [context trial setup](context-trial-runner.md) for frozen tasks, instruction arms
and trusted CLI execution. A prepared attempt is not an executed result.

Use `research source-reviews CASE_ID` when registry notices affect conclusions.
[Correction review](source-correction-review.md) explains how to inspect the notice,
record a scoped disposition and preserve the source history.


## Return to an investigation and open the claim

```bash
agent-science research desk --query "retrieval"
agent-science research open CASE_ID
agent-science research open CASE_ID --claim CLAIM_ID
agent-science research save CASE_ID
# On the return visit, after another investigation or refresh has saved a revision:
agent-science research desk
agent-science research open CASE_ID --claim CLAIM_ID
agent-science research seen CASE_ID --version INSPECTED_VERSION
```

The desk searches existing case questions and shows unseen versions and claims
that require review. It is paginated, newest saved cases first; `--query` narrows
the shelf. `open` groups the saved claims, including conflicting and unresolved
readings. Open one claim to see its exact quoted support, surrounding passage at
the original evidence version, current source binding, and correction or withdrawal
notice. Both original and current sources have executable inspection commands.
These passages are saved snapshots; opening them does not check the web.

`save` follows an investigation without clearing changes on repeated saves.
`seen --version` records only the version you inspected. Opening a page does not
mark it seen, and marking it seen does not clear a scientific correction or make
an authored claim true. A newer concurrent revision remains unseen. The older
`follow` action still resets its comparison baseline; use `save` for the return
journey. For fresh research, use the existing `update` and inspect/resume flow;
provider calls still require the existing explicit policy approval.

The same actions are available through `science_research`: `desk` (`query`,
`offset`), `open` (`case_id`, optional `claim_id` and `version`), `save` (`case_id`),
and `seen` (`case_id`, exact `version`). There is no hosted account requirement,
new model, automatic background refresh, or new evidence store.
