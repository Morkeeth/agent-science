# BLOCKED — live compound exhibit · 2026-09-22

**Attempted:** orphan-works / compound A/B on hosted URL with Parallel at runtime.

**Missing credentials on this agent VM (exact):**

| Credential | Path checked | Result |
|------------|--------------|--------|
| `PARALLEL_API_KEY` | env | unset |
| `~/.config/keys/parallel.key` | filesystem | absent |
| `GEMINI_API_KEY` | env | unset |
| `WORKSPACE_TOKEN` / `AGENT_SCIENCE_WORKSPACE_TOKEN` | env | unset |

**Hosted `/clear`:** private-workspaces — requires workspace bearer; public partner proof is `/health` + `/partners` only.

**Authoritative offline substitute:**

```bash
python3 scripts/compound_exhibit_receipt.py
```

**Partner gate (no secret required):**

```bash
python3 scripts/partner_admissibility_gate.py   # exit 2 · hosted RED · local C PASS
```

Do not claim a live Parallel drop on video until Oscar has keys + deploy +
`bash scripts/verify_partners_hosted.sh` exit 0 (or exit 2 only for clear-token BLOCKED after health+partners green).
