# RECEIPT — Night wave 2026-09-19 · cost gate + pack truth + BLOCKED compound + deploy prep

**Branch:** `cursor/night-wave-qwen-cost-pack-870b`  
**Slice:** ONE NOW in `hack.md` — Qwen cost gate (dated price card + always-silent null) · SUBMISSION-PACK re-measure · live compound BLOCKED · Oscar deploy prep only.

---

## SHIPPED

1. **Cost gate** — `scripts/eval_cost_gate.py` + `fixtures/price-card/parallel.json` (retrieved 2026-09-19 from https://www.parallel.ai/pricing) + `fixtures/billing/README.md` + `tests/test_cost_gate.py` (billing RED watched with `--require-billing` → exit 3).
2. **Null / baseline / shipping arms** on held-out refusal set — NULL always-refuse floor included so a result that embarrasses us can print.
3. **measure_compounding.py** now loads `PARALLEL_CALL` from the dated price card (stops carrying `$0.005`).
4. **SUBMISSION-PACK** truth refresh — public-repo lie fixed; controls dated 2026-09-19; stranger block adds `eval_cost_gate.py`; dictionary **239** after cold boot (not carried 265).
5. **BLOCKED live compound** — `docs/BLOCKED-live-compound-2026-09-19.md`.
6. **Deploy prep** — `docs/DEPLOY-PREP-2026-09-19.md` matching current `deploy.sh` (candidate, timeout 240, secrets only).
7. **Transcript** — `docs/RECEIPT-cost-gate-run-2026-09-19.txt`.

---

## VERIFIED (command → object)

| Claim | Command | Result |
|-------|---------|--------|
| Start gate | `python3 tests/test_watch_it_go_red.py` | **72 passed, 0 failed** |
| Pack suites | `python3 scripts/bench_check_docs.py` | **ALL 128/128 match** |
| Registry surface | `python3 tests/test_registry_surface.py -q` | **16/16** |
| Partner runtime | `python3 tests/test_partner_runtime.py` | **7/7** |
| Baseline eval | `python3 scripts/eval_refusal_baseline.py` | baseline **5/6**, shipping **6/6**, delta +1 |
| Ablation eval | `python3 scripts/eval_refusal_ablation.py` | ablation **5/6**, shipping **6/6**, delta +1 |
| Cost gate | `python3 scripts/eval_cost_gate.py` | NULL **3/6**, BASELINE **5/6**, SHIPPING **6/6**; A=$0.002 B=$0.001 @ Fast; billing RED |
| Billing RED control | `python3 scripts/eval_cost_gate.py --require-billing` | **exit 3** |
| Cost gate tests | `python3 tests/test_cost_gate.py -q` | **4/4 OK** |
| Offline compound | `python3 scripts/compound_exhibit_receipt.py` | A=**2**→B=**1**, corpus_hits_B=**2**, boundary GT A=**3** |
| Hosted health | `curl …/health` | revision `00028-hed`, **no** partner fields |
| Hosted clear | `curl -X POST …/clear` | **401** |
| Public repo | `gh api repos/Morkeeth/agent-science` | `visibility=public` |
| Dictionary size | `boot_registry.py` then `economics()['n']` | **239** (not 265) |

---

## WRONG / could not verify / left broken

1. **Billing checklist row still UNCHECKED** — price card is not an invoice. No Parallel/Gemini console export on this VM; `fixtures/billing/invoice.json` absent by design. Gate stays RED.
2. **Always-silent NULL did not beat shipping on accuracy** (3/6 < 6/6). The embarrassment tonight is cost-shaped (meter under-count; prior 5× Fast overstatement), not a null-beats-us accuracy table.
3. **parallel_calls under-count** — offline compound meters A=2 while fake-boundary ground-truth prints 3. Not fixed tonight; named in cost-gate FINDING. Pricing the meter understates true Search door spend.
4. **Live compound not run** — no `PARALLEL_API_KEY`, no workspace token; hosted clear 401. Offline receipt is authoritative.
5. **Live `/health` still stripped** — partner-admissibility fix remains undeployed on `00028-hed`. Deploy prep only; no `deploy.sh` executed.
6. **Hosted claim count / hit rate** — `/stats` and `/partners` return **303** under private-workspaces; could not re-derive the old hosted **265 / 0.80** at the live object. Local boot → **239**.
7. **`docs/STATUS.md` and film copy still say 265** in places — pack corrected; STATUS not fully scrubbed this slice (named so it cannot hide).
8. **McNemar on n=6** still not significant (baseline vs shipping p=1.0; null vs shipping p=0.25). Do not claim statistical victory.

---

## Findings worth keeping (could embarrass us)

- Prior `PARALLEL_CALL = 0.005` matched Search API **advanced** on the 2026-09-19 card, not default **fast** ($0.001) → **5×** overstatement if Fast was intended.
- Offline holdout cost is **$0 for every arm** — a cost gate that only scores RC1–RC6 cannot discriminate NULL/BASELINE/SHIPPING.
- Compound meter A=2 vs boundary ground-truth 3.
