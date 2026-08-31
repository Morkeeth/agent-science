# Personal truth DB + Magnet bridge

**Ruling:** Agent Science websearch expands into a **per-user truth database**.  
Shared field signals are inputs. Your asks, refuses, fetches, and skill verdicts live on **your** shelf.

## Shape

```
~/.agent-science/truth.db          # default (override: AGENT_SCIENCE_TRUTH_DB)
├── asks        every visibility / websearch result you ran
├── truths      promoted claims + Magnet skill rows (helped|hurt|baseline)
└── fetches     URLs pulled from field-signals (new material)
```

| Kind | Meaning |
|------|---------|
| `claim` | Verified or refused ask from visibility |
| `skill` | Magnet: skill X helped/hurt/baseline on probe Y |
| `field_fetch` | (reserved) · fetches table holds blog/★ URLs |

## Commands

```bash
# visibility auto-indexes (unless --no-personal)
python3 -m clearance visibility "ralph loop" --full

python3 -m clearance truth stats
python3 -m clearance truth recent
python3 -m clearance truth truths --kind skill
python3 -m clearance truth fetch-field          # pull ★/blogs into personal fetches
python3 -m clearance truth skill agent-science-websearch helped --probe demo
```

## Magnet combine

Magnet evaluates skills on **your** stack → `helped` / `hurt` / `baseline`.  
Those verdicts are **truths** — same layer as websearch claims:

```bash
python3 -m clearance truth skill ralph-claude-code helped --probe demo-pass-rate
```

New skills → new truths. Not a marketplace rating; measured on your eval.

## Ambition roadmap

| Slice | Status |
|-------|--------|
| Local personal DB + auto-index from visibility | ✅ stub |
| `truth fetch-field` from field-signals | ✅ |
| Magnet CLI bridge (`truth skill`) | ✅ stub |
| Live Magnet eval → auto-write skill truths | next |
| Continuous fetch of new blogs/skills into shelf | next |
| Multi-user / org shelves | later |

## Docs

`WEBSEARCH-FULL-RUNDOWN.md` · `TRUTH-LAYER-SOURCES.md` · `RESEARCH-WEBSEARCH-COMPETITORS-2026-08-31.md`
