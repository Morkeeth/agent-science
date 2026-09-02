# Product trace · buyer SOURCED + CATCH · 2026-09-02

**Buyer scenario:** Documentary clearance desk — one claim a lawyer can show as sourced, one claim caught as unsourced.  
**Fix that made this possible:** unsettled `no_independent_source` log rows no longer short-circuit search; GREEN may upgrade a poisoned refuse.

---

## Input

**Script:** `docs/cold-scripts/buyer-sourced-and-caught.txt`

```
Directive 2012/28/EU of the European Parliament and of the Council of 25 October 2012 on certain permitted uses of orphan works.

The orphan works directive requires every European museum to clear all film footage overnight.
```

**Subject:** `buyer-demo-local`  
**Env:** fresh `CORPUS_DB` + `REFUSAL_LOG_DB` (no GCS) — cold shelf

---

## Measured (local · 2026-09-02)

| Field | Value |
|-------|------:|
| Wall-clock | **206s** |
| Claims | 2 |
| SOURCED | **1** |
| UNSOURCED (caught) | **1** |
| Parallel API | 1 |
| Log hits | 0 |

### C1 · SOURCED

| | |
|---|---|
| **Claim** | Directive 2012/28/EU … certain permitted uses of orphan works |
| **URL** | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028 |
| **Span** | verbatim title from EUR-Lex |
| **Class** | PRIMARY (EU primary law) |

### C2 · UNSOURCED (caught)

| | |
|---|---|
| **Claim** | The orphan works directive requires every European museum to clear all film footage overnight |
| **Cause** | `search_found_no_admissible_source` |
| **Why** | we searched and no document we read states it |

---

## Why this beats the Google Books-only refuse trace

A producer reporting upward needs **both** numbers: claims cleared and claims caught. This run is 1 and 1. Gap report HTML now shows a **Buyer week** strip (cleared vs caught, last 7 days).

**Replay (after deploy for hosted):**

```bash
bash scripts/demo_clearance_desk.sh
# or local:
python3 agent_science.py docs/cold-scripts/buyer-sourced-and-caught.txt --subject buyer-demo
```

**Poison class (pre-fix):** hosted `/clear` on the Directive title returned `UNVERIFIED INDEPENDENCE` via `log_hit` from an old Wikipedia-only pass — never re-searched EUR-Lex. Fixed in `refusal_log.is_settled_for_reuse` + GREEN upgrade path.
