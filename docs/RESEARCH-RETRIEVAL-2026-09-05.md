# Saved research in the daily CLI/MCP flow

A broad ask could miss the exact dictionary even when a useful study was saved in a case. Case list filtering searched only a full substring of the question. The new `case find` command searches questions, claims and active assessment rationales. Personal visibility includes the same results; MCP exposes `science_case` action `find`.

Matches show literal terms and explicit topic expansions. Ranking does not assign scientific confidence or change claim states. The result retains opposing and stale assessments, authored limits, source links, saved repository scope and a version-pinned inspection action. Custom database references remain attached to that action. Source snapshots and original report bodies are not searched. Five claims per result are selected by relevance; brief retains the complete history.

The workflow is: find prior work, inspect the evidence and its limits, investigate a remaining gap, then select a trusted acceptance script for a pinned repository comparison. This change does not run agent-quality experiments or turn proposed tests into results.

## Validation

- 88 focused tests passed across saved research retrieval, report research, terminal cases, evidence cases and hosted boundaries.
- Five visibility transparency tests and six Parallel integration checks passed.
- Twelve manual local retrieval checks used the four actual saved field-pass cases: eight topic queries selected the intended case first; four unrelated queries returned no results. These are a small acceptance set, not a general retrieval benchmark. The private receipt stays outside git at the local Agent Science data location.
- A real `visibility "RAG for my repo" --json` run returned the saved retrieval case alongside `NOT_CLEARED` from the dictionary. No paid provider call was requested.
- Tests exercised CLI and stdio MCP, unreadable case storage, exact root filtering, pagination, superseded and stale assessments, and the `personal=False` boundary.
- Privacy scan after staging: zero matches across 368 tracked files.

The retrieval engine scans saved case revisions and uses a fixed topic vocabulary. It is not embedding search, does not inspect source bodies and does not establish that a finding applies to the current repository. A missing result means no local match, not no research in the world.

## Independent review

Cursor and Fable each exercised the CLI and stdio MCP with isolated fixture databases. Their checks covered pagination, latest versions, exact root matching, stale and superseded assessments, selected source quotes, and private visibility. Findings led to explicit MCP page-size descriptions and conflict rejection, consistent visibility root filtering, clear literal/topic labels, narrower topic phrases, missing-root errors, and a specific-keyword error for queries with no searchable terms. Regression tests cover these paths. Selected assessment quotations remain intentional output; unselected source text does not enter search results.
