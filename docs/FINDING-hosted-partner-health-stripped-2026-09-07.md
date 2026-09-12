# FINDING — Hosted partner health stripped by private-workspaces · 2026-09-07

**Status:** RED on live revision · fix in code awaiting Oscar `deploy.sh`  
**Re-measured:** 2026-09-12 against `agent-science-00028-hed` — still RED (same strip, newer revision).

## Object measured (not a proxy)

```bash
curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
python3 scripts/watch_hosted_partner_health.py
```

**Observed on `agent-science-00026-zel` (2026-09-07T00:11Z) and again on `agent-science-00028-hed` (2026-09-12T13:07Z):**

```json
{
  "ok": true,
  "service": "agent-science",
  "mode": "private-workspaces",
  "revision": "agent-science-00028-hed"
}
```

Missing: `gemini`, `gemini_path`, `parallel`, `parallel_sdk`, `agent_builder`, `engine_default`.

```bash
bash scripts/verify_partners_hosted.sh
# → AssertionError: missing health field gemini  (or equivalent)

python3 scripts/watch_hosted_partner_health.py
# baseline_arm (ok-only): GREEN
# partner_arm  (fields):  RED  missing=[...]
# FINDING: naive ok-only arm is GREEN while partner arm is RED
```

`GET /partners` and unauthenticated `POST /clear` return 303/401 HTML — not the partner manifest or clearance JSON claimed in older receipts.

## Why this happened

`cloud/case_http.py` served a minimal liveness `/health` under `AGENT_SCIENCE_HOSTED=1`. Partner-rich `/health` and `/partners` lived only on the local desk path in `cloud/service.py`. After the private-workspace pivot, Cloud Run never hit those routes.

Docs and receipts from 2026-08-30 through 2026-09-03 still claimed hosted `engine_default: adk`. Those claims were true of an earlier revision and became false without a RED control against the live URL after the pivot.

**2026-09-12:** the Sep-7 fix branch existed but was not on `main`; live advanced to `00028-hed` and remained stripped. A nearer proxy (STATUS.md / old receipts) still answered faster than curling `/health`.

## What the fix does (this branch)

1. Public `GET /health` returns full partner wiring **and** `mode`/`revision`.
2. Public `GET /partners` returns the track manifest (no secrets).
3. `POST /api/clear` is **auth-gated** (workspace bearer) — Parallel/Gemini/ADK at runtime without reopening unauthenticated clearance.
4. `deploy.sh` sets non-secret `AGENT_BUILDER=1`, `GCP_PROJECT`, `GOOGLE_CLOUD_LOCATION=global` so Vertex path reports correctly.
5. `track_checklist.parallel_search_at_runtime` is no longer hardcoded `True` — it requires a key or a verified receipt.
6. Partner verify script fails RED on stripped health; exit 2 if token missing for runtime clear.
7. `scripts/watch_hosted_partner_health.py` prints naive ok-only vs partner arms so stripped liveness cannot fake green.
8. `scripts/prove_partner_surfaces_local.py` — cold local HTTP prove, no network/keys.

## Not claimed

- Live hosted still RED until Oscar deploys this revision.
- This VM has no `PARALLEL_API_KEY` / workspace token — runtime clear on hosted not re-proved here tonight.
