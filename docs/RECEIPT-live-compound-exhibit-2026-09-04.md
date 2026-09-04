# RECEIPT — live compound exhibit · 2026-09-04

**Probe:** `python3 scripts/compound_fresh_hosted_probe.py`  
**Host:** https://agent-science-568004190078.us-central1.run.app  
**Local keys:** not required — hosted service holds Parallel/Gemini

---

## Result (at object)

```
RUN_A {'engine': 'adk', 'parallel_calls': 1, 'corpus_hits': 0, 'corpus_remembered': 2,
       'claims_extracted': 2, 'sourced': 0, 'unsourced': 2, 'elapsed_s': 42.2}
RUN_B {'engine': 'adk', 'parallel_calls': 1, 'corpus_hits': 1, 'corpus_remembered': 4,
       'claims_extracted': 3, 'sourced': 0, 'unsourced': 3, 'elapsed_s': 44.1}
COMPOUND {'subject': 'compound-fresh-a7009f2c6127', 'A_parallel': 1, 'B_parallel': 1,
          'B_hits': 1, 'pass': True}
```

| Metric | Run A | Run B | Pass rule |
|--------|------:|------:|-----------|
| `parallel_calls` | **1** | **1** | B ≤ A |
| `corpus_hits` | 0 | **1** | B ≥ 1 |
| engine | adk | adk | — |

**PASS** — A exercised Parallel (≥1); B compounded (`corpus_hits=1`); B Parallel did not rise.

---

## Honest limits

- **Parallel did not drop** (1→1). Compounding showed up as `corpus_hits`, not a Parallel cliff. Do not claim A=1→B=0 on this subject; that headline remains the sealed `longrun-0831-1320` measure.
- **Orphan-works full script** still **504 @ 300s** — not re-attempted; see `docs/FINDING-orphan-works-timeout-2026-09-03.md`.
- Earlier this wave assumed local keys were required and wrote a BLOCKED stub. **Wrong.** Hosted `/clear` carries the service keys; the fresh probe is the object.

---

## Supersedes

`docs/BLOCKED-live-compound-exhibit-2026-09-04.md` — kept as the record of the wrong local-key assumption.
