# COST FROM BILLING — Qwen PRIOR LOSS gate

**Date:** 2026-09-18 08:24 UTC · **Commit:** `d56aeb8`
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

## Arms

| Arm | Corpus shelf | A Parallel | B Parallel | Total Parallel | USD (card) | B corpus_hits |
|-----|--------------|----------:|----------:|---------------:|-----------:|--------------:|
| **Baseline** (naive always-search) | separate DBs | 2 | 3 | **5** | **$0.0250** | 0 |
| **Shipping** (shared subject shelf) | one DB | 2 | 1 | **3** | **$0.0150** | 2 |

**Delta (baseline − shipping):** +2 calls · $+0.0100 · shipping cheaper by 2 Parallel call(s), $0.0100 on price card (40% of baseline)

## Honesty

- Gemini extract / locate USD: **not priced** (no dated Gemini price card fetched tonight).
- Absolute dollars at compound-mini n are tiny; the gate tests *shape* (shared shelf beats re-search), not production budget.
- `measure_compounding.py` still hardcodes `PARALLEL_CALL = 0.005` without a fetch date — that file is **not** this gate; do not carry its number.

## Re-run

```bash
python3 scripts/eval_cost_from_billing.py
python3 scripts/eval_cost_from_billing.py --fetch-card   # refresh snapshot
```

