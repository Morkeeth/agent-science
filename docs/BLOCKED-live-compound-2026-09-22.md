# BLOCKED — live compound exhibit · 2026-09-22

**Object asked:** orphan-works (or fresh-subject) A/B on hosted `/clear` or local live `compound_exhibit_receipt` with Gemini + Parallel.

**Command that established the block:**

```bash
test -n "$PARALLEL_API_KEY" && echo set || echo missing
test -n "$GEMINI_API_KEY" && echo set || echo missing
test -f ~/.config/keys/parallel.key && echo keyfile || echo no-keyfile
test -f ~/.config/keys/gemini.key && echo keyfile || echo no-keyfile
```

**Result on this agent VM (2026-09-22):**
- `PARALLEL_API_KEY` = **missing**
- `GEMINI_API_KEY` = **missing**
- `~/.config/keys/parallel.key` = **missing**
- `~/.config/keys/gemini.key` = **missing**

**Hosted path also blocked for anonymous clear:** live mode is `private-workspaces`; `/partners` and research routes require workspace token. No `WORKSPACE_TOKEN` on this VM.

**Authoritative substitute (ran):**

```bash
python3 scripts/compound_exhibit_receipt.py
# → docs/COMPOUND-EXHIBIT-2026-08-29.md · Mode offline · A=2 → B=1 Parallel · corpus_hits B=2 · exit 0
```

Do not film or paste a live Parallel-drop claim from this session. Offline receipt only.
