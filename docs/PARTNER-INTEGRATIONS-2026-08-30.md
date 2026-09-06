# PARTNER INTEGRATIONS — Agent Science · Sep 9 path

**Date:** 2026-08-30 · **Last verified:** 2026-09-06 · **Repo:** Morkeeth/agent-science  
**Scope:** all four partners wired in code; deploy is Oscar's click.

Each partner must be **called at runtime** on its path — not documented only.

**2026-09-06 finding:** live revision `agent-science-00026-zel` returned liveness-only `/health` and redirected `/partners` to login. That is a partner-gate false green. Fix is in tree; live stays RED until Oscar deploys. See `docs/FINDING-hosted-partner-surface-2026-09-06.md`.

---

## Oscar deploy checklist (one pass)

1. **Rotate keys** if any revision ever had plaintext env vars (`deploy.sh` note).
2. **`bash deploy.sh`** — Oscar only; writes Secret Manager, IAM, Cloud Run revision (private workspaces).
3. **Verify partner surface on hosted (one command):**
   ```bash
   bash scripts/verify_partners_hosted.sh
   ```
   Expect: `/health` carries `gemini`, `parallel`, `engine_default`; `/partners` HTTP 200 JSON; `POST /clear` not public (401/303).
4. **Prove the fix beats naive liveness:**
   ```bash
   python3 scripts/eval_hosted_partner_surface.py
   ```
   Expect after deploy: live `shipping_pass=True`.
5. **Local clearance desk (ADK + Parallel on `/clear`)** — separate from hosted workspaces:
   ```bash
   env -u AGENT_SCIENCE_HOSTED -u K_SERVICE PORT=8099 AGENT_BUILDER=1 GCP_PROJECT=hack-fleet \
     python3 cloud/service.py
   curl -s localhost:8099/health | python3 -m json.tool
   # expect engine_default: adk when google-adk is installed
   ```
6. **Compound film beat** — local desk with keys, or offline receipt. Hosted unauthenticated `/clear` is intentionally gone.

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

**Health field:** `"gemini_path": "vertex:<project>"` or `"api-key"` or `"none"`.

**Constraint:** model output goes to `clearance/verify.py` only — never directly to a verdict.

---

## 2 · Parallel — source discovery

| Field | Value |
|-------|-------|
| **Role** | Find candidate source URLs when a claim has no `source_url` |
| **SDK entrypoint** | `clearance/search.py` — `find_sources()` |
| **SDK package** | `parallel-web==1.3.2` (`requirements.txt`, Docker image) — primary transport |
| **Fallback** | Same REST endpoint via urllib if SDK import fails (cold clone without pip) |
| **Called from (hosted)** | `clearance/cases.py` → `find_sources` via `cloud/case_worker.py` |
| **Called from (local desk)** | `clearance/facts.py` → `agent_science.py` on every live `/clear` |
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

**Judge manifest:** `GET /partners` — full track checklist + module map (public on hosted after this branch deploys).

---

## 3 · Google Cloud — Cloud Run desk / workspaces

| Field | Value |
|-------|-------|
| **Role** | Hosted private research workspaces; local clearance desk remains in-repo |
| **Entrypoint** | `cloud/service.py` (Dockerfile `CMD`) → `WorkspaceHTTP` when `AGENT_SCIENCE_HOSTED=1` or `K_SERVICE` |
| **Deploy script** | `deploy.sh` (Oscar only — never run from agent) |
| **Project / region** | `hack-fleet` / `us-central1` |
| **Service name** | `agent-science` |
| **Workspace store** | GCS bucket via `AGENT_SCIENCE_WORKSPACE_BUCKET` |

### `/health` spec (hosted private-workspaces, after this branch)

```json
{
  "ok": true,
  "service": "agent-science",
  "mode": "private-workspaces",
  "gemini": true,
  "gemini_path": "vertex:hack-fleet",
  "parallel": true,
  "parallel_sdk": true,
  "engine_default": "adk",
  "clearance_desk": "local-only",
  "hosted_parallel_path": "clearance/cases.py → find_sources",
  "revision": "…"
}
```

Bare `{ok, service, mode, revision}` is a **failed** partner gate.

### Routes

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/health` | public | Partner wiring + liveness |
| GET | `/partners` | public | Track manifest |
| GET/POST | `/cases`, `/api/cases` | workspace token | Private research |
| POST | `/clear`, `/search`, `/ingest` | **local desk only** | Not on hosted |

**Local desk:**
```bash
export PORT=8099 AGENT_BUILDER=1 GCP_PROJECT=hack-fleet
env -u AGENT_SCIENCE_HOSTED -u K_SERVICE python3 cloud/service.py
curl -s localhost:8099/health
curl -s localhost:8099/partners
```

---

## 4 · Agent Builder / ADK — default `/clear` engine (local desk)

| Field | Value |
|-------|-------|
| **Role** | ADK agent decides to call `clear_script_tool`; report lifted from tool response |
| **SDK entrypoint** | `cloud/agent.py` — `run_clearance()`, `build_agent()` |
| **Wired in** | `cloud/service.py` `_run_clearance()` — default when `AGENT_BUILDER≠0` |
| **Package** | `google-adk==2.7.1` (`requirements.txt`) |
| **Env vars** | `AGENT_BUILDER=1` (disable: `0`/`false`), plus Vertex vars above |
| **Hosted note** | Cloud Run serves private workspaces; ADK `/clear` is the **local desk** default path |

**Receipt:** `docs/RECEIPT-adk-default-path-2026-08-30.md`

**Controls:** `python3 tests/test_adk_default_path.py` — engine selection without live model.

**Fallback:** if ADK raises, direct pipeline runs with `engine: "direct"` and `adk_error` — never silent.

---

## Stranger cold clone (no keys)

```bash
git clone https://github.com/Morkeeth/agent-science.git && cd agent-science
bash scripts/verify_cold_clone.sh
bash scripts/verify_partners_hosted.sh --local
python3 scripts/eval_hosted_partner_surface.py
```

Live `/clear` on the public URL is not the Sep 9 path anymore. Partner **wiring** is public on `/health` + `/partners` after Oscar deploys this branch.
