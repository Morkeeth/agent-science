# Deploy prep — slice 1 (Oscar only) · 2026-09-15

**Script:** `deploy.sh` · **Do not run from cloud agent**

This is a pre-flight checklist for the **current** `deploy.sh` on `main`. Older prep docs (`DEPLOY-PREP-2026-09-03.md`, `DEPLOY-CLICK-LIST-2026-09-01.md`) describe a previous corpus-seed + `--clear-env-vars` flow that **no longer matches the script**.

---

## What deploy.sh does now (read the file, not this summary alone)

Verified by reading `deploy.sh` at HEAD (45 lines):

| Step | Action | Secret / risk surface |
|------|--------|------------------------|
| 1 | Require existing Secret Manager secrets `parallel-api-key` and `agent-science-workspace-access` | Secrets must already exist — script does **not** create key material from a local file |
| 2 | Ensure runtime SA `agent-science-workspace@…` + secretAccessor on both secrets | IAM |
| 3 | Ensure workspace bucket `gs://${PROJECT}-agent-science-workspaces` with public-access-prevention | GCS |
| 4 | Deploy **candidate** revision: `--no-traffic --tag=workspace-candidate` | Live traffic unchanged until Oscar promotes |
| 5 | Env: hosted flags, public origin, daily research/mutation budgets, timeout 180s research / Cloud Run timeout **240** | No plaintext Parallel/Gemini in `--set-env-vars` |
| 6 | Secrets via `--set-secrets` pinned to **enabled** secret versions | Immutable version pin |
| 7 | Print `CANDIDATE_REVISION` + traffic JSON — **does not** shift traffic | Oscar promotes separately |

**Explicitly absent vs 2026-09-03 prep:** no local `~/.config/keys/parallel.key` upload · no corpus DB seed to GCS · no `--clear-env-vars` · no post-deploy public `/search` stranger trial (hosted is private-workspaces).

**Not in deploy.sh:** public repo flip · Devpost · video · npm publish · traffic promotion.

---

## Diff vs last known public clearance revision

| Concern | Prior (clearance desk) | Current (`deploy.sh` 2026-09-15) |
|---------|------------------------|----------------------------------|
| Hosted mode | Public `/search` `/clear` `/registry` | `mode=private-workspaces` — `/health` only unauthenticated; `/cases` needs access key |
| Timeout | 300s (orphan-works still 504) | Cloud Run `--timeout=240` |
| Traffic | Direct deploy to 100% | Candidate tag, **no traffic** until promote |
| Keys | Optional seed from local key file | Secrets must pre-exist in Secret Manager |

Live probe 2026-09-15 (no deploy from this agent):

```bash
curl -sf https://agent-science-568004190078.us-central1.run.app/health
# {"ok": true, "service": "agent-science", "mode": "private-workspaces",
#  "revision": "agent-science-00028-hed"}
```

Unauthenticated `/search`, `/registry`, `/clear` → **303** to `/login` (or 501 on some aliases). Stranger clearance demo is **local CLI/MCP**, not the hosted URL, until Oscar decides otherwise.

---

## Pre-deploy (Oscar)

- [ ] Parallel key rotated if any old revision ever had plaintext env (`hack.md` OPEN QUESTIONS)
- [ ] Secret Manager: `parallel-api-key` and `agent-science-workspace-access` enabled versions exist
- [ ] `gcloud auth` + project `hack-fleet` (or `$GCP_PROJECT`)
- [ ] Set `AGENT_SCIENCE_PUBLIC_ORIGIN` to the HTTPS service origin if `gcloud run services describe` cannot resolve it
- [ ] Review `git log --oneline -5` on the commit you intend to deploy
- [ ] Decide traffic: candidate-only verify vs promote to 100%

---

## Deploy command (Oscar click)

```bash
cd agent-science
bash deploy.sh
# expect: CANDIDATE_REVISION=… and traffic still on the prior revision
```

Promote only after candidate verify (Oscar):

```bash
# example — confirm revision name from deploy.sh output first
gcloud run services update-traffic agent-science --region=us-central1 \
  --to-revisions=REVISION_NAME=100
```

---

## Post-deploy verify (candidate or live)

```bash
HOST=https://agent-science-568004190078.us-central1.run.app
# or candidate URL from Cloud Run tag workspace-candidate

curl -sf "$HOST/health" | python3 -m json.tool
# expect mode=private-workspaces

# With workspace access key (never put token in a URL):
# curl -sf -H "Authorization: Bearer $TOKEN" "$HOST/api/cases" …
```

**Local stranger path (no hosted token):**

```bash
python3 scripts/seed_document_cache.py
python3 -m clearance lookup "2012/28/EU"          # SOURCED cheap, 0 Parallel
python3 scripts/compound_exhibit_receipt.py       # A=2→B=1 offline
python3 tests/test_watch_it_go_red.py             # 72/72
```

**Do not claim:** public hosted compound on `/clear`, orphan-works full script under 240s, or unauthenticated `/search` SOURCED on current revision.

---

## Night-wave code safe to deploy (this branch)

Runtime fix that affects hosted fetch cache identity:

- `clearance/instruments.py` — `canonical()` unquotes CELEX `%3A` vs `:` so seed and routing share one document key

Docs/eval only (optional for submit path):

- `scripts/eval_artifact_claims.py`, `compound_exhibit_receipt.py`, `full_gate.sh`
- `fixtures/scripts/compound-mini-B.txt` (exact overlapping assertions)
- `docs/SUBMISSION-PACK-2026-08-29.md`, receipts, this prep file
