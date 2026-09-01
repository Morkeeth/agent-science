---
date: 2026-08-23
lane: HACK AGENT SCIENCE
project: Agent Science
event: Agentic Cinema · Devpost · deadline 2026-09-09 14:00 PT
status: BUILD COMPLETE — blocked only on Oscar's clicks
---

# CLOSING FOUR LINES

**HEADLINE**
A clearance desk that refuses to round up. It cleared 0 of 10 on a real script and I
called it rigour; it was a category error. Fixed, it clears what can be cleared, refuses
what cannot, and never confuses the two — including inside the document a lawyer signs.

**VISION**
From 2026 the EU AI Act requires AI companies to disclose training-data sources and
respect copyright opt-outs. That is a compliance obligation with a date, and the artifact
it demands is what this engine emits: per-item provenance for facts AND assets, one
engine, with the instrument or the passage quoted verbatim. Marketplaces sell pre-cleared
data. Nobody proves clearance on material you already hold — and nobody else can tell you
a claim is **unsourceable**, because absence is not something you find by searching harder.

**PROOF** — repo `agent-science` @ `0586f25`, pushed to a PRIVATE remote at
github.com/Morkeeth/agent-science. Nothing public, nothing deployed.
- `python3 tests/test_watch_it_go_red.py` → **71 passed, 0 failed**, every control
  watched going red before it was trusted green
- `fixtures/CLEARANCE-PACK.md` — the deliverable. 50 items, facts and assets in one
  document, 39 uncleared with the blocking instrument named on each
- `fixtures/compounding/CURVE.md` — reuse compounds 0 → 20 → 39 → 46% across 4
  productions, n=56 claims; **cost per claim flat, because the corpus removes the easy
  claims first**
- `docs/MARKET-validated.md` — ClaimReview, Troveo, Human Archive, Deeptune, the AI Act
- `demo.sh` — the whole story in one real run, 253s

**HONEST VERDICT**
Three integrations run live: Vertex, Parallel, and Google Cloud. **Agent Builder is still
not called on the default path and is not counted.** The compounding number was published
wrong three times and corrected three times — each correction caught by the repo
re-running its own harness and disagreeing with the README, never by re-reading it. Five
defects tonight were mine and all five surfaced by running the artifact. The extractor
had a per-call ceiling that would have silently checked 10 claims of a 200-claim film.
Everything above is measured; the limits are stated in the files themselves.

# FIRST THING WHEN OSCAR WAKES

1. **ROTATE BOTH KEYS.** Gemini (aistudio.google.com) and Parallel (parallel.ai). They
   sit in plaintext in a Cloud Run revision that cannot be un-written. Five minutes.
2. Then redeploy with the fixed `deploy.sh` — it needs **no Gemini key at all** (Vertex +
   the runtime service account) and puts Parallel in Secret Manager.
3. Repo goes public **at submission, not before**. 7,415 registrants.
