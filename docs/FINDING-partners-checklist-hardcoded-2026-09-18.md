# FINDING — `/partners` checklist hardcoded Parallel · 2026-09-18

**Object:** `cloud/partners.py` → `manifest()["track_checklist"]["parallel_search_at_runtime"]`  
**Also live:** `GET …/partners` on revision `agent-science-00028-hed` (303 login — not JSON)

## Commands

```bash
# Local object — no Parallel key, empty receipts
python3 - <<'PY'
import os, json, tempfile
from pathlib import Path
from unittest.mock import patch
from clearance import search
from cloud import partners
search.RECEIPTS = Path(tempfile.mkdtemp()) / "absent.jsonl"
env = {k: v for k, v in os.environ.items() if k != "PARALLEL_API_KEY"}
with patch.dict(os.environ, env, clear=True):
    os.environ.pop("PARALLEL_API_KEY", None)
    print(json.dumps(partners.manifest()["track_checklist"], indent=2))
PY
```

**Observed before fix:** `parallel_search_at_runtime: true` while
`partners.parallel.runtime: false`, `live_calls: 0`, `verified_search_id: null`.

**Why this is a false-green:** the judge track checklist answered "does Parallel run?"
with a constant `True` — a nearer proxy than the key or a receipt. Same failure
mode as stripped `/health` and as `grep -qv` on empty input.

## Fix in tree

`parallel_search_at_runtime` = `bool(PARALLEL_API_KEY)`.  
Added `parallel_search_proven` from `last_verified_receipt().verified_search_id`.

Control: `python3 tests/test_partner_runtime.py` →
`t_partners_checklist_not_hardcoded_parallel_runtime` · hosted_flow
`test_partners_checklist_goes_red_without_parallel_key`.

## Related live RED (same night)

```bash
python3 scripts/eval_hosted_partner_baseline.py
# naive ok:true PASS · shipping partner fields FAIL on 00028-hed
curl -sS -o /dev/null -w '%{http_code}\n' …/truths/ui   # 303
curl -sS -o /dev/null -w '%{http_code}\n' …/visibility/ui?q=ralph  # 303
```

Film surfaces were also **unmounted** on WorkspaceHTTP (auth → 404). Fix:
`cloud/case_http.py` public judge GET for `/truths/ui`, `/visibility[/ui]`,
`/popular[/ui]`. Local prove: `bash scripts/prove_judge_surfaces_local.sh`.
