# DESIGN PARTNER LOOP — friction template · slice 6 prep

**Audience:** Oscar sends to one real clearance lead (or research operator) before submit.  
**Goal:** one production runs a real script/question through the product; friction list lands in `CURSOR-LOG.md`.

**Product boundary (2026-09-13):** hosted Cloud Run is **private workspaces** (auth). The public clearance desk (`POST /clear`) is the **local** path. Do not email partners a hosted `/clear` curl — it will 401/303.

---

## Path A — Local clearance desk (documentary / E&O vertical)

What the partner does on a machine with the repo (or a tarball Oscar sends):

1. Clone and boot the local desk:
   ```bash
   git clone https://github.com/Morkeeth/agent-science.git && cd agent-science
   bash scripts/verify_partners_local.sh   # proves /health engine_default=adk
   PORT=8099 AGENT_BUILDER=1 GCP_PROJECT=hack-fleet python3 cloud/service.py
   ```
2. Open `http://127.0.0.1:8099/` — paste **documentary narration** (plain text).
3. Set **subject shelf** — a tag their team reuses (e.g. `season-2-ep3`).
4. Clear → gap report (HTML or JSON):
   ```bash
   curl -s -X POST http://127.0.0.1:8099/clear \
     -H 'Content-Type: application/json' \
     -d '{"script":"<paste>","subject":"<their-tag>"}'
   ```
5. **Second script** on same subject — partner should see `corpus_hits ≥ 1` and fewer Parallel calls when a Parallel key is configured.

---

## Path B — Hosted private workspace (research / agent-operator vertical)

1. Oscar issues a **workspace access key** (never put in a URL).
2. Partner opens the hosted origin → `/login` → `/cases`.
3. Creates a research case for one production question; inspects source snapshots; records a decision.
4. Returns later via `case review` / dashboard for flagged evidence changes.

Hosted partner wiring prove (no tenant data):

```bash
curl -s https://agent-science-568004190078.us-central1.run.app/health
curl -s https://agent-science-568004190078.us-central1.run.app/partners
```

Expect `engine_default: adk` and four partners in the manifest **after** Oscar deploys the 2026-09-13 partner-surfaces fix.

---

## Friction checklist (partner fills in)

| # | Question | Partner answer | Our action |
|---|----------|----------------|------------|
| 1 | Which path did you use (A local desk / B hosted workspace)? | | |
| 2 | How long from paste/question to usable result? | | |
| 3 | Any claim wrongly SOURCED? (paste claim_id) | | |
| 4 | Any claim wrongly UNSOURCED that they would clear manually? | | |
| 5 | Was the **reason** on UNSOURCED / refusal actionable? | | |
| 6 | Did compounding work on script 2? (Parallel delta) — Path A only | | |
| 7 | Subject tag / case question — intuitive or confusing? | | |
| 8 | Output format — HTML memo vs JSON vs case brief for their pipeline? | | |
| 9 | Auth / keys — friction enough to stop a trial? | | |
| 10 | Blocker that would stop them paying? | | |

---

## What we measure from the session

- Path A: `parallel_calls` run 1 vs run 2 · `corpus_hits` on run 2 · UNSOURCED by `cause`
- Path B: time-to-first-decision · unread citations remaining · whether they returned for review
- Wall-clock time-to-report

---

## Oscar → partner email (draft)

> Subject: 15-minute Agent Science trial  
>  
> We built a truth layer that returns every checkable claim as SOURCED (verbatim quote + URL) or UNSOURCED (named reason) — and a private research workspace for builder questions.  
>  
> **Try Path A (clearance):** clone the public repo, run `bash scripts/verify_partners_local.sh`, then paste one page of narration into the local desk. Paste a second page with the **same subject tag** and tell us if Parallel calls drop.  
>  
> **Try Path B (research):** Oscar will send a workspace access key separately (not in this email). Log in, create one case, read one source snapshot, write one decision.  
>  
> **Reply with:** anything wrongly sourced/unsourced, and whether the refusal reasons are usable in your workflow.  
>  
> Constraint we won't break: if the document doesn't contain the exact passage, we refuse — no paraphrase.

---

## Log destination

Partner friction → append to `CURSOR-LOG.md` under `## Design partner · <date>`.  
Slice 6 done-when: one real lead + friction list (Oscar owns outreach).
