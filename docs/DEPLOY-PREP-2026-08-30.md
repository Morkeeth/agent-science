# DEPLOY PREP — slice 1 desk · Oscar checklist · 2026-08-30

**Status:** PREP ONLY — this doc does not run `deploy.sh`. Outward deploy is Oscar's click.

**Current hosted revision (probed 2026-08-30):**

```bash
curl -s https://agent-science-568004190078.us-central1.run.app/health
```

```json
{
 "ok": true,
 "service": "agent-science",
 "gemini": true,
 "gemini_path": "vertex:hack-fleet",
 "parallel": true,
 "agent_builder": true,
 "adk_version": "2.7.1",
 "engine_default": "adk"
}
```

**Compound exhibit on hosted (re-derived 2026-08-30 night):** A=2 Parallel → B=1 Parallel, B corpus_hits=2 — `docs/RECEIPT-live-compound-exhibit-2026-08-30.md`.

---

## deploy.sh diff checklist (run before Oscar clicks deploy)

| Step | deploy.sh line | What it does | Pre-flight check |
|------|----------------|--------------|------------------|
| 1 | L21–25 | Enable GCP APIs | `gcloud services list --enabled --project=hack-fleet \| grep -E 'run|aiplatform|secretmanager'` |
| 2 | L27–38 | Parallel key → Secret Manager | `~/.config/keys/parallel.key` exists (0600); SA has `secretAccessor` |
| 3 | L40–45 | Corpus GCS bucket | `gs://hack-fleet-agent-science-corpus` exists; SA has `objectAdmin` |
| 4 | L50–54 | **Clear leaked env vars** | Prior `--set-env-vars` plaintext keys removed on update |
| 5 | L55–65 | Deploy with secrets | `--set-secrets=PARALLEL_API_KEY=parallel-api-key:latest` only; **no** plaintext API keys |
| 6 | L64 | Env vars set | `GEMINI_MODEL`, `GCP_PROJECT`, `CORPUS_GCS_URI`, `AGENT_BUILDER=1`, `GOOGLE_CLOUD_LOCATION=global` |
| 7 | L67–71 | Post-deploy probe | `curl -sf $URL/health` shows `engine_default: adk`, `parallel: true`, `gemini: true` |

---

## Constitution checks (must pass before deploy)

```bash
python3 scripts/seed_document_cache.py
python3 tests/test_watch_it_go_red.py          # 72/72
python3 tests/test_partner_runtime.py          # 5/5
python3 tests/test_adk_default_path.py       # 5/5
python3 scripts/bench_check_docs.py          # 109/109 match SUBMISSION-PACK
```

Secret scan (no plaintext keys in tree or recent git log):

```bash
git log --oneline -5 -- deploy.sh
grep -n 'set-env-vars.*API_KEY' deploy.sh || echo 'deploy.sh: no plaintext key env vars'
```

---

## Post-deploy verification (Oscar runs after deploy.sh)

1. **Health:** `curl -s $HOSTED_URL/health | jq .engine_default` → `"adk"`
2. **Compound:** POST `/clear` compound-mini A/B on fresh subject — B.parallel < A.parallel and B.corpus_hits ≥ 1
3. **Durable shelf:** second POST on same subject from different instance still shows corpus_hits ≥ 1 (GCS shelf)
4. **Seal prediction** in `docs/SUBMISSION-PACK-2026-08-29.md` after live A/B on `documentary-orphan-works*.txt`

---

## Known gaps (honest)

- **Local VM:** no Gemini/Parallel keys — live compound blocked locally; hosted proved.
- **RC5 substring false-GREEN:** both eval arms false-GREEN on held-out set — not a deploy blocker, documented engine limit.
- **sourced=0 on compound-mini hosted runs:** compounding metric passes; sourcing rate on live mini script does not.

---

## Do NOT (constitution)

- Flip repo public
- Devpost submit / video upload
- Run `deploy.sh` from an agent session without Oscar present
- Add `--set-env-vars` with plaintext API keys
