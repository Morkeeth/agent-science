# RECEIPT — live compound exhibit · 2026-08-31

**Status:** compound-mini PROVED on hosted URL. orphan-works A/B **504 Gateway Timeout** on Run A.

**URL:** https://agent-science-33kamss2jq-uc.a.run.app  
**Health:** `engine_default: adk`, `parallel: true`, `gemini_path: vertex:hack-fleet`

---

## Sealed prediction (SUBMISSION-PACK)

| Metric | Run A | Run B | Pass when |
|--------|-------|-------|-----------|
| `parallel_calls` | — | — | B < A |
| `corpus_hits` | — | — | B ≥ 1 |

---

## compound-mini · subject `compound-mini-live-2026-08-31`

```bash
cd /workspace
python3 <<'PY'
import json, urllib.request

URL = "https://agent-science-33kamss2jq-uc.a.run.app/clear"
SUBJECT = "compound-mini-live-2026-08-31"

def run(script_path, label):
    script = open(script_path).read()
    body = json.dumps({"script": script, "subject": SUBJECT}).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=600) as resp:
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

**Output this run (2026-08-31 UTC):**

| Metric | Run A | Run B |
|--------|-------|-------|
| `engine` | adk | adk |
| `parallel_calls` | 2 | 1 |
| `corpus_hits` | 0 | 2 |
| `corpus_remembered` | 2 | 3 |
| `claims_extracted` | 2 | 3 |
| `sourced` | 1 | 1 |
| `unsourced` | 1 | 2 |

**COMPOUND:** `A_parallel=2`, `B_parallel=1`, `B_hits=2`, **pass=True**

Wall clock: Run A ~85s, Run B ~26s.

---

## orphan-works · subject `orphan-works-live-2026-08-31`

**Scripts:** `fixtures/scripts/documentary-orphan-works.txt` → `documentary-orphan-works-B.txt`

**Outcome:** `HTTP 504 Gateway Timeout` on Run A (~4 min). Full orphan-works narration exceeds hosted gateway timeout; compound-mini is the proved hosted exhibit for this revision.

---

## A-vs-B delta fields (deploy pending)

Hosted JSON returned `prior_parallel_calls: null` and `parallel_delta: null` — expected until branch `cursor/compound-strip-delta-7f3b` is deployed. Local proof:

```bash
python3 tests/test_report_html.py
```

Compound strip HTML shows `3 → 1 (−2 vs last run)` from fixture dict at `_report_html` object.
