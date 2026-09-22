# QWEN EVAL GATE — artifact claims at object · 2026-09-22

**Gate item (PRIOR LOSS checklist):** *Every artifact claim measured at the submitted commit.*  
Previously unticked. This file + `scripts/eval_artifact_claims.py` closes it as a falsifiable measurement — not as a narrative.

**Companion:** `scripts/eval_null_arm.py` on the refusal-correctness holdout (false-SOURCED metric).

---

## Arms

| Arm | Behaviour |
|-----|-----------|
| **NULL** | Always `NOT_HELD` — refuse every artifact claim |
| **BASELINE** | Believe `doc_asserts` from the labelled set (what STATUS/SUBMISSION-PACK said) — **no object open** |
| **OBJECT** | Probe hosted URL / local suite / GitHub API / compound receipt at runtime |

Gold labels in `fixtures/artifact-claims/set.json` were written **after** opening each object on 2026-09-22. Re-probe must match; AC10 planted key must stay `NOT_HELD`.

---

## Run (re-derive — do not carry these numbers)

```bash
python3 scripts/eval_artifact_claims.py
python3 tests/test_artifact_claims.py          # includes RED control
python3 scripts/eval_null_arm.py               # offline refusal set
```

**Output this run (2026-09-22 UTC):**

```
ARTIFACT-CLAIMS
NULL:      6/10 = 0.600  95% CI [0.313, 0.832]
BASELINE:  4/10 = 0.400  95% CI [0.168, 0.687]
OBJECT:    10/10 = 1.000  95% CI [0.722, 1.000]
Delta (null - baseline): +2
False-HELD rate BASELINE: 6/6
FINDING: NULL beats BASELINE — trusting STATUS/SUBMISSION-PACK without opening
the object is worse than refusing every claim on this set.

NULL-ARM (refusal-correctness)
NULL 3/6 · BASELINE 5/6 · SHIPPING 6/6
False-SOURCED: NULL 0/3 · BASELINE 1/3 · SHIPPING 0/3
```

---

## Finding (honest)

- The submit-path embarrassment tonight is **documentation honesty**, not eval rigor on n=6.
- Six doc-asserted hosted/checklist claims were false at the object (AC1–AC5, AC10).
- Offline controls (AC6–AC9) still hold when measured.
- Shipping refusal engine beats null on accuracy; on **false-SOURCED** it ties null and beats baseline (RC5).

**What would make baseline win again:** Oscar deploy restoring public partner `/health` + `/partners`, and STATUS/SUBMISSION-PACK revised so `doc_asserts` match — then re-label the set deliberately (do not silently edit gold without a new `labelled_at`).
