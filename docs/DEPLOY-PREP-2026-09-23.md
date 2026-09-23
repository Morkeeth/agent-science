# Deploy prep — slice 1 (Oscar only) · refreshed 2026-09-23

**Script:** `deploy.sh` · **Do not run from cloud agent**

Pre-flight only. Deploy flips a live revision and touches Secret Manager — Oscar's click.

---

## Why deploy is needed now (measured)

Live revision **`agent-science-00028-hed`** still serves stripped `/health`:

```bash
curl -sS https://agent-science-568004190078.us-central1.run.app/health
# {"ok": true, "service": "agent-science", "mode": "private-workspaces",
#  "revision": "agent-science-00028-hed"}
# missing: gemini / parallel / engine_default
```

Tree already has the partner-admissibility restore (2026-09-16). Until Oscar deploys, `verify_partners_hosted.sh` stays RED on health partner fields. Finding: `docs/FINDING-hosted-health-partner-strip-2026-09-16.md`.

---

## What `deploy.sh` does (read before click)

| Step | Action | Secret surface |
|------|--------|----------------|
| 1 | Enable GCP APIs | none |
| 2 | Parallel key → Secret Manager from `~/.config/keys/parallel.key` | **Rotate first if any old revision had plaintext env** |
| 3 | Corpus bucket + optional seed from `cache/*.db` | GCS IAM on runtime SA |
| 4 | **`--clear-env-vars`** then deploy with `--set-secrets` only | Removes plaintext GEMINI/PARALLEL from prior revisions |
| 4b | Env: Vertex ADC (no Gemini key in clear), GCS corpus URIs, `AGENT_BUILDER=1` | |
| 5 | Post-deploy `curl …/health` | |

**Not in deploy.sh:** Devpost · video upload · npm publish · public-repo flip (already public since 2026-08-22).

---

## `deploy.sh` surface (this tree)

```bash
wc -l deploy.sh                    # 45
bash -n deploy.sh                  # syntax OK — run before click
git log -5 --oneline -- deploy.sh
```

Hard requirements inside the script (do not weaken):

- Reads Parallel key from `~/.config/keys/parallel.key` into Secret Manager
- Uses `--clear-env-vars` before `--set-secrets`
- Does **not** pass `--set-env-vars` with API key values

---

## Pre-deploy (Oscar)

- [ ] Parallel + Gemini keys rotated if any revision ever had plaintext env (`AS-KEYS-ROTATE`)
- [ ] `~/.config/keys/parallel.key` present locally (rotated value)
- [ ] `gcloud auth` + project `hack-fleet` (or `$GCP_PROJECT`)
- [ ] Optional: `python3 scripts/boot_registry.py` then seed GCS from `cache/refusal_log.db` (**238** claims remeasured 2026-09-23 after boot)
- [ ] Review: `git log --oneline -8` on `main` after merging this night wave
- [ ] Local prove still green: `bash scripts/prove_partner_health_local.sh`

Local agent prep (no deploy):

```bash
bash scripts/deploy_prep.sh
# partner_runtime expect 7/7 (was wrongly labelled 5/5 before 2026-09-23)
```

---

## Deploy command

```bash
cd agent-science   # local clone with rotated key file
bash deploy.sh
```

Expected tail: `HOSTED_URL=https://agent-science-….run.app` + health JSON including partner fields.

---

## Post-deploy verify (run each)

```bash
HOST=https://agent-science-568004190078.us-central1.run.app

curl -sf "$HOST/health" | python3 -m json.tool
# must show engine_default: adk AND gemini/parallel truthiness — not stripped

bash scripts/verify_partners_hosted.sh
# 4/4 partners + Parallel proof

bash scripts/new_user_trial.sh "$HOST"

# Only with WORKSPACE_TOKEN + live keys:
python3 scripts/compound_fresh_hosted_probe.py
```

**Do not claim:** full orphan-works script compound on hosted until Run A/B complete under timeout (prior **504** @ 300s).

---

## Diff notes (2026-09-23 night wave vs live)

Night wave ships **offline eval + pack truth + deploy docs**. Runtime partner-health fix is already on `main` from 2026-09-16 and still needs Oscar `deploy.sh` to move traffic off `00028-hed`.

Related:

- `docs/RECEIPT-night-wave-2026-09-23.md`
- `docs/BLOCKED-live-compound-2026-09-23.md`
- `docs/FINDING-hosted-health-partner-strip-2026-09-16.md`
