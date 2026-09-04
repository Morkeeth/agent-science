# Lane C — terminal workflow, followed questions and protocols

Worktree: `agent-science-night-c`; branch: `build/night-workflow-20260905`.
Source baseline: `e12ca6f`. No push, deployment, personal case access or paid provider/model call.

## Delivered

- `research_cli.add_parser/run`: start/show/context/resume/cancel/challenge/compare/follow/update/updates/experiment-plan/protocol plus CLI-only execute-protocol. Registered `func` dispatch, strict object arguments, explicit configured Gemini adapter selection, readable terminal output and JSON output.
- `research_workflow.handle`: shared JSON result path with strict IDs, versions and boolean live flags. MCP rejects execute-protocol. Follow saves a version baseline. Updates compares actual synthesis changes, does not acknowledge them, ranks affected decisions then claims, and never claims a web check. Explicit update creates a run without a paid call.
- `research_protocols`: immutable versioned DRAFT/READY plans, required denominator and acceptance definitions, real cited claim versions, pinned code commits, trusted script digest. Other experiment kinds retain their definitions without claiming an available runner.
- CLI execution captures bounded script bytes once, checks the frozen digest, and passes a private copy to the existing runner. The runner receives expected_case_version; the response must match that version, both pins and the digest. A completed result carries its real experiment ID. Responses omit script source and process output. One attempt per protocol version; completed attempts return stored results, unresolved/failed attempts require an explicit new version.
- `docs/RESEARCH-QUICKSTART.md`: installation, empty store, host reasoning, provider/model setup, aggregate policy, follow/update, and experiment workflow. Live configuration instructions were inspected against current adapters; no live run or fresh dependency installation was performed.

## Working commits

- `23e1662`: initial dispatch, followed store and experiment protocols; four local fixture tests.
- `ff0caa1`: working CLI dispatch, concise output, explicit reasoner and frozen/idempotent execution.
- `4e70a1f`: strict handler/protocol validation, claim scope/challenge rendering, expected-case guard integration, 20 tests and quickstart.
- Final slice: clean CLI configuration errors, claim-reference type validation, 21st test and this receipt.

The runner expected_case_version extension belongs to coordinator commit `e7e5dca`; it was read through the integration worktree during final tests, not copied into this lane's owned changes.

## Verification actually run

Final focused test output: `21 passed` (private temporary cases and Git repository). Test command preloads this lane's CLI/protocol modules, then uses the integration package path for actual A/B and the coordinator runner:

```python
import clearance
from clearance import research_cli, research_protocols
clearance.__path__.insert(0, '/Users/morkeeth/CODE/agent-science-night/clearance')
from clearance import experiments
import pytest
raise SystemExit(pytest.main(['tests/test_research_workflow.py', '-q']))
```

The real acceptance fixture creates two Git commits, holding a file first as `wrong`, then `expected`. A separate trusted script checks the expected file value. Actual CLI execute-protocol output recorded **baseline 0/1 passes; candidate 1/1 passes** with true pinned commit hashes and a persisted experiment ID. This proves that fixed fixture check only; it is not evidence of model or research quality.

Controls exercised:

- Caller script changes after capture: the real runner still runs the frozen bytes and candidate passes.
- Digest changes before capture: execution rejected.
- Case changes between workflow check and runner: expected-version guard rejects before any second experiment is recorded; protocol attempt records FAILED.
- KeyboardInterrupt in runner effect: attempt remains RUNNING with interrupted_at, and repeat execution is rejected.
- Completed retry: same experiment ID, only one case experiment.
- Non-code READY protocol: execution rejected because no compatible runner exists.
- Missing denominator, null/empty/malformed entries, missing claims, stale cases and missing trust acknowledgement: drafts or explicit rejection.
- MCP execute request, `live:"false"`, float/bool/null versions and missing IDs: explicit rejection before dispatch.
- Actual synthesis compare: a new authored unresolved interpretation produces an update; clock-only saved changes do not. Reading updates twice retains baseline and never changes checked_at.
- Contested/scope output retains claim state, rationale, conditions, strongest challenge and reversal condition.
- Missing reasoner configuration: error names required environment variables, returns status 2 without traceback.

The real integrated `stack_cli.main` was also invoked with research shorthand and a temporary empty database: start exited 0 with `awaiting_reasoning`, show exited 0 and printed runnable follow-up commands including the selected database. The first-use command did not pretend to have completed an investigation.

## Limits and remaining integration work

No live research, live Perplexity/Gemini test or fresh pip install was authorized/run. A/B modules are not duplicated in this worktree; their integrated implementations were used for tests. Coordinator owns full installed CLI/MCP acceptance and independent review. Task/outcome meanings remain authored; the user-selected script must actually implement them. The code runner has fixed paired counts/timeouts and does not implement arbitrary experimental stopping logic. Running trusted Git code is not sandboxing. An interrupted attempt may have an experiment saved on the case before its protocol link completed; it must be inspected, never blindly rerun.
