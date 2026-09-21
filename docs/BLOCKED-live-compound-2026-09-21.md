# BLOCKED — live compound exhibit · 2026-09-21

**Attempt:** orphan-works / compound A/B on hosted desk for night-wave submit-path gaps.

## Exact missing credentials / access

| Need | State on this VM |
|------|------------------|
| `PARALLEL_API_KEY` | **absent** (`env` + `~/.config/keys/parallel.key` missing) |
| `GEMINI_API_KEY` / Vertex ADC | **absent** for local live clear |
| Hosted `POST /clear` without workspace token | **401** — private-workspaces; unauthenticated clear is local-only |
| `WORKSPACE_TOKEN` / `AGENT_SCIENCE_WORKSPACE_TOKEN` | **absent** |

## Commands run (tonight)

```bash
env | grep -E 'PARALLEL|GEMINI|WORKSPACE' | sed 's/=.*/=PRESENT/'   # empty
test -f ~/.config/keys/parallel.key && echo PRESENT || echo MISSING   # MISSING
curl -sS https://agent-science-568004190078.us-central1.run.app/health
# → {"ok": true, "service": "agent-science", "mode": "private-workspaces",
#     "revision": "agent-science-00028-hed"}   # partner fields still stripped
curl -sS -o /tmp/clear.body -w '%{http_code}' -X POST \
  https://agent-science-568004190078.us-central1.run.app/clear \
  -H 'Content-Type: application/json' \
  -d '{"script":"The Dust Bowl displaced 2.5 million people.","subject":"dust-bowl-night-2026-09-21"}'
# → 401
```

## Authoritative offline arms (re-run tonight)

```bash
python3 scripts/eval_refusal_baseline.py     # baseline 5/6 · shipping 6/6 · delta +1
python3 scripts/eval_refusal_ablation.py     # ablation 5/6 · shipping 6/6 · delta +1
python3 scripts/compound_exhibit_receipt.py  # A=2→B=1 Parallel · corpus_hits B=2
python3 scripts/eval_cost_gate.py            # prices Search door from dated card; billing RED
```

**Do not** claim a live hosted compound pass from this session. Oscar: rotate keys if needed,
deploy partner-health fix, export workspace token, re-run `bash scripts/verify_partners_hosted.sh`.
