# FINDING — long_run_goal false green · 2026-09-17

## What looked green

`bash scripts/long_run_goal.sh` printed local OK lines and exited **0** while never
reaching hosted checks on private-workspaces revision `00028-hed`.

## Root causes (both measured)

1. **SIGPIPE under `pipefail`:** `out=$(python3 -m clearance lookup "$q" 2>&1 | head -1)`
   — same class as the 2026-09-16 cold-clone abort. Script died mid local lookups.
2. **`exec > >(tee …)` masked exit status:** after the honesty fix printed
   `failed=13`, the process still exited **0** because tee's status replaced the
   script's. Watched: failed tally ≠ process exit.

## Fix

- Drop `| head` from lookup capture (sed/full buffer instead).
- Hosted curls use `-sS` + HTTP code checks; stripped `/health` and 303/401 count as FAIL.
- Remove `exec > >(tee)`; explicit `exit 1` when `fail>0`.
- `new_user_trial.sh` same honesty for 303/401/stripped health.

## Commands

```bash
bash scripts/long_run_goal.sh; echo exit:$?
# → failed=13 exit:1 on 00028-hed (partner strip + private-workspaces)

bash scripts/new_user_trial.sh; echo exit:$?
# → Trial FAILED exit:1

bash scripts/verify_cold_clone.sh
# → OK (offline stranger path)
```
