# BLOCKED — Live compound exhibit · 2026-09-15

**Status:** BLOCKED on this agent VM — credentials absent.

## Exact missing credentials

| Credential | Expected location | Present? |
|------------|-------------------|----------|
| `PARALLEL_API_KEY` | env or `~/.config/keys/parallel.key` | **no** |
| `GEMINI_API_KEY` / Vertex ADC | env / `GOOGLE_APPLICATION_CREDENTIALS` | **no** |
| `AGENT_SCIENCE_WORKSPACE_TOKEN` | Oscar-managed workspace access | **no** |

Checked:

```bash
test -f ~/.config/keys/parallel.key; echo parallel_key_file=$?
test -n "$PARALLEL_API_KEY"; echo PARALLEL_API_KEY_set=$?
test -n "$GEMINI_API_KEY"; echo GEMINI_API_KEY_set=$?
```

## What remains authoritative

- Offline compound: `python3 scripts/compound_exhibit_receipt.py`
- Prior hosted sealed prediction: `docs/SEALED-PREDICTION-2026-08-31.md`
- Orphan-works full script: prior finding **504 @ 300s** — `docs/FINDING-orphan-works-timeout-2026-09-03.md`

## Unblock (Oscar)

1. Place Parallel key at `~/.config/keys/parallel.key` (0600) or inject Secret Manager via `deploy.sh`.
2. Ensure Cloud Run SA has Vertex ADC (no plaintext Gemini key in deploy).
3. After deploy of partner-health restore, run:
   ```bash
   export AGENT_SCIENCE_WORKSPACE_TOKEN='…'
   bash scripts/verify_partners_hosted.sh
   python3 scripts/compound_fresh_hosted_probe.py
   ```
