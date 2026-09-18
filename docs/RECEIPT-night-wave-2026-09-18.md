# RECEIPT — Night wave 2026-09-18 · Sep 9 gaps

**Branch:** `cursor/night-wave-sep9-gaps-26e3` · **Base:** `main`  
**Start gate:** `git pull && python3 tests/test_watch_it_go_red.py` → **72/72**

---

## SHIPPED

1. **Qwen PRIOR LOSS — Cost from billing (with baseline arm + dated price card)**
   - `scripts/eval_cost_from_billing.py`
   - `fixtures/price-cards/parallel-search-2026-09-18.md` (fetched from Parallel docs)
   - `tests/test_cost_from_billing.py` (parse RED paths + full eval)
   - `docs/COST-FROM-BILLING-2026-09-18.md`
   - Wired into `scripts/verify_cold_clone.sh` step 10

2. **SUBMISSION-PACK truth refresh**
   - `docs/SUBMISSION-PACK-2026-08-29.md` — dated 2026-09-18; suite table re-measured; stale "Private until submit" → **public since 2026-08-22**; stranger block adds cost gate; hosted partner/ADK honesty corrected

3. **Live compound — honest BLOCKED**
   - `docs/BLOCKED-live-compound-2026-09-18.md`

4. **Deploy prep (no deploy)**
   - `docs/DEPLOY-PREP-2026-09-18.md` — candidate `--no-traffic`, timeout 240, post-promote health/partners checks

5. **hack.md** — NOW + LOG + PRIOR LOSS cost checkbox updated

---

## VERIFIED (command → object)

| Claim | Command | Result |
|-------|---------|--------|
| Mutation controls | `python3 tests/test_watch_it_go_red.py` | **72/72** |
| Pack doc counts | `python3 scripts/bench_check_docs.py` | **128/128 match** |
| Registry stranger | `python3 tests/test_registry_surface.py -q` | **16/16** |
| Offline compound | `python3 scripts/compound_exhibit_receipt.py` | A=**2**→B=**1** Parallel · corpus_hits B=**2** · exit 0 |
| Refusal baseline | `python3 scripts/eval_refusal_baseline.py` | baseline **5/6** vs shipping **6/6** · delta +1 |
| Refusal ablation | `python3 scripts/eval_refusal_ablation.py` | ablation **5/6** vs shipping **6/6** · delta +1 |
| Cost gate | `python3 scripts/eval_cost_from_billing.py` | baseline Parallel **5** = **$0.0250** · shipping **3** = **$0.0150** · card `fetched_at_utc=2026-09-18T08:20:49Z` · invoice **BLOCKED** · exit 0 |
| Cost card refresh | `python3 scripts/eval_cost_from_billing.py --fetch-card` | live docs.parallel.ai parse OK · same rates |
| Cost controls | `python3 tests/test_cost_from_billing.py` | **4/4** (undated/malformed card SystemExit watched) |
| Local partner health | `bash scripts/prove_partner_health_local.sh` | **PROVE_PARTNER_HEALTH_LOCAL OK** · `engine_default=adk` |
| Repo visibility | `gh api repos/Morkeeth/agent-science --jq .visibility` | **public** |
| Live health | `curl -sS $HOST/health` | stripped · revision **agent-science-00028-hed** |
| Live partners | `curl -sS -D - $HOST/partners` | **303** → login (not public JSON) |
| Cold clone stranger path | `bash scripts/verify_cold_clone.sh` | **OK** exit 0 (steps 1–11 incl. cost gate) |

---

## WRONG

1. **Called `/partners` "501" in the first pass of NOW/BLOCKED drafting.** HEAD returned 501; GET returns **303→login**. Corrected before final receipt. Lesson: method matters; open the object the user hits.

2. **Did not obtain a Parallel invoice dollar total.** Gate is price-card × meter with `invoice: BLOCKED`. Ticking "Cost from billing" means dated card + named invoice status — not that billing API returned spend. Anyone reading only the checkbox without the receipt could overclaim.

3. **Absolute USD at compound-mini is tiny ($0.01 save).** Shape holds; production budget claim would need powered fixtures + real invoice. Not claimed.

4. **Live partner-admissibility remains RED** on traffic (`00028-hed`). Tree fix exists; Oscar deploy not run (constitution).

5. **Gemini USD still unpriced** — no dated Gemini price card fetched. Cost gate scopes Parallel Search only.

6. **SUBMISSION-PACK Devpost paste still cites commit `e6793ab` and "265+ claims"** — not re-derived tonight at those objects; left untouched to avoid rewriting the sealed paste block mid-submit. Pack *controls table* was re-measured; paste block was not.

7. **Cold-clone was re-run after wiring step 10:** `bash scripts/verify_cold_clone.sh` →
   **cold-clone verify OK** (exit 0) including cost gate PASS. Earlier draft of this receipt
   claimed it was not run; that was wrong.
