# PARTNER INTEGRATIONS — Agent Science · Sep 9 path

**Date:** 2026-08-30 · **Last verified:** 2026-09-07 · **Repo:** Morkeeth/agent-science  
**Scope:** all four partners wired in code; hosted is private-workspaces; deploy is Oscar's click.

Each partner must be **called at runtime** on the default path — not documented only.  
**Finding (2026-09-07):** live rev `00026-zel` stripped partner fields from `/health`. Fix is in code; hosted stays RED until Oscar redeploys. See `docs/FINDING-hosted-partner-health-stripped-2026-09-07.md`.

---

## Oscar deploy checklist (one pass)

1. **Rotate keys** if any revision ever had plaintext env vars (`deploy.sh` note).
2. **`bash deploy.sh`** — Oscar only; writes Secret Manager, IAM, Cloud Run **candidate** revision (no traffic until you promote).
3. **Verify public partner surfaces (no token):**
   ```bash
   bash scripts/verify_partners_hosted.sh
   ```
   Expect: health OK with `engine_default: adk`, `gemini_path` starting `vertex:`, `parallel: true`, `/partners` checklist true.  
   Exit **2** if `AGENT_SCIENCE_WORKSPACE_TOKEN` unset (public surfaces only). Exit **0** only after auth-gated clear + compound also pass.
4. **Runtime clear + compound (token required):**
   ```bash
   export AGENT_SCIENCE_WORKSPACE_TOKEN='<invite key from access secret — never in URL>'
   bash scripts/verify_partners_hosted.sh
   python3 scripts/compound_fresh_hosted_probe.py
   ```
5. **Or verify /health alone after promote:**
   ```bash
   curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
   ```
   Expect partner fields **and** `"mode": "private-workspaces"`.

---

## Hosted surface map (after this branch)

| Surface | Auth | Purpose |
|---------|------|---------|
| `GET /health` | public | Partner wiring + liveness |
| `GET /partners` | public | Judge track manifest |
| `POST /api/clear` | workspace bearer / session | Clearance with ADK + Parallel |
| `POST /api/cases` | workspace bearer / session | Research cases (also call Parallel when `live=true`) |
| `POST /clear`, `/search`, `/ingest` | **local desk only** | Unauthenticated legacy routes stay off Cloud Run |

---

## 1 · Gemini / Vertex — claim extraction & locate

| Field | Value |
|-------|-------|
| **Role** | Extract claims from script; propose passages in fetched documents |
| **SDK entrypoint** | `clearance/gemini.py` — `GeminiExtractor`, `GeminiLocator` |
| **Also used by** | `clearance/extract.py`, `cloud/agent.py` (ADK model client) |
| **Env vars** | `GEMINI_MODEL` (default `gemini-3.5-flash-lite`), `GCP_PROJECT` / `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION=global` |
| **Secret Manager** | **None on deploy** — Vertex via Application Default Credentials (Cloud Run SA) |
| **Plaintext key** | `GEMINI_API_KEY` / `GOOGLE_API_KEY` only for local dev without ADC |

**Health field:** `"gemini_path": "vertex:<project>"` or `"api-key"`.

**Constraint:** model output goes to `clearance/verify.py` only — never directly to a verdict.

---

## 2 · Parallel — source discovery

| Field | Value |
|-------|-------|
| **Role** | Find candidate source URLs when a claim has no `source_url` |
| **SDK entrypoint** | `clearance/search.py` — `find_sources()` |
| **SDK package** | `parallel-web==1.3.2` (`requirements.txt`, Docker image) |
| **Called from** | `clearance/facts.py` → live `/api/clear`; `clearance/cases.py` live investigate |
| **Env vars** | `PARALLEL_API_KEY` (Secret Manager on Cloud Run) |
| **Secret Manager name** | `parallel-api-key` (override: `PARALLEL_SECRET` in `deploy.sh`) |

**Deploy wiring (`deploy.sh`):**
```bash
--set-secrets="PARALLEL_API_KEY=${SECRET}:latest,…"
```

**Offline:** `cache/searches.json` — seeded by `python3 scripts/seed_document_cache.py`.  
**Receipts:** `cache/search_receipts.jsonl` — durable `search_id` for cold-start proof on `/partners`.

---

## 3 · Google Cloud — Cloud Run desk

| Field | Value |
|-------|-------|
| **Role** | Hosted private workspaces + public partner surfaces |
| **Entrypoint** | `cloud/service.py` → `cloud/case_http.py` when hosted |
| **Deploy script** | `deploy.sh` (Oscar only — never run from agent) |
| **Project / region** | `hack-fleet` / `us-central1` |
| **Non-secret env on deploy** | `AGENT_BUILDER=1`, `GCP_PROJECT`, `GOOGLE_CLOUD_LOCATION=global` |

### `/health` spec (public)

```json
{
  "ok": true,
  "service": "agent-science",
  "mode": "private-workspaces",
  "revision": "agent-science-…",
  "gemini": true,
  "gemini_path": "vertex:hack-fleet",
  "parallel": true,
  "parallel_sdk": true,
  "parallel_sdk_version": "1.3.2",
  "parallel_transport": "parallel-web",
  "agent_builder": true,
  "adk_version": "2.7.1",
  "engine_default": "adk"
}
```

---

## 4 · Agent Builder / ADK — default clearance engine

| Field | Value |
|-------|-------|
| **Role** | Default engine for clearance |
| **Module** | `cloud/agent.py` — `run_clearance` |
| **Package** | `google-adk` (pinned in `requirements.txt`) |
| **Default** | `AGENT_BUILDER=1` → `engine_default: adk` |
| **Hosted call** | `POST /api/clear` with workspace bearer + `request_id` |

```bash
curl -s -X POST "$BASE/api/clear" \
  -H "Authorization: Bearer $AGENT_SCIENCE_WORKSPACE_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"request_id":"clear-demo-0000000001","script":"The Dust Bowl displaced 2.5 million people.","subject":"dust-bowl"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print('engine',d.get('engine')); print('parallel_calls',d.get('parallel_calls'))"
```

Local desk (no hosted flag) still uses unauthenticated `POST /clear`.

---

## Controls

```bash
python3 tests/test_partner_runtime.py       # 10/10
python3 tests/test_parallel_integration.py  # 6/6
python3 tests/test_adk_default_path.py      # 5/5
python3 -m unittest tests.test_hosted_flow  # public health + auth clear
bash scripts/verify_partners_hosted.sh      # live URL — RED until redeploy
```
