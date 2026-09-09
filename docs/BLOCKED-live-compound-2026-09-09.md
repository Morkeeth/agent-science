# BLOCKED — live compound exhibit · 2026-09-09

**Status:** BLOCKED · offline compound is authoritative

## Missing on this VM

| Key / path | Present? |
|------------|----------|
| `PARALLEL_API_KEY` / `~/.config/keys/parallel.key` | **no** |
| `GEMINI_API_KEY` / ADC | **no** |

Command that would run live when keys exist:

```bash
python3 scripts/compound_exhibit_receipt.py   # selects live path when keys present
# or hosted (requires workspace bearer + public /clear — NOT on private-workspaces)
```

## Hosted object (also blocks the old A/B)

```bash
curl -sS -o /dev/null -w '%{http_code}\n' -X POST \
  -H 'Content-Type: application/json' \
  -d '{"script":"x","subject":"orphan-works"}' \
  https://agent-science-33kamss2jq-uc.a.run.app/clear
# → 401 Workspace access key required
```

Revision `agent-science-00028-hed` does not expose unauthenticated `/clear`. Even with provider keys, the historical hosted compound seal cannot be re-run without Oscar's workspace token and a product decision to restore a public desk.

## Authoritative substitute

```bash
python3 scripts/compound_exhibit_receipt.py
# 2026-09-09 offline: A=2 → B=1 Parallel · corpus_hits B=2 · exit 0
```

Receipt: `docs/COMPOUND-EXHIBIT-2026-08-29.md`.
