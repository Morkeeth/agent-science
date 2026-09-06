# FINDING — offline compound exhibit failed under exact-assertion reuse · 2026-09-06

**Object:** `python3 scripts/compound_exhibit_receipt.py` (no keys)  
**Not trusted:** the prior receipt table claiming A=2→B=1 without re-running.

---

## What failed (command output)

Re-run 2026-09-06 before the fixture fix:

| Run A parallel_calls | Run B parallel_calls | corpus_hits B |
|---:|---:|---:|
| 2 | 3 | 0 |

Exit code **3** from `compound_exhibit_receipt.py` (exhibit failed).

At the clear path: Run B claims had `reused_from=None`, `corpus_hits=0`, `log_hits=0`. The refusal log held GREEN rows for term `directive 2012/28/eu` under A's wording, but B's paraphrases hashed to different `claim:` slots (`clearance/refusal_log.py` `claim_key` — exact assertion identity).

## Why (object, not title)

`refusal_log` documents the rule: *Only an identical supported or refuted assertion may short-circuit a fresh search. Wording variants remain retrieval candidates until independently verified.*

`tests/test_cross_subject_reuse.py` already uses **identical** assertions across productions. The offline compound-mini **B** script still used paraphrases (`Europe's answer was Directive…`), so after exact-assertion reuse landed, the exhibit silently stopped measuring compounding while the markdown receipt from 2026-09-03 still said pass.

## Fix shipped this wave

- `fixtures/scripts/compound-mini-B.txt` — overlapping sentences identical to A; third claim remains new.
- `scripts/compound_exhibit_receipt.py` `_OFFLINE_CLAIMS["B"]` — same identity rule.

Re-run after fix must show A parallel > B parallel and `corpus_hits B ≥ 1`. Paraphrase compounding remains **out of scope** until a verified semantic-identity layer exists (not invented tonight).

## Embarrassing lesson

Pack and pitch still sold "overlapping claim" compounding. Under current code, overlap means **exact assertion**, not topical paraphrase. Carrying the old A=2→B=1 number without re-running the receipt was the failure mode this night exists to catch.
