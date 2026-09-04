#!/usr/bin/env bash
# Stranger path — adaptive research + challenge, no API key, no network.
# Usage: bash scripts/demo_research_challenge.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
DB="${TMPDIR:-/tmp}/agent-science-research-demo-$$.db"
export AGENT_SCIENCE_CASES_DB="$DB"
cleanup() { rm -f "$DB"; }
trap cleanup EXIT

python3 - <<'PY'
"""Offline research → challenge demo with local fixtures only."""
import json, os, tempfile
from pathlib import Path
from unittest.mock import patch
from clearance import cases, instruments, research, research_run
from clearance.stack_cli import main

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
Q = 'Do fresh agent sessions reduce repeated errors?'
db = os.environ['AGENT_SCIENCE_CASES_DB']

def snap(url, **kwargs):
    text = {SUPPORT: SUPPORT_TEXT, CONTRARY: CONTRARY_TEXT}.get(url)
    if not text:
        return None
    return {'text': text, 'sha256': cases.digest(text), 'fetched_at': '2026-09-05T00:00:00Z', 'cache_hit': True}

def discover(provider, query, **kwargs):
    return [cases.search.Candidate(CONTRARY, 'Replication failure', CONTRARY_TEXT[:100])]

with patch.object(instruments, 'document_snapshot', side_effect=snap):
    code = main(['research', 'start', Q, '--source', SUPPORT, '--db', db, '--plan-only'])
    assert code == 0
    runs = research_run.list_runs(db=db)
    case_id = runs[0]['case_id']
    data = cases.get(case_id, db=db)
    quote = data['evidence'][0]['quote']
    research.assess(case_id, data['version'], statement='Fresh sessions reduce repeated errors.',
                    relation='supports', rationale='Primary study measured fewer repeated errors.',
                    evidence_id=data['evidence'][0]['id'], quote=quote, db=db)

with patch.object(instruments, 'document_snapshot', side_effect=snap), \
     patch.object(research_run.discovery, 'find', side_effect=discover):
    code = main(['research', 'challenge', case_id, '--db', db, '--max-steps', '3'])
    assert code == 0
    run = research_run.list_runs(case_id=case_id, db=db)[0]
    if run['status'] == 'paused':
        code = main(['research', 'resume', run['id'], '--db', db])
        assert code == 0
    run = research_run.get_run(run['id'], db=db)
    brief = research.brief(cases.get(case_id, db=db))

print('DEMO OK')
print(f"case={case_id} run={run['id']} kind={run['kind']} status={run['status']} stop={run.get('stop_reason')}")
print(f"challenge_queries={sum(1 for s in run['steps'] if s['op']=='choose_gap')}")
print(f"claim_states={[c['state'] for c in brief['claims']]}")
print(f"strongest_challenge={(run.get('answer') or {}).get('strongest_challenge', 'n/a')[:120]}")
assert run['kind'] == 'challenge'
assert any(c['state'] == 'CONTESTED' or any(a['relation']=='contradicts' for a in c['assessments']) for c in brief['claims'])
PY
