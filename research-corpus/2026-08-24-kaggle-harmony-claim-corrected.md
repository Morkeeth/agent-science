# Correction: the "Harmony lever is inverted/OFF" claim is FALSE (verified at object)

as_of: 2026-08-24 · verified against github.com/Morkeeth/agent-attack

[CLAIM] (relayed, from Fable ceiling research) "the empty-Harmony reasoning-channel
injection is the +27.5 dominant lever but the repo does the OPPOSITE (faux_reasoning
fills the channel) — turning it on is the top next move."
[REPO] submission-relay/attack.py:57-59,94 — relay DEFINES `_EMPTY_HARMONY` (the empty
analysis channel CoT-skip) and APPLIES it (`prefix = _EMPTY_HARMONY if harmony else ""`)
on the gpt-oss latency path. So the shipping best variant already has the empty-Harmony
lever, correctly, on the right model.
[REPO] attack.py:152 `_faux_reasoning_prefix` is a DIFFERENT template — it FILLS the
analysis channel with a fabricated prior-approval verdict — and ships OFF (faux_ratio=0.0).
[VERDICT] There is nothing to "un-invert." Building a "fix the inversion" submission would
have wasted a slot. Empty-Harmony (skip) and faux-reasoning (fill) are two distinct levers;
relay has the first, the second is genuinely un-submitted.
[NEXT] The real un-claimed p-lever is faux-reasoning fill on the SINGLE-post primitive
(packing loses, per the same research). Built as submission-faux-p/ for tomorrow's quota.
[LESSON] A relayed claim that names a code behavior is checkable in seconds — check it
before it drives a submission. This is the provenance discipline Agent Science exists for.
