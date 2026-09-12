# RECEIPT — Partner admissibility re-land · 2026-09-12

**Branch:** `cursor/partner-admissibility-restore-abf6`  
**Slice:** re-land Sep-7 partner-admissible surfaces onto a shippable PR; prove local GREEN; re-measure live RED on `00028-hed`; add naive-baseline control so stripped liveness cannot fake green again.

## SHIPPED (tonight beyond Sep-7 cherry-pick)

| Item | Evidence |
|------|----------|
| Cherry-pick partner admissibility onto main tip | commits `1c624c0` + `527fc30` then tonight's additions |
| `scripts/prove_partner_surfaces_local.py` | cold HTTP prove — no network/keys |
| `scripts/watch_hosted_partner_health.py` | live curl + naive ok-only baseline arm |
| Naive-baseline unit control | `t_naive_ok_only_arm_greens_stripped_liveness` |
| Finding re-measured at object | live `00028-hed` still stripped |
| SUBMISSION-PACK | **132/132** after +1 partner control |

## VERIFIED (commands run 2026-09-12)

```text
python3 tests/test_watch_it_go_red.py                 # 72/72
python3 tests/test_partner_runtime.py                 # 11/11
python3 tests/test_parallel_integration.py            # 6/6
python3 tests/test_adk_default_path.py                # 5/5
PYTHONPATH=. python3 -m unittest tests.test_hosted_flow  # 15 OK
python3 scripts/prove_partner_surfaces_local.py       # PROVE OK
python3 scripts/bench_check_docs.py                   # 132/132
python3 scripts/eval_refusal_baseline.py              # baseline 5/6 shipping 6/6 delta +1
python3 scripts/eval_refusal_ablation.py              # ablation 5/6 shipping 6/6 delta +1
python3 scripts/eval_scorer_symmetry.py               # baseline 5/6 vs shipping 6/6
python3 scripts/eval_verify_holdout.py                # HOLDOUT OK 4 files
python3 scripts/watch_hosted_partner_health.py        # RED · naive GREEN · rev 00028-hed
bash scripts/verify_partners_hosted.sh                # RED on live until Oscar deploy
```

## BASELINE ARM (embarrassing, intentional)

Against live stripped `/health`:

- **Naive ok-only arm:** GREEN (`ok` + `service` only)
- **Partner fields arm:** RED (missing gemini/parallel/engine_default/…)

That gap is why STATUS and old receipts stayed “healthy” after the private-workspace pivot. The watch script freezes the failure mode.

## BLOCKED / WRONG

- **Live hosted** still revision `00028-hed` with stripped health — Oscar must `bash deploy.sh` then promote the candidate revision.
- **No workspace token / Parallel key on this VM** — cannot prove live `POST /api/clear` or orphan-works A/B here; offline eval + local HTTP prove remain authoritative.
- **Outward acts** (deploy, Devpost, video) remain Oscar-only.
- Promise-line README rewrite not re-opened: product ruling keeps CLI/MCP as front door; clearance promise remains in PITCH/SUBMISSION-PACK.

## FULL GATE (2026-09-12)

```text
bash scripts/full_gate.sh
# Local through cold-clone: OK (secrets · 72/72 · partner 11/11 · ADK 5/5 · 132/132 · evals · privacy)
# Hosted long run: RED — curl /health assert engine_default==adk fails on 00028-hed (expected until deploy)
```

`pip install -r requirements.txt` now includes `pytest` so §4a research suites run after a cold install (was ModuleNotFoundError without it).
