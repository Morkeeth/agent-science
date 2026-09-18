# Deploy prep — 2026-09-18 (Oscar only)

**Script:** `deploy.sh` · **Do not run from cloud agent**  
**Live revision probed tonight:** `agent-science-00028-hed`

This is a pre-flight checklist. Deploy flips a live revision and touches Secret Manager — Oscar's click only.

---

## Why deploy is needed (measured 2026-09-18)

| Probe | Command | Object result |
|-------|---------|---------------|
| Health partner strip | `curl -sS $HOST/health` | JSON has **no** `gemini` / `parallel` / `engine_default` — only `ok/service/mode/revision` |
| Partners public | `curl -sS -D - $HOST/partners` | **303** toward login (canonical origin dance) — not public partner JSON |
| Clear anonymous | `curl -sS -X POST $HOST/clear …` | **401** (expected under private-workspaces) |
| Tree fix | `bash scripts/prove_partner_health_local.sh` | **OK** — local private-workspaces returns `engine_default: adk` + partner fields |

Finding already filed: `docs/FINDING-hosted-health-partner-strip-2026-09-16.md`. Still RED on traffic.

---

## What `deploy.sh` does now (read before click)

Current `deploy.sh` (HEAD):

| Step | Action | Notes |
|------|--------|-------|
| 1 | Require Secret Manager secrets `parallel-api-key` + `agent-science-workspace-access` | No plaintext key files required on agent |
| 2 | Ensure runtime SA + bucket IAM | `agent-science-workspace@…` |
| 3 | Deploy **candidate tag** `--no-traffic --tag=workspace-candidate` | Does **not** auto-promote |
| 4 | `--timeout=240` | Prior orphan-works full script hit **504 @ 300s** — 240s is stricter; use compound-mini for video unless timeout raised |
| 5 | `--set-secrets` for Parallel + access config | No `--set-env-vars` for API keys |
| 6 | Prints `CANDIDATE_REVISION` + traffic JSON | Oscar promotes after verify |

**Not in deploy.sh:** public repo flip · Devpost · video · npm publish · automatic traffic split.

**Diff vs older deploy narratives:** this script is candidate-only (no live traffic flip). Promotion is a separate Oscar `gcloud run services update-traffic` (or console) step — confirm before assuming `/health` on the public URL changed.

---

## Pre-deploy (Oscar)

- [ ] Parallel + Gemini keys rotated if any revision ever had plaintext env (`AS-KEYS-ROTATE`)
- [ ] Secrets `parallel-api-key` and `agent-science-workspace-access` ENABLED versions exist
- [ ] `gcloud auth` + project `hack-fleet` (or `$GCP_PROJECT`)
- [ ] Review commits since last traffic: partner health restore in `cloud/case_http.py` + `cloud/partners.py`
- [ ] Decide timeout: keep 240 (safe) **or** raise if filming full orphan-works script

---

## Deploy + promote (Oscar clicks)

```bash
cd agent-science
bash deploy.sh
# → CANDIDATE_REVISION=…  (no traffic yet)

# Verify candidate URL (tag host), then promote THAT revision only:
# gcloud run services update-traffic agent-science --to-revisions=$REVISION=100 \
#   --region=us-central1 --project=hack-fleet
```

---

## Post-promote verify (run each)

```bash
HOST=https://agent-science-568004190078.us-central1.run.app

curl -sf "$HOST/health" | python3 -m json.tool
# expect: gemini, parallel, engine_default: adk, revision != 00028-hed stripped shape

curl -sf "$HOST/partners" | python3 -m json.tool
# expect: 200 JSON checklist — NOT 303 login

bash scripts/verify_partners_hosted.sh
# 4/4 partners when workspace token available for clear path

# Live compound only with WORKSPACE_TOKEN + keys:
# python3 scripts/compound_fresh_hosted_probe.py
```

**Do not claim:** full orphan-works script compound on hosted until Run A/B complete under the deployed timeout.

---

## Night-wave tree (safe; offline gates)

Shipped without requiring deploy:

- `scripts/eval_cost_from_billing.py` + `fixtures/price-cards/parallel-search-2026-09-18.md`
- `tests/test_cost_from_billing.py`
- SUBMISSION-PACK / BLOCKED / receipt docs

Deploy is required to clear the **live** partner-admissibility RED, not to land the cost gate.
