---
doc: use-bar-path
date: 2026-09-04
project: Agent Science
---

# USE-BAR PATH — Cursor / Claude before raw websearch

**Bar:** every factual ask goes through Agent Science (lookup or visibility) **before**
raw browser/WebSearch. Gate green ≠ Oscar uses this every search — only a filled
session receipt proves that.

**Hosted:** https://agent-science-568004190078.us-central1.run.app  
**Skill:** `.cursor/skills/agent-science-websearch/SKILL.md`  
**Interceptor:** `clearance/use_path.py` · MCP `science_use_bar` · CLI `use-bar`

---

## Exact commands (pick one path)

### A · Cursor MCP (preferred when MCP installed)

```bash
python3 scripts/install-mcp.sh   # once; then restart Cursor
```

In the agent turn, **before** any WebSearch / browser tool:

1. `science_use_bar` `{ "query": "…", "mode": "lookup", "traffic": "human" }`  
   — or `mode: "visibility"` for the full pane rundown  
2. Read `receipt_id` + `label` / span or refuse  
3. Only if `NOT_CLEARED` **and** the ask matters: `science_lookup` with `live=true`  
   or `science_visibility` with `live=true`  
4. Never invent a citation. Never paraphrase a SOURCED span.

Equivalent without use_bar wrapper: `science_visibility` (full) or `science_lookup`
(fast). Prefer visibility for research; lookup when you only need the verdict.

### B · CLI in the repo (no MCP)

```bash
cd agent-science   # or this clone

# Default free tier + session receipt
python3 -m clearance.stack_cli use-bar "YOUR QUERY" --traffic human

# Full visibility panes + receipt
python3 -m clearance.stack_cli use-bar "YOUR QUERY" --mode visibility --traffic human

# Fast verdict only (also logs to registry; tag traffic)
python3 -m clearance.stack_cli lookup "YOUR QUERY" --traffic human

# Show receipts from this machine
python3 -m clearance.stack_cli use-bar --receipts
```

Receipts default to `~/.agent-science/session-receipts.jsonl`  
(override: `AGENT_SCIENCE_RECEIPTS`).

### C · Hosted HTTP (browser / curl)

```bash
HOST=https://agent-science-568004190078.us-central1.run.app

# Free dictionary first — tag human so /popular is not gate-polluted
curl -sS "$HOST/search?q=YOUR+QUERY&live=false&traffic=human" | python3 -m json.tool

# Full visibility UI (film / judge face)
open "$HOST/visibility/ui?q=YOUR+QUERY"

# Human vs gate/demo split
curl -sS "$HOST/popular" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('traffic_notes')); print('human', d.get('popular_human',[])[:5])"
```

### D · Claude Code / other agents

Same as B, or call MCP tools if configured. Hard rule in system prompt:

> Before raw web search: run `python3 -m clearance.stack_cli use-bar "QUERY" --traffic human`
> and keep the `receipt_id`. If you skip this, say UNSOURCED habit — do not claim Agent Science was used.

---

## Traffic tags (do not pollute `/popular`)

| Tag | When |
|-----|------|
| `human` | Real operator / Oscar ask |
| `gate` | Smoke, trial, CI, `new_user_trial`, xyzzy probes |
| `fleet` | Automated agent fleets |
| `demo` | Film / visibility loops (`ralph loop agentic`, …) |
| omit | Heuristic classifies known probes/demos; else `unknown` |

Hosted popular measured **2026-09-03**: `ralph loop agentic` **110×**,
`xyzzy-nonexistent-claim-99999` **20×** — optimize from `popular_human`, not `popular_all`.

---

## Session proof (Oscar fills)

Template: `docs/SESSION-RECEIPT-TEMPLATE.md`  
Do **not** claim “Oscar uses this every websearch” without a filled template +
matching `receipt_id` lines from `~/.agent-science/session-receipts.jsonl`.

---

## Offline stranger check

```bash
bash scripts/use_bar_offline.sh
```

No API key required for intercept + traffic tests + baseline arms.

---

## Oscar-only (stop at the door)

- YouTube / film upload  
- Devpost submit  
- Key rotation in GCP / Parallel console  
- Redeploy with secrets in env  

Build lane ends when the path is documented, hooked, measured, and receipt-ready.
