# BLOCKED — live compound exhibit · 2026-08-30

**Subject:** orphan-works A/B on `documentary-orphan-works*.txt`  
**Mode attempted:** live (Gemini extract + Parallel search)

## Missing credentials (exact)

| Partner | Required | Present on VM |
|---------|----------|---------------|
| Gemini / Vertex | `GCP_PROJECT` + ADC **or** `~/.config/keys/gemini.key` | **No** — no `~/.config/keys/`, no `GEMINI_API_KEY`, no `GOOGLE_APPLICATION_CREDENTIALS` |
| Parallel | `PARALLEL_API_KEY` **or** `~/.config/keys/parallel.key` | **No** |

## What was run instead

Offline compound exhibit with faked network boundaries:

```bash
python3 scripts/compound_exhibit_receipt.py
# Run A parallel=2 → Run B parallel=1, corpus_hits=2
```

Receipt: `docs/COMPOUND-EXHIBIT-2026-08-29.md`

## Unblock path (Oscar)

1. Place keys at `~/.config/keys/{gemini,parallel}.key` (0600) **or** deploy via `deploy.sh` (Vertex ADC + Secret Manager).
2. Run:
   ```bash
   python3 agent_science.py fixtures/scripts/documentary-orphan-works.txt --subject orphan-works
   python3 agent_science.py fixtures/scripts/documentary-orphan-works-B.txt --subject orphan-works
   ```
3. Seal prediction in `docs/SUBMISSION-PACK-2026-08-29.md` when hosted GCS shelf shows B.parallel < A.parallel.

## Honest status

Live compound exhibit: **BLOCKED** on credentials. Offline A/B: **SHIPPED** with measured delta.
