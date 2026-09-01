> **SUPERSEDED IN PART, 2026-08-31.** Every number below was true when it was read on
> 2026-08-30, and is kept as the record of that run. The RC5 rows are no longer the
> current state: the semantic guard closed RC5, so baseline/ablation 5/6 vs shipping
> **6/6**, delta **+1**, McNemar p=1.0000 (b=0, c=1 — a real delta where this file
> reports a tie, and still NOT significant at n=6). Re-run:
> `python3 scripts/eval_refusal_baseline.py` and `..._ablation.py`.
> Full record: `docs/FINDING-semantic-guard-2026-08-31.md`.

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

## Checklist status (PRIOR LOSS gate)

- [x] Alternative arm named and run
- [x] Ablation with measured delta (delta=+1 at n=6; RC5 discordant; McNemar p=1.0)
- [x] External anchor — live rightsstatements.org (`scripts/eval_external_anchor.py`)
- [x] Holdout frozen — `scripts/eval_holdout_frozen.py` + `HOLDOUT-MANIFEST.json`
- [x] Scorer symmetrical — `scripts/eval_scorer_symmetry.py`
- [x] Offline path with no API key
- [x] Wilson CI + McNemar (n=6)
- [x] Honesty carries worst number (baseline 5/6; RC5 false-SUPPORTED in baseline arm)
