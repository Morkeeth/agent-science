# RECEIPT — live compound exhibit BLOCKED · 2026-09-16

**Object:** hosted orphan-works A/B on
https://agent-science-568004190078.us-central1.run.app  
**Attempted:** 2026-09-16T10:52Z–11:00Z UTC · cloud agent VM

## BLOCKED — missing keys

```
GEMINI_API_KEY   = missing
PARALLEL_API_KEY = missing
~/.config/keys/parallel.key = missing
~/.config/keys/gemini.key   = missing
```

No live `clear_script` / hosted `POST /clear` run was executed. Offline receipt
(`python3 scripts/compound_exhibit_receipt.py`) remains authoritative for
exact-match compound (A=2→B=1, corpus_hits B=2, exit 0).

## Hosted surface measured without keys

| Probe | Result |
|-------|--------|
| `GET /health` | 200 · `mode=private-workspaces` · rev `agent-science-00028-hed` |
| `GET /` `/judge` `/judge/demo` (follow redirects) | 200 public |
| `GET /search` `/registry` `/partners` (follow redirects) | **login wall** |
| `scripts/compound_hosted_probe.py` | not run — would need workspace auth + keys |

## What would unblock

1. Oscar places rotated keys in Secret Manager / local `~/.config/keys/` (not in repo).
2. Workspace bearer for hosted `/api` mutations if probing Cloud Run.
3. Re-run: `python3 scripts/compound_fresh_hosted_probe.py` or orphan-works full A/B.

Until then: do not claim a live compound exhibit from this night.
