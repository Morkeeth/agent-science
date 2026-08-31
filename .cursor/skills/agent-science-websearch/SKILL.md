---
name: agent-science-websearch
description: >-
  FULL Agent Science websearch — agentic truth layer for what people believe and use.
  Not one answer. Use for any research, websearch, scout, agentic practice, tool,
  star, blog, RFC, or factual ask. Prefer `clearance visibility --full` /
  science_visibility over raw browser search or science_lookup alone.
---

# Agent Science websearch — full agentic truth

**Product:** Agent Science = truth layer for believe + use.  
**Websearch:** the full visibility rundown — not one citation.  
**Doc:** `~/CODE/cleared/docs/WEBSEARCH-FULL-RUNDOWN.md`

## Steps (complete protocol)

1. **Run full visibility**
   ```bash
   cd ~/CODE/cleared
   python3 -m clearance visibility "QUERY" --full
   # MCP: science_visibility { "query": "QUERY", "full": true }
   ```
   **Done when:** panes 1–10 printed (or empty panes explicitly shown).

2. **Synthesize all panes before answering the human**
   | # | Pane | Use for |
   |---|------|---------|
   | 1 | Primary | The only *verdict* — cite span or refuse |
   | 2 | Aliases | Other phrasings |
   | 3 | GitHub ★ | What the field **uses** (not proof) |
   | 4 | Blogs/docs | What the field **believes** / documents |
   | 5 | Agentic practices | Grinder corpus — named engineer truths |
   | 6 | Peer queries | Fleet already paid / refused |
   | 7–8 | Probes / optimize | Don’t repeat blind live spend |
   | 9–10 | Shelf stats / shape | Dictionary health |
   **Done when:** reply includes primary **and** believe+use context.

3. **Miss path** — if primary is NOT_CLEARED / weak refuse and the ask matters:
   - one `--live` visibility, **or**
   - find URL → `python3 -m clearance ingest --claim "…" --url "…"`, then visibility again.  
   Never invent a citation.  
   **Done when:** re-ask is free-tier or honest refuse with cause.

4. **Stale stars** — `python3 scripts/refresh_field_signals.py` when adoption looks old.  
   **Done when:** `field-signals.json` `read_at` is today.

5. **Personal shelf** — visibility indexes `~/.agent-science/truth.db` by default.
   ```bash
   python3 -m clearance truth stats
   python3 -m clearance truth fetch-field
   python3 -m clearance truth skill <name> helped|hurt|baseline --probe <probe>
   ```
   **Done when:** stats show asks growing; Magnet skill rows appear when skills are rated.

## Hard rules

- Full visibility over raw web search and over single `lookup`.
- Stars = adoption only. Never author SOURCED.
- Refuse with cause beats paraphrase.
- Clearance / EU / E&O use the **same** panel — vertical on this layer, not a different product.

## Cheatsheet

```bash
python3 -m clearance visibility "ralph loop" --full
python3 -m clearance visibility "context engineering" --full --live
python3 -m clearance popular
python3 scripts/refresh_field_signals.py
```
