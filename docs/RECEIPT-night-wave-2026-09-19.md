# RECEIPT — Night wave 2026-09-19 · cost gate + pack truth + BLOCKED compound + deploy prep

**Branch:** `cursor/night-wave-qwen-cost-pack-870b`  
**Slice:** ONE NOW in `hack.md` — Qwen cost gate (dated price card + always-silent null) · SUBMISSION-PACK re-measure · live compound BLOCKED · Oscar deploy prep only.

---

## SHIPPED

1. **Cost gate** — `scripts/eval_cost_gate.py` + `fixtures/price-card/parallel.json` (retrieved 2026-09-19 from https://www.parallel.ai/pricing) + `fixtures/billing/README.md` + `tests/test_cost_gate.py` (billing RED watched with `--require-billing` → exit 3).
2. **Null / baseline / shipping arms** on held-out refusal set — NULL always-refuse floor included so a result that embarrasses us can print.
3. **measure_compounding.py** now loads `PARALLEL_CALL` from the dated price card (stops carrying `$0.005`).
4. **Compound receipt honesty** — per-run `find_sources` boundary counters; retracted the mislabeled "Run A only" total; cost gate prices the Search door, not `parallel_calls`.
5. **SUBMISSION-PACK** truth refresh — public-repo lie fixed; controls dated 2026-09-19; stranger block adds `eval_cost_gate.py`; dictionary **239** after cold boot (not carried 265).
6. **BLOCKED live compound** — `docs/BLOCKED-live-compound-2026-09-19.md`.
7. **Deploy prep** — `docs/DEPLOY-PREP-2026-09-19.md` matching current `deploy.sh` (candidate, timeout 240, secrets only).
8. **Transcript** — `docs/RECEIPT-cost-gate-run-2026-09-19.txt`.

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
| Cost gate | `python3 scripts/eval_cost_gate.py` | NULL **3/6**, BASELINE **5/6**, SHIPPING **6/6**; door A=$0.001 B=$0.002; billing RED |
| Billing RED control | `python3 scripts/eval_cost_gate.py --require-billing` | **exit 3** |
| Cost gate tests | `python3 tests/test_cost_gate.py -q` | **4/4 OK** |
| Offline compound | `python3 scripts/compound_exhibit_receipt.py` | parallel_calls A=**2**→B=**1**; find_sources A=**1**→B=**2** |
| Hosted health | `curl …/health` | revision `00028-hed`, **no** partner fields |
| Hosted clear | `curl -X POST …/clear` | **401** |
| Public repo | `gh api repos/Morkeeth/agent-science` | `visibility=public` |
| Dictionary size | `boot_registry.py` then `economics()['n']` | **239** (not 265) |

---

## WRONG / could not verify / left broken

1. **Billing checklist row still UNCHECKED** — price card is not an invoice. No Parallel/Gemini console export on this VM; `fixtures/billing/invoice.json` absent by design. Gate stays RED.
2. **Always-silent NULL did not beat shipping on accuracy** (3/6 < 6/6). Embarrassment tonight is cost-shaped.
3. **Almost published a false finding** — early read of "boundary GT A=3 vs meter A=2" trusted the receipt title "Run A only". Object was A+B total. Retracted after opening the counter. Classic name-vs-object failure.
4. **Real finding kept:** `parallel_calls` (2→1) is not Search-$ compounding. Door is find_sources **1→2** on the same offline fixture → priced Fast spend **−100%** (B costs more). Compound exhibit still seals on the claim counter; that is not a Parallel invoice story.
5. **Live compound not run** — no `PARALLEL_API_KEY`, no workspace token; hosted clear 401. Offline receipt is authoritative.
6. **Live `/health` still stripped** — partner-admissibility fix remains undeployed on `00028-hed`. Deploy prep only; no `deploy.sh` executed.
7. **Hosted claim count / hit rate** — `/stats` and `/partners` return **303** under private-workspaces; could not re-derive the old hosted **265 / 0.80** at the live object. Local boot → **239**.
8. **Film copy / some docs may still say 265** — pack + STATUS hosted table corrected; not every demo script scrubbed.
9. **McNemar on n=6** still not significant. Do not claim statistical victory.

---

## Findings worth keeping (could embarrass us)

- Prior `PARALLEL_CALL = 0.005` matched Search API **advanced** on the 2026-09-19 card, not default **fast** ($0.001) → **5×** overstatement if Fast was intended.
- Offline holdout cost is **$0 for every arm** — a cost gate that only scores RC1–RC6 cannot discriminate NULL/BASELINE/SHIPPING.
- Offline compound **claim-counter win** (2→1) is a **Search-door loss** (1→2) on this fixture when priced from `find_sources`.
