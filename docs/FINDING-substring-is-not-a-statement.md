---
date: 2026-08-22
status: OPEN — StringLocator still produces this; GeminiLocator does not
found_by: running the five adversarial controls against a live model
---

# The live model refused a claim the string matcher accepted — and the model was right

## What happened

Wired `gemini-3.5-flash` behind `locate()` and ran the real pitch claims through it.

C3, as written in `check_pitch.py` all day:

> *"'Copyright Not Evaluated' means **the holder never assessed the item**"*
> required terms: `has not been evaluated`

The CNE document says:

> *"The copyright and related rights **status of this Item** has not been evaluated.
> Please refer to the organization that has made the Item available for more information."*

**`StringLocator` returned GREEN.** The substring matched, the passage was real, the
quote was verbatim. Every control passed.

**`GeminiLocator` returned null.** The document does not say who did or did not assess
it — it says the *status* has not been evaluated. The claim attributes the
non-evaluation to *the holder*, which the document never states.

Rewritten precisely — *"The copyright and related rights status of this Item has not been
evaluated"* — Gemini returns **GREEN**, quoting that exact sentence.

## Why this matters more than the false UNKNOWN I was hunting

I have spent the day defending the **refuse-too-much** direction, on the reasoning that a
false GREEN is a lawsuit and a false UNKNOWN is free. That reasoning was right and it
pointed me at the wrong instrument. **The false GREEN was already live, in the product,
all day, produced by the string matcher** — and no control could see it, because every
control asked *is the quote real and verbatim?* and the quote was real and verbatim.

**A substring is not a statement.** `must_contain` proves a passage mentions the right
words; it cannot prove the passage asserts the claim. Only a reader can close that gap,
and until today the reader was `str.find`.

## Status

- `GeminiLocator` closes it, and this is the strongest argument for a model being
  load-bearing rather than decorative: it is not faster or cheaper, it is **correct
  where the deterministic version was wrong**.
- `StringLocator` still accepts it. Recorded rather than patched: a heuristic that can
  be taught this one case cannot be taught the general one, and pretending otherwise
  would hide the reason the model is there.
- The control in `tests/` pins the claim so a future locator cannot quietly start
  accepting it again.

## The correction it forces on my own record

My write-up of the refusal-correctness finding says all controls watch the
assert-too-much direction. **That was wrong.** They watch whether a quote is genuine.
Nothing was watching whether a genuine quote *supports the claim*, which is the
assert-too-much direction proper. `docs/SPEC-refusal-correctness-set.md` needs a third
group: claims whose supporting terms appear in a passage that does not state them.


---

# CORRECTION, 2026-08-22, same day — I overstated this and Cursor caught it

**What I claimed:** *"`GeminiLocator` closes it... it is correct where the deterministic
version was wrong."* I put that in a commit message, in this file, and relayed it to the
coordinator, who called it the headline of the run.

**What is actually true.** Cursor's review lane reported the sloppy C3 claim still
reaching GREEN with Gemini. I measured it across the model ladder rather than trusting
either of us:

| Locator | sloppy C3 claim |
|---|---|
| `StringLocator` | **GREEN** |
| `gemini-3.5-flash` | UNKNOWN — refused (my original single run) |
| `gemini-3.5-flash-lite` | **GREEN** — quotes the status sentence |
| `gemini-3.6-flash` | **GREEN** — quotes the status sentence |
| `gemini-3.7-flash` | UNMEASURABLE — HTTP 503 |

**The refusal was ONE MODEL ON ONE RUN, not a property of using a model.** I generalised
from a single observation to a claim about the architecture, which is exactly the error
this product exists to catch, committed in the write-up of a finding about that error.

## What survives, and it is still worth having

The **defect** is real and unchanged: a passage can be genuine, verbatim, on-topic and
still not state the claim, and `StringLocator` admits it. That was invisible to every
control before today.

What does **not** survive is the fix. **No locator closes this gap, because it is not a
locator problem.** `verify.py` is structural by design: verbatim presence plus
`must_contain`. **Nothing in this system reads meaning.** A stricter model may refuse a
sloppy claim on a given day; that is a behaviour, not a guarantee, and it varies by model
and by run.

So the honest statement is narrower and more useful:

> **`must_contain` must carry the distinctive detail of the claim — the attribution, the
> date, the quantity — because it is the only thing standing between a real quote and a
> claim it does not support. Where the falsehood is not encoded in the required terms,
> nothing in this system will catch it.**

That is also why the forced-lie probe L3 was caught: `"25 October 2013"` was absent from
the passage. A **string** test, not a semantic one — pinned in
`t_the_verifier_cannot_read_meaning_and_says_so`.

## The rule this leaves behind

**One observation of a model behaving well is not a property of the system.** Test a model
claim across the ladder before writing it down, and never on the run that produced it.
