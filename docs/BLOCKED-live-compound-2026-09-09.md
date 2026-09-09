# BLOCKED — live compound exhibit · 2026-09-09

**Why blocked (measured at object):**

1. Hosted desk revision `agent-science-00028-hed` is partner-dark:
   ```bash
   curl -sS https://agent-science-568004190078.us-central1.run.app/health
   # mode=private-workspaces only — no gemini/parallel/engine_default
   curl -sS -o /dev/null -w '%{http_code}\n' -X POST \
     https://agent-science-568004190078.us-central1.run.app/clear \
     -H 'Content-Type: application/json' \
     -d '{"script":"x","subject":"blocked"}'
   # 401
   ```
2. This VM has no `PARALLEL_API_KEY` / `GEMINI_API_KEY` and no `~/.config/keys/parallel.key`.
3. Prior orphan-works full script: Run A **504 @ 300s** — `docs/FINDING-orphan-works-timeout-2026-09-03.md`.

**Authoritative offline arm:** `python3 scripts/compound_exhibit_receipt.py` (A=2→B=1 Parallel).

**Unblock path (Oscar):** deploy dual-surface candidate → `bash scripts/verify_partners_hosted.sh` → compound-fresh probe (not full orphan-works until timeout raised).
