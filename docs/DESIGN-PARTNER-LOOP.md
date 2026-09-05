# DESIGN PARTNER LOOP — friction template · slice 6 prep

**Audience:** Oscar sends to one real clearance lead before Sep 9.  
**Goal:** one production runs their script through the desk; friction list lands in `CURSOR-LOG.md`.

> **Gate before sending:** live `/health` must show `engine_default: adk` and
> `mode: private-workspaces+public-desk`. As of 2026-09-05, revision `00026-zel` is
> partner-dark — Oscar must redeploy dual surface first
> (`docs/FINDING-hosted-partner-strip-2026-09-05.md`).

---

## Script upload flow (what the partner does)

1. Open hosted desk: `https://agent-science-568004190078.us-central1.run.app/` (after Oscar deploy of dual surface).
2. Set **subject shelf** — a tag their team reuses across episodes (e.g. `season-2-ep3`).
3. Paste **documentary narration** (plain text, not PDF).
4. Click **Clear script** → gap report HTML or JSON via API:
   ```bash
   curl -s -X POST https://agent-science-568004190078.us-central1.run.app/clear \
     -H 'Content-Type: application/json' \
     -d '{"script":"<paste>","subject":"<their-tag>"}'
   ```
5. **Second script** on same subject — partner should see `corpus_hits ≥ 1` and fewer Parallel calls (compounding).

Optional: partner with a workspace token can also use `/cases` for research decisions — separate from the clearance desk paste flow.

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
| 9 | Did `/health` and `/partners` make the four partners obvious? | | |

---

## What we measure from the session

- `parallel_calls` run 1 vs run 2 (from JSON report)
- `corpus_hits` on run 2
- Wall time paste → report
- Count of SOURCED / UNSOURCED rows the partner disputes

---

## Oscar → partner email (draft)

Subject: 30-minute clearance pass on your narration?

Hi — we built a desk that returns every checkable claim as a verbatim quote + URL, or UNSOURCED with a named reason (never a paraphrase). Could you paste one short documentary script and tell us where it frictioned? Link: https://agent-science-568004190078.us-central1.run.app/ — reply with the checklist above.

---

## After the session

Partner friction → append to `CURSOR-LOG.md` under `## Design partner · <date>`.  
Do not change product rules from one session; batch themes.

**Owner:** Oscar outreach. Build lane only prepares this template.
