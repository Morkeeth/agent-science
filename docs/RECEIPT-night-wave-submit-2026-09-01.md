# RECEIPT — night wave submit path · 2026-09-01

**Branch:** `cursor/night-wave-submit-path-2316`  
**Slice:** SUBMISSION-PACK truth refresh + Qwen eval gates (holdout frozen + scorer symmetry)

---

## 1 · SUBMISSION-PACK counts re-measured at object

```bash
python3 scripts/seed_document_cache.py
python3 scripts/bench_check_docs.py
```

**Output this run:**

```
ALL 127/127 match SUBMISSION-PACK
```

**Fixed in pack:** Devpost paste `registry **13/13**` → `registry surface **16/16**` (measured `python3 tests/test_registry_surface.py` → 16/16).

---

## 2 · Qwen eval gates (new)

### Holdout frozen

```bash
python3 scripts/eval_holdout_frozen.py
```

```
PASS  scoring labels match frozen manifest
FINDING: holdout labels frozen before tuning commits on record.
NOTE  post-freeze metadata on: RC5 — labels unchanged; not a re-label
```

Manifest: `fixtures/refusal-correctness/HOLDOUT-MANIFEST.json`  
Label hash: `34f809a92e3a94320dfdf23174eba8ebf902960b7ec3729cda0663be7cf43bdb`

### Scorer symmetry (delivered JSON only)

```bash
python3 scripts/seed_document_cache.py
python3 scripts/eval_scorer_symmetry.py
```

```
Baseline:  5/6 = 0.833  95% CI [0.436, 0.970]
Shipping:  6/6 = 1.000  95% CI [0.610, 1.000]
Delta (shipping - baseline): +1
RC5: baseline false-SUPPORTED, shipping refuses — delta visible to external judge.
```

### Baseline + ablation (re-derived)

```bash
python3 scripts/eval_refusal_baseline.py
python3 scripts/eval_refusal_ablation.py
```

| Arm | Score | Delta vs shipping |
|-----|-------|-------------------|
| Baseline (substring) | 5/6 | +1 (RC5) |
| Ablation (no verify) | 5/6 | +1 (RC5) |
| Shipping | 6/6 | — |

McNemar p=1.0 at n=6 — real delta, not significant.

---

## 3 · Stranger one-command block

```bash
git clone https://github.com/Morkeeth/agent-science.git && cd agent-science
bash scripts/verify_cold_clone.sh
python3 tests/test_registry_surface.py -q
python3 scripts/compound_exhibit_receipt.py | tail -8
```

**Output this run:** `=== cold-clone verify OK ===` · registry **16/16** · offline compound A=2→B=1 Parallel, corpus_hits=2.

---

## 4 · Live compound exhibit — BLOCKED

```bash
test -n "$PARALLEL_API_KEY" && echo PARALLEL=yes || echo PARALLEL=no
test -n "$GEMINI_API_KEY" && echo GEMINI=yes || echo GEMINI=no
test -f ~/.config/keys/parallel.key && echo parallel.key=yes || echo parallel.key=no
```

**Output this run:**

```
PARALLEL=no
GEMINI=no
parallel.key=no
```

**Finding:** Live orphan-works A/B on Gemini+Parallel cannot run on this VM. Offline compound receipt is authoritative (`python3 scripts/compound_exhibit_receipt.py`). Prior hosted receipt: `docs/RECEIPT-live-compound-exhibit-2026-08-31.md` (compound-mini PASS; orphan-works B 503).

---

## 5 · Controls pinned

```bash
python3 tests/test_watch_it_go_red.py 2>&1 | tail -1
python3 tests/test_eval_holdout_gate.py
python3 tests/test_vision_wiring.py
```

**Output:** 72 passed, 0 failed · 2/2 eval holdout gate · 3/3 vision wiring.

**Note:** `test_watch_it_go_red.py` requires `python3 scripts/seed_document_cache.py` first on cold checkout — already in `verify_cold_clone.sh` step 1.

---

## hack.md checklist updates

- [x] Holdout frozen before tuning — `eval_holdout_frozen.py`
- [x] Scorer symmetrical — `eval_scorer_symmetry.py`
- [ ] Cost from billing — not attempted (no billing export on VM)
- [ ] Video verified on live Devpost page — Oscar outward act
