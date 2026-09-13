# BLOCKED — Live compound exhibit · 2026-09-13

**Attempted:** orphan-works / partner live A/B on this Cloud Agent VM.  
**Outcome:** BLOCKED — not a silent skip.

## Exact missing credentials

| Credential | Checked how | Result |
|------------|-------------|--------|
| `PARALLEL_API_KEY` | `test -n "$PARALLEL_API_KEY"` | **missing** |
| `~/.config/keys/parallel.key` | `test -f` | **absent** |
| `GEMINI_API_KEY` | `test -n "$GEMINI_API_KEY"` | **missing** |
| Vertex ADC | no `GOOGLE_APPLICATION_CREDENTIALS` / usable ADC on this VM | **unavailable for live model** |

## What remains authoritative

| Exhibit | Command | Status |
|---------|---------|--------|
| Offline compound | `python3 scripts/compound_exhibit_receipt.py` | use this for video numbers until live keys exist |
| Eval baseline vs shipping | `python3 scripts/eval_refusal_baseline.py` | re-run 2026-09-13: **5/6 vs 6/6**, delta +1 |
| Eval ablation | `python3 scripts/eval_refusal_ablation.py` | re-run 2026-09-13: **5/6 vs 6/6**, delta +1 |
| Hosted orphan-works full script | prior finding | Run A **504** @ 300s (2026-09-03) — do not claim on video |

## Oscar unblock

1. Place Parallel key in Secret Manager / local `~/.config/keys/parallel.key` (never in repo).
2. Redeploy with `deploy.sh` (partner-surfaces commit).
3. Re-run `bash scripts/verify_partners_hosted.sh` then offline-or-live compound as appropriate.
