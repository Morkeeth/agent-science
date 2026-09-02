# DEPLOY PREP CHECKLIST — slice 1 (Oscar only)

**Date:** 2026-09-02 · **Script:** `deploy.sh` · **Do not run from agent**

This checklist is a diff review for Oscar before the next public deploy. No deploy was
executed in the night wave.

---

## Pre-flight (local)

- [ ] `python3 scripts/seed_document_cache.py && python3 tests/test_watch_it_go_red.py` → **72/72**
- [ ] `python3 scripts/bench_check_docs.py` → **127/127 match**
- [ ] `python3 scripts/freeze_holdout.py --check` → holdout intact
- [ ] Parallel key at `~/.config/keys/parallel.key` (never commit)
- [ ] `gcloud auth application-default login` for Vertex (Gemini uses ADC, not env key)

## deploy.sh review (what it does)

| Step | Action | Secret handling |
|------|--------|-----------------|
| 1 | Enable Cloud Run, Cloud Build, AR, Secret Manager, GCS, Vertex | — |
| 2 | Parallel key → Secret Manager via stdin | **Not** `--set-env-vars` |
| 3 | Corpus bucket `hack-fleet-agent-science-corpus` | SA gets `objectAdmin` |
| 3b | Seed `refusal_log.db` + `corpus.db` to GCS if local copies exist | — |
| 4 | `--clear-env-vars` then deploy with clean env | Removes leaked plaintext keys |
| 4 | `--set-secrets=PARALLEL_API_KEY=parallel-api-key:latest` | Parallel only via secret |
| 4 | `GEMINI_MODEL`, `GCP_PROJECT`, GCS URIs, `AGENT_BUILDER=1` | No API keys in clear |

## Post-deploy curls (from deploy.sh)

```bash
curl -sf "$HOSTED_URL/health"
curl -sf "$HOSTED_URL/stats" | head
curl -sf "$HOSTED_URL/popular" | head
curl -sf -X POST "$HOSTED_URL/clear" -H 'Content-Type: application/json' \
  -d '{"script":"Directive 2012/28/EU.","subject":"compound-prep"}' | head -c 400
```

## Post-deploy compound (Oscar)

```bash
bash scripts/long_run_goal.sh
```

Expect: A=1→B=0 Parallel, corpus_hits≥1 on fresh subject. Orphan-works full script Run B
may still timeout at 300s — see `docs/RECEIPT-live-compound-BLOCKED-2026-09-02.md`.

## Rotate before public repo

- [ ] Rotate Parallel key if ever in plaintext Cloud Run revision
- [ ] Rotate Gemini/Vertex credentials if ever in plaintext env
- [ ] Flip repo public only after rotation

## Outward acts (not in this checklist)

- Devpost submit · video upload · public repo flip — Oscar only
