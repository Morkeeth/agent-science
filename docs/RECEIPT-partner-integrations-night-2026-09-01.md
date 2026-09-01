# RECEIPT — partner integrations night · 2026-09-01

**URL:** https://agent-science-568004190078.us-central1.run.app  
**Branch:** `cursor/partner-integrations-night-6104` → merge to `main`  
**Scope:** all four partners called at runtime on hosted desk; promise line; eval gate re-run.

---

## 1 · Hosted `/health` — all four partners on path

```bash
curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
```

**Output this run (2026-09-01T00:05Z):**

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
    "agent_builder": true,
    "adk_version": "2.7.1",
    "engine_default": "adk"
}
```

**Finding:** Gemini via Vertex ADC (no plaintext key). Parallel SDK present. ADK default engine.

---

## 2 · Hosted `/partners` — judge manifest

```bash
curl -s https://agent-science-568004190078.us-central1.run.app/partners | python3 -m json.tool
```

**Finding:** `track_checklist` all `true` — `parallel_search_at_runtime`, `parallel_web_sdk`, `gemini_at_runtime`, `adk_agent_builder`, `hosted_url_required`.

---

## 3 · Compound exhibit — compound-mini (PASS)

**Subject:** `compound-night-<uuid>` (fresh — avoids warm GCS shelf)

```bash
cd /workspace
python3 <<'PY'
import json, urllib.request, time, uuid

BASE = "https://agent-science-568004190078.us-central1.run.app"
SUBJECT = f"compound-night-{uuid.uuid4().hex[:8]}"

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

**Output this run (2026-09-01T00:08Z):**

```
RUN_A {'engine': 'adk', 'parallel_calls': 2, 'corpus_hits': 0, 'corpus_remembered': 2, 'claims_extracted': 2, 'sourced': 1, 'unsourced': 1} elapsed=47.8s
RUN_B {'engine': 'adk', 'parallel_calls': 1, 'corpus_hits': 1, 'corpus_remembered': 3, 'claims_extracted': 2, 'sourced': 1, 'unsourced': 1} elapsed=37.2s
COMPOUND {'A_parallel': 2, 'B_parallel': 1, 'B_hits': 1, 'pass': True}
```

**Finding:** sealed prediction passes. `engine: adk` on both runs — ADK default path live.

---

## 4 · Orphan-works full script — BLOCKED on Run B

**Subject:** `orphan-works-night-<uuid>`

```bash
# same probe pattern; fixtures/scripts/documentary-orphan-works*.txt
```

**Output this run (2026-09-01T00:17Z):**

```
RUN_A {'engine': 'adk', 'parallel_calls': 7, 'corpus_hits': 0, 'claims_extracted': 9, 'sourced': 2, 'unsourced': 7} elapsed=201.7s
RUN_B ERROR HTTPError HTTP Error 504: Gateway Timeout elapsed=300.1s
```

**Finding:** Run A completes (7 Parallel, 9 claims). Run B hits **504 Gateway Timeout** at 300s — do not claim full orphan-works compound on video. Offline receipt remains authoritative for full-script narrative.

**Missing credential:** N/A — hosted has keys. Blocker is **Cloud Run gateway timeout**, not missing API key.

---

## 5 · Local controls (cold clone path)

```bash
python3 scripts/seed_document_cache.py
python3 tests/test_watch_it_go_red.py          # 72/72
python3 tests/test_partner_runtime.py          # 6/6
python3 tests/test_parallel_integration.py     # 6/6
python3 tests/test_adk_default_path.py         # 5/5
python3 scripts/bench_check_docs.py            # 127/127 match
bash scripts/full_gate.sh                      # FULL GATE OK 2026-09-01T00:05:58Z
```

---

## 6 · Qwen eval gate re-run

```bash
python3 scripts/eval_refusal_baseline.py
python3 scripts/eval_refusal_ablation.py
```

**Output this run (2026-09-01T00:05Z):**

```
Baseline:  5/6 = 0.833  95% CI [0.436, 0.970]
Shipping:  6/6 = 1.000  95% CI [0.610, 1.000]
Delta (shipping - baseline): +1
McNemar:   p=1.0000 (b=0 c=1 discordant)

Ablation:  5/6 = 0.833
Shipping:  6/6 = 1.000
Delta (shipping - ablation): +1
McNemar:   p=1.0000 (b=0 c=1 discordant)
```

**Finding:** shipping beats baseline/ablation by +1 (RC5). Not significant at n=6.

---

## Partner doc index

- `docs/PARTNER-INTEGRATIONS-2026-08-30.md` — SDK entrypoints, env vars, Secret Manager, curl examples
- `docs/RECEIPT-adk-default-path-2026-08-30.md` — ADK default engine receipt
- `docs/DESIGN-PARTNER-LOOP.md` — slice 6 friction template (Oscar sends to partner)
