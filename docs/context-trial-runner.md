# Local host context trials

A coding agent receives one task in a new detached worktree, with exactly one
assigned `AGENTS.md`. The local CLI then runs the selected external acceptance
script against its submitted tree. A prepared worktree is not a result.

`context_trials.create(spec)` freezes a READY `agent_context_trial` protocol,
exact protocol task prompts, a full base commit, instruction bytes and hashes,
acceptance bytes and hash, repetitions, host identity and capacity ceilings.
Artifacts and worktrees are created outside the source repository. The manifest
hash binds these inputs; the protocol remains separately versioned.

The spec has exactly these fields:

```json
{
  "protocol_id": "saved-protocol-id",
  "protocol_version": 3,
  "repo": "/selected/trusted/repository",
  "base_commit": "FULL_40_CHARACTER_COMMIT",
  "tasks": [{"id": "metadata-resume", "prompt": "EXACT_PROTOCOL_TASK", "acceptance_task": "metadata"}],
  "arms": [
    {"id": "baseline", "instructions_path": "/external/baseline.md", "sha256": "SHA256"},
    {"id": "candidate", "instructions_path": "/external/candidate.md", "sha256": "SHA256"}
  ],
  "acceptance_path": "/external/acceptance.py",
  "acceptance_sha256": "PROTOCOL_CHECK_SHA256",
  "host": {"provider": "native-host", "model": "unknown", "identity": "operator-selected-host"},
  "policy": {"max_attempts": 18, "total_seconds": 5940, "attempt_seconds": 300, "check_seconds": 30},
  "repetitions": 3,
  "artifact_root": "/external/trial-artifacts"
}
```

These are example limits, not spending approval. All task prompts must match the
protocol in order. `acceptance_task` is one fixed positional argument to the
captured Python script, not a command. The task IDs need not equal that argument.
The manifest supplements prose protocol fields with explicit executable pins;
the operator must inspect that mapping before trusted preparation.

`prepare(id, task_id=..., arm_id=..., repetition=..., expected_version=...,
trusted=True)` reserves the slot and its full attempt-plus-check ceiling before
creating a worktree. It returns the task, exact worktree and assigned host. The
host must work only there, preserve the instruction file, use a fresh context and
stop within the attempt ceiling. No model is launched by this module.

`complete(id, attempt_id, expected_version=..., trusted=True)` checks the lease,
Git ownership, exact base HEAD, instructions and acceptance hash. The host must
leave staged or unstaged changes uncommitted. It preserves the
patch and untracked files (including ignored sources), executes the captured check with a timeout, caps output
at 64 KiB, kills its process group, and detects changed tracked/untracked files
or instructions during acceptance. It records acceptance status and elapsed time.
Only the explicit local CLI exposes prepare/complete. MCP creation proposes limits
and copies selected inputs into local artifact files; trusted CLI preparation is
the execution acknowledgement. MCP cannot execute the selected script.

`abort(id, attempt_id, expected_version=..., reason=..., trusted=True)` closes an
unstarted/interrupted host lease. It does not delete work or refund capacity.
There is no automatic cleanup or retry. A process crash can leave PREPARING or
CHECKING; inspect the worktree and receipt. Aborting an abandoned CHECKING attempt
records REVIEW_REQUIRED with an unknown external outcome, never success. Stop any
remaining check process before trusting artifacts. The slot cannot be retried.

All prepared attempts remain in the fixed denominator, including invalid,
cancelled and timed-out attempts. Unchanged code does not count as a fix. Repeated
identical patches in the same task and arm are flagged for provenance review.
Separately reserved attempts still count when their actual checks pass: independent
agents can converge on identical fixes. The flag is not evidence of copying. An all-failing baseline is not a successful trial.

Host/model identity is operator-supplied. Unknown model identity, tokens, billing
and host calls remain unknown. The runner cannot enforce a native host's spending
or interrupt that host itself; it reserves local capacity and rejects late
submissions. It measures selected task acceptance, not general context-file
quality. Process timeouts and an environment with no inherited API credentials
are not a security sandbox for hostile repository code. Select a trusted repo and
check script. A real host attempt and an acceptance fixture are different evidence;
unit tests of this runner are only behavioral controls.

Fresh worktrees share the Git object database. Host isolation is cooperative, not
a blindness guarantee; a host can inspect other commits. Independent trial claims
require host traces showing what each context actually received.

## Terminal and MCP

```text
agent-science research context-trial-create --trial-file trial.json
agent-science research context-trials CASE_ID
agent-science research context-trial-show TRIAL_ID --json
agent-science research context-trial-prepare TRIAL_ID --task TASK_ID --arm ARM_ID --repetition 1 --expected-version 1 --trusted
agent-science research context-trial-complete TRIAL_ID --attempt ATTEMPT_ID --expected-version CURRENT_VERSION --trusted
agent-science research context-trial-abort TRIAL_ID --attempt ATTEMPT_ID --expected-version CURRENT_VERSION --reason "Host did not finish" --trusted
```

Use the version returned by the previous operation. Prepare returns the assigned
worktree and task; give only that task and its local instructions to a fresh host.
MCP `science_research` exposes `context-trial-create` with `trial_spec` and
`context-trial-show` with `trial_id`. It rejects execution actions.

Use `context-trials CASE_ID` (MCP action `context-trials`, `case_id`) to retrieve
the actual trials linked to a case. `--case-version N` limits this view to protocols
pinned at or before that case version. A historical case filters the linkage; trial
status remains the current execution status, not a historical execution snapshot.
Context trials remain separate from two-commit code comparisons.

Acceptance starts Python with `-I -B` and no startup `PYTHONPATH`, loads standard
check infrastructure, then adds the tested repository for imports. Bytecode caches
use a fresh external prefix and are excluded from submitted-file capture. Other
ignored sources are included. Captured patch/file hashes are checked after execution.
These controls prevent the exercised startup-shadow and receipt-tampering paths;
they do not contain arbitrary hostile code imported from a repository.

`host_elapsed_seconds` is the elapsed lease from prepared worktree to CLI submission,
including coordinator dispatch and response delay. It is not pure model latency.
