# Long run receipt — Agent Science · 2026-08-31

**Stamp:** 2026-08-31T11:21:39Z UTC  
**URL:** https://agent-science-568004190078.us-central1.run.app  
**Subject:** `longrun-0831-1321`  
**Log:** `/tmp/agent-science-longrun-60422.log`

## Summary

**19/19 checks PASS** · revision `agent-science-00014-p56` · **27 queries logged** · hit rate **0.74**

| Compound | Run A | Run B |
|----------|-------|-------|
| Parallel API | 0 | 0 |
| Corpus hits | 0 | **1** |
| Engine | adk | adk |

Warm dictionary: both runs 0 Parallel; Run B **corpus_hits=1** proves shelf reuse (goal met).

First run of session (`longrun-0831-1320`): A=**1** Parallel → B=**0** Parallel, corpus_hits=1 — classic compound drop.

## Goal

Truth dictionary stranger path: free lookup first, compound on repeat, honest miss, registry grows.

## Results

| Gate | Result |
|------|--------|
| Local controls | watch_it_go_red + dictionary/routing/popular/partner |
| Hosted health | `engine_default: adk`, Parallel + Gemini |
| Free tier | `2012/28/EU` + `Directive 2012/28/EU` SOURCED, 0 Parallel |
| NOT_CLEARED | miss returns `next_step` |
| Compound A/B | subject `longrun-0831-1321` — see log |
| Surfaces | /, /registry, /popular/ui, /stats |

## Stats delta

```json
before: {
 "n": 183,
 "cleared": 30,
 "refused": 153,
 "reuses": 9,
 "productions": 6,
 "queries_logged": 26,
 "queries_answered": 19,
 "queries_not_cleared": 7,
 "dictionary_hit_rate": 0.731,
 "aliases": 8,
 "db": "/tmp/refusal_log.db",
 "recent_queries": [
  {
   "id": 26,
   "query_text": "xyzzy-nonexistent-claim-99999",
   "result_label": "NOT_CLEARED",
   "verdict": null,
   "cause": "not_in_registry",
   "term": null,
   "citation_url": null,
   "quoted_terms": null,
   "resolves_with": null,
   "asked_at": "2026-08-31T11:21:52+00:00",
   "cost_tier": "free",
   "source": "dictionary_miss"
  },
  {
   "id": 25,
   "query_text": "xyzzy-nonexistent-claim-99999",
   "result_label": "NOT_CLEARED",
   "verdict": null,
   "cause": "not_in_registry",
   "term": null,
   "citation_url": null,
   "quoted_terms": null,
   "resolves_with": null,
   "asked_at": "2026-08-31T11:21:52+00:00",
   "cost_tier": null,
   "source": null
  },
  {
   "id": 24,
   "query_text": "Directive 2012/28/EU",
   "result_label": "SOURCED",
   "verdict": "GREEN",
   "cause": null,
   "term": "directive 2012/28/eu of the european parliament and of the council of 25 october",
   "citation_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028",
   "quoted_terms": "Legal act \u200b Directive 2012/28/EU of the European Parliament and of the Council of 25 October 2012 on certain permitted uses of orphan works Text with EEA relevance Directive 2012/28/EU of the European Parliament and of the",
   "resolves_with": null,
   "asked_at": "2026-08-31T11:21:52+00:00",
   "cost_tier": "free",
   "source": "dictionary_exact"
  },
  {
   "id": 23,
   "query_text": "2012/28/EU",
   "result_label": "SOURCED",
   "verdict": "GREEN",
   "cause": null,
   "term": "directive 2012/28/eu of the european parliament and of the council of 25 october",
   "citation_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028",
   "quoted_terms": "Legal act \u200b Directive 2012/28/EU of the European Parliament and of the Council of 25 October 2012 on certain permitted uses of orphan works Text with EEA relevance Directive 2012/28/EU of the European Parliament and of the",
   "resolves_with": null,
   "asked_at": "2026-08-31T11:21:51+00:00",
   "cost_tier": "free",
   "source": "dictionary_exact"
  },
  {
   "id": 22,
   "query_text": "2012",
   "result_label": "SOURCED",
   "verdict": "GREEN",
   "cause": null,
   "term": "directive 2012/28/eu of the european parliament and of the council of 25 october",
   "citation_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028",
   "quoted_terms": "Legal act \u200b Directive 2012/28/EU of the European Parliament and of the Council of 25 October 2012 on certain permitted uses of orphan works Text with EEA relevance Directive 2012/28/EU of the European Parliament and of the",
   "resolves_with": null,
   "asked_at": "2026-08-31T11:21:51+00:00",
   "cost_tier": null,
   "source": null
  },
  {
   "id": 21,
   "query_text": "xyzzy-nonexistent-claim-99999",
   "result_label": "NOT_CLEARED",
   "verdict": null,
   "cause": "not_in_registry",
   "term": null,
   "citation_url": null,
   "quoted_terms": null,
   "resolves_with": null,
   "asked_at": "2026-08-31T11:20:30+00:00",
   "cost_tier": "free",
   "source": "dictionary_miss"
  },
  {
   "id": 20,
   "query_text": "xyzzy-nonexistent-claim-99999",
   "result_label": "NOT_CLEARED",
   "verdict": null,
   "cause": "not_in_registry",
   "term": null,
   "citation_url": null,
   "quoted_terms": null,
   "resolves_with": null,
   "asked_at": "2026-08-31T11:20:30+00:00",
   "cost_tier": null,
   "source": null
  },
  {
   "id": 19,
   "query_text": "Directive 2012/28/EU",
   "result_label": "SOURCED",
   "verdict": "GREEN",
   "cause": null,
   "term": "directive 2012/28/eu of the european parliament and of the council of 25 october",
   "citation_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028",
   "quoted_terms": "Legal act \u200b Directive 2012/28/EU of the European Parliament and of the Council of 25 October 2012 on certain permitted uses of orphan works Text with EEA relevance Directive 2012/28/EU of the European Parliament and of the",
   "resolves_with": null,
   "asked_at": "2026-08-31T11:20:30+00:00",
   "cost_tier": "free",
   "source": "dictionary_exact"
  },
  {
   "id": 18,
   "query_text": "2012/28/EU",
   "result_label": "SOURCED",
   "verdict": "GREEN",
   "cause": null,
   "term": "directive 2012/28/eu of the european parliament and of the council of 25 october",
   "citation_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028",
   "quoted_terms": "Legal act \u200b Directive 2012/28/EU of the European Parliament and of the Council of 25 October 2012 on certain permitted uses of orphan works Text with EEA relevance Directive 2012/28/EU of the European Parliament and of the",
   "resolves_with": null,
   "asked_at": "2026-08-31T11:20:29+00:00",
   "cost_tier": "free",
   "source": "dictionary_exact"
  },
  {
   "id": 17,
   "query_text": "2012/28/EU",
   "result_label": "SOURCED",
   "verdict": "GREEN",
   "cause": null,
   "term": "directive 2012/28/eu of the european parliament and of the council of 25 october",
   "citation_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028",
   "quoted_terms": "Legal act \u200b Directive 2012/28/EU of the European Parliament and of the Council of 25 October 2012 on certain permitted uses of orphan works Text with EEA relevance Directive 2012/28/EU of the European Parliament and of the",
   "resolves_with": null,
   "asked_at": "2026-08-31T11:16:54+00:00",
   "cost_tier": "free",
   "source": "dictionary_exact"
  }
 ]
}
after:  {
 "n": 183,
 "cleared": 30,
 "refused": 153,
 "reuses": 11,
 "productions": 6,
 "queries_logged": 27,
 "queries_answered": 20,
 "queries_not_cleared": 7,
 "dictionary_hit_rate": 0.741,
 "aliases": 8,
 "db": "/tmp/refusal_log.db",
 "recent_queries": [
  {
   "id": 27,
   "query_text": "2012",
   "result_label": "SOURCED",
   "verdict": "GREEN",
   "cause": null,
   "term": "directive 2012/28/eu of the european parliament and of the council of 25 october",
   "citation_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028",
   "quoted_terms": "Legal act \u200b Directive 2012/28/EU of the European Parliament and of the Council of 25 October 2012 on certain permitted uses of orphan works Text with EEA relevance Directive 2012/28/EU of the European Parliament and of the",
   "resolves_with": null,
   "asked_at": "2026-08-31T11:22:07+00:00",
   "cost_tier": null,
   "source": null
  },
  {
   "id": 26,
   "query_text": "xyzzy-nonexistent-claim-99999",
   "result_label": "NOT_CLEARED",
   "verdict": null,
   "cause": "not_in_registry",
   "term": null,
   "citation_url": null,
   "quoted_terms": null,
   "resolves_with": null,
   "asked_at": "2026-08-31T11:21:52+00:00",
   "cost_tier": "free",
   "source": "dictionary_miss"
  },
  {
   "id": 25,
   "query_text": "xyzzy-nonexistent-claim-99999",
   "result_label": "NOT_CLEARED",
   "verdict": null,
   "cause": "not_in_registry",
   "term": null,
   "citation_url": null,
   "quoted_terms": null,
   "resolves_with": null,
   "asked_at": "2026-08-31T11:21:52+00:00",
   "cost_tier": null,
   "source": null
  },
  {
   "id": 24,
   "query_text": "Directive 2012/28/EU",
   "result_label": "SOURCED",
   "verdict": "GREEN",
   "cause": null,
   "term": "directive 2012/28/eu of the european parliament and of the council of 25 october",
   "citation_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028",
   "quoted_terms": "Legal act \u200b Directive 2012/28/EU of the European Parliament and of the Council of 25 October 2012 on certain permitted uses of orphan works Text with EEA relevance Directive 2012/28/EU of the European Parliament and of the",
   "resolves_with": null,
   "asked_at": "2026-08-31T11:21:52+00:00",
   "cost_tier": "free",
   "source": "dictionary_exact"
  },
  {
   "id": 23,
   "query_text": "2012/28/EU",
   "result_label": "SOURCED",
   "verdict": "GREEN",
   "cause": null,
   "term": "directive 2012/28/eu of the european parliament and of the council of 25 october",
   "citation_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028",
   "quoted_terms": "Legal act \u200b Directive 2012/28/EU of the European Parliament and of the Council of 25 October 2012 on certain permitted uses of orphan works Text with EEA relevance Directive 2012/28/EU of the European Parliament and of the",
   "resolves_with": null,
   "asked_at": "2026-08-31T11:21:51+00:00",
   "cost_tier": "free",
   "source": "dictionary_exact"
  },
  {
   "id": 22,
   "query_text": "2012",
   "result_label": "SOURCED",
   "verdict": "GREEN",
   "cause": null,
   "term": "directive 2012/28/eu of the european parliament and of the council of 25 october",
   "citation_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028",
   "quoted_terms": "Legal act \u200b Directive 2012/28/EU of the European Parliament and of the Council of 25 October 2012 on certain permitted uses of orphan works Text with EEA relevance Directive 2012/28/EU of the European Parliament and of the",
   "resolves_with": null,
   "asked_at": "2026-08-31T11:21:51+00:00",
   "cost_tier": null,
   "source": null
  },
  {
   "id": 21,
   "query_text": "xyzzy-nonexistent-claim-99999",
   "result_label": "NOT_CLEARED",
   "verdict": null,
   "cause": "not_in_registry",
   "term": null,
   "citation_url": null,
   "quoted_terms": null,
   "resolves_with": null,
   "asked_at": "2026-08-31T11:20:30+00:00",
   "cost_tier": "free",
   "source": "dictionary_miss"
  },
  {
   "id": 20,
   "query_text": "xyzzy-nonexistent-claim-99999",
   "result_label": "NOT_CLEARED",
   "verdict": null,
   "cause": "not_in_registry",
   "term": null,
   "citation_url": null,
   "quoted_terms": null,
   "resolves_with": null,
   "asked_at": "2026-08-31T11:20:30+00:00",
   "cost_tier": null,
   "source": null
  },
  {
   "id": 19,
   "query_text": "Directive 2012/28/EU",
   "result_label": "SOURCED",
   "verdict": "GREEN",
   "cause": null,
   "term": "directive 2012/28/eu of the european parliament and of the council of 25 october",
   "citation_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028",
   "quoted_terms": "Legal act \u200b Directive 2012/28/EU of the European Parliament and of the Council of 25 October 2012 on certain permitted uses of orphan works Text with EEA relevance Directive 2012/28/EU of the European Parliament and of the",
   "resolves_with": null,
   "asked_at": "2026-08-31T11:20:30+00:00",
   "cost_tier": "free",
   "source": "dictionary_exact"
  },
  {
   "id": 18,
   "query_text": "2012/28/EU",
   "result_label": "SOURCED",
   "verdict": "GREEN",
   "cause": null,
   "term": "directive 2012/28/eu of the european parliament and of the council of 25 october",
   "citation_url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32012L0028",
   "quoted_terms": "Legal act \u200b Directive 2012/28/EU of the European Parliament and of the Council of 25 October 2012 on certain permitted uses of orphan works Text with EEA relevance Directive 2012/28/EU of the European Parliament and of the",
   "resolves_with": null,
   "asked_at": "2026-08-31T11:20:29+00:00",
   "cost_tier": "free",
   "source": "dictionary_exact"
  }
 ]
}
```

## Run A / B (truncated)

```json
{
    "ok": true,
    "subject": "longrun-0831-1321",
    "extractor": "gemini-3.5-flash (vertex:hack-fleet)",
    "locator": "gemini-3.5-flash",
    "claims_extracted": 1,
    "sourced": 0,
    "unsourced": 1,
    "parallel_calls": 0,
    "parallel_api_calls": 0,
    "prior_run": null,
    "corpus_hits": 0,
    "log_hits": 1,
    "log_size": 183,
    "corpus_remembered": 1,
    "rows": [
        {
            "reused_from": null,
            "claim_id": "C1",
            "text": "The Orphan Works Directive is Directive 2012/28/EU.",
            "label": "UNVERIFIED INDEPENDENCE",
            "engine_verdict": "UNKNOWN",
            "cause": "no_independent_source",
            "reason": "log_hit (cross-subject) \u2014 established in production 'longrun-0831-1320'",
            "why": "documents state this, and every one traces to a derived or unclassified origin \u2014 a human must judge whether that is independent support",
            "citation_url": null,
            "quoted_terms": null,
            "source_class": null,
            "source_note": null,
            "corpus_hit": true,
            "probe": "log_hit",
            "cross_subject": true
        }
    ],
    "markdown": "# GAP REPORT \u2014 subject `longrun-0831-1321`\n\n| Claims | 1 |\n| SOURCED | 0 (0%) |\n| UNSOURCED | 1 (100%) |\n| Claims searched (no corpus/log hit) | 0 |\n| Parallel API calls (metered) | 0 |\n| Corpus hits (same subject) | 0 |\n| Log hits (cross subject) | 1 |\n| Remembered on this subject | 1 |\n| Claims established across all subjects | 183 |\n\n**1 claim(s) reused from ANOTHER subject's clearance \u2014 no Parallel call.** A claim proven (or proven-unprovable) once is free for every subject afterward; that is the cross-production moat.\n\n## Claims requiring action\n\n- **C1** \u2014 UNVERIFIED INDEPENDENCE (no_independent_source)\n  documents state this, and every one traces to a derived or unclassified origin \u2014 a human must judge whether that is independent support\n",
    "engine": "adk",
    "adk_version": "2.7.1",
    "model_routing": "vertex:hack-fleet",
    "adk_tool_calls": [
        "clear_script_tool"
```

```json
{
    "ok": true,
    "subject": "longrun-0831-1321",
    "extractor": "gemini-3.5-flash (vertex:hack-fleet)",
    "locator": "gemini-3.5-flash",
    "claims_extracted": 1,
    "sourced": 0,
    "unsourced": 1,
    "parallel_calls": 0,
    "parallel_api_calls": 0,
    "prior_run": {
        "at": "2026-08-31T11:21:57+00:00",
        "claims": 1,
        "corpus_hits": 0,
        "parallel_api_calls": 0
    },
    "corpus_hits": 1,
    "log_hits": 0,
    "log_size": 183,
    "corpus_remembered": 1,
    "rows": [
        {
            "reused_from": null,
            "claim_id": "C1",
            "text": "Directive 2012/28/EU is the EU orphan works law.",
            "label": "UNVERIFIED INDEPENDENCE",
            "engine_verdict": "UNKNOWN",
            "cause": "no_independent_source",
            "reason": "corpus_hit \u2014 log_hit (cross-subject) \u2014 established in production 'longrun-0831-1320'",
            "why": "documents state this, and every one traces to a derived or unclassified origin \u2014 a human must judge whether that is independent support",
            "citation_url": null,
            "quoted_terms": null,
            "source_class": null,
            "source_note": null,
            "corpus_hit": true,
            "probe": "corpus_hit"
        }
    ],
    "markdown": "# GAP REPORT \u2014 subject `longrun-0831-1321`\n\n| Claims | 1 |\n| SOURCED | 0 (0%) |\n| UNSOURCED | 1 (100%) |\n| Claims searched (no corpus/log hit) | 0 |\n| Parallel API calls (metered) | 0 |\n| Corpus hits (same subject) | 1 |\n| Log hits (cross subject) | 0 |\n| Remembered on this subject | 1 |\n| Claims established across all subjects | 183 |\n\n**1 claim(s) resolved from corpus \u2014 no Parallel call.** That is the second-production cost collapse.\n\n## Claims requiring action\n\n- **C1** \u2014 UNVERIFIED INDEPENDENCE (no_independent_source)\n  documents state this, and every one traces to a derived or unclassified origin \u2014 a human must judge whether that is independent support\n",
    "engine": "adk",
```

## Pass/fail

- **Checks passed:** 19 (updated at end of script)
- **Command to replay:** `bash scripts/long_run_goal.sh`
- **Stranger one-liner:** `bash scripts/new_user_trial.sh`

