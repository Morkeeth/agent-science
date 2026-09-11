# DESIGN PARTNER LOOP — friction template · slice 6 prep

**Audience:** Oscar sends to one real clearance / research lead.  
**Goal:** one production runs a real script or research question; friction list lands in `CURSOR-LOG.md`.  
**Updated 2026-09-11:** hosted Cloud Run is **private workspaces** — do **not** send partners to public `POST /clear` on the hosted URL (that route is local-only and returns auth errors).

---

## Path A — local clearance desk (script gap report)

Partner needs a clone + Parallel key (Oscar provisions a short-lived key out of band).

```bash
git clone https://github.com/Morkeeth/agent-science.git && cd agent-science
python3 scripts/seed_document_cache.py   # offline fixtures
export PARALLEL_API_KEY=…                # Oscar-issued, never committed
export AGENT_BUILDER=1 GCP_PROJECT=hack-fleet
python3 cloud/service.py                 # desk on :8080 — NOT the hosted URL
```

1. Open `http://127.0.0.1:8080/` on the partner machine (or Oscar screenshare).
2. Set **subject shelf** — a tag their team reuses (e.g. `season-2-ep3`).
3. Paste **documentary narration** (plain text).
4. Clear → gap report. Or:
   ```bash
   curl -s -X POST http://127.0.0.1:8080/clear \
     -H 'Content-Type: application/json' \
     -d '{"script":"<paste>","subject":"<their-tag>"}'
   ```
5. **Second script** on the same subject — expect `corpus_hits ≥ 1` and fewer Parallel calls.

**Constraint they will see:** verbatim span or UNSOURCED — never paraphrase.

---

## Path B — hosted private workspace (research case)

Partner gets a **workspace bearer token** from Oscar (never in a URL).

1. Open hosted origin → sign in with the token.
2. Create a case with their real question (no private scripts in the discovery query unless they intend it).
3. Inspect sources → record a decision with rationale + evidence IDs.
4. Return later: `review` / refresh — does the decision still hold?

Hosted public proof surfaces (no token): `GET /health` · `GET /partners` after Oscar redeploy of the 2026-09-11 admissibility fix.

---

## Path C — CLI / MCP (fleet default)

```bash
python3 -m clearance lookup "their claim"          # free tier first
python3 -m clearance case create --question "…"
```

---

## Friction checklist (partner fills in)

| # | Question | Partner answer | Our action |
|---|----------|----------------|------------|
| 1 | Which path did you use (A local desk / B hosted case / C CLI)? | | |
| 2 | How long from paste/question to usable output? | | |
| 3 | Any claim wrongly SOURCED? (paste claim_id) | | |
| 4 | Any claim wrongly UNSOURCED that they would clear manually? | | |
| 5 | Was the **reason** on UNSOURCED actionable? | | |
| 6 | Did compounding work on script 2? (Parallel delta) — Path A only | | |
| 7 | Subject tag / case naming — intuitive or confusing? | | |
| 8 | Output format — HTML memo vs JSON vs case brief for their pipeline? | | |
| 9 | Blocker that would stop them paying / adopting? | | |

---

## What we measure from the session

- Path A: `parallel_calls` run 1 vs run 2 · `corpus_hits` on run 2 · UNSOURCED by `cause`
- Path B: time-to-first-decision · whether they could name a challenge
- Path C: whether `live=false` lookup answered before a paid call
- Wall-clock time-to-report

---

## Oscar → partner email (draft)

> Subject: 15-minute Agent Science trial  
>  
> We built a truth layer: every checkable claim comes back as SOURCED (verbatim quote + URL) or UNSOURCED (named reason).  
>  
> **Try it one of two ways:**  
> 1) Screenshare a local desk clear on a page of your narration (compounding on a second paste with the same subject tag).  
> 2) Use a private hosted workspace token to open a research case on a real question.  
>  
> **Do not** use public `POST /clear` on the Cloud Run URL — that surface is local-only.  
>  
> **Reply with:** anything wrongly sourced/unsourced, and whether the refusal reasons are usable in your workflow.  
>  
> Constraint we won't break: if the document doesn't contain the exact passage, we refuse — no paraphrase.

---

## After the session

- Paste friction answers into `CURSOR-LOG.md` under a dated heading.
- File bugs as FINDING docs when a wrongly SOURCED row appears.
- Oscar owns outreach and token issuance.
