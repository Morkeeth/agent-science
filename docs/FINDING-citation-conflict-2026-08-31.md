# A live false GREEN worth €20,000,000, and the mechanism that closes it

**2026-08-31, ~04:40–07:40. Branch `night/l5-semantic-guard`.**

## The finding

The lane brief handed to this session asserted that the engine already **refused**
"Article 50 fines = €35M/7%" via a check called `number_not_bound_to_subject`.

Neither the refusal nor the check existed. `grep` finds no such code in the repo, and
the shipping engine **cleared the claim GREEN** against the live document:

```
$ python3 - <<'PY'
import clear_corpus
from clearance.facts import Claim, judge_claim
CLAIM = 'Article 50 transparency breaches are subject to "administrative fines of up to EUR 35 000 000"'
URL = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689"
v = judge_claim(Claim("A50", CLAIM, URL, clear_corpus._must_contain(CLAIM)), fetch=True)
print(v.verdict, v.cause); print(v.quoted_terms)
PY
GREEN None
Non-compliance with the prohibition of the AI practices referred to in Article 5 shall be
subject to administrative fines of up to EUR 35 000 000 or, if the offender is an
undertaking, up to 7 % of its total worldwide annual turnover for the preceding financial
year, whichever is higher.
```

That span is Article **99(3)**, and it is about Article **5**. Article 50 is reached by
Article 99(4)(g) — *"transparency obligations for providers and deployers pursuant to
Article 50"* — whose tier is **EUR 15 000 000 / 3 %**. Both figures on the page are real.
The sentence joining them is false and the difference is €20,000,000.

The span passes every test a keyword-grounded answer applies: it is verbatim, it is in
the cited document, and it carries **73 %** of the claim's content terms.

**The same error is in this repo's own research corpus.**
`research-corpus/2026-08-24-verification-stack-positioning.md` attaches "fines to €35M or
7 %" to the high-risk obligations of Articles 8–17, 26, 27 and 73 — all Article 99(4)
provisions, all €15M / 3 %.

## Why nothing in the guard could see it

A provision citation is **two tokens that mean one thing**, and every similarity path in
`clearance/semantic.py` splits the pair and then discards the number:

```
>>> from clearance import semantic as S
>>> S.content("Article 5")
{'article'}          # "5" is dropped: the filter is len(t) > 1
>>> S.content("Article 50") & S.content("Article 5")
{'article'}          # the claim and the span agree on the only token either can see
```

The check was not too weak. It was **reading the wrong object** — the twelfth instance of
this night's defect class, and the first one found inside the instruction rather than
inside a product.

## The mechanism: `cited_provision_differs`

`clearance/semantic.check_citation`, registered as the fourth mechanism in `CHECKS` and
shipping in `DEFAULT_CHECKS` beside `polarity`.

- `provisions(text)` parses `(head, number)` from **raw text**, before tokenisation.
  Heads are a closed class of legal/technical structural nouns. `Article 33(1)` and
  `Article 33` are one provision; `Article 5` is not a prefix of `Article 50`.
- **The gate is CONFLICT, never absence.** It refuses only when the clause carrying the
  anchor cites a *rival* provision with the same head noun. Absence is ordinary topic
  continuity — the exact reason `binding` and `coverage` were measured and cut as gates
  on 2026-08-31 — so the absence arm is built, run, printed, and **does not ship**.
- **Asymmetric, both ways biased against refusing.** Presence of the claimed provision
  anywhere in the span stands the check down; a rival only counts inside the carrier
  clause.

## Two defects the measurement found, that thinking did not

**1. An exclusion is not a subject.** The gate's first run refused the *true* claim.
Article 99(4)'s carrier clause names exactly one provision, and names it to exclude it —
*"other than those laid down in Articles 5"*. Reading an exception as the clause's subject
refuses the right answer to the very question the exhibit was built around. Closed by
`_EXCLUSION`, another closed class of English, pinned by
`t_an_excluded_provision_is_not_a_rival`.

**2. The control arm was not a control arm.** `inspect()` took `checks=DEFAULT_CHECKS` as
a *default argument*, which Python binds once at import. The eval harness set
`semantic.DEFAULT_CHECKS` to measure a BASE arm and **changed nothing** — BASE silently
ran the treatment. Caught by a receipt printing `BASE=REFUSED` for a case measured GREEN
on the same engine twenty minutes earlier. A harness that substitutes a rule which never
applies makes the control agree with the treatment and reports the agreement as a result.
Pinned by `t_default_checks_is_read_at_call_time_not_bound_at_import`.

## The measurement — and the limit that matters more

`python3 scripts/eval_citation_conflict.py` → `docs/EVAL-citation-conflict-2026-08-31.json`

```
GOLD  fixtures/refusal-correctness/set.json  n=6  labelled 2026-08-22T21:30:00Z
  correct BASE      6/6
  correct CONFLICT  6/6
  correct ABSENCE   6/6

ATTRIBUTION  over the 27 GREEN verdicts the BASE engine produces on the frozen population,
             0 of which cite a provision at all
  CONFLICT  would refuse 0 of those 0
  ABSENCE   would refuse 0 of those 0

REGISTRY  frozen population research-corpus/ (22 files, manifest frozen 2026-08-31), 312 claims, offline, doc cache
  BASE      sourced   27  refused  269  unknown   16
  CONFLICT  sourced   27  refused  269  unknown   16
  ABSENCE   sourced   27  refused  269  unknown   16
  CONFLICT changes 0 verdict(s) vs BASE — the corpus does not exercise it

WEDGE  via judge_claim, live document (590,271 characters fetched)
  WEDGE-1 expect REFUSED  BASE GREEN  SHIPS UNKNOWN  cited_provision_differs  OK
  WEDGE-2 expect SOURCED  BASE GREEN  SHIPS GREEN                             OK
```

**"Measured on 312 claims, zero false refusals" would be true and it would be the wrong
object.** Zero of the 27 cleared claims on this shelf cite a provision at all, so the
population contains no case the check could have got wrong. A flip count over a
population with no eligible rows reads exactly like a safety result and is not one.

So the honest statement, and the one printed on the front surface:

> On the labelled held-out set it costs nothing: base 6/6, conflict 6/6, absence 6/6,
> unchanged. On the frozen shelf it changes 0 of 312 verdicts — and **that number is not
> evidence of safety, because 0 of the 27 cleared claims on this shelf cite a provision
> at all.** This corpus cannot exercise the mechanism. Its only evidence is two cases, one
> of which is the case it was built for.

The same emptiness is why the ABSENCE arm's 6/6 is **not** an argument for shipping it.

## The adversarial pass — an independent held-out probe, and what it found

The lane closed saying its evidence was n=2. An adversarial session built the population
that did not exist: **11 provision-bearing claims against the same Regulation, labelled
before any run** (8 true claims whose anchor is verbatim under the article it names, 3
false near-misses whose anchor is verbatim under a *different* article).

```
$ python3 scripts/probe_citation_heldout.py   # BASE=polarity  SHIPS=polarity+citation
id   label     BASE     SHIPS    agrees?  code
T1   SOURCED   GREEN    GREEN    OK
T2   SOURCED   GREEN    GREEN    OK
T3   SOURCED   UNKNOWN  UNKNOWN  WRONG    not_a_statement     <- pre-existing, both arms
T4   SOURCED   GREEN    GREEN    OK
T5   SOURCED   GREEN    GREEN    OK
T6   SOURCED   GREEN    GREEN    OK
T7   SOURCED   GREEN    GREEN    OK
T8   SOURCED   GREEN    GREEN    OK
F1   REFUSED   GREEN    UNKNOWN  OK       cited_provision_differs
F2   REFUSED   GREEN    UNKNOWN  OK       cited_provision_differs
F3   REFUSED   GREEN    GREEN    WRONG                        <- a live false GREEN
SHIPS 9/11   BASE 7/11
```

**The gate costs nothing here and closes two of three.** It introduced **zero** false
refusals: every arm that moved, moved from a false GREEN to a refusal. T3 is refused
identically by BASE — a pre-existing locator behaviour (`419 characters — a page, not a
passage`), not this mechanism.

**F3 is the finding.** The claim *"Article 5 breaches attract 'fines not exceeding 3 % of
their annual total worldwide turnover'"* is false — Article 5 is the 35M/7 % tier — and
the shipping engine clears it **GREEN** on Article 101(1), a paragraph about
general-purpose AI models. It is WEDGE-1 again, in the same document.

```
provisions(claim)  = [('article', '5')]
provisions(span)   = []
carrier provisions = []
conflict finding   = None
absence finding    = cited_provision_absent: the claim is about Article 5 and the span
                     never names it
```

**The gate's recall boundary, stated exactly: it closes the error only when the rival
provision is cited BY NUMBER inside the carrier clause.** Article 101 names its subject
by description — "providers of general-purpose AI models" — so there is no rival numeral
to conflict with, and only the ABSENCE arm, which does not ship, catches it. That is not
an argument to ship ABSENCE; it is the measurement the held-out set was supposed to
produce, and it says the shipped gate is a *partial* answer to the class it was built
for. The pitch must say "refuses this shape of the error", never "refuses the error".

**A fourth false case was written and withdrawn, and the wrong label was mine.** `F4`
asserted "Annex IV sets out the technical documentation … for GPAI models" and was
labelled REFUSED; the engine returned SOURCED and the engine is right — the span it
found *is* Annex IV. The case was written to demonstrate the roman-numeral blind spot and
does not. It is recorded in the probe rather than deleted, because scoring against a
label the author got wrong is this repo's own founding defect committed inside the probe
built to find it. **The reportable score is 9/11 vs 7/11, not 9/12 vs 7/12.**

**A second boundary, in the parser.** `provisions()` requires an arabic numeral:

```
>>> S.provisions("Annex III high-risk")   -> []
>>> S.provisions("Annex IV")              -> []
>>> S.provisions("Articles 8-17")         -> [('article', '8')]   # the range collapses
```

Roman-numbered provisions are invisible, and in this exhibit's own instrument the
high-risk list is **Annex III** and the technical documentation is **Annex IV**. A claim
about one, cleared on a span about the other, is the identical error and this mechanism
cannot see it.

## The population was a mutable write target — CLOSED 2026-08-31 (wave 5)

`clearance/ingest.py::append_markdown` wrote dated claim files **into
`research-corpus/`** — the same directory `eval_citation_conflict.py` replays as its
measurement population. So using the product changed its own published denominator: the
night read n=313, then n=314 an hour later when a parallel lane ingested a claim, and a
clean checkout read 312, because two of "the 314" were untracked files the product had
written to itself.

**The control was written first and watched go red against that layout:**

```
$ python3 tests/test_frozen_population.py          # 2026-08-31 ~05:50, before the fix
FAIL  test_using_the_product_does_not_move_its_own_denominator:
      one append_markdown() call changed the frozen population: 312 -> 313 claims
      (extra: ['2026-08-31-t-frozen-population-probe.md'])
FAIL  test_ingest_does_not_write_into_the_measurement_population:
      ingest writes into the measured population: .../cleared/research-corpus
FAIL  test_no_published_number_is_computed_over_the_live_sink:
      ['eval_citation_conflict.py', 'eval_semantic_guard.py', 'clear_corpus.py']
FAIL  test_the_written_instructions_point_at_the_sink_not_the_population:
      AGENTS.md tells a writer to append to the FROZEN population
FAIL  test_the_evals_resolve_their_population_through_the_frozen_gate
3/8 passed
```

The fix separates the two directories and pins the frozen one by hash:

| | |
|---|---|
| `research-corpus/` | **FROZEN.** Committed, hashed in `MANIFEST.json` (22 files, 312 claims, frozen 2026-08-31). Replayed by both evals through `clearance.population.frozen_dir()`, which raises rather than measure a drifted directory. Nothing in the product writes here. |
| `research-inbox/` | **LIVE.** Where `clearance.ingest` writes. No published number is computed over it. |

Three writers had to be closed, not one: `ingest.py`, **`AGENTS.md`** (which told the
fleet to append research to `research-corpus/`) and the `science_ingest` MCP tool
description. An agent recontaminates a frozen corpus by following prose, so the prose is
pinned by a control too. The manifest is generated from `git ls-files`, so it can only
ever freeze content a clean checkout also has — which is the property that failed.

**The honest number, with its command and its population:**

```
$ python3 scripts/eval_citation_conflict.py                    2026-08-31 ~05:45
REGISTRY  frozen population research-corpus/ (22 files, manifest frozen 2026-08-31),
          312 claims, offline, doc cache
  BASE / CONFLICT / ABSENCE   sourced 27   refused 269   unknown 16
  CONFLICT changes 0 verdict(s) vs BASE — the corpus does not exercise it
GOLD  base 6/6  conflict 6/6  absence 6/6
```

Every conclusion is untouched: still 27 cleared, still 0 of them citing a provision,
still 0 flips. Only the denominator is now reproducible — and it reads 312 everywhere it
is printed, because the surface reads it from the receipt rather than from a literal.

**The sweep for the same pattern.** `eval_semantic_guard.py` had the identical
contamination and is fixed the same way. Every other eval (`eval_refusal_baseline`,
`eval_refusal_ablation`, `eval_stats`, `eval_external_anchor`) computes over
`fixtures/refusal-correctness/set.json`, a committed labelled file. The receipts
(`compound_exhibit_receipt`, `second_subject_receipt`, `wedge_receipt`) compute over
named fixture scripts. The one remaining figure over a growing directory is the registry
database itself — **that is the live shelf by design**, it is allowed to grow, and after
the wave-4 fix the page names it as a different population from the corpus.

## What is open

1. ~~**A labelled set for this mechanism.**~~ BUILT by the adversarial pass:
   `scripts/probe_citation_heldout.py`, 11 provision-bearing claims labelled before any
   run — SHIPS 9/11 vs BASE 7/11, zero false refusals introduced. What stays open is its
   size and the two rows it misses (below).
2. **A corpus that exercises it.** Legal and regulatory sources are where citations live;
   `research-corpus/` is an AI-industry corpus and contains almost none.
3. The absence arm stays built, measured and off.

## Files

| Path | What |
|---|---|
| `clearance/semantic.py` | `check_citation`, `provisions`, `_EXCLUSION`, the call-time `DEFAULT_CHECKS` fix |
| `clearance/wedge.py` | the exhibit — INPUTS and provenance only, no verdict, no span, no number |
| `scripts/wedge_receipt.py` | runs the engine, writes `fixtures/wedge/receipt.json`, seeds the registry |
| `scripts/eval_citation_conflict.py` | three arms, two populations, the wedge |
| `tests/test_citation_conflict.py` | 21 controls, every one run RED first |
| `tests/test_front_surface.py` | 19 controls on the page itself |
