# FINDING — Offline compound exhibit went RED on re-run · 2026-09-10

**Status:** measured RED · fixed in `scripts/compound_exhibit_receipt.py` + fixtures

## What was measured

```bash
python3 scripts/compound_exhibit_receipt.py; echo EXIT:$?
```

Without a pipe (pipes to `tail`/`tee` hide the exit code — false green):

| Run A parallel | Run B parallel | corpus_hits B | EXIT |
|---------------:|---------------:|--------------:|-----:|
| 2 | 3 | 0 | **3** |

Committed receipt `docs/COMPOUND-EXHIBIT-2026-08-29.md` still claimed A=2→B=1, corpus_hits=2 (dated 2026-09-03). Re-deriving at the object falsified it.

## Root cause (opened the object)

Claim identity is the **full assertion** (`agent_science._claim_key` → `refusal_log.norm_term(text)`), not the `must_contain` anchor. Comment in code: *"Old anchor-keyed rows intentionally miss until re-evaluated."*

`compound-mini-B.txt` / `_OFFLINE_CLAIMS["B"]` paraphrased the two overlapping facts:

- A: `In 2012 the European Union passed Directive 2012/28/EU…`
- B: `Europe's answer was Directive 2012/28/EU — known as…`

Different wording → different keys → no corpus hit → Run B paid Parallel again for both, plus the new forty-percent claim → B=3.

This is the product integrity rule working. The exhibit was still shaped for the old anchor-key world.

## Naive baseline that would have passed

Reading the receipt file without re-running the script. Same class of failure as carrying numbers from a prompt.

## Fix

Overlapping facts in Run B use the **same assertion text** as Run A (exact reuse). The new British Library claim still forces Parallel. Exhibit proves compounding under current identity rules, not paraphrase-as-reuse.
