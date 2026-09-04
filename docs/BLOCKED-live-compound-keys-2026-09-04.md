# BLOCKED — Live compound / orphan exhibit · 2026-09-04

**Status:** BLOCKED on this VM — not a green tick.

## Exact missing credentials

| Credential | Checked how | Result |
|------------|-------------|--------|
| `PARALLEL_API_KEY` | `test -n "$PARALLEL_API_KEY"` | **missing** |
| `~/.config/keys/parallel.key` | `test -f` | **absent** |
| `GEMINI_API_KEY` | `test -n "$GEMINI_API_KEY"` | **missing** |
| Vertex ADC for local Gemini | no `GOOGLE_APPLICATION_CREDENTIALS` / usable ADC in agent env | **not used tonight** |

Command:

```bash
(test -n "$PARALLEL_API_KEY" && echo PARALLEL=set || echo PARALLEL=missing)
(test -n "$GEMINI_API_KEY" && echo GEMINI=set || echo GEMINI=missing)
(test -f ~/.config/keys/parallel.key && echo parallel.key=present || echo parallel.key=absent)
```

Output (2026-09-04): `PARALLEL=missing` · `GEMINI=missing` · `parallel.key=absent`.

## What was still proved without local keys

Hosted desk already has Secret Manager Parallel + Vertex ADC:

```bash
bash scripts/verify_partners_hosted.sh
python3 scripts/partner_honesty_exhibit.py
```

Both ran against https://agent-science-568004190078.us-central1.run.app — partners live · ADK default · honesty classes recorded in `docs/RECEIPT-partner-honesty-night-2026-09-04.md`.

## What was NOT attempted

- Local `python3 agent_science.py fixtures/scripts/documentary-orphan-works.txt` live path (needs keys)
- Hosted full orphan-works A/B re-hammer (prior object finding: **504 @ 300s** on Run A — `docs/FINDING-orphan-works-timeout-2026-09-03.md`)

Oscar: inject keys on a workstation or raise Cloud Run `--timeout` before claiming orphan-works compound on camera.
