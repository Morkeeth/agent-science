# SUBMISSION — Agent Science · Agentic Cinema

**Event:** Agentic Cinema · Devpost · Sep 9 2026 2:00pm PDT  
**Code:** https://github.com/Morkeeth/agent-science (private until submit)  
**Docs:** https://github.com/Morkeeth/hack-agent-science (private)  
**License:** MIT (`LICENSE`)

## Hosted URL

**https://agent-science-568004190078.us-central1.run.app**

- Desk UI: `/`
- API: `POST /clear` with `{"script": "...", "subject": "orphan-works"}`
- Health: `GET /health`
- Shelf: `GET /corpus?subject=orphan-works`

## Runtime integrations (honest)

| Integration | Status | Receipt |
|-------------|--------|---------|
| Gemini (extract + locate) | ✅ | live default path |
| Parallel Search | ✅ | live default path |
| Google Cloud (Cloud Run) | ✅ | URL above · project `hack-fleet` |
| Agent Builder (ADK) | ⬜ **wired as the default `/clear` path and proved LOCALLY** under `env -u GEMINI_API_KEY` (`engine: adk`, `adk_tool_calls: [clear_script_tool]`, `vertex:hack-fleet`) — receipt in `docs/RECEIPT-agent-builder.md`. Stays ⬜ until the hosted URL returns `"engine_default": "adk"`; that needs `deploy.sh`, which is Oscar's click |
| Corpus compounding | ✅ local full orphan A/B **43% search avoided** · GCS shelf in `deploy.sh` |

## Checklist

- [x] Hosted project URL
- [ ] Public repo — private now; flip at submit
- [x] OSS license (MIT)
- [ ] Demo video ≤3 min — **PARKED**
- [ ] Devpost text — parked
- [ ] Sealed prediction — after exhibit is on the live URL with durable corpus

## Sealed prediction (draft)

Second `POST /clear` same subject + overlapping claim → `corpus_hits ≥ 1` and fewer `parallel_calls` than first run on a shared corpus shelf.
