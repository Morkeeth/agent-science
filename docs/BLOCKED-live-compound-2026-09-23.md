# BLOCKED — live compound exhibit · 2026-09-23

**Attempt:** orphan-works / compound A/B on hosted or local for night wave.

## Exact missing credentials / access

| Need | State on this VM |
|------|------------------|
| `PARALLEL_API_KEY` | **absent** (`env` empty; `~/.config/keys/parallel.key` missing) |
| `GEMINI_API_KEY` / Vertex ADC | **absent** |
| `WORKSPACE_TOKEN` / `AGENT_SCIENCE_WORKSPACE_TOKEN` | **absent** |
| Hosted `POST /clear` without token | **401** (private-workspaces) |

## Commands run

```bash
(test -n "$PARALLEL_API_KEY" && echo PARALLEL=set || echo PARALLEL=missing)   # missing
(test -n "$GEMINI_API_KEY" && echo GEMINI=set || echo GEMINI=missing)         # missing
test -f ~/.config/keys/parallel.key && echo PRESENT || echo MISSING          # MISSING
curl -sS -m 15 https://agent-science-568004190078.us-central1.run.app/health
# → {"ok": true, "service": "agent-science", "mode": "private-workspaces",
#     "revision": "agent-science-00028-hed"}   # partner fields still stripped
curl -sS -o /tmp/clear.body -w '%{http_code}' -X POST \
  https://agent-science-568004190078.us-central1.run.app/clear \
  -H 'Content-Type: application/json' \
  -d '{"script":"The Dust Bowl displaced 2.5 million people.","subject":"dust-bowl"}'
# → 401
```

## Authoritative offline arms (re-run tonight)

```bash
python3 scripts/eval_refusal_baseline.py
# baseline 5/6=0.833 · shipping 6/6=1.000 · delta +1
python3 scripts/compound_exhibit_receipt.py
# offline A=2→B=1 Parallel when seeded — no live keys required
python3 scripts/eval_artifact_claims.py
# shipping 10/10 beats null 9/10; planted AC10 STALE
```

**Do not** claim a live hosted compound pass from this session. Oscar: rotate keys if needed (`AS-KEYS-ROTATE`), deploy partner-health fix, export workspace token, re-run `bash scripts/verify_partners_hosted.sh`.
