# DESIGN PARTNER LOOP — friction template · slice 6 prep

**Audience:** Oscar sends to one real clearance / research lead.  
**Goal:** one production tries the product; friction list lands in `CURSOR-LOG.md`.  
**Updated 2026-09-15:** hosted path is private workspaces; local desk remains the paste-script clearance UI.

---

## Path A — Local / CLI desk (script clearance)

1. Clone + cold verify (no keys):
   ```bash
   git clone https://github.com/Morkeeth/agent-science.git && cd agent-science
   bash scripts/verify_cold_clone.sh
   ```
2. With Parallel key + Vertex/Gemini available, run local desk:
   ```bash
   export PORT=8099 AGENT_BUILDER=1 GCP_PROJECT=hack-fleet
   export PARALLEL_API_KEY="$(cat ~/.config/keys/parallel.key)"
   python3 cloud/service.py
   ```
3. Open `http://127.0.0.1:8099/` — set **subject shelf**, paste narration, **Clear script**.
4. Or API:
   ```bash
   curl -s -X POST http://127.0.0.1:8099/clear \
     -H 'Content-Type: application/json' \
     -d '{"script":"<paste>","subject":"<their-tag>"}'
   ```
5. Second script on same subject — expect `corpus_hits ≥ 1` and fewer Parallel calls.

---

## Path B — Hosted private workspace (research cases)

1. Oscar issues a workspace access key (Secret Manager `agent-science-workspace-access`). **Never put the token in a URL.**
2. Open `https://agent-science-568004190078.us-central1.run.app/login` — paste access key.
3. Create a case with a real research question; optionally enable live discovery.
4. Inspect sources → record a decision citing verified evidence IDs.
5. Return later via review when evidence changes.

Partner admissibility (public, no login):

```bash
curl -s https://agent-science-568004190078.us-central1.run.app/health | python3 -m json.tool
curl -s https://agent-science-568004190078.us-central1.run.app/partners | python3 -m json.tool
```

---

## Friction checklist (partner fills in)

| # | Question | Partner answer | Our action |
|---|----------|----------------|------------|
| 1 | How long from paste/question to usable result? | | |
| 2 | Any claim wrongly SOURCED / decision overclaimed? | | |
| 3 | Any refusal / gap they would clear manually? | | |
| 4 | Was the **named reason** actionable? | | |
| 5 | Did compounding / reuse help on the second pass? | | |
| 6 | Subject tag / case framing — intuitive or confusing? | | |
| 7 | Output format — HTML vs JSON vs CLI for their pipeline? | | |
| 8 | Hosted login friction — acceptable for their team? | | |
| 9 | Blocker that would stop them paying? | | |

---

## What we measure from the session

- Local clearance: `parallel_calls` run 1 vs run 2 · `corpus_hits` · UNSOURCED by `cause`
- Hosted research: live provider attempts counted · sources read · decision review flags
- Time-to-first useful result (wall clock)

---

## Oscar → partner email (draft)

> Subject: 15-minute Agent Science trial  
>  
> Agent Science returns every checkable claim as SOURCED (verbatim quote + URL) or UNSOURCED (named reason) — and keeps a private research case when you need decisions over time.  
>  
> **Try local clearance:** clone the public repo, run the desk, paste one page of narration, then a second page with the same subject tag.  
> **Or hosted workspace:** I’ll send you an access key (not a public paste URL).  
>  
> **Reply with:** anything wrongly sourced/unsourced, and whether refusal reasons are usable in your workflow.  
>  
> Constraint we won't break: if the document doesn't contain the exact passage, we refuse — no paraphrase.

---

## Log destination

Partner friction → append to `CURSOR-LOG.md` under `## Design partner · <date>`.  
Slice 6 done-when: one real lead + friction list (Oscar owns outreach).
