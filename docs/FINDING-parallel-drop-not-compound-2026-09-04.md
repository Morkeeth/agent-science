# FINDING — Parallel drop ≠ compound · search cache · 2026-09-04

**Measured at object.** Do not cite without re-running `python3 scripts/partner_honesty_exhibit.py`.

## What we believed

Pitch and sealed prediction language treated **fewer `parallel_calls` on Run B** as the compound exhibit. Soft verify gates used `B_parallel ≤ A_parallel` plus `corpus_hits ≥ 1`.

## What the object showed

### 1. Soft green, sealed red

`partner_honesty_exhibit.py` stamp **2026-09-04T00:15:26Z**:

| Arm | A Parallel | B Parallel | B corpus_hits |
|-----|----------:|----------:|--------------:|
| Shipping (same subject) | 1 | 1 | 1 |
| Naive (different subjects) | 1 | 1 | 0 |

- Soft gate: **PASS** (`B ≤ A` and hits≥1)
- Sealed prediction (`B < A`): **FAIL** — class `SOFT_PASS_FLAT`
- Mechanism: Run B extracted **3** claims vs A's **2**; the new claim paid for one Parallel call while the overlap hit the corpus.

Earlier the same night, `verify_partners_hosted.sh` compound-fresh also printed A=1→B=1 hits=1 (soft pass).

### 2. Naive arm also "drops" Parallel

Stamp **2026-09-04T00:12:42Z** (distinct tokens, different subjects):

| Arm | A→B Parallel | B hits |
|-----|-------------:|-------:|
| Shipping | 2→1 | 1 |
| Naive | 2→1 | 0 |

Naive matched shipping's Parallel delta with **zero** corpus hits. Cause: `clearance/search.py` caches Parallel results in `cache/searches.json` by claim text — **global across subjects**. Overlapping claim text on Run B hits search cache → no live Parallel for that claim → Parallel count drops without a corpus shelf.

### 3. Contaminated baseline (caught and fixed)

First naive attempt reused shipping's claim text → NAIVE_A `parallel_calls=0` via search cache. Exhibit now forces **distinct tokens** for naive; first-run contamination is documented in the receipt.

## What is still true

- Sealed long-run A=1→B=0 with hits=1 remains a real hosted measure (`docs/SEALED-PREDICTION-2026-08-31.md`).
- Shipping still beats naive on **`corpus_hits`** (1 vs 0) when the shelf works.
- Partners (Vertex, Parallel, Cloud Run, ADK) are on the `/clear` path.

## Pitch / video correction

Lead with **`corpus_hits` on repeat subject**. Treat Parallel drop as supporting when sealed holds; never as the only proof. Soft verify alone is not the sealed claim.

## Commands

```bash
python3 scripts/partner_honesty_exhibit.py
bash scripts/verify_partners_hosted.sh   # prints COMPOUND_CLASS soft vs sealed
```
