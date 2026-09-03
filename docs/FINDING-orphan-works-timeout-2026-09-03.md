# FINDING — orphan-works full script exceeds Cloud Run timeout · 2026-09-03

**Measured at object.** Do not cite prior receipts without re-running.

## What we ran

```bash
python3 - <<'PY'
import json, time, urllib.request, uuid
from pathlib import Path
BASE = "https://agent-science-568004190078.us-central1.run.app"
subject = f"orphan-probe-{uuid.uuid4().hex[:8]}"
script = Path("fixtures/scripts/documentary-orphan-works.txt").read_text()
body = json.dumps({"script": script, "subject": subject}).encode()
req = urllib.request.Request(BASE + "/clear", data=body,
    headers={"Content-Type": "application/json"}, method="POST")
t0 = time.time()
with urllib.request.urlopen(req, timeout=300) as resp:
    data = json.loads(resp.read())
PY
```

**Output (2026-09-03T00:11Z):** `HTTP Error 504: Gateway Timeout` after **300.1s**.

## Regression vs prior receipts

| Date | Run A | Run B | Source |
|------|-------|-------|--------|
| 2026-08-31 | ok (~86s, 2 Parallel) | **503** | `RECEIPT-live-compound-exhibit-2026-08-31.md` |
| 2026-09-01 | ok (~202s, 7 Parallel) | **504** @ 300s | `RECEIPT-partner-integrations-night-2026-09-01.md` |
| **2026-09-03** | **504** @ 300s | not attempted | this finding |

**Run A alone now fails.** Prior docs said "use compound-mini for video" because Run B timed out; the failure mode has widened to the full script on any run.

## Root cause (at object)

| Factor | Value |
|--------|-------|
| Script size | 25 lines · 1,357 chars · ~9 extractable claims |
| Cloud Run timeout | **300s** (`deploy.sh` line 73: `--timeout=300`) |
| Per-claim cost | ~30–40s when Parallel + Gemini locate run live |
| Warm shelf | Does not help first run on fresh subject — all claims miss |

**Math:** 9 claims × ~35s ≈ 315s > 300s ceiling. Explains 504 without invoking a code regression.

## What still works (verified tonight)

```bash
python3 scripts/compound_fresh_hosted_probe.py
# RUN_A parallel_calls=2 → RUN_B parallel_calls=1, corpus_hits=1, pass=True
```

```bash
python3 scripts/compound_hosted_probe.py
# compound-mini warm shelf: A=0 B=0 Parallel, corpus_hits=2, pass=True
```

## Oscar unblock (deploy only — not agent)

1. **`deploy.sh`:** raise `--timeout=600` (or 900) for full-script clearance.
2. **Video:** film `compound_fresh_hosted_probe.py` output or compound-mini — **not** full orphan-works script.
3. **Honest claim:** "Full 25-line narration exceeds 300s hosted ceiling; compound economics proved on fresh-subject probe."

## Constraint honored

We refused to tick "orphan-works compound live" — the done-when was run and it returned 504.
