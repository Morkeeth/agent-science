# Research expansion — 2026-09-04

The terminal and MCP can import an existing report, read its original citations, investigate a named gap through Parallel or Perplexity, and retain claim-specific assessments with source quotations. The research brief distinguishes unresolved, supported-as-assessed, contradicted-as-assessed, contested and stale claims. These states describe authored assessments, not a model-independent scientific verdict.

## Interface

- `case import report.md --question "Your research question" --live`: retain a Markdown/text or Sonar JSON report and inspect its citations. Defaults to 12 documents, configurable up to 40; unread citations remain visible.
- `case investigate CASE_ID --version N --query "Public follow-up query" --provider parallel --provider perplexity --live`: append evidence without replacing earlier findings. Results per provider are bounded to 1–10.
- `case investigate CASE_ID --version N --source URL --live`: read an unread citation directly or recheck a source, without a discovery request.
- `case source`, `case assess`, `case brief`: inspect a snapshot, record a claim-specific interpretation with an exact quote and rationale, and see agreement, disagreement and open questions.
- `case report`: read the retained original report with version and pagination metadata.
- `case refresh`, `case review`: revisit sources and identify affected assessments and decisions. Historical versions remain available.

The `science_case` MCP tool exposes the same actions. Import takes inline report_text; it does not give a remote caller a new arbitrary file-reading interface. Local report contents and repo contents are never automatically submitted to discovery queries. The original report is omitted from routine tool output.

## Verification

The focused regression command covers research expansion, the terminal workflow, evidence cases, hosted API/pages and the browser. Its 70 tests passed. Research checks include real CLI and stdio MCP processes, support/contradiction states, fabricated quotes, historical views, stale writes and concurrent revisions, stale-assessment review, supersession, source-read budgets and provider deduplication.

The Perplexity adapter was checked against the official Search API reference retrieved on 2026-09-04. Transport fixtures exercise the documented results array, request body, headers, missing credentials and HTTP failures. This is contract testing, not a live Perplexity search measurement.

A real CLI flow fetched the current Perplexity API reference, inspected its source text, recorded a supported-as-assessed claim and retrieved the original report unchanged. The saved result is `review/acceptance/research-live-source-20260904.json`. The report was a deliberately small API documentation check, not the user's unidentified Perplexity research report and not a scientific effectiveness study. Its case and source snapshots remain in a private local store.

Perplexity credentials are absent in this environment. The real investigate command recorded an unavailable provider with the missing-key reason. No live Perplexity success, search cost or research-quality improvement is claimed. Set PERPLEXITY_API_KEY or the documented local key file to enable it.

## Limits

Import extracts report passages and explicit citation mappings, not atomic semantic claims. Assessment requires a user or agent to read and explain the evidence; exact quotation checks alone cannot prove entailment. There is no automatic paper citation-graph traversal or statistical synthesis in this slice. Existing lookup/visibility routing is unchanged. Perplexity has no local result cache yet, and provider billing is not inferred from request counts. The complete hosted/deployment gate was not run; this slice changes local CLI/MCP research workflows.


## Independent review and field use

Cursor and Fable independently exercised CLI and stdio MCP flows using temporary reports and stores. They verified historical views, supersession, quote guards and source privacy. Their concrete findings led to fixes for Parallel SDK exceptions, incomplete Perplexity responses, reference titles/labels/parenthesized URLs, missing-version errors and private case-search receipts. Search cache writes are atomic; Parallel SDK automatic retries are disabled. Regression tests cover the provider failures and parsing cases.

The subsequent field pass used the user's full agentic-science scope: memory/context, retrieval, agent UX and multi-agent coordination. Six actual Parallel searches led to primary-paper assessments with applicability limits, saved in the default local case store. See `research-inbox/2026-09-05-agentic-science-field-pass.md`. These are authored interpretations of retrieved studies, not measurements of this product's quality.

The field pass also exercised actual PDF extraction. PDF bytes are now parsed by a separate worker with timeout, input/page/text limits, and a pinned pypdf dependency. Legacy caches containing undecoded PDF bytes are not reused as source text. A live arXiv paper was re-read successfully after the change. The catalog lookup now restricts practitioner hits to the practitioner table rather than treating internal coaching rows as source records.

Final checks also passed all six Parallel integration checks and five visibility checks. The focused research suite includes transport continuation, private receipt storage, PDF extraction and catalog provenance controls.
