# DEPLOY PREP — slice 1 desk · Oscar only · 2026-08-30

**Outward act:** `bash deploy.sh` is Oscar's click. This doc is prep only — no deploy run from agents.

**Current hosted (probed 2026-08-30):**

| URL | health |
|-----|--------|
| https://agent-science-568004190078.us-central1.run.app | `engine_default: adk`, gemini+parallel true |
| https://agent-science-33kamss2jq-uc.a.run.app | same shape (alias) |

---

## deploy.sh checklist (read before click)

### Secret handling (constitution)

- [ ] **No plaintext keys in `--set-env-vars`.** Script clears env vars on existing service before deploy (`--clear-env-vars`), then sets only non-secret config.
- [ ] **Parallel via Secret Manager only:** `--set-secrets="PARALLEL_API_KEY=${SECRET}:latest"`.
- [ ] **Gemini via Vertex ADC** on Cloud Run SA — no `GEMINI_API_KEY` in deploy surface.
- [ ] **Rotate** Parallel/Gemini if they were ever in plaintext env on a prior revision (script prints NOTE).

### Pre-flight (Oscar)

```bash
# 1. Parallel key file present
test -f "$HOME/.config/keys/parallel.key"

# 2. gcloud project + SA
gcloud config get-value project   # expect hack-fleet
gcloud auth list

# 3. Local controls green before shipping revision
python3 scripts/seed_document_cache.py
python3 tests/test_watch_it_go_red.py 2>&1 | tail -1
python3 tests/test_adk_default_path.py 2>&1 | tail -1

# 4. Diff deploy.sh against last deploy (no accidental env leak)
git diff HEAD -- deploy.sh
```

### deploy.sh steps (what the script does)

1. Enable Run, Cloud Build, Artifact Registry, Secret Manager, Storage, AI Platform.
2. Create/update Secret Manager secret `parallel-api-key` from `$HOME/.config/keys/parallel.key`.
3. Grant compute SA `secretAccessor` + `aiplatform.user`.
4. Create corpus bucket `gs://hack-fleet-agent-science-corpus` if missing; grant objectAdmin.
5. **If service exists:** `--clear-env-vars` first (removes leaked plaintext keys from prior revisions).
6. `gcloud run deploy agent-science --source .` with:
   - `GEMINI_MODEL`, `GCP_PROJECT`, `CORPUS_DB`, `CORPUS_GCS_URI`, `AGENT_BUILDER=1`, `GOOGLE_CLOUD_LOCATION=global`
   - `--set-secrets` for Parallel only
7. Print `HOSTED_URL` + curl `/health`.

### Post-deploy verify (Oscar)

```bash
URL="$(gcloud run services describe agent-science --region=us-central1 --format='value(status.url)')"
curl -s "$URL/health" | python3 -m json.tool
# expect: engine_default=adk, gemini=true, parallel=true

# Compound exhibit on hosted (receipt template in docs/RECEIPT-live-compound-exhibit-2026-08-30.md)
# POST /clear compound-mini A then B on fresh subject — B.parallel < A.parallel, B.corpus_hits >= 1
```

### Known gaps (do not hide)

- **Durable GCS corpus shelf** required for sealed prediction on orphan-works scripts (not compound-mini).
- **Local VM** has no keys — live compound only on hosted or Oscar machine with keys.
- **sourced=0** on live compound-mini runs — compounding metric passes; sourcing rate does not.

---

## Diff since last deploy note (2026-08-30)

Run at object:

```bash
git log -5 --oneline -- deploy.sh Dockerfile cloud/ requirements.txt
```

No agent deploy this night. Relevant runtime changes on `main` since slice 1 last probe:

- ADK default path (`engine_default: adk`) — verified hosted 2026-08-30
- `google-adk==2.7.1` in requirements.txt / Dockerfile
- Eval gates + holdout freeze (offline; no deploy surface change)
- Partner runtime wiring tests — 5/5

**Oscar action:** run `bash deploy.sh` only when ready to ship a new revision with current `main` + confirm secret rotation if needed.
