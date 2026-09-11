# BLOCKED — live compound exhibit · 2026-09-11

**Attempted:** orphan-works / compound A/B with Parallel drop on a live path.  
**Result:** BLOCKED — exact missing credentials and route boundary named below.

## Missing on this VM

| Credential / object | Checked | Result |
|---------------------|---------|--------|
| `PARALLEL_API_KEY` env | `echo ${PARALLEL_API_KEY:+set}` | **unset** |
| `~/.config/keys/parallel.key` | `test -f` | **missing** |
| `GEMINI_API_KEY` env | env probe | **unset** |
| `~/.config/keys/gemini.key` | `test -f` | **missing** |
| Hosted `POST /clear` | `curl -X POST …/clear` | **401/HTML error** — local-only on private-workspaces |

## What still proves compound offline

```bash
python3 scripts/compound_exhibit_receipt.py
```

Offline receipt remains authoritative (A→B Parallel drop + corpus_hits). Do not film hosted orphan-works full script (prior 504 finding stands).

## Unblock (Oscar)

1. Provision Parallel (+ Vertex ADC already on Cloud Run after deploy).
2. Redeploy admissibility fix so `/health` proves partners.
3. Run local desk clear with keys, or film offline compound + hosted `/health`·`/partners` only.
