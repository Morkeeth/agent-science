# COMPOUND EXHIBIT — orphan-works A/B

**Date:** 2026-08-29 21:58 UTC · **Subject:** `orphan-works` · **Mode:** live
**Fixtures:** `documentary-orphan-works.txt` → `documentary-orphan-works-B.txt`

## Quantified compounding

| Run A parallel_calls | Run B parallel_calls | delta | corpus_hits B |
|---:|---:|---:|---:|
| 11 | 9 | +2 | 5 |

- Run B parallel < Run A: **yes**
- corpus_hits B ≥ 1: **yes**

## Live chain

Two consecutive `agent_science.clear_script` runs on one corpus DB with Gemini extract + Parallel search.

## Registry backfill

`python3 clear_corpus.py research-corpus --backfill` → **176 rows** (29 SOURCED + proven-unprovable refusals) in `cache/refusal_log.db`

## Controls

```
PASS  test_every_query_becomes_a_browsable_row
PASS  test_miss_is_honest_not_cleared
PASS  test_serve_page_renders_without_format_keyerror
PASS  test_sourced_returns_verbatim_span
PASS  test_unknown_carries_named_refusal

5/5 passed
```

```
PASS  test_not_gameable_reuse_carries_the_original_verdict_both_poles
PASS  test_second_subject_reuses_the_log_and_spends_no_parallel_call

2/2 passed
```

## Related receipts

- `python3 review/corpus_compound_receipt.py` — rights-leg 50/50 reuse, zero network on Run 2
- `docs/SECOND-SUBJECT-RECEIPT-2026-08-29.md` — dust-bowl cross-subject reuse
