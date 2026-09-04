"""Frozen user-flow acceptance, not a scientific quality benchmark. No web calls."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

with tempfile.TemporaryDirectory(prefix='science-flow-check-') as temp:
    db=str(Path(temp)/'cases.db')
    def run(*args):
        proc=subprocess.run([sys.executable,'-m','clearance','research',*args,'--db',db,'--json'],capture_output=True,text=True,timeout=20)
        if proc.returncode:
            raise AssertionError(proc.stderr or proc.stdout)
        return json.loads(proc.stdout)
    planned=run('When should an agent ask for human intervention?')
    assert planned['status']=='awaiting_reasoning' and not planned['steps']
    cid,rid=planned['case_id'],planned['id']
    context=run('context',rid)
    assert context['case_version']==1 and not context['evidence']
    run('follow',cid)
    proposal={'case_version':1,'findings':[{'statement':'This case has no evidence establishing an intervention policy.',
        'relation':'unresolved','rationale':'No source has been retrieved or inspected in this local acceptance run.',
        'strongest_challenge':'A controlled comparison may identify an effective intervention policy.',
        'what_would_change':'A relevant controlled comparison with task outcomes would allow this question to be assessed.'}],
        'next_action':{'kind':'finish','reason':'Insufficient evidence is explicitly unresolved; no provider calls were made.'}}
    completed=run('resume',rid,'--proposal',json.dumps(proposal))
    assert completed['status']=='completed' and completed['case_version']==2
    answer=run('show','--case-id',cid)
    assert answer['conclusions'][0]['relation']=='unresolved'
    assert answer['gaps']
    before=run('show','--case-id',cid,'--version','1')
    assert not before['conclusions']
    report=run('compare',cid,'--from-version','1')
    assert report['reasoning_changes'] and report['changed']
    updates=run('updates')
    assert len(updates['updates'])==1 and updates['checked_online'] is False
    challenge=run('challenge',cid)
    assert challenge['base_case_version']==2 and challenge['challenges']
    cancelled=run('cancel',challenge['id'])
    assert cancelled['status']=='cancelled'
    print(json.dumps({'flow':'start/context/host-proposal/history/compare/follow/challenge/cancel','passed':True,'live_calls':0,'meaning':'Functional acceptance only; no scientific effectiveness was measured.'}))
