# RECEIPT — Night wave 2026-09-07

**Branch intent:** `cursor/night-wave-stranger-truth-aa0d` · **Hosted rev probed:** `agent-science-00026-zel`  
**Start gate:** `git pull origin main` · `python3 tests/test_watch_it_go_red.py` → **72/72**

---

## SHIPPED

1. **Artifact-claim eval gate** (Qwen PRIOR LOSS row: every artifact claim at object)  
   - `fixtures/artifact-claims/set.json` · `scripts/eval_artifact_claims.py`  
   - Baseline arm: health-ok ⇒ hosted claim holds; trust written pack numbers  
   - Shipping arm: open HTTP / fixture / suite  
   - Output: `docs/ARTIFACT-CLAIM-EVAL-2026-09-07.json`

2. **Cost-from-billing gate** (PRIOR LOSS unchecked row)  
   - `fixtures/price-card/parallel-search-2026-09-07.json` (fetched from https://www.parallel.ai/pricing)  
   - `scripts/eval_cost_from_billing.py` · `docs/COST-FROM-BILLING-2026-09-07.json`  
   - Billing status: **UNKNOWN** (no invoice / key on VM)

3. **Stranger trial watches RED** — `scripts/new_user_trial.sh` exits **2** on `mode=private-workspaces` instead of KeyError on missing `engine_default`

4. **Offline compound exhibit restored under integrity rules**  
   - Paraphrase mini-B was a false compound (A=2→B=3, corpus_hits=0)  
   - Overlapping claims are now identical assertions; B adds the forty-percent claim  
   - Re-run: A=**2**→B=**1**, corpus_hits=**2**, exit 0

5. **SUBMISSION-PACK truth refresh** — public-repo row corrected; hosted stranger desk marked login-walled; offline one-command block remains the stranger path; Oscar checklist no longer says "flip to public"

6. **Deploy prep only** — `docs/DEPLOY-PREP-2026-09-07.md` matches current `deploy.sh` (candidate tag, no traffic)

7. **Live compound BLOCKED receipt** — this section (keys absent + hosted login wall)

---

## VERIFIED (command → result)

| Claim | Command | Result |
|-------|---------|--------|
| Mutation controls | `python3 tests/test_watch_it_go_red.py` | **72/72** |
| Pack suite counts | `python3 scripts/bench_check_docs.py` | **128/128 match** |
| Registry surface | `python3 tests/test_registry_surface.py -q` | **16/16** |
| Refusal baseline | `python3 scripts/eval_refusal_baseline.py` | baseline **5/6**, shipping **6/6**, delta +1 |
| Refusal ablation | `python3 scripts/eval_refusal_ablation.py` | ablation **5/6**, shipping **6/6** |
| Scorer symmetry | `python3 scripts/eval_scorer_symmetry.py` | baseline **5/6**, shipping **6/6** |
| Holdout | `python3 scripts/eval_verify_holdout.py` | **HOLDOUT OK — 4 files** |
| Artifact claims | `python3 scripts/eval_artifact_claims.py` | baseline match **4/10**; false-GREEN **HS1–HS5 + D1** (D1 = stale Private claim removed); D2–D5 hold |
| Cost billing | `python3 scripts/eval_cost_from_billing.py` | price card **2026-09-07** · rate **$0.005** · spend **UNKNOWN** |
| Hosted health | `curl -sS $HOST/health` | `ok` · `mode=private-workspaces` · rev `agent-science-00026-zel` |
| Stranger trial RED | `bash scripts/new_user_trial.sh` | **EXIT 2** RED private-workspaces |
| Offline compound | `python3 scripts/compound_exhibit_receipt.py` | A=**2**→B=**1** · corpus_hits=**2** · exit 0 |
| Gap 561/600 | read `fixtures/gap-report-600.md` | string present |
| Flip 247/600 | read `fixtures/shift-ai-training-vs-noncommercial.md` | string present |
| Local registry size | `sqlite3 cache/refusal_log.db` after boot | **241** claims · **25** GREEN |

---

## WRONG

1. **I first trusted SUBMISSION-PACK / STATUS that hosted was still a stranger desk.** Opening `/health` showed `private-workspaces`; following redirects on `/search` and `/registry` landed on Sign in. The near proxy (`/health` 200) was false-GREEN on five hosted claims — the same failure mode as the Qwen retros.

2. **I almost shipped the offline compound number from the pack without re-running it.** First re-run tonight was A=2→B=3, corpus_hits=0 (exhibit **failed**) because mini-B paraphrased overlapping claims and same-subject integrity now requires identical assertions. The pack's A=2→B=1 was a carried figure relative to current code until the fixture was fixed.

3. **Cost-from-billing is not closed.** Price card is dated; observed spend is UNKNOWN. Ticking that PRIOR LOSS box as "done with a dollar amount" would be a lie — the gate ran and refused to invent spend.

4. **Local free lookup `2012/28/EU` is UNSOURCED** after `boot_registry.py` on this VM (CELEX route, EUR-Lex not admissible in cheap path; registry holds UNKNOWN for the short term). Hosted stranger trial docs that assume SOURCED free on that query are double-broken (login wall + local cheap miss). Not fixed tonight — needs a SOURCED seed that survives SOURCED-only replay, or a live fetch Oscar controls.

5. **`long_run_goal.sh` / `film/preflight.sh` / `verify_partners_hosted.sh` still assume old `/health` shape** (`engine_default`). Only `new_user_trial.sh` was hardened to RED. Those scripts will still crash or false-fail; left broken on purpose rather than silently widening the slice into a full hosted-script rewrite.

6. **Devpost paste inside SUBMISSION-PACK still carries older marketing lines** in §1–3 (buyer prose). Only the lead "Try it" / checklist / controls tables were corrected. A full Devpost rewrite is Oscar's outward act.

7. **No live Parallel/Gemini compound.** Keys absent; hosted `/clear` returns 401 / error page without workspace access key.

---

## BLOCKED (Oscar)

- Restore a public stranger desk **or** re-film against CLI/offline compound + private workspace login  
- Attach Parallel billing export as `PARALLEL_BILLING_JSON` to close cost gate with a real spend  
- Video · Devpost · traffic promote — outward only
