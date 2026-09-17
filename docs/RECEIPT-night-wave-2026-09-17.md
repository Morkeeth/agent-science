# RECEIPT — night wave 2026-09-17 · cost gate + pack truth + deploy prep

**Branch:** `cursor/night-wave-submit-gaps-ac28` · **Contract:** `hack.md` NOW  
**Start gate:** `git pull` + `python3 tests/test_watch_it_go_red.py` → **72/72**

---

## SHIPPED

1. **Qwen cost-from-billing gate** — `scripts/eval_cost_from_billing.py` + dated price card
   `fixtures/price-cards/parallel-search-advanced.json` (fetched from Parallel docs; rate
   **parsed from body**, not carried). Arms: ALWAYS_SILENT / NAIVE_NO_REUSE / SHIPPING.
2. **Hardcoded `29 SOURCED` killed** — `compound_exhibit_receipt.py` now prints
   `refusal_log.stats()` cleared/refused. RED control:
   `tests/test_compound_receipt_counts.py`.
3. **SUBMISSION-PACK truth refresh** — suite table re-measured; public-repo row [x];
   claims **239** local (not carried 265+); stranger block adds cost eval; hosted stats
   honesty (303).
4. **Live compound BLOCKED receipt** — `docs/BLOCKED-live-compound-2026-09-17.md`
   (`/clear` 401; no keys/token; health still stripped on `00028-hed`).
5. **Deploy prep** — `docs/DEPLOY-PREP-2026-09-17.md` matches current candidate-tag
   `deploy.sh` (no agent deploy).

---

## VERIFIED (command → object)

| Claim | Command | Result |
|-------|---------|--------|
| Mutation controls | `python3 tests/test_watch_it_go_red.py` | 72/72 |
| Pack suite totals | `python3 scripts/bench_check_docs.py` | 128/128 match |
| Registry surface | `python3 tests/test_registry_surface.py -q` | 16/16 |
| Partner runtime | `python3 tests/test_partner_runtime.py` | 7/7 |
| Baseline / ablation | `eval_refusal_baseline.py` · `eval_refusal_ablation.py` | 5/6 vs 6/6, delta +1 |
| Scorer symmetry | `python3 scripts/eval_scorer_symmetry.py` | 5/6 vs 6/6 |
| Cost gate | `python3 scripts/eval_cost_from_billing.py` | silent 3/6@$0 · ship 6/6 · 5→3 calls |
| Compound offline | `python3 scripts/compound_exhibit_receipt.py` | A=2→B=1 · hits=2 · **25 GREEN / 214 refused / 239** |
| Hardcoded count control | `python3 tests/test_compound_receipt_counts.py` | 2/2 |
| Public repo | `gh repo view … --json visibility` | PUBLIC |
| Hosted health | `curl …/health` | `00028-hed` stripped (no partner fields) |
| Hosted clear | `curl -X POST …/clear` | **401** |
| Hosted partners/stats/search | curl `-w http_code` | **303** each |
| Keys on VM | env + `~/.config/keys/parallel.key` | **missing** |

Cost gate raw finding (re-run; do not carry):

```
ALWAYS_SILENT                 0     0.0000
NAIVE_NO_REUSE                5     0.0250
SHIPPING                      3     0.0150   # A=2→B=1 measured
ALWAYS_SILENT: 3/6 = 0.500  95% CI [0.188, 0.812]
SHIPPING:      6/6 = 1.000  95% CI [0.610, 1.000]
McNemar: p=0.2500 (b=0 c=3 discordant)
Price card fetched: 2026-09-17T20:17:40Z · $5/1000 advanced Search
```

---

## WRONG

1. **Guessed NOW was still partner-admissibility** until reading that slice was already
   shipped 2026-09-16 — updated NOW before code, but burned the first minutes on a
   finished slice's receipts.
2. **Could not open Parallel console billing** — cost gate is price-card × call counts,
   not an invoice. Checklist item is met as dated price-card estimate; calling it
   "from billing" without a key would be a lie — the script says so every run.
3. **Hosted claim count 265+ not re-derived** — `/stats` 303. Local boot is **239**.
   Any doc still saying 265 without a hosted object is stale; pack corrected, STATUS.md
   left for a later pass (avoid sprawl).
4. **Live compound still BLOCKED** — no keys, no workspace token, `/clear` 401. Offline
   compound is authoritative tonight.
5. **Partner `/health` still RED on live** — fix is in tree; Oscar must `deploy.sh` +
   promote. This agent did not deploy.
6. **McNemar p=0.2500 on silent vs shipping** — correctness delta +3 is real on the
   table but not significant at n=6; do not pitch "statistically proven".
7. **Import path for CER** — first `importlib` attempt failed on dataclasses; switched
   to `runpy`. Works, but is uglier than a package layout (not restructured tonight).

---

## Oscar next

1. `docs/DEPLOY-PREP-2026-09-17.md` → deploy candidate → promote → `verify_partners_hosted.sh`
2. Keys + workspace token → live compound or keep BLOCKED honest
3. Video + Devpost (outward)
