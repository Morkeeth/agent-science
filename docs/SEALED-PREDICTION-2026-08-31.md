# Sealed prediction — Agent Science · Agentic Cinema

**Sealed:** 2026-08-31T11:25:00Z UTC · **Do not edit after seal.**  
**Evidence:** `docs/LONG-RUN-RECEIPT-2026-08-31.md` · revision `agent-science-00014-p56`

---

## Prediction (verbatim)

> On the hosted URL, a second `POST /clear` with the **same `subject`** and an overlapping EU-directive claim returns **`corpus_hits ≥ 1`** and **`parallel_api_calls` on Run B ≤ Run A** on a shared corpus shelf.

## Measured at seal (hosted)

| Field | Run A | Run B | Pass? |
|-------|------:|------:|-------|
| Subject | `longrun-0831-1320` | same | — |
| `parallel_api_calls` | **1** | **0** | ✅ B < A |
| `corpus_hits` | 0 | **1** | ✅ ≥ 1 |
| `engine` | adk | adk | — |

**Second confirmation** (`longrun-0831-1321`, warm shelf): A=0, B=0, B `corpus_hits=1` — passes corpus clause; Parallel already 0.

## Offline anchor (unchanged)

`compound-mini-A.txt` → `compound-mini-B.txt`: A=**2** Parallel, B=**1** Parallel, B corpus hits=**2** — `docs/COMPOUND-EXHIBIT-2026-08-29.md`.

## Honest limits (pre-registered)

- Full `documentary-orphan-works` script: Run B **503** on hosted — do **not** claim on video.
- Warm dictionary may show A=0 Parallel — **corpus_hits** is the valid metric when shelf is hot.

## Seal hash

```
SHA256(prediction sentence, UTF-8):
a510bfa72bc5dad770ee2db800d4abc83da89e9f97bbb056232404b3fa5292b3
```

**Commit at seal:** `c845812` on `main` (receipt + long run)
