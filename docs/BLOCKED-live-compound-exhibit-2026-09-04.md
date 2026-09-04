# BLOCKED — live compound via *local* keys · 2026-09-04

**Status:** **SUPERSEDED** for the hosted exhibit.

Hosted live compound **PASSed** without local keys:
`docs/RECEIPT-live-compound-exhibit-2026-09-04.md`
(`compound_fresh_hosted_probe.py` · subject `compound-fresh-a7009f2c6127`).

This file remains as the record of the wrong assumption that local
`PARALLEL_API_KEY` / `GEMINI_API_KEY` were required to probe hosted `/clear`.

---

## Key check (run at object) — still true for *local* clearance

```bash
test -n "${PARALLEL_API_KEY:-}" && echo PARALLEL=set || echo PARALLEL=missing
test -f ~/.config/keys/parallel.key && echo parallel.key=exists || echo parallel.key=missing
test -n "${GEMINI_API_KEY:-}" && echo GEMINI=set || echo GEMINI=missing
test -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" && echo ADC=set || echo ADC=missing
```

**Output (2026-09-04T00:05Z, this VM):**

```
PARALLEL=missing
parallel.key=missing
GEMINI=missing
ADC=missing
```

Local `POST /clear` / offline-with-live-search remains blocked. Hosted probe does not.
