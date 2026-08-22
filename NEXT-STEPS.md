# NEXT STEPS — read this first, every session

**PRODUCT:** Agent Science · **Agentic Cinema, Sep 9 14:00 PDT · Parallel track**

## State @ deploy
- **Hosted URL:** https://agent-science-568004190078.us-central1.run.app
- **GCP project:** `hack-fleet` · Cloud Run service `agent-science`
- **Entry point:** `agent_science.py` + `cloud/service.py` + `cloud/agent.py` (ADK)
- **Runtime:** Gemini ✅ · Parallel ✅ · Cloud Run ✅
- **Controls:** `python3 tests/test_watch_it_go_red.py` → **41 passed**
- **License:** MIT

## Queue — what remains

| # | Slice | Owner | Status |
|---|-------|-------|--------|
| 1 | End-to-end + corpus in `clear_script()` | Build | ✅ |
| 2 | Cloud Run hosted URL | Deploy | ✅ |
| 3 | ≤3min video on hosted URL | Oscar | ⬜ |
| 4 | GitHub push (both repos) | Oscar | ⬜ |
| 5 | Devpost submit + sealed prediction dated | Oscar | ⬜ |
| 6 | Phase 0 hours in hack-agent-science/PHASE-0.md | Oscar | ⬜ |

## Redeploy

```bash
cd ~/CODE/cleared && ./deploy.sh
```

## Review lane

`FOR-CURSOR.md` + `CURSOR-LOG.md` · append-only · never `git add -A`
