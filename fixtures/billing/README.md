# Billing fixtures

- `PRICE-CARD.json` — public Parallel price card snapshot (date + URL + verbatim span). Used only by the **baseline** arm of `scripts/eval_cost_from_billing.py`.
- `export.json` — **optional**. Operator drops a real billing export here (or sets `BILLING_EXPORT_PATH`). Without it the shipping arm must REFUSE.

Do not invent export rows. A missing export is the correct failure.
