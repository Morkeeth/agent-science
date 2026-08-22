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
