# RECEIPT — truth layer night wave · 2026-08-31

Night build: WOW websearch transparency, CONTRARY_TO_RESEARCH, stack-fit magnet, community notes, truths dashboard.

---

## SHIPPED

| Slice | What exists now |
|-------|-----------------|
| **S1** | `clearance/visibility.py` — transparency panes: `angles_searched`, `shallow_route`, `imbalance`; wired to CLI `visibility --full` and MCP `science_visibility` |
| **S2** | `CONTRARY_TO_RESEARCH` in `clearance/verdict.py`; detection in `clearance/contrary.py`; seed `truth-dictionary/contrary-seeds.json` + `research-inbox/2026-08-31-contrary-ralph-loop.md` |
| **S3** | `clearance/stack_fit.py` — stack detect + `fits\|partial\|mismatch` + improvement line; CLI `stack-fit` and `truth skill --fit` |
| **S4** | `scripts/refresh_hn_signals.py`; HN (live Algolia when available) + ARKIVX snapshot in `field-signals.json` |
| **S5** | `clearance/community_notes.py` — JSONL upload/dispute; CLI `notes list\|upload\|dispute`; seed `data/community-notes-seed.jsonl` |
| **S6** | `GET /truths/ui` — popular queries + field ★ strip; video script transparency beats |
| **S7** | `VISION-2026-08.md`, `docs/VIDEO-SCRIPT-2026-08-29.md`, `docs/STATUS.md`, `hack.md` LOG |
| **S8** | 4 new test suites (15 tests); `full_gate.sh` extended |

**Tests added:** `test_visibility_transparency.py` (4), `test_contrary_verdict.py` (4), `test_stack_fit.py` (4), `test_community_notes.py` (3) → **+15** (124→139 product suites in gate loop).

---

## VERIFIED

| Claim | Command |
|-------|---------|
| Full gate green | `bash scripts/full_gate.sh` → **FULL GATE OK** |
| Transparency panes on `--full` | `python3 -m clearance.stack_cli visibility "ralph loop agentic" --full --no-personal 2>&1 \| head -25` → `## 1b · Transparency`, `SHALLOW_ROUTE`, `variant=` angles, `IMBALANCE` |
| CONTRARY demo | `python3 -m clearance.stack_cli lookup "ralph loop agentic practice"` → `[CONTRARY_TO_RESEARCH]` with named why |
| Stack-fit | `python3 -m clearance.stack_cli stack-fit "science_lookup MCP fleet"` → `fit=fits` |
| Community notes | `python3 -m clearance.stack_cli notes list --path /tmp/x.jsonl` → seeded pending row |
| New suites | `python3 tests/test_visibility_transparency.py` etc. → **15/15 passed** |
| HN refresh honest | `python3 scripts/refresh_hn_signals.py` → `HN live: 5 stories` (Algolia) or snapshot warn |
| Docs gate | `python3 scripts/bench_check_docs.py` → ALL match |

### Baseline arm (lookup-only vs full visibility)

Query: `ralph loop agentic practice`

| Arm | Output | What changed |
|-----|--------|--------------|
| **Baseline** (`lookup` only) | `CONTRARY_TO_RESEARCH` + one `why` paragraph | Primary label only |
| **Full visibility** | Same primary **plus** transparency angles (5 routes/tiers), stack-fit `fits`, 3 GitHub ★, 5 blogs, practices corpus, peer queries | Panes 1b/1c/3–6 add field context lookup alone cannot show |

**Finding:** visibility adds measurable context (angles searched, adoption ★, practitioner depth, stack-fit). Lookup-only would miss shallow-route warning and imbalance on other queries.

---

## WRONG

| Item | Detail |
|------|--------|
| ARKIVX not live | `arkivx` block is **snapshot only** — no API wired; documented honestly in `TRUTH-LAYER-SOURCES.md` |
| HN may be snapshot | `refresh_hn_signals.py` falls back to static snapshot when Algolia blocked — check `source` field |
| CONTRARY not in `Verdict` dataclass | `CONTRARY_TO_RESEARCH` is a stack label via `contrary.py`, not a `Verdict()` construction — clearance script rows unchanged |
| `/truths/ui` not on hosted | Built in `cloud/service.py` but **not deployed** (Oscar deploy only) — verify locally: `python3 -m clearance.stack_cli serve` then open `/truths/ui` |
| Gate count in STATUS | Re-derived at gate run; prior prompt said 124/124 — measured **139** new-suite total in gate loop after this branch |
| Community notes path | Default `~/.agent-science/community-notes.jsonl` — film seed is in-repo `data/` only until first CLI list copies it |

---

*Oscar film glance:* Run `python3 -m clearance.stack_cli visibility "ralph loop agentic" --full` — beat 1b shows **what was searched**; beat 1 primary shows **CONTRARY_TO_RESEARCH** stamp when field outruns paper.
