# RECEIPT — partner admissibility night · 2026-09-22

**Branch:** `cursor/partner-integrations-night-0738`  
**Start SHA:** `d56aeb8` · **Scope:** partner integrations — prove honesty + three-arm gate  
**Outward acts not run:** deploy.sh · key rotation · Devpost · video · public flip

---

## Commands run (at object)

```bash
git pull origin main
python3 tests/test_watch_it_go_red.py          # 72/72
curl -sS …/health | python3 -m json.tool       # stripped keys only · rev 00028-hed
bash scripts/verify_partners_hosted.sh         # exit 1 · gemini got None
pip install 'google-adk==2.7.1' 'parallel-web==1.3.2'
bash scripts/prove_partner_health_local.sh     # unpatched · engine_default=adk · OK
python3 scripts/partner_admissibility_gate.py  # exit 2 · A PASS / B FAIL / C PASS
python3 tests/test_partner_admissibility_gate.py  # 6/6
python3 scripts/bench_check_docs.py            # 128/128
python3 scripts/eval_refusal_baseline.py       # baseline 5/6 · shipping 6/6 · delta +1
python3 scripts/eval_refusal_ablation.py       # ablation 5/6 · shipping 6/6 · delta +1
python3 tests/test_adk_default_path.py         # 5/5
python3 -m unittest tests.test_hosted_flow -v  # OK
```

Gate JSON: `docs/RECEIPT-partner-admissibility-gate-2026-09-22.json`  
Finding: `docs/FINDING-adk-prove-patched-2026-09-22.md`

---

## Three-arm result (re-derive — do not carry)

| Arm | Object | Result |
|-----|--------|--------|
| A naive (ours) | hosted `/health` | **PASS** (`ok=true`) |
| B partner fields (ours) | hosted `/health` | **FAIL** (no gemini/parallel/engine_default) |
| /partners public (ours) | hosted `/partners` | **FAIL** (HTTP 303 → run.app) |
| A naive (PeriodCheck) | their `/api/health` | **PASS** (`status=ready`) |
| B partner fields (PeriodCheck) | their `/api/health` | **FAIL** (liveness-only by design) |
| C local unpatched | this checkout after pip | **PASS** (adk 2.7.1 · sdk 1.3.2 · engine_default=adk) |

**Verdict:** LOCAL OK · HOSTED RED (deploy required). Arm A alone would have reported green.

---

## PeriodCheck baseline (repo object, not tagline)

- Clone: `https://github.com/ahsan3274/periodcheck` · **2576** Python LOC (counted with `find … -name '*.py' | xargs wc`)
- This repo (same counter, excluding `.venv*`): **30998** Python LOC
- Dependencies at their `pyproject.toml`: `google-adk[gcp]`, `parallel-web`, Document AI
- Hosted: `https://periodcheck-697827662390.us-central1.run.app` · `/api/health` = `{status, service}` only
- Their `live-evaluation.json` summary at object: gold_claims_extracted **13/13**, end_to_end_accuracy **1.0**, research_failures **0**

They beat us on evidence packaging for the first run. Our compound + refuse spine is the counter — only if hosted partner proof is visible after Oscar deploy.

---

## Shipped this session

1. Unpatched local ADK prove (find + fix silent patch)
2. Three-arm admissibility gate with PeriodCheck baseline + JSON receipt
3. `/partners` 303 watched RED in `verify_partners_hosted.sh`
4. Public judge/film surfaces on WorkspaceHTTP (`/truths/ui`, `/visibility[/ui]`, `/popular[/ui]`)
5. Kill hardcoded `parallel_search_at_runtime: True` — tracks key + verified receipt
6. Partner doc + SUBMISSION-PACK honesty (**129/129**; hosted ADK unchecked)
7. Design-partner loop friction note for private-workspaces + prove modes
8. Qwen eval + bench_check_docs re-derived at object
9. Film preflight asserts partner fields + `/partners` 200 (still RED live until deploy)

---

## BLOCKED (Oscar)

- Live partner fields on `/health` + public `/partners` — until `deploy.sh`
- Live compound / Parallel on hosted `/clear` — no `PARALLEL_API_KEY` / `WORKSPACE_TOKEN` on agent VM
- Key rotation — `AS-KEYS-ROTATE`
