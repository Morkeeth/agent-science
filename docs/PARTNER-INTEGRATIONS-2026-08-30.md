# PARTNER INTEGRATIONS — Agent Science · Sep 9 path

**Date:** 2026-08-30 · **Last verified:** 2026-09-15 · **Repo:** Morkeeth/agent-science · **Scope:** all four partners wired in code; deploy is Oscar's click.

Each partner must be **called at runtime** on the default path — not documented only.

**Hosted shape (2026-09-15):** Cloud Run serves **private workspaces**. Public track proof is `GET /health` + `GET /partners`. Legacy public `POST /clear` / `POST /search` stay closed (401). Local desk still exposes `/clear` with ADK default. Live Parallel on hosted runs through authenticated workspace research (`POST /api/cases` with `live=true`).

---

## Oscar deploy checklist (one pass)

1. **Rotate keys** if any revision ever had plaintext env vars (`deploy.sh` note).
2. **`bash deploy.sh`** — Oscar only; writes Secret Manager, IAM, Cloud Run candidate revision (no traffic until promote).
3. **Verify partner surfaces (no workspace key):**
   ```bash
   bash scripts/verify_partners_hosted.sh
   ```
   Expect: `/health` has `mode: private-workspaces`, `engine_default: adk`, `parallel_sdk: true`, `gemini_path` starts with `vertex:` · `/partners` checklist all true · public `/clear` closed.
4. **Optional live Parallel on hosted** (workspace key):
   ```bash
   export AGENT_SCIENCE_WORKSPACE_TOKEN='…'   # never put in a URL
   bash scripts/verify_partners_hosted.sh
   ```
5. **Local ADK clearance proof** (no deploy):
   ```bash
   export PORT=8099 AGENT_BUILDER=1 GCP_PROJECT=hack-fleet PARALLEL_API_KEY="$(cat ~/.config/keys/parallel.key)"
   python3 cloud/service.py &
   curl -s localhost:8099/health | python3 -m json.tool
   ```
6. **Or verify /health alone after promote:**
   ```bash
   curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
   ```

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

**Local without API key (Vertex ADC):**
```bash
export GCP_PROJECT=hack-fleet GEMINI_MODEL=gemini-3.5-flash GOOGLE_CLOUD_LOCATION=global
env -u GEMINI_API_KEY -u GOOGLE_API_KEY python3 agent_science.py fixtures/scripts/split-sentence.txt
```

**Health field:** `"gemini_path": "vertex:<project>"` or `"api-key"` (on Cloud Run without project env: `vertex:adc`).

**Constraint:** model output goes to `clearance/verify.py` only — never directly to a verdict.

---

## 2 · Parallel — source discovery

| Field | Value |
|-------|-------|
| **Role** | Find candidate source URLs when a claim/case needs discovery |
| **SDK entrypoint** | `clearance/search.py` — `find_sources()` |
| **SDK package** | `parallel-web==1.3.2` (`requirements.txt`, Docker image) — primary transport |
| **Fallback** | Same REST endpoint via urllib if SDK import fails (cold clone without pip) |
| **Called from** | Local: `clearance/facts.py` → `agent_science.py` on live `/clear`. Hosted: `cloud/case_worker.py` → `cases.create/refresh` with `live=true` |
| **Env vars** | `PARALLEL_API_KEY` (injected from Secret Manager on Cloud Run) |
| **Secret Manager name** | `parallel-api-key` (override: `PARALLEL_SECRET` in `deploy.sh`) |
| **Local key path** | `~/.config/keys/parallel.key` (0600) |

**Deploy wiring (`deploy.sh`):**
```bash
--set-secrets="PARALLEL_API_KEY=${SECRET}:latest"
```

**curl (live API — requires key):**
```bash
curl -s -X POST https://api.parallel.ai/v1/search \
  -H "Content-Type: application/json" \
  -H "x-api-key: $(cat ~/.config/keys/parallel.key)" \
  -d '{"objective":"Find primary source for EU Orphan Works Directive 2012/28/EU","search_queries":["Directive 2012/28/EU","orphan works directive"],"mode":"advanced"}'
```

**Offline:** `cache/searches.json` — seeded by `python3 scripts/seed_document_cache.py`.

**Receipts:** `cache/search_receipts.jsonl` — each live call logs `search_id` when returned.

**Meter:** `clearance/search.py` `LIVE_CALLS` — single increment in `_live_search()` (SDK or REST).

**Judge manifest:** `GET /partners` — full track checklist + module map (public on hosted).

**Live probe:** `python3 scripts/partner_probe.py` → `docs/RECEIPT-partner-probe-*.md`

---

## 3 · Google Cloud — Cloud Run private workspaces

| Field | Value |
|-------|-------|
| **Role** | Hosted private research workspaces — auth required for cases |
| **Entrypoint** | `cloud/service.py` → `cloud/case_http.py` when `AGENT_SCIENCE_HOSTED=1` or `K_SERVICE` |
| **Deploy script** | `deploy.sh` (Oscar only — never run from agent) |
| **Project / region** | `hack-fleet` / `us-central1` (env: `GCP_PROJECT`, `GCP_REGION`) |
| **Service name** | `agent-science` (`GCP_SERVICE`) |
| **Workspace shelf** | GCS bucket via `AGENT_SCIENCE_WORKSPACE_BUCKET` |
| **Access secret** | Secret Manager `agent-science-workspace-access` → `AGENT_SCIENCE_ACCESS_CONFIG` |

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
  "last_parallel_search_id": null,
  "agent_builder": true,
  "adk_version": "2.7.1",
  "engine_default": "adk"
}
```

| Field | Meaning |
|-------|---------|
| `mode` | `private-workspaces` on Cloud Run; `local-desk` on `python3 cloud/service.py` |
| `gemini_path` | `vertex:<project>`, `vertex:adc`, `api-key`, or `none` |
| `parallel` | `PARALLEL_API_KEY` present in env |
| `agent_builder` | `google-adk` importable |
| `engine_default` | What local `POST /clear` will use: `adk` or `direct` |

### Routes

| Method | Path | Auth | Response |
|--------|------|------|----------|
| GET | `/health` | none | Partner JSON above |
| GET | `/partners` | none | Track manifest — all four partners + checklist |
| GET | `/login` | none | Workspace login form |
| GET/POST | `/cases`, `/api/cases` | workspace bearer/session | Private research |
| POST | `/clear`, `/search` | **closed on hosted** | 401 — use local desk or CLI |

**Local desk:**
```bash
export PORT=8099 AGENT_BUILDER=1 GCP_PROJECT=hack-fleet
python3 cloud/service.py
curl -s localhost:8099/health
```

---

## 4 · Agent Builder / ADK — default `/clear` engine

| Field | Value |
|-------|-------|
| **Role** | ADK agent decides to call `clear_script_tool`; report lifted from tool response |
| **SDK entrypoint** | `cloud/agent.py` — `run_clearance()`, `build_agent()` |
| **Wired in** | `cloud/service.py` `_run_clearance()` — default when `AGENT_BUILDER≠0` |
| **Package** | `google-adk==2.7.1` (`requirements.txt`, Dockerfile `AGENT_BUILDER=1`) |
| **Env vars** | `AGENT_BUILDER=1` (disable: `0`/`false`), plus Vertex vars above |
| **Secret Manager** | None — uses same ADC as Vertex |

**Receipt:** `docs/RECEIPT-adk-default-path-2026-08-30.md` · hosted surface restore `docs/RECEIPT-partner-hosted-admissibility-2026-09-15.md` · night wave `docs/RECEIPT-partner-integrations-night-2026-09-15.md`

**Controls:** `python3 tests/test_adk_default_path.py` — engine selection without live model.  
**Hosted regression control:** `python3 tests/test_partner_runtime.py` → `t_hosted_workspace_exposes_partner_health`.

**Gap report fields when ADK runs:** `engine: "adk"`, `adk_version`, `adk_tool_calls`, `model_routing`.

**Fallback:** if ADK raises, direct pipeline runs with `engine: "direct"` and `adk_error` — never silent.

---

## Stranger cold clone (no keys)

```bash
git clone https://github.com/Morkeeth/agent-science.git && cd agent-science
bash scripts/verify_cold_clone.sh
```

Receipts: `docs/RECEIPT-hosted-partner-runtime-2026-08-30.md`, `docs/RECEIPT-live-compound-exhibit-2026-08-30.md`, `docs/RECEIPT-partner-hosted-admissibility-2026-09-15.md`, `docs/RECEIPT-partner-integrations-night-2026-09-15.md`.

Live partner RED watcher (expect exit 2 until Oscar redeploy):

```bash
python3 scripts/watch_partner_health_object.py
```
