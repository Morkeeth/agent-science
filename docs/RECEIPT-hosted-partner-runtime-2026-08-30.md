# RECEIPT — all four partners called at runtime on hosted desk · 2026-08-30

**URL:** https://agent-science-568004190078.us-central1.run.app

Each partner must be **called at runtime** on the default path — not documented only.

---

## 1 · `/health` — partner presence

```bash
curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
```

**Output this run:**

```json
{
    "ok": true,
    "service": "agent-science",
    "gemini": true,
    "gemini_path": "vertex:hack-fleet",
    "parallel": true,
    "agent_builder": true,
    "adk_version": "2.7.1",
    "engine_default": "adk"
}
```

| Partner | Field | Value |
|---------|-------|-------|
| Gemini / Vertex | `gemini_path` | `vertex:hack-fleet` |
| Parallel | `parallel` | `true` |
| Google Cloud | `service` | `agent-science` on Cloud Run |
| Agent Builder / ADK | `engine_default` | `adk` |

---

## 2 · `POST /clear` — default path uses ADK + Parallel

```bash
curl -s -X POST https://agent-science-568004190078.us-central1.run.app/clear \
  -H 'Content-Type: application/json' \
  -d '{"script":"The Dust Bowl displaced 2.5 million people.","subject":"dust-bowl-receipt-test"}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print({k:d.get(k) for k in ['engine','parallel_calls','claims_extracted','sourced','unsourced']})"
```

**Output this run:**

```
{'engine': 'adk', 'parallel_calls': 1, 'claims_extracted': 1, 'sourced': 0, 'unsourced': 1}
```

- **ADK:** `engine: adk` stamped on response.
- **Parallel:** `parallel_calls: 1` — search invoked for unsourced claim.
- **Gemini:** inside ADK clearance pipeline (Vertex ADC on Cloud Run SA).
- **GCP:** response served from Cloud Run revision.

---

## 3 · Compound exhibit (live A/B)

See `docs/RECEIPT-live-compound-exhibit-2026-08-30.md` — Run A `parallel_calls=2`, Run B `parallel_calls=1`, `corpus_hits=2`.

---

## What is NOT proved

- Local VM without ADC/keys — see `docs/BLOCKED-live-compound-exhibit-2026-08-30.md`.
- `deploy.sh` execution — Oscar only.
