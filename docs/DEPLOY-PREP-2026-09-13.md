# Deploy prep — 2026-09-13 (Oscar only · do not run from cloud agent)

**Script:** `deploy.sh` (45 lines) · **Current hosted:** rev `agent-science-00028-hed` · `mode=private-workspaces`  
**This doc is a checklist.** Deploy / promote / secret rotation = Oscar's click.

Diff vs live `deploy.sh` on this branch tip: **none required for tonight's offline gates.** Night wave touched docs, fixtures, eval scripts, and `verify_cold_clone.sh` only — no `clearance/` runtime change that needs a new revision for the stranger offline path.

---

## What deploy.sh does (read before click)

| Step | Action | Secret surface |
|------|--------|----------------|
| 1 | Describe Parallel + workspace-access secrets | must already exist |
| 2 | Ensure runtime SA `agent-science-workspace@…` | IAM create if missing |
| 3 | Bind secret accessor + workspace bucket IAM | no plaintext env |
| 4 | Deploy **`--no-traffic --tag=workspace-candidate`** | atomic; timeout **240s** |
| 5 | Print `CANDIDATE_REVISION` + current traffic JSON | Oscar promotes later |

**Not in deploy.sh:** public repo flip · Devpost · video · npm publish · local corpus seed ("Existing cloud state is never replaced").

---

## Pre-deploy (Oscar)

- [ ] Parallel key rotated if any old revision ever had plaintext env (`hack.md` OPEN QUESTIONS)
- [ ] `gcloud auth` + project `hack-fleet` (or `$GCP_PROJECT`)
- [ ] Secrets `parallel-api-key` and `agent-science-workspace-access` have ENABLED versions
- [ ] Review: `git log --oneline -10` on the revision you intend to ship
- [ ] Read `docs/RECEIPT-live-compound-BLOCKED-2026-09-13.md` — hosted unauthenticated routes **303→Sign-in**

---

## Deploy command (candidate only)

```bash
cd agent-science
bash deploy.sh
# Expected: CANDIDATE_REVISION=…  and traffic JSON still on previous revision
```

**Do not** promote from a cloud agent.

---

## Post-candidate verify (Oscar)

```bash
HOST=https://agent-science-568004190078.us-central1.run.app
curl -sf "$HOST/health" | python3 -m json.tool
# expect mode private-workspaces

# Authenticated workspace paths only — bearer token, never in URL
# Do NOT expect unauthenticated /search desk (303 → Sign-in)
```

---

## If deploy fails

| Symptom | Check |
|---------|-------|
| Secret describe fails | Secret exists in `$GCP_PROJECT` |
| SA missing | Script creates `agent-science-workspace` — needs `iam.serviceAccount.create` |
| Candidate up, promote forgotten | Traffic still on old revision — intentional until Oscar promotes |
| 504 on long clear | timeout is 240s; use compound-mini / offline receipt for demos |
