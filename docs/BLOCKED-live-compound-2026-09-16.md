# BLOCKED — live compound exhibit · 2026-09-16 (re-probed 2026-09-20)

**Attempt:** orphan-works / compound A/B on hosted desk for partner night wave.

## Exact missing credentials / access (re-checked 2026-09-20)

| Need | State on this VM |
|------|------------------|
| `PARALLEL_API_KEY` | **absent** (`env` + `~/.config/keys/parallel.key` missing) |
| `GEMINI_API_KEY` / Vertex ADC | **absent** for local live clear (`vertex_token` falsy) |
| Hosted `POST /clear` without workspace token | **401** — private-workspaces; unauthenticated clear is local-only |
| `WORKSPACE_TOKEN` / `AGENT_SCIENCE_WORKSPACE_TOKEN` | **absent** |
| Hosted `/health` partner fields | **stripped** on `agent-science-00028-hed` (`watch_hosted_partner_health.sh` RED OK) |

## Commands run

```bash
env | grep -E 'PARALLEL|GEMINI|WORKSPACE' | sed 's/=.*/=PRESENT/'   # empty
test -f ~/.config/keys/parallel.key && echo PRESENT || echo MISSING   # MISSING
curl -sS -o /tmp/clear.body -w '%{http_code}' -X POST \
  https://agent-science-568004190078.us-central1.run.app/clear \
  -H 'Content-Type: application/json' \
  -d '{"script":"The Dust Bowl displaced 2.5 million people.","subject":"dust-bowl"}'
# → 401
bash scripts/watch_hosted_partner_health.sh   # WATCH RED OK · revision agent-science-00028-hed
```

## Authoritative offline arms (re-run 2026-09-20)

```bash
python3 scripts/eval_refusal_baseline.py       # baseline 5/6=0.833 · shipping 6/6=1.000 · delta +1
python3 scripts/eval_refusal_ablation.py       # ablation 5/6 · shipping 6/6 · delta +1
python3 scripts/prove_partner_calls_local.py   # mocked Parallel LIVE_CALLS=1 + ADK engine
```

**Do not** claim a live hosted compound pass from this session. Oscar: rotate keys if needed,
deploy partner-health + callable-gemini fix, export workspace token, re-run
`EXPECT_STATE=green bash scripts/watch_hosted_partner_health.sh` then
`bash scripts/verify_partners_hosted.sh`.
