# RECEIPT — night wave 2026-09-16 · compound truth + cost gate + pack

**Branch:** `cursor/night-wave-compound-truth-053a` · **Consumer:** cursor  
**Started from:** `main` @ `45c8975` · `python3 tests/test_watch_it_go_red.py` → **72/72**

---

## SHIPPED

1. **Exact-match offline compound restored** — paraphrased `compound-mini-B` was making the killer demo RED under exact-assertion reuse; overlapping assertions are now identical; receipt exit 0 (A=2→B=1, corpus_hits=2).
2. **`scripts/eval_compound_paraphrase.py`** — shipping vs naive term-keyed baseline on paraphrased B; naive **beats** shipping (embarrassment finding).
3. **`scripts/eval_cost_gate.py`** — Parallel price card fetched at object (2026-09-16); shipping 3 calls vs always-search 5; billing **UNKNOWN** without invoice.
4. **SUBMISSION-PACK truth refresh** — 128/128 re-measured; public-repo checkbox corrected; hosted login-wall documented; stranger one-command block extended.
5. **Live compound BLOCKED receipt** — keys missing; honest stop.
6. **Deploy prep** — `docs/DEPLOY-PREP-2026-09-16.md` for current `deploy.sh` candidate path (no deploy run).
7. **Finding** — `docs/FINDING-paraphrase-compound-2026-09-16.md`.

---

## VERIFIED (command → result)

| Claim | Command | Result |
|-------|---------|--------|
| watch_it_go_red | `python3 tests/test_watch_it_go_red.py` | **72/72** |
| exact-match compound | `python3 scripts/compound_exhibit_receipt.py` | exit **0** · A=2→B=1 · corpus_hits B=2 |
| paraphrase gate | `python3 scripts/eval_compound_paraphrase.py` | shipping FAIL · naive PASS |
| cost gate | `python3 scripts/eval_cost_gate.py` | card fetch ok · Δcalls +2 · billing UNKNOWN |
| pack counts | `python3 scripts/bench_check_docs.py` | **128/128 match** |
| registry stranger | `python3 tests/test_registry_surface.py -q` | **16/16** |
| refusal baseline | `python3 scripts/eval_refusal_baseline.py` | baseline 5/6 · shipping 6/6 |
| hosted health | `curl …/health` | `private-workspaces` · rev `00028-hed` |
| hosted /search | `curl -L …/search` | **login wall** |
| repo visibility | `gh api repos/Morkeeth/agent-science` | `private: false` |

Raw capture: see this night's shell transcript / `docs/RECEIPT-cost-gate-2026-09-16.json`.

---

## WRONG

1. **I initially trusted SUBMISSION-PACK's A=2→B=1** until `compound_exhibit_receipt.py` exited 3 on the paraphrased fixture — the carried number was false under current engine rules.
2. **Cost from billing is NOT closed** — price-card estimate only; `AGENT_SCIENCE_BILLING_INVOICE_USD` unset; PRIOR LOSS checkbox stays open.
3. **Live orphan-works compound unverified** — no Parallel/Gemini keys; hosted `/clear` path not exercised.
4. **Hosted stranger `/search` free-tier claim was stale** — current revision login-walls it; older receipts that imply logged-out search are wrong for rev `00028-hed`.
5. **Naive term arm labels BL claim UNSOURCED** while shipping labels UNVERIFIED INDEPENDENCE — baseline is deliberately weaker on independence; do not treat naive labels as product-correct.
6. **Cold clone script OK locally** (`bash scripts/verify_cold_clone.sh` exit 0 on this branch) — still not a fresh GitHub clone of the unmerged branch tip.
7. **Registry `stats` n=0 on this VM's local `cache/refusal_log.db`** — backfill row count in compound receipt still prints the hardcoded "29 SOURCED…" parenthetical from the script template while measured backfill_rows was 0; that parenthetical is a carried phrase and should be treated as suspect.

---

## Outward acts not done (Oscar)

Devpost · video upload · deploy promote · key rotation · billing invoice export.
