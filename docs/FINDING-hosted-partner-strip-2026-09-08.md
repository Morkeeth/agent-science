# FINDING — Hosted partner strip · 2026-09-08

**Object measured:** live Cloud Run revision `agent-science-00028-hed`  
**Command that found it:** `curl -sS https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool`

## What is true at the object

Live `/health` returns only:

```json
{"ok": true, "service": "agent-science", "mode": "private-workspaces", "revision": "agent-science-00028-hed"}
```

Missing: `gemini`, `gemini_path`, `parallel`, `parallel_sdk`, `agent_builder`, `engine_default`.

`GET /partners` → **303** to login.  
`POST /clear` → **401** Workspace access key required.  
`bash scripts/verify_partners_hosted.sh` → **RED** (assertion: missing partner field `gemini`).

## Baseline arm that beats us on live

`python3 scripts/eval_hosted_partner_surface.py`

| Target | naive (ok+service) | shipping (partner fields + public /partners + /clear≠401 + /api/cases=401) |
|--------|--------------------|-----------------------------------------------------------------------------|
| live 00028-hed | **PASS** | **FAIL** |
| local dual-surface fix | PASS | **PASS** |

The naive arm any competent team ships in two hours (liveness JSON) wins on today's hosted URL. That is the finding.

## Why this kept happening

Private-workspaces merge (`2d5e3ec`) routed every hosted path through `WorkspaceHTTP`, which served a stripped liveness `/health`. Multiple restore branches (`90708f4`, `19cd462`, `9e4484d`, …) fixed it and **never landed on main**. Docs and hack.md still claimed `engine_default: adk` on hosted.

## Fix in this branch (not yet on live)

Dual surface on one process:

- public desk: `/`, `/clear`, `/health`, `/partners`, registry/visibility
- private: `/cases`, `/api/cases`, `/login`

Prove without deploy:

```bash
bash scripts/demo_partner_dual_surface.sh
bash scripts/verify_partners_hosted.sh --local
python3 tests/test_hosted_partner_surfaces.py
```

Oscar: `bash deploy.sh` then `bash scripts/verify_partners_hosted.sh` against the candidate tag.

## What we got wrong earlier

Prior receipts claimed 4/4 partners live on hosted while revision 00028 was already stripped. Reading STATUS/hack.md was faster than curling `/health`. The object disagreed.
