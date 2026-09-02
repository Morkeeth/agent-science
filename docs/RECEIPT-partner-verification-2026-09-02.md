# RECEIPT — partner verification night · 2026-09-02

**URL:** https://agent-science-568004190078.us-central1.run.app  
**Branch:** `cursor/partner-verification-night-5157`  
**Scope:** re-verify all four partners at runtime; ship one-command Oscar verify script; fix unseeded test trap.

---

## 1 · Hosted `/health` — all four partners

```bash
curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
```

**Output this run (2026-09-02T00:10Z):**

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
    "last_parallel_search_id": null,
    "agent_builder": true,
    "adk_version": "2.7.1",
    "engine_default": "adk"
}
```

---

## 2 · POST `/clear` — ADK engine at runtime

```bash
curl -s -X POST https://agent-science-568004190078.us-central1.run.app/clear \
  -H 'Content-Type: application/json' \
  -d '{"script":"The Dust Bowl displaced 2.5 million people.","subject":"dust-bowl-verify"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('engine'), d.get('parallel_calls'))"
```

**Output:** `adk 1`

---

## 3 · Compound exhibit — compound-mini A/B (PASS)

```bash
python3 scripts/compound_hosted_probe.py
```

**Output this run:**

```
RUN_A {'engine': 'adk', 'parallel_calls': 0, 'corpus_hits': 0, ...}
RUN_B {'engine': 'adk', 'parallel_calls': 0, 'corpus_hits': 1, ...}
COMPOUND {'A_parallel': 0, 'B_parallel': 0, 'B_hits': 1, 'pass': True}
```

**Finding:** warm GCS shelf → A=0 Parallel is valid when `corpus_hits≥1` on B (matches hack.md compound note).

---

## 4 · One-command partner verify (NEW)

```bash
bash scripts/verify_partners_hosted.sh
```

Runs `/health`, `/partners`, live `/clear` (engine=adk), and compound-mini A/B in one pass.

---

## 5 · Full gate + eval gates

```bash
bash scripts/full_gate.sh                    # FULL GATE OK 2026-09-02T00:10:45Z
python3 scripts/bench_check_docs.py          # 127/127
python3 scripts/eval_refusal_baseline.py     # baseline 5/6, shipping 6/6, delta +1
python3 scripts/eval_refusal_ablation.py     # ablation 5/6, shipping 6/6, delta +1
python3 tests/test_watch_it_go_red.py        # 72/72 (auto-seeds when cache empty)
```

---

## BLOCKED

**Orphan-works full script Run B** — not re-claimed. Prior runs: **504 Gateway Timeout** at 300s (Run A ok). Use compound-mini for video compound beat.

---

## WRONG

| Item | Status |
|------|--------|
| START command without seed | **Fixed** — `test_watch_it_go_red.py` auto-seeds empty cache |
| Orphan-works hosted B | Still BLOCKED — not probed to completion this run |
| McNemar p=1.0 at n=6 | Eval delta +1 is real but not significant |
