# eval/ — falsifiable gates with baseline arms

This directory exists because the Qwen loss retro found **no top-level `eval/`** on our
submission tag while the winner had one. Each gate here names an **alternative arm**
(what a competent team builds without this repo), runs both on the **same held-out
inputs**, and writes a receipt with the worst number in plain sight.

## Gates

| Gate | Script | External anchor | Offline? |
|------|--------|-----------------|----------|
| Refusal correctness | `eval/refusal_correctness_gate.py` | `fixtures/refusal-correctness/set.json` | yes |

Three arms: **BASELINE** (naive substring, no verify) · **ABLATION** (StringLocator, verify off) · **SHIPPING** (locator + verify).

## Stranger path (no API key)

```bash
python3 scripts/seed_test_cache.py          # once after clone
python3 eval/refusal_correctness_gate.py    # baseline vs shipping receipt
python3 tests/test_registry_surface.py -q   # registry controls
python3 scripts/compound_exhibit_receipt.py # offline compound A/B receipt
```

Receipts land beside the scripts (`eval/RECEIPT-*.md`, `docs/COMPOUND-EXHIBIT-*.md`).
