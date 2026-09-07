# BLOCKED — Live compound exhibit · 2026-09-07

**Status:** BLOCKED on this agent VM · offline receipts remain authoritative

## Exact missing credentials

| Credential | Purpose | Present here? |
|------------|---------|---------------|
| `PARALLEL_API_KEY` or `~/.config/keys/parallel.key` | Live Parallel discovery | **No** |
| `GEMINI_API_KEY` / Vertex ADC | Claim extraction | **No** |
| `AGENT_SCIENCE_WORKSPACE_TOKEN` | Hosted `/api/clear` after private-workspace pivot | **No** |

Checked:

```bash
env | grep -E 'PARALLEL|GEMINI|GOOGLE|VERTEX|AGENT_SCIENCE_WORKSPACE' || true
ls ~/.config/keys/ 2>&1
# → no keys directory; no matching env vars
```

## What still proves compound offline

```bash
python3 scripts/compound_exhibit_receipt.py
# A=2 → B=1 Parallel, corpus_hits ≥ 1 — no keys required
```

## What Oscar runs after deploy + token

```bash
export AGENT_SCIENCE_WORKSPACE_TOKEN='…'
bash scripts/verify_partners_hosted.sh
python3 scripts/compound_fresh_hosted_probe.py
```

Do not film orphan-works full script until timeout finding is addressed (`docs/FINDING-orphan-works-timeout-2026-09-03.md`).
