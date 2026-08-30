# DESIGN PARTNER LOOP — friction template · slice 6 prep

**Audience:** Oscar sends to one real clearance lead before Sep 9.  
**Goal:** one production runs their script through the desk; friction list lands in `CURSOR-LOG.md`.

---

## Script upload flow (what the partner does)

1. Open hosted desk: `https://agent-science-568004190078.us-central1.run.app/` (after Oscar deploy).
2. Set **subject shelf** — a tag their team reuses across episodes (e.g. `season-2-ep3`).
3. Paste **documentary narration** (plain text, not PDF).
4. Click **Clear script** → gap report HTML or JSON via API:
   ```bash
   curl -s -X POST https://agent-science-568004190078.us-central1.run.app/clear \
     -H 'Content-Type: application/json' \
     -d '{"script":"<paste>","subject":"<their-tag>"}'
   ```
5. **Second script** on same subject — partner should see `corpus_hits ≥ 1` and fewer Parallel calls (compounding).

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
| 7 | Output format — HTML memo vs JSON for their pipeline? | | |
| 8 | Blocker that would stop them paying? | | |

---

## What we measure from the session

- `parallel_calls` run 1 vs run 2 (from JSON report)
- `corpus_hits` on run 2
- Count of UNSOURCED by `cause` (especially `no_independent_source`, `search_found_no_admissible_source`)
- Time-to-report (wall clock)

---

## Oscar → partner email (draft)

> Subject: 15-minute clearance desk trial  
>  
> We built a desk that returns every checkable claim as SOURCED (verbatim quote + URL) or UNSOURCED (named reason).  
>  
> **Try it:** [hosted URL] — paste one page of narration, pick a subject tag, clear. Paste a second page with the **same tag** and tell us if the Parallel call count drops.  
>  
> **Reply with:** anything wrongly sourced/unsourced, and whether the refusal reasons are usable in your workflow.  
>  
> Constraint we won't break: if the document doesn't contain the exact passage, we refuse — no paraphrase.

---

## Log destination

Partner friction → append to `CURSOR-LOG.md` under `## Design partner · <date>`.  
Slice 6 done-when: one real lead + friction list (Oscar owns outreach).
