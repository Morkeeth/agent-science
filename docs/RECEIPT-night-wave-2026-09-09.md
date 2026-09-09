# RECEIPT — Sep 9 night wave · submit-path truth at object

**Date:** 2026-09-09 · **Branch:** `cursor/sep9-submit-gaps-367d` · **Hosted rev measured:** `agent-science-00028-hed`

## What this wave did

Not a doc polish. Opened the objects that submission claims pointed at.

1. **Offline compound was RED on main** — paraphrase mini-B under exact-assertion integrity → A=2 B=3 corpus_hits=0. Restored exact overlapping assertions → A=2→B=1 hits=2.
2. **Hosted stranger URLs were false-GREEN in Devpost** — `/visibility/ui` returns public-entry stub; `/search` 303 to login; `/health` still `ok: true`. Artifact gate watched the pack go RED (AC7, AC11) before the paste was corrected.
3. **CELEX cache key** — `%3A` vs `:` collapsed so free lookup and seed share one document key.
4. **Live compound** honestly BLOCKED (no keys + hosted `/clear` 401).
5. **Deploy prep only** — `docs/DEPLOY-PREP-2026-09-09.md`; deploy.sh not run.

## Commands run (at object)

```text
python3 tests/test_watch_it_go_red.py                 → 72 passed, 0 failed
python3 scripts/bench_check_docs.py                   → ALL 128/128 match SUBMISSION-PACK
python3 scripts/compound_exhibit_receipt.py           → A=2 B=1 corpus_hits=2 exit 0
python3 scripts/eval_compound_baseline.py             → soft false-PASS; shipping refuses paraphrase; exact PASS
python3 scripts/eval_artifact_claims.py               → before pack fix exit 3 (AC7,AC11); after exit 0 arms agree 10/12
python3 scripts/eval_refusal_baseline.py              → baseline 5/6 shipping 6/6
python3 scripts/eval_scorer_symmetry.py               → baseline 5/6 shipping 6/6
python3 scripts/eval_verify_holdout.py                → HOLDOUT OK — 4 files
python3 tests/test_registry_surface.py -q             → 16/16
python3 -m clearance lookup "2012/28/EU"              → [SOURCED] tier=free
curl …/health                                         → mode=private-workspaces rev=00028-hed
```

Stale-pack RED transcript: `docs/receipts/artifact-claims-RED-2026-09-09.txt`

## Findings

- `docs/FINDING-compound-paraphrase-reuse-2026-09-09.md`
- `docs/FINDING-hosted-stranger-surface-2026-09-09.md`
- `docs/BLOCKED-live-compound-2026-09-09.md`

## Still Oscar

Video · Devpost submit · deploy promote · workspace token for any hosted research demo.
