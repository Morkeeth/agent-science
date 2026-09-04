# Hosted evidence cases — build receipt

Recorded 2026-09-04T21:16:19.369748+00:00.

## Released behavior

The private hosted workspace connects a question to saved source text, an authored decision, a refresh, and a review of what changed. A superseding decision clears the earlier active review flag while keeping its reasoning and evidence version. Source reading and older case pages are paginated. Repository uploads and experiments remain local.

Cloud Run revision **agent-science-00026-zel** serves the public service. Its runtime source is **0363a54**; the source archive retrieved from the actual revision contains **61 files**, each byte-equal to that commit. Image SHA-256: `44de8def36c19f784be8d4bc2be5657c017107363658f45449b0f63191e47d58`.

Deployment first created a no-traffic candidate. Cloud acceptance passed before that exact revision received 100% of traffic. The upload allowlist excludes local databases, caches, research notes and media. No existing local case store was seeded into the cloud.

## Evidence collected

- **89 focused tests passed**, plus 27 subtests. This covers case integrity, public-source boundaries, storage, authentication, native forms and versioned decisions. These are software checks, not a measure of research quality.
- Native Chromium completed sign-in, source reading, decision creation, a source change, supersession and sign-out at 390px. The negative referrer-policy control made the actual browser send `Origin: null` and the server reject the form with 403. Normal same-origin forms passed.
- On Cloud Run, a real public documentation case was saved, reopened from GCS, read in three source pages, checked against its content hash, cited and superseded. Foreign-workspace reads and stale decision submissions were rejected.
- Native browser discovery on the final candidate completed **3 actual Parallel calls**, fetched **4 documents**, and located **3 quotations**. No research-repository or declared-official coverage was established in that discovery case. Quote occurrence does not establish support or applicability.
- An actual GCS stale writer was rejected. A fresh read retained the winning case. Only the uniquely named acceptance object was then removed, with its generation precondition.
- The live canonical and legacy service addresses were checked after promotion. The operator access key signs into a separate empty workspace; release-check cases are not mixed into it.

Command used for the focused run:

```bash
python3 -m pytest -q tests/test_hosted_browser.py tests/test_hosted_flow.py tests/test_hosted_case_pages.py tests/test_case_storage.py tests/test_evidence_cases.py tests/test_refresh_sources.py tests/test_evidence_integrity.py tests/test_safe_sources.py
```

The browser test requires the optional Playwright package and Chromium. Runtime requirements remain in `requirements.txt`.

## Review and limits

Cursor and Fable reviewed the hosted request, authentication, worker, storage and deployment paths. Their native-form finding was resolved and reproduced as a failing browser control. A separate final origin review rejected missing, null, attacker and suffix-spoofed origins while accepting only the configured canonical and candidate origins.

Storage uses [Cloud Storage generation preconditions](https://docs.cloud.google.com/storage/docs/request-preconditions). The referrer choice follows the [Fetch Origin-header algorithm](https://fetch.spec.whatwg.org/#append-a-request-origin-header); external source links additionally use `noreferrer`.

Configured daily limits are 10 live research runs per workspace, 50 service-wide, 100 writes per workspace and 1,000 service-wide. They are request ceilings, not dollar measurements. Failed admitted attempts count; durable request reservations prevent duplicate work across day changes. Research workers stop after 180 seconds. The default workspace cap is 64 MiB; storage-full responses name the limit condition and require an operator capacity change.

Concurrent writes to the same workspace can return 409 after research. The losing result is not saved and its admitted attempt remains counted. The service does not merge conflicting histories or replay paid work automatically. Cases refresh on request; there is no scheduled source monitor. Login uses private access tokens, not public self-registration.
