# PRD — Agent Science as a public skill

*2026-08-27. Ideation, not a ship. Grounded in what is in this repo today, Cursor's
current skill/plugin docs, and the two bars that keep getting collapsed: **publishable**
vs **used**.*

Oscar asked: *what is missing here to publish as a public skill and have people use it?*
Those are two different products. This document names both, then the vision that makes
the second one worth building.

Related, not replaced:
- `VISION-2026-08.md` — the spine (websearch companion / registry). This is that spine
  in the shape a stranger actually installs.
- `PRD-2026-08.md` — the paying vertical (Art. 53 / clearance desk). Still true. Not
  the skill's front copy.
- `docs/AUDIT-what-is-missing.md` — the user-shaped hole (we grade homework; we do not
  do the work). Still the design risk of a public skill.
- `research-corpus/2026-08-25-helicon-launch.md` — install friction is the launch.

---

## 1. The answer, first

**A `SKILL.md` is missing. That is the smallest gap, and it is not the one that
matters.**

What is missing *to publish*: a skill package (folder + `SKILL.md` with `name` /
`description`), a public GitHub repo, and — if we want one-click rather than
copy-paste — a Cursor plugin (`.cursor-plugin/plugin.json`) submitted for marketplace
review. MIT is already on disk. None of that exists. Hours of packaging.

What is missing *to have people use it*: a stranger-usable runtime. Today the engine
needs Gemini + Parallel keys, the registry is a local sqlite file that does not sync
even across our own Cloud Run instances, the hosted surface is a documentary paste
box (`POST /clear`), and there is no `/ask`. A skill that tells an agent "cite
verbatim or refuse" without a tool behind it is a prompt. Models already pretend to
cite sources. Nobody installs a prompt that does what the model already fakes.

**The skill is the distribution form of Oscar's spine, not of the clearance-desk
README.** Agents do not paste documentary scripts. They ask "is this true / what does
this RFC actually say / source this claim." That is `ask_registry.py` plus the engine,
pointed at the most-searched things. Article 53 and E&O ride the same `Verdict`. They
are not what a Cursor user types `/` for.

---

## 2. Two bars, not one

| Bar | Meaning | What we have | What's missing |
|---|---|---|---|
| **A. Publishable** | a stranger can install the package | MIT licence, engine, hosted desk, `ask_registry.py` CLI | `SKILL.md`, plugin manifest, **public repo** (still private), marketplace listing, install copy in the README |
| **B. Used** | a stranger invokes it twice | a local registry of ~176 rows and a paste box judges use | zero-config path, an `/ask` that returns one verdict not a gap-report wall, a **shared** registry, a `description` that auto-fires on research questions, a next action on every refusal |

Bar A without Bar B is a listing nobody opens. Bar B without Bar A is what we have:
a real engine only we run.

The Helicon note still applies: every extra step between "I heard of this" and "I saw
a sourced row on *my* question" halves the pool. Clone + venv + two API keys is not
a skill. It is a research repo.

---

## 3. What exists vs what a public skill actually is

Verified 2026-08-27 against the tree and Cursor's public docs, not from memory.

**Live in this repo:**
- The rule: a model may only LOCATE; `Verdict.__post_init__` cannot build GREEN/RED
  without a citation and quoted terms (`clearance/verdict.py`).
- The engine: extract → Parallel → fetch → locate → verbatim verify → independence.
- The registry, under another name: `clearance/refusal_log.py` + `ask_registry.py`
  ("sourced answer or an honest miss").
- A hosted desk: `POST /clear` with `{script, subject}` — a whole script, not a
  question.
- MIT (`LICENSE`). Controls that watch themselves go red.

**Absent, in the shape Cursor will actually load:**

```
.cursor/skills/agent-science/SKILL.md     # does not exist
skills/agent-science/SKILL.md             # does not exist (plugin layout)
.cursor-plugin/plugin.json                # does not exist
mcp.json                                  # does not exist
GET|POST /ask                             # does not exist
```

Cursor discovers skills from `.cursor/skills/`, `.agents/skills/`, user-level
`~/.cursor/skills/`, and (for distribution) plugins. A skill is a folder whose
`SKILL.md` has YAML `name` + `description`; the description is the entire
auto-invocation mechanism — the body loads only on a match
([cursor.com/docs/skills](https://cursor.com/docs/skills)).

A **plugin** is what "public" means inside Cursor: `.cursor-plugin/plugin.json`,
skills + optional MCP, hosted in a **public** Git repo, submitted at
[cursor.com/marketplace/publish](https://cursor.com/marketplace/publish) (review
also routing through [cursor.directory](https://cursor.directory/)). Marketplace
plugins must be open source. Review is manual, on the order of days to two weeks,
not a self-serve flip.

This GitHub repo is **private** (`gh repo view` → `PRIVATE`, 2026-08-27).
`PLAN-30.md` §1.5 still says public-only-at-hackathon-submit. That single fact
blocks Remote-Rule install, marketplace submit, and "paste this GitHub URL."

---

## 4. The trap: shipping a prompt and calling it a skill

Three packages we could slap a `SKILL.md` on. Only one is a product.

### 4.1 Instructions-only skill *(theater)*

A markdown file that says: never invent a citation; quote verbatim; refuse if you
cannot. Portable, zero deps, works in Claude Code / Codex / Cursor via the Agent
Skills standard.

**Nobody keeps it.** The host model already produces citations. Without the
verifier, the skill cannot tell a real quote from a fluent fake — which is the
only reason this repo exists. `docs/FINDING-substring-is-not-a-statement.md` is
the exhibit: verbatim and on-topic can still fail to *state the claim*. An
instruction cannot enforce `Verdict.__post_init__`.

Use: internal custom mode for *us*. Not a public product.

### 4.2 Skill wrapping this CLI *(researchers only)*

`python3 agent_science.py <script>` / `python3 ask_registry.py "<q>"`. Honest.
Requires clone, Python, Gemini key, Parallel key, and a local sqlite that starts
empty. Matches the Helicon "every step halves the pool" failure. Fine as a
power-user path; not the front door.

### 4.3 Plugin + MCP against a hosted `/ask` *(the unit people use)*

One-click install. The agent gets tools, not advice:

| Tool | Does | Keys needed by the user |
|---|---|---|
| `ask` | hit the **shared** registry; return SOURCED + quote + URL, or NOT CLEARED YET | none (read) |
| `verify_passage` | structural check: is this quote verbatim in this fetched URL, and does it carry the claim's terms? | none if we fetch; or user-supplied URL |
| `clear_claim` | full engine on one claim (search → locate → verify → independence → write the log) | us, or a user token |

The skill's job is **when to call which tool, and how to print a verdict an agent
can act on.** The MCP's job is the constructor. Split them and the skill stays
thin (progressive disclosure); merge them and we ship a 2,000-line `SKILL.md`
nobody loads.

This is also the Agent Plugins shape (`plugin.json` + `skills/` + `mcp.json`) so
the same package loads in anything that implements the standard, not only Cursor.

---

## 5. Full vision — three nouns, one `Verdict`

Oscar's line, restated as a system rather than a slogan:

> Agent Science is the source-of-truth companion for search: a growing registry
> of the most-asked checkable claims, each one sourced verbatim from a real
> document or refused with a reason. Compliance desks and clearance desks are
> the same object pointed at different nouns.

```
                         REGISTRY  (the Big thing)
              most-asked claims, sourced or proven-unprovable
              independence-classified, append-only
                             ▲
              every ask writes; every hit is free
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   AGENT SKILL          HOSTED DESK          PAYING VERTICALS
   daily, in Cursor     human paste          A1 Art. 53 dossier
   /ask /verify         /clear scripts       E&O pack
   plugin + MCP         compounding UI       asset × instrument
        │                    │                    │
        └────────────────────┴────────────────────┘
                             │
                      the same engine
                   locate ≠ assert
                   refuse, don't score
```

**This is not a pivot.** `VISION-2026-08.md` already said the companion is the
product and A1 is a customer. The skill is simply the companion's install path.
The clearance desk is the companion pointed at a script. The Art. 53 annex is
the companion pointed at a training-data inventory. One constructor, three
doors.

### 5.1 Why the skill has to be the front door (for *use*)

- Skills auto-invoke on `description` match. A compliance filing is twice a
  year; "what does this RFC say" is every session. Auto-invoke only fires on
  the daily noun.
- Agents already search. They currently emit fluent citations. The skill is
  the intercept: before you assert a checkable claim, `ask`; on a miss,
  `clear_claim` or print NOT CLEARED YET. That intercept *is* the product
  moment, the way A→B compounding is the product moment on the Desk.
- Every intercept is an ingest. The fleet's `research-corpus/` was "every
  websearch becomes a claim." Public skill traffic is that loop with other
  people's searches. That is how the registry becomes "the most-searched
  things" instead of our 176 rows.

### 5.2 Why the registry has to be shared (for the moat)

A per-user sqlite is a cache. A shared log is a network. Today
`refusal_log.py` is not even GCS-synced across *our* Cloud Run instances
(`PRD-2026-08.md` §7). Until a second stranger's `ask` can hit a row the
first stranger cleared, we are not the company in the vision — we are a
verifier-as-a-service with linear cost.

The refusal half is the half no fact-check marketplace accumulates
(`docs/MARKET-validated.md`: ClaimReview records published verdicts, not
"we searched and nothing admissible states this"). A public skill that only
writes GREENs is leaving the asset on the table.

### 5.3 Why refuse-not-score stays the wedge

If the skill downweights, it is Perplexity with extra steps. If it refuses,
an agent can choose: stop, ask the user, or escalate. Those are different
acts. The AUDIT (`docs/AUDIT-what-is-missing.md`) still holds: a refusal
without a next action is a complaint, and a wall of them trains the agent
to ignore the skill. So the public skill must print **task, not grade**:

- SOURCED → quote, URL, independence class. Agent may assert, with that
  citation only.
- NOT CLEARED YET → "do not assert this; here is what would resolve it"
  (primary-source query, rightsholder, paywall, wording bug).
- DISPUTED → both quotes. Agent must present the conflict, not pick.

Same discipline as the Desk. Different screen.

### 5.4 The end-state (ceiling, not this quarter)

- The registry is a browsable public good for *read* (most-asked sourced
  claims) and a metered *write* (clearing a new claim costs search).
- Cursor / Claude Code / Codex install the same plugin.
- Paying verticals buy the dossier and the tenant shelf, not the ask box.
- Cross-customer compounding on *public* facts (dates of directives, RFC
  SHALL lines, "React 19 does X according to the docs") — never on a
  studio's unpublished script. Isolation is the product for private
  shelves; the network effect is the public layer.

If a screenshot of the skill could be a Perplexity citation chip, we failed.
The tell is the UNSOURCED row with a named cause.

---

## 6. What "used" requires, in order of leverage

Not a calendar. The dependency order.

### Slice 0 — pick the noun (copy, not code)

Public-facing `description` must match how agents talk, or auto-invoke never
fires:

> Use when the user or the agent is about to assert a checkable claim, cite a
> source, answer "is this true", or quote a spec/RFC/docs page. Returns a
> verbatim sourced answer or an honest refusal. Never invent a citation.

Not: "clear a documentary script for E&O." That description will sit idle in
a coding IDE.

Decision: **the skill speaks VISION. The README can still lead with the
desk for the hackathon judge.** Two doors, one engine. Do not make the
judge's paste box the skill's when-to-use.

### Slice 1 — registry-read skill (the only honest v0)

Ship a skill + script that queries a **hosted, public-read** registry.
No user keys. Misses print NOT CLEARED YET. Hits print quote + URL.

This is `ask_registry.py` with a URL in front of it instead of
`cache/refusal_log.db`. It is useful the first time a popular claim is in
the log ("EU AI Act Art. 53 penalty", "Directive 2012/28/EU adopted
2012-10-25"). It is a stub the rest of the time. **Ship it anyway**: it
teaches the invocation shape, and it does not lie. An honest miss is the
brand.

Blockers: GCS-share the log (already the open gap in the PRD); add
`GET /ask?q=`; make the Cloud Run URL a product API, not a hackathon
exhibit; **public repo** or a second public `agent-science-skill` repo
that only contains the package (engine stays private until submit — a
workaround, not a strategy).

### Slice 2 — `verify_passage` without search

Given `{claim, url, quote}`, run `clearance/verify.py` (verbatim, terms,
statement-ness). This is the structural heart, it needs no Parallel key,
and it is the thing instructions-only cannot do. Agent flow: model
proposes a citation → skill verifies → GREEN or refuse.

This is the dogfood for `verify_corpus`. It is also the cheapest public
tool: one fetch, no search spend.

### Slice 3 — plugin + MCP (the install)

```
agent-science-plugin/
  plugin.json                  # Agent Plugins standard (portable)
  .cursor-plugin/plugin.json   # Cursor extras if needed
  skills/agent-science/SKILL.md
  mcp.json                     # remote MCP → hosted /ask, /verify, /clear_claim
  assets/logo.svg
  README.md                    # one-liner install, one example miss, one example hit
```

Submit marketplace. Also: GitHub Remote Rule, `awesome-claude-skills` /
equivalent Cursor lists. The README's first command must produce a
verdict on the *stranger's* question, not on `fixtures/scripts/…`.

`variables` in the Cursor manifest are how a later paid token is
configured (`API_TOKEN`); v0 should not require one.

### Slice 4 — `clear_claim` (the write path)

On a registry miss, optionally run the full engine and append the log.
This is where money and abuse live. Do not turn this on for anonymous
public until there is a cap. Options: we eat a small Parallel budget per
day as launch fuel; or the user brings a Parallel key via plugin
`variables`; or misses stay misses until a design partner pays.

**Launch with Slice 1+2.** Add 4 when we can measure abuse. A public
clear-anything endpoint with our keys is a search bill with a skill
attached.

### Slice 5 — the work list, not the wall

Port the AUDIT's resolution queue into the skill's output schema so
UNSOURCED is a task. Without this, first-week usage dies the same way
powered-leg-A died: 0 cleared, seven "you figure it out."

### Slice 6 — verticals on the same tools

`clear_script` / dossier / Art. 53 annex remain the Desk and the paid
API. The skill may *link* ("this looks like a production script — run
the desk") but must not *be* the desk. Different buyer, different cadence.

---

## 7. Draft skill (spec only — do not install yet)

Not in `.cursor/skills/` until Slice 1 has a URL. Installing an
instructions-only skill in this repo would auto-invoke on research
questions and then fail without tools — training *us* to ignore it.

```markdown
---
name: agent-science
description: >
  Source-of-truth companion for checkable claims. Use when asserting a fact,
  citing a source, answering "is this true", quoting a spec/RFC/docs page,
  or clearing a claim in a script/report. Returns SOURCED (verbatim quote +
  URL) or an honest refusal with the reason. Never invent a citation.
disable-model-invocation: false
---

# Agent Science

A model may only LOCATE evidence. It may never ASSERT it.

## When to use

- The user asks whether something is true, current, or in a spec.
- You are about to emit a citation, statistic, date, or "the docs say."
- A script/report/PRD claim needs a source or an explicit UNSOURCED.

## When not to use

- Taste, design, or code-change questions with no external fact.
- Private/unpublished material the public registry must not ingest.
- Legal conclusions. Verdicts are evidence records, not advice.

## Tools (once MCP is wired)

1. `ask(query)` — registry first. If SOURCED, assert only the quoted span.
2. `verify_passage(claim, url, quote)` — if the agent already has a candidate.
3. `clear_claim(claim)` — only on a miss, and only if the write path is enabled.
4. If all miss: print NOT CLEARED YET + cause + next action. Do not round up.

## Output shape (always)

- verdict: SOURCED | UNSOURCED | DISPUTED | NOT CLEARED YET
- quote: verbatim span or empty
- url: fetched document or empty
- independence: primary | derived | unclassified | n/a
- cause: the engine's cause string, not a paraphrase
- next: one action, or "none — you may assert this"

## Hard rules

- No GREEN without quote + url. If a tool cannot return both, it is not SOURCED.
- Unclassified is never promoted to primary.
- Do not summarise a refusal into a hedged yes.
```

Plugin `description` (marketplace card): *Sourced verbatim or refused. A
registry of already-cleared claims your agent can ask before it invents a
citation.*

---

## 8. Honest risks (do not round these up)

- **Wrong refusal is still open** (`docs/FINDING-refusal-correctness.md`).
  A public skill that refuses a true claim trains users to uninstall. Slice 2
  (`verify_passage`) should ship with the held-out refuse-everything *and*
  the held-out supported set, same as `test_watch_it_go_red.py`.
- **Substring ≠ statement** and **circular sourcing** remain unsolved. Public
  copy must not claim we catch either. The skill should surface those FINDING
  classes when they apply, not hide them.
- **Marketplace is curated and slow.** Treat directory listing + GitHub URL
  as the real v0 distribution; marketplace as amplification.
- **Hackathon vs public repo.** `PLAN-30` 1.5 vs this PRD: if Sep 9 still
  wants private-until-submit, put the *skill package* in a tiny public repo
  that talks to the hosted API, and keep the engine private. Two repos is
  ugly; one private repo means zero public installs. Pick.
- **Cost and abuse.** Anonymous `clear_claim` is a bill. Registry-read and
  `verify_passage` are the only tools that can be free.
- **Privacy.** A shared registry of "most-searched things" will contain
  whatever agents ask. Need a public/private split on day one: public facts
  compound; user scripts stay on a tenant shelf or local. Do not wait for
  the first leaked screenplay.
- **Not legal advice / not insurance.** The Desk's buyer is a lawyer. The
  skill's user is an agent. Same verdict, different liability sentence in
  the README.
- **Design hole, unchanged.** If v0 prints a gap-report wall, we repeat
  powered-leg-A for a larger audience. Output schema in §7 is load-bearing.

---

## 9. Decision (Oscar)

Three ships. Only one is the vision.

| | What we publish | What a stranger gets | Verdict |
|---|---|---|---|
| **A. Prompt skill** | `SKILL.md` in a public gist/repo | better instructions, same hallucinations | Do not. It spends the name. |
| **B. CLI skill** | this repo, public, with a skill that shells out to `ask_registry.py` | works for us and for people who already have keys | Power-user path. Not the launch. |
| **C. Registry-read plugin** | public package + `GET /ask` + `verify_passage` | instant hit or honest miss, no keys | **The v0.** Matches the spine. |
| **D. Full companion** | C + metered `clear_claim` + shared log + work-list output | the intercept + the moat | The product. After C is used, not before. |

Recommend **C this week in packaging terms, D as the ceiling.** Do not
submit marketplace until `GET /ask` returns a real row for at least the
back-filled corpus terms (Art. 53, Directive 2012/28/EU, the FINDING
claims) — otherwise the first reviewer types a question, gets an empty
registry, and files us under "unfinished."

The engine is not the blocker. The public object is.

---

## 10. What would change in the existing PRDs

- `VISION-2026-08.md` § "What changes in the build" item 1 ("registry
  becomes the front surface") — **the skill/plugin *is* that surface** for
  agent users; the Desk remains the surface for humans with a script.
- `PRD-2026-08.md` build plan item 2 (dossier a lawyer signs) stays the
  paid artifact. It is not the skill's artifact. The skill's artifact is
  one verdict row.
- `BUILD-PLAN-STARTUP.md` H1 "API + webhooks / Agent Builder as a client"
  — add "MCP + marketplace plugin" as a first-class client, same API.
- `NEXT-STEPS.md` head-of-queue is still independence workbench / async /
  dossier. This PRD does not jump that queue for the *company*. It names
  the *distribution wedge* that the vision already asked for. Packaging
  late remains correct for Sep 9; **if the question is "public skill,"
  packaging *is* the work**, and the missing piece underneath it is
  `GET /ask` + a shared log.

---

*External claims about Cursor's skill/plugin mechanics are captured in
`research-corpus/2026-08-27-prd-public-skill.md` so this PRD can be cleared
by the same engine.*
