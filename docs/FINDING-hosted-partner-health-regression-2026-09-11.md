# FINDING — hosted partner `/health` stripped after private-workspaces cutover

**Date:** 2026-09-11 · **Object:** live Cloud Run + `cloud/case_http.py`  
**Revision measured:** `agent-science-00028-hed`

## What we thought

hack.md LOG and partner receipts claimed **4/4 partners on hosted** with
`engine_default: adk` on `/health`. `scripts/verify_partners_hosted.sh` was the
done-when.

## What the object said

```bash
curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
```

Returned only:

```json
{
  "ok": true,
  "service": "agent-science",
  "mode": "private-workspaces",
  "revision": "agent-science-00028-hed"
}
```

`gemini`, `parallel`, `parallel_sdk`, `agent_builder`, and `engine_default` were
**absent**. `/partners` redirected into the login wall. `POST /clear` returned
auth/error HTML — expected under the workspace boundary, but the verify script
still assumed a public desk.

## Why the docs stayed green

The nearer proxy answered faster than the object:

1. Local unit tests asserted partner strings inside `cloud/service.py` — the
   path that **does not run** when `K_SERVICE` is set.
2. Older receipts measured an earlier revision that still served the desk.
3. `verify_partners_hosted.sh` was not re-run against live before claiming the
   prior night wave still held.

This is the same failure mode as the Qwen loss retros: a nearer proxy beat the
real object.

## Baseline vs shipping (re-derived)

```bash
python3 scripts/eval_partner_health_baseline.py
```

| Arm | Score | Notes |
|-----|------:|-------|
| Naive (live 00028 shape) | **1/8** | revision only |
| Shipping (code after fix) | **8/8** | full partner fields + `/partners` checklist |
| Live hosted (pre-redeploy) | **1/8** | still naive until Oscar `deploy.sh` |

## Fix (this branch)

- `cloud/partners.health()` — shared public payload
- `cloud/case_http.py` serves full `/health` and `/partners` **before** auth
- Legacy `/clear` · `/search` stay local-only on hosted (boundary preserved)
- `tests/test_partner_runtime.py::t_hosted_health_exposes_partners` — RED control
  that scores the stripped shape ≤1 and shipping = denominator
- `scripts/verify_partners_hosted.sh` rewritten for the workspace boundary

## Oscar

Redeploy (`bash deploy.sh` — Oscar only). Then:

```bash
bash scripts/verify_partners_hosted.sh
python3 scripts/eval_partner_health_baseline.py
```

Expect live score **8/8** and `/partners` HTTP 200 without a session.
