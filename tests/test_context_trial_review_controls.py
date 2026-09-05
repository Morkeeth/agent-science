"""Independent-review failure classes exercised against real temporary objects."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest
import test_context_trials as fixtures
from clearance import context_trials as trials, research_protocols


@pytest.fixture
def fx():
    fixture = fixtures.ContextTrials(); fixture.setUp()
    yield fixture
    fixture.doCleanups()


def protocol(fx, script=None, missing_hash=False):
    if script is not None:
        fx.script.write_text(script)
    fields=dict(kind='agent_context_trial',hypothesis='Frozen task intervention',claim_refs=[dict(claim_id=fx.case['claims'][0]['id'],version=fx.case['version'])],repo=str(fx.repo),tasks=['Fix the value under the frozen contract.'],baseline='Baseline',intervention='Candidate',outcomes=['Accepted fixes'],budget=dict(runs=2,timeout=30,basis='Four attempts'),stopping_rule='All fixed slots')
    digest=hashlib.sha256(fx.script.read_bytes()).hexdigest()
    if not missing_hash:
        fields['check_sha256']=digest
    saved=research_protocols.create(fx.case['id'],fields,db=fx.db)
    fx.spec.update(protocol_id=saved['id'],acceptance_sha256=digest)


def test_descendant_checkout_is_not_a_submitted_fix(fx):
    (fx.repo/'code.py').write_text('value = 1\n'); fx.git('add','.'); fx.git('commit','-m','upstream fix')
    later=fx.git('rev-parse','HEAD').strip()
    trial=fx.prepare(fx.start()); tree=Path(trial['attempts'][0]['worktree'])
    subprocess.check_call(['git','-C',str(tree),'checkout','-q','--detach',later])
    done=fx.complete(trial)
    assert done['attempts'][0]['state']=='INVALID'
    assert 'HEAD differs' in done['attempts'][0]['result']['error']


def test_assigned_untracked_instructions_are_not_host_work(fx):
    fx.git('rm','AGENTS.md'); fx.git('commit','-m','no tracked instructions')
    fx.spec['base_commit']=fx.git('rev-parse','HEAD').strip()
    protocol(fx,'raise SystemExit(0)\n')
    done=fx.complete(fx.prepare(fx.start()))
    assert done['attempts'][0]['state']=='INVALID'
    assert 'no code change' in done['attempts'][0]['result']['error']


@pytest.mark.parametrize('version',[None,0,-1,True,'1'])
def test_protocol_pin_must_be_positive_integer(fx,version):
    fx.spec['protocol_version']=version
    with pytest.raises(ValueError,match='positive exact version'): fx.start()


def test_git_failure_is_structured_cli_and_mcp_error(fx):
    fx.spec['base_commit']='a'*40
    with pytest.raises(ValueError,match='Git operation failed'): fx.start()
    spec=fx.root/'spec.json'; spec.write_text(json.dumps(fx.spec))
    root=Path(__file__).resolve().parents[1]
    cli=subprocess.run([sys.executable,'-m','clearance','research','context-trial-create','--trial-file',str(spec),'--db',fx.db,'--json'],cwd=root,capture_output=True,text=True,timeout=30)
    assert cli.returncode==2 and 'Traceback' not in cli.stderr
    request={'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'science_research','arguments':{'action':'context-trial-create','trial_spec':fx.spec,'db':fx.db}}}
    mcp=subprocess.run([sys.executable,'-m','clearance.mcp_server'],input=json.dumps(request)+'\n',cwd=root,capture_output=True,text=True,timeout=30)
    assert mcp.returncode==0 and json.loads(mcp.stdout)['id']==1
    assert 'Git operation failed' in mcp.stdout


def test_concurrent_preparation_keeps_both_leases(fx,monkeypatch):
    trial=fx.start(); original=trials._git; hook={}
    def git(repo,*args):
        out=original(repo,*args)
        if args[:2]==('worktree','add') and hook: hook.pop('run')()
        return out
    monkeypatch.setattr(trials,'_git',git)
    hook['run']=lambda: trials.prepare(trial['id'],task_id='fix',arm_id='candidate',repetition=1,expected_version=2,trusted=True,db=fx.db)
    result=fx.prepare(trial)
    assert len(result['attempts'])==2
    assert all(a['state']=='AWAITING_HOST' for a in result['attempts'])
    assert len({a['worktree'] for a in result['attempts']})==2


def test_abort_during_prepare_retains_cancelled_state(fx,monkeypatch):
    trial=fx.start(); original=trials._git
    def git(repo,*args):
        out=original(repo,*args)
        if args[:2]==('worktree','add'):
            current=trials.get(trial['id'],db=fx.db)
            trials.abort(trial['id'],current['attempts'][0]['id'],expected_version=current['version'],reason='Operator stopped preparation',trusted=True,db=fx.db)
        return out
    monkeypatch.setattr(trials,'_git',git)
    with pytest.raises(ValueError,match='cancelled'): fx.prepare(trial)
    assert trials.get(trial['id'],db=fx.db)['attempts'][0]['state']=='CANCELLED'


def test_overlapping_completions_flag_same_patch(fx,monkeypatch):
    trial=fx.prepare(fx.start())
    trial=trials.prepare(trial['id'],task_id='fix',arm_id='baseline',repetition=2,expected_version=trial['version'],trusted=True,db=fx.db)
    a,b=trial['attempts']
    for attempt in (a,b): Path(attempt['worktree'],'code.py').write_text('value = 1\n')
    original=trials._run_check; nested=[]
    def run(*args,**kwargs):
        if not nested:
            nested.append(True)
            trials.complete(trial['id'],b['id'],expected_version=trials.get(trial['id'],db=fx.db)['version'],trusted=True,db=fx.db)
        return original(*args,**kwargs)
    monkeypatch.setattr(trials,'_run_check',run)
    done=trials.complete(trial['id'],a['id'],expected_version=trial['version'],trusted=True,db=fx.db)
    assert done['summary']['accepted']==2
    assert all(a['result']['duplicate_patch_hash'] for a in done['attempts'])


@pytest.mark.parametrize('policy',[dict(total_seconds=10),dict(check_seconds=86000,total_seconds=86400)])
def test_impossible_or_excessive_check_policy_rejected(fx,policy):
    fx.spec['policy'].update(policy)
    with pytest.raises(ValueError,match='policy'): fx.start()


def test_abandoned_check_closed_unknown_without_retry(fx):
    trial=fx.prepare(fx.start()); aid=trial['attempts'][0]['id']
    trial=trials._update(trial['id'],trial['version'],lambda body: body['attempts'][0].update(state='CHECKING'),fx.db)
    done=trials.abort(trial['id'],aid,expected_version=trial['version'],reason='Inspected abandoned check after process crash',trusted=True,db=fx.db)
    assert done['attempts'][0]['state']=='REVIEW_REQUIRED'
    assert done['attempts'][0]['external_outcome']=='unknown'
    assert done['summary']['finished']==1 and done['summary']['accepted']==0
    with pytest.raises(ValueError,match='no blind retry'): fx.complete(done)


def test_repo_import_does_not_write_bytecode_or_invalidate_fix(fx):
    protocol(fx,'import code as m\nraise SystemExit(0 if m.value == 1 else 1)\n')
    trial=fx.prepare(fx.start()); tree=Path(trial['attempts'][0]['worktree'])
    (tree/'code.py').write_text('value = 1\n')
    done=fx.complete(trial)
    assert done['attempts'][0]['state']=='ACCEPTED'
    assert not (tree/'__pycache__').exists()


def test_worktree_pathlib_cannot_shadow_frozen_check(fx):
    trial=fx.prepare(fx.start()); tree=Path(trial['attempts'][0]['worktree'])
    (tree/'pathlib.py').write_text("class Path:\n def __init__(self,*args): pass\n def read_text(self): return 'value = 1'\n")
    done=fx.complete(trial)
    assert done['attempts'][0]['state']=='REJECTED'
    assert (tree/'code.py').read_text()=='value = 0\n'


def test_ignored_startup_hook_captured_but_not_executed(fx):
    trial=fx.prepare(fx.start()); tree=Path(trial['attempts'][0]['worktree'])
    (tree/'code.py').write_text('value = 2\n'); (tree/'.gitignore').write_text('*\n')
    (tree/'sitecustomize.py').write_text('import os\nos._exit(0)\n')
    done=fx.complete(trial); result=done['attempts'][0]['result']
    assert done['attempts'][0]['state']=='REJECTED'
    assert set(result['untracked_hashes'])=={'.gitignore','sitecustomize.py'}
    assert Path(tree.parent,'untracked','sitecustomize.py').exists()


@pytest.mark.parametrize('target',["../attempt.patch","../untracked/new.py"])
def test_capture_artifact_tampering_invalidates_result(fx,target):
    protocol(fx,f"from pathlib import Path\nPath({target!r}).write_bytes(b'tampered')\nraise SystemExit(0)\n")
    trial=fx.prepare(fx.start()); tree=Path(trial['attempts'][0]['worktree'])
    (tree/'code.py').write_text('value = 1\n'); (tree/'new.py').write_text('pass\n')
    done=fx.complete(trial)
    assert done['attempts'][0]['state']=='INVALID'
    assert 'artifact changed' in done['attempts'][0]['result']['error']


def test_missing_protocol_check_hash_has_named_error(fx):
    protocol(fx,missing_hash=True)
    with pytest.raises(ValueError,match='frozen acceptance check SHA256'): fx.start()
