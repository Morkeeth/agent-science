# Agent Science

Research a builder question, inspect the source evidence, and record a decision that can change when its evidence changes.

**Clearance desk (hackathon track):** paste a documentary script → every checkable claim back as a **verbatim quote + URL**, or **UNSOURCED** with a named reason. Constraint: if the document does not contain the exact passage, refuse — never paraphrase. Partners at runtime: Vertex · Parallel · Cloud Run · ADK (`docs/PARTNER-INTEGRATIONS-2026-08-30.md`).

Agent Science is a CLI/MCP research companion for coding work. Public-source discovery, versioned evidence, decisions and repo experiments work locally without a hosted account. The CLI and MCP interface keep the question, exact source quotations, source snapshots, actual search attempts, repo context and decision history together.

## Use it from your terminal

From this checkout, install the local command once:

```bash
python3 scripts/install-cli.py
```

Then run `agent-science` from your own repository. It preserves that working directory, so `--root .` captures your repo rather than Agent Science's checkout. The installer uses `~/.local/bin` and never replaces an unrelated command. Add that directory to your PATH if it is not already there.

```bash
agent-science case review --root .
agent-science case list --query "fresh sessions" --root .
```

The longer `python3 -m clearance` form below works from this checkout too.

## Start a research case

```bash
python3 -m clearance case create \
  "Do fresh agent sessions reduce repeated errors in long coding tasks?" \
  --root . --official-domain code.claude.com --live
```

`--live` enables three Parallel discovery calls: research, official documentation and practitioner experience. Up to two results per angle are fetched. Duplicate URLs are read once. The source categories actually found are reported separately from the intended search angles.

Omit `--live` to use cached sources only. Provide repeated `--source URL` options to investigate specific documents without search calls. Keys are loaded at runtime; they do not belong in the repo. Install the runtime dependencies with `pip install -r requirements.txt` for the SDK/ADK paths.

CLI and MCP cases are private local data in `~/.agent-science/cases.db`. Use `--db PATH` or `AGENT_SCIENCE_CASES_DB` to choose another store. Repo context contains marker names, content hashes and the Git commit; file contents are not sent to search.

The result includes a case ID and evidence IDs. Use those IDs with:

```text
python3 -m clearance case show CASE_ID
python3 -m clearance case source CASE_ID --evidence EVIDENCE_ID
python3 -m clearance case decide CASE_ID --version 1 --statement "The decision" --reason "Why this evidence matters" --evidence EVIDENCE_ID
python3 -m clearance case refresh CASE_ID --live
python3 -m clearance case show CASE_ID --version 1
```

A decision cites one case version. Refresh retains old snapshots and flags dependent decisions when their source text changes, a source becomes unavailable, or the repo context changes. It does not silently reverse the decision. An offline refresh checks stored snapshots only; its output reports cached reads separately from web fetches.

**A verified quote proves that a source contains those words. It does not, by itself, prove that the source supports the question.** Cases leave that relationship unassessed. Inspect the source snapshot before recording an authored decision. Stars, search categories and a paper title are not evidence of effectiveness.

## Return to decisions that need review

```bash
python3 -m clearance case review --root .
python3 -m clearance case list --query "fresh sessions" --root .
```

These commands inspect saved cases without web requests. Review filtering happens before pagination, so an older unresolved decision is not hidden behind newer cases. Use `--limit` and `--offset` to page through matching cases; `list --json --page-info` adds pagination metadata while plain `list --json` retains its array shape.

Read the current case and its source version, then replace a decision with your revised reasoning:

```text
python3 -m clearance case decide CASE_ID --version 2 --supersedes DECISION_ID --statement "Revised choice" --reason "What changed and why it matters" --evidence EVIDENCE_ID
```

`--version` is required: a refresh between reading and saving rejects the stale decision. Superseding retains the old decision and its evidence history. Source output names its case version, fetch time and content hash; long documents include the next offset.

## Import research and investigate gaps

Import a Perplexity report as Markdown/text, or a Sonar JSON response with `choices[0].message.content` and `citations`. The report stays local. Import reads its cited URLs only; it does not send report text or repo contents to a search provider.

```bash
# Reuse saved research before making a new provider call
agent-science case find "RAG for my repo"
agent-science case find "human intervention" --json

agent-science case import report.md --question "Do fresh sessions reduce repeated errors?" --root . --live
```

Without `--live`, only existing source snapshots are read. By default, up to 12 cited documents are inspected; `--max-documents` permits 1–40. PDF sources use bounded text extraction through the pinned `pypdf` dependency; encrypted, scanned or oversized PDFs remain unavailable. The original report and all extracted citation URLs are retained, and `brief` lists unread citations. Imported paragraphs become **unassessed passages**, not independently verified claims. Numbered `[1]` citations are matched to Markdown reference definitions (including titles) or Sonar's citation array. Sonar `search_results` URLs are retained as leads; their ordering is not assumed to establish citation numbering. Unresolved citation markers remain explicit. Inline URLs are retained too. The parser does not infer missing references or split complex paragraphs into atomic claims.

Use the returned case ID to inspect the report, read a source, or add a targeted search:

```text
agent-science case report CASE_ID
agent-science case brief CASE_ID
agent-science case investigate CASE_ID --version 1 --source https://example.org/cited-paper --live
agent-science case investigate CASE_ID --version 1 --query "fresh sessions coding agents replication failures" --provider parallel --provider perplexity --limit 5 --live
```

Use repeated `--source URL` to read up to 10 unread citations directly, without a search query or provider key. An explicit live source read also rechecks an existing snapshot.

Investigation retains prior evidence and records the explicit query, providers, actual attempts and newly read sources. `--limit` bounds results per provider to 1–10. New sources receive provider attribution; duplicate URLs are read once. Each write advances the case version. Always inspect the new version before the next write.

Perplexity uses its [first-party Search API](https://docs.perplexity.ai/api-reference/search-post), configured with `PERPLEXITY_API_KEY` or `~/.config/keys/perplexity.key`. Parallel case discovery caches and receipts live in `~/.agent-science/search` (override with `AGENT_SCIENCE_SEARCH_DIR`), outside Git. Live investigation bypasses discovery caches; each attempt, including an unavailable provider, advances the case version. There is no Perplexity cache yet; offline calls explicitly skip it. Missing credentials and failed requests are recorded as unavailable/error attempts, with no fabricated results or automatic paid retries. Request counts are recorded; provider billing is not inferred. Existing lookup/visibility routing remains unchanged; choose providers through `case investigate`.

## Assess a claim against evidence

After reading a source with `case source`, record your interpretation with an exact source passage:

```text
agent-science case assess CASE_ID --version 2 --claim CLAIM_ID --relation supports --evidence EVIDENCE_ID --quote "Exact passage copied from this source snapshot" --reason "Why this result supports this claim, and where it applies"
```

Use `--statement` instead of `--claim` to add a new claim. Relations are `supports`, `contradicts`, `context` and `unresolved`. The first three require an exact 20–4000 character source quote; unresolved claims may have no source. Quote occurrence is mechanically checked. The interpretation remains authored by the user or agent; it is not an automatic entailment judgment or a confidence score.

The brief shows supporting and opposing assessments, open questions and stale evidence. Opposing active assessments produce `CONTESTED`. Use `--supersedes ASSESSMENT_ID` with `--claim` to replace an assessment, preserving its historical version. Refresh checks source changes; affected claims enter `case review` alongside affected decisions. Separate hosts are listed for visibility, never counted as independent experiments.

MCP exposes the same actions through `science_case`: `import` takes `report_text` instead of reading a file; `investigate` takes `query` and `providers`, or `sources` for direct citation reads; `assess` takes `claim_id` or `statement`, `relation`, `rationale`, `evidence_id` and `quote`. `investigate` and `assess` require the inspected `version`. `brief` and `report` support historical versions; report text is paginated with `offset` and `limit` and omitted from routine case output.

## Test a practice on your repo

The experiment command runs a selected, trusted Python acceptance script against two immutable Git revisions. It captures the script once, alternates arm order across pairs, restores the pinned worktree before each run, and records pass counts, wall time, output hashes and limitations.

```text
python3 -m clearance case experiment CASE_ID --repo . --baseline BASE_COMMIT --candidate CANDIDATE_COMMIT --check /path/to/acceptance.py --runs 3
```

The case repo must match the experiment repo. The acceptance script runs with that revision as its working directory and Python import path. Both revisions must have their required runtime dependencies available. The tool does not install packages or execute commands from research pages.

The result names its experiment ID and pinned commits. Cite that measured result directly in a decision:

```text
python3 -m clearance case decide CASE_ID --version 1 --experiment EXPERIMENT_ID --statement "The choice supported by this check" --reason "Measured result and limits"
```

A decision can cite source IDs, valid experiment IDs, or both. Experiments from another case and invalid runs are rejected. The measurement stays bounded to its selected check and commits; it is not a general recommendation.

Use independent acceptance criteria. A test copied from the implementation can defend the same bug. Modified acceptance scripts invalidate the experiment; child processes are cleaned up after each run. This is a runner for trusted local code, not an OS sandbox. API cost, human rework and general practice superiority are not inferred from pass counts or wall time.

## Agents and the existing search surface

```bash
python3 -m clearance mcp
python3 -m clearance visibility "your question" --full --root .
python3 -m clearance lookup "a specific factual assertion" --live --refresh
python3 -m clearance serve
```

`science_case` provides create, show, source, decide, refresh, list and review over MCP. Decide requires `version` and accepts `supersedes` and `experiment_ids`. List/review accept `root`, `query`, `page_size` and `offset`; `page_info=true` adds list pagination metadata. Rejected tool actions set `isError=true`. Experiments require the explicit local CLI. `science_visibility` shows actual lookup attempts and matched catalog context. `science_lookup` reuses only the same settled assertion; `refresh=true` bypasses verdict, document and search caches. An unsupported keyword match cannot become a research-conflict verdict.

The local browser desk remains available for documentary clearance. The [hosted service](https://agent-science-568004190078.us-central1.run.app) is a separate deployment; these local changes are not automatically deployed there.

## Verification

```bash
python3 tests/test_evidence_cases.py
python3 tests/test_evidence_integrity.py
python3 tests/test_same_subject_integrity.py
python3 tests/test_safe_sources.py
python3 tests/test_visibility_transparency.py
python3 tests/test_watch_it_go_red.py
python3 scripts/eval_refusal_baseline.py
```

The frozen six-item refusal evaluation currently distinguishes the shipping verifier from its substring baseline on one item: 6/6 versus 5/6, McNemar p=1.0000. This small result does not establish broad superiority. The new adversarial suites check polarity, exact-claim reuse, invalidation, source boundaries and decision-version behavior separately.

Source fetches accept public HTTP(S) only, pin validated DNS addresses, revalidate redirects, and limit bytes and time. Cached snapshots retain content hashes and fetch times; legacy snapshots remain undated. Hosted workspaces add authentication, request budgets and conditional cloud persistence; see below. See [the build receipt](docs/BUILD-EVIDENCE-CASES-2026-09-04.md) for the current scope and validation.

MIT licensed.


## Optional hosted evidence inspector

[Open the workspace](https://agent-science-33kamss2jq-uc.a.run.app/cases). [Build and verification receipt](docs/BUILD-HOSTED-CASES-2026-09-04.md).

The hosted service now serves `/cases`: question → saved sources → authored decision → refresh → review. A revised decision can supersede an earlier one while preserving its evidence and reasoning. Historical source pages stay bound to the version you opened.

Sign in with a workspace access token, or use `Authorization: Bearer <token>` with the JSON API. Keep tokens out of URLs. Each workspace has a separate cloud database. Local case databases and repo experiments are never uploaded by deployment.

- `GET /api/cases?page=1` lists 20 cases and the current request allowance.
- `POST /api/cases` accepts `request_id`, `question`, optional `sources` / `official_domains`, and boolean `live`.
- `GET /api/cases/{id}?version=1` reads a saved version.
- `GET /api/cases/{id}/sources/{evidence_id}?version=1&offset=0` reads source text.
- `POST /api/cases/{id}/refresh` accepts a new `request_id` and boolean `live`.
- `POST /api/cases/{id}/decisions` accepts `request_id`, current `version`, `statement`, `rationale`, `evidence_ids`, and optional `supersedes` decision ID.

Use a random UUID for each new mutation and reuse it when retrying that same mutation. A completed retry returns the saved result. An interrupted request requires a fresh ID after checking the workspace. A concurrent write returns 409 instead of replacing newer data. Stale decision forms also return 409.

The default limits are **10 admitted live research runs per workspace per UTC day**, **50 across the service**, and **100 writes per workspace / 1,000 across the service**. These are configured request ceilings, not measured dollar costs. Failed research attempts count. Jobs stop after 180 seconds; hosted source collections stop at 24 documents. New browser cases select live research by default; turn it off to create an empty case. Offline refresh reuses that case's saved sources and makes no claim about web freshness.

The cloud runtime exposes private case routes and public liveness only. Earlier public `/search`, `/clear`, `/ingest`, registry and query-history routes remain available in the local legacy server, not the hosted workspace. Repository uploads and experiment execution remain local.

Deployment uses a dedicated runtime service account, Secret Manager access configuration, a private GCS bucket, and conditional generation writes. The upload allowlist excludes caches, local databases, notes and media. `deploy.sh` references existing pinned secret versions; it neither uploads local state nor rotates credentials.

For local workspace development, set `AGENT_SCIENCE_HOSTED=1`, `AGENT_SCIENCE_WORKSPACE_DIR` to a private directory, `AGENT_SCIENCE_PUBLIC_ORIGIN=http://127.0.0.1:8080`, and `AGENT_SCIENCE_ALLOW_HTTP=1`. `AGENT_SCIENCE_ACCESS_CONFIG` is JSON with a random `session_key` of at least 43 characters and `users` mapping workspace slugs to SHA-256 token hashes. Use random access tokens of at least 32 characters. Run `python3 cloud/service.py`. Cloud Run refuses to start without cloud storage and access configuration.

### Find research in daily use

`case find "QUERY"` searches saved questions, claims and active assessment reasoning. It recognizes explicit topic vocabulary such as RAG/Obsidian, memory/context files, UX/intervention and multi-agent coordination. Matches explain their terms and topics. Relevance does not change the scientific assessment. Results include authored limits, source links and a version-pinned `case brief` command. `--root .` requires an existing directory and restricts results to cases attached to that exact repository; omit it to search all local cases. Use `--limit` and `--offset` for pagination.

The normal personal `visibility` result also includes saved research, alongside its dictionary result. With an explicit root it restricts saved cases to that repository; without one it searches across repositories. A dictionary miss does not erase related case evidence. With `personal=False`, visibility never opens the private case store. MCP agents use `science_case` with `action: "find"` and `query`. This path makes no web or model call; it does not search full source snapshots or original report bodies. Selected source quotes attached to assessments can appear in results.

Read the assessment limits before choosing an experiment. Use `case experiment` with a trusted acceptance script and explicit baseline/candidate commits to measure a repository change. Retrieved suggestions are not executable instructions or measured results.
