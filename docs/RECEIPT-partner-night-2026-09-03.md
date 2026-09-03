# RECEIPT — partner integrations night · 2026-09-03

**URL:** https://agent-science-568004190078.us-central1.run.app  
**Branch:** `main`  
**Scope:** re-verify four partners; ship fresh compound probe; document orphan-works timeout regression.

---

## 1 · Hosted `/health` — all four partners

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
    "parallel_sdk": true,
    "parallel_sdk_version": "1.3.2",
    "parallel_transport": "parallel-web",
    "agent_builder": true,
    "adk_version": "2.7.1",
    "engine_default": "adk"
}
```

---

## 2 · Parallel at runtime (fresh claim — not warm shelf)

```bash
bash scripts/verify_partners_hosted.sh
# step 3: UUID-embedded claim → parallel_calls >= 1, engine=adk
```

**Output this run:** `parallel_calls: 2` · `engine: adk`

---

## 3 · Compound-fresh A/B (NEW — forces Parallel drop)

```bash
python3 scripts/compound_fresh_hosted_probe.py
```

**Output (2026-09-03T00:16Z):**

```
RUN_A {'engine': 'adk', 'parallel_calls': 2, 'corpus_hits': 0, ...}
RUN_B {'engine': 'adk', 'parallel_calls': 1, 'corpus_hits': 1, ...}
COMPOUND {'subject': 'compound-fresh-08aba584c625', 'A_parallel': 2, 'B_parallel': 1, 'B_hits': 1, 'pass': True}
```

**Why:** `compound_hosted_probe.py` can show A=0 Parallel on warm GCS shelf. Fresh probe embeds UUID in claims so Run A must call Parallel.

---

## 4 · Compound-mini (warm shelf)

```bash
python3 scripts/compound_hosted_probe.py
```

**Output:** A=0 B=0 Parallel · B `corpus_hits=2` · pass (corpus clause only).

---

## 5 · Orphan-works full script — REGRESSION

```bash
# fixtures/scripts/documentary-orphan-works.txt on fresh subject
```

**Output:** `HTTP Error 504: Gateway Timeout` after **300.1s** on Run A alone.

See `docs/FINDING-orphan-works-timeout-2026-09-03.md`. Do **not** claim full orphan-works compound on video.

---

## 6 · Gates

```bash
git pull && python3 tests/test_watch_it_go_red.py          # 72/72
bash scripts/full_gate.sh                                 # FULL GATE OK
python3 scripts/bench_check_docs.py                       # 127/127
python3 scripts/eval_refusal_baseline.py                  # baseline 5/6, shipping 6/6, delta +1
python3 scripts/eval_refusal_ablation.py                  # ablation 5/6, shipping 6/6, delta +1
bash scripts/verify_cold_clone.sh                         # cold-clone verify OK
```

---

## Shipped tonight

| Item | Path |
|------|------|
| Fresh compound probe | `scripts/compound_fresh_hosted_probe.py` |
| Partner verify hardened | `scripts/verify_partners_hosted.sh` (Parallel ≥1 + fresh compound) |
| Orphan-works finding | `docs/FINDING-orphan-works-timeout-2026-09-03.md` |
