# Agent Science

Research a builder question, inspect the source evidence, and record a decision that can change when its evidence changes.

Agent Science combines public-source discovery with versioned cases, available locally or in a private hosted workspace. The CLI and MCP interface keep the question, exact source quotations, source snapshots, actual search attempts, repo context and decision history together.

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
python3 -m clearance case decide CASE_ID --statement "The decision" --reason "Why this evidence matters" --evidence EVIDENCE_ID
python3 -m clearance case refresh CASE_ID --live
python3 -m clearance case show CASE_ID --version 1
```

A decision cites one case version. Refresh retains old snapshots and flags dependent decisions when their source text changes, a source becomes unavailable, or the repo context changes. It does not silently reverse the decision. An offline refresh checks stored snapshots only; its output reports cached reads separately from web fetches.

**A verified quote proves that a source contains those words. It does not, by itself, prove that the source supports the question.** Cases leave that relationship unassessed. Inspect the source snapshot before recording an authored decision. Stars, search categories and a paper title are not evidence of effectiveness.

## Test a practice on your repo

The experiment command runs a selected, trusted Python acceptance script against two immutable Git revisions. It captures the script once, alternates arm order across pairs, restores the pinned worktree before each run, and records pass counts, wall time, output hashes and limitations.

```text
python3 -m clearance case experiment CASE_ID --repo . --baseline BASE_COMMIT --candidate CANDIDATE_COMMIT --check /path/to/acceptance.py --runs 3
```

The case repo must match the experiment repo. The acceptance script runs with that revision as its working directory and Python import path. Both revisions must have their required runtime dependencies available. The tool does not install packages or execute commands from research pages.

Use independent acceptance criteria. A test copied from the implementation can defend the same bug. Modified acceptance scripts invalidate the experiment; child processes are cleaned up after each run. This is a runner for trusted local code, not an OS sandbox. API cost, human rework and general practice superiority are not inferred from pass counts or wall time.

## Agents and the existing search surface

```bash
python3 -m clearance mcp
python3 -m clearance visibility "your question" --full --root .
python3 -m clearance lookup "a specific factual assertion" --live --refresh
python3 -m clearance serve
```

`science_case` provides create, show, source, decide, refresh and list over MCP. Experiments require the explicit local CLI. `science_visibility` shows actual lookup attempts and matched catalog context. `science_lookup` reuses only the same settled assertion; `refresh=true` bypasses verdict, document and search caches. An unsupported keyword match cannot become a research-conflict verdict.

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


## Private hosted workspaces

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
