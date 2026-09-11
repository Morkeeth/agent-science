# DESIGN PARTNER LOOP — friction template · slice 6 prep

**Audience:** Oscar sends to one real clearance / licensing lead.  
**Goal:** one production runs a script through the stack; friction list lands in `CURSOR-LOG.md`.  
**Updated:** 2026-09-11 — hosted desk is private-workspaces; public anonymous `/clear` is gone.

---

## Two paths (pick one for the partner)

### A · Local / CLI (preferred for builders — no hosted account)

```bash
git clone https://github.com/Morkeeth/agent-science.git && cd agent-science
python3 scripts/boot_registry.py
python3 -m clearance lookup "Directive 2012/28/EU"
# script clearance on local desk (keys optional for fixture path):
python3 scripts/seed_document_cache.py
python3 agent_science.py fixtures/scripts/split-sentence.txt
```

Or MCP: `bash scripts/install-mcp.sh` → tool `science_lookup` / `science_clear`.

### B · Hosted workspace (Oscar issues a bearer / login key)

1. Open https://agent-science-568004190078.us-central1.run.app/login
2. Paste the access key Oscar sent (never put the key in a URL).
3. Create a research case for their clearance question — **not** the old public paste desk.
4. Public partner proof (no key): `GET /health` and `GET /partners` after Oscar redeploys the 2026-09-11 fix.

**Do not** email partners the old `POST /clear` curl against the hosted URL — it redirects to login (measured 2026-09-11).

---

## Script upload flow (what the partner does)

1. Choose path A or B above.
2. Set a **subject shelf** / case label their team reuses (e.g. `season-2-ep3`).
3. Paste **documentary narration** (plain text).
4. Run clearance → gap report: every claim SOURCED (verbatim + URL) or UNSOURCED (named cause).
5. **Second script** on the same shelf — watch for corpus reuse / fewer live search calls.

Local JSON shape (local desk):
```bash
curl -s -X POST http://127.0.0.1:8099/clear \
  -H 'Content-Type: application/json' \
  -d '{"script":"<paste>","subject":"<their-tag>"}'
```

---

## Friction checklist (partner fills in)

| # | Question | Partner answer | Our action |
|---|----------|----------------|------------|
| 1 | How long from paste to report? | | |
| 2 | Any claim wrongly SOURCED? (paste claim_id) | | |
| 3 | Any claim wrongly UNSOURCED that they would clear manually? | | |
| 4 | Was the **reason** on UNSOURCED actionable? | | |
| 5 | Did compounding work on script 2? (search / Parallel delta) | | |
| 6 | Subject/case label — intuitive or confusing? | | |
| 7 | Output format — HTML memo vs JSON for their pipeline? | | |
| 8 | Login / key friction on hosted (if used)? | | |
| 9 | Blocker that would stop them paying? | | |

---

## What we measure from the session

- Live search / `parallel_calls` run 1 vs run 2 (from JSON report)
- `corpus_hits` on run 2
- Count of UNSOURCED by `cause`
- Time-to-report (wall clock)
- Whether they needed a hosted account (path B) or stayed local (path A)

---

## Oscar → partner email (draft)

> Subject: 15-minute clearance / truth-layer trial  
>  
> We built a stack that returns every checkable claim as SOURCED (verbatim quote + URL) or UNSOURCED (named reason).  
>  
> **Try it locally (no account):** clone https://github.com/Morkeeth/agent-science and run the stranger block in the README / SUBMISSION-PACK — or paste one page into a local desk.  
>  
> **Hosted (if I sent you a key):** sign in at the hosted URL I gave you, open Cases, and work one question. Public `/health` shows partner wiring without logging in.  
>  
> **Reply with:** anything wrongly sourced/unsourced, and whether the refusal reasons are usable in your workflow.  
>  
> Constraint we won't break: if the document doesn't contain the exact passage, we refuse — no paraphrase.

---

## Log destination

Partner friction → append to `CURSOR-LOG.md` under `## Design partner · <date>`.  
Slice 6 done-when: one real lead + friction list (Oscar owns outreach).
