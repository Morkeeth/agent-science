# FINDING — hosted partner strip still dark · 2026-09-09

**Object measured:** live Cloud Run URL  
`https://agent-science-568004190078.us-central1.run.app`  
**Revision:** `agent-science-00028-hed`  
**Commands:**

```bash
curl -sS https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
bash scripts/verify_partners_hosted.sh
python3 scripts/eval_hosted_partner_surface.py
```

## What went red (today)

`/health` returned only:

```json
{"ok": true, "service": "agent-science", "mode": "private-workspaces", "revision": "agent-science-00028-hed"}
```

Missing at the object: `gemini`, `gemini_path`, `parallel`, `parallel_sdk`, `agent_builder`,
`engine_default`. `GET /partners` → **303** to the candidate alias. `POST /clear` → **401**.

`bash scripts/verify_partners_hosted.sh` → **exit 1**  
`AssertionError: gemini: expected True, got None`

## Embarrassing baseline

`python3 scripts/eval_hosted_partner_surface.py` against live:

| Arm | Live 00028 | Local dual-surface fix |
|-----|------------|------------------------|
| Naive (`ok` + `service`) | **pass** | pass |
| Shipping (partner fields + public `/partners` + `/clear`≠401 + `/api/cases`=401) | **fail** | **pass** |

Live hosted loses to a two-hour naive liveness check. That is the finding.

## Why docs looked green

Dual-surface restores existed on feature branches (`90708f4`, `19cd462`, `9e4484d`, …) and
were **not ancestors of `main`**. Receipts from 2026-08-30 … 2026-09-03 measured earlier
desk revisions. Local greps of `cloud/service.py` for `engine_default` passed while hosted
routed every path through stripped `WorkspaceHTTP`.

## Fix on this branch (code — not yet live)

Dual surface on one process (`cloud/partner_status.py` + `cloud/service.py` routing):

| Path | Auth | Role |
|------|------|------|
| `/health`, `/partners`, `/`, `/clear`, registry/visibility | public | partner track + clearance desk |
| `/cases`, `/api/cases`, `/login` | workspace token/session | private research |

Controls:

```bash
python3 tests/test_hosted_partner_surfaces.py   # 5/5
bash scripts/demo_partner_dual_surface.sh       # local prove, no deploy
python3 scripts/eval_hosted_partner_surface.py  # live loses; local wins
```

## Still Oscar

`bash deploy.sh` is Oscar's click. Until this candidate is promoted, **live hosted remains
partner-dark**. After deploy:

```bash
bash scripts/verify_partners_hosted.sh
# Expect: engine_default=adk · mode=private-workspaces+public-desk · Parallel ≥1 on /clear
```
