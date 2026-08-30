# RECEIPT — live compound exhibit on hosted URL · 2026-08-30

**Status:** PROVED on hosted Cloud Run desk (not offline fakes).

**URL:** https://agent-science-568004190078.us-central1.run.app  
**Subject shelf:** `compound-mini-live-2026-08-30`  
**Scripts:** `fixtures/scripts/compound-mini-A.txt` → `fixtures/scripts/compound-mini-B.txt`

---

## Prediction (from SUBMISSION-PACK)

> Second `POST /clear` on same subject returns `corpus_hits ≥ 1` and strictly fewer `parallel_calls` than the first run.

---

## Run (re-derive — do not carry these numbers)

```bash
cd /workspace
python3 <<'PY'
import json, urllib.request

URL = "https://agent-science-568004190078.us-central1.run.app/clear"
SUBJECT = "compound-mini-live-2026-08-30"

def run(script_path, label):
    script = open(script_path).read()
    body = json.dumps({"script": script, "subject": SUBJECT}).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=300) as resp:
        d = json.loads(resp.read())
    keys = ["engine","parallel_calls","corpus_hits","corpus_remembered","claims_extracted","sourced","unsourced"]
    print(label, {k: d.get(k) for k in keys})
    return d

a = run("fixtures/scripts/compound-mini-A.txt", "RUN_A")
b = run("fixtures/scripts/compound-mini-B.txt", "RUN_B")
ap, bp, bh = a.get("parallel_calls") or 0, b.get("parallel_calls") or 0, b.get("corpus_hits") or 0
print("COMPOUND", {"A_parallel": ap, "B_parallel": bp, "B_hits": bh, "pass": bp < ap and bh >= 1})
PY
```

**Output this run (2026-08-30 UTC):**

```
RUN_A {'engine': 'adk', 'parallel_calls': 2, 'corpus_hits': 0, 'corpus_remembered': 2, 'claims_extracted': 2, 'sourced': 0, 'unsourced': 2}
RUN_B {'engine': 'adk', 'parallel_calls': 1, 'corpus_hits': 2, 'corpus_remembered': 3, 'claims_extracted': 3, 'sourced': 0, 'unsourced': 3}
COMPOUND {'A_parallel': 2, 'B_parallel': 1, 'B_hits': 2, 'pass': True}
```

---

## Finding (honest)

- **Compound prediction passes:** B.parallel (1) < A.parallel (2) and B.corpus_hits (2) ≥ 1.
- **All four partners on path:** `engine: adk` (Agent Builder), Parallel called on both runs, Vertex Gemini inside ADK pipeline.
- **sourced=0 on both runs:** live extraction did not produce SOURCED verdicts on this mini script — compounding metric (Parallel drop + corpus hits) is what passed, not sourcing rate.
- **Latency:** ~5 min wall clock for both POSTs (hosted cold-ish path).

**Supersedes:** `docs/BLOCKED-live-compound-exhibit-2026-08-30.md` for hosted URL only. Local VM still blocked (no keys).
