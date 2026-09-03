---
doc: cloud-receipt
wave: 2026-09-04 use-bar path
agent: cursor cloud
branch: cursor/use-bar-path-9ff9
---

# CLOUD RECEIPT — as-use 2026-09-04

**Slice:** use-bar path (NOT film theater). Make default websearch measurable.

## SHIPPED

| Artifact | What |
|----------|------|
| `docs/USE-BAR-PATH-2026-09-04.md` | Exact Cursor/Claude/MCP/CLI/hosted commands before raw websearch |
| `docs/SESSION-RECEIPT-TEMPLATE.md` | Oscar fills — agents must not claim daily use without it |
| `clearance/use_path.py` | Interceptor + session receipts (`science_use_bar` / CLI `use-bar`) |
| `clearance/traffic.py` | human \| gate \| fleet \| demo \| unknown |
| `clearance/query_analytics.py` | `popular_human` + `traffic_notes` (gate/demo excluded from optimize queue) |
| `clearance/mcp_server.py` | `science_use_bar` tool; lookup/search take `traffic` |
| `cloud/service.py` | `?traffic=` on `/search`; popular UI shows human vs all |
| `scripts/use_bar_offline.sh` | Stranger one-command, no key |
| `scripts/eval_use_path_baseline.py` | shipping_local / shipping_hosted / naive_cite / always_silent |
| `fixtures/use-path/cases.json` | 6 scored cases |
| `.cursor/skills/agent-science-websearch/SKILL.md` | Step 0 = use-bar + receipt |

## VERIFIED (command → object)

| Claim | Command | Result |
|-------|---------|--------|
| Hosted health | `curl -sS …/health \| python3 -m json.tool` | `ok: true`, `engine_default: adk`, parallel+gemini true |
| Hosted visibility UI | `curl -sS -o /tmp/vis_ui.html -w '%{http_code}' …/visibility/ui` | **200** |
| Hosted free search | `curl -sS '…/search?q=Directive+2012/28/EU&live=false'` | **SOURCED** `cost_tier=free` `dictionary_exact` |
| Popular pollution at object | `curl -sS …/popular` → inspect `popular_queries` | **ralph loop agentic 110×**; ralph variants in top list **148 asks**; xyzzy **20×** |
| Traffic unit tests | `python3 tests/test_traffic_class.py` | **traffic tests OK** |
| Use-path / MCP tests | `python3 tests/test_use_path.py` | **use_path tests OK** |
| Popular split tests | `python3 tests/test_popular.py` | **popular tests OK** |
| Offline stranger path | `bash scripts/use_bar_offline.sh` | **use-bar offline OK** (receipt written; gate probe NOT_CLEARED) |
| Baseline arms | `python3 scripts/eval_use_path_baseline.py` | **shipping_hosted 18/18**; **naive_cite 14**; **always_silent 12**; **shipping_local 12** |
| CLI interceptor | `python3 -m clearance.stack_cli use-bar "…" --traffic human --json` | `receipt_id` emitted |

### Baseline finding (embarrassing + true)

```
winner: shipping_hosted
finding: shipping_hosted leads (18/18). Hosted ahead of local (18 vs 12) —
  cold/boot shelf cannot replay SOURCED for flagship without warm exact rows / EUR-Lex fetch.
  Local tied/lost to always_silent (12 vs 12).
```

Naive always-cite **beats local shipping** on this fixture. Hosted warm shelf still perfect.
Do not paper over: offline free path for `2012/28/EU` returned **UNSOURCED** via `route:celex`
(`search_found_no_admissible_source`) on this VM — EUR-Lex fetch blocked; no warm exact-replay row.

## Oscar-only (stop at the door)

- Film / YouTube upload  
- Devpost submit  
- Key rotation in console  
- Redeploy with secrets / ship traffic_notes onto hosted until Oscar deploys  

**Not claimed:** “Oscar uses Agent Science every websearch.” Template:
`docs/SESSION-RECEIPT-TEMPLATE.md`.

## WRONG / left broken

1. **Hosted `/popular` does not yet return `traffic_notes` / `popular_human`** — code is in this
   branch only; live revision still the old schema. Measured pollution from old endpoint.
2. **Local / cold-boot shipping loses to naive_cite** on flagship sourced cases — shelf + CELEX
   fetch gap; not fixed tonight (would need fixture seed or deploy of warm GCS row — outward).
3. **Interceptor is habit + receipt, not a hard Cursor hook** — agents can still call raw
   WebSearch; we cannot force the IDE. Receipt is the measurable stub.
4. **Did not run `full_gate.sh` / `watch_it_go_red` this wave** — scope was use-path; those remain
   prior-wave greens, not re-derived here.
5. **`/stats` traffic_notes** lands only after this code is served; local `stack_search.stats()`
   includes it.

## Hack NOW boxes

Ticked only after the commands above ran. See `hack.md` §NOW WAVE 2026-09-04.
