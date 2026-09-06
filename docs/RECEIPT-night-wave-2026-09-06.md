# RECEIPT — night wave 2026-09-06 · Sep 9 submit-path truth

**Slice:** Qwen cost-from-billing gate + hosted stranger path at object + SUBMISSION-PACK refresh + offline compound exact-assertion fix + deploy prep (no deploy)  
**Branch:** `cursor/night-wave-submit-truth-2d54`  
**Keys on VM:** PARALLEL missing · GEMINI missing → live compound **BLOCKED**

---

## SHIPPED

1. **Cost-from-billing gate** — `fixtures/billing/PRICE-CARD.json` (fetched from https://parallel.ai/pricing, Advanced Search $5/1K) + `scripts/eval_cost_from_billing.py`  
   - Baseline invents USD from price card × receipt Parallel counts  
   - Shipping **REFUSES** without `fixtures/billing/export.json` / `BILLING_EXPORT_PATH`
2. **Hosted stranger-path probe** — `scripts/probe_hosted_stranger_path.py` (+ `--self-test` RED/GREEN/outage control)  
   - Live URL **RED**: `mode=private-workspaces`, paths 303→login
3. **FINDING** — `docs/FINDING-hosted-stranger-path-2026-09-06.md`
4. **Offline compound regression found + fixed** — paraphrased mini-B stopped compounding under exact-assertion reuse (A=2→B=3, corpus_hits=0). Fixture + extractor aligned to identical overlapping assertions. Finding: `docs/FINDING-offline-compound-exact-assertion-2026-09-06.md`
5. **SUBMISSION-PACK truth refresh** — public-repo checkbox corrected (public since 2026-08-22); hosted try-it marked RED; controls **128/128**; stranger block stays offline
6. **`new_user_trial.sh`** — honest exit 2 BLOCKED on private-workspaces (no KeyError false crash)
7. **Deploy prep** — `docs/DEPLOY-PREP-2026-09-06.md` matching current private-workspace `deploy.sh` (Oscar only; no deploy run)
8. **`full_gate.sh`** — cost billing + stranger probe; exit **2** `OFFLINE OK · HOSTED BLOCKED` instead of false FULL GATE OK
9. **PeriodCheck field at objects** — `docs/FINDING-periodcheck-object-2026-09-06.md` (2576 LOC · 13/13 live-eval · hosted UI 200)

---

## VERIFIED (command at object)

```bash
git pull && python3 tests/test_watch_it_go_red.py 2>&1 | tail -3
# 72 passed, 0 failed

python3 scripts/eval_cost_from_billing.py
# BASELINE invented $0.0350 from 7 Parallel calls × $0.005
# SHIPPING REFUSE · billing_export_missing

python3 scripts/probe_hosted_stranger_path.py --self-test
# SELF-TEST PASS (RED private · GREEN public · RED outage)

python3 scripts/probe_hosted_stranger_path.py
# HOSTED STRANGER PATH RED · mode=private-workspaces · /search 303→login
# exit 1

bash scripts/new_user_trial.sh
# BLOCKED: hosted mode='private-workspaces' revision='agent-science-00026-zel'
# exit 2

python3 scripts/bench_check_docs.py
# ALL 128/128 match SUBMISSION-PACK

python3 tests/test_registry_surface.py -q
# 16/16 passed

python3 scripts/eval_verify_holdout.py
# HOLDOUT OK — 4 files match MANIFEST

python3 scripts/eval_scorer_symmetry.py
# Baseline 5/6 vs Shipping 6/6; RC5 discordant

python3 scripts/eval_refusal_baseline.py && python3 scripts/eval_refusal_ablation.py
# baseline 5/6 vs shipping 6/6; ablation 5/6 vs shipping 6/6; delta +1 each

python3 scripts/compound_exhibit_receipt.py
# exit 0 · A=2 → B=1 Parallel · corpus_hits B=2
# (pre-fix re-run exited 3 with A=2→B=3 — see FINDING)

bash scripts/full_gate.sh
# === FULL GATE OFFLINE OK · HOSTED BLOCKED === (exit 2)
# cost gate + stranger probe wired; long_run skipped on RED

# PeriodCheck at objects (clone + live-evaluation.json + hosted curl):
# Python LOC 2576 · live-eval 13/13 · hosted UI HTTP 200
# docs/FINDING-periodcheck-object-2026-09-06.md

test -n "$PARALLEL_API_KEY" || test -f ~/.config/keys/parallel.key; echo $?
# 1 — missing
```

---

## BLOCKED

**Live compound exhibit (orphan-works A/B on hosted):**

```bash
# Keys missing on this VM
# AND unauthenticated POST /clear → 401 on private-workspaces revision
```

Offline `compound_exhibit_receipt.py` is authoritative for stranger/no-key path. Hosted re-seal requires Oscar workspace auth + keys.

**Orphan-works full script:** prior 504/503 — do not claim on video.

---

## WRONG / honest limits

- **Assumed hosted stranger demo still worked** until curl at the live URL — STATUS/PITCH/Devpost try-it were stale proxies; the object is login-walled.
- **Carried A=2→B=1 from the markdown receipt** until re-running `compound_exhibit_receipt.py` went RED (A=2→B=3). Exact-assertion reuse made paraphrased mini-B a false compounding story.
- **Cost gate shipping arm cannot SOURCED tonight** — no billing export on disk; baseline dollars are invented and labeled as such. Unticked “cost from billing” is now a runnable gate that refuses, not a silent blank.
- **Did not restore a public exhibit surface** — product direction is private workspaces; restoring public `/search` is Oscar’s deploy decision (`DEPLOY-PREP-2026-09-06.md`).
- **Did not claim `FULL GATE OK`** — `bash scripts/full_gate.sh` exited **2** with `OFFLINE OK · HOSTED BLOCKED` after stranger probe RED (correct; long_run skipped).
- **McNemar p=1.0000 at n=6 still not significant** — delta +1 on refusal set unchanged.
- **Video / Devpost / deploy promote** — outward acts; not done.
- **PeriodCheck LOC tonight (2576) is not the old “11–14k” figure** — re-derived at their HEAD clone; do not carry the prior counter without reconciling what it included.
