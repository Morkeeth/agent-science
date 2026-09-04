#!/usr/bin/env bash
# Stranger day-two path — follow a question, see a ranked change report.
# No API key, no network. Usage: bash scripts/demo_research_day_two.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
DB="${TMPDIR:-/tmp}/agent-science-day-two-$$.db"
export AGENT_SCIENCE_CASES_DB="$DB"
cleanup() { rm -f "$DB"; }
trap cleanup EXIT

python3 - <<'PY'
"""Offline: research → decide → follow → source changes → updates change report."""
import os
from unittest.mock import patch
from clearance import cases, instruments, research, follow, updates, experiment_protocol
from clearance.stack_cli import main

SUPPORT = 'https://example.org/fresh-sessions-help'
NOISE = 'https://example.org/sidebar-noise'
SUPPORT_V1 = (
    'Fresh agent sessions reduced the number of repeated errors in our maintenance experiment. '
    'Limitation: the result may not generalize beyond Python repair tasks.'
)
SUPPORT_V2 = (
    'Fresh agent sessions increased the number of repeated errors in our maintenance experiment. '
    'Limitation: the result may not generalize beyond Python repair tasks.'
)
NOISE_V1 = 'Sidebar promo: unrelated archival newsletter signup form for museum visitors only.'
NOISE_V2 = 'Sidebar promo UPDATED: still unrelated archival newsletter signup form.'
Q = 'Do fresh agent sessions reduce repeated errors?'
db = os.environ['AGENT_SCIENCE_CASES_DB']

def snap(mapping):
    def _snap(url, **kwargs):
        text = mapping.get(url)
        if not text:
            return None
        return {'text': text, 'sha256': cases.digest(text), 'fetched_at': '2026-09-05T00:00:00Z', 'cache_hit': True}
    return _snap

with patch.object(instruments, 'document_snapshot', side_effect=snap({SUPPORT: SUPPORT_V1, NOISE: NOISE_V1})):
    assert main(['research', 'start', Q, '--source', SUPPORT, '--source', NOISE, '--db', db, '--plan-only']) == 0
from clearance import research_run
case_id = research_run.list_runs(db=db)[0]['case_id']
data = cases.get(case_id, db=db)
eid = next(e['id'] for e in data['evidence'] if e['url'] == SUPPORT)
quote = next(e['quote'] for e in data['evidence'] if e['url'] == SUPPORT)
research.assess(case_id, data['version'], statement='Fresh sessions reduce repeated errors.',
                relation='supports', rationale='Primary study measured fewer repeated errors.',
                evidence_id=eid, quote=quote, db=db)
data = cases.get(case_id, db=db)
cases.decide(case_id, statement='Prefer fresh sessions on maintenance tasks.',
             rationale='Supported by the verified primary quote.',
             evidence_ids=[eid], expected_version=data['version'], db=db)

assert main(['research', 'follow', case_id, '--db', db, '--note', 'day-two watch']) == 0

# Day two: cited finding reverses; sidebar also churns
with patch.object(instruments, 'document_snapshot', side_effect=snap({SUPPORT: SUPPORT_V2, NOISE: NOISE_V2})):
    assert main(['research', 'updates', '--db', db]) == 0
    run = updates.list_runs(db=db)[0]

assert run['summary']['material_changes'] == 1
assert run['items'][0]['score']['material_effects'][0]['kind'] == 'decision_review_required'
text = updates.render_run(run)
assert 'MATERIAL' in text
assert 'NOTHING MATERIAL CHANGED' not in text

# Quiet re-check after no further change → meaningful empty
with patch.object(instruments, 'document_snapshot', side_effect=snap({SUPPORT: SUPPORT_V2, NOISE: NOISE_V2})):
    quiet = updates.run_updates(db=db, refresh=True, live=False)
assert quiet['summary']['empty'] is True

# Experiment plan stays a plan (observation — no runner)
claim_id = cases.get(case_id, db=db)['claims'][0]['id']
assert main([
    'research', 'experiment-plan', case_id,
    '--hypothesis', 'If acceptance fails on the intervention, revise the fresh-session claim.',
    '--claim', claim_id, '--kind', 'observation', '--db', db,
]) == 0
proto = experiment_protocol.list_protocols(case_id=case_id, db=db)[0]
assert proto['status'] == 'planned'
assert proto['execution'] is None

# Executable code_change protocol → trusted runner → linked experiment (still not "the result")
import subprocess, tempfile, os
from pathlib import Path
repo = Path(tempfile.mkdtemp()) / 'repo'
repo.mkdir()
check = Path(tempfile.mkdtemp()) / 'accept.py'
check.write_text('raise SystemExit(0)\n')
env = {**os.environ, 'GIT_AUTHOR_NAME': 'demo', 'GIT_AUTHOR_EMAIL': 'd@d',
       'GIT_COMMITTER_NAME': 'demo', 'GIT_COMMITTER_EMAIL': 'd@d'}
subprocess.run(['git', 'init'], cwd=repo, check=True, capture_output=True)
(repo / 'x.txt').write_text('base\n')
subprocess.run(['git', 'add', 'x.txt'], cwd=repo, check=True, capture_output=True, env=env)
subprocess.run(['git', 'commit', '-m', 'base'], cwd=repo, check=True, capture_output=True, env=env)
base = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
(repo / 'x.txt').write_text('cand\n')
subprocess.run(['git', 'add', 'x.txt'], cwd=repo, check=True, capture_output=True, env=env)
subprocess.run(['git', 'commit', '-m', 'cand'], cwd=repo, check=True, capture_output=True, env=env)
cand = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()

with patch.object(instruments, 'document_snapshot', side_effect=snap({SUPPORT: SUPPORT_V1})):
    measured_case = cases.create(
        'Does the intervention preserve the acceptance check?',
        sources=[SUPPORT], root=str(repo), db=db,
    )
code_proto = experiment_protocol.create(
    measured_case['id'],
    hypothesis='Candidate passes the same acceptance script as baseline.',
    kind='code_change',
    repo=str(repo),
    baseline_ref=base,
    intervention_ref=cand,
    acceptance_check=str(check),
    comparison_budget={'paired_runs': 1, 'timeout_seconds': 30},
    db=db,
)
assert code_proto['status'] == 'planned' and code_proto['executable'] is True
linked = experiment_protocol.execute(code_proto['id'], db=db)
assert linked['status'] == 'linked'
assert linked['execution']['experiment_id']
assert linked['execution']['valid'] is True
# Prior version remains the plan/denominator
v1 = experiment_protocol.get(code_proto['id'], version=1, db=db)
assert v1['status'] == 'planned' and v1['execution'] is None

print('DEMO OK')
print(f"case={case_id} follow={follow.get_by_case(case_id, db=db)['id']}")
print(f"update_run={run['id']} material={run['summary']['material_changes']} top={run['items'][0]['score']['material_effects'][0]['kind']}")
print(f"quiet_empty={quiet['summary']['empty']}")
print(f"protocol={proto['id']} status={proto['status']}")
print(f"code_protocol={linked['id']} status={linked['status']} experiment={linked['execution']['experiment_id']} valid={linked['execution']['valid']}")
print(f"what_would_change={run['items'][0]['what_would_change_this_answer'][:140]}")
PY
