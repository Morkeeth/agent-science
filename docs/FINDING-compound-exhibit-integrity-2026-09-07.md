# FINDING — Offline compound exhibit broken since assertion-integrity · 2026-09-07

**Status:** RED found by re-running the object · fixture fixed to match integrity contract

## What was measured

```bash
python3 scripts/compound_exhibit_receipt.py; echo EXIT:$?
```

Before fixture fix (this night, main tree behavior):

| Run A parallel | Run B parallel | corpus_hits B |
|---:|---:|---:|
| 2 | 3 | 0 |

Script exit code **3** (failure). Docs still carried the 2026-09-03 pass numbers until re-run.

## Root cause (opened the object, not the title)

`f61635e` (2026-09-04) requires **exact assertion** for same-subject corpus/log reuse
(`tests/test_same_subject_integrity.py`). Offline Run B used paraphrases of Run A's claims
in `compound-mini-B.txt` / `_OFFLINE_CLAIMS["B"]`. Those no longer hit the corpus, so every
B claim called Parallel again — compounding inverted.

## Fix

- `fixtures/scripts/compound-mini-B.txt` — overlapping claims use **identical** A wording;
  British Library claim remains the new spend.
- `_OFFLINE_CLAIMS["B"]` in `scripts/compound_exhibit_receipt.py` aligned the same way.

Integrity tests unchanged. Paraphrase is not silent reuse.

## Re-measure after fix

```bash
python3 scripts/compound_exhibit_receipt.py; echo EXIT:$?
```

**Result 2026-09-07:** A=**2** → B=**1** Parallel · corpus_hits B=**2** · exit **0**
