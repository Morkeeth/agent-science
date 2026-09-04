# Terminal workflow — 2026-09-04

CLI and MCP are the primary product interface. The existing Claude design remains the design direction; this change does not modify hosted pages.

## User flow

Install the local command with `python3 scripts/install-cli.py`. From a project, run `agent-science case review --root .`, inspect the current case and source version, and save a decision with `--version`. Use `--supersedes` to replace a decision while preserving its history. A decision can cite a verified source, a valid saved repo experiment, or both.

Review uses saved snapshots only. It does not fetch the web or inspect current repo changes. Refresh explicitly before assessing new evidence. Local work needs no hosted account.

## Validation

Candidate: `b8302612c9ed833f9de84831ce79414effcc2836`.

- 50 pytest tests passed across terminal, evidence, hosted API/pages and browser regression suites. Terminal checks run actual CLI and stdio MCP processes.
- Forced two concurrent legacy database readers to reach migration together; both completed. Corrupt SQLite input returned a structured error and the same MCP process answered its next request.
- An independent agent used stdio MCP to inspect, review, supersede and retrieve historical evidence. It ran a local experiment and cited the saved experiment in a decision.
- Cursor and Fable reviews identified the Markdown tool response regression, migration race and unhandled SQLite failures. These were fixed and exercised. List/review now avoid duplicate case loading and apply cheap filters before loading evidence.
- The full gate now invokes pytest explicitly for the new suites. The complete hosted/deployment gate was not run because this slice is local CLI/MCP work.
- Privacy scan: zero hits across 355 tracked files before this receipt was added.

## Measured acceptance

The actual `case experiment` command ran the frozen `review/acceptance/terminal_workflow.py` against baseline `2d5e3ecb84dbeb51f2b95d33e8b8b5c49c276680` and the candidate. Baseline: 0/3; candidate: 3/3. All runs retained the same acceptance bytes and captured output completely. The old commit fails because the review command is absent.

This is one deterministic terminal contract repeated three times, not three independent quality evaluations. It checks local review, query retrieval, caller repo context, MCP tool discovery, missing-version error signaling and session continuation. Broader research quality, API cost and human rework were not measured.

The saved local case is `fd9d26c32d77`, experiment `f9c97fda4618`, decision `2ada5258f04a`. The decision cites that experiment. A sanitized measurement is in `review/acceptance/terminal-workflow-result-20260904.json`; source snapshots and the private database remain outside Git.
