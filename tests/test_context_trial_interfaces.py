"""Exercise real terminal/MCP boundaries; artificial task is not an agent trial."""
import json
from pathlib import Path
import subprocess
import sys
import test_context_trials as fixtures


def cli(*args):
    return subprocess.run([sys.executable,'-m','clearance','research',*args],text=True,capture_output=True,timeout=30)


def mcp(args):
    request={'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'science_research','arguments':args}}
    p=subprocess.run([sys.executable,'-m','clearance.mcp_server'],input=json.dumps(request)+'\n',text=True,capture_output=True,timeout=30)
    assert p.returncode==0,p.stderr
    result=json.loads(p.stdout)['result']
    return result,json.loads(result['content'][0]['text'])


def test_cli_prepares_executes_and_aborts_while_mcp_only_plans():
    fixture=fixtures.ContextTrials();fixture.setUp()
    try:
        result,trial=mcp({'action':'context-trial-create','trial_spec':fixture.spec,'db':fixture.db})
        assert not result['isError'],trial
        assert trial['summary']['prepared']==0
        result,error=mcp({'action':'context-trial-prepare','trial_id':trial['id'],'db':fixture.db})
        assert result['isError'] and 'unknown research action' in error['error'].lower()
        p=cli('context-trial-prepare',trial['id'],'--task','fix','--arm','baseline','--repetition','1','--expected-version','1','--trusted','--db',fixture.db,'--json')
        assert p.returncode==0,p.stderr
        trial=json.loads(p.stdout);attempt=trial['attempts'][0]
        (Path(attempt['worktree'])/'code.py').write_text('value = 1\n')
        p=cli('context-trial-complete',trial['id'],'--attempt',attempt['id'],'--expected-version',str(trial['version']),'--trusted','--db',fixture.db,'--json')
        assert p.returncode==0,p.stderr
        trial=json.loads(p.stdout)
        assert trial['attempts'][0]['state']=='ACCEPTED'
        result,shown=mcp({'action':'context-trial-show','trial_id':trial['id'],'db':fixture.db})
        assert not result['isError'] and shown['summary']['accepted']==1
        result,linked=mcp({'action':'context-trials','case_id':trial['manifest']['case_id'],'db':fixture.db})
        assert not result['isError'] and linked['trials'][0]['id']==trial['id']
        assert linked['trials'][0]['summary']['accepted']==1
        p=cli('context-trials',trial['manifest']['case_id'],'--db',fixture.db)
        assert p.returncode==0 and trial['id'] in p.stdout
        from clearance import cases, context_trials
        other=cases.create('An unrelated case',db=fixture.db)
        assert context_trials.for_case(other['id'],db=fixture.db)['trials']==[]
        assert context_trials.for_case(trial['manifest']['case_id'],case_version=1,db=fixture.db)['trials']==[]

        p=cli('context-trial-show',trial['id'],'--db',fixture.db)
        assert p.returncode==0 and '1/4 attempts finished' in p.stdout
        p=cli('context-trial-prepare',trial['id'],'--task','fix','--arm','candidate','--repetition','1','--expected-version',str(trial['version']),'--trusted','--db',fixture.db,'--json')
        assert p.returncode==0,p.stderr
        trial=json.loads(p.stdout)
        p=cli('context-trial-abort',trial['id'],'--attempt',trial['attempts'][-1]['id'],'--expected-version',str(trial['version']),'--reason','Host did not execute this fixture attempt.','--trusted','--db',fixture.db,'--json')
        assert p.returncode==0,p.stderr
        trial=json.loads(p.stdout)
        assert trial['attempts'][-1]['state']=='CANCELLED' and trial['summary']['denominator']==4
    finally:
        fixture.doCleanups()
