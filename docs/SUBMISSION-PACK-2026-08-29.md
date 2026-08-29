# SUBMISSION PACK — Agentic Cinema · slice 7

**Date:** 2026-08-29 · **Repo:** https://github.com/Morkeeth/agent-science @ `e6793ab`  
**Hosted:** https://agent-science-568004190078.us-central1.run.app · **Deadline:** 2026-09-09 14:00 PT  
**Scope:** docs only — no public repo flip, no video upload, no Devpost submit, no `deploy.sh`

---

## Quantified done-when (Oscar gates)

| Gate | Requirement | Status | Evidence |
|------|-------------|--------|----------|
| Video | ≤ 3 min (≤ 180 s) | [ ] | Script: `docs/VIDEO-SCRIPT-2026-08-29.md` — beats sum **178 s** |
| Devpost | All mandatory fields filled | [ ] | Paste block below (§1–3 from `PITCH.md`, **3771 chars**) |
| Public repo | Stranger can clone | [ ] | Private until submit — flip visibility on GitHub |
| OSI licence | Open-source approved | [x] | `LICENSE` (MIT) |
| Sealed prediction | Pre-registered, falsifiable | [ ] | Draft below; seal after live corpus exhibit on hosted URL |

**Controls on disk @ `e6793ab`:** `test_registry_surface.py` **5/5** · `test_cross_subject_reuse.py` **2/2** · `test_backfill_seeds_reuse.py` **2/2** · `test_clear_corpus.py` **4/4** · `test_search_path.py` **5/5** · `test_source_map.py` **3/3** · `test_refusal_correctness.py` **6/6** · `test_watch_it_go_red.py` **26 pass / 13 fail** (suite crashes on missing EUR-Lex body) → **53 pass / 13 fail** across 8 suites.

**Compound exhibit (offline, slice 3):** Run A **2** Parallel → Run B **1** Parallel, **2** corpus hits — `docs/COMPOUND-EXHIBIT-2026-08-29.md`.

---

## Sealed prediction (draft — do not edit after seal)

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
| Controls | registry **5/5** · cross-subject reuse **2/2** · compound exhibit B **1** Parallel vs A **2** (offline) |
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
