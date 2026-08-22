# SUBMISSION — Agent Science · Agentic Cinema

**Event:** Agentic Cinema · Devpost · Sep 9 2026 2:00pm PDT  
**Repo:** `~/CODE/cleared` (canonical) · `~/CODE/hack-agent-science` (docs/fixtures)  
**License:** MIT (`LICENSE`)

## Hosted URL

**https://agent-science-568004190078.us-central1.run.app**

- Paste UI: `/`
- API: `POST /clear` with `{"script": "...", "subject": "dust-bowl"}`
- Health: `GET /health`

## Runtime integrations (judge-checkable)

| Integration | Status | Receipt |
|-------------|--------|---------|
| Gemini (extract + locate) | ✅ | `agent_science.py`, `clearance/gemini.py`, `clearance/extract.py` |
| Parallel Search | ✅ | `clearance/search.py` — called on default path |
| Google Cloud (Cloud Run) | ✅ | URL above, project `hack-fleet` |
| Agent Builder (ADK) | ✅ | `cloud/agent.py` — `build_agent()` wraps `clear_script` tool |

## Checklist

- [x] Hosted project URL
- [x] Public repo + OSS license (MIT)
- [ ] Demo video ≤3 min
- [ ] Devpost text description
- [ ] Sealed prediction (see below)

## Sealed prediction (draft — Oscar to date)

On a second `POST /clear` with the **same subject tag** and overlapping claim text, **`corpus_hits ≥ 1`** and **`parallel_calls` lower than the first run** on the same Cloud Run instance.

## Demo script for video

Use `fixtures/scripts/split-sentence.txt` or paste UI with subject `orphan-works`.

```bash
curl -X POST https://agent-science-568004190078.us-central1.run.app/clear \
  -H 'Content-Type: application/json' \
  -d @- <<'EOF'
{"script":"...", "subject": "dust-bowl"}
EOF
```
