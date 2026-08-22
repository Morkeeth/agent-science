---
date: 2026-08-22
project: CLEARED
status: SPEC ONLY — deliberately not built
answers: docs/FINDING-refusal-correctness.md
---

# Spec: the refusal-correctness set

A design problem, not a build problem, which is why it is written while blocked.

## What it is for

Every one of the 31 controls watches the **assert-too-much** direction. Nothing watches
a refusal being wrong. A false GREEN is a lawsuit; a false UNKNOWN is free, invisible,
and looks like rigour. This set is the only thing that can make the suite fail in the
second direction.

## The ground-truth problem — and where I disagree with the coordinator's framing

The stated constraint: *the set must be built from documents where the ground truth is
known independently of our engine, or it just measures agreement with ourselves.*

Agreed on the danger, and I think the framing points at the wrong scarcity. The question
a refusal answers is **"does this document support this claim?"** — that is a reading
judgement, and there is no oracle for it. Independence cannot come from finding documents
with pre-attached answers, because such documents mostly do not exist. It has to come from
**who labels and when**:

- Every item carries `labelled_by` and `labelled_at`, and the label is written **before**
  the engine is run on it. A label recorded after seeing our output measures agreement.
- The labeller records the **passage they would accept**, not just SUPPORTED/NOT. A set
  that records only a verdict cannot tell a right answer from a right answer for the
  wrong reason — which is the failure this whole repo keeps producing.
- A label is a claim about a document, so it is cited exactly like every other claim in
  this system: document URL, character offset, quoted span. The set is subject to its own
  product.

The genuinely hard part is not independence. It is **adversarial construction**.

## The construction rule

A set built from claims we already handle correctly measures nothing. Seed it from
**failures we have actually produced**, then generalise:

| Seed | Real instance from this run |
|---|---|
| The claim's terms appear FIRST in navigation, and the supporting sentence is further down | EUR-Lex `2012/28/EU` — produced a false UNKNOWN |
| The document has almost no sentence boundaries | EUR-Lex headers — returned nothing |
| The supporting sentence is preceded by a language picker | rightsstatements.org CNE |
| The subject and its verb straddle the trim point | *"…status of this Item has not been evaluated"* → *"Item has not been evaluated"* |

Then the placements no locator has met yet: a table cell, a footnote, a caption, a second
language, an occurrence after the first, a PDF, a claim supported across two sentences.

## Both directions, or it is not a control

- Items where the correct answer is **SUPPORTED**. A locator that refuses everything must
  fail. This is the whole point.
- Items where the correct answer is **NOT SUPPORTED**. A locator that accepts everything
  must fail — including one where the claim is *nearly* stated, differing by a negation, a
  date, or a quantity. That is where a model will be most confident and most wrong.
- Items where the document does not mention the subject at all.

## The metric, and the five-cause rule it must respect

Report false-UNKNOWN rate and false-GREEN rate **separately**. A single accuracy number
lets one hide inside the other.

And the standing rule, one layer down: **do not optimise "fewer UNKNOWNs".**

| Cause | Whose | Must trend |
|---|---|---|
| `terms_never_fetched` | ours | → 0 |
| `unruled_instrument` | ours | → 0 |
| `no_instrument` | the world's | **must not move** |
| `holder_states_not_evaluated` | the world's | **must not move** |
| `source_does_not_state_it` | the world's | **must not move** |

A metric that pushes all five down destroys the product. Printing the world's gaps *is*
the product — this is "do not chase the 37" restated for the fact leg.

## Done when

The suite fails on a false UNKNOWN. Today it cannot fail in that direction at all.
