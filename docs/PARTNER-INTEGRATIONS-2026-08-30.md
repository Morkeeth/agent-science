# PARTNER INTEGRATIONS — Agent Science · Sep 9 path

**Date:** 2026-08-30 · **Last verified:** 2026-09-08 · **Repo:** Morkeeth/agent-science · **Scope:** all four partners wired in code; dual-surface on this branch; **live hosted still stripped until Oscar `deploy.sh`.**

Each partner must be **called at runtime** on the default path — not documented only.

**Live object (2026-09-08):** revision `agent-science-00028-hed` serves liveness-only `/health` (`mode: private-workspaces`) — `docs/FINDING-hosted-partner-strip-2026-09-08.md`. Local dual-surface prove is green; hosted verify is intentionally RED until deploy.

---

## Oscar deploy checklist (one pass)

1. **Rotate keys** if any revision ever had plaintext env vars (`deploy.sh` note).
2. **`bash deploy.sh`** — Oscar only; candidate revision with dual-surface env + Secret Manager Parallel + workspace access.
3. **Verify candidate tag first:**
   ```bash
   bash scripts/verify_partners_hosted.sh https://workspace-candidate---<service-host>
   ```
   Expect: `mode=private-workspaces+public-desk` · `engine_default: adk` · `/clear` stamps `engine: adk` with `parallel_calls ≥ 1` on fresh claim · compound probes PASS.
4. **Promote** only after candidate verify is green.
5. **Live URL verify:**
   ```bash
   bash scripts/verify_partners_hosted.sh
   curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
   ```
6. **Without deploy (agent machines):**
   ```bash
   bash scripts/demo_partner_dual_surface.sh
   bash scripts/verify_partners_hosted.sh --local
   python3 scripts/eval_hosted_partner_surface.py   # naive wins on live until deploy
   ```

---

## Dual surface (one Cloud Run revision)

| Surface | Paths | Auth |
|---------|-------|------|
| **Public desk** (partner track) | `/`, `/clear`, `/health`, `/partners`, `/registry`, `/visibility`, `/search`, `/stats` | none |
| **Private workspaces** | `/cases`, `/api/cases`, `/login`, `/logout` | bearer / session |

Routing: `cloud/partner_status.is_workspace_path` · `cloud/service.py` Handler.

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

**Offline:** `cache/searches.json` — seeded by `python3 scripts/seed_document_cache.py`.

**Receipts:** `cache/search_receipts.jsonl` — each live call logs `search_id` when returned.

**Meter:** `clearance/search.py` `LIVE_CALLS` — single increment in `_live_search()` (SDK or REST).

**Judge manifest:** `GET /partners` — full track checklist + module map.

---

## 3 · Google Cloud — Cloud Run dual surface

| Field | Value |
|-------|-------|
| **Role** | Hosted clearance desk + private research workspaces |
| **Entrypoint** | `cloud/service.py` (Dockerfile `CMD`) |
| **Path split** | `cloud/partner_status.py` |
| **Deploy script** | `deploy.sh` (Oscar only — never run from agent) |
| **Project / region** | `hack-fleet` / `us-central1` |
| **Service name** | `agent-science` |
| **Corpus shelf** | GCS via `CORPUS_GCS_URI` / `REFUSAL_LOG_GCS_URI` |

### `/health` spec (after dual-surface deploy)

```json
{
  "ok": true,
  "service": "agent-science",
  "mode": "private-workspaces+public-desk",
  "public_desk": true,
  "gemini": true,
  "gemini_path": "vertex:hack-fleet",
  "parallel": true,
  "parallel_sdk": true,
  "agent_builder": true,
  "engine_default": "adk"
}
```

A response with only `ok` / `service` / `mode=private-workspaces` / `revision` is **RED** — that is revision 00028 today.

### Routes

| Method | Path | Auth | Response |
|--------|------|------|----------|
| GET | `/health` | none | Partner JSON above |
| GET | `/partners` | none | Track manifesto |
| GET | `/` | none | Desk UI |
| POST | `/clear` | none | Gap report; `engine` stamped |
| GET/POST | `/cases`, `/api/cases` | workspace token | Private research |

**Local dual-surface prove (no keys, no deploy):**
```bash
bash scripts/demo_partner_dual_surface.sh
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
**Controls:** `python3 tests/test_adk_default_path.py`  
**Fallback:** if ADK raises, direct pipeline with `engine: "direct"` and `adk_error` — never silent.

---

## Stranger cold clone (no keys)

```bash
git clone https://github.com/Morkeeth/agent-science.git && cd agent-science
bash scripts/verify_cold_clone.sh
bash scripts/demo_partner_dual_surface.sh
python3 scripts/eval_hosted_partner_surface.py
```

Live `/clear` with Parallel+ADK requires Oscar deploy. Offline controls prove partner **code paths** and the dual-surface contract.
