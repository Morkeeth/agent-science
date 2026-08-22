---
date: 2026-08-22
event: Agentic Cinema · Devpost · deadline 2026-09-09 14:00 PT
repo: /Users/morkeeth/CODE/cleared @ 8ce8b7b (local only, never pushed)
status: fork UNRULED — this pitch holds under either ruling
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

**The corpus compounds.** Run 1: 0 of 50 verdicts reused. Run 2: **50 of 50 reused, zero
network calls**, asserted by a tripwire that replaces `urlopen` and fails the build if
anything reaches out. The second production about the same subject costs a fraction of
the first.

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
| Repo | `/Users/morkeeth/CODE/cleared` @ `8ce8b7b` |
| Controls | `python3 tests/test_watch_it_go_red.py` → **31 passed, 0 failed**, coordinator-run on this machine at four separate commits |
| Gap report | `fixtures/gap-report-600.md` — **561 of 600 (94%)** of a real Europeana moving-image sample not sellable as-is |
| Second question | `fixtures/shift-ai-training-vs-noncommercial.md` — 247 of 600 flip |
| Both legs, one engine | `fixtures/clearance-report-mixed.md` |
| The probe that saved the idea | `docs/PROBE-real-rights-instruments.md` |

**Always with the denominator.** 94% of *these 600 items*, measured. Never "94% of film
archives" — see below for why that distinction is the demo.

**The single best row, 1 of 600:** an EU orphan work. In copyright, rights-holder not
locatable. **RED under all four questions.** The Orphan Works Directive arguably permits
non-commercial institutional use — but only on a documented diligent search, which is not
on file, so it stays RED. It is the one place the honest answer costs us the better number.

**The demo nobody can call staged:** we pointed the product at *our own marketing*. Five
claims, real sources fetched. Three verified verbatim. Two failed — and both were ours.
One was an overclaim about the Orphan Works Directive that EUR-Lex does not support. The
other was **"94% of film archives are unclearable"**, our own headline, generalised from
one library to a category, returned `UNKNOWN / no_source_offered`. The number was never
wrong; the object it was attached to was.

## 4 · HONEST VERDICT — read this first, not last

**This is not yet an admissible submission.** The rules require Google Cloud AI *and* the
partner service "imported and actually called" at runtime. Gemini: absent. Agent Builder:
absent. Partner service: absent. The build is a deterministic Python engine.

That clause was quoted into `docs/PHASE1-SPEC-EXTRACT.md` in hour one and never pointed at
the build for six hours. **The document existed; the comparison did not.**

What changed is the shape of the remaining work, not the status. The model's job is
already scoped and its safety net already exists: a **locator** proposes a passage, a
**verifier** proves it occurs verbatim in the fetched document, and five adversarial
proposers are refused — including a real passage lifted from the wrong document. Gemini
becomes a one-file swap behind a red-tested guard. A checked model, not a wrapped one.

**GCP access is the blocker where delay compounds.** The fork costs design time. Hours can
be estimated late. But Agent Builder is a hosted service nobody here has provisioned, and
the first thing you learn provisioning one is what it refuses to do. Failing on Sep 8 is
not a delay — it is the entry.

## IF THE FORK GOES THE OTHER WAY

- **Nothing in section 2 or 3 changes.** The engine, the citation guard, the corpus, the
  gap report, the second question and both nouns are the middle of both products. The
  FACT leg is already built and tested — Agent Science's engine exists today.
- **What changes:** which end gets built (Gemini shot-level asset indexing vs claim
  extraction from a script) and which partner SDK gets wired — ClickHouse MCP vs Parallel.
  The partner choice is admissibility-critical, because it must be *called at runtime*.
- **What is lost either way: nothing.** No fork-dependent work was started.
