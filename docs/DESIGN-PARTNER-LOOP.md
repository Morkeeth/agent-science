# DESIGN PARTNER LOOP — friction template · slice 6 prep

**Audience:** Oscar sends to one real clearance lead before Sep 9.  
**Goal:** one production runs their script through the desk; friction list lands in `CURSOR-LOG.md`.  
**Updated:** 2026-09-04 — measured latencies + known blockers from honesty night.

---

## Script upload flow (what the partner does)

1. Open hosted desk: `https://agent-science-568004190078.us-central1.run.app/` (after Oscar deploy).
2. Set **subject shelf** — a tag their team reuses across episodes (e.g. `season-2-ep3`).
3. Paste **documentary narration** (plain text, not PDF). **Keep under ~1 page for the trial** — full orphan-works script (~9 claims) hits Cloud Run **504 @ 300s** (`docs/FINDING-orphan-works-timeout-2026-09-03.md`).
4. Click **Clear script** → gap report HTML or JSON via API:
   ```bash
   curl -s -X POST https://agent-science-568004190078.us-central1.run.app/clear \
     -H 'Content-Type: application/json' \
     -d '{"script":"<paste>","subject":"<their-tag>"}'
   ```
5. **Second script** on same subject — partner should see `corpus_hits ≥ 1`. **Do not promise Parallel always drops** — overnight honesty runs showed soft flat (1→1) when Run B adds a new claim; film **corpus_hits**, not Parallel alone (`docs/RECEIPT-partner-honesty-night-2026-09-04.md`).

### Measured wall times (hosted · 2026-09-04 honesty exhibit)

| Run shape | elapsed_s (object) |
|-----------|-------------------:|
| Fresh 2-claim clear (SHIP_A) | 22–41 s |
| Repeat subject with overlap (SHIP_B) | 15–26 s |
| Naive fresh (distinct subject) | 18–47 s |

Partner expectation to set: **under a minute for a short paste**, not instant.

---

## Friction checklist (partner fills in)

| # | Question | Partner answer | Our action |
|---|----------|----------------|------------|
| 1 | How long from paste to report? | | Compare to table above |
| 2 | Any claim wrongly SOURCED? (paste claim_id) | | |
| 3 | Any claim wrongly UNSOURCED that they would clear manually? | | |
| 4 | Was the **reason** on UNSOURCED actionable? | | |
| 5 | Did compounding work on script 2? (`corpus_hits ≥ 1`) | | Parallel may stay flat — ask about hits |
| 6 | Subject tag — intuitive or confusing? | | |
| 7 | Output format — HTML memo vs JSON for their pipeline? | | |
| 8 | Blocker that would stop them paying? | | |
| 9 | Did a longer script time out / error? | | Known: full orphan-works → 504 @ 300s |

---

## What we measure from the session

- `parallel_calls` run 1 vs run 2 (from JSON report) — **secondary**
- `corpus_hits` on run 2 — **primary compound signal**
- Count of UNSOURCED by `cause` (especially `no_independent_source`, `search_found_no_admissible_source`)
- Time-to-report (wall clock)
- Whether `engine` stamped `adk`

---

## Oscar → partner email (draft)

> Subject: 15-minute clearance desk trial  
>  
> We built a desk that returns every checkable claim as SOURCED (verbatim quote + URL) or UNSOURCED (named reason).  
>  
> **Try it:** [hosted URL] — paste one page of narration, pick a subject tag, clear. Paste a second page with the **same tag** and tell us if `corpus_hits` rises (Parallel may or may not drop).  
>  
> **Reply with:** anything wrongly sourced/unsourced, and whether the refusal reasons are usable in your workflow.  
>  
> Constraint we won't break: if the document doesn't contain the exact passage, we refuse — no paraphrase.  
> **Please keep the first paste short** (one page) — longer scripts can hit the 300s timeout.

---

## Log destination

Partner friction → append to `CURSOR-LOG.md` under `## Design partner · <date>`.  
Slice 6 done-when: one real lead + friction list (Oscar owns outreach).
