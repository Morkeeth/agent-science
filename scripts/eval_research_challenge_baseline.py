#!/usr/bin/env python3
"""Compare adaptive challenge vs naive fixed-search baseline (offline fixtures).

Re-derives every number at the object. A result where the naive arm wins is a finding.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clearance import cases, instruments, research, research_run

SUPPORT = 'https://example.org/fresh-sessions-help'
CONTRARY = 'https://example.net/fresh-sessions-fail'
SUPPORT_TEXT = (
    'Fresh agent sessions reduced the number of repeated errors in our maintenance experiment. '
    'Limitation: the result may not generalize beyond Python repair tasks.'
)
CONTRARY_TEXT = (
    'Fresh agent sessions increased repeated errors on the evaluated maintenance tasks. '
    'The replication failed to confirm the original benefit.'
)
QUESTION = 'Do fresh agent sessions reduce repeated errors?'


def snap(url, **kwargs):
    text = {SUPPORT: SUPPORT_TEXT, CONTRARY: CONTRARY_TEXT}.get(url)
    if not text:
        return None
    return {'text': text, 'sha256': cases.digest(text), 'fetched_at': '2026-09-05T00:00:00Z', 'cache_hit': True}


def contradict_count(data):
    brief = research.brief(data) if data.get('claims') else {'claims': []}
    return sum(
        1 for c in brief['claims']
        for a in c['assessments']
        if a['relation'] == 'contradicts' and a['state'] == 'CURRENT'
    )


def main():
    import tempfile
    from pathlib import Path
    root = Path(tempfile.mkdtemp(prefix='science-eval-'))
    naive_db = root / 'naive.db'
    adaptive_db = root / 'adaptive.db'

    with patch.object(instruments, 'document_snapshot', side_effect=snap):
        naive = research_run.naive_fixed_search_arm(QUESTION, sources=[SUPPORT], db=naive_db)
        # Naive "challenge": re-search the same question angles — no overturn map.
        naive2 = cases.refresh(naive['id'], db=naive_db)
        naive_score = contradict_count(naive2)

    with patch.object(instruments, 'document_snapshot', side_effect=snap):
        base = cases.create(QUESTION, sources=[SUPPORT], db=adaptive_db)
        quote = base['evidence'][0]['quote']
        base = research.assess(
            base['id'], base['version'], statement='Fresh sessions reduce repeated errors.',
            relation='supports', rationale='Primary study measured fewer repeated errors.',
            evidence_id=base['evidence'][0]['id'], quote=quote, db=adaptive_db,
        )

    def discover(provider, query, **kwargs):
        return [cases.search.Candidate(CONTRARY, 'Replication failure', CONTRARY_TEXT[:100])]

    with patch.object(instruments, 'document_snapshot', side_effect=snap), \
            patch.object(research_run.discovery, 'find', side_effect=discover):
        run = research_run.start_challenge(
            base['id'], version=base['version'], db=adaptive_db, live=False,
            limits={'max_rounds': 2, 'max_discovery_calls': 4, 'max_document_reads': 6},
        )
    after = cases.get(base['id'], db=adaptive_db)
    adaptive_score = contradict_count(after)

    result = {
        'question': QUESTION,
        'naive_contradict_assessments': naive_score,
        'adaptive_contradict_assessments': adaptive_score,
        'adaptive_wins': adaptive_score > naive_score,
        'challenge_run_id': run['id'],
        'challenge_stop_reason': run.get('stop_reason'),
        'meaning': (
            'Naive arm = fixed create/refresh without an overturn map. '
            'Adaptive arm = research challenge against a pinned supported claim. '
            'Scores count CURRENT contradicts assessments only.'
        ),
    }
    print(json.dumps(result, indent=2))
    if not result['adaptive_wins']:
        raise SystemExit('FINDING: adaptive challenge did not beat naive baseline on contrary assessments')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
