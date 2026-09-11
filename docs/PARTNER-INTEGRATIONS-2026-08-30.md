# PARTNER INTEGRATIONS — Agent Science · Sep 9 path

**Date:** 2026-08-30 · **Last verified:** 2026-09-11 · **Repo:** Morkeeth/agent-science · **Scope:** all four partners wired in code; deploy is Oscar's click.

Each partner must be **called at runtime** on the default path — not documented only.

**2026-09-11 object check:** live revision `agent-science-00028-hed` stripped partner fields from `/health` after the private-workspaces cutover. Code on this branch restores public `/health` + `/partners`. Hosted stays red until Oscar redeploys — see `docs/FINDING-hosted-partner-health-regression-2026-09-11.md`.

---

## Oscar deploy checklist (one pass)

1. **Rotate keys** if any revision ever had plaintext env vars (`deploy.sh` note).
2. **`bash deploy.sh`** — Oscar only; writes Secret Manager, IAM, Cloud Run revision.
3. **Verify public partner surfaces (one command):**
   ```bash
   bash scripts/verify_partners_hosted.sh
   ```
   Expect: `/health` carries `gemini` · `parallel` · `parallel_sdk` · `agent_builder` · `engine_default: adk` · `/partners` HTTP 200 without auth · stranger-proof score 8/8 vs naive 1/8 · hosted `POST /clear` stays 401/404 (local-only).
4. **Baseline score (embarrassing arm included):**
   ```bash
   python3 scripts/eval_partner_health_baseline.py
   ```
5. **Local `/clear` ADK + Parallel proof** (keys required; not on hosted):
   ```bash
   VERIFY_LOCAL_CLEAR=1 bash scripts/verify_partners_hosted.sh
   # or local desk:
   export AGENT_BUILDER=1 PARALLEL_API_KEY=… GCP_PROJECT=hack-fleet
   python3 cloud/service.py   # then POST /clear on :8080
   ```
6. **Or verify /health alone after deploy:**
   ```bash
   curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
   ```
   Expect: `"gemini_path": "vertex:…"`, `"parallel": true`, `"engine_default": "adk"`, `"mode": "private-workspaces"`.

---

## Hosted vs local boundary

| Surface | Local desk (`python3 cloud/service.py`) | Hosted Cloud Run (`K_SERVICE`) |
|---------|------------------------------------------|--------------------------------|
| `GET /health` | full partner payload | full partner payload (public) |
| `GET /partners` | track manifest | track manifest (public) |
| `POST /clear` | ADK default + Parallel | **local-only** — 401 without workspace; do not demo on hosted URL |
| `GET/POST /search` | dictionary websearch | local-only |
| `/cases` | n/a | private research workspace (token) |

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

**Health field:** `"gemini_path": "vertex:<project>"` or `"api-key"`.

**Constraint:** model output goes to `clearance/verify.py` only — never directly to a verdict.

---

## 2 · Parallel — source discovery

| Field | Value |
|-------|-------|
| **Role** | Find candidate source URLs when a claim has no `source_url` |
| **SDK entrypoint** | `clearance/search.py` — `find_sources()` |
| **SDK package** | `parallel-web==1.3.2` (`requirements.txt`, Docker image) — primary transport |
| **Fallback** | Same REST endpoint via urllib if SDK import fails (cold clone without pip) |
| **Called from** | `clearance/facts.py` → `agent_science.py` on every live `/clear` |
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

**Judge manifest:** `GET /partners` — full track checklist + module map.

**Live probe:** `python3 scripts/partner_probe.py` → `docs/RECEIPT-partner-probe-*.md`

---

## 3 · Google Cloud — Cloud Run desk

| Field | Value |
|-------|-------|
| **Role** | Hosted private research workspaces + public partner proof surfaces |
| **Entrypoint** | `cloud/service.py` → `cloud/case_http.py` when `K_SERVICE` / `AGENT_SCIENCE_HOSTED=1` |
| **Deploy script** | `deploy.sh` (Oscar only — never run from agent) |
| **Project / region** | `hack-fleet` / `us-central1` (env: `GCP_PROJECT`, `GCP_REGION`) |
| **Service name** | `agent-science` (`GCP_SERVICE`) |
| **Corpus shelf** | GCS `gs://hack-fleet-agent-science-corpus/corpus.db` via `CORPUS_GCS_URI` |

### `/health` spec

```json
{
  "ok": true,
  "service": "agent-science",
  "mode": "private-workspaces",
  "gemini": true,
  "gemini_path": "vertex:hack-fleet",
  "parallel": true,
  "parallel_sdk": true,
  "parallel_sdk_version": "1.3.2",
  "parallel_transport": "parallel-web",
  "last_parallel_search_id": "srch_…",
  "agent_builder": true,
  "adk_version": "2.7.1",
  "engine_default": "adk",
  "revision": "agent-science-…"
}
```

| Field | Meaning |
|-------|---------|
| `gemini_path` | `vertex:<project>`, `api-key`, or `none` |
| `parallel` | `PARALLEL_API_KEY` present in env |
| `agent_builder` | `google-adk` importable |
| `engine_default` | What local `POST /clear` will use: `adk` or `direct` |
| `mode` | `private-workspaces` on hosted |

### Routes

| Method | Path | Hosted | Response |
|--------|------|--------|----------|
| GET | `/health` | public | JSON above |
| GET | `/partners` | public | Track manifest — all four partners + checklist |
| GET | `/cases` | token | Private research workspace |
| POST | `/clear` | **local desk only** | Gap report JSON; `engine` field stamped |

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
| **Package** | `google-adk==2.7.1` (`requirements.txt`) |
| **Env vars** | `AGENT_BUILDER=1` (disable: `0`/`false`), plus Vertex vars above |
| **Secret Manager** | None — uses same ADC as Vertex |

**Receipt:** `docs/RECEIPT-adk-default-path-2026-08-30.md`

**Controls:** `python3 tests/test_adk_default_path.py` — engine selection without live model.

**Gap report fields when ADK runs:** `engine: "adk"`, `adk_version`, `adk_tool_calls`, `model_routing`.

**Fallback:** if ADK raises, direct pipeline runs with `engine: "direct"` and `adk_error` — never silent.

---

## Stranger cold clone (no keys)

```bash
git clone https://github.com/Morkeeth/agent-science.git && cd agent-science
bash scripts/verify_cold_clone.sh
python3 scripts/eval_partner_health_baseline.py
```

Receipts: `docs/RECEIPT-partner-admissibility-2026-09-11.md`, `docs/FINDING-hosted-partner-health-regression-2026-09-11.md`.

Live hosted partner fields require Oscar deploy. Offline controls prove partner **code paths** exist and are tested.
