# Agentic engineering practices → Agent Science dictionary

**Origin:** `~/CODE/aistrava/docs/PRACTICES-CORPUS.md` (Agent Grinder coach corpus)  
**Imported:** 2026-08-31 · **Why:** re-center Agent Science on developer / agentic truths — the companion vision — not only EU clearance demos.

Grinder already did the hard part: named practitioners, named practices, named URLs. Agent Science’s job is the other half — **verify the claim against the document, remember SOURCED and REFUSED, serve free on re-ask.**

## Practitioners (inspiration set)

| Who | Why they matter here |
|-----|----------------------|
| Andrej Karpathy | Rules files, 80/20 agent/human, one task per session |
| Simon Willison | Explore → plan → code → commit; define “done” |
| Geoffrey Huntley | Ralph loop — one unit, commit, exit |
| Thorsten Ball | LLM + loop + enough tokens; make the check real |
| Addy Osmani | Self-improving rules/memory |
| Anthropic Engineering | Context as the resource; plan + CLAUDE.md + TDD |
| Mitchell Hashimoto | Always an agent running; spec.md first; oracle subagent |
| CodeScene | More rigor for agentic coding, not less |
| arXiv 2512.14012 / 2509.06216 | “Don’t vibe, control” + agentic SE pillars |

## Through-line (what the dictionary should carry)

1. Verification loop is the craft  
2. Rules/context files matter  
3. Commit per unit of work  
4. Scope tightly; define done  
5. Control, not vibe  
6. Context is the scarce resource  
7. Plan first; save the spec  

## Seed files in this repo

| Path | Role |
|------|------|
| `docs/inspiration/PRACTICES-CORPUS.md` | Mirror of Grinder corpus (cited) |
| `research-inbox/2026-08-31-agentic-practices.md` | `[CLAIM]`/`[URL]` pairs for ingest |
| `truth-dictionary/aliases.json` | Casual → canonical for these lookups |
| `fixtures/scripts/demo-agentic-practices.txt` | Short narration for scout / video |

## How to grow the shelf

```bash
# Verify + record each claim against its named URL (no Parallel discovery)
python3 -m clearance ingest --file research-inbox/2026-08-31-agentic-practices.md

# Or one claim:
python3 -m clearance ingest --claim "…" --url "https://…"

# Then fleet asks free:
python3 -m clearance lookup "ralph loop"
python3 -m clearance lookup "context engineering agents"
```

**Discipline (shared with Grinder):** search snippets are a lead. Figures (41%→11%, 80% prompt cut) must survive `verify` on the primary page or stay UNSOURCED with cause — that refusal is still a dictionary row.

## Split that matches the vision

| Layer | Owns |
|-------|------|
| **Grinder** | Detect session characteristics; coach with cited practice |
| **Agent Science** | **Scientific coach with facts** — prove the practice (or any claim) against the source; registry of most-asked truths; clearance/E&O as one shelf of those truths |

Same inspiration. Different job. Together: coach the work, ground it in documents.
