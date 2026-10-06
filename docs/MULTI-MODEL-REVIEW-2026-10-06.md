# Multi-model review — Agent Science (`origin/main` @ d56aeb8)

*2026-10-06. Four independent reviews of the shipping tree, then a synthesis.
Object: `github.com/Morkeeth/agent-science` at `d56aeb8` (2026-09-16). Not the
stale Aug 28 docs branch `cursor/public-skill-prd-c838`.*

Reviewers (Cursor Task subagents, isolated, no shared notes):

| Lens | Model | Agent |
|---|---|---|
| Honesty / constructor / tests | Claude Opus 4.5 | [Opus honesty review](bc-a1488b4d-5b19-55fb-8305-0ad54e17650d) |
| Engineering / tenancy / MCP | GPT-5.6 Terra | [GPT engineering review](bc-d1563cac-24fc-5605-a70a-c5d22ae2d57e) |
| Product / identity / buyer | Grok 4.7 | [Grok product-strategy review](bc-1f7ad7f2-0d98-5fff-9c31-ecfb7857a5a4) |
| Ship / first-run / UX | Gemini 3.8 Flash | [Gemini ship-readiness review](bc-ad1556a8-bd75-5023-b18d-cda7d917c233) |

This file is the synthesis. Disagreements are labelled. Spot-checks against
`clearance/cases.py`, `clearance/mcp_server.py`, and `cloud/service.py` are
noted where a claim was re-read at the object.

---

## Consensus verdict

**The clearance constructor is still honest. The product the README now leads
with is not that constructor.** Four models, four lenses, one shape:

Main as of mid-September is a **local CLI/MCP research ledger** (cases,
versioned snapshots, authored decisions, `REVIEW_REQUIRED` when a source
hash moves) plus a **token-gated hosted inspector**. The tests that watch
themselves go red still defend `Verdict.__post_init__`. The path a stranger
is told to run — `agent-science research …` / `case create` — labels a
sentence `QUOTE_VERIFIED` when it shares four-letter words with the question
(`clearance/cases.py` `_quote`, lines 119–128). The hosted Cloud Run process
(`K_SERVICE` set) hands **every** request to `WorkspaceHTTP`, so judge URLs
in `SUBMISSION.md` (`/visibility/ui`, `/clear`) 404 on the live service.

Agentic Cinema ended 9 Sep 2026. The last product commits still restore
partner fields on `/health` for a judge. `HANDOFF-2026-09-05.md` says
scientific quality versus baseline is **still unmeasured**. No named buyer
has been contacted (`SUBMISSION.md`).

This is not one company with three doors. It is three products in one repo
that were never reconciled after the deadline.

---

## What this is (identity audit — unanimous)

| Surface | What it says the product is |
|---|---|
| `README.md` | CLI/MCP research companion for coding work |
| `AGENTS.md` | Terminal/agent is the front door; dashboard optional |
| `.cursor/skills/agent-science-websearch` | “Use for any research”; `science_visibility` |
| `hack.md` / `CLAUDE.md` / `docs/STATUS.md` | Truth layer; clearance as vertical; film still open |
| `PITCH.md` | Paste a documentary script; E&O / studios |
| Hosted (`K_SERVICE`) | Private workspace desk (“Keep the evidence. See what changes.”) |
| Local `cloud/service.py` without `K_SERVICE` | Clearance paste box + `/registry` + `/visibility/ui` |

Grok: four front doors. Gemini: 79 files under `docs/` plus root status
markdown; a newcomer hits two eras in ten minutes. Opus: `bench_check_docs`
128/128 grades 11 **legacy** suites and none of the research/case suites.

**Correction:** Gemini listed `BUILD-NOW.md` among main’s root files. That
file exists only on `cursor/public-skill-prd-c838` (this conversation’s
earlier PR). It is **not** on `main`. The sprawl finding still holds.

---

## Strengths (all four, with overlap)

1. **`Verdict` still cannot emit GREEN/RED/DISPUTED without URL + quote**
   (`clearance/verdict.py`). Opus constructed objects; the guard holds.
   `test_watch_it_go_red` 72/72. README states the refusal-eval result
   fairly: 6/6 vs substring baseline 5/6, McNemar p=1.0, “does not
   establish broad superiority.”
2. **Hosted private workspaces are real engineering** (GPT, spot-checked).
   Auth before workspace access, signed cookies, CSRF/origin, per-tenant
   GCS with generation preconditions, spend reservations
   (`cloud/case_auth.py`, `case_storage.py`, `case_budget.py`).
   `clearance/safe_fetch.py`: DNS pinning, TLS hostname, byte/time limits.
3. **The research CLI does not overclaim a finished investigation.**
   `research start` returns `awaiting_reasoning` / `Completed steps: 0`
   (Opus measured; Gemini hit the same wall as a stranger).
   README: a verified quote proves those words exist; it does not prove
   support. That sentence is true — and then `_quote` still stamps
   `QUOTE_VERIFIED` on word overlap.
4. **Repo context hashes files; contents are not sent to search**
   (`cases.py` around the `_quote` block).
5. **The tree retracts its own claims in writing** (offline-compound
   finding, prior-loss section of `hack.md`, README p-value). That
   discipline is the culture. It did not travel onto the case path.

---

## Critical defects (ranked). Consensus unless noted.

### 1. `QUOTE_VERIFIED` is overlap, not verification — *measured*

`clearance/cases.py` `_quote`: if the Parallel excerpt is not already a
short substring of the fetched text, rank sentences by shared
`[a-zA-Z]{4,}` tokens with the **question**, minus a tiny stoplist.
Opus: a question about agent sessions returned *“Our cookie policy
explains how sessions are stored.”* `assert quote in snapshot['text']`
(line 178) cannot fail — it asserts a slice of the same string.
The shipping locator / polarity guard / `Verdict` constructor are **not
on this path**.

This is the FINDING-substring class, rebuilt as the default product.

**All four models hit this or its UX twin.** Opus named the mechanism.
Gemini saw empty/offline cases with “0 verified quotes” and a live
`RuntimeError` instead of a key-missing message. Grok: refuse-not-score
is a constitution line, not the wedge; the research path makes the
human author the assessment.

### 2. Hosted URL is a different product than the docs send people to — *measured*

`cloud/service.py` `main()` / `do_GET`: if `K_SERVICE` or
`AGENT_SCIENCE_HOSTED`, **all** requests go to `WorkspaceHTTP`.
`/clear`, `/visibility/ui`, `/truths/ui` exist only on the local
compounding-desk handler. Opus: live revision `00028-hed` serves
`1c4b487` on `release/2026-09-07-reviewed-public-snapshot`, not an
ancestor of current main. `568004190078` 303s to `33kamss2jq`.

`SUBMISSION.md` still points a judge at `/visibility/ui?q=ralph+loop…`.

### 3. MCP spend policy is a seam that is not the service — *code read*

README: live calls need an approved aggregate policy. `science_research`
requires it. `science_search` **defaults `live: true`**
(`mcp_server.py` tool schema + `handle_tool` line 337:
`live = arguments.get("live", name == "science_search")`).
GPT + Opus: `science_case` create with `live: true` made discovery
calls with no policy. An agent with MCP access can spend Parallel
without the gate the README advertises.

GPT: hosted budget reservations are real; MCP is stdio and local, so
the threat is “trusted host, unbounded tools,” not a public API. Still
a broken contract.

### 4. Partner `/health` grades values the test set — *code + test read*

Opus: `partners.py` reports `parallel` from env-var presence, hardcodes
`parallel_search_at_runtime: True`, `vertex:adc` whenever `K_SERVICE`
is set. Tests inject a fake key and patch `adk_available=True`. The
hosted worker does not import Gemini/ADK; `engine_default: adk` names
a `/clear` route the hosted process does not serve. Latest commit
restores those fields so a verify script can see them.

### 5. Compounding exhibit was greened by copying run A’s strings — *git measured*

`d56aeb8` / `docs/FINDING-offline-compound-exact-assertion-2026-09-16.md`:
paraphrased B still spends search. After the fix, B uses A’s exact
assertions. The “most-searched gets cheaper” pitch is an exact-string
cache, which the repo already knew.

### 6. A stranger cannot finish one task — *Gemini, exercised*

Install CLI: works. `research "…"`: `awaiting_reasoning`. Resume:
same, unless you hand-build a proposal JSON. `case create --live`
without keys: bare `RuntimeError`. Offline review: no cases. No
bundled demo case. Design is still the C-grade axis, now as a terminal
dead-end instead of a paste-box wall.

### 7. Docs and eval gate cover the wrong product

`hack.md` still SHIP for a past deadline. Film/Devpost checklists
assign Oscar work for an event that is over. Refusal eval (n=6) is
the **legacy** clearance path; RC5 was the guard’s development target
in the same commit that edited `set.json` (Opus). Handoff: 54 unknown
judgments on saved research answers are missing evidence, not 54 bugs;
quality vs baseline unmeasured.

---

## Dissent (do not round up)

| Topic | Split |
|---|---|
| **How good is hosted tenancy?** | GPT: credible isolation + CAS + CSRF. Opus: partner health is theater; hosted `/health` stripped body is more honest. Both can be true: workspace auth is real, partner manifest is not. |
| **Is MCP a real surface?** | GPT: yes, stdio JSON-RPC, many tools. Grok: the installable skill teaches the *dead* noun (websearch ritual). |
| **Would a Cursor user keep it?** | Grok: no, unprompted. Gemini: they would keep `case import` + quote lock **if** they ever saw a finished case. Opus: research CLI honesty is a strength that currently looks like a blank screen. |
| **Next move** | See below. Four different one-moves, not a committee wishlist. |
| **BUILD-NOW.md on main** | Gemini error. Ignore. |

---

## What we would not do next

- Merge `cursor/public-skill-prd-c838` as the plan. It is ~100 commits
  behind; it tells you to build `GET /ask` while main already has
  `/search` + `/registry` on the **local** desk and a different hosted
  app. The skill-without-runtime warning in that PRD is still right.
- Ship a new `SKILL.md` that wraps `science_search`. Same trap: a
  prompt in front of overlap-verified quotes.
- Marketplace submit, public-skill packaging, or a second GitHub repo.
- Another night wave restoring `/health` fields for a judge who left.
- Thin the constructor to make `_quote` look better.

---

## One next move (synthesis)

The four one-moves were:

1. **Opus** — freeze a refusal eval for `(question, page)` pairs on
   `_quote`, including negatives that share a word and do not address
   the question; watch current main fail; only then route through the
   shipping locator/guard.
2. **GPT** — one spend reservation for every live MCP tool.
3. **Grok** — replace `agent-science-websearch` with “reopen the
   decision whose source changed”; pass/fail is a second session by
   someone who does not have `AGENTS.md` open. Else take the gap
   report to **one named clearance person** (the call `SUBMISSION.md`
   admits was never made).
4. **Gemini** — `agent-science demo`: bundled offline case, version
   1→2 diff, decision brief, no keys, <30s.

**Do Opus’s eval first.** It is the only move that is a control, not a
surface. This repo’s own law: a rule in a file gets bypassed; a rule
in a test gets caught. Until `_quote` can go red on a cookie-policy
sentence, README “research companion” is a second product wearing the
constructor’s reputation.

Immediately after (same week, not a roadmap): Gemini’s offline `demo`
so a stranger can finish one task, and stop sending humans to hosted
`/visibility/ui`. Grok’s buyer call and GPT’s MCP budget are real;
they are not the hole that makes the README false.

If the eval is declined, say in the README that case quotes are
**overlap excerpts, not Verdicts**. That sentence already almost
exists. Make it bind.

---

## Scope of this review

Reviewed `origin/main` @ `d56aeb8`. Did not merge to production, did
not change engine code. Four subagent transcripts are the primary
evidence; synthesis re-read `_quote`, MCP `science_search` default,
and `K_SERVICE` dispatch at the object.
