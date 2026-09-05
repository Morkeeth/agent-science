# RECEIPT — night wave 2026-09-05 · Sep 9 submit gaps

**Branch:** `cursor/night-wave-sep5-submit-d6b4` · **Base:** `main` @ `69cc6b1`  
**Floor held:** `python3 tests/test_watch_it_go_red.py` → **72 passed, 0 failed**

---

## SHIPPED

1. **Compound exhibit restored under exact-assertion reuse** — `compound-mini-B.txt` uses A's exact overlapping claims + one new claim; offline receipt A=2→B=1, corpus_hits=2. Finding: `docs/FINDING-compound-exact-assertion-2026-09-05.md`.
2. **Qwen artifact-claims gate** — `scripts/eval_artifact_claims.py` · baseline = trust pack · shipping = re-measure at object. Watched **RED** (3 lies) before pack fix; **GREEN** after.
3. **Cost price-card gate** — `scripts/eval_cost_price_card.py` · Parallel Search API Basic list price from `https://www.parallel.ai/pricing` with card-read date · baseline always-search vs shipping compound calls. **Not** a billing-console read.
4. **SUBMISSION-PACK truth refresh** — public-repo row corrected; hosted `private-workspaces` / login wall named; stranger one-command block adds `eval_artifact_claims.py`; compound caveats for exact-assertion.
5. **Deploy prep for current `deploy.sh`** — `docs/DEPLOY-PREP-2026-09-05.md` (candidate/--no-traffic; no Oscar deploy run).
6. **Live compound BLOCKED receipt** — no Parallel/Gemini keys on this VM; hosted `POST /clear` = **401**.

---

## VERIFIED (command → result)

| Claim | Command | Result |
|-------|---------|--------|
| Mutation controls | `python3 tests/test_watch_it_go_red.py` | **72/72** |
| Registry | `python3 tests/test_registry_surface.py -q` | **16/16** |
| Pack suites vs docs | `python3 scripts/bench_check_docs.py` | **128/128 match** |
| Offline compound | `python3 scripts/compound_exhibit_receipt.py; echo $?` | A=**2**→B=**1**, hits=**2**, exit **0** |
| Baseline eval | `python3 scripts/eval_refusal_baseline.py` | baseline **5/6**, shipping **6/6**, delta +1 |
| Ablation | `python3 scripts/eval_refusal_ablation.py` | ablation **5/6**, shipping **6/6** |
| Scorer | `python3 scripts/eval_scorer_symmetry.py` | baseline **5/6**, shipping **6/6** |
| Holdout | `python3 scripts/eval_verify_holdout.py` | **HOLDOUT OK — 4 files** |
| Artifact claims (pre-fix) | `python3 scripts/eval_artifact_claims.py` | **RED** 13/16 — hosted open-UI lie + Private-until-submit lie |
| Artifact claims (post-fix) | `python3 scripts/eval_artifact_claims.py` | **OK** (re-run after pack honesty) |
| Cost price card | `python3 scripts/eval_cost_price_card.py` | shipping beats naive always-search on list price |
| Hosted health | `curl -sS …/health` | `ok: true`, mode **`private-workspaces`**, rev **`agent-science-00026-zel`** |
| Hosted /search | `curl -D- …/search?q=…&live=false` | **303** → login |
| Hosted /clear | `curl -X POST …/clear` | **401** |
| GitHub visibility | `curl …/repos/Morkeeth/agent-science` | `private=false`, `visibility=public` |
| Keys on VM | env + `~/.config/keys/` | **PARALLEL + GEMINI MISSING** |

---

## WRONG / BLOCKED / LEFT BROKEN

1. **Carried compound numbers** — pack claimed A=2→B=1 while HEAD returned A=2→B=3 until fixtures were updated. I almost trusted the Sep 3 receipt; running the object caught it.
2. **Hosted stranger demo is dead on current revision** — `/visibility/ui` and `/search` are login-walled. Devpost paste still needs Oscar scrub for any remaining open-URL marketing outside the pack section fixed tonight.
3. **"Cost from billing" remains open** — price-card gate is falsifiable list-price math only. Parallel/GCP **billing console not read** (no access). Checklist row stays unchecked for true billing.
4. **Live orphan-works / hosted compound** — **BLOCKED**: missing API keys locally; hosted clear **401**. Cannot refresh sealed hosted A/B tonight.
5. **ADK `engine_default` on hosted /health** — gone from health JSON under private-workspaces; pack now marks hosted ADK row unchecked. Local ADK tests still 5/5.
6. **`deploy_prep.sh` still prints old routes** (`/search` open, corpus GCS seed story) and claims `partner_runtime 5/5` while suite is **7/7** — not rewritten beyond the new DEPLOY-PREP doc; Oscar should prefer `docs/DEPLOY-PREP-2026-09-05.md`.
7. **Video + Devpost** — still Oscar outward acts; not touched.

---

## BLOCKED receipt — live compound exhibit

```
DATE: 2026-09-05
PATH: hosted POST /clear orphan-works A/B  OR  local live compound_exhibit.py
PARALLEL_API_KEY: MISSING
GEMINI_API_KEY / ADC: MISSING
HOSTED POST /clear: HTTP 401 (private-workspaces)
AUTHORITATIVE: offline python3 scripts/compound_exhibit_receipt.py → A=2→B=1 hits=2
```

### Cost gate transcript (re-derived)

```
Cost gate — list price from Parallel price card (NOT billing console)
Price card URL:  https://www.parallel.ai/pricing
Card read date:  2026-09-05 UTC
Processor:       Search API · Basic
Basic $/1K:      $5.00  →  $0.0050 per request
Turbo $/1K:      $1.00 (shown for range; not used in arms)
Evidence:        ken dense compressed excerpts Price per request: $0.001 - $0.005 for 10 results Search playground [ Sear

BILLING: not read. Parallel/GCP invoices are Oscar-only. This gate is
falsifiable from the public card + offline compound receipt only.

Arms on offline compound-mini (exact-assertion reuse):
  Baseline (naive always-search): 5 calls × $0.0050 = $0.0250
  Shipping (measured A+B):         3 calls × $0.0050 = $0.0150
  Compound receipt:               A=2 → B=1 parallel, B corpus_hits=2
  Delta (baseline − shipping):    $0.0100 (2 calls avoided)

FINDING: compounding saves list-price dollars vs naive always-search on this path.
LIMITATION: n is the mini exhibit (5 naive vs 3 shipping calls). Not a billing audit.
```

### Artifact-claims RED transcript (before pack honesty)

Baseline 16/16 trust-pack vs shipping **13/16** — failures: `hosted:search`, `hosted:visibility`, `github:public`. Full log: `docs/receipts/artifact-claims-RED-2026-09-05.txt`.

