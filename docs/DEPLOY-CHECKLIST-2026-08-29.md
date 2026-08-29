# DEPLOY CHECKLIST — slice 1 (Oscar only)

**Date:** 2026-08-29 · **Script:** `deploy.sh` · **Do not run from agent runs**

This is prep only. Deploy flips a public URL and touches Secret Manager — constitution
reserves that to Oscar.

---

## What `deploy.sh` does (read at object, not from memory)

| Step | Action | Secret / risk |
|------|--------|---------------|
| 1 | Enables Run, Cloud Build, Artifact Registry, Secret Manager, Storage, Vertex | none |
| 2 | Creates/updates Parallel key in Secret Manager from `$HOME/.config/keys/parallel.key` | **Oscar stdin/file only** |
| 3 | Creates GCS bucket `hack-fleet-agent-science-corpus` + IAM for runtime SA | corpus shelf |
| 4 | **`--clear-env-vars`** on existing service, then deploy with `--set-env-vars` (no plaintext keys) + `--set-secrets` for Parallel | removes leaked plaintext from prior revisions |
| 5 | Prints `HOSTED_URL` + curls `/health` | smoke test |

**Gemini:** no key in deploy — Vertex ADC via Cloud Run service account (`roles/aiplatform.user`).

**Env vars set on deploy:**
```
GEMINI_MODEL=gemini-3.5-flash
GCP_PROJECT=hack-fleet
CORPUS_DB=/tmp/corpus.db
CORPUS_GCS_URI=gs://hack-fleet-agent-science-corpus/corpus.db
AGENT_BUILDER=1
GOOGLE_CLOUD_LOCATION=global
```

**Secrets:** `PARALLEL_API_KEY=parallel-api-key:latest`

---

## Pre-deploy diff Oscar should eyeball

```bash
git diff main -- deploy.sh cloud/service.py cloud/agent.py agent_science.py
```

Nothing in tonight's branch touches `deploy.sh` (constitution). Hosted behaviour changes
only after Oscar runs the script on `main` + slice-1 branch.

---

## Post-deploy verification (Oscar runs)

```bash
URL=$(gcloud run services describe agent-science --region=us-central1 \
  --format='value(status.url)')
curl -sf "$URL/health"
curl -sf -X POST "$URL/clear" -H 'Content-Type: application/json' \
  -d '{"subject":"orphan-works","script":"'"$(head -5 fixtures/scripts/documentary-orphan-works.txt)"'"}' \
  | head -c 400
```

**Sealed prediction gate** (`docs/SUBMISSION-PACK-2026-08-29.md`): Run A then Run B on
`documentary-orphan-works*.txt` with shared GCS shelf — B must show `corpus_hits ≥ 1`
and `parallel_calls` strictly less than A.

---

## Blockers on this VM (2026-08-29)

| Item | Status |
|------|--------|
| Gemini key / ADC | not available in agent VM |
| Parallel key | not in env; `$HOME/.config/keys/parallel.key` absent |
| Live compound exhibit | **BLOCKED** — see `docs/COMPOUND-EXHIBIT-2026-08-29.md` offline receipt |
| Public repo flip | Oscar only |
| Devpost / video | Oscar only |

---

## Key rotation note

`deploy.sh` line 72: if Parallel or Gemini keys were ever in plaintext `--set-env-vars`,
rotate after first clean deploy. The script clears env vars before each deploy specifically
to close that wound.
