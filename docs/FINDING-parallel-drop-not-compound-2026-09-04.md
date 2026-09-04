# FINDING — Parallel drop ≠ same-subject compound · 2026-09-04

**Measured at object.** Do not cite without re-running `python3 scripts/partner_honesty_exhibit.py`.

**Correction:** an earlier draft of this finding blamed Parallel **search-result cache**
for naive-arm Parallel drops. That was a nearer proxy. Re-measure with `log_hits` and
`parallel_api_calls` on the gap report shows the naive drop is **cross-subject log
reuse**. Search cache is real (`parallel_api_calls` can be &lt; `parallel_calls`) but was
not the mechanism for the naive Parallel *claim-path* drop.

---

## What we believed

Pitch language treated **fewer `parallel_calls` on Run B** as the compound exhibit.
Soft verify used `B_parallel ≤ A_parallel` plus `corpus_hits ≥ 1`.

## What the object showed

### 1. Soft green, sealed red (repeatable tonight)

| Stamp (UTC) | A→B Parallel | B corpus_hits | Class |
|-------------|-------------:|--------------:|-------|
| 00:06 verify_partners | 1→1 | 1 | SOFT_PASS_FLAT |
| 00:15 honesty | 1→1 | 1 | SOFT_PASS_FLAT |
| 00:22 honesty | 1→1 | 1 | SOFT_PASS_FLAT |

Mechanism (00:22 SHIP_B): `claims_extracted=3` vs A's 2 — new claim pays one
`parallel_calls` while overlap hits corpus (`corpus_hits=1`) and/or log
(`log_hits=1`). Soft gate PASS; sealed `B < A` FAIL.

### 2. Naive Parallel drop = log_hits, not corpus

Stamp **2026-09-04T00:22:38Z** (distinct tokens, different subjects):

| Arm | A Parallel | B Parallel | B corpus | B log_hits | A/B API calls |
|-----|----------:|----------:|---------:|-----------:|---------------|
| Shipping | 1 | 1 | 1 | 1 | 1 / 0 |
| Naive | 2 | 1 | 0 | **2** | 2 / 1 |

Naive dropped Parallel 2→1 with **zero** corpus hits because `log_hits=2` —
cross-subject refusal-log reuse on the overlapping claim terms. That is a real
product feature (fleet compounding), but it is **not** the same-subject shelf
demo. Film **`corpus_hits`** for same-subject compound; say **log reuse** when
Parallel drops across subjects.

### 3. Search cache is still real (secondary)

SHIP_B 00:22: `parallel_calls=1` but `parallel_api_calls=0` → cache gap 1.
Receipts already log `cache_hit` in `cache/search_receipts.jsonl`. Do not collapse
cache, log, and corpus into one "Parallel drop" story.

### 4. Contaminated first naive baseline (caught)

First naive attempt reused shipping claim text → NAIVE_A `parallel_calls=0` via
search/log warm paths. Exhibit now forces **distinct tokens**; contamination is
in the receipt.

## What is still true

- Sealed long-run A=1→B=0 with hits=1 remains a real hosted measure
  (`docs/SEALED-PREDICTION-2026-08-31.md`).
- Shipping still shows **`corpus_hits ≥ 1`** on repeat subject when the shelf works.
- Partners (Vertex, Parallel, Cloud Run, ADK) are on the `/clear` path.

## Pitch / video correction

Lead with **`corpus_hits` on repeat subject**. Treat Parallel drop as supporting
when sealed holds. When Parallel drops with `corpus_hits=0`, read **`log_hits`**
before claiming compound.

## Commands

```bash
python3 scripts/partner_honesty_exhibit.py
# look for log_hits + parallel_api_calls on each arm
bash scripts/verify_partners_hosted.sh   # prints COMPOUND_CLASS soft vs sealed
```
