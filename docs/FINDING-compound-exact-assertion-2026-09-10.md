---
date: 2026-09-10
status: OPEN → closed by fixture realignment tonight (paraphrase arm kept as counter-example)
measured_by: `python3 scripts/compound_exhibit_receipt.py`
---

# Offline compound exhibit failed under exact-assertion reuse

## What was claimed

`docs/COMPOUND-EXHIBIT-2026-08-29.md` (last green 2026-09-03) and SUBMISSION-PACK said
offline compound-mini A/B delivered **A=2 → B=1 Parallel · corpus_hits B=2**.

## What ran tonight (before fix)

```bash
python3 scripts/compound_exhibit_receipt.py
# exit 3
# A parallel_calls=2 · B parallel_calls=3 · corpus_hits B=0
```

Overlapping claims in `compound-mini-B.txt` were **paraphrases**, not identical
assertions. After commits `176f5db` / `f61635e` (2026-09-04), corpus recall and log
lookup bind the **complete assertion**. Different wording → different slot → search
again. That is intentional integrity, not a flaky counter.

| Run | C1 wording | C2 wording | Expected under old term-key | Measured under exact assertion |
|-----|------------|------------|-----------------------------|--------------------------------|
| A | "In 2012 the European Union passed Directive…" | "Member states had until 29 October 2014…" | store | store |
| B | "Europe's answer was Directive…" (paraphrase) | "deadline for national transposition…" (paraphrase) | reuse ×2 | **search ×2** + new claim |

## What this does not mean

- Same-subject **identical** wording still compounds — `tests/test_same_subject_integrity.py` **8/8**.
- Rights-leg identical-item reuse still holds — `python3 review/corpus_compound_receipt.py` → 0/50 then 50/50.
- Hosted sealed A=1→B=0 (2026-08-31) is a different object; not re-run tonight (no keys; hosted `/search` returns **303** under private-workspaces).

## Fix chosen tonight

Realign `compound-mini-B.txt` overlapping lines to the **exact** A assertions, keep the
new British Library claim as the only fresh search. Re-run the receipt. Keep a
**paraphrase counter-arm** in `scripts/eval_cost_baseline.py` so the old fixture shape
cannot silently look green again.

## WRONG (before this night)

Pack and stranger docs still printed A=2→B=1 after exact-assertion landed — a carried
number from 2026-09-03, not re-derived at the object.
