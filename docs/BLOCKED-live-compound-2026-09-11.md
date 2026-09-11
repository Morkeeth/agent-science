# BLOCKED — Live compound exhibit · 2026-09-11

**Attempted:** orphan-works / fresh-subject hosted A/B compound for partner night wave.  
**Result:** not run — credentials absent on this VM; hosted `/clear` gated.

## Exact missing credentials / surfaces

| Need | Object checked | Result |
|------|----------------|--------|
| `PARALLEL_API_KEY` | `env` · `~/.config/keys/parallel.key` | **absent** |
| `GEMINI_API_KEY` / Vertex ADC | `env` · ADC | **absent** (no key file; no usable ADC for live clear) |
| Hosted anonymous `/clear` | `curl -sS -o /dev/null -w '%{http_code}' …/clear` | **303** → login (`mode: private-workspaces`) |
| `AGENT_SCIENCE_WORKSPACE_TOKEN` | env | **absent** |

## What remains authoritative

- Offline compound: `python3 scripts/compound_exhibit_receipt.py` (prior A=2→B=1)
- Hosted compound history: `docs/RECEIPT-live-compound-exhibit-2026-08-31.md` / partner-night 2026-09-03
- Partner wiring local proof: `bash scripts/prove_partners_local.sh` (2026-09-11)
- Live partner health: **RED** until Oscar redeploys — `docs/FINDING-hosted-partner-proof-dark-2026-09-11.md`

Do not claim a live compound pass from this night.
