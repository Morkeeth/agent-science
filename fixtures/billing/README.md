# Billing invoice fixture (Oscar only)

`scripts/eval_cost_gate.py` watches this directory.

- **Absent `invoice.json` → BILLING RED.** That is the control. Do not tick
  hack.md "Cost from billing" until a real console export lands here.
- Price-card estimates live in `fixtures/price-card/parallel.json` and are a
  different object. A price card is not billing.

## Expected shape for `invoice.json`

```json
{
  "provider": "Parallel",
  "period_start": "YYYY-MM-DD",
  "period_end": "YYYY-MM-DD",
  "currency": "USD",
  "total": 0.0,
  "line_items": [
    {"sku": "search.fast", "quantity": 0, "unit_usd": 0.001, "amount_usd": 0.0}
  ],
  "price_card_retrieved_at": "must match or post-date fixtures/price-card/parallel.json",
  "exported_at": "ISO-8601",
  "source": "parallel.ai console export / CSV"
}
```

Never commit live API keys. Totals and quantities only.
