# RECEIPT — night wave 2026-09-22 · artifact truth + null arm

**Branch:** `cursor/night-wave-submit-gaps-2b67` · **START:** `test_watch_it_go_red.py` → **72/72**

---

## SHIPPED

1. **Qwen gate — every artifact claim at its object**  
   `fixtures/artifact-claims/set.json` · `scripts/eval_artifact_claims.py` · `tests/test_artifact_claims.py`  
   Arms: NULL (always NOT_HELD) · BASELINE (believe doc) · OBJECT (probe).  
   Planted RED control AC10 watched going red when probe lies.

2. **Null arm on refusal-correctness set**  
   `scripts/eval_null_arm.py` — false-SOURCED rate printed beside accuracy.

3. **SUBMISSION-PACK / STATUS honesty refresh** — stale hosted claims corrected at object.  
4. **BLOCKED live compound** — `docs/BLOCKED-live-compound-2026-09-22.md`.  
5. **Deploy prep** — `docs/DEPLOY-PREP-2026-09-22.md` matching current `deploy.sh` (candidate, no traffic).
6. **External baseline** — `docs/EXTERNAL-BASELINE-PERIODCHECK-2026-09-22.md` (their `live-evaluation.json` 13/13 re-derived).

---

## VERIFIED (command → result)

| Claim | Command | Result |
|-------|---------|--------|
| Mutation controls | `python3 tests/test_watch_it_go_red.py` | **72/72** |
| Suite doc gate | `python3 scripts/bench_check_docs.py` | **128/128** match |
| Registry | `python3 tests/test_registry_surface.py -q` | **16/16** |
| Offline compound | `python3 scripts/compound_exhibit_receipt.py` | A=**2**→B=**1**, corpus_hits=**2**, exit 0 |
| Baseline/ablation | `eval_refusal_baseline.py` · `eval_refusal_ablation.py` | 5/6 vs 6/6, delta +1 |
| Null arm | `python3 scripts/eval_null_arm.py` | NULL 3/6 · BASE 5/6 · SHIP 6/6 · false-SOURCED 0/1/0 |
| Artifact claims | `python3 scripts/eval_artifact_claims.py` | NULL **6/10** · BASE **4/10** · OBJECT **10/10** |
| Artifact tests + RED | `python3 tests/test_artifact_claims.py` | **3/3** · CONTROL FAIL when probe lies |
| Local partner health | `bash scripts/prove_partner_health_local.sh` | `engine_default: adk` · OK |
| Live /health | `curl -sS …/health` | rev **00028-hed** · keys only ok/service/mode/revision |
| Live /visibility/ui | `curl -sSL …/visibility/ui` | **local-only** notice — not judge panel |
| Live /partners | `curl -sSL …/partners` | Sign-in HTML, not JSON |
| Repo visibility | `curl …/repos/Morkeeth/agent-science` | `private=false` · `visibility=public` |
| PeriodCheck eval JSON | their `live-evaluation.json` | `correct_verdicts` **13**/`gold_claims` **13** · e2e 1.0 |
| PeriodCheck hosted | `curl …periodcheck-….run.app/` | **200** upload UI |
| Keys for live compound | env + `~/.config/keys/*` | **all missing** → BLOCKED |

---

## WRONG / could not verify / left broken

1. **STATUS.md and SUBMISSION-PACK were lying about hosted stranger surfaces** — `/visibility/ui` and `/truths/ui` are local-only on Cloud Run; `/partners` is behind login; `/health` has no `engine_default`. Null beat doc-trust **6/10 vs 4/10**. That is the finding; docs are being corrected in this wave, but the labelled set keeps the stale `doc_asserts` so the gate stays falsifiable.
2. **Live compound not run** — no Parallel/Gemini keys and no workspace token. Offline receipt only.
3. **Hosted partner admissibility still RED** until Oscar `deploy.sh` + traffic promote — fix in tree since 2026-09-16, live still `00028-hed`.
4. **`docs/STATUS.md` "265 claims · hit rate ~0.80"** — `/stats` is auth-gated; number **not re-derived** tonight. Do not carry it.
5. **McNemar on artifact null vs baseline** p=0.75 — null win is real on the point estimate but not significant at n=10; report the rates, not a significance claim.
6. **Did not** Devpost / video / public flip / deploy — Oscar only (repo already public).
