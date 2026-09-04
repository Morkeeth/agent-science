"""Paired acceptance runs on immutable Git revisions.

Only the explicit local CLI invokes code. Search results and MCP calls cannot run it.
The selected acceptance script is copied once and held constant across both arms.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from clearance import cases


def compare(case_id, *, repo, baseline, candidate, check, runs=3, timeout=60, db=None):
    case = cases.get(case_id,db=db)
    repo=Path(repo).resolve(); check=Path(check).resolve()
    if case.get('repo') and Path(case['repo']['root']).resolve()!=repo:
        raise ValueError('experiment repo must match the case repo')
    if not 1 <= runs <= 10 or not 1 <= timeout <= 300:
        raise ValueError('runs must be 1–10; timeout must be 1–300 seconds')
    if not check.is_file() or check.suffix!='.py' or check.stat().st_size>200_000:
        raise ValueError('check must be a Python acceptance script of at most 200 KB')
    # Capture before either arm. Nothing under test supplies its own acceptance rule.
    check_bytes=check.read_bytes()
    def resolve(ref):
        return subprocess.check_output(['git','-C',str(repo),'rev-parse','--verify',ref+'^{commit}'],text=True,stderr=subprocess.PIPE,timeout=10).strip()
    pins={'baseline':resolve(baseline),'candidate':resolve(candidate)}
    if pins['baseline']==pins['candidate']:
        raise ValueError('baseline and candidate resolve to the same commit')
    rows=[]; added=[]
    with tempfile.TemporaryDirectory(prefix='science-experiment-') as temporary:
        root=Path(temporary)
        acceptance=root/'acceptance.py';acceptance.write_bytes(check_bytes)
        try:
            for arm,commit in pins.items():
                dst=root/arm
                subprocess.run(['git','-C',str(repo),'worktree','add','--detach',str(dst),commit],check=True,capture_output=True,timeout=30)
                added.append(dst)
            for i in range(runs):
                order=('baseline','candidate') if i%2==0 else ('candidate','baseline')
                for arm in order:
                    # Each run starts at the pinned commit: prior runs cannot leave fixtures behind.
                    dst=root/arm
                    subprocess.run(['git','-C',str(dst),'reset','--hard',pins[arm]],check=True,capture_output=True,timeout=10)
                    subprocess.run(['git','-C',str(dst),'clean','-fdx'],check=True,capture_output=True,timeout=10)
                    env=os.environ.copy();env['PYTHONPATH']=str(dst);env['PYTHONDONTWRITEBYTECODE']='1'
                    if acceptance.is_symlink():
                        acceptance.unlink()
                    acceptance.write_bytes(check_bytes)
                    started=time.monotonic()
                    # Bounded memory capture; never accumulate an unbounded log file.
                    import threading
                    import signal
                    output_hash=hashlib.sha256(); tail=bytearray(); byte_count=[0]
                    proc=subprocess.Popen([sys.executable,str(acceptance)],cwd=dst,env=env,
                        stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True)
                    def drain(stream=proc.stdout, hasher=output_hash, captured=tail, count=byte_count):
                        while True:
                            chunk=stream.read(4096)
                            if not chunk: break
                            hasher.update(chunk);count[0]+=len(chunk)
                            captured.extend(chunk)
                            if len(captured)>2000:del captured[:-2000]
                    reader=threading.Thread(target=drain,daemon=True);reader.start()
                    timed_out=False
                    try:
                        try:code=proc.wait(timeout=timeout)
                        except subprocess.TimeoutExpired:
                            code=None;timed_out=True
                    finally:
                        # A successful parent can leave children alive too.
                        try:os.killpg(proc.pid,signal.SIGKILL)
                        except ProcessLookupError:pass
                        proc.wait();reader.join(timeout=3)
                    capture_complete=not reader.is_alive()
                    if capture_complete:proc.stdout.close()
                    raw=bytes(tail)
                    check_unchanged=acceptance.is_file() and not acceptance.is_symlink() and acceptance.read_bytes()==check_bytes
                    rows.append({'arm':arm,'pair':i+1,'commit':pins[arm],'exit_code':code,'timed_out':timed_out,
                                 'acceptance_unchanged':check_unchanged,'seconds':round(time.monotonic()-started,4),'output_sha256':output_hash.hexdigest(),'output_bytes':byte_count[0],
                                 'output_truncated':byte_count[0]>2000,'capture_complete':capture_complete,
                                 'output_tail':raw[-2000:].decode('utf-8',errors='replace')})
        finally:
            for path in added:
                subprocess.run(['git','-C',str(repo),'worktree','remove','--force',str(path)],capture_output=True,timeout=30)
    aggregate={}
    for arm in pins:
        arm_rows=[r for r in rows if r['arm']==arm]
        aggregate[arm]={'passed':sum(r['exit_code']==0 and r['acceptance_unchanged'] for r in arm_rows),'runs':runs,
                        'median_seconds':statistics.median(r['seconds'] for r in arm_rows)}
    b,c=aggregate['baseline'],aggregate['candidate']
    valid=all(r['acceptance_unchanged'] and r['capture_complete'] for r in rows)
    summary=f"baseline {b['passed']}/{runs} passes; candidate {c['passed']}/{runs} passes on the same acceptance script"
    if not valid: summary='INVALID: acceptance script changed or a detached process kept output open. '+summary
    return cases.record_experiment(case_id,{'valid':valid,'case_version':case['version'],'repo':str(repo),'pins':pins,
        'acceptance_sha256':hashlib.sha256(check_bytes).hexdigest(),'acceptance_source':check_bytes.decode('utf-8',errors='replace'),
        'runs':rows,'aggregate':aggregate,'summary':summary,
        'limits':['A passing script is only as strong as its independent acceptance criteria.',
                  'Wall time includes process startup. API cost and human rework were not measured.',
                  'Repeated runs on one machine do not establish general practice superiority.',
                  'Run only trusted code: worktree isolation and child cleanup are not an OS sandbox.']},db=db)
