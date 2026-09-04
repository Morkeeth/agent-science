# Agent Science: overnight research engine

Status: **Lane A landed on branch `cursor/nightplan-research-engine-b1eb`** — adaptive research run + challenge + resume; CLI/MCP wired; offline demo and naive baseline eval exit 0. Lanes B/C and live six-topic field pass remain open. Receipt: `docs/CLOUD-RECEIPT-nightplan-2026-09-05.md`.
Baseline: e12ca6f7c4ad489b8e20bb16c307470635b0883d · plan commit `69cc6b1`.

## Morning product target

A developer asks a broad question from their repository. Agent Science finds prior research, decomposes the question, reads original sources, pursues evidence that could change the answer, and returns a cited conclusion with its conditions and unresolved gaps. The developer can challenge that conclusion, resume the investigation, compare it with an earlier version, and define an experiment for their repository.

The signature behavior is **“What would change this answer?”** Each conclusion names its strongest challenge and the observation or experiment that could reverse it. A challenge must produce a real follow-up investigation, not another paragraph agreeing with the first answer.

The day-two user returns to a tracked question and sees new evidence, changed conclusions, and affected decisions. Research accumulates across memory/context, retrieval, coding workflows, UX/design, coordination and evaluation.

CLI and MCP remain the main interfaces. Extend the existing cases and preserve the current visual design. This plan does not authorize a public push, deployment, or overnight spending.

## Proposed user flow — interfaces to build

```text
agent-science research "When does persistent memory help coding agents?" --root .
agent-science research challenge CASE_ID
agent-science research resume RUN_ID
agent-science research compare CASE_ID --from-version VERSION
agent-science research follow CASE_ID
agent-science research updates
agent-science research experiment-plan CASE_ID --root .
```

The initial command produces a local plan. Explicit live execution uses a configured run policy and reports its limits. MCP exposes the same persisted run and case objects; the coding agent can supply reasoning steps through the same validation contract used by the CLI reasoner.

The answer starts with the bounded conclusion and practical consequence. It then shows conditions, evidence for and against, what practitioners actually use, unresolved questions, and what would change the answer. Adoption signals remain separate from empirical effectiveness. Every substantive assertion has an inspected source anchor or is explicitly marked as an inference or unresolved.

## Starting point and architecture

Already available: case revisions and decisions (`cases.py`), import/investigate/assess/brief (`research.py`), Parallel and Perplexity adapters (`discovery.py`), source snapshots and PDF extraction, local retrieval (`research_search.py`), and comparisons on pinned repository commits (`experiments.py`).

Build three cooperating components around those functions:

1. Research-run orchestration: question decomposition, actionable gaps, provider/model calls, checkpoints and stopping reasons.
2. Evidence interpretation: study identity, study conditions, claim relationships, competing explanations and versioned synthesis.
3. Daily use: terminal/MCP commands, question following, change reports, experiment protocols and first-use setup.

Existing source independence helpers group some URL families; they do not establish study identity or independent replication. Existing Gemini code locates passages and must retain that contract. Add a separate structured reasoning adapter rather than teaching the quote locator to issue scientific verdicts.

## Three build lanes and one coordinator

Each lane starts from the pinned baseline in its own worktree. The coordinator owns the interface contract, integration branch, evaluation set and release receipt. Every lane reads the same plan and current repository instructions, verifies its actual branch/worktree, and maintains a ranked queue within its ownership. No shared working tree. No parallel changes to the same integration files.

### A — Autonomous investigation

Own new run-state and planner modules, plus narrowly scoped discovery changes.

Ordered work:
- Persist a question map: subquestion, competing explanation, importance, proposed search, inspected evidence and current gap.
- Implement the loop: retrieve locally → choose next gap → discover → read originals → propose assessments → validate anchors → revise the map → decide the next action.
- Search distinct intents: original result, replication/failure, official constraints and field practice. Use query content, not a fixed “three angles” ceiling, to choose follow-ups.
- Follow cited URLs and study identifiers. Record inaccessible documents, failed provider calls and exhausted gaps explicitly.
- Implement challenge as a new run against a pinned answer version, looking for observations that could overturn its material claims.
- Add interruption/resume, bounded calls, cancellation and explicit stop reasons: evidence sufficient for the stated scope, diminishing new evidence, missing access, or budget exhausted.

Acceptance: a follow-up query is demonstrably chosen from a gap found in a previous source; a challenge can revise the answer; interruption does not lose completed evidence or blindly repeat a paid call. A fixed search list or repeated prompt is not completion of this lane.

### B — Evidence and conditional conclusions

Own new study/claim/synthesis modules. Propose migrations through the shared contract; the coordinator integrates changes to case storage.

Ordered work:
- Normalize DOI and arXiv identities and versions; associate HTML/PDF mirrors with the same study. Preserve uncertain links as candidates rather than merging by title resemblance.
- Extract structured conditions with source spans: task, population, model/version, comparator, dataset, metric, resource budget, study design and limitations. Missing data remains unknown.
- Represent claim relationships: support, contradiction, different scope, context only and unresolved. Preserve authorship and the source version behind each interpretation.
- Produce a synthesis that separates empirical findings, official constraints, field adoption and local measurements.
- Add the strongest challenge and a falsification condition to each material conclusion.
- Diff answer versions by changed evidence and reasoning; distinguish a changed source from a newly available source and from a changed interpretation.

Acceptance: five reports repeating one paper remain one study; two papers about different tasks are not automatically a contradiction; a qualitative interview study cannot become a causal claim about effectiveness. A fabricated quotation or unsupported numerical result is rejected by an exercised control. Model agreement is not a measure of truth.

### C — Daily CLI/MCP, updates and local experiments

Own new command/render/watch/protocol modules and first-use documentation. The coordinator alone edits shared CLI and MCP entry points after the component interfaces are fixed.

Ordered work:
- Build the proposed command family and matching MCP actions using the shared run contract. Expose current intent, completed evidence work, the next action and stop/cancel/resume controls.
- Add a followed-question store and an explicit update run. Reuse snapshots where appropriate; only actual fetches advance “checked online” timestamps.
- Rank updates by their effect on a saved conclusion or decision. Show a meaningful empty result when nothing material changed.
- Create versioned experiment protocols: hypothesis, cited claim versions, selected repository, fixed tasks, baseline and intervention, outcome definitions, comparison budget and stopping rule.
- Connect compatible code-change protocols to the existing experiment runner. Other experiments remain explicitly planned until a real runner executes them. Never relabel a plan as a result.
- Complete fresh installation and provider setup, and guide a new user from an empty local store to their first useful live investigation.

Acceptance: a new terminal user and a real MCP agent can research, challenge, inspect evidence, follow a question and see a changed decision. A protocol records its denominator before execution. The user can execute a trusted repository comparison and retrieve its actual outcome through the case.

## Shared contract, fixed before fan-out

The coordinator writes schemas and thin interface tests first, without building the whole implementation serially:

- `ResearchRun`: ID, case ID, base case version, question map, status, cursor, configured limits, observed usage, step events and stop reason.
- `RunStep`: stable operation ID, proposed public query or source URL, model/provider identity, state, response reference and resulting case version. Unknown external outcomes are explicit; retries cannot assume an unobserved request was free.
- `Study`: canonical identity, versions, document references, identity evidence and extracted conditions with anchors.
- `Synthesis`: case version, material conclusions, conditions, competing evidence, unresolved gaps, strongest challenge and falsification conditions.
- `ExperimentProtocol`: immutable version, source claim references, repository/commit pins where applicable, frozen task set, acceptance definition and budget basis. Executed experiments remain separate records linked back to the protocol.

One serial writer per case handles mutations with expected-version checks. Source work can run concurrently, but assessments and synthesis must bind to the exact committed evidence they used. Historical cases remain readable. Private case contents and repository files do not become provider queries by default.

Reasoning comes from the configured model adapter or the MCP host. Both submit structured proposals to the same validator. Public source content is data, never tool authority. Without an available reasoner, expose the saved plan and the missing capability; do not claim an autonomous run completed.

## Overnight execution sequence

These are ordering checkpoints, not estimates of engineering duration.

1. **Orient and freeze:** verify lane ownership and dependencies; pin the baseline and evaluation inputs; verify provider access without printing keys; fix the shared contract; create a deliverable registry with owner, branch, commit, status and evidence path.
2. **First integrated path:** all three lanes deliver thin working implementations early. Run one real question from CLI and MCP before expanding scope. Keep integration continuous; do not leave it until morning.
3. **Expand together:** adaptive challenge, study deduplication, scoped synthesis, change reports and experiment protocols. After each merge, run the affected user path against the actual integration commit.
4. **Live field pass:** one real investigation in each of the six topic families. Reuse the existing four cases as prior work, then expand to coding workflows and evaluation. Keep provider receipts and research snapshots outside Git.
5. **Independent review and morning acceptance:** Cursor and Fable review a pinned candidate. Fix findings, exercise failure controls and rerun affected flows. Verify the installed command against the final local integration commit.

If a lane loses provider access, it continues with protocol implementation, stored-source replay, another already-authorized provider or the MCP reasoning path. The missing live validation remains named. It does not turn fixtures into live evidence. Each lane continues down its queue rather than pausing at routine milestones.

## Frozen evaluation and real evidence

Freeze 18 questions before tuning: three each for memory/context, retrieval, coding, UX/design, coordination and evaluation. Use 12 for development and six unseen questions for acceptance, one from each family. These are proposed sample sizes, not measured performance claims.

Compare against the pinned current build under the same recorded resource limits. Preserve baseline outputs and source snapshots. Run the six held-out questions three times to expose variation. Keep reproducible snapshot replay separate from fresh-web runs; neither stands in for the other.

Question examples:
- When do repository context files help, and when do they reduce task success?
- When does hybrid retrieval earn its extra context cost?
- Does test feedback improve coding outcomes on tasks unlike the benchmark?
- What evidence supports when an agent should ask a human to intervene?
- When do delegated agents improve outcomes under matched resource budgets?
- Which evaluation metrics predict accepted changes rather than plausible output?

Acceptance questions and expected distinctions must be written independently of the new synthesis. Reviewers inspect primary source passages and task definitions, not only the engine's own explanations.

Report per question: relevant original evidence recovered, citation correctness, scope errors, strongest contrary evidence considered, unresolved gaps, proposed experiment specificity, latency, observed calls/tokens and billing where actually available. Keep a named error inventory. Do not compress unknowns into an invented confidence percentage.

Exercise failure controls: duplicate mirrors, incomparable populations, retracted/superseded evidence where metadata is available, unavailable PDFs, fabricated quotes, malicious page instructions, stale versions, interrupted requests, exhausted limits and missing keys. A control only counts after its failure path has fired.

## Run policy and operating boundaries

Proposed per-live-question ceilings: 8 discovery calls, 20 document reads, 12 reasoning calls and 3 investigation rounds. These are initial operating limits, not evidence-quality thresholds or spending authorization. The launch configuration must also contain an approved aggregate resource/cost policy; atomically reserve capacity before calls and stop when it is exhausted. Record unknown costs as unknown. Do not infer dollar billing from request counts.

Use Parallel where already configured. Exercise Perplexity only if valid access is available; absence does not block the rest of the build. Cached/offline work continues independently. No silent provider retries beyond the run policy.

Followed-question updates run explicitly under the same policy. A scheduler can invoke that operation after it is configured; this plan does not install an always-on paid loop. Local experiment execution still requires a selected trusted script. Models and search pages cannot choose arbitrary executable code.

## Morning deliverables

- An integrated CLI/MCP investigation and challenge flow, with runnable commands.
- Six real topic investigations with source-grounded conclusions and explicit limits, or exact named gaps where live validation did not occur.
- A changed-answer report that points to affected decisions.
- A frozen experiment protocol and at least one executed repository comparison, reported only as evidence for its actual check.
- Fresh-user installation through a first useful query, plus the existing local workflows still passing.
- Frozen-baseline comparison results, failure-control output and independent review findings.
- `NIGHTRUN-2026-09-05.md`: What this is / Shipped / Verified (actual output) / Reverted / Needs operator / Scorecard / Next prompt. Include exact commits and outstanding work. Maintain lane receipts separately; aggregate the final closeout once.

All proposed capabilities remain outstanding until built and exercised. Prepare a concrete release candidate and source diff for publication review; the older local film commits and other uncommitted work must not be swept into a public push.
