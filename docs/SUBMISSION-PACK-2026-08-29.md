# SUBMISSION PACK — Agentic Cinema · slice 7

**Date:** 2026-09-03 · **Repo:** https://github.com/Morkeeth/agent-science @ `main`  
**Hosted:** https://agent-science-568004190078.us-central1.run.app · **Deadline:** 2026-09-09 14:00 PT  
**Scope:** docs + offline controls — no public repo flip, no video upload, no Devpost submit, no `deploy.sh`

---

## Stranger one-command block (cold clone, no keys)

```bash
git clone https://github.com/Morkeeth/agent-science.git && cd agent-science
bash scripts/verify_cold_clone.sh
python3 tests/test_registry_surface.py -q
python3 scripts/compound_exhibit_receipt.py
bash scripts/demo_truth_layer.sh
python3 ask_registry.py "agentlint" | head -5
```

Offline compound receipt writes `docs/COMPOUND-EXHIBIT-2026-08-29.md` with A=2→B=1 Parallel, corpus_hits≥1 — no Gemini/Parallel keys required.

---

## Quantified done-when (Oscar gates)

| Gate | Requirement | Status | Evidence |
|------|-------------|--------|----------|
| Video | ≤ 3 min (≤ 180 s) | [ ] | Script: `docs/VIDEO-SCRIPT-2026-08-29.md` — beats sum **178 s** |
| Devpost | All mandatory fields filled | [ ] | Paste block below (§1–3 from `PITCH.md`) |
| Public repo | Stranger can clone | [ ] | Private until submit — flip visibility on GitHub |
| OSI licence | Open-source approved | [x] | `LICENSE` (MIT) |
| Sealed prediction | Pre-registered, falsifiable | [x] | `docs/SEALED-PREDICTION-2026-08-31.md` — hosted A=1→B=0, corpus_hits=1 |
| Partner integrations | All four called at runtime | [x] docs | `docs/PARTNER-INTEGRATIONS-2026-08-30.md` |
| ADK default path | `engine_default: adk` | [x] local / [x] hosted | `docs/RECEIPT-adk-default-path-2026-08-30.md` |

**Controls re-measured 2026-09-03** (run each at object):

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
| partner_runtime | `python3 tests/test_partner_runtime.py` | **6/6** |
| parallel_integration | `python3 tests/test_parallel_integration.py` | **6/6** |
| **Total** | 11 suites | **127/127** |
| docs gate | `python3 scripts/bench_check_docs.py` | **127/127 match** |
| holdout freeze | `python3 scripts/eval_verify_holdout.py` | **4 files pinned** |
| scorer symmetry | `python3 scripts/eval_scorer_symmetry.py` | baseline **5/6** vs shipping **6/6** on delivered labels |

**Compound exhibit (offline, 2026-09-03):** `python3 scripts/compound_exhibit_receipt.py` · A=**2**→B=**1** Parallel · B corpus hits=**2** — `docs/COMPOUND-EXHIBIT-2026-08-29.md`. Live hosted (2026-08-31): `long_run_goal.sh` · A=**1**→B=**0** · sealed `docs/SEALED-PREDICTION-2026-08-31.md`. Orphan-works full script: run B **504** — do not claim on video.

**Eval gate:** `docs/QWEN-EVAL-GATE-2026-08-30.md` — baseline **5/6 = 0.833** vs shipping **6/6 = 1.000**, delta +1 (RC5); McNemar p=1.0000 at n=6. Holdout + symmetrical scorer re-run 2026-09-03: `docs/RECEIPT-night-wave-2026-09-03.md`.

---

## Sealed prediction (sealed 2026-08-31 — do not edit)

> **Prediction:** On the hosted URL, a second `POST /clear` with the same `subject` and an overlapping claim returns `corpus_hits ≥ 1` and strictly fewer `parallel_calls` than the first run on a shared corpus shelf.

| Field | Run A (cold) | Run B (warm) | Pass? |
|-------|-------------:|-------------:|-------|
| `parallel_calls` | — | — | B < A |
| `corpus_hits` | 0 expected | ≥ 1 | yes if ≥ 1 |

**Offline receipt (2026-08-29):** `orphan-works` · fixtures `compound-mini-A.txt` → `compound-mini-B.txt` · A=**2** Parallel · B=**1** Parallel · B corpus hits=**2** — `scripts/compound_exhibit_receipt.py`.

**Seal when:** hosted orphan-works A/B on `documentary-orphan-works*.txt` with durable GCS shelf (slice 1 deploy). Until then: draft only.

---

## Devpost paste block (≤ 5000 chars · 3771 chars)

Copy everything between the lines into Devpost project description / inspiration / built-with fields as needed.

---BEGIN DEVPOST PASTE---

## 0 · TRUTH LAYER (lead with this)

> **Agent Science is the truth layer for what agentic builders believe and use** — not another answer engine.

When you or your agent websearches, you get a **full visibility panel**: what was searched (every angle, every tier), what the field runs (GitHub ★, blogs, peers), and a primary verdict — **sourced verbatim**, **refused with cause**, or **CONTRARY TO RESEARCH** when practitioners outrun papers. Stack-fit scores whether a truth fits *your* repo. The shelf compounds: ask once, free forever.

**Try it:** https://agent-science-568004190078.us-central1.run.app/visibility/ui?q=ralph+loop+agentic  
**Truths dashboard:** `/truths/ui` · **265+ claims** on disk

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
agencies · E&O underwriters, who price a risk they currently cannot measure · and the AI
labs on the other side of the table, who cannot pay until provenance exists.

**The one rule the product never breaks:** cite the document, or print that you could not.
No verdict exists in this codebase without a citation — that is enforced in the
constructor, not by convention.

## 2 · WHY IT IS DEFENSIBLE

**The corpus compounds.** Run 1 on `europeana-film-archive.json` (50 items): 0 of 50 reused.
Run 2: **50 of 50 reused, zero network calls** (`review/corpus_compound_receipt.py`).
The second production about the same subject costs a fraction of the first.

**One index, N questions, N buyers.** Asked the same 600 items a second question —
`noncommercial_reuse`, what a university or public-service archive may use — and **247 of
600 (41%) change verdict**, driven by the instruments' own terms with no re-ingest. A
control fails the build if a new use case moves less than 10% of the library, so a second
buyer cannot be asserted, only shown.

**Competitors are channel, not competition.** Troveo, Veritone, Vermillio run
marketplaces and matchmaking. Finding an asset you cannot legally use is worth nothing.
This is the independent evidentiary layer both sides' lawyers need: the audit, not the
market.

## 3 · THE PROOF

| | |
|---|---|
| Repo | `https://github.com/Morkeeth/agent-science` @ `e6793ab` |
| Entry point | `python3 agent_science.py <script.txt>` — Gemini + Parallel **live by default** |
| Hosted | https://agent-science-568004190078.us-central1.run.app — `POST /clear` · `GET /corpus` |
| Controls | registry **16/16** · cross-subject reuse **2/2** · compound exhibit B **1** Parallel vs A **2** (offline) |
| License | `LICENSE` (MIT) |
| Gap report | `fixtures/gap-report-600.md` — **561 of 600 (94%)** not sellable as-is |
| Second question | `fixtures/shift-ai-training-vs-noncommercial.md` — 247 of 600 flip |
| Registry | `python3 ask_registry.py --serve` — every query a browsable row; verbatim span or named refusal |
| Compound receipt | `docs/COMPOUND-EXHIBIT-2026-08-29.md` |

**Always with the denominator.** 94% of *these 600 items*, measured. Never "94% of film
archives" — see below for why that distinction is the demo.

**The single best row, 1 of 600:** an EU orphan work. In copyright, rights-holder not
locatable. **RED under all four questions.** The Orphan Works Directive arguably permits
non-commercial institutional use — but only on a documented diligent search, which is not
on file, so it stays RED. It is the one place the honest answer costs us the better number.

**The demo nobody can call staged:** we pointed the product at *our own marketing*. Five
claims, real sources fetched. Two verified verbatim (C1, C2). One passed on substring match
but misattributes the source (C3). Two failed — and both were ours. C4: EUR-Lex does not
support commercial-use overclaim. C5: **"94% of film archives"** generalised from one
library returned `search_found_no_admissible_source` — the number was never wrong; the
object was.

---END DEVPOST PASTE---

---

## Oscar checklist (outward acts — not done in this slice)

- [ ] `git push` + flip repo to public on GitHub
- [ ] Record video from `docs/VIDEO-SCRIPT-2026-08-29.md` (≤ 180 s)
- [ ] Upload video to Devpost
- [ ] Paste Devpost block + fill remaining fields (built with, links, screenshot)
- [ ] Seal prediction hash in Devpost / commit message after live A/B
- [ ] `bash deploy.sh` — hosted `engine_default: adk` + durable corpus shelf (slice 1)
