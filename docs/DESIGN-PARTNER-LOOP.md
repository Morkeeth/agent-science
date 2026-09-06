# DESIGN PARTNER LOOP — friction template · slice 6 prep

**Audience:** Oscar sends to one real clearance / research lead before Sep 9.  
**Goal:** one production tries the product; friction list lands in `CURSOR-LOG.md`.

**Product boundary (2026-09-06):** hosted Cloud Run is **private workspaces** (token required). The unauthenticated paste-script desk is the **local clearance desk**. Do not send partners a broken public `/clear` URL.

---

## Path A — Local clearance desk (script → gap report)

Oscar runs locally (or shares a screen) with keys configured:

```bash
export PORT=8099 AGENT_BUILDER=1 GCP_PROJECT=hack-fleet
# PARALLEL_API_KEY from Secret Manager / ~/.config/keys/parallel.key — never paste into chat
env -u AGENT_SCIENCE_HOSTED -u K_SERVICE python3 cloud/service.py
```

1. Open `http://127.0.0.1:8099/`
2. Set **subject shelf** — a tag their team reuses (e.g. `season-2-ep3`).
3. Paste **documentary narration** (plain text).
4. Click **Clear script** → gap report; or API:
   ```bash
   curl -s -X POST http://127.0.0.1:8099/clear \
     -H 'Content-Type: application/json' \
     -d '{"script":"<paste>","subject":"<their-tag>"}'
   ```
5. **Second script** on same subject — expect `corpus_hits ≥ 1` and fewer Parallel calls.

---

## Path B — Hosted private workspace (research case)

1. Oscar issues a workspace access token (never put in a URL).
2. Partner opens `https://agent-science-568004190078.us-central1.run.app/login`
3. Signs in → creates a case with their question / sources.
4. Inspects evidence, records a decision, returns later via review.

Public partner wiring (no token): `GET /health`, `GET /partners` — after the 2026-09-06 partner-surface deploy.

---

## Friction checklist (partner fills in)

| # | Question | Partner answer | Our action |
|---|----------|----------------|------------|
| 1 | Path A or B — which matched their workflow? | | |
| 2 | How long from paste/create to usable output? | | |
| 3 | Any claim wrongly SOURCED? (paste claim_id) | | |
| 4 | Any claim wrongly UNSOURCED they would clear manually? | | |
| 5 | Was the **reason** on UNSOURCED / refusal actionable? | | |
| 6 | Did compounding work on script 2? (Parallel delta) | | |
| 7 | Subject tag / case naming — intuitive or confusing? | | |
| 8 | Output format — HTML memo vs JSON for their pipeline? | | |
| 9 | Blocker that would stop them paying? | | |

---

## What we measure from the session

- Path A: `parallel_calls` run 1 vs run 2; `corpus_hits` on run 2; UNSOURCED by `cause`
- Path B: case version churn; decisions flagged on refresh; time-to-first-decision
- Wall-clock time-to-report

---

## Oscar → partner email (draft)

> Subject: 15-minute Agent Science trial  
>  
> We return every checkable claim as SOURCED (verbatim quote + URL) or UNSOURCED (named reason). The shelf compounds so the second ask is cheaper.  
>  
> **Option A (script clearance):** Oscar screenshares the local desk — paste one page of narration, then a second page with the same subject tag.  
> **Option B (hosted research):** Oscar sends a workspace token separately (not in this email). Sign in, open a case, inspect sources.  
>  
> **Reply with:** anything wrongly sourced/unsourced, and whether refusal reasons are usable in your workflow.  
>  
> Constraint we won't break: if the document doesn't contain the exact passage, we refuse — no paraphrase.

---

## Log destination

Partner friction → append to `CURSOR-LOG.md` under `## Design partner · <date>`.  
Slice 6 done-when: one real lead + friction list (Oscar owns outreach).
