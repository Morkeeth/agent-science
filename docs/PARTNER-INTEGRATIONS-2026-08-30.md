# PARTNER INTEGRATIONS — Agent Science · Sep 9 path

**Date:** 2026-08-30 · **Last verified:** 2026-09-18 · **Repo:** Morkeeth/agent-science · **Scope:** all four partners wired in code; deploy is Oscar's click.

Each partner must be **called at runtime** on the default path — not documented only.

### Hosted mode (private-workspaces) — measured 2026-09-18

Cloud Run sets `K_SERVICE`, so all traffic goes through `cloud/case_http.py` WorkspaceHTTP.

| Route | Auth | Role |
|-------|------|------|
| `GET /health` | **public** | Partner proof JSON (`gemini`, `parallel`, `engine_default`, …) + `mode` + `revision` |
| `GET /partners` | **public** | Track checklist JSON for judges (`parallel_search_at_runtime` = key present, not a constant) |
| `GET /truths/ui` · `/visibility[/ui]` · `/popular[/ui]` | **public** | Film / judge read-only; `live` defaults false |
| `POST /clear`, `/search`, `/ingest`, `/registry` | **workspace / local-only** | Mutations and shared history stay shut |
| `/cases`, `/api/cases` | **workspace** | Private research |

**Findings (live still RED until Oscar deploy):**

- Revision `agent-science-00028-hed` stripped `/health` — `docs/FINDING-hosted-health-partner-strip-2026-09-16.md`
- `/partners` checklist hardcoded `parallel_search_at_runtime: true` — `docs/FINDING-partners-checklist-hardcoded-2026-09-18.md`
- Film surfaces unmounted (303/404) — `docs/FINDING-hosted-judge-surfaces-missing-2026-09-18.md`
- Baseline: `python3 scripts/eval_hosted_partner_baseline.py` → naive PASS / shipping FAIL on live

**Local prove (no network, no real keys):**

```bash
bash scripts/prove_partner_health_local.sh
bash scripts/prove_judge_surfaces_local.sh
```
---

## Oscar deploy checklist (one pass)

1. **Rotate keys** if any revision ever had plaintext env vars (`deploy.sh` note). Oscar console only.
2. **`bash deploy.sh`** — Oscar only; writes Secret Manager, IAM, Cloud Run revision. Never `--set-env-vars` for secrets.
3. **Verify public partner proof (one command):**
   ```bash
   bash scripts/verify_partners_hosted.sh
   ```
   Expect: health OK with `engine_default: adk`, `gemini: true`, `parallel: true` · `/partners` JSON checklist true.
   Steps 3–5 (`/clear` + compound) need `export WORKSPACE_TOKEN=…`; without it the script exits **2** (PARTIAL) after proving public health+partners — not a silent green.
4. **Compound with Parallel drop (video beat), after token:**
   ```bash
   export WORKSPACE_TOKEN='…'   # Oscar workspace bearer — never in URL or repo
   python3 scripts/compound_fresh_hosted_probe.py
   ```
5. **Or verify /health alone:**
   ```bash
   curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
   ```
   Expect: `"gemini_path": "vertex:…"`, `"parallel": true`, `"engine_default": "adk"`, `"mode": "private-workspaces"`.
6. **Verify /clear** (workspace bearer — not public):
   ```bash
   curl -s -X POST https://agent-science-568004190078.us-central1.run.app/clear \
     -H "Authorization: Bearer $WORKSPACE_TOKEN" \
     -H 'Content-Type: application/json' \
     -d '{"script":"The Dust Bowl displaced 2.5 million people.","subject":"dust-bowl"}' \
     | python3 -c "import sys,json; d=json.load(sys.stdin); print('engine',d.get('engine')); print('parallel_calls',d.get('parallel_calls'))"
   ```
   If `/clear` is not mounted on the workspace desk, use local `python3 cloud/service.py` (no `K_SERVICE`) for ADK+Parallel call proof.

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

```json
{
  "ok": true,
  "service": "agent-science",
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
  "mode": "private-workspaces",
  "revision": "agent-science-NNNNN-xxx"
}
```

`mode` + `revision` appear on Cloud Run (WorkspaceHTTP). Local desk omits them.

| Field | Meaning |
|-------|---------|
| `gemini_path` | `vertex:<project>`, `api-key`, or `none` |
| `parallel` | `PARALLEL_API_KEY` present in env |
| `agent_builder` | `google-adk` importable |
| `engine_default` | What clearance will use when `/clear` runs: `adk` or `direct` |

Shared builder: `cloud.partners.health_payload()` — used by `cloud/service.py` and `cloud/case_http.py`.

### Routes

| Method | Path | Body | Response |
|--------|------|------|----------|
| GET | `/health` | — | JSON above (public on hosted) |
| GET | `/partners` | — | Track manifest — checklist measured at object (public) |
| GET | `/truths/ui` | — | Truths dashboard HTML (public; film) |
| GET | `/visibility/ui?q=` | — | Visibility HTML — Transparency pane (public; `live` default false) |
| GET | `/visibility?q=` | — | Visibility JSON (public) |
| GET | `/popular/ui` | — | Popular queries HTML (public) |
| GET | `/` | — | Local desk UI; hosted redirects to `/cases` or `/login` |
| GET | `/corpus?subject=` | — | `{subject, remembered, total}` (local desk) |
| POST | `/clear` | `{"script","subject"}` | Gap report JSON; `engine` stamped — **local desk, or hosted with workspace auth if mounted** |

**Local desk (ADK default path, no hosted gate):**
```bash
export PORT=8099 AGENT_BUILDER=1 GCP_PROJECT=hack-fleet
# PARALLEL_API_KEY from ~/.config/keys/parallel.key when proving live Parallel
python3 cloud/service.py
curl -s localhost:8099/health
```

**Hosted partner + film prove without deploy wait:**
```bash
bash scripts/prove_partner_health_local.sh
bash scripts/prove_judge_surfaces_local.sh
python3 tests/test_adk_default_path.py   # 5/5
python3 scripts/eval_hosted_partner_baseline.py   # expect exit 2 until Oscar deploy
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
```

Receipts: `docs/RECEIPT-hosted-partner-runtime-2026-08-30.md`, `docs/RECEIPT-live-compound-exhibit-2026-08-30.md`.

Live `/clear` requires Oscar deploy + keys. Offline controls prove partner **code paths** exist and are tested.
