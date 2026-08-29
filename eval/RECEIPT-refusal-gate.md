# REFUSAL CORRECTNESS GATE — alternative arm receipt

**Date:** 2026-08-29 20:36 UTC
**Anchor:** `fixtures/refusal-correctness/set.json` — labelled 2026-08-22T21:30:00Z

## Arms

| Arm | Implementation |
|-----|----------------|
| **BASELINE** | `NaiveFirstOccurrence`: first `must_contain` window, **no verify** |
| **SHIPPING** | `StringLocator` (DEFAULT) + `verify.py` structural guard |

## Catchable items (n=5; RC5 excluded — documented engine_limit)

| id | gold | BASELINE | SHIPPING | baseline quote (trim) | shipping quote (trim) |
|----|------|----------|----------|----------------------|------------------------|
| RC1 | SUPPORTED | GREEN | GREEN | 'a href="#">2012/28/EU</a>\n  <a href="#">29 October' | 'repeats distinctive terms first (false-UNKNOWN see' |
| RC2 | SUPPORTED | GREEN | GREEN | 'ropean Parliament and of the Council of 25 October' | 'Parliament and of the Council of 25 October 2012\no' |
| RC3 | NOT_SUPPORTED | UNKNOWN | UNKNOWN | '' | 'document opened, 615 characters read; the locator ' |
| RC4 | NOT_SUPPORTED | UNKNOWN | UNKNOWN | '' | 'document opened, 192 characters read; the locator ' |
| RC6 | SUPPORTED | GREEN | GREEN | 'and related rights status of this Item has not bee' | 'IT</nav>\n<p>About this rights statement.</p>\n<p>Th' |

## Aggregate (catchable only)

| Arm | correct | n | accuracy | false GREEN | false UNKNOWN |
|-----|--------:|--:|---------:|------------:|--------------:|
| BASELINE | 5 | 5 | 100% | 0 | 0 |
| SHIPPING | 5 | 5 | 100% | 0 | 0 |

## Honesty & limitations (worst numbers)

- **RC5 engine_limit** (substring_not_a_statement): gold NOT_SUPPORTED, baseline=GREEN, shipping=GREEN (fixture pins shipping=GREEN)

- Baseline GREEN quotes that **fail verify**: 0 (shipping: 0)

## Gate command

```bash
python3 eval/refusal_correctness_gate.py
```

n<100 → report counts and per-item rows, not bare points without CIs.
