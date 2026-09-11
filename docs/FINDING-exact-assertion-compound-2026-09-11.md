# FINDING — paraphrase is not compound · 2026-09-11

**Object opened:** `scripts/compound_exhibit_receipt.py` + `clearance/corpus.recall` + `agent_science._claim_key`  
**Not opened first (failure mode):** the Sep-3 receipt title that still said A=2→B=1 PASS.

## What happened

Re-running the offline compound exhibit on 2026-09-11 produced:

| Run A parallel | Run B parallel | corpus_hits B |
|---:|---:|---:|
| 2 | 3 | 0 |

Exit code 3. The SUBMISSION-PACK and cold-clone stranger path would have lied if we had carried the old receipt.

## Cause (at the engine, not the title)

After `176f5db` / `f61635e`, same-subject reuse requires **exact assertion** identity:

- `_claim_key` hashes `norm_term(full claim text)`, not the `must_contain` anchor.
- `corpus.recall(..., assertion=)` returns None when wording differs.

`compound-mini-A` and `compound-mini-B` (and the offline fixed claim lists) used **paraphrases** of the overlapping EU-directive claims. Different predicates → different keys → zero corpus hits → B searched three times.

## Fix shipped

Overlapping A/B claims now share **identical** assertion text; B adds one novel British Library claim. Re-run:

```bash
python3 scripts/compound_exhibit_receipt.py
# A=2 → B=1 · corpus_hits B=2 · exit 0
```

## Lesson for the judge pack

"Overlapping claim" in the sealed prediction means the **same assertion**, not the same CELEX number in different sentences. Film and Devpost copy that imply paraphrase compounding are wrong under current reuse rules.
