# Native-host context trial: 18 attempts

The existing instruction bundle passed **9/9** selected attempts. The concise
bundle passed **8/9**. This pilot does not establish a benefit from shortening
instructions or a general superiority of either bundle. Content and length changed
together; these were three selected maintenance tasks, not a representative coding
benchmark. No product instruction file was replaced on this evidence.

## Frozen definition

- Case `c5d4051a667f` v12; protocol `6bcf588dafaa` v3.
- Trial `2fda7ea51a36443c`; three tasks × two arms × three fresh contexts = 18 slots.
- Tested base `3dd6e3bf8401564a4f09b401595cd60cf4de6233`.
- Original runner `526bd881ba41b1a14bec323ff9d948ffe1de5d5a` throughout.
- Existing instructions: 10,868 bytes, SHA-256
  `ca746e3306cc7895a996ff7ef22744e2e2f002440dcf97db1c3be10ec7ba775b`.
- Concise instructions: 1,113 bytes, SHA-256
  `7318bdf1d5f601c7300ada0c89f518fbfab2100eb7e53332c11d1f6ed3bcb48a`.
- External acceptance script: SHA-256
  `4ff4a68990a4b844f42948f5aca25c5621bb4520790626e6048f1a8942cdae0f`.
- Limits fixed before attempts: 300 seconds per host lease, 30 seconds per check,
  18 maximum attempts and 5,940 reserved seconds. No refunds or replacement attempts.

An independent agent authored acceptance from behavior contracts before this trial.
Calibration rejected all three baseline defects and accepted the then-current fixes.
That calibration was a control check, not a context-effect result. The same frozen
script then checked actual native-host submitted patches. Its retained output header
still says acceptance-control calibration; the trial record binds each execution to
its distinct host attempt and submitted tree.

Each attempt used a fresh native context and detached worktree. Hosts received the
same task-specific behavior requirement, read their assigned AGENTS.md, and were
instructed to avoid other worktrees/history, network/provider calls and acceptance
files. Patches remained uncommitted. Task order was shuffled before execution with
seed 20260905; both arm orders were used within paired concurrent attempts.

## Actual outcomes

- Offline → approved live metadata: existing **3/3**, concise **3/3**.
- Reject unassessed synthesis; allow explicitly unresolved assessments: existing
  **3/3**, concise **3/3**.
- Reject duplicated baseline outcomes across no-op revisions: existing **3/3**,
  concise **2/3**.

Attempt `c2e13451d0f1467b`, concise repetition 2, failed the no-op revision check despite its
own local tests passing. Its whole-evidence hash retained incidental capture metadata,
so the real no-op investigation could still fill another repetition. The independently
frozen check exercised the actual persisted operation and rejected it. The submitted
patch, failing output and slot remain intact; no repair was substituted.

Median elapsed leases were 110.50 seconds for existing instructions and 110.63 for
concise instructions. These include coordinator dispatch/submission delays and are
not pure model latency. Exact model version, host tokens, host calls and billing
remain unknown. No efficiency or dollar-cost comparison is claimed.

[Machine receipt](context-trial.json) retains each original state, timing and digest.
Full patches, worktrees, acceptance output and host coordination records remain
outside Git. The host-produced changes are experimental outputs, not product commits.

## Review and repeatability

[Cursor/Fable runner review](CONTEXT-RUNNER-REVIEW.md) found concrete measurement
and recovery defects. The product runner was fixed separately while the pilot stayed
pinned. A post-review acceptance replay of the 18 preserved patches produced the
same 18 verdicts with no tracked patch changes. These are rechecks, not 18 additional
host attempts. Twelve rechecks used `243fa1a`, six used `99ebf5d`; their context runner
source blobs are identical.

An independent final receipt review checked all 18 slots, exact base HEADs, assigned
instruction hashes, captured patches, composite hashes and acceptance-output hashes.
It found no receipt defect changing the counts. Current worktree scans found no
noncache untracked files or identified import-shadow modules. Current scans cannot
exclude transient historical interference. Shared Git/filesystem access means host
blindness is cooperative, not independently attested.

A real MCP agent retrieved the actual trial through its case. Inspect it locally:

```text
agent-science research context-trials c5d4051a667f
agent-science research context-trial-show 2fda7ea51a36443c --json
```

The substantive result is limited: both bundles enabled these selected fixes, one
concise-bundle attempt failed, and this run supplies no demonstrated reason to
replace the existing instructions. Broader tasks, resource measurement and independent
host isolation remain necessary before a general context-policy conclusion.
