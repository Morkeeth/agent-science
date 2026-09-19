# FINDING — partner local prove mocked ADK · 2026-09-19

**Object:** `scripts/prove_partner_health_local.sh` (pre-fix on main at `d56aeb8`)  
**Command that exposed it:**

```bash
python3 -c "from cloud import agent; print(agent.adk_available(), agent.adk_version())"
# → False None   (google-adk not installed in the agent VM)

bash scripts/prove_partner_health_local.sh
# → PROVE_PARTNER_HEALTH_LOCAL OK · engine_default: adk · adk_version: 2.7.1
```

**Observed defect:** the prove script patched `cloud.agent.adk_available` → `True` and
`adk_version` → `"2.7.1"`. A green local prove therefore did **not** establish that
Agent Builder is importable or that `engine_default: adk` would hold without the
patch. Same false-green class as stripped hosted `/health` and hardcoded
`parallel_search_at_runtime: True`.

**Also measured:** `parallel-web` was absent (`sdk_available() False`, transport
`urllib-rest`) while `requirements.txt` pins `parallel-web==1.3.2` and
`verify_partners_hosted.sh` asserts `parallel_sdk: True`. Local prove accepted
`parallel_sdk: false`.

**Fix:** `prove_partner_health_local.sh` now requires real `google.adk` and
`parallel` imports at the pinned versions; no availability mocks.
`scripts/prove_adk_clear_path.py` proves `_run_clearance` selects `engine: adk`
with a real import (runner stubbed only — no live Gemini spend).

**Still RED until Oscar deploy:** live revision `agent-science-00028-hed` health
remains stripped; baseline eval naive PASS / shipping FAIL.
