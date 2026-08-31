# Agent Science websearch — full rundown

**What this is:** how websearch works when the product is **Agent Science** — the truth layer for what people **believe** and **use**. Not Google. Not one citation. Agentic truth.

**Ruling (2026-08-31):** Name = Agent Science. Companion (B) lead. Clearance (A) = another truth on the same layer. Websearch **is** this layer.

---

## 1 · One sentence

You ask something an agent would ask while building. Agent Science returns a **verified primary** (verbatim span or named refuse) **and** the **field context** around it — what people use (GitHub ★), what they write (blogs/docs), what the fleet already asked, and which aliases map here — then **remembers** so the next ask is free.

That whole thing is websearch.

---

## 2 · Why “one answer” is the wrong product

Raw search: ten blue links.  
Most “AI search”: one summarized answer with footnotes.

**Agentic truth** needs more:

| Need | Why |
|------|-----|
| **Believe** | What practitioners and docs claim |
| **Use** | What the field actually installs / runs (★, push, awesome-lists) |
| **Verify** | Span in a fetched document — or refuse |
| **Memory** | Ask once → shelf → free forever |
| **Peers** | What other agents already burned money asking |

One SOURCED row without use/belief context is a citation.  
One star list without verify is a popularity contest.  
**Both together** = Agent Science websearch.

---

## 3 · The full stack (who does what)

```
                    ┌─────────────────────────────────────┐
                    │     AGENT SCIENCE  (truth layer)     │
                    │  believe + use → verify → remember   │
                    └─────────────────────────────────────┘
           ┌───────────────┬───────────────┬───────────────┐
           │               │               │               │
     dictionary      field signals    fleet popular    clearance
     (primary)       (★ + blogs)      (peer asks)      (vertical A)
           │               │               │               │
     free/cheap/live  field-signals   refusal_log      same engine
     science_lookup   .json           queries table    POST /clear
```

| Piece | Job |
|-------|-----|
| **Agent Science** | The name. Truth layer. Websearch. |
| **Agentic truth** | The content class — practices, tools, loops, papers, rights, laws people believe/use while building agents |
| **Grinder** | Sees *your* session; coaches with cited practice |
| **Visibility panel** | The websearch UI for agents — multi-pane, not one answer |
| **Clearance desk** | Same engine on production scripts — A on the layer |

---

## 4 · Cost tiers (how an ask pays)

| Tier | Path | Parallel? |
|------|------|-----------|
| **free** | Exact prior SOURCED · registry hit · alias | No |
| **cheap** | Deterministic URL route (arXiv, CELEX, rights vocab) + fetch + verify | No |
| **live** | Parallel discovery + Gemini locate + verify | Yes |

Always try free → cheap before live. Visibility shows the tier on the primary pane.

---

## 5 · Full visibility panes (the expanded websearch)

Run:

```bash
cd ~/CODE/cleared
python3 -m clearance visibility "QUERY" --full
# MCP: science_visibility  { "query": "QUERY", "full": true }
```

| # | Pane | Signal | Rule |
|---|------|--------|------|
| 1 | **Primary** | Verified verdict | Cite span or refuse with cause |
| 2 | **Aliases** | Other phrasings → canonical | Grow with `aliases.json` |
| 3 | **Field use ★** | GitHub stars / push | Adoption only — never authors SOURCED |
| 4 | **Field blogs/docs** | Practitioner + official + latest | Belief / practice sources |
| 5 | **Agentic practices** | Grinder PRACTICES-CORPUS hits | Named engineer truths |
| 6 | **Peer queries** | Fleet ask history | What’s already expensive |
| 7 | **Parallel probes** | Receipts from live searches | What discovery already tried |
| 8 | **Optimize** | Misses / live spend | What to ingest or alias next |
| 9 | **Shelf stats** | Hit rate, sourced/refused | Health of the dictionary |

**Done = all panes considered**, not pane 1 alone.

---

## 6 · End-to-end agent protocol (full run)

1. **Ask with visibility** — `clearance visibility "…"` or `science_visibility` (full).
2. **Read primary** — SOURCED / UNSOURCED / NOT_CLEARED + cause + tier.
3. **Read use** — which repos are starred for this topic; note ★ ≠ truth.
4. **Read belief** — blogs/docs + agentic practices corpus lines.
5. **Read peers** — if the fleet already refused or paid live, don’t repeat blindly.
6. **If miss and you need it** — one `--live` pass, **or** find a URL and `ingest` (claim+url). Never invent.
7. **Re-visibility** — confirm shelf grew (free tier on re-ask).
8. **Answer the human** — primary citation/refuse **plus** field context (believe + use).

That is the expanded websearch. That is agentic truth through Agent Science.

---

## 7 · What goes into the layer (inputs)

| Input | File / surface |
|-------|----------------|
| Practitioner corpus | `docs/inspiration/PRACTICES-CORPUS.md` |
| Practice claim seeds | `research-inbox/2026-08-31-agentic-practices.md` |
| Latest blogs / docs | `research-inbox/2026-08-31-field-blogs.md` |
| GitHub ★ snapshot | `truth-dictionary/field-signals.json` |
| Aliases | `truth-dictionary/aliases.json` |
| Frozen eval population | `research-corpus/` (do not write) |
| Live ingest trail | `research-inbox/` |
| Refresh stars | `python3 scripts/refresh_field_signals.py` |

---

## 8 · What it is not

| Not | Instead |
|-----|---------|
| Raw browser search | Visibility panel |
| One ChatGPT answer with links | Primary + believe + use panes |
| Citation wall of famous names | Verified spans + adoption signals |
| Clearance-only product | Clearance is vertical A on this layer |
| Stars as proof | Stars as use rank only |

---

## 9 · Commands cheatsheet

```bash
# Full expanded websearch (preferred)
python3 -m clearance visibility "ralph loop" --full

# Fast single verdict (only when you already know you need just that)
python3 -m clearance lookup "ralph loop"

# Live discovery on miss
python3 -m clearance visibility "obscure claim" --live --full

# Grow the shelf
python3 -m clearance ingest --claim "…" --url "https://…"

# What the field asks / costs
python3 -m clearance popular

# Adoption refresh
python3 scripts/refresh_field_signals.py
```

MCP: `science_visibility` · `science_lookup` · `science_ingest` · `science_popular`

Skill: `agent-science-websearch` (project + `~/.claude/skills` + `~/.cursor/skills`)

---

## 10 · Film / judge one-liner

> Agent Science is how agents websearch: the truth layer for what people believe and use — verified or refused, remembered, with the field’s stars and practices in view — not one answer.

---

*Canonical with `VISION-2026-08.md` · `TRUTH-LAYER-SOURCES.md` · `INSPIRATION-PRACTICES-2026-08-31.md`*
