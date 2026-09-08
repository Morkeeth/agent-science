# FINDING — Offline compound exhibit inverted · 2026-09-08

**Object:** `python3 scripts/compound_exhibit_receipt.py` on main before fixture fix

## Measured (before fix)

| Run A parallel | Run B parallel | corpus_hits B | exit |
|---:|---:|---:|---:|
| 2 | 3 | 0 | 3 |

Compounding inverted — B spent *more* Parallel than A.

## Cause (opened the object)

Same-subject integrity (`f61635e`, 2026-09-04) requires **exact assertion** text for corpus reuse. Offline Run B still used paraphrases of Run A's claims in `compound-mini-B.txt` and `_OFFLINE_CLAIMS["B"]`. Docs kept printing A=2→B=1 from earlier receipts.

## Fix (this branch)

- Overlapping B claims use identical A wording; British Library claim remains the new spend.
- Re-measure must be run at the object after the change.

## Why it matters

Partner track video beat is "second run costs less." A silent paraphrase fixture made the offline exhibit lie green in docs while the command was red.
