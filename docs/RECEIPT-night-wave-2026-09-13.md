# RECEIPT — night wave 2026-09-13 (compound truth · cost/artifact gates · cold-clone RED)

**Branch:** `cursor/compound-exhibit-truth-5561` · **Mode:** offline (no Parallel/Gemini keys on this VM)  
**Floor:** `python3 tests/test_watch_it_go_red.py` → **72/72** (start of night)  
**Brought forward:** unmerged Sep 12 submit-gaps work (exact-B + cost/artifact gates), then re-measured and hardened at object tonight.

---

## SHIPPED

1. **Stranger offline compound restored** — exact-overlap `compound-mini-B.txt`; paraphrase preserved as `compound-mini-B-paraphrase.txt` baseline that fails.
2. **Qwen falsifiable gate with baseline arms** — `scripts/eval_compound_cost_arms.py`
   - Arms: **NAIVE** (always re-search) · **PARAPHRASE** (old B wording) · **EXACT** (sealed-prediction shape)
   - Cost from dated Parallel Search **price card** (not invoice): `fixtures/price-cards/parallel-search-2026-09-13.json` (rates re-fetched 2026-09-13; match 2026-09-12 card)
3. **Artifact claims at HEAD** — `scripts/eval_artifact_claims.py` (NAIVE trusts docs; shipping re-derives; soft `N+ claims` forbidden)
4. **Cold-clone false-green closed** — `scripts/verify_cold_clone.sh` captures `COMPOUND_RC`; no `head` SIGPIPE on compound step
5. **Controls** — `tests/test_compound_cost_arms.py` **6/6** (paraphrase watched RED; cold-clone exit capture asserted)
6. **SUBMISSION-PACK truth refresh** — dates/counts re-measured; hosted note corrected to **303→Sign-in** (was wrongly **501**)
7. **Live compound BLOCKED receipt** — keys missing
8. **Deploy prep** — `docs/DEPLOY-PREP-2026-09-13.md` (no deploy run)

---

## VERIFIED (command → object · 2026-09-13)

| Claim | Command | Result |
|-------|---------|--------|
| watch_it_go_red | `python3 tests/test_watch_it_go_red.py` | **72/72** |
| docs gate | `python3 scripts/bench_check_docs.py` | **128/128** |
| refusal baseline | `python3 scripts/eval_refusal_baseline.py` | baseline **5/6**, shipping **6/6**, δ+1 |
| compound cost arms | `python3 scripts/eval_compound_cost_arms.py` | NAIVE fail · PARAPHRASE fail · EXACT A=2→B=1 hits=2 · GATE OK |
| artifact claims | `python3 scripts/eval_artifact_claims.py` | **128/128** + frozen **312** · soft unbound=0 |
| offline compound | `python3 scripts/compound_exhibit_receipt.py` | A=**2**→B=**1**, corpus_hits=**2**, exit 0 |
| cost-arm controls | `python3 tests/test_compound_cost_arms.py` | **6/6** |
| cold-clone RED | force paraphrase B claims → `bash scripts/verify_cold_clone.sh` | **exit 3** + `FAIL: compound_exhibit_receipt.py exited 3` |
| cold-clone GREEN | restore exact B → `bash scripts/verify_cold_clone.sh` | **exit 0** · `=== cold-clone verify OK ===` |
| registry surface | `python3 tests/test_registry_surface.py -q` | **16/16** |
| holdout | `python3 scripts/eval_verify_holdout.py` | HOLDOUT OK · 4 files |
| hosted health | `curl -sf …/health` | `ok` · `mode=private-workspaces` · rev `agent-science-00028-hed` |
| hosted /search | `curl -sS …/search` (no follow) | **303**; `-L` → Sign-in HTML **200** |
| hosted public entry | `curl -sS -L …/` | title **Agent Science · public entry**; `/judge/demo` read-only exhibit |
| live keys | env / `~/.config/keys/` | **missing** |
| demo truth layer | `bash scripts/demo_truth_layer.sh` | exit 0 |
| public repo | `gh repo view Morkeeth/agent-science --json visibility` | **PUBLIC** |

### Cost arms table (re-derived 2026-09-13 — do not carry)

```
arm          A_pc B_pc B_hits finds   $turbo     $adv pass
NAIVE           2    3      0     4   0.0040   0.0200 NO
PARAPHRASE      2    3      0     4   0.0040   0.0200 NO
EXACT           2    1      2     3   0.0030   0.0150 YES
```

Price card: `https://docs.parallel.ai/getting-started/pricing.md` fetched **2026-09-13T22:28:00Z** · turbo/fast **$0.001**/req · **NOT an invoice**.

---

## WRONG / BLOCKED / LEFT BROKEN

1. **main at night start claimed A=2→B=1 while object measured A=2→B=3 hits=0** — false until exact-B restore. Found by running `compound_exhibit_receipt.py`, not by reading.
2. **Sep 12 receipt said hosted `/search` is 501** — wrong tonight; object is **303 → Sign-in**. Corrected in pack + this receipt.
3. **Cost from billing remains unclosed as invoice** — gate uses public price card with date; Parallel console invoice is Oscar-only.
4. **Live compound exhibit BLOCKED** — no `PARALLEL_API_KEY` / `GEMINI_API_KEY` on this VM.
5. **Hosted stranger desk is gone** — `private-workspaces` mode; unauthenticated routes redirect to Sign-in. Offline cold clone is the stranger path.
6. **McNemar on refusal set still n=6, p=1.0** — delta +1 is real, not significant.
7. **NAIVE and PARAPHRASE cost the same** on this fixture ($0.004 turbo) — paraphrase gets zero shelf benefit; only EXACT saves $0.001.
8. **Registry backfill measured 239 rows / 25 SOURCED** locally after boot — older receipts carried "29 SOURCED".
9. **Devpost paste still carries older commit hashes / hosted claim language** — not fully re-audited line-by-line tonight beyond pack control table + soft-number gate.
10. **Video + Devpost + deploy promote** remain Oscar outward acts.

---

## Product execution checkpoint (observed · revision this branch)

| Dimension | Status | Evidence |
|-----------|--------|----------|
| 1. Promised user value | **observed** (offline + hosted public) | Offline: gap/compound with verbatim SOURCED + Parallel drop. Hosted: `/judge/demo` read-only claim exhibit; hostname check |
| 2. Independent use | **partial** | Cold clone one-command works without keys; hosted public entry usable without token; full workspace needs sign-in |
| 3. Distinctive promise | **observed** | Exact-assertion compound + refuse pole + baseline arms that can embarrass us; public entry keeps uncertainty |
| 4. Action and return | **partial** | Offline re-ask compounds; hosted return is workspace login (bearer untested) |
| 5. Access | **observed** (public entry) / **absent** (workspace) | Public repo + offline path + `/` public entry + `/judge/demo`; research workspace requires token |

Subjective: restoring exact-B is the right stranger demo; it also makes the product's exact-assertion integrity visible rather than hidden by a soft match.

---

## Oscar only (not done)

- Deploy / promote candidate revision
- Devpost · video upload · key rotation in console
- Invoice-backed cost line from Parallel billing
- Bearer-token hosted workspace demo for film
