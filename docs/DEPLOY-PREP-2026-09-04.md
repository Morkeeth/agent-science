# Deploy prep — slice 1 (Oscar only) · 2026-09-04

**Script:** `deploy.sh` (89 lines) · **Do not run from cloud agent**

This is a pre-flight checklist. Deploy flips a live revision and touches Secret
Manager — Oscar's click only. Night-wave changes are docs + offline eval gates;
runtime Python for clearance is unchanged this slice.

---

## deploy.sh diff notes (read before click)

| Line | Setting | Risk |
|------|---------|------|
| 73 | `--timeout=300` | Full orphan-works script **504 @ 300s** (Run A and B). Raise to **600** (or 900) if filming full script. |
| 72 | `--memory=512Mi` | OK for compound-mini / fresh probe |
| 59–64 | `--clear-env-vars` before `--set-secrets` | Keeps plaintext GEMINI/PARALLEL out of new revision |
| 75 | Vertex ADC · no Gemini key in clear | Correct |
| 76 | `PARALLEL_API_KEY=${SECRET}:latest` | Requires rotated key in Secret Manager if any old revision leaked |

**Command to review script (no deploy):**

```bash
sed -n '58,76p' deploy.sh
# expect: clear-env-vars → deploy --timeout=300 → set-secrets Parallel only
```

**Not in deploy.sh:** public repo flip · Devpost · video · npm publish.

---

## Pre-deploy (Oscar)

- [ ] Parallel key rotated if any revision ever had `PARALLEL_API_KEY` in plaintext env (`hack.md` OPEN QUESTIONS)
- [ ] `~/.config/keys/parallel.key` present locally
- [ ] `gcloud auth` + project `hack-fleet` (or `$GCP_PROJECT`)
- [ ] Optional: raise `--timeout=600` in `deploy.sh` before click if orphan-works full script is needed for video
- [ ] Optional: `python3 scripts/boot_registry.py` + seed local `cache/refusal_log.db` for GCS upload
- [ ] Review: `git log --oneline -5` on `main`

---

## Deploy command

```bash
cd agent-science   # local clone with keys
bash deploy.sh
```

Expected tail: `HOSTED_URL=https://agent-science-….run.app` + health JSON snippet.

---

## Post-deploy verify (run each)

```bash
HOST=https://agent-science-568004190078.us-central1.run.app

curl -sf "$HOST/health" | python3 -m json.tool
# engine_default: adk

curl -sf "$HOST/stats" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['n'], d['dictionary_hit_rate'])"
# re-derive — do not carry STATUS figures forward without this

bash scripts/verify_partners_hosted.sh
# 4/4 partners

bash scripts/new_user_trial.sh "$HOST"
# lookup 2012/28/EU SOURCED free

python3 scripts/compound_fresh_hosted_probe.py
# prefer fresh subject — warm shelf may show A=0 Parallel
```

**Do not claim:** full orphan-works script compound on hosted until Run A/B complete under the new timeout (prior **504 @ 300s**).

---

## If deploy fails

1. Check Secret Manager version for `parallel-api-key`
2. Confirm runtime SA has `secretmanager.secretAccessor` + `aiplatform.user`
3. Re-run with only `--clear-env-vars` repair if an old plaintext env survived

---

*Oscar owns the click. Cloud agents stop at this checklist.*
