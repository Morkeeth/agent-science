# DESIGN PARTNER LOOP — friction template · slice 6 prep

**Audience:** Oscar sends to one real clearance / research lead.  
**Goal:** one production runs a real question or script through Agent Science; friction lands in `CURSOR-LOG.md`.

**Product front door:** CLI/MCP first. Hosted Cloud Run is a **private workspace** (login token). Shared public `/clear` is local-only.

---

## Path A — Terminal (preferred, no hosted account)

1. Clone and install:
   ```bash
   git clone https://github.com/Morkeeth/agent-science.git && cd agent-science
   python3 scripts/install-cli.py
   pip install -r requirements.txt   # Parallel SDK + ADK when keys exist
   ```
2. Cold path without keys:
   ```bash
   bash scripts/verify_cold_clone.sh
   python3 -m clearance lookup "Directive 2012/28/EU"
   ```
3. Script clearance on the local desk (ADK default when `AGENT_BUILDER=1`):
   ```bash
   export PORT=8099 AGENT_BUILDER=1
   # PARALLEL_API_KEY / Vertex ADC for live discovery — partner's own keys
   python3 cloud/service.py
   curl -s -X POST localhost:8099/clear \
     -H 'Content-Type: application/json' \
     -d '{"script":"<paste narration>","subject":"<their-tag>"}'
   ```
4. Second script, **same subject** — look for `corpus_hits ≥ 1` and fewer `parallel_calls`.

---

## Path B — Hosted private workspace (Oscar issues access token)

1. Open `https://agent-science-568004190078.us-central1.run.app/` → sign in with token Oscar sends (never put the token in a URL).
2. Create a research case from their real question; enable live research only if budget allows.
3. Inspect sources, record a decision with rationale + evidence IDs.
4. Public partner proof (no login): `/health` and `/partners` — confirm Parallel/Gemini/ADK readiness fields.

Do **not** tell partners to `POST /clear` on the hosted URL — that route is gated (401). Clearance demo = Path A.

---

## Friction checklist (partner fills in)

| # | Question | Partner answer | Our action |
|---|----------|----------------|------------|
| 1 | Path used — CLI desk or hosted workspace? | | |
| 2 | How long from paste/question to usable output? | | |
| 3 | Any claim wrongly SOURCED? (paste claim_id / quote) | | |
| 4 | Any refuse that they would have cleared manually? | | |
| 5 | Was the UNSOURCED / refuse **reason** actionable? | | |
| 6 | Did compounding work on run 2? (Parallel delta / corpus_hits) | | |
| 7 | Subject tag / case naming — intuitive or confusing? | | |
| 8 | Output format — HTML / JSON / CLI — fit for their pipeline? | | |
| 9 | Blocker that would stop them paying or adopting? | | |

---

## What we measure from the session

- `parallel_calls` run 1 vs run 2 (JSON report) when using local `/clear`
- `corpus_hits` on run 2
- Count of UNSOURCED by `cause`
- Time-to-report (wall clock)
- Hosted: whether `/health` showed `engine_default: adk` and `parallel: true` after Oscar deploy

---

## Oscar → partner email (draft)

> Subject: 15-minute Agent Science trial  
>  
> We built a truth desk: every checkable claim comes back SOURCED (verbatim quote + URL) or UNSOURCED (named reason). Same layer powers agent research cases.  
>  
> **Try it (no account):** clone https://github.com/Morkeeth/agent-science · `bash scripts/verify_cold_clone.sh` · paste one page into local `POST /clear` (README).  
> **Or:** I can send a hosted workspace token for private cases.  
>  
> **Reply with:** anything wrongly sourced/unsourced, and whether refusal reasons are usable.  
>  
> Constraint we will not break: if the document does not contain the exact passage, we refuse — no paraphrase.

---

## Log destination

Partner friction → append to `CURSOR-LOG.md` under `## Design partner · <date>`.  
Slice 6 done-when: one real lead + friction list (Oscar owns outreach).
