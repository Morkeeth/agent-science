# Overnight component contract, revision 1

Baseline product code: e12ca6f. Integration starts with that code plus the saved plan.
Each lane owns only the files named below. The coordinator owns CLI/MCP entry points,
shared contract, integration tests, evaluation and final documentation.

## A: clearance/night_runs.py, clearance/reasoning.py, tests/test_night_runs.py

Public APIs (keyword db selects existing cases database):
- start(question, *, root=None, case_id=None, challenge=False, policy=None, db=None) -> run dict
- get(run_id, *, db=None) -> run dict
- resume(run_id, *, proposal=None, reasoner=None, live=False, db=None) -> run dict
- cancel(run_id, *, db=None) -> run dict
- context(run_id, *, db=None) -> bounded local reasoning context

run has id, case_id, case_version, revision, status, question_map, steps, limits,
usage, stop_reason. Persist in separate night_* tables in the case DB. Case
versions and run revisions are distinct. A run paused for host reasoning is not
complete. start makes no external call. resume(proposal=...) advances one host
step; reasoner callable(context)->proposal may drive the bounded loop. No implicit
paid model calls. Implement one explicit configured reasoning adapter; no shell
execution selected by source text. A saved challenge pins the case version and
uses its strongest challenges rather than rerunning the initial question.

Policy has discovery_calls, document_reads, reasoning_calls, rounds; live calls
require an explicitly configured shared policy with aggregate limits. This build
is exercised without paid calls unless existing authorization is found.

Proposal is a JSON object:
- question_map: optional list of {id, question, gap, competing_explanation, importance}
- findings: optional list of findings accepted by B below
- next_action: {kind: search|read|finish, reason: string, node_id?: string,
  query?: public string, urls?: list of public URLs, providers?: list}
- stop_reason: optional bounded explanation for finish
Proposals require the inspected case_version; reject stale ones.
A calls B.apply if findings exist, then invokes research.investigate for search/read.
The next reasoning context uses the actual new evidence. All side effects are
reserved/checkpointed; uncertain interrupted requests cannot silently retry.

## B: clearance/studies.py, clearance/synthesis.py, tests/test_studies_synthesis.py

- studies.group(evidence: list) -> list of study dictionaries (stable identity,
  versions, evidence_ids, identity basis; uncertain matches stay separate).
- synthesis.apply(case_id, version, proposal, *, db=None) -> saved case dict.
- synthesis.build(case_data) -> answer dict with case_id, version, conclusions,
  studies, gaps, limits; all interpretations explicitly authored.
- synthesis.compare(case_id, from_version, *, db=None) -> change report.

Finding schema: statement, relation (supports|contradicts|context|unresolved|
 different_scope), rationale, optional evidence_id and exact quote, conditions
(optional list of {field,value,evidence_id,quote}), strongest_challenge and
what_would_change. Require substantial challenge and falsification text for any
non-unresolved finding. Allowed condition fields: task, population, model,
comparator, dataset, metric, budget, study_design, limitations. Conditions must
carry checked source anchors; do not treat free model text as extracted fact.
Unsupported findings must remain unresolved. Store with case claims and preserve
research.brief compatibility; different_scope can use context relation plus an
explicit scope relationship. One atomic case revision per apply, not per finding.
Reject invalid anchors and stale versions without partial writes. Do not modify
existing cases.py/research.py; request coordinator changes if necessary.

## C: clearance/research_cli.py, clearance/research_workflow.py,
clearance/research_protocols.py, tests/test_research_workflow.py, docs/RESEARCH-QUICKSTART.md

- research_cli.add_parser(sub): argparse registration, proposed research command
  family. Coordinator normalizes `research "question"` to start subcommand.
- research_cli.run(args): CLI dispatch.
- research_workflow.handle(arguments: dict) -> JSON-serializable result; shared by
  CLI and new science_research MCP tool. Lazy imports A/B while lanes build.
- research_workflow.follow(case_id, *, db=None) -> record
- research_workflow.updates(*, db=None) -> local changes since followed versions

Actions: start, show, context, resume, cancel, challenge, compare, follow, updates,
experiment-plan. CLI supports --db, --json; MCP never executes experiments.
Use current case version for follow baseline; reading updates must not consume
it or mark web checked. Explicit follow again may acknowledge current version.
Experiment protocols pin hypothesis, case version, repo, tasks, baseline,
intervention, outcome definitions, comparison budget and stopping rule. Required
fields cannot be invented from missing user input. Draft and READY are distinct.
Add a CLI-only execute-protocol path for complete compatible trusted-code plans,
using experiments.compare, with actual result IDs linked to protocols. Never
execute arbitrary scripts received through MCP or source pages.

## Integration

Coordinator alone changes clearance/stack_cli.py and clearance/mcp_server.py,
scripts/full_gate.sh and README.md. Each lane commits complete slices and sends
commit hashes. No push/deploy, no paid research/model calls, no reading or modifying
personal cases during tests. Use private fixture databases. Use pinned source
fixtures as replay data, never label them live. Worktree-specific closeout goes in
review/night/LANE-{A,B,C}.md. Continue the ranked work queue without approval pauses.
