# BLOCKED — live compound exhibit · re-probed 2026-09-23

**Attempt:** orphan-works / compound A/B on hosted `/clear`  
**URL:** https://agent-science-568004190078.us-central1.run.app

## Exact missing credentials (this agent VM)

```text
PARALLEL_API_KEY   — absent
GEMINI_API_KEY     — absent
WORKSPACE_TOKEN    — absent (hosted /clear is workspace-auth)
```

Command that established absence:

```bash
python3 -c 'import os; print([k for k in ("PARALLEL_API_KEY","GEMINI_API_KEY","WORKSPACE_TOKEN") if not os.environ.get(k)])'
# → ['PARALLEL_API_KEY', 'GEMINI_API_KEY', 'WORKSPACE_TOKEN']
```

## What is NOT claimed

- No live Parallel call on hosted `/clear` tonight.
- No orphan-works A/B receipt from this VM.
- Offline compound + local call-proof remain the authoritative arms.

## Unblock (Oscar)

1. Rotate keys if needed (`AS-KEYS-ROTATE`) — console only.
2. `bash deploy.sh` so partner health + film surfaces leave `00028-hed`.
3. Export `WORKSPACE_TOKEN` + `PARALLEL_API_KEY` out of band on a machine that may hold them.
4. `bash scripts/verify_partners_hosted.sh` then `python3 scripts/compound_fresh_hosted_probe.py`.
