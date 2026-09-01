# COLD-SCRIPTS · public documentary cold runs

**Measured:** 2026-09-01 · **Command:** `python3 agent_science.py <file> --subject <name>`  
**Rule:** No fixtures from `fixtures/scripts/` — only public sources cited below.

---

## Cost of one cold run

| Script | Wall-clock | Parallel API |
|--------|----------:|-------------:|
| EU orphan works | ~7s | 0 |
| Google Books settlement | ~19s | 1 |
| Apollo 11 | ~7s | 0 (0 claims extracted) |

---

## Script 1 · EU Directive 2012/28/EU

**Source:** https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32012L0028  
**File:** `docs/cold-scripts/eu-orphan-works-directive.txt`

| Claims | SOURCED | UNSOURCED | Parallel |
|--------|--------:|----------:|---------:|
| 1 | 0 | 1 | 0 |

Honest refuse — cross-subject log hit, no verbatim span for this wording.

---

## Script 2 · Google Books settlement (2011)

**Source:** https://arstechnica.com/tech-policy/2011/03/judge-rejects-google-book-monopoly/  
**File:** `docs/cold-scripts/google-books-settlement.txt`

| Claims | SOURCED | UNSOURCED | Parallel |
|--------|--------:|----------:|---------:|
| 1 | 0 | 1 | 1 |

Cause: `search_found_no_admissible_source` — refusal is correct.

---

## Script 3 · Apollo 11 (NASA public domain)

**Source:** https://www.nasa.gov/history/alsj/a11/a11.html  
**File:** `docs/cold-scripts/apollo-11-landing.txt`

0 claims extracted — script too short for Gemini extractor. Use longer excerpt next pass.

---

## Summary

Two public scripts → two honest refusals with named causes. No product tuning post-measurement.
