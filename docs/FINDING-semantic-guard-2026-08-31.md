---
date: 2026-08-31
status: CLOSED — RC5 promoted out of `engine_limit` into the enforced pole
supersedes: docs/FINDING-substring-is-not-a-statement.md (status: OPEN since 2026-08-22)
run: `python3 scripts/eval_semantic_guard.py`
receipt: docs/EVAL-semantic-guard-2026-08-31.json
---

# The verifier could not read the claim, because it was never given the claim

## The hole

`clearance.verify` proves a passage is **real** (verbatim in the fetched document) and
that it **mentions** the claim's distinctive term. Neither fact can establish that the
passage *asserts* the claim. RC5, in the held-out set since 2026-08-22:

```
claim  "This Item is free of known copyright restrictions worldwide."
span   "Some collections elsewhere are free of known copyright restrictions;
        this Item is not one of them until evaluated."
```

Verbatim. Carries the terms. Says the opposite. **GREEN.**

## The diagnosis that was available and wrong

The attractive reading is *the check was too weak*. It is not. The signature is
`verify(passage, document=, must_contain=)` — **the claim is not a parameter.** Support is
a relation between two texts and only one of them was ever in the room. No amount of
structural strength closes that; the fix is a parameter first and an algorithm second.

## What was built

`clearance/semantic.py`. Three separately-attributable checks over a closed class of
English function words. Behind `CLEARANCE_SEMANTIC_GUARD`; `=0` reproduces the
2026-08-30 engine exactly, including this false GREEN, and a control asserts it.

Written **red first**: `tests/test_semantic_guard.py` was run against a fully wired,
completely inert null guard. 4 behavioural controls failed for their own reason, 9
passed — including the false-refusal controls, proving the suite can tell the two
directions apart before either was implemented.

## The measurement changed the design twice

### 1. The first arm made the product WORSE — 5/6 → 4/6 on the held-out set

RC1 and RC2 flipped to refusals. Reading the spans rather than the score:

| id | span the shipping engine had cleared GREEN on |
|---|---|
| RC1 | `<nav><a href="#">29 October 2014</a></nav>` — a navigation link |
| RC2 | `Parliament and of the Council of 25 October 2012…` — the wrong sentence |

The term occurs **twice** in that document and the locator returned occurrence one. Both
scored as *correct* because `set.json` labels whether a claim is SUPPORTED and **never
which span supported it**. Two false GREENs sitting inside the labelled-correct column of
the fixture written to catch false GREENs.

So the guard was never costing true GREENs. It was exposing a defect the set could not
see. The fix is not a softer threshold — the locator now yields **candidates** and the
best admissible span wins (`clearance/facts.py::_admissible`). New control
`t_shipping_path_greens_supported_items_on_the_RIGHT_span` asserts *which* span cleared
each supported item.

Two locator defects fell out of that, both real:

- `_start_of_statement` required a capitalised word followed by a lowercase one, so
  **"Member States shall bring into force…" could only start at "States"** — an EU
  directive's operative provision quoted from its second word.
- the look-back window (130 chars) was **shorter than the sentence it was trying to find
  the start of**, and opened inside the word "Member".

### 2. Two of the three checks were cut as gates

`binding` and `coverage` both refuse **this product's own canonical claim**:

```
claim  "An 'In Copyright' item requires permission"
span   "For other uses you need to obtain permission from the rights-holder(s)."
```

That span is the operative clause of the instrument and the claim is a fair paraphrase of
it. The claim's subject sits in the *previous* sentence, because that is how English
works — topic continuity, not repetition. A gate demanding every clause restate its own
subject refuses ordinary prose, and refuse-everything is a failure this repo has already
lost a day to.

They were kept, exported and measured. **`coverage` is used where it is sound: to prefer
one admissible span over another.** Choosing the better of two legitimate spans costs
nothing; refusing a legitimate span costs a claim.

**Shipped gate: `polarity` only.** RC5 falls to it twice over.

## Two more defects, found by reading the flipped rows

- **"not A but B" is a correction, not a denial.** The guard refused *"these files are
  not static documentation **but** … evolve like configuration code"* — a sentence that
  states the claim. Two bugs in one row: the carrier clause was found by searching each
  clause for `must_contain`, which fails whenever the term ends on the punctuation the
  splitter has just consumed; and `but` was read as though it were `;`.
- **`fails`, `lacks`, `unable` were in the negator list.** They are lexical verbs, and the
  module's own docstring claims a closed class of function words. The list contradicted
  its own stated principle and nobody noticed until it refused a real span ending
  *"…then fails."*

Both pinned by controls.

## Results — `python3 scripts/eval_semantic_guard.py`, 2026-08-31

**GOLD** — `fixtures/refusal-correctness/set.json`, n=6, labelled 2026-08-22 by Cursor
before any engine run.

```
  id    gold           guard OFF      guard ON
  RC1   SUPPORTED      SUPPORTED      SUPPORTED
  RC2   SUPPORTED      SUPPORTED      SUPPORTED
  RC3   NOT_SUPPORTED  NOT_SUPPORTED  NOT_SUPPORTED
  RC4   NOT_SUPPORTED  NOT_SUPPORTED  NOT_SUPPORTED
  RC5   NOT_SUPPORTED  SUPPORTED      NOT_SUPPORTED  *closed*
  RC6   SUPPORTED      SUPPORTED      SUPPORTED
  correct: guard OFF 5/6   guard ON 6/6
```

**1 false GREEN closed. 0 true GREENs lost.**

**REGISTRY** — every claim in `research-corpus/`, n=313, re-cleared offline against the
document cache; same command, same parser, same locator as the shipped registry.

```
  guard OFF  {'sourced': 27, 'refused': 270, 'unknown': 16}
  guard ON   {'sourced': 27, 'refused': 270, 'unknown': 16}
  verdicts changed: 0/313 (0.0%)
  refusals RESCUED to SOURCED: 0
  SOURCED on a DIFFERENT span: 8/27 — same verdict, better evidence
```

**The effect on this corpus is not fewer GREENs. It is better evidence under the same
GREENs.** When the guard refuses a span the locator offers the next occurrence, and a
better one usually exists in the same document:

```
claim: arXiv:2511.12884 — Agent READMEs
was  : Search arXiv Press Enter to search · Advanced search --> Computer Science >…
now  : Software Engineering arXiv:2511.12884 (cs) [Submitted on 17 Nov 2025 … Title: Agent READMEs: An Empirical…
```

A run reporting only the verdict delta would have read 0.0% and concluded the guard does
nothing. That is the wrong object: **the verdict was never what was wrong. The span was.**

**ATTRIBUTION** — each mechanism run alone over the 27 GREEN verdicts:

```
  polarity  fires on   1/27      (the shipped gate)
  binding   fires on  15/27      (not a gate — refuses paraphrase)
  coverage  fires on  12/27      (not a gate — used to rank, and to flag thin evidence)
  coverage threshold sweep:  0.30 -> 8/27   0.40 -> 12/27   0.50 -> 14/27   0.60 -> 17/27
```

## What is NOT closed

- **The `coverage` residue.** 12 of 28 registry rows are SOURCED on a span carrying under
  40% of the claim's terms — page furniture around a matching title, where the document
  offered no better sentence. The guard does not refuse them, because a gate that would
  also refuses honest paraphrase. They are now **counted and marked on the registry
  surface** as *thin evidence*, with the fraction printed per row.
- **This is not comprehension.** Three narrow checks over negation and subject binding.
  It will not catch a false GREEN that is fluent, on-topic, positively phrased and simply
  about a different fact. Nothing here should be sold as reading.
- **n=6 on the only labelled population.** The gold result is 6/6 on six items. The
  313-claim replay is unlabelled and every changed row was printed and adjudicated by
  hand; that is a weaker instrument than a label set and is not a substitute for one.
