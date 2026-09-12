# RECEIPT — night wave 2026-09-12 (compound regression · cost gate · pack truth)

**Branch:** `cursor/night-wave-submit-gaps-5210` · **Mode:** offline (no Parallel/Gemini keys on this VM)  
**Floor:** `python3 tests/test_watch_it_go_red.py` → **72/72** (start of night)

---

## SHIPPED

1. **Qwen falsifiable gate with baseline arm** — `scripts/eval_compound_cost_arms.py`
   - Arms: **NAIVE** (always re-search) · **PARAPHRASE** (old compound-mini-B wording) · **EXACT** (sealed-prediction shape)
   - Cost from dated Parallel Search **price card** (not invoice): `fixtures/price-cards/parallel-search-2026-09-12.json`
2. **Artifact claims at HEAD** — `scripts/eval_artifact_claims.py` (NAIVE trusts docs; shipping re-derives; soft `265+` removed)
3. **Stranger offline compound restored** — `compound-mini-B.txt` exact-overlap + one new claim; paraphrase preserved as `compound-mini-B-paraphrase.txt`
4. **Controls** — `tests/test_compound_cost_arms.py` (paraphrase watched RED; exact watched GREEN)
5. **SUBMISSION-PACK truth refresh** — counts re-measured at object; public-repo row corrected; hosted private-workspaces noted
6. **Live compound BLOCKED receipt** — keys missing; hosted `/search` **501** unauthenticated
7. **Deploy prep refresh** — `docs/DEPLOY-PREP-2026-09-12.md` matching current `deploy.sh` (candidate tag; no deploy run)

---

## VERIFIED (command → object)

| Claim | Command | Result |
|-------|---------|--------|
| watch_it_go_red | `python3 tests/test_watch_it_go_red.py` | **72/72** |
| docs gate | `python3 scripts/bench_check_docs.py` | **128/128** |
| refusal baseline | `python3 scripts/eval_refusal_baseline.py` | baseline **5/6**, shipping **6/6**, δ+1 |
| compound cost arms | `python3 scripts/eval_compound_cost_arms.py` | NAIVE fail · PARAPHRASE fail · EXACT A=2→B=1 hits=2 · GATE OK |
| artifact claims | `python3 scripts/eval_artifact_claims.py` | **128/128** + frozen **312** · soft unbound=0 |
| offline compound | `python3 scripts/compound_exhibit_receipt.py` | A=**2**→B=**1**, corpus_hits=**2**, exit 0 |
| cost-arm controls | `python3 tests/test_compound_cost_arms.py` | **5/5** |
| registry surface | `python3 tests/test_registry_surface.py -q` | **16/16** |
| holdout | `python3 scripts/eval_verify_holdout.py` | HOLDOUT OK · 4 files |
| hosted health | `curl -sf …/health` | `ok` · `mode=private-workspaces` · rev `agent-science-00028-hed` |
| hosted /search | `curl -sI …/search` | **501** (local-only routes retired on hosted) |
| live keys | `test -n "$PARALLEL_API_KEY"` / `gemini.key` | **missing** |

### Cost arms table (re-derived 2026-09-12 — do not carry)

```
arm          A_pc B_pc B_hits finds   $turbo     $adv pass
NAIVE           2    3      0     4   0.0040   0.0200 NO
PARAPHRASE      2    3      0     4   0.0040   0.0200 NO
EXACT           2    1      2     3   0.0030   0.0150 YES
```

Price card: `https://docs.parallel.ai/getting-started/pricing.md` fetched **2026-09-12T13:12:00Z** · turbo/fast **$0.001**/req · **NOT an invoice**.

---

## WRONG / BLOCKED / LEFT BROKEN

1. **SUBMISSION-PACK claimed A=2→B=1 on paraphrase B** after 2026-09-04 exact-assertion binding — **false at object** until tonight's fixture fix. Found by running `compound_exhibit_receipt.py`, not by reading.
2. **Cost from billing remains unclosed as invoice** — gate uses public price card with date; Parallel console invoice is Oscar-only. Checklist row updated to say so.
3. **Live compound exhibit BLOCKED** — no `PARALLEL_API_KEY` / `GEMINI_API_KEY` on this VM.
4. **Hosted stranger `/search` is 501** under `private-workspaces` mode — pack previously implied open `/search` on the hosted URL. Do not claim unauthenticated hosted search.
5. **McNemar on refusal set still n=6, p=1.0** — delta +1 is real, not significant.
6. **NAIVE and PARAPHRASE cost the same** on this fixture ($0.004 turbo) — paraphrase gets zero shelf benefit; only EXACT saves $0.001. Embarrassing for any pitch that treated paraphrased "same claim" as free.
7. **Registry backfill measured 239 rows / 25 SOURCED** locally after boot — older receipts carried "29 SOURCED"; compound receipt no longer prints that carried figure.
8. **Pack soft `265+ claims`** was unbound — removed; frozen denominator is **312** via `freeze_population.py --check`. Hosted `298 claims` in `submission/DEVPOST-PASTE.md` was **not** re-verified tonight (private-workspaces; no bearer).
9. **Submit-tag seal** of artifact claims still Oscar — gate measures HEAD, not a future Devpost commit.

---

## Oscar only (not done)

- Deploy / promote candidate revision
- Devpost · video upload · key rotation in console
- Invoice-backed cost line from Parallel billing
