# RECEIPT — night wave 2026-09-23 · artifact-claims gate

**Branch intent:** close the open PRIOR LOSS row *Every artifact claim measured at the submitted commit*, with a baseline arm that can embarrass us. Also refresh SUBMISSION-PACK at object, honest live-compound BLOCKED, deploy prep only.

## SHIPPED

1. **`scripts/eval_artifact_claims.py`** + `fixtures/artifact-claims/set.json` + planted STALE  
   Arms: **null** (always FRESH, never opens object) · **baseline** (trust-doc, always FRESH) · **shipping** (remeasure).  
   Exit 1 while live pack rows are STALE; exit 0 only when live rows FRESH and planted AC10 remains STALE and shipping beats null.
2. **`scripts/eval_cost_billing.py`** + pinned Parallel price card dated **2026-09-23T00:12:00Z**  
   Exit 2 BLOCKED without billing export — PRIOR LOSS "Cost from billing" stays unchecked.
3. **SUBMISSION-PACK truth refresh** — public-repo row, claims-on-disk **238**, tip pin `@ main`, stranger block + gates.
4. **Controls:** `tests/test_eval_artifact_claims.py` (**5/5**), cold-clone step 11, full_gate 5a2, `deploy_prep.sh` partner_runtime **7/7**, demo duration AC11 (**179.675 s ≤ 180**).
5. Deploy prep doc + live-compound BLOCKED receipt (no keys on this VM).

## FIRST RUN (pack still dirty) — the embarrassment

Command: `python3 scripts/boot_registry.py && python3 scripts/eval_artifact_claims.py`  
Registry after boot: **238** claims. Exit **1**.

| id | gold | claimed | measured |
|----|------|---------|----------|
| AC7 | STALE | `e6793ab` | `d56aeb8` (HEAD) |
| AC8 | STALE | Private until submit | hack.md public since 2026-08-22 |
| AC9 | STALE | 265+ | 238 |
| AC10 | STALE | 999999 | 238 (planted) |

Null/baseline **6/10**; shipping **10/10**. McNemar null vs shipping: b=0 c=4.

## AFTER REPAIR (live rows)

Command: `python3 scripts/eval_artifact_claims.py` → exit **0**

```
Null:      10/11 = 0.909
Baseline:  10/11 = 0.909
Shipping:  11/11 = 1.000
STALE at object: AC10
GATE OK — live claims FRESH; planted AC10 STALE; shipping 11/11 beats null 10/11.
```

## VERIFIED (commands run at object)

| Claim | Command | Result |
|-------|---------|--------|
| watch_it_go_red | `python3 tests/test_watch_it_go_red.py` | 72/72 |
| docs gate | `python3 scripts/bench_check_docs.py` | 128/128 match |
| registry_surface | `python3 tests/test_registry_surface.py -q` | 16/16 |
| partner_runtime | `python3 tests/test_partner_runtime.py` | 7/7 |
| refusal baseline | `python3 scripts/eval_refusal_baseline.py` | 5/6 vs 6/6, delta +1 |
| scorer symmetry | `python3 scripts/eval_scorer_symmetry.py` | 5/6 vs 6/6 |
| artifact claims | `python3 scripts/eval_artifact_claims.py` | GATE OK · ship 11/11 > null 10/11 |
| artifact tests | `python3 tests/test_eval_artifact_claims.py` | 5/5 |
| demo duration | `ffprobe … demo/demo-final.mp4` | 179.675 s ≤ 180 |
| cost billing | `python3 scripts/eval_cost_billing.py` | exit 2 BLOCKED |
| repo visibility | `gh api repos/Morkeeth/agent-science --jq .visibility` | `public` |
| registry count | `SELECT COUNT(*) FROM claims` after boot | 238 |
| gap 561/600 | `fixtures/gap-report-600.md` | 561 of 600 |
| flip 247/600 | `fixtures/shift-ai-training-vs-noncommercial.md` | 247 of 600 |
| demo length | `ffprobe … demo/demo-final.mp4` | 179.675 s |
| hosted health | `curl …/health` | still stripped (`00028-hed`) — Oscar deploy |
| live compound | see `docs/BLOCKED-live-compound-2026-09-23.md` | BLOCKED — no keys |

## WRONG / LEFT BROKEN

1. **Carried "265+" for claims-on-disk** until the gate opened the registry — measured **238** after boot. Pack was wrong; null would have shipped it.
2. **Pack still said the repo was private** after it had been public since 2026-08-22 — nearer checklist text beat the GitHub object.
3. **Cost-from-billing remains UNCHECKED** — price card is dated, but no Parallel billing export exists on this VM. Estimates ($0.015 offline / $0.005 sealed at advanced $0.005) are orientation only.
4. **Live hosted `/health` still missing partner fields** on revision `agent-science-00028-hed` — tree fix from 2026-09-16 not deployed (Oscar).
5. **Live compound not run** — `PARALLEL_API_KEY` / `GEMINI_API_KEY` / workspace token absent; offline compound remains authoritative.
6. **McNemar on artifact gate n=11 is not significant** (p=1.0 after repair, p=0.125 on first dirty run at n=10) — tendency only, same honesty bar as refusal n=6.
7. **`deploy_prep.sh` had been printing partner_runtime 5/5** while the suite is 7/7 — fixed tonight; caught by reading the script, not by a prior control.
8. **`compound_exhibit_receipt.py` hardcoded "(29 SOURCED + …)"** while the registry object was **25 GREEN / 213 refused** after boot — same failure mode as the week’s carried-number bugs. Fixed to print `refusal_log.stats()` cleared/refused.

## PRIOR LOSS checklist delta

- [x] **Every artifact claim measured at the submitted commit** — gate + first-run RED transcript above.
- [ ] **Cost from billing** — still open; infrastructure + dated price card shipped; billing export blocked.
