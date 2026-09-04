# RECEIPT — night wave 2026-09-04

**Slice:** Artifact-claims falsifiable gate + SUBMISSION-PACK/STATUS truth + null arm + live compound + deploy prep  
**Branch:** `cursor/night-wave-artifact-claims-acb8`  
**Keys on VM:** PARALLEL missing · GEMINI missing · ADC missing — **hosted probe does not need them**

---

## SHIPPED

1. **Artifact-claims eval** — `scripts/eval_artifact_claims.py` (baseline=trust-doc vs shipping=re-derive at object)
2. **RED control** — `tests/test_artifact_claims.py` plants pack `watch_it_go_red **26/13**` and requires eval exit ≠ 0
3. **Null arm steelman** — `scripts/eval_null_arm.py` (always-UNKNOWN vs baseline vs shipping on n=6)
4. **SUBMISSION-PACK truth** — public repo [x]; Devpost `@ main`; hosted **300+ / n=306 / hr=0.627**; stranger block retained
5. **STATUS truth** — killed carried **265 / ~0.80**; replaced with `/stats` measure; honesty note
6. **Qwen gate doc** — `docs/QWEN-EVAL-GATE-ARTIFACT-CLAIMS-2026-09-04.md` (pre-fix delta +4 preserved)
7. **Live compound exhibit** — hosted fresh probe PASS `compound-fresh-a7009f2c6127` A=1 B=1 hits=1 (`docs/RECEIPT-live-compound-exhibit-2026-09-04.md`)
8. **Deploy prep** — `docs/DEPLOY-PREP-2026-09-04.md` (`--timeout=300` risk; no deploy run)
9. **Wiring** — `full_gate.sh` §5a + `verify_cold_clone.sh` steps 9–10
10. **hack.md** — NOW + LOG + PRIOR LOSS row ticked with command

---

## VERIFIED (command at object)

```bash
python3 tests/test_watch_it_go_red.py 2>&1 | tail -3
# 72 passed, 0 failed

python3 scripts/bench_check_docs.py
# ALL 127/127 match SUBMISSION-PACK

# PRE-FIX (captured before pack edit) — shipping found 4 stale:
# AC4 Private until submit · AC5 @ e6793ab · AC7 public row · AC8 STATUS 265/0.80 vs live 306/0.627
# Baseline 4/8 · Shipping 8/8 · delta +4

python3 scripts/eval_artifact_claims.py
# FINDING: zero stale artifact claims at object. (post-fix)

python3 tests/test_artifact_claims.py
# PASS  test_planted_stale_26_13_goes_red
# 2/2 passed

python3 scripts/eval_null_arm.py
# Null 3/6 · Baseline 5/6 · Shipping 6/6 · shipping beats null

python3 scripts/eval_refusal_baseline.py && python3 scripts/eval_refusal_ablation.py
# baseline 5/6 vs shipping 6/6; ablation 5/6 vs shipping 6/6

python3 tests/test_registry_surface.py -q
# 16/16 passed

python3 scripts/compound_exhibit_receipt.py
# offline A=2→B=1 Parallel

python3 scripts/compound_fresh_hosted_probe.py
# RUN_A parallel_calls=1 · RUN_B parallel_calls=1 corpus_hits=1 · COMPOUND pass=True
# subject=compound-fresh-a7009f2c6127

curl -sf https://agent-science-568004190078.us-central1.run.app/stats
# n≈306+ · dictionary_hit_rate=0.627 · queries_logged=279

curl -sf https://api.github.com/repos/Morkeeth/agent-science | python3 -c \
  "import sys,json; print(json.load(sys.stdin)['private'])"
# False
```

---

## BLOCKED

**Cost from billing:** no billing console on this VM — PRIOR LOSS row stays open.

**Orphan-works full script:** hosted **504 @ 300s** — `deploy.sh --timeout=300`.

**Local-key clearance:** PARALLEL/GEMINI/ADC missing on this VM — not required for hosted `/clear` probe.

---

## WRONG / honest limits

- **Pre-fix delta is the real finding; post-fix 8/8 is after we cheated by fixing the docs.** The gate's value is the 4 stale claims it caught — including STATUS hit rate **0.627** vs the carried **~0.80** (wrong by ~17 points). A report that only showed post-fix green would be a demo.
- **Assumed live compound needed local keys — wrong.** Hosted `/clear` carries service keys; `compound_fresh_hosted_probe.py` PASSed without PARALLEL/GEMINI on the VM. The early BLOCKED stub is kept as the record of that mistake.
- **Hosted Parallel did not drop** on fresh subject (1→1); compounding was `corpus_hits=1`. Do not overwrite the sealed A=1→B=0 headline with tonight's equal-Parallel run.
- **AC6 briefly false-greened** because STATUS's `deadline: 2026-09-09` matched a "refreshed date" regex — fixed by matching the exact stale `265 claims` / `hit rate ~0.80` strings instead of inferring freshness from any Sep date.
- **Hosted `/stats` n drifts during the night** (301→312 while measuring). Pack uses **300+** lower bound; STATUS stamps a point-in-time n=306. AC8 tolerance widened to ±25 for that reason.
- **Null arm does not embarrass us tonight** (3/6 vs 6/6). Shipped anyway so a future regression is visible.
- **Did not close Cost-from-billing** — would require Oscar's Parallel/Gemini billing console + dated price card; inventing a USD figure would violate "never carry a number / re-derive at object."
- **Did not run `full_gate.sh` end-to-end** — long_run + stranger trial hit hosted; offline subset + artifact gate + fresh compound verified instead.
- **127/127 pack gate covers exactly half the tree** — `python3 scripts/eval_suite_coverage.py` → **127/254 = 0.500** PASS lines; 21 files ungated (incl. semantic_guard 18, front_surface 23, citation_conflict 21). Shipped the measurement; did **not** silently expand the pack denominator tonight.
- **Prompt said "fix stale 26/13"** — that exact pair was not in the pack (already 16/16 / 127/127 from Sep-3). Used **26/13 as the RED-control plant** instead; the live stales were Private-until-submit, `@ e6793ab`, and 265/~0.80.
