# FINDING — compound exhibit broke under exact-assertion reuse · 2026-09-05

**Object:** `python3 scripts/compound_exhibit_receipt.py`  
**Prior pack claim:** A=2→B=1 Parallel, corpus_hits=2 (carried from 2026-09-03 receipt)  
**Measured at HEAD before fix:** A=2→B=3 Parallel, corpus_hits=0, exit 3

## What failed

After `f61635e` (*Invalidate same-subject reuse when assertions or evidence change*),
`corpus.recall(..., assertion=...)` requires `norm_term(assertion) == norm_term(stored title)`.
`compound-mini-B.txt` paraphrased the overlapping claims:

| Run | Text |
|-----|------|
| A | `In 2012 the European Union passed Directive 2012/28/EU…` |
| B (old) | `Europe's answer was Directive 2012/28/EU — known as…` |

Same `must_contain`, different assertion → **no corpus hit**, B re-searched everything, Parallel rose.

## What was not the failure

- Cross-subject log reuse tests still **2/2**.
- Exact-text same-subject reuse still works: measured A=2→B=1, hits=2 when B copies A's wording and adds one new claim.
- The Sep 3 receipt was true **under paraphrase-tolerant reuse**; it became a carried lie after the integrity change.

## Fix (tonight)

- `fixtures/scripts/compound-mini-B.txt` — exact overlap of A's two claims + British Library claim.
- `scripts/compound_exhibit_receipt.py` offline claim lists matched.
- Re-run: **A=2→B=1, corpus_hits=2, exit 0** (command below).

```bash
python3 scripts/compound_exhibit_receipt.py; echo exit=$?
```

## Lesson

A sealed offline exhibit is not sealed against product rule changes. The artifact-claims
gate (`scripts/eval_artifact_claims.py`) re-runs the receipt at the submitted commit so a
carried A→B number cannot stay green.
