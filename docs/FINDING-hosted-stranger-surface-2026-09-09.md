# FINDING — hosted stranger URLs were false-GREEN · 2026-09-09

**Status:** documented + pack/Devpost corrected. Deploy not run (Oscar only).

## Object measured

```bash
curl -sS https://agent-science-568004190078.us-central1.run.app/health
# {"ok": true, "service": "agent-science", "mode": "private-workspaces",
#  "revision": "agent-science-00028-hed"}

# Unauthenticated (vanity host 303 → canonical origin):
# /search /registry /partners /stats /popular/ui → 303 /login
# POST /clear → 401
# /visibility/ui /truths/ui → 200 public-entry STUB (not the search panel)
# /judge/demo → 200 read-only PEP 8 evidence case
```

## What went wrong

SUBMISSION-PACK and `submission/DEVPOST-PASTE.md` still pointed judges at hosted `/visibility/ui`, `/truths/ui`, and a public clearance desk. `/health` returning `ok: true` is a **nearer proxy** that stayed green while the advertised surface died.

`scripts/eval_artifact_claims.py` on the stale pack (before refresh):

| id | baseline (trust docs) | shipping (object) |
|----|----------------------|-------------------|
| AC7 hosted `/search` SOURCED | True | False (303) |
| AC11 `/visibility/ui` panel | True | False (stub) |

Baseline **11/12**, shipping **9/12**, delta −2 — naive doc-trust beats truth-checking until the pack is honest.

## Fix

- Pack + Devpost: stranger path = cold clone + `/judge/demo`; declare private-workspaces.
- Gate: `python3 scripts/eval_artifact_claims.py` (exit 3 on pack false-GREEN).

## Lesson

Open the hosted URL itself. A 200 on the wrong page is how tonight's false-GREEN worked.
