# Context runner: independent review and disposition

Cursor and Fable reviewed immutable `526bd881ba41b1a14bec323ff9d948ffe1de5d5a`
against `06a2beec614ad5eb1646e7bca2952cae61b9cac0`. They used synthetic temporary
Git repositories and explicit temporary case databases. Their baseline suite
passed while their separate reproducers demonstrated concrete defects. Review
agreement is not counted as an additional test or a measure of truth.

Fix source: `eb6d68fb231f68b9c452de21ade1b2d5722721d2`.
Integrated fix: `1dc7c3ca9fca1ca88b41c0d6037a48a0d5e31c57`.

## Exercised changes

- A later descendant commit cannot count as the host's fix: exact base HEAD is
  required. Assigned untracked AGENTS.md cannot defeat the no-change control.
- Malformed Git references produce named CLI/MCP errors, not a dead MCP process.
  Missing acceptance hashes, non-integer protocol versions and unusable or excessive
  policies are rejected before preparation.
- Interleaved preparations retain their own attempt IDs. Cancellation cannot become
  UNKNOWN when preparation returns. Concurrent identical patch results flag both
  records without excluding legitimate convergence from the denominator.
- An abandoned CHECKING attempt can close as REVIEW_REQUIRED, with unknown external
  outcome and no retry, capacity refund or success inference.
- Isolated Python startup prevents the reproduced pathlib/sitecustomize shadow
  attacks. Bytecode uses an external cache prefix. Ignored source files are captured;
  normal import bytecode cannot invalidate an otherwise valid submitted fix.
- Captured patch and untracked artifact modifications during acceptance invalidate
  the result, even if the selected script exits zero.

The 20 added control cases in `tests/test_context_trial_review_controls.py`
exercise these failures against real temporary objects and subprocesses. Together
with the original runner and CLI/MCP tests: **31 passed in 11.23s** on the integrated
fix plus the case-result lookup. The broader local research suite passed **270 tests
and 16 subtests in 29.46s**. These are behavioral controls, not context-effect results.

## Trial applicability and remaining limits

The native-host pilot remained at its original runner pin throughout execution.
It did not switch implementation after an observed outcome. Its workers were told
to leave changes uncommitted and to avoid other worktrees/history; source fixes
from these attempts are not merged into the product. Selected task failures remain
failures. Separate post-review acceptance replay checks the preserved submitted
patches with the corrected launcher and reports any changed verdict; it is not a
new host repetition or a replacement for the original receipt.

Worktrees share a Git object database. Fresh-context isolation and model identity
are not independently attested. Host traces are conversation records; no claim of
complete audited tool-use provenance is made. The runner is not a sandbox against
arbitrary malicious repository imports. The explicit CLI acknowledgement is the
operator's trust decision; MCP creation can propose limits and copy local inputs,
but cannot execute checks. Elapsed host lease includes coordinator delay. Tokens,
billing and pure model latency remain unknown.

Full reviewer outputs and reproductions remain outside Git. Source review and
runner review are separate; neither validates exhaustive research recall or causal
scientific conclusions.
