# Prior-art probes — ANGLE 1 (structural-deferral cascade) provisional

**Date:** 2026-08-24 · **Role:** patent counsel · **For:** `github.com/Morkeeth/hack-fleet-ata/PROVISIONAL-SPEC-ANGLE1.md`
**Question probed:** does anything anticipate the *no-score, closed-form structural* deferral
limitation — defer to an LLM **only** on `disjoint objects + compatible intents`, with the
deterministically-decided cases carrying **no confidence score**?

## Reduction-to-practice, re-verified against the code (not the draft)
Ran `contract/test_confidence.py` and a direct count on the frozen corpus
(`CONTROLS` 8 + `HELDOUT` 8 + `HELDOUT2` 8 = 24 rows):

- **5/5 tests pass.**
- **Confident set: 13/24 rows, 13/13 correct** (precision 1.0 on the kept set).
- **Deferred tail: 11/24 rows** — ids `C2,C4,C8,H1,H2,H7,H8,T2,T3,T4,T8`.
- The "cascade recovers every row" test escalates to a **perfect oracle**, not a real LLM.
  So the honest claim is "confident set never wrong on the frozen corpus" +
  "escalating the deferred cell to an oracle recovers all 24" — **not** measured end-to-end
  LLM accuracy.

Two code facts the plain-English draft glosses, now pinned for the spec so the claims read
on the actual implementation:
- **`_overlap` is not set intersection.** It is intersection **OR** a prefix-4 match on
  tokens ≥5 chars (`parser`/`parse`, `serializer`/`serialize`). Claim language must say so.
- **`_compatible` maps unknown intent (`None`) → `CHANGE`.** A prompt with a placeable
  object but no recognized verb still gets a bucket. "Deriving an intent bucket" must cover
  this default path.

## Art distinguished (the named three + the newest neighbor)

| Ref | What it routes on | Distinguished because |
|---|---|---|
| **FrugalGPT** (arXiv:2305.05176) | learned scoring function + tuned per-query threshold | a *calibrated score*; ours has none |
| **Learning-to-Defer** (Madras et al. line) | learned rejector; defers on a *learned confidence/cost* | learned continuous signal vs closed-form structural cell |
| **UCCI** (arXiv:2605.18796) — *verified*: "Calibrated Uncertainty for Cost-Optimal LLM Cascade Routing" | token-level margin uncertainty → isotonic regression → per-query error prob → cost-minimized threshold | the *purest* calibrated-score router; ours defers with no probability at all |

## Two+ new targeted probes on the EXACT claim wording

**Probe 1 — arXiv/web, "structural decidability, no confidence threshold" (2026 state of art).**
Newest neighbors all replace the *raw score* with another **statistical** object, never a
structural predicate over input tokens:
- **Conformal Cascade** (arXiv:2607.25018) — *fetched Algorithm 1*: accepts iff
  `1 ≤ |C_k(x)| ≤ κ`, i.e. **conformal prediction-set cardinality** vs a calibrated
  threshold `q̂_k`. Still a distribution-calibrated object, explicitly "rather than from
  structural properties of input tokens." Closest art; **strengthens** our distinction.
- **GATEKEEPER** (arXiv:2502.19335) — confidence *tuning*.
- **Semantic-Agreement / ABC** (arXiv:2509.21837) — **ensemble agreement** as the deferral
  signal. Still a continuous inter-model signal, not a closed-form cell.
- **Confidence Tokens** (arXiv:2410.13284) — a *learned* routing token.

**Probe 2 — Google Patents, "defer to LLM on object-token overlap + intent category, not
confidence."** Surfaced intent-classification / meta-classifier prior art
(US8843470B2 meta-classifier for query intent; US10977446B1 intent induction;
US12222992B1 intent-based ranking to generate LLM responses; EP4398156A1 intent
explainability). **None** route a cheap classifier's *escalation* on a structural
object-overlap × intent-bucket cell; they classify intent or rank, they do not gate an LLM
call on a proven-unique undecidable partition with no score.

**Conclusion of the probes:** nothing found anticipates the no-score, closed-form
structural-deferral limitation. The 2026 frontier (Conformal Cascade, UCCI, ABC) has moved
*toward* alternatives to the raw threshold but every one is still a **calibrated/statistical**
signal. Novelty over the cascade line is, if anything, **firmer** than the original draft
assumed.

## Effect on the marginal verdict — UNCHANGED
Novelty over cascades is clean and now better-supported. The marginal call was never
novelty; it is **§103 obviousness over the decades-old rule-first / ML-fallback hybrid**
(expert system that falls through to a learned model). These probes do **not** touch that
flank. Distinguishing feature to argue: those hybrids fall back on *"no rule matched"*
(absence of a decision); this falls back on a *specific enumerated cell proven to be the
sole lexically-undecidable one* (a positive decision that a named cell is where evidence
runs out). Whether an examiner treats that as a patentable distinction or an obvious
refinement is the marginal call — one attorney hour settles it.

**One-liner for the record:** *marginal, unchanged; novelty flank slightly firmer.*

## Honest caveats carried into the spec
- **"Provably-sole undecidable"** is a design property validated **empirically on 24 frozen
  items**, not a universal theorem. Kept out of the claim language (§112 indefiniteness
  risk — "provably" is not a testable structural limitation); lives in the description as
  rationale.
- **Rest-of-world novelty already lost** — the reduction-to-practice is in a public repo.
  This is a **US-grace filing only** (§102(b)(1) one-year window).
- **AI-assisted inventorship** — the fleet generated much of the code. USPTO 2024 guidance
  requires a natural person's significant contribution to *conception*; Oscar's conception
  of the structural-deferral partition is the inventorship basis, stated on record.

## Sources
- FrugalGPT — https://arxiv.org/abs/2305.05176
- Cost-Saving LLM Cascades with Early Abstention — https://arxiv.org/abs/2502.09054
- UCCI: Calibrated Uncertainty for Cost-Optimal LLM Cascade Routing — https://arxiv.org/abs/2605.18796
- Conformal Cascade — https://arxiv.org/abs/2607.25018 (Algorithm 1 fetched)
- GATEKEEPER: Confidence Tuning — https://arxiv.org/abs/2502.19335
- Semantic Agreement / ABC — https://arxiv.org/abs/2509.21837
- Learning to Route LLMs with Confidence Tokens — https://arxiv.org/abs/2410.13284
- US8843470B2 — https://patents.google.com/patent/US8843470B2/en
- US10977446B1 — https://patents.google.com/patent/US10977446B1/en
- US12222992B1 — https://patents.google.com/patent/US12222992B1/en
- EP4398156A1 — https://patents.google.com/patent/EP4398156A1/en
