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
