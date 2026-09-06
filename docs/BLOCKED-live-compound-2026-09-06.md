# BLOCKED — live compound / orphan-works exhibit · 2026-09-06

**Status:** BLOCKED on this VM — exact missing credentials named below.

## Missing credentials (object check)

```bash
test -n "$PARALLEL_API_KEY" && echo HAS_PARALLEL_ENV || echo NO_PARALLEL_ENV
# → NO_PARALLEL_ENV

test -f ~/.config/keys/parallel.key && echo HAS_PARALLEL_FILE || echo NO_PARALLEL_FILE
# → NO_PARALLEL_FILE

test -n "$GEMINI_API_KEY" && echo HAS_GEMINI_ENV || echo NO_GEMINI_ENV
# → NO_GEMINI_ENV
```

No `~/.config/keys/` directory on this Cloud Agent VM.

## What cannot run without them

| Attempt | Why blocked |
|---------|-------------|
| Orphan-works A/B live on hosted `POST /clear` | Hosted `/clear` is workspace-auth only (product boundary); also no keys for local desk live Parallel |
| `python3 scripts/compound_fresh_hosted_probe.py` | Needs public `/clear` or workspace token — neither available here |
| Local live Parallel discovery | Needs `PARALLEL_API_KEY` or `~/.config/keys/parallel.key` |

## Authoritative offline receipts (do not invent live numbers)

- Offline compound: `python3 scripts/compound_exhibit_receipt.py`
- Prior hosted compound (when desk was public): `docs/RECEIPT-live-compound-exhibit-2026-08-31.md`
- Orphan-works timeout finding: `docs/FINDING-orphan-works-timeout-2026-09-03.md`

## Unblock (Oscar)

1. Place Parallel key at `~/.config/keys/parallel.key` (0600) or inject via Secret Manager on deploy.
2. Deploy partner-surface branch (`bash deploy.sh`).
3. For film compound beat: either local desk (`AGENT_SCIENCE_HOSTED` unset) with keys, or authenticated workspace research that exercises Parallel.
