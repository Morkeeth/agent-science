# BLOCKED — live compound exhibit · 2026-09-16

**Attempt:** orphan-works / compound A/B on hosted desk for partner night wave.

## Exact missing credentials / access

| Need | State on this VM |
|------|------------------|
| `PARALLEL_API_KEY` | **absent** (`env` + `~/.config/keys/parallel.key` missing) |
| `GEMINI_API_KEY` / Vertex ADC | **absent** for local live clear |
| Hosted `POST /clear` without workspace token | **401** — private-workspaces; unauthenticated clear is local-only |
| `WORKSPACE_TOKEN` / `AGENT_SCIENCE_WORKSPACE_TOKEN` | **absent** |

## Commands run

```bash
env | grep -E 'PARALLEL|GEMINI' | sed 's/=.*/=PRESENT/'   # empty
test -f ~/.config/keys/parallel.key && echo PRESENT || echo MISSING   # MISSING
curl -sS -o /tmp/clear.body -w '%{http_code}' -X POST \
  https://agent-science-568004190078.us-central1.run.app/clear \
  -H 'Content-Type: application/json' \
  -d '{"script":"The Dust Bowl displaced 2.5 million people.","subject":"dust-bowl"}'
# → 401
```

## Authoritative offline arms (re-run tonight)

```bash
python3 scripts/eval_refusal_baseline.py   # baseline 5/6=0.833 · shipping 6/6=1.000 · delta +1
python3 scripts/eval_refusal_ablation.py   # ablation 5/6 · shipping 6/6 · delta +1
python3 scripts/compound_exhibit_receipt.py  # offline compound when seeded
```

**Do not** claim a live hosted compound pass from this session. Oscar: rotate keys if needed,
deploy partner-health fix, export workspace token, re-run `bash scripts/verify_partners_hosted.sh`.
