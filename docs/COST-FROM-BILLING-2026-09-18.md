# COST FROM BILLING — Qwen PRIOR LOSS gate

**Date:** 2026-09-18 08:31 UTC · **Commit:** `0f374aa`
**Fixtures:** `compound-mini-A.txt` → `compound-mini-B.txt` · subject `orphan-works-cost-gate`

## Price card (not an invoice)

| Field | Value |
|-------|-------|
| Source | `fixtures/price-cards/parallel-search-2026-09-18.md` |
| Fetched at (UTC) | **2026-09-18T08:20:49Z** |
| Shipping search mode | `advanced` (`find_sources` default) |
| Rate used | **$0.005** / request (= $5 / 1,000 `advanced` requests) |
| Turbo/fast (not used) | $0.001 / request |

## Invoice / billing API

- **Status:** `BLOCKED`
- **invoice_usd:** `None`
- **Reason / detail:** PARALLEL_API_KEY absent (env + ~/.config/keys/parallel.key)

This gate **does not** claim invoice truth without a Parallel billing response.
USD below is **price-card × meter** only.

## Arms · compound-mini (default cold-clone gate)

| Arm | Corpus shelf | A Parallel | B Parallel | Total Parallel | USD (card) | B corpus_hits |
|-----|--------------|----------:|----------:|---------------:|-----------:|--------------:|
| **Baseline** (naive always-search) | separate DBs | 2 | 3 | **5** | **$0.0250** | 0 |
| **Shipping** (shared subject shelf) | one DB | 2 | 1 | **3** | **$0.0150** | 2 |

**Delta (baseline − shipping):** +2 calls · $+0.0100 · shipping cheaper by 2 Parallel call(s), $0.0100 on price card (40% of baseline)

## Arms · powered-synthetic (larger n, still offline)

Fixed claim lists (~8 A / ~10 B exact-assertion overlaps). **Not** live `powered-A-law.txt` / `powered-B-archive.txt` Gemini extract (those need keys — BLOCKED on this VM).

| Arm | A Parallel | B Parallel | Total | USD (card) | B corpus_hits |
|-----|----------:|----------:|------:|-----------:|--------------:|
| Baseline | 8 | 10 | **18** | **$0.0900** | 0 |
| Shipping | 8 | 3 | **11** | **$0.0550** | 7 |

**Powered delta:** +7 calls · $+0.0350

## Honesty

- Gemini extract / locate USD: **not priced** (no dated Gemini price card fetched tonight).
- Absolute dollars even on powered-synthetic remain cents — shape and ratio matter more than the dollar printout at this fixture size.
- `measure_compounding.py` still hardcodes `PARALLEL_CALL = 0.005` without a fetch date — that file is **not** this gate; do not carry its number.

## Re-run

```bash
python3 scripts/eval_cost_from_billing.py
python3 scripts/eval_cost_from_billing.py --fetch-card   # refresh snapshot
```

