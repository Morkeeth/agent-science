# PARTNER INTEGRATIONS — Agent Science · Sep 9 path

**Date:** 2026-08-30 · **Last verified:** 2026-09-11 · **Repo:** Morkeeth/agent-science · **Scope:** all four partners wired in code; deploy is Oscar's click.

Each partner must be **called at runtime** on the default path — not documented only.

**2026-09-11 finding:** live Cloud Run rev `agent-science-00028-hed` served a stripped `/health` under `private-workspaces` (no `engine_default` / partner fields) and redirected `/partners` to login. That made STATUS and old receipts read green while `bash scripts/verify_partners_hosted.sh` went **RED**. Fix is in tree (`cloud/partners.health_payload` + public `/partners`); **Oscar must redeploy** for live to heal. See `docs/FINDING-hosted-partner-proof-dark-2026-09-11.md`.

---

## Oscar deploy checklist (one pass)

1. **Rotate keys** if any revision ever had plaintext env vars (`deploy.sh` note).
2. **`bash deploy.sh`** — Oscar only; writes Secret Manager, IAM, Cloud Run revision.
3. **Verify public partner surfaces (one command):**
   ```bash
   bash scripts/verify_partners_hosted.sh
   ```
   Expect after this branch is deployed: `/health` carries `gemini`, `parallel`, `agent_builder`, `engine_default` · `/partners` JSON (not login HTML).
   Under `mode: private-workspaces` without `AGENT_SCIENCE_WORKSPACE_TOKEN`, steps 3–5 (`/clear` + compound) report **BLOCKED** honestly — not false-green.
4. **Prove clear+Parallel with a workspace bearer (optional, Oscar):**
   ```bash
   AGENT_SCIENCE_WORKSPACE_TOKEN=<bearer> bash scripts/verify_partners_hosted.sh
   ```
5. **Local proof without deploy:**
   ```bash
   bash scripts/prove_partners_local.sh
   ```
   Expect: hosted-mode `/health` partner fields · `/partners` OK · anonymous `/clear` stays 401 · `engine_default: adk` when `google-adk` importable.
6. **Or verify /health alone (after deploy):**
   ```bash
   curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
   ```
   Expect: `"mode": "private-workspaces"` **and** `"engine_default": "adk"` (or `direct` with `agent_builder: false` named), `"gemini_path": "vertex:…"`, `"parallel": true`.
7. **Local desk `/clear` (not hosted):**
   ```bash
   # non-hosted local service — see Local desk below
   curl -s -X POST http://127.0.0.1:8099/clear \
     -H 'Content-Type: application/json' \
     -d '{"script":"The Dust Bowl displaced 2.5 million people.","subject":"dust-bowl"}' \
     | python3 -c "import sys,json; d=json.load(sys.stdin); print('engine',d.get('engine')); print('parallel_calls',d.get('parallel_calls'))"
   ```

---

## Hosted boundary (private-workspaces)

| Surface | Public? | Notes |
|---------|---------|-------|
| `GET /health` | **Yes** | Full partner admissibility fields (must not be a liveness stub) |
| `GET /partners` | **Yes** | Track checklist for judges |
| `POST /clear`, `/search`, `/ingest`, `/registry` | **No** | Local-only or workspace auth — AGENTS.md |
| `/cases`, `/api/cases` | Auth | Workspace bearer / session |

Do not claim hosted anonymous `/clear` compound after private-workspaces. Offline compound + local prove remain authoritative until a tokenized hosted clear is measured.

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
| **Role** | Hosted clearance desk — paste script, get gap report |
| **Entrypoint** | `cloud/service.py` (Dockerfile `CMD`) |
| **Deploy script** | `deploy.sh` (Oscar only — never run from agent) |
| **Project / region** | `hack-fleet` / `us-central1` (env: `GCP_PROJECT`, `GCP_REGION`) |
| **Service name** | `agent-science` (`GCP_SERVICE`) |
| **Corpus shelf** | GCS `gs://hack-fleet-agent-science-corpus/corpus.db` via `CORPUS_GCS_URI` |

### `/health` spec

Public under private-workspaces. Builder: `cloud/partners.health_payload()`.

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
  "last_parallel_search_id": "srch_…",
  "agent_builder": true,
  "adk_version": "2.7.1",
  "engine_default": "adk"
}
```

| Field | Meaning |
|-------|---------|
| `mode` | `private-workspaces` on Cloud Run hosted path |
| `gemini_path` | `vertex:<project>`, `api-key`, or `none` |
| `parallel` | `PARALLEL_API_KEY` present in env |
| `agent_builder` | `google-adk` importable |
| `engine_default` | What `/clear` will use when that route is available: `adk` or `direct` |

### Routes

| Method | Path | Auth | Response |
|--------|------|------|----------|
| GET | `/health` | public | JSON above |
| GET | `/partners` | public | Track manifest — all four partners + checklist |
| GET | `/` | login → `/cases` | Private workspace UI |
| POST | `/clear` | **local desk only** (hosted: gated) | Gap report JSON; `engine` field stamped |
| GET | `/corpus?subject=` | local desk | `{subject, remembered, total}` |
| GET/POST | `/cases`, `/api/cases` | workspace bearer | Private research |

**Local desk:**
```bash
export PORT=8099 AGENT_BUILDER=1 GCP_PROJECT=hack-fleet
# do NOT set AGENT_SCIENCE_HOSTED / K_SERVICE for the clearance desk
python3 cloud/service.py
curl -s localhost:8099/health
bash scripts/prove_partners_local.sh   # private-workspaces shape without deploy
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
bash scripts/prove_partners_local.sh
```

Receipts: `docs/RECEIPT-partner-hosted-proof-2026-09-11.md`, `docs/FINDING-hosted-partner-proof-dark-2026-09-11.md`.

Hosted `/clear` requires Oscar deploy + workspace token. Offline controls prove partner **code paths** and local private-workspaces health shape.
