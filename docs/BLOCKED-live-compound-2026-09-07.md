# BLOCKED — Live compound exhibit · 2026-09-07

**Status:** BLOCKED on this agent VM · offline receipts remain authoritative  
**Re-checked:** 2026-09-12 — still no keys / workspace token on this VM; live `/health` still stripped on `00028-hed`.

## Exact missing credentials

| Credential | Purpose | Present here? |
|------------|---------|---------------|
| `PARALLEL_API_KEY` or `~/.config/keys/parallel.key` | Live Parallel discovery | **No** |
| `GEMINI_API_KEY` / Vertex ADC | Claim extraction | **No** |
| `AGENT_SCIENCE_WORKSPACE_TOKEN` | Hosted `/api/clear` after private-workspace pivot | **No** |

Checked 2026-09-12:

```bash
env | grep -E 'PARALLEL|GEMINI|GOOGLE|VERTEX|AGENT_SCIENCE_WORKSPACE' || true
ls ~/.config/keys/ 2>&1
# → no keys directory; no matching env vars
python3 scripts/watch_hosted_partner_health.py
# → RED on agent-science-00028-hed (partner fields absent)
```

## What still proves compound offline

```bash
python3 scripts/compound_exhibit_receipt.py
# A=2 → B=1 Parallel, corpus_hits ≥ 1 — no keys required
PYTHONPATH=. python3 scripts/prove_partner_surfaces_local.py
# partner /health + /partners + auth boundary — no network
```

## What Oscar runs after deploy + token

```bash
export AGENT_SCIENCE_WORKSPACE_TOKEN='…'
bash scripts/verify_partners_hosted.sh
python3 scripts/compound_fresh_hosted_probe.py
```

Do not film orphan-works full script until timeout finding is addressed (`docs/FINDING-orphan-works-timeout-2026-09-03.md`).
