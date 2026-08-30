# QWEN EVAL GATE — alternative arm · 2026-08-30

**Gate item:** Alternative arm named and run — competent baseline without this project, identical inputs, offline.

**Held-out set:** `fixtures/refusal-correctness/set.json` (n=6, labelled before controls).

---

## Arms

| Arm | Description |
|-----|-------------|
| **Baseline** | Substring in document: GREEN if `must_contain` appears anywhere (no verifier, no independence) |
| **Shipping** | `StringLocator` + `verify` + `judge_claim` (DEFAULT path) |

---

## Run (re-derive — do not carry these numbers)

```bash
python3 scripts/seed_document_cache.py
python3 scripts/eval_refusal_baseline.py
```

**Output this run (2026-08-30 UTC):**

```
Baseline:  5/6 = 0.833  95% CI [0.436, 0.978]
Shipping:  5/6 = 0.833  95% CI [0.436, 0.978]
Delta (shipping - baseline): +0
McNemar:   p=1.0000 (no discordant pairs — arms identical on every item)
FINDING: tied — verifier adds no delta on n=6; look at per-item false GREENs.
RC5 substring trap: BOTH arms false-GREEN — documented engine limit.
```

---

## Finding (honest)

- **Tied at 0.833** on n=6 — verifier does not beat naive substring on accuracy alone.
- **RC5** is the embarrassment: both arms false-GREEN. Documented in `docs/FINDING-substring-is-not-a-statement.md`; pinned in set.json as `engine_limit: substring_not_a_statement`.
- **RC1/RC2** false-UNKNOWN direction: shipping clears where baseline also clears — no regression.
- **RC3/RC4** both refuse near-miss and wrong-doc — structural guard works on those poles.

**What would beat baseline:** semantic refusal on RC5 (not shipped). **What baseline misses:** independence demotion, transport propagation, forced-lie transcript — not scored on this 6-item set.

---

## Ablation — verify() switched off

```bash
python3 scripts/seed_document_cache.py
python3 scripts/eval_refusal_ablation.py
```

**Output this run (2026-08-30 UTC):**

```
Ablation:  5/6 = 0.833  95% CI [0.436, 0.978]
Shipping:  5/6 = 0.833  95% CI [0.436, 0.978]
Delta (shipping - ablation): +0
McNemar:   p=1.0000 (no discordant pairs — arms identical on every item)
FINDING: tied — verify() adds no delta on n=6.
RC5 substring trap: BOTH arms false-GREEN — semantic guard still missing.
```

**Finding:** ablation (locator only, no `verify()`) ties shipping on n=6. RC3 near-miss date still refuses because `StringLocator` never proposes a passage containing `29 October 2020` — verify() is not the mechanism that saves RC3 on this locator. The signature guard's measurable delta on this set is **zero**; RC5 false-GREEN persists in both arms.

---

## External anchor — live rightsstatements.org

```bash
python3 scripts/eval_external_anchor.py
```

Pages fetched at runtime from rightsstatements.org (not our fixtures). Labels EA1/EA2 mirror RC4/RC6.

**Output this run (2026-08-30 UTC):**

```
Baseline:  2/2 = 1.000  95% CI [0.342, 1.000]
Shipping:  2/2 = 1.000  95% CI [0.342, 1.000]
McNemar:   p=1.0000 (no discordant pairs — arms identical on every item)
FINDING: tied on external anchor — no measured delta.
```

---

## Docs count gate

```bash
python3 scripts/bench_check_docs.py
```

Re-derives all 9 suite counts against `docs/SUBMISSION-PACK-2026-08-29.md` — exit 1 if stale.

---

## Holdout frozen — before any tuning pass

```bash
python3 scripts/eval_holdout_frozen.py
```

**Output this run (2026-08-30 UTC):**

```
PASS — holdout matches FROZEN manifest; safe to score eval arms.
sha256: df578e315a49b67de7ee1348d7c9619bf1a8d485237ec52f214f6c5c878a42f9
```

Manifest: `fixtures/refusal-correctness/FROZEN.json` — changing `set.json` requires deliberate manifest update.

---

## Scorer symmetrical — judge from delivered output only

```bash
python3 scripts/seed_document_cache.py
python3 scripts/eval_scorer_symmetry.py
```

All arms emit the same public row (`SOURCED`/`UNSOURCED` + passage). One external judge — no internal GREEN/UNKNOWN enums.

**Output this run (2026-08-30 UTC):**

```
Baseline   2/6 = 0.333  95% CI [0.097, 0.700]
Shipping   3/6 = 0.500  95% CI [0.188, 0.812]
Ablation   3/6 = 0.500  95% CI [0.188, 0.812]
McNemar (shipping vs baseline, symmetric judge): p=1.0000 (b=0 c=1 discordant)
RC5 substring trap: shipping false-SOURCED under symmetric judge — documented engine limit.
FINDING: shipping=3 baseline=2 ablation=3
```

**Finding:** under symmetric judge (requires verified passage for SOURCED), baseline **loses** on RC1/RC2 because it never quotes. Shipping beats baseline by 1 item (RC6 only). RC5 still false-SOURCED in all substring arms — worst number unchanged.

---

## Honesty & limitations (worst numbers — do not bury)

| Metric | Worst arm | Value | Why it matters |
|--------|-----------|-------|----------------|
| Refusal accuracy (internal enum) | baseline = shipping | **5/6 = 0.833 tie** | Verifier adds zero delta on held-out set |
| Refusal accuracy (symmetric judge) | baseline | **2/6 = 0.333** | Naive substring cannot produce verified passages |
| RC5 substring trap | baseline + shipping + ablation | **false pass** | Document negates claim; terms appear nearby |
| Live compound sourcing | hosted compound-mini | **sourced=0 both runs** | Compounding proved; sourcing rate did not |
| Cross-subject offline | dust-bowl | **keys blocked locally** | Only offline reuse test runnable without keys |

---

## Checklist status (PRIOR LOSS gate)

- [x] Alternative arm named and run
- [x] Ablation with measured delta (delta=0; RC5 both false-GREEN)
- [x] External anchor — live rightsstatements.org (`scripts/eval_external_anchor.py`)
- [x] Holdout frozen (`scripts/eval_holdout_frozen.py` + `FROZEN.json`)
- [x] Scorer symmetrical (`scripts/eval_scorer_symmetry.py`)
- [x] Offline path with no API key
- [x] Wilson CI + McNemar (n=6)
- [x] Honesty carries worst number (symmetric baseline 2/6; RC5 false-SOURCED; live sourced=0)
