# REFUSAL CORRECTNESS GATE — alternative arm receipt

**Date:** 2026-08-29 20:48 UTC
**Anchor:** `fixtures/refusal-correctness/set.json` — labelled 2026-08-22T21:30:00Z

## Arms

| Arm | Implementation |
|-----|----------------|
| **BASELINE** | `NaiveFirstOccurrence`: first `must_contain` window, **no verify** |
| **ABLATION** | `StringLocator` (DEFAULT) with **verify bypassed** |
| **SHIPPING** | `StringLocator` (DEFAULT) + `verify.py` structural guard |

## Catchable items (n=5; RC5 excluded — documented engine_limit)

| id | gold | BASELINE | ABLATION | SHIPPING |
|----|------|----------|----------|----------|
| RC1 | SUPPORTED | GREEN | GREEN | GREEN |
| RC2 | SUPPORTED | GREEN | GREEN | GREEN |
| RC3 | NOT_SUPPORTED | UNKNOWN | UNKNOWN | UNKNOWN |
| RC4 | NOT_SUPPORTED | UNKNOWN | UNKNOWN | UNKNOWN |
| RC6 | SUPPORTED | GREEN | GREEN | GREEN |

## Aggregate (catchable only)

| Arm | correct | n | accuracy | false GREEN | false UNKNOWN |
|-----|--------:|--:|---------:|------------:|--------------:|
| BASELINE | 5 | 5 | 100% | 0 | 0 |
| ABLATION | 5 | 5 | 100% | 0 | 0 |
| SHIPPING | 5 | 5 | 100% | 0 | 0 |

## Honesty & limitations (worst numbers)

- **Verify delta on catchable set:** 0 false GREEN prevented (verify and ablation tie on safety here; RC5 engine_limit still fails all arms)
- **RC5 engine_limit** (substring_not_a_statement): gold NOT_SUPPORTED, baseline=GREEN, ablation=GREEN, shipping=GREEN (fixture pins shipping=GREEN)

- GREEN quotes that **fail verify** (catchable): baseline=0, ablation=0, shipping=0

## Gate command

```bash
python3 eval/refusal_correctness_gate.py
```

n<100 → report counts and per-item rows, not bare points without CIs.
