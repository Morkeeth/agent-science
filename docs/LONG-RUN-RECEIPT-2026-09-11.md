# Long run receipt — Agent Science · 2026-09-11

**Stamp:** 2026-09-11T00:20:49Z UTC  
**URL:** https://agent-science-568004190078.us-central1.run.app  
**Subject:** `longrun-0911-0020`  
**Hosted mode:** `private-workspaces`  
**Log:** `/tmp/agent-science-longrun-3882.log`

## Goal

Truth dictionary stranger path: free lookup first, compound on repeat, honest miss, registry grows.
When hosted mode is `private-workspaces`, anonymous desk probes are **skipped** and offline compound + artifact-claims substitute.

## Results

| Gate | Result |
|------|--------|
| Local controls | watch_it_go_red + dictionary/routing/popular/partner |
| Hosted health | mode=`private-workspaces` (re-curl; do not carry engine_default from old receipts) |
| Anonymous desk | skipped if private-workspaces; else free tier + compound |
| Surfaces | gated behind workspace login when private-workspaces |

## Stats delta

```json
before: {"blocked":"private-workspaces","note":"anonymous /stats login-gated"}
after:  {"blocked":"private-workspaces","note":"anonymous /stats login-gated"}
```

## Run A / B (truncated)

```json
{
    "blocked": "private-workspaces"
}
```

```json
{
    "blocked": "private-workspaces"
}
```

## Pass/fail

- **Checks passed:** 12 (updated at end of script)
- **Command to replay:** `bash scripts/long_run_goal.sh`
- **Stranger one-liner:** `bash scripts/new_user_trial.sh`

