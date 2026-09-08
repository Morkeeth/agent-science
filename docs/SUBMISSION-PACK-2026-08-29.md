# SUBMISSION PACK — Agentic Cinema · slice 7

**Date:** 2026-09-08 · **Repo:** https://github.com/Morkeeth/agent-science @ `main` (PUBLIC since 2026-08-22)  
**Hosted:** https://agent-science-568004190078.us-central1.run.app · **Deadline:** 2026-09-09 14:00 PT  
**Scope:** docs + offline controls + artifact-claim gate — no deploy, no video upload, no Devpost submit

---

## Stranger one-command block (cold clone, no keys, no network beyond git)

```bash
git clone https://github.com/Morkeeth/agent-science.git && cd agent-science
bash scripts/verify_cold_clone.sh
python3 scripts/seed_document_cache.py
python3 tests/test_registry_surface.py -q
python3 scripts/compound_exhibit_receipt.py
python3 -m clearance lookup "2012/28/EU"
python3 scripts/eval_artifact_claims.py
bash scripts/demo_truth_layer.sh
```

Offline compound receipt writes `docs/COMPOUND-EXHIBIT-2026-08-29.md` with A→B Parallel drop + corpus_hits≥1 — no Gemini/Parallel keys required. Free CELEX lookup uses the seeded document cache (EUR-Lex live fetch often 403).

---

## Quantified done-when (Oscar gates)

| Gate | Requirement | Status | Evidence |
|------|-------------|--------|----------|
| Video | ≤ 3 min (≤ 180 s) | [ ] | Script: `docs/VIDEO-SCRIPT-2026-08-29.md` — beats sum **178 s** |
| Devpost | All mandatory fields filled | [ ] | Paste block below; **do not claim unauthenticated hosted /search** |
| Public repo | Stranger can clone | [x] | `gh api repos/Morkeeth/agent-science --jq .visibility` → **public** (since 2026-08-22) |
| OSI licence | Open-source approved | [x] | `LICENSE` (MIT) |
| Sealed prediction | Pre-registered, falsifiable | [x] | `docs/SEALED-PREDICTION-2026-08-31.md` — offline compound still holds; hosted public desk **withdrawn** |
| Partner integrations | All four called at runtime | [x] docs | `docs/PARTNER-INTEGRATIONS-2026-08-30.md` |
| ADK default path | `engine_default: adk` | [x] local | Hosted health is now `mode=private-workspaces` (no public ADK desk) |

**Controls re-measured 2026-09-08** (run each at object):

| Suite | Command | Result |
|-------|---------|--------|
| watch_it_go_red | `python3 tests/test_watch_it_go_red.py` | **72/72** |
| adk_default_path | `python3 tests/test_adk_default_path.py` | **5/5** |
| registry_surface | `python3 tests/test_registry_surface.py` | **16/16** |
| cross_subject_reuse | `python3 tests/test_cross_subject_reuse.py` | **2/2** |
| backfill_seeds_reuse | `python3 tests/test_backfill_seeds_reuse.py` | **2/2** |
| clear_corpus | `python3 tests/test_clear_corpus.py` | **4/4** |
| search_path | `python3 tests/test_search_path.py` | **5/5** |
| source_map | `python3 tests/test_source_map.py` | **3/3** |
| refusal_correctness | `python3 tests/test_refusal_correctness.py` | **6/6** |
| partner_runtime | `python3 tests/test_partner_runtime.py` | **7/7** |
| parallel_integration | `python3 tests/test_parallel_integration.py` | **6/6** |
| **Total** | 11 suites | **128/128** |
| docs gate | `python3 scripts/bench_check_docs.py` | **128/128 match** |
| holdout freeze | `python3 scripts/eval_verify_holdout.py` | **4 files pinned** |
| scorer symmetry | `python3 scripts/eval_scorer_symmetry.py` | baseline **5/6** vs shipping **6/6** on delivered labels |
| artifact claims | `python3 scripts/eval_artifact_claims.py` | baseline vs shipping at object |

**Compound exhibit (offline, 2026-09-08):** `python3 scripts/compound_exhibit_receipt.py` · exact-claim integrity — Run B repeats A's assertion text for overlapping claims · A=**2**→B=**1** Parallel · B corpus hits=**2** — `docs/COMPOUND-EXHIBIT-2026-08-29.md`.

**Hosted boundary (measured 2026-09-08 at object):** revision `agent-science-00026-zel`, `mode=private-workspaces`. Unauthenticated `/search`, `/clear`, `/registry`, `/visibility/ui`, `/truths/ui`, `/partners`, `/stats` return **303 → sign-in**. `/health` is public JSON. Private `/cases` requires a workspace access token. **Do not film or Devpost-link the old public desk URLs.** Stranger path for submit = cold clone + local commands above. Optional hosted inspector: sign-in at `/cases` (Oscar token).

**Eval gate:** `docs/QWEN-EVAL-GATE-2026-08-30.md` — refusal baseline **5/6** vs shipping **6/6**. Artifact-claim gate: `scripts/eval_artifact_claims.py` (this wave).

---

## Sealed prediction (sealed 2026-08-31 — do not edit)

> **Prediction:** On the hosted URL, a second `POST /clear` with the same `subject` and an overlapping claim returns `corpus_hits ≥ 1` and strictly fewer `parallel_calls` than the first run on a shared corpus shelf.

| Field | Run A (cold) | Run B (warm) | Pass? |
|-------|-------------:|-------------:|-------|
| `parallel_calls` | — | — | B < A |
| `corpus_hits` | 0 expected | ≥ 1 | yes if ≥ 1 |

**Offline receipt (2026-09-08):** `orphan-works` · fixtures `compound-mini-A.txt` → `compound-mini-B.txt` (exact overlapping assertions) · A=**2** Parallel · B=**1** Parallel · B corpus hits=**2** — `scripts/compound_exhibit_receipt.py`.

**Hosted status:** public unauthenticated `/clear` is **not** on revision `00026-zel`. Seal remains a historical hosted measure; current authoritative compound for submit is the offline receipt.

---

## Devpost paste block (≤ 5000 chars)

Copy everything between the lines into Devpost. Prefer local cold-clone demo links over hosted desk URLs.

---BEGIN DEVPOST PASTE---

## 0 · TRUTH LAYER (lead with this)

> **Agent Science is the truth layer for what agentic builders believe and use** — not another answer engine.

When you or your agent websearches, you get a **full visibility panel**: what was searched (every angle, every tier), what the field runs (GitHub ★, blogs, peers), and a primary verdict — **sourced verbatim**, **refused with cause**, or **CONTRARY TO RESEARCH** when practitioners outrun papers. The shelf compounds: ask once, free forever — **exact assertion reuse**, not paraphrase.

**Try it (cold clone, no keys):**
`git clone https://github.com/Morkeeth/agent-science && cd agent-science && bash scripts/verify_cold_clone.sh`

**Hosted:** private research workspace at the service URL (access token). Unauthenticated public desk routes were withdrawn; film the local desk or signed-in `/cases`.

Clearance and E&O insurance? One paying vertical on the same layer — sections below.

## 1 · THE COMPANY

> **A production cannot be insured until every fact is sourced and every asset is cleared.
> Both are done by hand today, and a miss is a lawsuit.**

Every documentary, docseries, true-crime, sports doc and historical drama must produce
two reports before it can be insured and released. E&O cover is mandatory for
distribution and requires both. Humans do this work now, slowly and expensively.

And a second market opened this year: rights-holders trying to license libraries to AI
companies, with those deals dying in due diligence for one reason — **nobody can prove
provenance at asset level.**

**Buyers:** studios · broadcasters · sports leagues · stock libraries · estates · ad
agencies · E&O underwriters · and the AI labs on the other side of the table.

**The one rule the product never breaks:** cite the document, or print that you could not.
No verdict exists in this codebase without a citation — enforced in the constructor.

## 2 · WHY IT IS DEFENSIBLE

**The corpus compounds.** Run 1 on `europeana-film-archive.json` (50 items): 0 of 50 reused.
Run 2: **50 of 50 reused, zero network calls** (`review/corpus_compound_receipt.py`).
The second production about the same subject costs a fraction of the first.

**One index, N questions, N buyers.** Asked the same 600 items a second question —
`noncommercial_reuse` — and **247 of 600 (41%) change verdict**, driven by the instruments'
own terms with no re-ingest.

**Competitors are channel, not competition.** Troveo, Veritone, Vermillio run
marketplaces. Finding an asset you cannot legally use is worth nothing. This is the
independent evidentiary layer: the audit, not the market.

## 3 · THE PROOF

| | |
|---|---|
| Repo | `https://github.com/Morkeeth/agent-science` (public, MIT) |
| Entry point | `python3 agent_science.py <script.txt>` — Gemini + Parallel **live by default** |
| Hosted | private workspaces — `/cases` with access token; `/health` public |
| Controls | registry **16/16** · cross-subject reuse **2/2** · offline compound A=**2**→B=**1** Parallel |
| License | `LICENSE` (MIT) |
| Gap report | `fixtures/gap-report-600.md` — **561 of 600 (94%)** not sellable as-is |
| Second question | `fixtures/shift-ai-training-vs-noncommercial.md` — 247 of 600 flip |
| Compound receipt | `docs/COMPOUND-EXHIBIT-2026-08-29.md` |

**Always with the denominator.** 94% of *these 600 items*, measured. Never "94% of film
archives."

**The demo nobody can call staged:** we pointed the product at *our own marketing*. Five
claims, real sources. C5: **"94% of film archives"** generalised from one library returned
`search_found_no_admissible_source` — the number was never wrong; the object was.

---END DEVPOST PASTE---

---

## Oscar checklist (outward acts — not done in this slice)

- [x] Repo public on GitHub (since 2026-08-22) — no flip needed
- [ ] Record video from `docs/VIDEO-SCRIPT-2026-08-29.md` (≤ 180 s) — **film local desk or signed-in `/cases`, not withdrawn public `/visibility/ui`**
- [ ] Upload video to Devpost
- [ ] Paste Devpost block + fill remaining fields (built with, links, screenshot)
- [ ] Decide: restore a public judge desk revision **or** submit on cold-clone + private workspace narrative (`docs/DEPLOY-PREP-2026-09-08.md`)
- [ ] `bash deploy.sh` only if restoring/changing hosted — candidate tag, then promote (Oscar)
