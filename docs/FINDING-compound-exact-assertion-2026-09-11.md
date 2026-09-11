# FINDING — offline compound exhibit broken under exact-assertion reuse

**Date:** 2026-09-11 · **Object:** `python3 scripts/compound_exhibit_receipt.py`  
**Measured:** Run A `parallel_calls=2` · Run B `parallel_calls=3` · `corpus_hits B=0` · exit 3

## What docs claimed

SUBMISSION-PACK and older receipts: offline compound A=**2**→B=**1** Parallel with
`corpus_hits≥1`.

## What the object said (re-derived)

```bash
env -u PARALLEL_API_KEY -u GEMINI_API_KEY python3 scripts/compound_exhibit_receipt.py
```

| Run A parallel | Run B parallel | corpus_hits B |
|---------------:|---------------:|--------------:|
| 2 | 3 | 0 |

## Why

Commit `f61635e` made `corpus.recall` require `norm_term(assertion) ==
norm_term(stored subject_title)`. Compound-mini B **paraphrased** the overlapping
claims ("Europe's answer was Directive…" vs "In 2012 the European Union passed…").
Under the constitution, different wording is a different assertion — so B correctly
pays Parallel again. The old exhibit was measuring silent paraphrase reuse, which
the product must not do.

`_claim_key` already hashes the full assertion (not the must_contain anchor), so
even a shared key path cannot equate paraphrases.

## Fix direction

Keep exact-assertion reuse. Change the **exhibit fixtures** so overlapping claims
share **verbatim** text; B adds only a genuinely new claim (forty percent). That
proves compounding without weakening the refuse-paraphrase spine.

## Naive vs shipping

| Arm | Behavior |
|-----|----------|
| Naive (old exhibit) | Paraphrase B → false compound green under pre-f61635e recall |
| Shipping (constitution) | Paraphrase B → corpus_hits 0 (honest) |
| Shipping exhibit (fixed fixtures) | Exact overlap + one new claim → Parallel drop + corpus_hits≥1 |
