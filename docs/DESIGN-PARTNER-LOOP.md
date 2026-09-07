# DESIGN PARTNER LOOP — friction template · slice 6 prep

**Audience:** Oscar sends to one real clearance lead before Sep 9.  
**Goal:** one production runs their script through the desk; friction list lands in `CURSOR-LOG.md`.

**Hosted mode (2026-09-07):** Cloud Run is **private workspaces**. Unauthenticated `POST /clear` is gone. Partners use an invite key Oscar issues from Secret Manager (`agent-science-workspace-access`).

---

## Script upload flow (what the partner does)

### Option A — Hosted (invite key)

1. Open hosted desk: `https://agent-science-568004190078.us-central1.run.app/login`
2. Paste the **access key** Oscar sent (never put it in a URL or shared doc).
3. Confirm public partner wiring (optional): open `/health` — expect `engine_default: adk` and `parallel: true`.
4. Clear via API (or Oscar-provided form once filmed):
   ```bash
   export AGENT_SCIENCE_WORKSPACE_TOKEN='<invite key>'
   curl -s -X POST https://agent-science-568004190078.us-central1.run.app/api/clear \
     -H "Authorization: Bearer $AGENT_SCIENCE_WORKSPACE_TOKEN" \
     -H 'Content-Type: application/json' \
     -d '{"request_id":"<16+ random chars>","script":"<paste>","subject":"<their-tag>"}'
   ```
5. **Second script** on the same `subject` — partner should see `corpus_hits ≥ 1` and fewer or equal Parallel calls.

### Option B — Local desk (no account)

```bash
git clone https://github.com/Morkeeth/agent-science.git && cd agent-science
pip install -r requirements.txt
export PARALLEL_API_KEY=…   # or ~/.config/keys/parallel.key
export PORT=8099 AGENT_BUILDER=1 GCP_PROJECT=hack-fleet
python3 cloud/service.py
# browser: http://127.0.0.1:8099/  → paste script → Clear
```

---

## Friction checklist (partner fills in)

| # | Question | Partner answer | Our action |
|---|----------|----------------|------------|
| 1 | How long from paste to report? | | |
| 2 | Any claim wrongly SOURCED? (paste claim_id) | | |
| 3 | Any claim wrongly UNSOURCED that they would clear manually? | | |
| 4 | Was the **reason** on UNSOURCED actionable? | | |
| 5 | Did compounding work on script 2? (Parallel delta) | | |
| 6 | Subject tag — intuitive or confusing? | | |
| 7 | Output format — JSON for their pipeline vs HTML memo? | | |
| 8 | Invite-key login — friction vs open paste desk? | | |
| 9 | Blocker that would stop them paying? | | |

---

## What we measure from the session

- `parallel_calls` run 1 vs run 2 (from JSON report)
- `corpus_hits` on run 2
- Count of UNSOURCED by `cause`
- Time-to-report (wall clock)
- Whether they needed Option B (local) because hosted auth blocked them

---

## Oscar → partner email (draft)

> Subject: 15-minute clearance desk trial  
>  
> We built a desk that returns every checkable claim as SOURCED (verbatim quote + URL) or UNSOURCED (named reason).  
>  
> **Try it:** I will send you a one-time access key for https://agent-science-568004190078.us-central1.run.app/login — paste one page of narration with a subject tag, then a second page with the **same tag**, and tell us if the Parallel call count drops.  
>  
> **Reply with:** anything wrongly sourced/unsourced, and whether the refusal reasons are usable in your workflow.  
>  
> Constraint we won't break: if the document doesn't contain the exact passage, we refuse — no paraphrase.

---

## Log destination

Partner friction → append to `CURSOR-LOG.md` under `## Design partner · <date>`.  
Slice 6 done-when: one real lead + friction list (Oscar owns outreach).
