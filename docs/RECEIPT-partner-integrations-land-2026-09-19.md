# RECEIPT — Partner integrations land · 2026-09-19

**Branch:** `cursor/partner-integrations-land-81e9`  
**Commit:** `2fcc963a9e8c749aaa0a851bd80954fbf8e467d0`  
**Slice:** Land unmerged partner-admissibility night; unmask ADK prove; meter search cache; baseline that embarrasses live.

## Bigger object (not the proxy)

Prior nights claimed partner health restored in tree. Opening the objects tonight:

| Object | Command | Result |
|--------|---------|--------|
| Live `/health` | `curl …/health` | still stripped on `00028-hed` |
| Unmerged fix | `git merge-base --is-ancestor eb6d425 main` | exit 1 — checklist honesty never landed |
| Local prove | `prove_partner_health_local.sh` vs `adk_available()` | prove GREEN while `adk_available() False` |

## Shipped

1. **Merged** `origin/cursor/partner-admissibility-night-5719` — kill hardcoded `parallel_search_at_runtime`, public film surfaces, hosted baseline eval, RED controls.
2. **Unmasked local prove** — `scripts/prove_partner_health_local.sh` requires real `google-adk==2.7.1` + `parallel-web==1.3.2` (no mocks). Finding: `docs/FINDING-partner-prove-mocked-adk-2026-09-19.md`.
3. **ADK clear path prove** — `python3 scripts/prove_adk_clear_path.py` → `engine: adk` with real import.
4. **Search cache meter** — `search_cache_hits` on gap reports; separate from Parallel API spend.
5. **Honesty classify** — offline sealed vs soft; hosted exhibit BLOCKED without token (exit 2).
6. **SUBMISSION-PACK** — partner_runtime **10/10**, total **131/131** re-derived.
7. **Cold clone** — `pip install -r requirements.txt` before partner prove; steps 11–12 ADK path + baseline.

## Commands run (done-when)

```text
python3 tests/test_watch_it_go_red.py                 → 72 passed, 0 failed
python3 tests/test_partner_runtime.py                 → 10/10 passed
python3 -m unittest tests.test_hosted_flow -v         → 17 tests OK
bash scripts/prove_partner_health_local.sh            → OK · parallel_sdk=true · engine_default=adk
python3 scripts/prove_adk_clear_path.py               → engine=adk · adk_version=2.7.1
bash scripts/prove_judge_surfaces_local.sh            → PROVE_JUDGE_SURFACES_LOCAL OK
python3 scripts/eval_hosted_partner_baseline.py       → exit 2 · naive PASS / shipping FAIL
python3 scripts/partner_honesty_exhibit.py            → exit 2 BLOCKED (no WORKSPACE_TOKEN)
python3 tests/test_partner_honesty_classify.py        → 8/8
python3 scripts/bench_check_docs.py                   → 131/131
python3 scripts/eval_refusal_baseline.py              → baseline 5/6 · shipping 6/6 · delta +1
python3 scripts/eval_refusal_ablation.py              → ablation 5/6 · shipping 6/6 · delta +1
```

## Still RED / Oscar

- Live deploy of in-tree health + film surfaces + honest checklist
- Live `/clear` compound — needs `WORKSPACE_TOKEN` + Parallel secret
- Key rotation — `AS-KEYS-ROTATE`
