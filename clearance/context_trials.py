"""Local host-driven context trials. No model calls and no MCP execution surface.

A prepared attempt is a reservation, never an agent result. Only the explicit
trusted CLI completion runs the frozen external Python acceptance script.
"""
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
import uuid

from clearance import cases, research_protocols


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def _connect(db):
    con = cases.connect(db)
    con.execute('CREATE TABLE IF NOT EXISTS context_trials(id TEXT PRIMARY KEY, version INTEGER NOT NULL, body TEXT NOT NULL)')
    return con


def get(trial_id, *, db=None):
    with closing(_connect(db)) as con:
        row = con.execute('SELECT body FROM context_trials WHERE id=?', (trial_id,)).fetchone()
    if not row:
        raise ValueError('context trial not found')
    body = json.loads(row['body'])
    attempts = body['attempts']
    body['summary'] = {'denominator': body['manifest']['denominator'], 'prepared': len(attempts),
        'accepted': sum(a['state'] == 'ACCEPTED' for a in attempts),
        'finished': sum(a['state'] in ('ACCEPTED', 'REJECTED', 'TIMEOUT', 'INVALID', 'CANCELLED', 'REVIEW_REQUIRED') for a in attempts),
        'interpretation': 'Acceptance checks on selected tasks; not general context effectiveness.',
        'tokens': None, 'billing': None, 'host_identity_basis': 'Operator-supplied; model identity and fresh-host isolation are not independently attested.'}
    return body



def for_case(case_id, *, case_version=None, db=None):
    """Retrieve actual trial summaries separately from code-comparison results."""
    case = cases.get(case_id, version=case_version, db=db)
    with closing(_connect(db)) as con:
        rows = [json.loads(row['body']) for row in con.execute('SELECT body FROM context_trials ORDER BY id')]
    trials = []
    for body in rows:
        manifest = body['manifest']
        if manifest['case_id'] != case_id or manifest['case_version'] > case['version']:
            continue
        trial = get(body['id'], db=db)
        trials.append({'id': trial['id'], 'version': trial['version'],
            'case_version': manifest['case_version'], 'protocol_id': manifest['protocol_id'],
            'protocol_version': manifest['protocol_version'], 'summary': trial['summary']})
    return {'object_type': 'case_context_trials', 'case_id': case_id,
            'case_version': case['version'], 'trials': trials}


def _update(trial_id, expected_version, change, db):
    # Public operations require a version. Internal phase transitions use None
    # only with a state guard inside this same BEGIN IMMEDIATE transaction.
    with closing(_connect(db)) as con, con:
        con.execute('BEGIN IMMEDIATE')
        row = con.execute('SELECT body FROM context_trials WHERE id=?', (trial_id,)).fetchone()
        if not row:
            raise ValueError('context trial not found')
        body = json.loads(row['body'])
        if expected_version is not None and (type(expected_version) is not int or body['version'] != expected_version):
            raise ValueError('stale trial version')
        change(body)
        body['version'] += 1
        con.execute('UPDATE context_trials SET version=?,body=? WHERE id=?', (body['version'], _json(body), trial_id))
    return get(trial_id, db=db)


def _text(value, label):
    if not isinstance(value, str) or not value.strip() or len(value) > 30000:
        raise ValueError(label + ' must be known nonempty text')
    if value.strip().lower() in ('unknown', 'unspecified', 'none', 'null'):
        raise ValueError(label + ' must be known nonempty text')
    return value


def _id(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}', value):
        raise ValueError('invalid task or arm identity')
    return value


def _read(path, digest):
    path = Path(path).resolve()
    if not re.fullmatch('[0-9a-f]{64}', str(digest)):
        raise ValueError('invalid SHA256')
    with path.open('rb') as stream:
        data = stream.read(200001)
    if len(data) > 200000 or _hash(data) != digest:
        raise ValueError('frozen file hash mismatch or oversized file')
    return data


def _git(repo, *args):
    try:
        return subprocess.check_output(['git', '-c', 'core.hooksPath=/dev/null', '-C', str(repo), *args], stderr=subprocess.PIPE, timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError('Git operation failed: ' + ' '.join(args[:2])) from exc


def create(spec, *, db=None):
    required = {'protocol_id', 'protocol_version', 'repo', 'base_commit', 'tasks', 'arms', 'acceptance_path', 'acceptance_sha256', 'host', 'policy', 'repetitions', 'artifact_root'}
    if not isinstance(spec, dict) or set(spec) != required:
        raise ValueError('context trial requires exactly: ' + ', '.join(sorted(required)))
    if type(spec['protocol_version']) is not int or spec['protocol_version'] < 1:
        raise ValueError('protocol_version must be a positive exact version')
    protocol = research_protocols.get(spec['protocol_id'], version=spec['protocol_version'], db=db)
    if protocol['kind'] != 'agent_context_trial' or protocol['status'] != 'READY':
        raise ValueError('a READY agent_context_trial protocol is required')
    repo = Path(spec['repo']).resolve()
    if str(repo) != protocol['repo'] or cases.get(protocol['case_id'], db=db)['version'] != protocol['case_version']:
        raise ValueError('protocol repository or case version changed')
    pin = spec['base_commit']
    if not re.fullmatch('[0-9a-f]{40}', str(pin)) or _git(repo, 'rev-parse', pin + '^{commit}').decode().strip() != pin:
        raise ValueError('base_commit must be an exact commit')
    tasks, arms = spec['tasks'], spec['arms']
    if not isinstance(tasks, list) or not tasks or not isinstance(arms, list) or len(arms) < 2:
        raise ValueError('tasks and at least two arms are required')
    if any(not isinstance(t, dict) or set(t) != {'id', 'prompt', 'acceptance_task'} for t in tasks):
        raise ValueError('tasks require id, acceptance_task and exact protocol prompt')
    if [t['prompt'] for t in tasks] != protocol['tasks']:
        raise ValueError('task prompts must equal the frozen protocol tasks in order')
    for t in tasks:
        _id(t['id']); _id(t['acceptance_task']); _text(t['prompt'], 'task prompt')
    if len({t['id'] for t in tasks}) != len(tasks):
        raise ValueError('duplicate task identity')
    if type(spec['repetitions']) is not int or spec['repetitions'] != protocol['budget']['runs']:
        raise ValueError('repetitions must match protocol budget')
    host = spec['host']
    if not isinstance(host, dict) or set(host) != {'provider', 'model', 'identity'}:
        raise ValueError('host requires provider, model and identity')
    for k, v in host.items():
        if k == 'model' and v == 'unknown':
            continue
        _text(v, k)
    policy = spec['policy']
    if not isinstance(policy, dict) or set(policy) != {'max_attempts', 'total_seconds', 'attempt_seconds', 'check_seconds'}:
        raise ValueError('invalid execution policy fields')
    if any(type(v) is not int or v < 1 or v > 86400 for v in policy.values()):
        raise ValueError('policy ceilings must be positive bounded integers')
    if policy['total_seconds'] < policy['attempt_seconds'] + policy['check_seconds']:
        raise ValueError('execution policy cannot admit even one attempt')
    denominator = len(tasks) * len(arms) * spec['repetitions']
    if policy['max_attempts'] > denominator or max(policy['attempt_seconds'], policy['check_seconds']) > protocol['budget']['timeout']:
        raise ValueError('execution policy exceeds frozen denominator or attempt timeout')
    if not protocol.get('check_sha256'):
        raise ValueError('protocol requires a frozen acceptance check SHA256')
    if spec['acceptance_sha256'] != protocol['check_sha256']:
        raise ValueError('acceptance hash differs from protocol')
    acceptance_source = Path(spec['acceptance_path']).resolve()
    if acceptance_source == repo or repo in acceptance_source.parents:
        raise ValueError('acceptance script must be external to the tested repository')
    acceptance = _read(acceptance_source, spec['acceptance_sha256'])
    root = Path(spec['artifact_root']).resolve()
    if root == repo or repo in root.parents:
        raise ValueError('trial artifacts must stay outside repository')
    captures = []
    for arm in arms:
        if not isinstance(arm, dict) or set(arm) != {'id', 'instructions_path', 'sha256'}:
            raise ValueError('arms require id, instructions_path, sha256')
        _id(arm['id'])
        captures.append(_read(arm['instructions_path'], arm['sha256']))
    if len({a['id'] for a in arms}) != len(arms) or len({a['sha256'] for a in arms}) != len(arms):
        raise ValueError('arms require distinct identities and instruction bytes')
    trial_id = uuid.uuid4().hex[:16]
    directory = root / trial_id
    directory.mkdir(parents=True, mode=0o700)
    (directory / 'acceptance.py').write_bytes(acceptance)
    frozen_arms = []
    for arm, data in zip(arms, captures):
        destination = directory / (arm['id'] + '-AGENTS.md')
        destination.write_bytes(data)
        frozen_arms.append({'id': arm['id'], 'sha256': arm['sha256'], 'instructions_path': str(destination), 'instructions_bytes': len(data)})
    manifest = {**spec, 'repo': str(repo), 'arms': frozen_arms, 'acceptance_path': str(directory / 'acceptance.py'),
        'artifact_root': str(directory), 'denominator': denominator, 'case_id': protocol['case_id'], 'case_version': protocol['case_version'],
        'protocol_sha256': _hash(_json({k:v for k,v in protocol.items() if k != 'executions'}).encode())}
    body = {'object_type': 'context_trial', 'id': trial_id, 'version': 1, 'created_at': cases.now(), 'manifest': manifest, 'manifest_sha256': _hash(_json(manifest).encode()), 'attempts': [], 'reserved_seconds': 0}
    with closing(_connect(db)) as con, con:
        con.execute('INSERT INTO context_trials VALUES(?,?,?)', (trial_id, 1, _json(body)))
    return get(trial_id, db=db)


def _trusted(trusted):
    if trusted is not True:
        raise ValueError('explicit local CLI trusted execution acknowledgement required')


def prepare(trial_id, *, task_id, arm_id, repetition, expected_version, trusted=False, db=None):
    _trusted(trusted)
    if type(expected_version) is not int:
        raise ValueError('expected_version must be an integer')
    attempt_id = uuid.uuid4().hex[:16]
    def reserve(body):
        m = body['manifest']; policy = m['policy']
        task = next((t for t in m['tasks'] if t['id'] == task_id), None)
        arm = next((a for a in m['arms'] if a['id'] == arm_id), None)
        if not task or not arm or type(repetition) is not int or not 1 <= repetition <= m['repetitions']:
            raise ValueError('unknown attempt slot')
        if any((a['task_id'], a['arm_id'], a['repetition']) == (task_id, arm_id, repetition) for a in body['attempts']):
            raise ValueError('attempt slot already reserved; inspect instead of retrying')
        seconds = policy['attempt_seconds'] + policy['check_seconds']
        if len(body['attempts']) >= policy['max_attempts'] or body['reserved_seconds'] + seconds > policy['total_seconds']:
            raise ValueError('aggregate execution capacity exhausted')
        if cases.get(m['case_id'], db=db)['version'] != m['case_version']:
            raise ValueError('protocol case version changed')
        _read(m['acceptance_path'], m['acceptance_sha256']); _read(arm['instructions_path'], arm['sha256'])
        body['reserved_seconds'] += seconds
        body['attempts'].append({'id': attempt_id, 'task_id': task_id, 'arm_id': arm_id, 'repetition': repetition,
            'state': 'PREPARING', 'host': m['host'], 'task': task['prompt'], 'acceptance_task': task['acceptance_task'], 'created_at': cases.now(),
            'worktree': str(Path(m['artifact_root']) / attempt_id / 'worktree'), 'started_epoch': None,
            'tokens': None, 'billing': None, 'host_calls': None})
    saved = _update(trial_id, expected_version, reserve, db)
    attempt = next(a for a in saved['attempts'] if a['id'] == attempt_id); m = saved['manifest']; tree = Path(attempt['worktree'])
    try:
        tree.parent.mkdir(mode=0o700)
        _git(m['repo'], 'worktree', 'add', '--detach', str(tree), m['base_commit'])
        arm = next(a for a in m['arms'] if a['id'] == arm_id)
        target = tree / 'AGENTS.md'
        if target.is_symlink():
            target.unlink()
        target.write_bytes(_read(arm['instructions_path'], arm['sha256']))
        def ready(body):
            a = next(a for a in body['attempts'] if a['id'] == attempt_id)
            if a['state'] != 'PREPARING':
                raise ValueError('attempt preparation was cancelled or state changed')
            a.update(state='AWAITING_HOST', started_at=cases.now(), started_epoch=time.time())
        return _update(trial_id, None, ready, db)
    except BaseException:
        def unknown(body):
            a = next(a for a in body['attempts'] if a['id'] == attempt_id)
            if a['state'] == 'PREPARING':
                a['state'] = 'UNKNOWN'; a['error'] = 'Preparation interrupted or failed; inspect preserved worktree.'
        _update(trial_id, None, unknown, db)
        raise


def _run_check(script, task, tree, timeout, output_path):
    """Bound output on disk while draining pipes; kill the whole child session."""
    import selectors
    env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'PYTHONNOUSERSITE': '1', 'PYTHONDONTWRITEBYTECODE': '1',
           'CONTEXT_TRIAL_TASK': task, 'HOME': str(tree.parent)}
    # Start isolated; preload acceptance infrastructure before adding tested code.
    launcher = ('import sys,runpy,pathlib,json,os,hashlib,tempfile,subprocess,time,unittest,importlib,uuid; '
                'script,task,tree=sys.argv[1:]; sys.pycache_prefix=str(pathlib.Path(script).parent / ("check-pycache-"+uuid.uuid4().hex)); sys.path.insert(0,tree); '
                'sys.argv=[script,task]; runpy.run_path(script,run_name="__main__")')
    process = subprocess.Popen([sys.executable, '-I', '-B', '-c', launcher, str(script), task, str(tree)], cwd=tree, env=env, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, start_new_session=True)
    start = time.monotonic(); written = 0; timed_out = False
    try:
        with output_path.open('wb') as output, selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            while selector.get_map():
                if time.monotonic() - start >= timeout:
                    timed_out = True
                    break
                for key, _ in selector.select(min(.1, timeout)):
                    data = os.read(key.fileobj.fileno(), 8192)
                    if not data:
                        selector.unregister(key.fileobj)
                    else:
                        remaining = max(0, 65536 - written)
                        output.write(data[:remaining]); written += len(data[:remaining])
        if not timed_out:
            process.wait(timeout=max(.01, timeout - (time.monotonic() - start)))
    except subprocess.TimeoutExpired:
        timed_out = True
    finally:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
        process.stdout.close()
    return {'exit_code': process.returncode, 'timed_out': timed_out, 'elapsed_seconds': time.monotonic() - start,
            'output_path': str(output_path), 'output_sha256': _hash(output_path.read_bytes()), 'output_limit_bytes': 65536}



def _untracked(tree):
    # Include ignored sources: .gitignore is an agent-controlled input. Normal
    # __pycache__ cannot influence the isolated check's fresh pycache_prefix.
    names = set()
    for flags in (('--others', '--exclude-standard'), ('--others', '--ignored', '--exclude-standard')):
        names.update(_git(tree, 'ls-files', *flags, '-z').decode().split('\0'))
    return sorted(name for name in names if name and name != 'AGENTS.md' and not ('__pycache__' in Path(name).parts and Path(name).suffix == '.pyc'))


def complete(trial_id, attempt_id, *, expected_version, trusted=False, db=None):
    _trusted(trusted)
    if type(expected_version) is not int:
        raise ValueError('expected_version must be an integer')
    def claim(body):
        a = next((a for a in body['attempts'] if a['id'] == attempt_id), None)
        if not a or a['state'] != 'AWAITING_HOST':
            raise ValueError('attempt is not awaiting host completion; no blind retry')
        a['state'] = 'CHECKING'; a['submitted_at'] = cases.now()
    saved = _update(trial_id, expected_version, claim, db)
    m = saved['manifest']; a = next(a for a in saved['attempts'] if a['id'] == attempt_id)
    tree = Path(a['worktree']); result = {}; state = 'INVALID'
    try:
        elapsed = time.time() - a['started_epoch']
        result['host_elapsed_seconds'] = max(0, elapsed)
        if elapsed < 0 or elapsed > m['policy']['attempt_seconds']:
            state = 'TIMEOUT'; raise ValueError('host submission exceeded frozen attempt time ceiling')
        script = _read(m['acceptance_path'], m['acceptance_sha256'])
        arm = next(arm for arm in m['arms'] if arm['id'] == a['arm_id'])
        _read(tree / 'AGENTS.md', arm['sha256'])
        if _git(tree, 'rev-parse', '--show-toplevel').decode().strip() != str(tree):
            raise ValueError('attempt worktree identity changed')
        common = Path(_git(tree, 'rev-parse', '--git-common-dir').decode().strip())
        if not common.is_absolute():
            common = tree / common
        original_common = Path(_git(m['repo'], 'rev-parse', '--git-common-dir').decode().strip())
        if not original_common.is_absolute():
            original_common = Path(m['repo']) / original_common
        if common.resolve() != original_common.resolve():
            raise ValueError('attempt Git ownership changed')
        head = _git(tree, 'rev-parse', 'HEAD').decode().strip()
        if head != m['base_commit']:
            raise ValueError('attempt HEAD differs from frozen base; leave fixes uncommitted')
        # Capture staged and unstaged tracked changes; untracked files are
        # separately frozen below. AGENTS is the assigned intervention, not a fix.
        patch = _git(tree, 'diff', '--binary', m['base_commit'], '--', '.', ':(exclude)AGENTS.md')
        untracked = _untracked(tree)
        files = {}
        for name in untracked:
            path = tree / name
            if path.is_symlink() or not path.is_file() or path.stat().st_size > 200000:
                raise ValueError('untracked attempt file is unsafe or too large')
            content = path.read_bytes()
            files[name] = _hash(content)
            captured_file = tree.parent / 'untracked' / name
            captured_file.parent.mkdir(parents=True, exist_ok=True)
            captured_file.write_bytes(content)
        if not patch and not files:
            raise ValueError('no code change; baseline execution cannot count as an agent fix')
        fingerprint = _hash(patch + _json(files).encode())
        if any(other.get('result', {}).get('patch_sha256') == fingerprint and other['task_id'] == a['task_id'] and other['arm_id'] == a['arm_id'] for other in saved['attempts'] if other['id'] != attempt_id):
            result['duplicate_patch_hash'] = True
        patch_path = tree.parent / 'attempt.patch'; patch_path.write_bytes(patch)
        captured = tree.parent / 'acceptance-captured.py'; captured.write_bytes(script)
        result.update(head=head, patch_sha256=fingerprint, patch_path=str(patch_path), untracked_hashes=files)
        check = _run_check(captured, a['acceptance_task'], tree, m['policy']['check_seconds'], tree.parent / 'acceptance-output.txt')
        result['acceptance'] = check
        after = _git(tree, 'diff', '--binary', m['base_commit'], '--', '.', ':(exclude)AGENTS.md')
        after_files = {}
        for name in _untracked(tree):
            path = tree / name
            if path.is_symlink() or not path.is_file() or path.stat().st_size > 200000:
                raise ValueError('attempt file changed during acceptance')
            after_files[name] = _hash(path.read_bytes())
        _read(tree / 'AGENTS.md', arm['sha256'])
        _read(captured, m['acceptance_sha256'])
        if patch_path.is_symlink() or patch_path.read_bytes() != patch:
            raise ValueError('captured patch artifact changed during acceptance')
        for name, digest in files.items():
            artifact = tree.parent / 'untracked' / name
            if artifact.is_symlink() or _hash(artifact.read_bytes()) != digest:
                raise ValueError('captured untracked artifact changed during acceptance')
        if after != patch or after_files != files or _git(tree, 'rev-parse', 'HEAD').decode().strip() != head:
            raise ValueError('attempt changed during acceptance; result invalid')
        result['acceptance_passed'] = check['exit_code'] == 0 and not check['timed_out']
        state = 'TIMEOUT' if check['timed_out'] else ('ACCEPTED' if check['exit_code'] == 0 else 'REJECTED')
    except (Exception, KeyboardInterrupt) as exc:
        result['error'] = str(exc)
        if isinstance(exc, KeyboardInterrupt):
            state = 'UNKNOWN'
    def finish(body):
        attempt = next(attempt for attempt in body['attempts'] if attempt['id'] == attempt_id)
        if attempt['state'] != 'CHECKING':
            raise ValueError('attempt state changed during acceptance')
        if result.get('patch_sha256'):
            for other in body['attempts']:
                if other['id'] != attempt_id and other['task_id'] == a['task_id'] and other['arm_id'] == a['arm_id'] and other.get('result', {}).get('patch_sha256') == result['patch_sha256']:
                    result['duplicate_patch_hash'] = True
                    other['result']['duplicate_patch_hash'] = True
        attempt.update(state=state, finished_at=cases.now(), result=result)
    return _update(trial_id, None, finish, db)


def abort(trial_id, attempt_id, *, expected_version, reason, trusted=False, db=None):
    """Close a host lease without deleting work or refunding reserved capacity."""
    _trusted(trusted); _text(reason, 'cancellation reason')
    if type(expected_version) is not int:
        raise ValueError('expected_version must be an integer')
    def change(body):
        a = next((a for a in body['attempts'] if a['id'] == attempt_id), None)
        if not a or a['state'] not in ('AWAITING_HOST', 'PREPARING', 'UNKNOWN', 'CHECKING'):
            raise ValueError('attempt cannot be cancelled in this state')
        if a['state'] == 'CHECKING':
            a.update(state='REVIEW_REQUIRED', finished_at=cases.now(), recovery_reason=reason, external_outcome='unknown', recovery_note='Operator closed abandoned check; no retry or success inference. Verify no old process remains before using artifacts.')
        else:
            a.update(state='CANCELLED', finished_at=cases.now(), cancellation_reason=reason)
    return _update(trial_id, expected_version, change, db)
