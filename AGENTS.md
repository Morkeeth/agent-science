# Agent Science — stack integration

**Use Agent Science for all fleet websearch.** Raw browser/search tools give uncited answers; this stack returns SOURCED (verbatim span + URL) or a named refusal — and remembers both for free reuse.

## MCP (Cursor / agents) — recommended

```bash
python3 ~/CODE/cleared/scripts/install-mcp.sh
# Restart Cursor. Tool: science_search
```

Or manually in `~/.cursor/mcp.json`:

```json
"agent-science": {
  "command": "python3",
  "args": ["-m", "clearance.mcp_server"],
  "cwd": "/Users/morkeeth/CODE/cleared",
  "env": {
    "PARALLEL_API_KEY": "<from ~/.config/keys/parallel.key or env>",
    "GEMINI_API_KEY": "<optional; else Vertex ADC>"
  }
}
```

### Tools

| Tool | When |
|------|------|
| `science_lookup` | **Default for daily factual lookups** — truth dictionary (free → cheap → live only if `live=true`) |
| `science_search` | When dictionary miss needs **fresh Parallel discovery** (same as lookup with live) |
| `science_browse` | See what the stack already searched |
| `science_stats` | Dictionary size, hit rate, sourced/refused counts |
| `science_popular` | **Top dev queries** — what to alias, ingest, or route next |
| `science_ingest` | After manual research — verify claim+URL into dictionary |
| `science_clear` | Full documentary script → gap report |

## Daily workflow (cost-efficient)

```bash
# 1. Boot dictionary once (or after fleet research)
python3 scripts/boot_registry.py

# 2. Free lookup — registry + routing, no Parallel
python3 -m clearance lookup "orphan works directive"

# 3. Only if NOT_CLEARED and you need fresh web results
python3 -m clearance lookup "obscure claim" --live
# or: python3 -m clearance search "obscure claim"

# 4. After you find a source manually — grow the dictionary
python3 -m clearance ingest --claim "..." --url "https://..."

# 5. Weekly — see what devs ask most; optimize dictionary
python3 -m clearance popular
```

Add casual phrasings to `truth-dictionary/aliases.json` — they map to canonical queries for free hits.

## CLI

```bash
cd ~/CODE/cleared
python3 scripts/boot_registry.py                    # cold start from fleet corpus
python3 -m clearance search "Directive 2012/28/EU"  # verified lookup
python3 -m clearance browse
python3 -m clearance serve                          # desk :8080 + /registry + /search
```

## HTTP (hosted or local)

| Route | Purpose |
|-------|---------|
| `GET/POST /search` | Stack websearch JSON |
| `GET /registry` | Browse UI |
| `POST /ingest` | Ingest `{claim,url}` or `{text}` |
| `GET /stats` | Registry stats |
| `POST /clear` | Script clearance |

## Research skill contract

When the fleet saves research, append to `research-inbox/YYYY-MM-DD-<slug>.md`:

**Never write into `research-corpus/`.** That directory is the FROZEN measurement
population every published number is computed over; it is hashed in
`research-corpus/MANIFEST.json` and a write there moves the denominator of every eval
in this repo. Growing it is a reviewed act: add files, re-run
`python3 scripts/freeze_population.py`, commit the manifest, and say which numbers moved.


```markdown
[CLAIM] The EU orphan works directive is Directive 2012/28/EU.
[URL] https://eur-lex.europa.eu/...
```

Then: `python3 -m clearance ingest --text "$(cat file.md)"` or `science_ingest` MCP.

After research sessions, grow the dictionary automatically:

```bash
python3 scripts/auto_ingest_inbox.py
```

## Keys

- `PARALLEL_API_KEY` or `~/.config/keys/parallel.key`
- `GEMINI_API_KEY` or GCP ADC (`GOOGLE_APPLICATION_CREDENTIALS`)
- `REFUSAL_LOG_DB` — override registry path (default `cache/refusal_log.db`)

## Do not

- Use raw web search for facts that will appear in submissions, pitches, or code comments — route through `science_search`.
- Paraphrase a SOURCED span; cite the verbatim quote or print UNSOURCED.
