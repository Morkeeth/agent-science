---
date: 2026-08-22
event: Agentic Cinema · Devpost · deadline 2026-09-09 14:00 PT
repo: /Users/morkeeth/CODE/cleared @ ab03e3a (local only, never pushed)
status: slice 7 prep @ e6793ab — tests 53 pass / 13 fail (8 suites; watch_it_go_red crashes on missing EUR-Lex body)
---

# The clearance desk for factual production

## 1 · THE COMPANY

> **A production cannot be insured until every fact is sourced and every asset is cleared.
> Both are done by hand today, and a miss is a lawsuit.**

Every documentary, docuseries, true-crime, sports doc and historical drama must produce
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
market. *(Competitor names sourced by cross-review 2026-08-22; re-verify before quoting.)*

## 3 · THE PROOF

| | |
|---|---|
| Repo | `/Users/morkeeth/CODE/cleared` @ `ab03e3a` |
| Entry point | `python3 agent_science.py <script.txt>` — Gemini + Parallel **live by default** |
| Controls | `python3 tests/test_watch_it_go_red.py` → **41 passed, 0 failed** |
| License | `LICENSE` (MIT) |
| Gap report | `fixtures/gap-report-600.md` — **561 of 600 (94%)** not sellable as-is |
| Second question | `fixtures/shift-ai-training-vs-noncommercial.md` — 247 of 600 flip |
| Both legs, one engine | `fixtures/clearance-report-mixed.md` |
| Live script run | `fixtures/scripts/split-sentence.txt` → 1 claim extracted, 1 SOURCED (Parallel found EUR-Lex) |
| The probe that saved the idea | `docs/PROBE-real-rights-instruments.md` |

**Always with the denominator.** 94% of *these 600 items*, measured. Never "94% of film
archives" — see below for why that distinction is the demo.

**The single best row, 1 of 600:** an EU orphan work. In copyright, rights-holder not
locatable. **RED under all four questions.** The Orphan Works Directive arguably permits
non-commercial institutional use — but only on a documented diligent search, which is not
on file, so it stays RED. It is the one place the honest answer costs us the better number.

**The demo nobody can call staged:** we pointed the product at *our own marketing*. Five
claims, real sources fetched. Two verified verbatim (C1, C2). One passed on substring match
but misattributes the source (C3 — see `docs/FINDING-substring-is-not-a-statement.md`).
Two failed — and both were ours. C4: EUR-Lex does not support commercial-use overclaim.
C5: **"94% of film archives"** generalised from one library returned
`search_found_no_admissible_source` — the number was never wrong; the object was.

## 4 · HONEST VERDICT — read this first, not last

**Not yet submittable.** Runtime today: **Gemini ✅ · Parallel ✅ · Agent Builder 🟡**.
All three run on the default `/clear` path and are proved LOCALLY with the API keys
stripped (`docs/RECEIPT-agent-builder.md`). The hackathon requires them on the **hosted**
URL, and the hosted service still serves the pre-ADK revision.

What remains is one command, not a slice: `bash deploy.sh`. It writes a Secret Manager
version, edits IAM and ships a billed public revision, so it is Oscar's click by the
script's own header. Then `curl <hosted>/health` returns `"engine_default": "adk"` and
this line becomes ✅. 72 controls green. Forced-lie transcript replayed against the live
verifier (six for six).

**CORRECTED 2026-08-23 — "GCP access is the blocker where delay compounds" was false, and
it had been false for a while.** It ranked #1 on the board as an Oscar-only item while
project `hack-fleet` already had `billingEnabled: true`, `aiplatform` and
`agentregistry` enabled, and ADC on disk. Nobody probed it; the sentence was carried
forward instead. The genuine unknown it predicted did exist, and it was found in fifteen
minutes of actually running the thing: the ADK client 404s on every regional Vertex
endpoint, because only the `global` location publishes these models — a fact
`clearance/gemini.py:51` had already written down.

## IF THE FORK GOES THE OTHER WAY

- **Nothing in section 2 or 3 changes.** The engine, the citation guard, the corpus, the
  gap report, the second question and both nouns are the middle of both products. The
  FACT leg is already built and tested — Agent Science's engine exists today.
- **What changes:** which end gets built (Gemini shot-level asset indexing vs claim
  extraction from a script) and which partner SDK gets wired — ClickHouse MCP vs Parallel.
  The partner choice is admissibility-critical, because it must be *called at runtime*.
- **What is lost either way: nothing.** No fork-dependent work was started.
