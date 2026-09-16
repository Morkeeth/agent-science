# FINDING — offline compound exhibit exit 3 · 2026-09-16

**Object:** `python3 scripts/compound_exhibit_receipt.py`  
**Measured:** Run A `parallel_calls=2`, Run B `parallel_calls=3`, `corpus_hits B=0`, exit **3**.

## Why

`clearance/refusal_log.py` reuses only **exact assertions** (`claim_key` /
`search_registry` docstring: *"reuse a verdict only for the same assertion"*).
The offline compound B arm was feeding **paraphrases** of A's claims
("Europe's answer was Directive…" vs "In 2012 the European Union passed…").
Those are different `claim_key`s → no corpus/log hit → B paid Parallel again for
both overlapping facts plus the new BL claim.

This is the product spine working as designed. The exhibit fixtures were the defect.

## Fix

`scripts/compound_exhibit_receipt.py` `_OFFLINE_CLAIMS["B"]` now reuses A's exact
assertion strings for the two overlapping facts, and keeps the British Library
claim as the only new Parallel spend. Done-when:

```bash
python3 scripts/compound_exhibit_receipt.py >/tmp/compound.out; echo exit:$?
# expect exit 0 · A parallel > B parallel · corpus_hits B ≥ 1
grep -E 'parallel_calls|corpus_hits B' /tmp/compound.out | head -5
```
