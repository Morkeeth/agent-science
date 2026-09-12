# Deploy prep — 2026-09-12 (Oscar only · do not run from cloud agent)

**Script:** `deploy.sh` (45 lines) · **Current hosted:** rev `agent-science-00028-hed` · `mode=private-workspaces`  
**This doc is a checklist.** Deploy / promote / secret rotation = Oscar's click.

---

## What deploy.sh does now (diff vs 2026-09-03 prep)

| Was (2026-09-03 prep) | Is now (`deploy.sh` @ main) |
|-----------------------|-----------------------------|
| `--clear-env-vars` then `--set-secrets` | **No** clear-env; atomic `--no-traffic --tag=workspace-candidate` |
| Corpus bucket seed from local `cache/*.db` | **No local seed** — "Existing cloud state is never replaced" |
| Vertex/Gemini plaintext scrub narrative | Parallel + **workspace access** secrets only |
| Direct traffic to new revision | Candidate tag only; Oscar verifies then promotes |
| timeout 300s (older narrative) | **`--timeout=240`** |

Secrets required before click:

- `parallel-api-key` (Secret Manager)
- `agent-science-workspace-access` (Secret Manager)
- Runtime SA `agent-science-workspace@${GCP_PROJECT}.iam.gserviceaccount.com`
- Bucket `${PROJECT}-agent-science-workspaces`

---

## Pre-deploy (Oscar)

- [ ] Parallel key rotated if any old revision ever had plaintext env (`hack.md` OPEN QUESTIONS)
- [ ] `gcloud auth` + project `hack-fleet` (or `$GCP_PROJECT`)
- [ ] Both secrets exist and have an ENABLED version
- [ ] Review: `git log --oneline -10` on the revision you intend to ship
- [ ] Read `docs/RECEIPT-live-compound-BLOCKED-2026-09-12.md` — hosted `/search` is 501 by design now

---

## Deploy command (candidate only)

```bash
cd agent-science
bash deploy.sh
# Expected: CANDIDATE_REVISION=…  and traffic JSON still on previous revision
```

**Do not** promote from a cloud agent. After candidate health checks, Oscar promotes the exact revision.

---

## Post-candidate verify (Oscar)

```bash
HOST=https://agent-science-568004190078.us-central1.run.app
# candidate host from deploy output tag workspace-candidate
curl -sf "$HOST/health" | python3 -m json.tool
# expect mode private-workspaces

# Authenticated workspace paths only for /cases and research — bearer token, never in URL
# Do NOT expect unauthenticated /search or /partners (501)
```

---

## Night-wave note (2026-09-12)

Build lane shipped **docs + offline eval gates + compound fixture fix** only. No runtime Python change to `clearance/` pipeline requires deploy for the stranger offline path. Deploy is optional unless Oscar needs a new candidate for video or workspace demos.

Files safe without deploy:

- `scripts/eval_compound_cost_arms.py`, `tests/test_compound_cost_arms.py`
- `fixtures/scripts/compound-mini-B.txt`, `compound-mini-B-paraphrase.txt`
- `fixtures/price-cards/parallel-search-2026-09-12.json`
- `docs/SUBMISSION-PACK-2026-08-29.md`, receipts

---

## If deploy fails

| Symptom | Check |
|---------|-------|
| Secret describe fails | Secret exists in `$GCP_PROJECT` |
| SA missing | Script creates `agent-science-workspace` — needs `iam.serviceAccount.create` |
| Candidate up, promote forgotten | Traffic still on old revision — intentional until Oscar promotes |
| 504 on long `/clear` | timeout is 240s; use compound-mini for demos |
