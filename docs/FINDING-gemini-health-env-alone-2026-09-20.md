# FINDING — gemini:true from GCP_PROJECT alone · 2026-09-20

**Object:** `cloud.partners.resolve_gemini_path()` → `/health` field `gemini`  
**Command that exposed it:**

```bash
GCP_PROJECT=hack-fleet python3 - <<'PY'
import os
os.environ.pop("GEMINI_API_KEY", None)
os.environ.pop("GOOGLE_API_KEY", None)
from cloud.partners import health_payload, resolve_gemini_path
from clearance import gemini as g
print("path", resolve_gemini_path())
print("gemini", health_payload()["gemini"])
print("vertex_token", bool(g.vertex_token()))
PY
```

**Observed before fix (this VM, no ADC):**

| Field | Value |
|-------|-------|
| `resolve_gemini_path()` | `vertex:hack-fleet` |
| `/health` `gemini` | `true` |
| `vertex_token()` | absent / falsy |

**Why this is a false-green class defect:** partner admissibility requires partners
**called at runtime**. `GCP_PROJECT` (or `K_SERVICE` → `vertex:adc`) made health claim
Vertex was reachable when no access token existed. `bash scripts/prove_partner_health_local.sh`
greened on that shape while patching ADK and setting a fake Parallel key — shape proof,
not call proof.

**Related live defect still RED:** revision `agent-science-00028-hed` strips partner fields
entirely (`docs/FINDING-hosted-health-partner-strip-2026-09-16.md`). Watched tonight:

```bash
bash scripts/watch_hosted_partner_health.sh   # EXPECT_STATE=red → WATCH RED OK
```

**Fix in tree:**

- `resolve_gemini_path()` returns `vertex:…` only when `vertex_token()` succeeds (or API key).
- `/health` adds `gemini_configured` (env intent) vs `gemini` (callable).
- Receipt-backed Parallel fields on health: `verified_search_id`, `verified_calls_logged`.
- `track_checklist.parallel_search_at_runtime` is key presence, not hardcoded `True`.
- Call-proof script: `python3 scripts/prove_partner_calls_local.py`
- RED control: `tests/test_partner_runtime.py::t_gemini_project_env_alone_is_not_callable`

**Still not a live Parallel call on this VM:** no `PARALLEL_API_KEY`. Offline mock call
increments `LIVE_CALLS` and stamps `search_id` — that is transport proof, not billing proof.
