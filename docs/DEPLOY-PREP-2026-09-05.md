# Deploy prep — 2026-09-05 (Oscar only · do not run from cloud agent)

**Script:** `./deploy.sh` (repo root) · **Current hosted:** rev `agent-science-00026-zel` · mode `private-workspaces`

This checklist matches the **current** `deploy.sh` object. The 2026-09-03 prep doc described an older `--clear-env-vars` + corpus-seed path and is stale.

---

## What deploy.sh does now (read the file)

| Step | Action | Notes |
|------|--------|-------|
| 1 | Require Secret Manager secrets `parallel-api-key` + `agent-science-workspace-access` | Fail closed if missing |
| 2 | Ensure runtime SA `agent-science-workspace@…` + secretAccessor | |
| 3 | Ensure GCS bucket `${PROJECT}-agent-science-workspaces` + objectUser | **No local corpus/case seed** — comment in script |
| 4 | Deploy **candidate** revision with `--no-traffic --tag=workspace-candidate` | timeout **240s**, concurrency 1, max-instances 3 |
| 5 | Wire secrets via `--set-secrets` only (no `--set-env-vars` for API keys) | Env is workspace limits + bucket + origins |
| 6 | Print `CANDIDATE_REVISION` + traffic JSON | **Does not promote traffic** |

**Not in deploy.sh:** public repo · Devpost · video · npm · flipping open `/search` without auth.

---

## Diff vs live (Oscar eyes)

```bash
curl -sS https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
# expect: mode private-workspaces, ok true

git log --oneline origin/main -10
diff -u <(git show HEAD:deploy.sh) deploy.sh   # if reviewing a branch
```

Hosted stranger surface **measured 2026-09-05**:

| Path | Unauthenticated result |
|------|------------------------|
| `/health` | 200 JSON |
| `/search`, `/registry`, `/visibility/ui`, `/truths/ui`, `/popular/ui`, `/cases` | 303 → Sign in /login |
| `POST /clear` | **401** |

Judges cannot run the old open compound demo on this revision without a workspace token.

---

## Pre-deploy (Oscar)

- [ ] Parallel key rotated if any old revision held plaintext env (`hack.md` OPEN QUESTIONS)
- [ ] `gcloud auth` + project `hack-fleet` (or `$GCP_PROJECT`)
- [ ] Secrets enabled: `parallel-api-key`, `agent-science-workspace-access`
- [ ] Decide: keep private-workspaces for submit, **or** add a separate public exhibit service — product ruling 2026-09-04 says CLI/MCP is primary; dashboard must not become required
- [ ] If filming hosted: have a workspace bearer ready; never put it in a URL
- [ ] Review orphan-works timeout: prior **504 @ 300s**; current deploy timeout is **240s** — full script still unsafe for video; use compound-mini / fresh subject

---

## Deploy command (Oscar click)

```bash
cd agent-science
bash deploy.sh
# → CANDIDATE_REVISION=…
# Verify candidate URL, then promote that exact revision (gcloud run services update-traffic …)
```

---

## Post-deploy verify

```bash
HOST=https://agent-science-568004190078.us-central1.run.app
curl -sf "$HOST/health" | python3 -m json.tool

# Without token — expect login wall / 401, not 500:
curl -sS -D- -o /dev/null "$HOST/search?q=test&live=false" | head -5
curl -sS -D- -o /dev/null -X POST "$HOST/clear" -H 'Content-Type: application/json' -d '{}' | head -5

# With workspace token (Oscar): private /api/cases path only — do not send repo paths
```

**Offline stranger path (no deploy):**

```bash
python3 tests/test_registry_surface.py -q
python3 scripts/compound_exhibit_receipt.py
python3 scripts/eval_artifact_claims.py
```

---

## Do not

- Run this from a cloud agent
- `--set-env-vars` PARALLEL/GEMINI plaintext
- Claim open hosted `/visibility/ui` on Devpost while mode is `private-workspaces`
- Seed cloud from local user case DBs (constitution / hosted workspace boundary)
