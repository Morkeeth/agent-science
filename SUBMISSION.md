# SUBMISSION — Agent Science · Agentic Cinema

**Event:** Agentic Cinema · Devpost · Sep 9 2026 2:00pm PDT  
**Code:** https://github.com/Morkeeth/agent-science (private until submit)  
**License:** MIT (`LICENSE`)

One repo. `hack-agent-science` was a local docs sibling; it is not on GitHub
(404 as of 2026-08-28). Canonical plan: `BUILD-NOW.md`.

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
| Agent Builder (ADK) | ✅ hosted `/health` returns `"engine_default": "adk"`, `adk_version: 2.7.1` (curl 2026-08-28). Local `env -u` receipt remains `docs/RECEIPT-agent-builder.md` |
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
