# DESIGN PARTNER LOOP — friction template · slice 6 prep

**Audience:** Oscar sends to one real clearance / research lead.  
**Goal:** one production runs a real question or script through the desk; friction list lands in `CURSOR-LOG.md`.

**Hosted reality (2026-09-18):** Cloud Run is **private-workspaces**. Unauthenticated paste-to-`/clear` is gone. Partners sign in with a workspace access key Oscar issues.

**Public without a key (after Oscar deploys this branch):** `/health`, `/partners`, `/truths/ui`, `/visibility/ui`, `/popular/ui`. Live revision `00028-hed` still strips health and 303s film surfaces — do not promise those URLs until `deploy.sh` + `bash film/preflight.sh` exit 0.

---

## Script / investigation flow (what the partner does)

### A · Workspace research desk (hosted default)

1. Open hosted URL: `https://agent-science-568004190078.us-central1.run.app/`
2. **Sign in** with the access key Oscar sent (not a password; never paste the key into a URL).
3. Create or open a case for their question / script claim.
4. Inspect sources (exact quotes) before accepting any SOURCED-looking row.
5. Record a decision with rationale citing evidence IDs they actually opened.
6. **Return visit:** open the same case — note whether evidence review flags fired.

### B · Local clearance desk (compound Parallel demo)

For the classic paste-script → gap report (ADK + Parallel), partner runs locally or Oscar demos on a non-hosted desk:

```bash
git clone https://github.com/Morkeeth/agent-science.git && cd agent-science
pip install -r requirements.txt
# Oscar provides PARALLEL_API_KEY out of band — never commit it
export AGENT_BUILDER=1 GCP_PROJECT=hack-fleet PARALLEL_API_KEY='…'
python3 cloud/service.py   # local desk :8080 (or PORT=)
curl -s -X POST localhost:8080/clear \
  -H 'Content-Type: application/json' \
  -d '{"script":"<paste>","subject":"<their-tag>"}'
```

Second script on the **same subject** should show `corpus_hits ≥ 1` and fewer Parallel calls.

### C · One-command stranger smoke (no keys)

```bash
pip install -r requirements.txt   # google-adk + parallel-web — prove refuses mocks
bash scripts/new_user_trial.sh
bash scripts/prove_partner_health_local.sh
bash scripts/prove_judge_surfaces_local.sh
python3 scripts/prove_adk_clear_path.py
python3 scripts/eval_hosted_partner_baseline.py   # expect exit 2 until Oscar deploy
```

**Friction measured 2026-09-19 (agent night, no partner session yet):**
- Live `/health` still stripped → partner verify + film preflight fail at object
- Previous local prove patched ADK → false green without `pip install -r requirements.txt`
- Hosted `/clear` needs `WORKSPACE_TOKEN` — honesty exhibit exits 2 BLOCKED without it
- Soft compound (flat Parallel + corpus_hits) must not be filmed as STRICT_DROP
---

## Friction checklist (partner fills in)

| # | Question | Partner answer | Our action |
|---|----------|----------------|------------|
| 1 | How long from first click to a usable answer? | | |
| 2 | Was **login / access key** confusing? | | |
| 3 | Any claim wrongly treated as supported? (paste claim/evidence id) | | |
| 4 | Any refusal reason that was not actionable? | | |
| 5 | Did they open the **source snapshot** before trusting a quote? | | |
| 6 | On a return visit, was review/stale state understandable? | | |
| 7 | Local `/clear` compounding (if tried) — Parallel drop visible? | | |
| 8 | Output format — HTML desk vs JSON/MCP for their pipeline? | | |
| 10 | Did they run `pip install -r requirements.txt` before local prove? | | |
| 11 | Did hosted `/health` show `engine_default: adk` (post-deploy)? | | |

---

## What we measure from the session

- Time-to-first useful answer (wall clock)
- Whether they opened source text before deciding
- Hosted: case version + decision supersede count
- Local clear (if used): `parallel_calls` run 1 vs run 2, `corpus_hits` on run 2
- Count of named refusals by cause

---

## Oscar → partner email (draft)

> Subject: 15-minute Agent Science trial  
>  
> We built a desk that returns checkable claims as **verbatim quote + URL** or **UNSOURCED with a named reason** — and remembers what was already proved so the second ask is cheaper.  
>  
> **Try it:** [hosted URL] — sign in with the access key in this email (do not forward). Open one real question from your week, read the source passages, and tell us what felt wrong.  
>  
> Optional compound demo: we can hop on a call and run two scripts on the same subject so you see Parallel calls drop.  
>  
> **Reply with:** anything that looked falsely supported, refusal reasons that were useless, and the one blocker that would stop a second visit.  
>  
> Constraint we will not break: if the document does not contain the exact passage, we refuse — no paraphrase.

---

## Log destination

Partner friction → append to `CURSOR-LOG.md` under `## Design partner · <date>`.  
Slice 6 done-when: one real lead + friction list (Oscar owns outreach).
