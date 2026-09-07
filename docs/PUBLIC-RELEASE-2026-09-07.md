# Public release contract · 7 September

The public root and `/judge` expose a pure source-hostname check using the actual classifier. It does not fetch a URL, call a model, retain a case or inspect a workspace. Legacy GET routes `/clear`, `/front`, `/visibility/ui` and `/truths/ui` explain that those research surfaces are local-only. Private `/cases` and `/api/cases` remain authenticated; anonymous mutations remain refused.

The PRIMARY result is a hostname hint, never proof of authorship, independence, freshness or entailment. Domain matching now uses parsed hostname boundaries, not arbitrary substrings, user-info, ports or paths. `example.gov.attacker.invalid` is unclassified. Real publisher subdomains, case-insensitive names and trailing DNS dots remain supported. Malformed and non-HTTP(S) source URLs are unclassified.

Source authority beyond a hostname is still a product gap. A third-party document hosted on a government domain is not automatically authoritative; this release names the limitation rather than pretending it solved attribution.

States must stay separate: local candidate; merged/pushed default branch; hosted revision; judge functional acceptance; completed submission. No deployment, hosted provider validation, public video upload or submission was performed by this patch.

Cold acceptance: public entry works without access/config lookup; anonymous method check refuses a deceptive hostname; no private store/research call is made; `/api/cases` and POST `/clear` still refuse anonymous users; an authenticated workspace's existing tests pass. See `tests/test_hosted_flow.py` and `tests/test_authority_hostname_boundary.py`.

The public `/judge/demo` is an authored, read-only research example with two real document excerpts, fetched timestamps and raw-document hashes. It uses only `cloud/public_demo.json`, not the workspace, research cache or any provider. Source inspection and comparison are linked and revisitable. No live search/model run or automated entailment is claimed. It is a reviewable public evidence interaction, not complete judge acceptance of the live research workflow.
