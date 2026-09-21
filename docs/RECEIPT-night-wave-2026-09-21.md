# RECEIPT — night wave 2026-09-21 · cost gate + artifact claims + pack truth

**Branch:** `cursor/night-wave-sep9-gaps-2bda` · **Constitution:** no Devpost / video / deploy / public flip

---

## SHIPPED

1. **Qwen cost gate (dated price card + null arm)** — restored from unmerged Sep-19 work, re-run tonight  
   - `scripts/eval_cost_gate.py` · `fixtures/price-card/parallel.json` (retrieved **2026-09-21T00:10:55Z** from docs.parallel.ai)  
   - Arms: NULL **3/6** · BASELINE **5/6** · SHIPPING **6/6**  
   - Billing control watched RED: `--require-billing` → exit **3**  
   - Embarrassing: `parallel_calls` A=2/B=1 ≠ Search door find_sources A=1/B=2; priced −100% “saving”  
   - Embarrassing: prior hardcoded `$0.005` was **5×** Fast-tier overstatement  
   - PRIOR LOSS **Cost from billing** stays **unticked** (no invoice)

2. **Artifact claims at object** — restored from unmerged Sep-11 work, re-run tonight  
   - `scripts/eval_artifact_claims.py` · baseline (title trust) **3/8** vs shipping **8/8**, delta **+5**  
   - 5/5 known-stale hosted/pack claims refused when the object was opened

3. **SUBMISSION-PACK truth refresh** — public-repo lie fixed; 265+ unbound figure replaced with **238** after `boot_registry.py`; stranger block adds cost + artifact; controls dated **2026-09-21**; **128/128**

4. **Live compound BLOCKED** — `docs/BLOCKED-live-compound-2026-09-21.md`

5. **Deploy prep** — `docs/DEPLOY-PREP-2026-09-21.md` (candidate `--no-traffic`, timeout 240, partner strip still live)

6. **Cold-clone** steps 11–12 wire cost + artifact gates

---

## VERIFIED (command → result)

| Claim | Command | Result |
|-------|---------|--------|
| Mutation controls | `python3 tests/test_watch_it_go_red.py` | **72/72** |
| Pack suite total | `python3 scripts/bench_check_docs.py` | **128/128** |
| Cost gate | `python3 scripts/eval_cost_gate.py` | NULL 3/6 · BASELINE 5/6 · SHIPPING 6/6 · billing RED |
| Billing RED control | `python3 scripts/eval_cost_gate.py --require-billing; echo $?` | exit **3** |
| Cost gate tests | `python3 tests/test_cost_gate.py` | **4/4** |
| Artifact claims | `python3 scripts/eval_artifact_claims.py` | baseline **3/8** · shipping **8/8** |
| Artifact tests | `python3 tests/test_eval_artifact_claims.py` | all passed |
| Offline compound | `python3 scripts/compound_exhibit_receipt.py` | A=2→B=1 · corpus_hits B=2 |
| Holdout | `python3 scripts/eval_verify_holdout.py` | HOLDOUT OK · 4 files |
| Refusal baseline | `python3 scripts/eval_refusal_baseline.py` | 5/6 vs 6/6 · delta +1 |
| Repo public MIT | `gh api repos/Morkeeth/agent-science` | `visibility=public` · `license=MIT` |
| Live health strip | `curl -sS …/health` | only ok/service/mode/revision · rev `00028-hed` |
| Live clear | `curl -X POST …/clear` | **401** |
| Keys on VM | `test -f ~/.config/keys/parallel.key` | **MISSING** |

Full stdout: `docs/RECEIPT-cost-gate-run-2026-09-21.txt` · `docs/RECEIPT-artifact-claims-run-2026-09-21.txt`

---

## WRONG / could not verify / left broken

1. **Prompt said "fix stale 26/13"** — no `26/13` string existed in the pack object tonight. Stale lies that *were* present: Public repo marked Private; hosted ADK checked green; unbound **265+** claims. Fixed those. If 26/13 meant something else, it was not found.
2. **Did not invent billing** — price card ≠ invoice. "Cost from billing" remains unchecked on purpose.
3. **Did not deploy** — live partner health still RED on `00028-hed`.
4. **Did not run live compound** — no Parallel/Gemini keys, no workspace token; offline receipt is authoritative.
5. **Hosted claim count** — `/stats` login-gated; 238 is local boot only, not hosted.
6. **Free-tier count** — marketing pages historically disagree (5k vs 80k); card note says not re-derived tonight.
7. **Prior night-wave branches** (`night-wave-qwen-cost-pack-870b`, `night-wave-artifact-claims-acb8`) had this work and it never landed on main — tonight restores it rather than rediscovering from scratch; numbers were all re-run at object on 2026-09-21.
