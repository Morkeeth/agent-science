# FINDING — hosted partner surface false-green · 2026-09-06

**Status:** measured RED on live revision `agent-science-00026-zel`; FIXED in code (this branch); **not live until Oscar deploys**.

## Object measured (not a proxy)

```bash
curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
# → {"ok": true, "service": "agent-science", "mode": "private-workspaces", "revision": "agent-science-00026-zel"}

curl -s -o /dev/null -w '%{http_code}\n' https://agent-science-568004190078.us-central1.run.app/partners
# → 303 (redirect toward login)

bash scripts/verify_partners_hosted.sh
# → AssertionError: gemini: expected True, got None
```

## What went wrong

Private-workspaces mode replaced the clearance desk on Cloud Run. `/health` kept returning `ok: true`, so any check that only looked at liveness stayed green while:

| Partner gate | Live 00026 |
|--------------|------------|
| `gemini` / `gemini_path` on `/health` | **absent** |
| `parallel` / `parallel_sdk` on `/health` | **absent** |
| `engine_default: adk` on `/health` | **absent** |
| Public `GET /partners` JSON | **303 → login** |
| Unauthenticated `POST /clear` | **401** (intentional boundary) |

This is the same failure class as a control that never went red: the nearer proxy (`ok: true`) answered faster than opening the partner fields.

## Baseline arm (embarrassing)

```bash
python3 scripts/eval_hosted_partner_surface.py
```

| Target | Naive (ok+service) | Shipping (partner fields + public /partners) |
|--------|--------------------|-----------------------------------------------|
| Live 00026 | **PASS** | **FAIL** |
| Local fix server | PASS | **PASS** |

Naive wins on live. That is the finding.

## Fix in this branch (not yet deployed)

1. `cloud/partners.py` — shared `health_payload()` + honest hosted notes on the manifest.
2. `cloud/case_http.py` — `/health` returns partner fields; `GET /partners` is public before auth.
3. `scripts/verify_partners_hosted.sh` — fails on liveness-only health; `--local` proves the fix without keys.
4. Product boundary preserved: hosted `/clear` stays non-public; Parallel runtime path on hosted is `clearance/cases.py → find_sources`; ADK `/clear` remains local desk.

## Oscar next click

```bash
# after reviewing this PR
bash deploy.sh   # Oscar only
bash scripts/verify_partners_hosted.sh
python3 scripts/eval_hosted_partner_surface.py
```

Expect after deploy: live `shipping_pass=True`, `/partners` HTTP 200 JSON, `/health` carries `engine_default` + `parallel`.
