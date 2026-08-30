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
Baseline accuracy: 5/6 = 0.833
Shipping accuracy: 5/6 = 0.833
Delta (shipping - baseline): +0
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
Ablation accuracy: 5/6 = 0.833
Shipping accuracy: 5/6 = 0.833
Delta (shipping - ablation): +0
RC5 substring trap: BOTH arms false-GREEN — semantic guard still missing.
```

**Finding:** ablation (locator only, no `verify()`) ties shipping on n=6. RC3 near-miss date still refuses because `StringLocator` never proposes a passage containing `29 October 2020` — verify() is not the mechanism that saves RC3 on this locator. The signature guard's measurable delta on this set is **zero**; RC5 false-GREEN persists in both arms.

---

## Docs count gate

```bash
python3 scripts/bench_check_docs.py
```

Re-derives all 9 suite counts against `docs/SUBMISSION-PACK-2026-08-29.md` — exit 1 if stale.

---

## Checklist status (PRIOR LOSS gate)

- [x] Alternative arm named and run
- [x] Ablation with measured delta (delta=0; RC5 both false-GREEN)
- [ ] External anchor dataset we did not build
- [x] Offline path with no API key
- [x] Honesty carries worst number (tie + RC5 false-GREEN both arms)
