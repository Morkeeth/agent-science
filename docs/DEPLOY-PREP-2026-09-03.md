# Deploy prep — slice 1 (Oscar only)

**Date:** 2026-09-03 · **Script:** `deploy.sh` · **Do not run from cloud agent**

This is a pre-flight checklist. Deploy flips a live revision and touches Secret Manager — Oscar's click only.

---

## What deploy.sh does (read before click)

| Step | Action | Secret surface |
|------|--------|----------------|
| 1 | Enable GCP APIs | none |
| 2 | Parallel key → Secret Manager from `~/.config/keys/parallel.key` | **Oscar must have rotated key if ever leaked in env** |
| 3 | Corpus bucket + optional seed from `cache/*.db` | GCS IAM on runtime SA |
| 4 | **`--clear-env-vars`** then deploy with `--set-secrets` only | Removes plaintext GEMINI/PARALLEL from prior revisions |
| 4b | Env: Vertex ADC (no Gemini key in clear), GCS corpus URIs, `AGENT_BUILDER=1` | |
| 5 | Post-deploy `curl …/health` | |

**Not in deploy.sh:** public repo flip · Devpost · video · npm publish.

---

## Pre-deploy (Oscar)

- [ ] Parallel key rotated if any revision ever had `PARALLEL_API_KEY` in plaintext env (`hack.md` OPEN QUESTIONS)
- [ ] `~/.config/keys/parallel.key` present locally
- [ ] `gcloud auth` + project `hack-fleet` (or `$GCP_PROJECT`)
- [ ] Optional: `python3 scripts/boot_registry.py` + seed local `cache/refusal_log.db` for GCS upload
- [ ] Review diff since last deploy: `git log --oneline -5` on `main`

---

## Deploy command

```bash
cd agent-science   # local clone
bash deploy.sh
```

Expected tail: `HOSTED_URL=https://agent-science-….run.app` + health JSON snippet.

---

## Post-deploy verify (run each)

```bash
HOST=https://agent-science-568004190078.us-central1.run.app

curl -sf "$HOST/health" | python3 -m json.tool
# engine_default: adk

bash scripts/verify_partners_hosted.sh
# 4/4 partners

bash scripts/new_user_trial.sh "$HOST"
# lookup 2012/28/EU SOURCED free

python3 scripts/compound_hosted_probe.py
# compound-mini or fresh subject — warm shelf may show A=0 Parallel
```

**Do not claim:** full orphan-works script compound on hosted until Run B completes under 300s (prior **504**).

---

## Diff notes (2026-09-03 vs last known rev 00018)

Night wave changes are **docs + offline eval gates only** — no runtime Python changes to clearance pipeline in this slice. Deploy is optional for submit path unless Oscar needs hosted refresh for video.

Files touched this wave (safe to deploy as-is):

- `scripts/eval_verify_holdout.py`, `eval_scorer_symmetry.py`, `freeze_holdout.py`
- `fixtures/refusal-correctness/MANIFEST.json`
- `scripts/verify_cold_clone.sh`, `full_gate.sh`
- `docs/SUBMISSION-PACK-2026-08-29.md`, receipts

---

## If deploy fails

| Symptom | Check |
|---------|-------|
| Secret access denied | Runtime SA has `secretAccessor` on `parallel-api-key` |
| Vertex 403 | SA has `roles/aiplatform.user` |
| 504 on `/clear` | Reduce script size for video; use compound-mini subject |
| Stale dictionary | Re-seed GCS `refusal_log.db` from local cache |
