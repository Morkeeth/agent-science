# COMPOUND EXHIBIT — orphan-works A/B

**Date:** 2026-09-05 00:14 UTC · **Subject:** `orphan-works` · **Mode:** offline
**Fixtures:** `compound-mini-A.txt` → `compound-mini-B.txt`

## Quantified compounding

| Run A parallel_calls | Run B parallel_calls | delta | corpus_hits B |
|---:|---:|---:|---:|
| 2 | 1 | +1 | 2 |

- Run B parallel < Run A: **yes**
- corpus_hits B ≥ 1: **yes**

## Offline simulation (no Gemini/Parallel keys on this VM)

Network boundaries faked; verdict rules run for real:

- GeminiExtractor → fixed claim lists from compound-mini-A/B (not live extraction)
- search.find_sources → scripted primary URLs + honest call counter
- instruments.document → fixture bodies (no HTTP)
- StringLocator (DEFAULT) + verify + independence — real shipping rules

Ground-truth Parallel calls at fake boundary (Run A only): `3`

## Registry backfill

`python3 clear_corpus.py research-corpus --backfill` → **0 rows** (29 SOURCED + proven-unprovable refusals) in `cache/refusal_log.db`

## Controls

```
PASS  test_a_filtered_total_counts_the_SET_not_the_PAGE
PASS  test_a_full_span_is_not_flagged_thin
PASS  test_every_query_becomes_a_browsable_row
PASS  test_every_refusal_says_what_would_settle_it
PASS  test_miss_is_honest_not_cleared
PASS  test_sourced_returns_verbatim_span
PASS  test_the_curve_never_renders_without_its_provenance
PASS  test_the_separation_note_survives_a_non_zero_reuse_counter
PASS  test_the_shelf_shows_a_refusal_in_the_same_column_as_evidence
PASS  test_the_template_is_never_run_through_format
PASS  test_thin_evidence_is_counted_and_shown_not_hidden
PASS  test_thin_total_counts_every_sourced_row_not_just_this_page
PASS  test_truths_dashboard_page_renders
PASS  test_unknown_carries_named_refusal
PASS  test_visibility_json_panel_shape
PASS  test_visibility_ui_renders_transparency

16/16 passed
```

```
PASS  test_not_gameable_reuse_carries_the_original_verdict_both_poles
PASS  test_second_subject_reuses_support_and_retries_unsettled_claim

2/2 passed
```

## Related receipts

- `python3 review/corpus_compound_receipt.py` — rights-leg 50/50 reuse, zero network on Run 2
- `docs/SECOND-SUBJECT-RECEIPT-2026-08-29.md` — dust-bowl cross-subject reuse
