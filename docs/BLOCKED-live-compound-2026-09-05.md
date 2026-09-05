# BLOCKED — live compound exhibit · 2026-09-05

**Attempt:** orphan-works / compound A/B on hosted URL + local live Parallel.

## Missing credentials (exact)

| Credential | Checked | Result |
|------------|---------|--------|
| `PARALLEL_API_KEY` | `test -n "$PARALLEL_API_KEY"` | **unset** |
| `~/.config/keys/parallel.key` | `test -f` | **absent** |
| `GEMINI_API_KEY` | `test -n "$GEMINI_API_KEY"` | **unset** |
| Vertex ADC | not probed further — Parallel already blocking live discovery | — |

## Hosted object (no keys needed to observe)

```bash
curl -sS https://agent-science-568004190078.us-central1.run.app/health
# → stripped health (00026-zel) — partners not reported
bash scripts/verify_partners_hosted.sh
# → exit 1 · gemini: expected True, got None
```

`POST /clear` is not reachable for anonymous compound probes on live revision
(login redirect). Dual-surface fix restores it in code; Oscar deploy required.

## Offline authoritative receipts

- `python3 scripts/compound_exhibit_receipt.py` — offline A→B Parallel drop
- Prior hosted: `docs/RECEIPT-live-compound-exhibit-2026-08-31.md`
- Orphan-works timeout: `docs/FINDING-orphan-works-timeout-2026-09-03.md`

Do not claim a fresh live compound from this VM night.
