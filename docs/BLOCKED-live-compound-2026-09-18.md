# BLOCKED — live compound exhibit · 2026-09-18

**Attempt:** orphan-works / compound A/B on hosted desk for night-wave Sep 9 gaps.

## Exact missing credentials / access

| Need | State on this VM / live |
|------|-------------------------|
| `PARALLEL_API_KEY` | **absent** (`env` + `~/.config/keys/parallel.key` missing) |
| `GEMINI_API_KEY` / Vertex ADC | **absent** for local live clear |
| Hosted `POST /clear` | **401** — private-workspaces; unauthenticated clear is local-only |
| Workspace bearer token | **absent** |
| Hosted `/health` partner fields | **stripped** — revision `agent-science-00028-hed` returns only `ok/service/mode/revision` |
| Hosted `/partners` | **303 → /login** on custom domain (not public JSON); tree fix serves before auth |

## Commands run (at object)

```bash
# keys
(test -n "$PARALLEL_API_KEY" && echo PARALLEL=set || echo PARALLEL=missing)  # missing
(test -f ~/.config/keys/parallel.key && echo present || echo absent)          # absent

# health — stripped
curl -sS https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
# → {"ok": true, "service": "agent-science", "mode": "private-workspaces",
#     "revision": "agent-science-00028-hed"}

# partners — auth wall (not 200 JSON)
curl -sS -D - -o /dev/null https://agent-science-568004190078.us-central1.run.app/partners | head -5
# → HTTP/2 303  location: …/partners  (then login when followed)

# clear — refused
curl -sS -o /tmp/clear.body -w '%{http_code}\n' -X POST \
  https://agent-science-568004190078.us-central1.run.app/clear \
  -H 'Content-Type: application/json' \
  -d '{"script":"Directive 2012/28/EU covers orphan works.","subject":"orphan-works-probe"}'
# → 401
```

## Authoritative offline arms (re-run tonight)

```bash
python3 scripts/compound_exhibit_receipt.py
# A=2 → B=1 Parallel · corpus_hits B=2 · exit 0

python3 scripts/eval_cost_from_billing.py
# baseline Parallel 5 ($0.0250) vs shipping 3 ($0.0150) · invoice BLOCKED · exit 0

bash scripts/prove_partner_health_local.sh
# PROVE_PARTNER_HEALTH_LOCAL OK · engine_default=adk
```

**Do not** claim a live hosted compound pass from this session. Oscar: rotate keys if needed,
`bash deploy.sh` per `docs/DEPLOY-PREP-2026-09-18.md`, export workspace token, re-run
`bash scripts/verify_partners_hosted.sh`.
