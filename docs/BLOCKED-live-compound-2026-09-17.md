# BLOCKED — live compound exhibit · 2026-09-17

**Attempt:** orphan-works / hosted compound A/B for night-wave submit-path close.

## Exact missing credentials / access (probed this run)

| Need | State on this VM | Command |
|------|------------------|---------|
| `PARALLEL_API_KEY` | **absent** | `test -n "$PARALLEL_API_KEY"` → missing |
| `~/.config/keys/parallel.key` | **absent** | `test -f …` → missing |
| `GEMINI_API_KEY` | **absent** | env probe → missing |
| `WORKSPACE_TOKEN` / `AGENT_SCIENCE_WORKSPACE_TOKEN` | **absent** | env probe → missing |
| Hosted `POST /clear` without token | **401** | curl below |

```bash
curl -sS -o /tmp/clear.body -w '%{http_code}\n' -X POST \
  https://agent-science-568004190078.us-central1.run.app/clear \
  -H 'Content-Type: application/json' \
  -d '{"script":"The Dust Bowl displaced 2.5 million people.","subject":"dust-bowl-night-2026-09-17"}'
# → 401
```

## Hosted surface (same revision)

```bash
curl -sS https://agent-science-568004190078.us-central1.run.app/health
# → {"ok": true, "service": "agent-science", "mode": "private-workspaces",
#     "revision": "agent-science-00028-hed"}
# Missing partner fields: gemini / parallel / engine_default (strip still live)

curl -sS -o /dev/null -w '%{http_code}\n' …/partners   # 303
curl -sS -o /dev/null -w '%{http_code}\n' …/stats      # 303
curl -sS -o /dev/null -w '%{http_code}\n' '…/search?q=test&live=false'  # 303
```

## Authoritative offline arms (re-run 2026-09-17)

```bash
python3 scripts/compound_exhibit_receipt.py
# Mode: offline · A=2 → B=1 Parallel · corpus_hits B=2 · registry 239 rows (25 GREEN)

python3 scripts/eval_cost_from_billing.py
# ALWAYS_SILENT $0 · NAIVE_NO_REUSE 5 calls · SHIPPING 3 calls · silent 3/6 vs shipping 6/6
```

**Do not** claim a live hosted compound pass from this session. Oscar: rotate keys if needed,
`bash deploy.sh` (partner-health fix is in tree), export workspace token, then
`bash scripts/verify_partners_hosted.sh`.
