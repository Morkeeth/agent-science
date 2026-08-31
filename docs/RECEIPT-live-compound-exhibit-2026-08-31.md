# RECEIPT — live compound exhibit · re-derived 2026-08-31

**URL:** https://agent-science-568004190078.us-central1.run.app  
**Also resolves:** https://agent-science-33kamss2jq-uc.a.run.app (same revision, probed 2026-08-31)

---

## 1 · compound-mini (fresh subject — PASS)

**Subject:** `compound-fresh-c1eb52fe` (UUID suffix — avoids warm GCS shelf)

```bash
cd /workspace
python3 <<'PY'
import json, urllib.request, time, uuid

BASE = "https://agent-science-568004190078.us-central1.run.app"
SUBJECT = "compound-fresh-c1eb52fe"

def run(script_path, label):
    script = open(script_path).read()
    body = json.dumps({"script": script, "subject": SUBJECT}).encode()
    req = urllib.request.Request(BASE + "/clear", data=body,
        headers={"Content-Type": "application/json"}, method="POST")
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as resp:
        d = json.loads(resp.read())
    keys = ["engine","parallel_calls","corpus_hits","corpus_remembered","claims_extracted","sourced","unsourced"]
    print(label, {k: d.get(k) for k in keys}, f"elapsed={time.time()-t0:.1f}s")
    return d

a = run("fixtures/scripts/compound-mini-A.txt", "RUN_A")
b = run("fixtures/scripts/compound-mini-B.txt", "RUN_B")
ap, bp, bh = a.get("parallel_calls") or 0, b.get("parallel_calls") or 0, b.get("corpus_hits") or 0
print("COMPOUND", {"A_parallel": ap, "B_parallel": bp, "B_hits": bh, "pass": bp < ap and bh >= 1})
PY
```

**Output this run (2026-08-31 UTC):**

```
RUN_A {'engine': 'adk', 'parallel_calls': 2, 'corpus_hits': 0, 'corpus_remembered': 2, 'claims_extracted': 2, 'sourced': 1, 'unsourced': 1} elapsed=86.5s
RUN_B {'engine': 'adk', 'parallel_calls': 1, 'corpus_hits': 1, 'corpus_remembered': 3, 'claims_extracted': 2, 'sourced': 1, 'unsourced': 1} elapsed=31.5s
COMPOUND {'A_parallel': 2, 'B_parallel': 1, 'B_hits': 1, 'pass': True}
```

**Finding:** prediction passes on fresh subject. All four partners on path (`engine: adk`, Parallel called).

---

## 2 · Warm-subject false FAIL (control — do not reuse shelf)

Re-running on `compound-mini-live-2026-08-30` (prior night's subject) **without** a fresh UUID:

```
RUN_A parallel_calls=0 corpus_hits=2   # shelf already warm
RUN_B parallel_calls=0 corpus_hits=3
COMPOUND pass=False                    # B.parallel < A.parallel fails
```

**Lesson:** compound metric requires a **cold subject shelf** or explicit corpus reset. Reusing a subject from a prior receipt invalidates the Parallel-drop claim.

---

## 3 · orphan-works full script (PARTIAL — 503 on run B)

**Subject:** `orphan-works-live-66d21d70`

```
RUN_A parallel_calls=9 corpus_hits=0 corpus_remembered=9 claims_extracted=9 sourced=4 unsourced=5 elapsed=292.6s
RUN_B HTTP 503 Service Unavailable (after ~5 min wall clock)
```

**Status:** run A completed; run B blocked by Cloud Run 503. Compound prediction **not sealed** on full orphan-works scripts. Offline receipt still authoritative: `docs/COMPOUND-EXHIBIT-2026-08-29.md` (2→1 Parallel).

**Unblock:** Oscar retries B on hosted desk or increases Cloud Run timeout/concurrency; agent may retry with backoff.

---

## Health (all four partners)

```bash
curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
```

```json
{
  "ok": true,
  "service": "agent-science",
  "gemini": true,
  "gemini_path": "vertex:hack-fleet",
  "parallel": true,
  "agent_builder": true,
  "adk_version": "2.7.1",
  "engine_default": "adk"
}
```
