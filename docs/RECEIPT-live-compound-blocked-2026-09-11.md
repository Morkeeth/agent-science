# RECEIPT — live compound exhibit BLOCKED · 2026-09-11

**Attempted:** orphan-works A/B on hosted or local live path.  
**Outcome:** **BLOCKED** — no live keys on this VM; hosted desk is not anonymous.

## Missing objects (named, not guessed)

| Need | Present? | Checked how |
|------|----------|-------------|
| `PARALLEL_API_KEY` env | no | `echo` / env probe |
| `~/.config/keys/parallel.key` | no | `test -f` |
| `GEMINI_API_KEY` / `GOOGLE_API_KEY` | no | env probe |
| `~/.config/keys/gemini.key` | no | `test -f` |
| Anonymous hosted `POST /clear` | no | `curl -L` → workspace sign-in HTML (`Access token`) |
| Hosted `/health` | yes | `{"ok": true, "mode": "private-workspaces", "revision": "agent-science-00028-hed"}` |

## Authoritative substitute

Offline compound (no keys), exact-assertion fixtures:

```bash
python3 scripts/compound_exhibit_receipt.py
# A=2 → B=1 Parallel · corpus_hits B=2 · exit 0
```

Receipt: `docs/COMPOUND-EXHIBIT-2026-08-29.md` (re-derived 2026-09-11).

## What this does **not** prove

- Hosted Parallel drop on Cloud Run tonight
- Orphan-works full-script A/B under service timeout 240s
- That a judge can run compound without a workspace token

Oscar: live compound needs keys locally **or** a tokenized hosted `/clear` path filmed with the access wall visible.
