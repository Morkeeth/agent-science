# RECEIPT — live compound exhibit BLOCKED

**Date:** 2026-09-02 00:15 UTC · **Subject:** `orphan-works` · **Mode:** BLOCKED (no keys)

## Why blocked

This VM has no Gemini or Parallel credentials:

| Key | Status |
|-----|--------|
| `GEMINI_API_KEY` | not set |
| `PARALLEL_API_KEY` | not set |
| `~/.config/keys/gemini.key` | missing |
| `~/.config/keys/parallel.key` | missing |

Live compound A/B on `documentary-orphan-works*.txt` cannot run here. Do not claim live
numbers from this receipt.

## Offline path (authoritative on this VM)

```bash
python3 scripts/compound_exhibit_receipt.py
```

**Output (2026-09-02):**

| Run A parallel_calls | Run B parallel_calls | delta | corpus_hits B |
|---:|---:|---:|---:|
| 2 | 1 | +1 | 2 |

- Run B parallel < Run A: **yes**
- corpus_hits B ≥ 1: **yes**

## Hosted prior (2026-08-31 — not re-run tonight)

From `docs/LONG-RUN-RECEIPT-2026-08-31.md`:

- `long_run_goal.sh` → A=**1**→B=**0** Parallel · B corpus hits=**1**
- Orphan-works full script Run B → **504 Gateway Timeout** at 300s

## Oscar unblock

1. Ensure `~/.config/keys/parallel.key` exists locally
2. Vertex ADC for Gemini (no plaintext key in deploy — see `deploy.sh`)
3. Run `bash scripts/long_run_goal.sh` on a machine with keys
4. Do **not** claim orphan-works full script on video until Run B completes under 300s
