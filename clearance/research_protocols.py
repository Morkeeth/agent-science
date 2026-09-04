"""Immutable experiment plans and links to actual trusted CLI experiment runs."""
from contextlib import closing
import hashlib
import json
from pathlib import Path
import subprocess
import uuid

from clearance import cases

REQUIRED = ('hypothesis', 'claim_refs', 'repo', 'tasks', 'baseline', 'intervention',
            'outcomes', 'budget', 'stopping_rule')


def _connect(db):
    con = cases.connect(db)
    con.executescript('''
        CREATE TABLE IF NOT EXISTS night_protocols(id TEXT, version INTEGER, case_id TEXT, body TEXT NOT NULL, PRIMARY KEY(id,version));
        CREATE TABLE IF NOT EXISTS night_protocol_executions(id TEXT PRIMARY KEY, protocol_id TEXT, protocol_version INTEGER, state TEXT, body TEXT NOT NULL);
    ''')
    return con


def get(protocol_id, *, version=None, db=None):
    with closing(_connect(db)) as con:
        row = con.execute('SELECT body FROM night_protocols WHERE id=? AND (? IS NULL OR version=?) ORDER BY version DESC LIMIT 1', (protocol_id, version, version)).fetchone()
        if row is None:
            raise ValueError('protocol or version not found')
        result = json.loads(row['body'])
        result['executions'] = [json.loads(r['body']) for r in con.execute('SELECT body FROM night_protocol_executions WHERE protocol_id=? AND protocol_version=?', (protocol_id, result['version']))]
        return result


def _pin(repo, ref):
    try:
        return subprocess.check_output(['git', '-C', repo, 'rev-parse', '--verify', str(ref) + '^{commit}'], stderr=subprocess.PIPE, text=True, timeout=10).strip()
    except (OSError, subprocess.SubprocessError):
        raise ValueError('Git revision does not resolve to a commit') from None


def create(case_id, fields, *, root=None, protocol_id=None, db=None):
    if not isinstance(fields, dict):
        raise ValueError('protocol must be an object')
    case = cases.get(case_id, db=db)
    allowed = set(REQUIRED) | {'kind', 'check_sha256'}
    if set(fields) - allowed:
        raise ValueError('unknown protocol fields: ' + ', '.join(sorted(set(fields) - allowed)))
    body = dict(fields)
    if root:
        body['repo'] = root
    missing = [field for field in REQUIRED if not body.get(field)]
    for field in ('hypothesis', 'stopping_rule'):
        if field in body and (not isinstance(body[field], str) or not body[field].strip()):
            raise ValueError(field + ' must be nonempty text')
    for field in ('claim_refs', 'tasks', 'outcomes'):
        if body.get(field) and not isinstance(body[field], list):
            raise ValueError(field + ' must be a list')
    for ref in body.get('claim_refs', []):
        if not isinstance(ref, dict) or not {'claim_id', 'version'} <= ref.keys():
            raise ValueError('claim_refs require claim_id and version')
        cited = cases.get(case_id, db=db, version=ref['version'])
        if ref['claim_id'] not in {c['id'] for c in cited.get('claims', [])}:
            raise ValueError('cited claim not found in pinned case version')
    if body.get('repo'):
        body['repo'] = str(Path(body['repo']).resolve())
        if case.get('repo') and body['repo'] != str(Path(case['repo']['root']).resolve()):
            raise ValueError('protocol repo must match case repo')
    if body.get('budget'):
        budget = body['budget']
        if not isinstance(budget, dict) or not {'runs', 'timeout', 'basis'} <= budget.keys():
            raise ValueError('budget requires runs, timeout and basis')
        if type(budget['runs']) is not int or not 1 <= budget['runs'] <= 10 or type(budget['timeout']) is not int or not 1 <= budget['timeout'] <= 300 or not isinstance(budget['basis'], str) or not budget['basis'].strip():
            raise ValueError('invalid comparison budget')
    if body.get('repo'):
        for key in ('baseline', 'intervention'):
            if body.get(key):
                body[key] = _pin(body['repo'], body[key])
    if body.get('baseline') and body.get('baseline') == body.get('intervention'):
        raise ValueError('baseline and intervention must differ')
    kind = body.get('kind', 'code_change')
    if kind == 'code_change' and not body.get('check_sha256'):
        missing.append('check_sha256')
    if body.get('check_sha256') and (len(body['check_sha256']) != 64 or any(c not in '0123456789abcdef' for c in body['check_sha256'])):
        raise ValueError('check_sha256 must be a lowercase SHA256 digest of the trusted acceptance script')
    with closing(_connect(db)) as con, con:
        con.execute('BEGIN IMMEDIATE')
        previous = con.execute('SELECT case_id, MAX(version) AS version FROM night_protocols WHERE id=?', (protocol_id,)).fetchone()
        if protocol_id and previous['version'] is None:
            raise ValueError('protocol not found')
        if previous['version'] and previous['case_id'] != case_id:
            raise ValueError('protocol belongs to a different case')
        body.update(id=protocol_id or uuid.uuid4().hex[:12], version=(previous['version'] or 0) + 1,
                    case_id=case_id, case_version=case['version'], created_at=cases.now(), kind=kind,
                    status='DRAFT' if missing else 'READY', missing=missing)
        con.execute('INSERT INTO night_protocols VALUES(?,?,?,?)', (body['id'], body['version'], case_id, json.dumps(body)))
    return get(body['id'], db=db)


def execute(protocol_id, *, check, trusted=False, version=None, db=None):
    from clearance import experiments
    if trusted is not True:
        raise ValueError('explicit trusted-script acknowledgement is required')
    plan = get(protocol_id, version=version, db=db)
    if plan['status'] != 'READY' or plan['kind'] != 'code_change':
        raise ValueError('only READY code_change protocols have a compatible runner')
    if cases.get(plan['case_id'], db=db)['version'] != plan['case_version']:
        raise ValueError('case changed; create a new protocol version before execution')
    path = Path(check).resolve()
    if hashlib.sha256(path.read_bytes()).hexdigest() != plan['check_sha256']:
        raise ValueError('acceptance script differs from the frozen protocol')
    receipt = {'id': uuid.uuid4().hex, 'protocol_id': protocol_id, 'protocol_version': plan['version'],
               'state': 'RUNNING', 'started_at': cases.now(), 'experiment_id': None}
    with closing(_connect(db)) as con, con:
        con.execute('INSERT INTO night_protocol_executions VALUES(?,?,?,?,?)', (receipt['id'], protocol_id, plan['version'], receipt['state'], json.dumps(receipt)))
    try:
        result = experiments.compare(plan['case_id'], repo=plan['repo'], baseline=plan['baseline'], candidate=plan['intervention'], check=str(path), runs=plan['budget']['runs'], timeout=plan['budget']['timeout'], db=db)
        receipt.update(state='COMPLETED', experiment_id=result['id'], result=result)
    except Exception as exc:
        receipt.update(state='FAILED', error=str(exc))
        raise
    finally:
        receipt['finished_at'] = cases.now()
        with closing(_connect(db)) as con, con:
            con.execute('UPDATE night_protocol_executions SET state=?,body=? WHERE id=?', (receipt['state'], json.dumps(receipt), receipt['id']))
    return receipt
