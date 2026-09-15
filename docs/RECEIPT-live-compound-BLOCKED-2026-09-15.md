# RECEIPT — live compound exhibit · BLOCKED · 2026-09-15

**Slice:** Night wave ambitious item 3 — orphan-works A/B on hosted or local with keys.

## Attempt

```bash
test -n "$PARALLEL_API_KEY" || test -f "$HOME/.config/keys/parallel.key"; echo exit:$?
# exit:1

test -n "$GEMINI_API_KEY" || test -f "$HOME/.config/keys/gemini.key"; echo exit:$?
# exit:1

curl -sf https://agent-science-568004190078.us-central1.run.app/health
# {"ok": true, "mode": "private-workspaces", "revision": "agent-science-00028-hed"}

curl -s -o /dev/null -w '%{http_code}\n' \
  'https://agent-science-568004190078.us-central1.run.app/search?q=2012/28/EU&live=false'
# 303 → /login (public /search not exposed)
```

## Verdict

**BLOCKED** — missing `PARALLEL_API_KEY` / `GEMINI_API_KEY` (and key files) on this VM.  
Additionally, hosted revision does not expose unauthenticated `/clear` or `/search`; a live compound exhibit on the public URL is not available without a workspace access key (Oscar).

## Authoritative substitute

```bash
python3 scripts/compound_exhibit_receipt.py
# offline A=2 → B=1 Parallel · corpus_hits B=2 · exit 0
# docs/COMPOUND-EXHIBIT-2026-08-29.md
```
