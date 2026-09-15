# RECEIPT — Partner integrations night · 2026-09-15

**Branch:** `cursor/partner-integrations-night-93d1`  
**Slice:** All four partners provable in code on the private-workspace path; free-tier CELEX restored; film objects corrected; live thin health watched RED.

## Objects opened (not proxies)

```bash
curl -s https://agent-science-568004190078.us-central1.run.app/health
python3 scripts/watch_partner_health_object.py
python3 -m clearance lookup "2012/28/EU"
curl -sL …/visibility/ui | head
curl -sL …/judge/demo | head
```

### Live hosted (revision `agent-science-00028-hed`) — WATCHED RED

| Surface | Result |
|---------|--------|
| `/health` | `{ok,service,mode,revision}` only — missing partner fields |
| `/partners` | Login HTML (not track JSON) |
| `/visibility/ui` · `/truths/ui` | Local-only notices — not Transparency / truths dashboard |
| `/judge/demo` | Public evidence example works |

`python3 scripts/watch_partner_health_object.py` → **exit 2**.

Naive arm = this live revision. Shipping arm = this branch (awaiting Oscar `deploy.sh`).

### Free-tier CELEX (was poisoned)

Before fix: `lookup "2012/28/EU"` → `UNSOURCED` · `search_found_no_admissible_source` · read 0 of 1 (encoding miss).  
After `instruments.canonical` unquote + alias cheap route:

```bash
python3 scripts/seed_document_cache.py
python3 -m clearance lookup "2012/28/EU"
# [SOURCED] … tier=cheap|free · via route:celex|dictionary_exact · 0 Parallel API
python3 -m clearance lookup "orphan works directive"
# [SOURCED] … tier=cheap · via route:celex
```

## Verified commands (this VM)

```text
python3 tests/test_watch_it_go_red.py                 # 72/72
python3 tests/test_adk_default_path.py                # 5/5
python3 tests/test_partner_runtime.py                 # 8/8
python3 -m unittest tests.test_hosted_flow.HostedFlow.test_anonymous_partner_health_and_manifest  # OK
python3 scripts/prove_partner_health_local.py         # LOCAL_PARTNER_HTTP_OK
python3 scripts/bench_check_docs.py                   # 129/129
python3 scripts/eval_refusal_baseline.py              # baseline 5/6 shipping 6/6 delta +1
python3 scripts/eval_refusal_ablation.py              # ablation 5/6 shipping 6/6 delta +1
python3 scripts/eval_artifact_claims.py               # shipping 7/7 (pack public-repo was stale)
python3 scripts/compound_exhibit_receipt.py           # A=2→B=1 Parallel, corpus_hits=2
python3 scripts/watch_partner_health_object.py        # exit 2 (live still thin)
bash film/preflight.sh                                # FAIL only on thin health + partners (expected)
```

## What this branch adds beyond the admissibility restore

| Item | Path |
|------|------|
| Live RED watcher | `scripts/watch_partner_health_object.py` |
| Local hosted+desk HTTP proof | `scripts/prove_partner_health_local.py` |
| CELEX encoding + alias routing | `clearance/instruments.py` · `clearance/dictionary.py` |
| Film surface finding | `docs/FINDING-hosted-film-surface-2026-09-15.md` |
| Artifact-claim eval gate | `scripts/eval_artifact_claims.py` (in `full_gate.sh`) |
| SUBMISSION-PACK public-repo truth | was unchecked/private wording; object is public |

## BLOCKED (Oscar)

1. `bash deploy.sh` — promote partner-health restore so live `/health` goes green.
2. Workspace token + keys for live compound — `docs/BLOCKED-live-compound-2026-09-15.md`.
3. Film hosted beat = `/judge/demo` + post-deploy `/health`, not `/visibility/ui`.
