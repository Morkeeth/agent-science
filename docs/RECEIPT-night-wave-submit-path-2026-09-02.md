# RECEIPT — submit path night wave

**Date:** 2026-09-02 · **Branch:** `cursor/night-wave-submit-path-e9f3`

## Shipped

1. **Holdout frozen gate** — `fixtures/refusal-correctness/MANIFEST.json`, `clearance/holdout.py`,
   `scripts/freeze_holdout.py`, `tests/test_holdout_frozen.py`
2. **Symmetric scorer gate** — `scripts/eval_refusal_symmetric.py` · both arms emit
   `{supported, quote}`; external bool scorer only
3. **SUBMISSION-PACK truth refresh** — fixed stale **13/13** → **16/16** in Devpost paste;
   stranger one-command block added
4. **BLOCKED live compound receipt** — `docs/RECEIPT-live-compound-BLOCKED-2026-09-02.md`
5. **Deploy prep checklist** — `docs/DEPLOY-PREP-CHECKLIST-2026-09-02.md` (no deploy run)

## Verified (commands run)

```bash
python3 scripts/seed_document_cache.py && python3 tests/test_watch_it_go_red.py
# 72 passed, 0 failed

python3 scripts/freeze_holdout.py --check
# holdout intact: 6 items, labelled 2026-08-22T21:30:00Z, frozen 2026-09-02

python3 tests/test_holdout_frozen.py
# 3/3 passed

python3 scripts/eval_refusal_symmetric.py
# Baseline:  5/6 = 0.833  95% CI [0.436, 0.970]
# Shipping:  6/6 = 1.000  95% CI [0.610, 1.000]
# Delta (shipping - baseline): +1
# McNemar:   p=1.0000 (b=0 c=1 discordant)
# RC5 substring trap: baseline false-GREEN, shipping refuses — symmetric delta proven.

python3 scripts/bench_check_docs.py
# ALL 127/127 match SUBMISSION-PACK

python3 scripts/compound_exhibit_receipt.py
# offline A=2 B=1 corpus_hits=2 PASS

python3 tests/test_registry_surface.py -q
# 16/16 passed
```

## Wrong / not verified

- **Live compound on hosted URL** — BLOCKED: no `PARALLEL_API_KEY` or `GEMINI_API_KEY` on this VM
- **`test_vision_wiring.py`** — fails (`websearch companion` string missing from desk page); not in SUBMISSION-PACK 127 suite; left broken
- **Cost from billing gate** — still unchecked in Qwen checklist
- **Deploy** — checklist only; `deploy.sh` not executed (Oscar only)
