---
date: 2026-08-22
lane: HACK AGENT SCIENCE
project: CLEARED
event: Agentic Cinema (Devpost) — deadline 2026-09-09 14:00 PT
status: STOPPED — blocked on Oscar's ruling, not on work
---

# CLOSING FOUR LINES

**HEADLINE**
A clearance engine that cannot assert anything it has not read — and it caught its own
pitch overclaiming. 94% of 600 real Europeana film items are not sellable as-is, every
verdict citing a live instrument and quoting its operative clause verbatim.

**VISION**
An institution cannot act on a claim, only on evidence. Studios, broadcasters, leagues
and estates are sitting on libraries they cannot sell into the AI-licensing market
because nobody can prove, asset by asset, what they are allowed to do with them. CLEARED
is the evidentiary layer both sides' lawyers need: one engine, two nouns — a fact with no
source and an asset with no rights instrument are the same record — answering N questions
against one index, and printing what it cannot clear, with the reason.

**PROOF**
- Repo: `/Users/morkeeth/CODE/cleared` @ `e13f430` (local only — never pushed, no licence
  file, no hosted URL; every outward act held for Oscar)
- `python3 tests/test_watch_it_go_red.py` → **31 passed, 0 failed**, coordinator-run twice
  on this machine, not self-reported
- `/Users/morkeeth/CODE/cleared/fixtures/gap-report-600.md` — 561 of 600 (94%) blocked
- `/Users/morkeeth/CODE/cleared/fixtures/shift-ai-training-vs-noncommercial.md` — 247 of
  600 (41%) change verdict on the second question, no re-ingest, network tripwire green
- `/Users/morkeeth/CODE/cleared/fixtures/clearance-report-mixed.md` — facts and assets in
  one table, one engine
- `/Users/morkeeth/CODE/cleared/docs/PROBE-real-rights-instruments.md` — the probe that
  killed the "you can only demo this with an invented contract" gate
- `/Users/morkeeth/CODE/cleared/docs/FINDING-refusal-correctness.md` — the next control,
  named and unbuilt
- `/Users/morkeeth/CODE/cleared/docs/SPEC-refusal-correctness-set.md` — its design, written
  while blocked; still not built
- `/Users/morkeeth/CODE/cleared/clearance/verify.py` — the guard a model plugs into: five
  adversarial proposers refused, including a real passage lifted from the wrong document

**ADMISSIBILITY — stated first because it is the thing most likely to be misread**
As of `e13f430` this repo is **NOT an admissible submission.** The rules require Google
Cloud AI *and* the partner service "imported and actually called" at runtime. Gemini:
absent. Agent Builder: absent. ClickHouse MCP: absent. I quoted that clause into
`docs/PHASE1-SPEC-EXTRACT.md` in hour one and built for six hours without pointing it at
the build — the document existed; the comparison did not. What has changed is the shape of
the remaining work, not the status: the Gemini slice is now a one-file swap behind a
red-tested guard. Agent Builder is a hosted GCP service, so this lane now sits behind
Oscar's GCP gate as well as behind his fork ruling.

**HONEST VERDICT**
The middle is built and the ends are not, deliberately. Everything here is true whether
Oscar rules CLEARED or Agent Science; nothing fork-dependent was started. Four defects in
this repo were the product committing the exact error it exists to catch — quoting one
document while citing another, on 35 real items, while every test passed. Each was found
by rendering the output and looking at it, never by reading the source. The number that
went furthest wrong was not wrong: 94% was attached to the wrong noun. The lane is
stopped, not finished: fork · hours available Sep 1–9 · the AnotherBlock beats.
