# Product trace · Google Books settlement claim · 2026-09-02

**Buyer scenario:** Documentary producer pastes narration about the 2011 Google Books settlement collapse.  
**Command:** hosted `POST /clear` (no local keys) — same path as `bash scripts/demo_clearance_desk.sh`

---

## Input

**Source script (public):** `docs/cold-scripts/google-books-settlement.txt`  
**Primary URL cited in script header:** https://arstechnica.com/tech-policy/2011/03/judge-rejects-google-book-monopoly/

```
The Google Books settlement collapsed in 2011 when a federal judge rejected it.
Google had proposed a deal with authors and publishers to digitize millions of books.
The judge ruled the agreement would give Google too much power over orphan works.
Authors argued the settlement went too far in granting Google exclusive rights.
```

**Subject shelf:** `cold-trace-google-books-2026-09-02`

---

## Request

```bash
curl -sS -X POST "https://agent-science-568004190078.us-central1.run.app/clear" \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
{"script":"<file contents>","subject":"cold-trace-google-books-2026-09-02"}
EOF
```

---

## Measured

| Field | Value |
|-------|------:|
| Wall-clock | **62s** |
| HTTP | 200 |
| Claims extracted | 2 |
| SOURCED | 0 |
| UNSOURCED / flagged | 2 |
| `parallel_api_calls` | **3** |
| `corpus_hits` | 0 |
| Engine | `adk` (vertex:hack-fleet) |

**Cost estimate:** 3 Parallel search calls × ~$0.01/search order-of-magnitude (metered; exact invoice not in repo).

---

## Verdicts (lawyer-facing)

### C1 · UNVERIFIED INDEPENDENCE

**Claim:** The Google Books settlement was rejected by a federal judge in 2011.

| | |
|---|---|
| **Verdict** | UNVERIFIED INDEPENDENCE |
| **Cause** | `no_independent_source` |
| **Why** | Documents verified but collapse to non-independent origins (wikipedia, wired.com) — human must judge independence |
| **Citation** | none admitted as primary |

### C2 · UNSOURCED

**Claim:** A federal judge rejected the Google Books settlement on the grounds that it would give Google too much power over orphan works.

| | |
|---|---|
| **Verdict** | UNSOURCED |
| **Cause** | `search_found_no_admissible_source` |
| **Why** | Searched, read 2 of 3 candidate documents; none states this claim verbatim |
| **Citation** | none |

---

## Why this is the product demo

A producer or insurer does not need a green check — they need **each fact named, with source or named refusal**, in a report they can forward. This trace is two honest refusals with causes, not a paraphrase. That is the clearance desk artifact.

**Replay:**

```bash
bash scripts/demo_clearance_desk.sh docs/cold-scripts/google-books-settlement.txt my-subject
```

**Raw JSON:** saved at measurement time in terminal log; re-run producesLive rows (claim count may vary slightly with extractor).
