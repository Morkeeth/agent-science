# Deploy prep — 2026-09-07 (Oscar only · no agent click)

**Script:** `deploy.sh` (current main) · **Do not run from cloud agent**

This checklist matches the **private workspace** deploy path that replaced the old public desk. Deploy creates a **candidate revision with `--no-traffic`** — traffic promote is a separate Oscar click.

---

## What deploy.sh does now (read before click)

| Step | Action | Secret surface |
|------|--------|----------------|
| 1 | Require existing Secret Manager secrets `parallel-api-key` + `agent-science-workspace-access` | no local key file read into argv |
| 2 | Ensure runtime SA `agent-science-workspace@…` + secret accessor IAM | SA create if missing |
| 3 | Ensure workspace bucket (`$PROJECT-agent-science-workspaces`) + objectUser IAM | public-access-prevention on |
| 4 | Pin **immutable** secret versions (latest ENABLED) | reproducible revision |
| 5 | `gcloud run deploy … --no-traffic --tag=workspace-candidate` | candidate only |
| 6 | Env: `AGENT_SCIENCE_HOSTED=1`, public origin, allowed origins, bucket, daily limits | no Gemini plaintext |
| 7 | Secrets: `PARALLEL_API_KEY`, `AGENT_SCIENCE_ACCESS_CONFIG` | versions pinned |
| 8 | Print `CANDIDATE_REVISION` + current traffic JSON | Oscar verifies before promote |

**Not in deploy.sh:** public repo flip · Devpost · video · npm publish · automatic traffic promote · seeding local corpus/case data into cloud.

**Diff vs DEPLOY-PREP-2026-09-03:** old prep described `--clear-env-vars` + public desk `/health` with `engine_default`. Current script deploys `cloud/case_http.py` private-workspaces shape (`mode: private-workspaces`, login wall). Post-deploy `new_user_trial.sh` is expected **RED** until a public desk exists again.

---

## Pre-deploy (Oscar)

- [ ] Parallel key rotated if any old revision ever had plaintext env (`hack.md` OPEN QUESTIONS)
- [ ] Secrets already populated: `parallel-api-key`, `agent-science-workspace-access`
- [ ] `gcloud auth` + project `hack-fleet` (or `$GCP_PROJECT`)
- [ ] Decide: keep private-workspaces for submit video, **or** restore public desk (separate change — not this checklist)
- [ ] Review `git log --oneline -10` on `main` before click

---

## Deploy command (candidate only)

```bash
cd agent-science   # local clone with gcloud
bash deploy.sh
```

Expected: `CANDIDATE_REVISION=…` and note that candidate has **no traffic**.

Promote (Oscar only, after verify):

```bash
# Example only — Oscar chooses the exact revision name printed by deploy.sh
gcloud run services update-traffic agent-science --region=us-central1 \
  --to-revisions=REVISION=100
```

---

## Post-deploy verify (run each — expect honest RED on stranger trial)

```bash
HOST=https://agent-science-568004190078.us-central1.run.app

curl -sf "$HOST/health" | python3 -m json.tool
# expect: ok true, mode private-workspaces, revision …

bash scripts/new_user_trial.sh "$HOST"
# expect EXIT 2 RED while mode=private-workspaces

# Offline stranger path still green (no hosted needed):
python3 tests/test_registry_surface.py -q
python3 scripts/compound_exhibit_receipt.py
```

**Do not claim:** unauthenticated hosted `/search` · `/registry` · `/clear` compound · `/visibility/ui` for judges — measured 2026-09-07 as login wall (`docs/ARTIFACT-CLAIM-EVAL-2026-09-07.json`).

---

## If deploy fails

- Missing secret → create/version in Secret Manager first (never paste key into `deploy.sh` argv)
- SA missing → script creates it; re-run
- Bucket conflict → check `WORKSPACE_BUCKET`
- Do **not** remove generation preconditions or seed cloud from local user case DBs
