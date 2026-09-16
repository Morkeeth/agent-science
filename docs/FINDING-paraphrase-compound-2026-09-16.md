# FINDING — paraphrase compound vs exact-assertion reuse · 2026-09-16

**Object measured:** `python3 scripts/eval_compound_paraphrase.py` · offline · no API keys  
**Related:** `scripts/compound_exhibit_receipt.py` (exact-match A/B) · engine commits `f61635e` / `176f5db`

## What broke the killer demo

Re-running the offline compound exhibit on 2026-09-16 against paraphrased
`compound-mini-B` (the fixture as of 2026-09-03) returned:

| Run A parallel | Run B parallel | corpus_hits B | exit |
|---:|---:|---:|---:|
| 2 | 3 | 0 | **3 (FAIL)** |

Root cause at the object: after exact-assertion binding, Run B's overlapping
claims are **different assertions** from Run A even when they share the same
`must_contain` anchor (`Directive 2012/28/EU`, `29 October 2014`). Corpus recall
and registry lookup both require the assertion text (or its slot hash). Paraphrases
miss on purpose. SUBMISSION-PACK still claimed A=2→B=1 — a carried number.

## Arms (identical paraphrased inputs)

| Arm | Rule | Compound score on paraphrased B |
|-----|------|----------------------------------|
| **shipping** | exact-assertion corpus + log | **FAIL** (B_parallel=3, corpus_hits=0) |
| **naive_term** | reuse by `must_contain` / term only | **PASS** (B_parallel=1, corpus_hits=2) |

**Embarrassment:** the naive two-hour baseline beats shipping on the Parallel-drop
metric the pitch sells. Shipping is constitutionally correct; the metric on
paraphrased scripts rewards the weaker arm.

## What we restored (not a silent rewrite of the rule)

- `compound-mini-B.txt` + offline claim lists now use **identical** assertion text
  for the two overlapping facts, plus the new British Library claim.
- Exact-match exhibit: A=2→B=1 Parallel, corpus_hits B=2, exit 0
  (`python3 scripts/compound_exhibit_receipt.py`).
- Paraphrase economics stay visible in `eval_compound_paraphrase.py` — do not
  equate paraphrases to paint the exhibit green.

## What this does not settle

- Live hosted orphan-works A/B (keys missing on this VM; `/search` is login-walled
  under `private-workspaces`).
- Whether judges see exact-match or paraphrase scripts in the film.
- Cost from a real Parallel **billing invoice** (price-card estimate only —
  `scripts/eval_cost_gate.py`).
