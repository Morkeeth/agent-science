---
date: 2026-08-22
status: OPEN — the pipeline is correct; the DEMO is not
found_by: reading the first successful end-to-end run instead of celebrating it
---

# 5 of 5 SOURCED, and the number is worthless

## The run

First full end-to-end on a real script: `fixtures/scripts/real-orphan-works.txt`,
5 claims extracted by Gemini on Vertex, Parallel found a source for every one, every
passage verified verbatim. **SOURCED 5, UNSOURCED 0.**

## Why it proves nothing

**The script was built from the Wikipedia article on orphan works. Parallel found the
Wikipedia article on orphan works.** The "source" for each claim is the document the
claim was copied out of.

That is not verification. It is a round trip. Every check the engine performs is
genuine — the passage really is verbatim in the fetched document — and the result is
still meaningless, because the document is the script's own origin.

**100% is the number a circular setup produces.** A gap report with no gaps in it is a
sign the input was rigged, not that the product is good. The honest reading of this run
is that the *plumbing* works end to end, nothing more.

Second problem, smaller and also real: one of the five resolved against
`bafybei….ipfs.dweb.link/wiki/Orphan_works.html` — an **IPFS mirror of Wikipedia**. A
mirror is not a source. It is an accurate copy of some past state of another document,
which is a different thing from the document.

## What this means for the product, not just the demo

**A source that is the claim's own origin is not evidence.** The engine currently cannot
tell the difference, and neither can any locator, because at the passage level the two
are identical — the text matches perfectly, which is exactly the problem.

Candidate rules, none built:
- a candidate whose text CONTAINS the script passage nearly verbatim is self-citation,
  not corroboration, and should be refused or labelled
- a candidate that is a known mirror of another candidate is one source, not two
- **independence has to be a property of the SOURCE SET**, not of an individual verdict —
  the same shape as the refusal-correctness finding, one level up

## What the demo needs

A script whose claims must be checked against documents it was **not** written from:
prose asserting things about the world, verified against primary sources — legislation,
official registers, court records. Then UNSOURCED rows appear because they are true,
not because the input was chosen to produce them.

**A demo that cannot produce an UNSOURCED row is not demonstrating this product.** The
whole pitch is what it refuses.
