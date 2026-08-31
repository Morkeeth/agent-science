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

ATTRIBUTION  over the 27 GREEN verdicts the BASE engine produces on research-corpus/,
             0 of which cite a provision at all
  CONFLICT  would refuse 0 of those 0
  ABSENCE   would refuse 0 of those 0

REGISTRY  research-corpus/, 314 claims, offline, doc cache
  BASE      sourced   27  refused  271  unknown   16
  CONFLICT  sourced   27  refused  271  unknown   16
  CONFLICT changes 0 verdict(s) vs BASE — the corpus does not exercise it

WEDGE  via judge_claim, live document (590,271 characters fetched)
  WEDGE-1 expect REFUSED  BASE GREEN  SHIPS UNKNOWN  cited_provision_differs  OK
  WEDGE-2 expect SOURCED  BASE GREEN  SHIPS GREEN                             OK
```

**"Measured on 314 claims, zero false refusals" would be true and it would be the wrong
object.** Zero of the 27 cleared claims on this shelf cite a provision at all, so the
population contains no case the check could have got wrong. A flip count over a
population with no eligible rows reads exactly like a safety result and is not one.

So the honest statement, and the one printed on the front surface:

> On the labelled held-out set it costs nothing: base 6/6, conflict 6/6, absence 6/6,
> unchanged. On the live shelf it changes 0 of 314 verdicts — and **that number is not
> evidence of safety, because 0 of the 27 cleared claims on this shelf cite a provision
> at all.** This corpus cannot exercise the mechanism. Its only evidence is two cases, one
> of which is the case it was built for.

The same emptiness is why the ABSENCE arm's 6/6 is **not** an argument for shipping it.

## What is open

1. **A labelled set for this mechanism.** n=2 and one of them is the motivating case. The
   honest next object is a held-out set of provision-bearing claims — near-misses,
   correct citations, and sub-paragraph cases — labelled before any run.
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
| `tests/test_front_surface.py` | 14 controls on the page itself |
