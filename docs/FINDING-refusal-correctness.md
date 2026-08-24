---
date: 2026-08-22
project: CLEARED
status: NAMED, NOT BUILT — the next control, deliberately unwritten
found_by: rendering a fix and looking at it again
---

# The control that does not exist yet: are our refusals correct?

## The finding

While fixing the GREEN-evidence defect I introduced a **false UNKNOWN** and nearly
shipped it as honesty. The fix scanned only the first occurrence of the claim's terms.
On EUR-Lex the first occurrence of `2012/28/EU` is a navigation label, so C1 flipped
GREEN → UNKNOWN — and the document *does* state the claim, further down the same page.

I reported that flip as the conservative outcome before checking it.

> **A wrong refusal is not the safe direction. It is the same defect facing the other way.**

## Why this is the failure this product will actually develop

Every incentive in the design points at it:

| Force | Direction it pushes |
|---|---|
| The pitch is *"we decline rather than guess"* | refusing reads as the product working |
| All 24 controls watch the **assert-too-much** direction | nothing watches the other one |
| A false GREEN is a lawsuit | expensive, visible, feared |
| A false UNKNOWN costs nothing visible | free, invisible, unpunished |

So the product drifts conservative, and **reads as more honest the further it drifts.**
A refusal looks like rigour. Nobody audits rigour.

This is the same shape as the substitution defect (`docs/` history, commit `1eeb8b4`) and
the same shape as the wrong-object failure in the 94% number: the check was correct and
pointed at the wrong thing.

## The control, unbuilt

A refusal is a claim about a document — *"this document does not support this"* — and it
is the only claim in the system that is currently accepted without evidence being tested.
The control has to answer: **for every UNKNOWN, would a careful human reading that exact
document agree?**

Rough shape, not a specification:

- A held-out set of claims with a **known** verdict, including claims that ARE supported
  but only in an awkward place in the document — a header, a table cell, a footnote, a
  second language, an occurrence after the first.
- The suite fails on a **false UNKNOWN**, not only on a false GREEN. Today the suite
  cannot fail in that direction at all.
- `terms_never_fetched` and `unruled_instrument` are ours and must trend to zero;
  `no_instrument`, `holder_states_not_evaluated` and `source_does_not_state_it` are the
  world's and must NOT. A control that pushes all five down would destroy the product —
  see the standing rule not to chase the 37.

## The rule this leaves behind

**Every mechanism that can refuse needs a test that watches it refuse wrongly.**
Not built today; named so it does not evaporate.


---

## Update, same day: half of this is now built

The locator/verifier split (`clearance/locate.py`, `clearance/verify.py`) is the answer
to this finding, arriving from the admissibility requirement rather than from the
finding itself.

A refusal is now **traceable to the implementation that caused it** — every
`source_does_not_state_it` prints the locator's name and the refusal code, so a false
UNKNOWN can be attributed rather than merely observed. `StringLocator` is named as one
implementation, not as the product, and the site-specific navigation list lives inside
it. A control greps `verify.py` to keep that list out of the guard.

**Still unbuilt, and still the finding:** a held-out set with known verdicts, where the
suite fails on a false UNKNOWN. Traceability is not correctness. Nothing yet watches a
refusal being wrong.


---

## Correction, 2026-08-22, same day: the premise above is half wrong

This file says every control watches the assert-too-much direction and nothing watches a
wrong refusal. **The first half is not true.** The controls watch whether a quote is
GENUINE — real, verbatim, chrome-free. Nothing watched whether a genuine quote actually
*states the claim*. A live model found the gap on the first run:
`docs/FINDING-substring-is-not-a-statement.md`.

So the incentive table stands, but the score does not. **A false GREEN was live in the
product all day**, produced by the string matcher and invisible to 31 green controls.
Both directions were unwatched; I only knew about one of them.


---

## Update, 2026-08-24: the held-out set is built, and it now binds the SHIPPING locator

Two things this file still asserted are now false. It said the set was "still unbuilt":
it was built and committed by the Cursor lane on 2026-08-22
(`fixtures/refusal-correctness/set.json`, `tests/test_refusal_correctness.py`, six
items RC1–RC6, wired into `tests/test_watch_it_go_red.py`). Verifying at the object
found the set real but its teeth loose in exactly the two directions this finding is
about:

- **The false-UNKNOWN seed was not enforced.** RC1 — the supporting sentence that sits
  after a nav occurrence of the same date — was pinned only as "may be GREEN or
  UNKNOWN." The suite could not fail on the one defect the finding was written about.
- **The false GREEN was invisible.** RC5 (the substring-is-not-a-statement trap) is a
  live false GREEN on the shipping `StringLocator`, but the NOT_SUPPORTED pole was
  tested with a *greedy stand-in* that passed RC5 only by structural accident (its slice
  started mid-word). Nothing ran the actual product locator against the set.

Fix (this session): `t_shipping_locator_binds_both_poles_on_held_out_set` runs the real
`DEFAULT` locator over the whole set and fails on a false UNKNOWN (RC1/RC2/RC6 must
GREEN) and on a false GREEN, and cannot be satisfied by a stuck all-GREEN or all-UNKNOWN
locator (SUPPORTED greens and NOT_SUPPORTED abstains on the same engine in the same run).
Demonstrated red by re-injecting the historical first-occurrence/nav defect: RC1 flips to
`UNKNOWN/source_does_not_state_it` and the assertion fires. Reverted, 72 green.

RC5 is carried as a **documented limitation**, not relabelled. Its gold stays
NOT_SUPPORTED (a careful human refuses it); a new `engine_limit:
"substring_not_a_statement"` field records that the shipping engine returns GREEN today
and pins that AS A DEFECT — when a locator finally refuses the negated-claim substring,
the pin fails with an instruction to promote RC5 into the enforced pole. This mirrors the
answerable/unanswerable split that grounded-refusal benchmarks (RefusalBench,
arXiv:2510.10390; AbstentionBench, arXiv:2506.09038) use to score over-abstention rather
than only hallucination.

**Open for Oscar:** accepting `engine_limit` on RC5 ratifies a standing product
limitation — "the engine cannot catch a negated claim whose `must_contain` terms appear
verbatim." That is a ruling, not a bug to be quietly fixed.
