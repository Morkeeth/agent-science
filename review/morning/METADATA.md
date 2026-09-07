# Primary source metadata lane — 2026-09-05

Base: `ea05a10`. Branch: `build/science-metadata-20260905`.

Built `clearance/source_metadata.py`: `inspect(evidence, live=False)` and trusted-local `apply(case_id, version, evidence_id, metadata, db=...)`. The coordinator owns command/run integration and correction review rendering.

The inspector makes at most two fixed-endpoint GETs: exact Crossref DOI and current arXiv identifier. No search/model calls, redirects or retries. Responses have a 2 MB limit and 20 second socket timeout. arXiv requests have at least three seconds between starts within this process; independent processes require caller coordination. An error records its outcome; only received responses advance metadata timestamps. Oversized-response hashes explicitly identify a bounded prefix.

Crossref incoming `updated-by` retractions affect the exact source identity. Outgoing `update-to` relations identify notices about another work and do not retract the notice. Corrections and expressions of concern require review without declaring a retraction. Citation references and prose cannot trigger these state changes. arXiv latest versions supersede only an explicitly pinned earlier source version; unversioned sources retain an unknown snapshot version. No source-body hash or source-body checked timestamp changes. Historical cases stay readable; absent metadata never clears an earlier flag.

The apply function is for the result of a local inspector call. It must not be exposed as an API accepting model-authored registry metadata. Registry metadata itself is not cryptographic proof and can be incomplete or incorrect.

## Actual verification

`python3 -m pytest tests/test_source_metadata.py tests/test_studies_synthesis.py -q`

Result: **44 passed, 2 subtests passed**. Fourteen new metadata tests exercise offline/missing access, exact identity mismatch, ambiguous identifiers, retraction direction, corrections, history and stale writes, absent metadata retaining flags, arXiv version scope, ignored malicious instructions, XML declarations, redirect rejection, HTTP error receipts, maximum calls and size rejection.

Two free primary-registry checks completed at 2026-09-05 08:31 UTC:

- Crossref `10.1021/am300292v`: HTTP 200, incoming retraction from `10.1021/acsami.9b11759`, source `retraction-watch`. Response SHA-256 `89a5cd2aabdd08d96580348f705328bae3ac80aac944f3d4c22362e685c97954`.
- arXiv `1706.03762v1`: HTTP 200, current entry `1706.03762v7`, updated 2023-08-02. Response SHA-256 `7616bf1bea0810481b6dab31a43dc9a580a30c620c6106e5527b3e26ffbb5148`.

Full inspector receipts are outside Git. These checks validate endpoint handling and known relations, not universal retraction coverage or a scientific conclusion about the papers. Correction handling used fixtures; no live correction lookup was measured. No private case database, paid API, deployment or push was used.

## Primary documentation

Crossref documents update metadata and publisher/Retraction Watch provenance in its [Retraction Watch documentation](https://www.crossref.org/documentation/retrieve-metadata/retraction-watch/) and [API format](https://github.com/CrossRef/rest-api-doc/blob/master/api_format.md). The [arXiv API manual](https://info.arxiv.org/help/api/user-manual.html) documents Atom entries, exact IDs and version behavior. The implementation reads only structured identity/relation/version fields; abstracts, titles and page instructions have no execution authority.
