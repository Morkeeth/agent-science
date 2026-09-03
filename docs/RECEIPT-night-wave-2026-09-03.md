# RECEIPT — night wave 2026-09-03

**Slice:** SUBMISSION-PACK truth refresh + Qwen eval gates (holdout freeze + scorer symmetry)  
**Branch:** `cursor/night-wave-submission-eval-4ae1`  
**Keys on VM:** PARALLEL missing · GEMINI missing → live compound **BLOCKED**

---

## SHIPPED

1. **Holdout freeze gate** — `fixtures/refusal-correctness/MANIFEST.json` + `scripts/eval_verify_holdout.py` + `scripts/freeze_holdout.py`
2. **Scorer symmetry eval** — `scripts/eval_scorer_symmetry.py` (baseline substring vs shipping on delivered SOURCED/UNSOURCED labels only)
3. **SUBMISSION-PACK refresh** — stale `registry 13/13` → **16/16**; stranger block adds `test_registry_surface.py -q` + offline compound receipt; re-measured 127/127
4. **Cold-clone path extended** — `scripts/verify_cold_clone.sh` steps 6–9
5. **Full gate** — holdout + scorer symmetry in `scripts/full_gate.sh` §5a
6. **Deploy prep** — `docs/DEPLOY-PREP-2026-09-03.md` (Oscar checklist, no deploy run)

---

## VERIFIED (command at object)

```bash
git pull && python3 tests/test_watch_it_go_red.py 2>&1 | tail -3
# 72 passed, 0 failed

python3 scripts/bench_check_docs.py
# ALL 127/127 match SUBMISSION-PACK

python3 scripts/eval_verify_holdout.py
# HOLDOUT OK — 4 files match MANIFEST (frozen 2026-08-22T21:30:00Z)

python3 scripts/eval_scorer_symmetry.py
# Baseline 5/6 vs Shipping 6/6 on delivered labels; RC5 discordant (baseline false-SOURCED)

python3 scripts/eval_refusal_baseline.py && python3 scripts/eval_refusal_ablation.py
# baseline 5/6 vs shipping 6/6; ablation 5/6 vs shipping 6/6; delta +1 each

python3 tests/test_registry_surface.py -q
# 16/16 passed

python3 scripts/compound_exhibit_receipt.py
# offline A=2→B=1 Parallel, corpus_hits B=2 — docs/COMPOUND-EXHIBIT-2026-08-29.md
```

---

## BLOCKED

**Live compound exhibit (orphan-works A/B on hosted):**

```bash
test -n "$PARALLEL_API_KEY" || test -f ~/.config/keys/parallel.key
# exit 1 — missing on this VM

test -n "$GEMINI_API_KEY" || test -f ~/.config/keys/gemini.key
# exit 1 — missing on this VM
```

Honest receipt: use offline `compound_exhibit_receipt.py` or Oscar deploy with keys present.

**Orphan-works full script Run B on hosted:** prior **504 Gateway Timeout** at 300s — do not claim on video.

---

## WRONG / honest limits

- **Scorer symmetry does not rescue n=6** — McNemar p=1.0000 at b=0 c=1; delta +1 is real but not significant.
- **Baseline still false-SOURCED on RC5** when scored on delivered labels — the embarrassment is visible and intentional.
- **Live compound not re-run** — no keys; offline receipt is authoritative for this VM.
- **Holdout MANIFEST does not include `regression.json`** — only the labelled gold set is pinned; regression set is separate.
- **Did not run `full_gate.sh` end-to-end** — hosted long_run requires network + live URL; cold-clone subset verified instead.
