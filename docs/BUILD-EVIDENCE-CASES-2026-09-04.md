# Evidence cases — first build

Built from `7d93fd5` in isolated worktrees. This release implements a local case → authored decision → evidence refresh → decision-review flow, plus an explicit local experiment runner. It is not a hosted rollout.

## User outcomes

- Research a builder question through three actual search calls with different objectives: research, official documentation, practitioner experience. Source categories and missing coverage are reported from returned documents, not search labels.
- Inspect exact quotations and full, paginated source snapshots. Quotes establish occurrence only; the support relationship stays unassessed until a reader examines the source.
- Capture context from the user's specified repo. Only local hashes, marker names and commit metadata are recorded; repo contents are not sent to search.
- Bind an authored decision and rationale to specific evidence IDs in a case version.
- Refresh source URLs and discovery; retain history and flag affected decisions. Offline refresh explicitly reports cached reads. No change in saved evidence is not a claim that the web is unchanged.
- Compare two pinned Git commits using one captured acceptance script. Arm order alternates; each run starts from a restored disposable worktree. Acceptance mutation invalidates the result, output collection is bounded, and children in the run's process group are terminated on completion and timeout.
- Use the same case store through CLI and `science_case` MCP. Both accept a custom DB; source drill-down can select a historical version. Case tool output omits full acceptance scripts and captured process output. Raw experiment records remain local.

## Integrity changes

Polarity is checked in both directions. Reuse requires the exact assertion, not a topic substring or broad date slot. Observation history is retained, and newer changes to a verdict, citation or quote prevent old support from being replayed through either cache. Unknowns retry. Refresh reaches the source and search caches as well as the verdict store. Traces contain executed operations; query analytics record one event per lookup.

The old keyword-driven CONTRARY_TO_RESEARCH verdict now abstains. The product cannot infer a scientific contradiction from a seed, stars or a title. Stack markers similarly return an unassessed fit rather than an invented benefit.

Source fetching is restricted to public HTTP(S), including DNS-pinned destinations and redirect checks. Bytes and elapsed time are bounded. Document versions retain text hashes and timestamps; old undated data is not stamped fresh. Ingestion writes unique files and processes the current request only. The declared container layout includes its missing ingestion module and practitioner corpus.

## Validation performed

- New functional suites cover evidence cases, exact assertion reuse, same-subject invalidation, public source fetching, refresh propagation and observed transparency.
- Existing mutation controls and frozen population checks were rerun. The six-item refusal evaluation remains 6/6 versus the 5/6 substring baseline (p=1.0000); no broad accuracy claim follows.
- A real live case made three Parallel calls and read four distinct URLs across two hosts. All four selected quotations occurred in fetched documents. No declared official source was returned; the product reports this gap. Quotes were adjacent evidence, not a settled answer about fresh-session effectiveness.
- An independent agent completed the actual stdio MCP flow: initialize, list tools, create, inspect, decide, refresh, inspect history. It recorded a cautious local-test decision and no effectiveness claim. Its feedback produced cache/fetch counts and full-source drill-down.
- Independent Cursor review found a same-verdict/different-quote fallback gap, now covered by regression testing. Other reviews found acceptance-script mutation, child cleanup, historical-version leakage and quote-loss-on-refresh defects; all received fixes and regression coverage.

The acceptance script in `review/acceptance/evidence_contract.py` is held constant across both experiment arms. It checks four polarity combinations and the uncertainty-to-support failure from the audit. Its scope is evidence integrity, not a benchmark of agent-session strategies.

## Boundaries still open

- New case and experiment flows are local CLI/MCP. The hosted service is unchanged. Shared authentication, per-user request budgets and coordinated multi-instance persistence require the deployment slice.
- The experiment runner executes explicitly selected trusted code. It is not a security sandbox; it does not install dependencies, meter API spend or measure human rework.
- Source text changes trigger review; the system does not infer that a changed page necessarily reverses a decision. Semantic entailment remains a harder problem than quote occurrence.
- Case refresh is explicit. No background monitoring schedule or autonomous repo modification was installed.
- No fresh graphical browser session was available in the audit environment. CLI/MCP flows, renderer checks and HTTP surfaces are the verified interaction surfaces; mobile and accessibility interaction remain unverified.
- Old already-collided claim records cannot be reconstructed by migration. Old traffic analytics remain historical; the one-ask-one-event rule applies to new calls.
