# BLOCKED — Live compound exhibit · 2026-09-10

**Status:** BLOCKED on this VM · offline receipt remains authoritative

## Missing credentials (exact)

| Credential | Checked | Result |
|------------|---------|--------|
| `PARALLEL_API_KEY` | `test -n "$PARALLEL_API_KEY"` | **missing** |
| `~/.config/keys/parallel.key` | `test -f` | **absent** |
| `GEMINI_API_KEY` | `test -n "$GEMINI_API_KEY"` | **missing** |
| Vertex ADC | `clearance.gemini.vertex_project()` | **None** |

## Hosted orphan-works A/B

Not attempted: without Parallel + Gemini/Vertex, a live `/clear` (local desk) cannot run discovery+locate. Hosted shared `/clear` is also **401** under private-workspaces (product boundary).

## Authoritative offline measure

```bash
python3 scripts/compound_exhibit_receipt.py
```

See `docs/COMPOUND-EXHIBIT-2026-08-29.md` (A=2→B=1 Parallel, corpus hits ≥1).

## Hosted partner readiness after Oscar deploy

```bash
bash scripts/verify_partners_hosted.sh
```

Expect: `/health` partner fields · public `/partners` · `/clear` gated OK.
