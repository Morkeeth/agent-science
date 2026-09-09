# FINDING — offline compound exhibit broke on paraphrase reuse · 2026-09-09

**Status:** fixed in `fixtures/scripts/compound-mini-B.txt` + `scripts/compound_exhibit_receipt.py`.

## Object measured

```bash
python3 scripts/compound_exhibit_receipt.py
# before fix: A=2 B=3 corpus_hits=0 → exhibit FAILED (exit 3)
# after fix:  A=2 B=1 corpus_hits=2 → PASS (exit 0)
```

## What went wrong

Same-subject integrity (`f61635e`: reuse only for the same assertion) correctly refuses **paraphrase** reuse. The offline compound exhibit still fed Run B paraphrases of Run A claims, so:

- `corpus.recall` missed (different `claim_key`)
- Both overlapping claims re-spent Parallel → B parallel **rose**

The receipt number A=2→B=1 sitting in SUBMISSION-PACK was true under an older reuse rule and had not been re-run at the object on main after integrity landed. Side-branch fixes from 2026-09-05..08 never merged.

## Fix

Run B reuses the **exact** Run A assertion strings for the overlapping claims, then adds one new claim. That matches the product rule and restores A=2→B=1 with `corpus_hits=2`.

Baseline that still false-PASSes: `python3 scripts/eval_compound_baseline.py` (soft must_contain reuse).

## Lesson

A compound number sitting in a markdown file is not a control. Re-running the exhibit is the control.
