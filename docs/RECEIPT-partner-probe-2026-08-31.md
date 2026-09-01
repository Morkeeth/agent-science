# Partner probe receipt

**At:** 2026-08-31T14:05:36.859346+00:00

## Manifest

```json
{
  "event": "Agentic Cinema",
  "track": "Parallel",
  "partners": {
    "gemini_vertex": {
      "role": "claim extraction + passage locate",
      "module": "clearance/gemini.py",
      "runtime": true,
      "gemini_path": "vertex:none",
      "secret_manager": false,
      "notes": "Vertex ADC on Cloud Run; API key local dev only"
    },
    "parallel": {
      "partner": "parallel",
      "track_requirement": "Search API at runtime via parallel-web SDK or REST",
      "sdk_package": "parallel-web",
      "sdk_installed": true,
      "sdk_version": "1.3.2",
      "transport": "parallel-web",
      "endpoint": "https://api.parallel.ai/v1/search",
      "live_calls": 0,
      "last_search_id": null,
      "receipts_log": "agent-science/cache/search_receipts.jsonl",
      "runtime": false,
      "module": "clearance/search.py",
      "called_from": "clearance/facts.py \u2192 judge_claim"
    },
    "google_cloud": {
      "role": "Cloud Run desk + GCS corpus shelf",
      "module": "cloud/service.py",
      "deploy": "deploy.sh",
      "corpus_gcs": null,
      "refusal_log_gcs": null
    },
    "agent_builder_adk": {
      "role": "default /clear engine",
      "module": "cloud/agent.py",
      "package": "google-adk",
      "version": "2.7.1",
      "importable": true,
      "engine_default": "adk",
      "tool": "clear_script_tool"
    }
  },
  "track_checklist": {
    "parallel_search_at_runtime": true,
    "parallel_web_sdk": true,
    "gemini_at_runtime": true,
    "adk_agent_builder": true,
    "hosted_url_required": true
  },
  "receipts": [
    "docs/PARTNER-INTEGRATIONS-2026-08-30.md",
    "docs/PARTNER-INTEGRATION-RESEARCH-2026-08-31.md",
    "docs/RECEIPT-adk-default-path-2026-08-30.md"
  ],
  "repo_root": "agent-science"
}
```

## Live Parallel

```json
{
  "partner": "parallel",
  "track_requirement": "Search API at runtime via parallel-web SDK or REST",
  "sdk_package": "parallel-web",
  "sdk_installed": true,
  "sdk_version": "1.3.2",
  "transport": "parallel-web",
  "endpoint": "https://api.parallel.ai/v1/search",
  "live_calls": 0,
  "last_search_id": null,
  "receipts_log": "agent-science/cache/search_receipts.jsonl",
  "key_present": true,
  "live_probe": {
    "ok": true,
    "n_candidates": 3,
    "search_id": "search_142d9170731a0a9036468d323a868bc5",
    "calls": 1,
    "transport": "parallel-web",
    "urls": [
      "https://en.wikipedia.org/wiki/Orphan_Works_Directive",
      "https://eur-lex.europa.eu/eli/dir/2012/28/oj/eng",
      "https://digital-strategy.ec.europa.eu/en/library/report-application-orphan-works-directive"
    ]
  }
}
```

## ADK

```json
{
  "importable": true,
  "version": "2.7.1"
}
```
