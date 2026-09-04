# First use — research, challenge, follow (no nightplan required)

Cold clone, no API key, no network. One evening path from empty local store to a day-two change report.

## Install

```bash
git clone https://github.com/Morkeeth/agent-science
cd agent-science
# optional: python3 -m venv .venv && source .venv/bin/activate
```

## Offline demos (stranger path)

```bash
# Lane A — plan → challenge → contested claim
bash scripts/demo_research_challenge.sh

# Lane C — follow a question → ranked change report → experiment plan (not a result)
bash scripts/demo_research_day_two.sh
```

Both exit 0 with `DEMO OK` and print the case/run ids.

## Manual day-one (plan only)

```bash
DB=/tmp/as-first-use.db

# Local question map; no provider calls
python3 -m clearance research "When does persistent memory help coding agents?" \
  --plan-only --db "$DB"

# Or seed with an explicit source URL (still offline if the doc is cached/fixtures)
python3 -m clearance research start "Do fresh sessions reduce repeated errors?" \
  --source https://example.org/study --plan-only --db "$DB"
```

Live discovery needs `--live` and `PARALLEL_API_KEY` (or `~/.config/keys/parallel.key`). Default stays offline.

## Challenge (overturn, do not agree)

```bash
python3 -m clearance research challenge CASE_ID --db "$DB" --max-steps 4
python3 -m clearance research resume RUN_ID --db "$DB"
```

A challenge is a **new investigation** against a pinned case version. It looks for observations that could overturn material claims. Signature line in every answer: **What would change this answer?**

## Day-two — follow and updates

```bash
python3 -m clearance research follow CASE_ID --db "$DB" --note "watch this"
python3 -m clearance research updates --db "$DB"          # refresh snapshots; rank by effect
python3 -m clearance research updates --db "$DB" --live   # only this advances checked_online
python3 -m clearance research follow --list --db "$DB"
```

Updates rank changes by effect on saved conclusions and decisions. Sidebar/uncited noise is recorded at low rank and omitted from the material headline. When nothing material changed, the report says so explicitly — that empty result is intentional.

## Experiment plan (denominator before execution)

```bash
python3 -m clearance research experiment-plan CASE_ID \
  --hypothesis "Intervention preserves the acceptance check." \
  --kind observation \
  --db "$DB"

# Compatible code_change protocols can execute a trusted local acceptance script:
# python3 -m clearance research experiment-plan --execute --protocol-id PROTO --db "$DB"
```

A protocol is a **plan**, never a result. Execution attaches a separate measured `experiment_id`. Renaming a plan into a result is refused.

## MCP

```bash
python3 -m clearance mcp
# Tool: science_research
# actions: research, challenge, resume, show, list, cancel, follow, unfollow, updates, experiment-plan
```

## Command map

| Intent | Command |
|--------|---------|
| Plan investigation | `research "…" --plan-only` |
| Challenge answer | `research challenge CASE_ID` |
| Resume paused run | `research resume RUN_ID` |
| Track for day-two | `research follow CASE_ID` |
| Change report | `research updates` |
| Record experiment denominator | `research experiment-plan CASE_ID --hypothesis "…"` |
| Offline demos | `bash scripts/demo_research_challenge.sh` · `bash scripts/demo_research_day_two.sh` |

## Honesty

- No keys on this path → no live web quality claim.
- Assessments need exact source quotes; the local planner does not author scientific verdicts.
- `checked_online` is true only after an update with `live` and actual fetches.
- Do not claim USE BAR met from these demos.
