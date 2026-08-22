# SUBMISSION — Agent Science · Agentic Cinema

**Event:** Agentic Cinema · Devpost · Sep 9 2026 2:00pm PDT  
**Repo:** https://github.com/Morkeeth/agent-science — **PRIVATE until submission day.**
7,415 registrants; Devpost requires public *at submit*, not before. Flipping early publishes the idea to the field for 18 days and buys nothing.  
**License:** MIT (`LICENSE`)

## Hosted URL

~~https://agent-science-568004190078.us-central1.run.app~~ — **DO NOT USE.**

This revision was deployed with a pre-fix script that wrote **both API keys in plaintext**
into the Cloud Run service config, its immutable revisions, and its Cloud Build logs.
**Both keys must be rotated; removing them does not close it.** The hosted URL is
re-established after rotation with the fixed `deploy.sh` — which needs no Gemini key at
all (Vertex + the runtime service account) and puts Parallel in Secret Manager.

- Paste UI: `/`
- API: `POST /clear` with `{"script": "...", "subject": "dust-bowl"}`
- Health: `GET /health`

## Runtime integrations (judge-checkable)

| Integration | Status | Receipt |
|-------------|--------|---------|
| Gemini (extract + locate) | ✅ | `agent_science.py`, `clearance/gemini.py`, `clearance/extract.py` |
| Parallel Search | ✅ | `clearance/search.py` — called on default path |
| Google Cloud (Vertex) | ✅ | `clearance/gemini.py` — answers as `gemini-3.5-flash (vertex:hack-fleet)` on the default path |
| Google Cloud (Cloud Run) | ⏸ | deployed, then withdrawn over the key leak. Re-deploy after rotation |
| Agent Builder (ADK) | ❌ **NOT PROVEN** | `cloud/agent.py` exists but needs `google-adk` installed and **has never executed**. The seam exists; the service is not called. Not counted until `env -u` proves it. |

## Checklist

- [ ] Hosted project URL — **withdrawn pending key rotation**
- [ ] Public repo + OSS license (MIT) — repos private; public only when submitting
- [ ] Demo video ≤3 min — **PARKED until build is exhibit-ready**
- [ ] Devpost text description — parked
- [ ] Sealed prediction (see below) — after compounding exhibit works

## Sealed prediction (draft — date when exhibit is real)

On a second `POST /clear` with the **same subject tag** and overlapping claim text, **`corpus_hits ≥ 1`** and **`parallel_calls` lower than the first run** on the same Cloud Run instance.

## Demo path (for later — not next)

Use `fixtures/scripts/documentary-orphan-works.txt` — **7 claims, 6 SOURCED, 1 UNSOURCED**,
written from general knowledge and not from any source, so the gap is true rather than
chosen. Do **not** use `PLUMBING-TEST-do-not-quote.txt`: it was built from the article
Parallel then "found", so its 5/5 is a round trip. See `docs/FINDING-circular-sourcing.md`.

```bash
curl -X POST https://agent-science-568004190078.us-central1.run.app/clear \
  -H 'Content-Type: application/json' \
  -d @- <<'EOF'
{"script":"...", "subject": "dust-bowl"}
EOF
```
