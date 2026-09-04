"""Actual CLI/MCP boundaries over isolated, explicitly synthetic source fixtures."""
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

from clearance import cases, instruments, research, synthesis, research_workflow

QUOTE='The evaluated workflows improved completion on maintenance tasks with independent checks.'
COUNTER='The replication found no improvement on the evaluated maintenance tasks with independent checks.'


def seed(db):
    def snapshot(url, **kwargs):
        text=COUNTER if url.endswith('replication') else QUOTE
        return {'text':text,'sha256':cases.digest(text),'fetched_at':'2026-09-04T00:00:00Z','cache_hit':True}
    with patch.object(instruments,'document_snapshot',side_effect=snapshot):
        return research.import_report('Do these workflows improve maintenance outcomes?',
            'A workflow may improve maintenance outcomes.[1]\n\n[1] https://example.org/study\n[2] https://example.org/replication',db=db)


def call(arguments):
    message={'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'science_research','arguments':arguments}}
    proc=subprocess.run([sys.executable,'-m','clearance.mcp_server'],input=json.dumps(message)+'\n',capture_output=True,text=True,timeout=20)
    assert proc.returncode==0,proc.stderr
    result=json.loads(proc.stdout)['result']
    return result,json.loads(result['content'][0]['text'])


def finding(data, relation='supports'):
    quote=QUOTE if relation=='supports' else COUNTER
    evidence=next(e for e in data['evidence'] if quote in e.get('snapshot_text',''))
    return {'statement':'These evaluated workflows improve maintenance outcomes.', 'relation':relation,
        'rationale':'Limited to the reported tasks and independent acceptance checks.',
        'evidence_id':evidence['id'],'quote':quote,
        'strongest_challenge':'An independent replication could fail to reproduce the reported improvement.',
        'what_would_change':'A matched replication measuring actual accepted maintenance changes could reverse this conclusion.',
        'conditions':[{'field':'task','value':'maintenance tasks','evidence_id':evidence['id'],'quote':quote}]}


def test_actual_cli_shorthand_starts_without_network_or_keys(tmp_path):
    db=tmp_path/'cases.db'
    proc=subprocess.run([sys.executable,'-m','clearance','research','When should an agent request intervention?','--db',str(db),'--json'],capture_output=True,text=True,timeout=20)
    assert proc.returncode==0,proc.stderr
    run=json.loads(proc.stdout)
    assert run['status']=='awaiting_reasoning'
    assert not run['steps']
    assert all(v==0 for v in run['usage'].values())


def test_real_mcp_host_proposal_challenge_compare_follow(tmp_path):
    db=tmp_path/'cases.db';data=seed(db)
    status,run=call({'action':'start','case_id':data['id'],'db':str(db)})
    assert not status['isError']
    status,run=call({'action':'resume','run_id':run['id'],'db':str(db),'proposal':{
        'case_version':data['version'],'findings':[finding(data)],
        'next_action':{'kind':'finish','reason':'Bounded conclusion from the inspected maintenance study.'}}})
    assert not status['isError'],run
    assert run['status']=='completed'
    call({'action':'follow','case_id':data['id'],'db':str(db)})
    status,challenge=call({'action':'challenge','case_id':data['id'],'db':str(db)})
    assert not status['isError']
    assert challenge['base_case_version']==2 and challenge['challenges']
    status,context=call({'action':'context','run_id':challenge['id'],'db':str(db)})
    assert not status['isError'] and context['challenge']
    status,done=call({'action':'resume','run_id':challenge['id'],'db':str(db),'proposal':{
        'case_version':2,'findings':[finding(data,'contradicts')],
        'next_action':{'kind':'finish','reason':'The saved replication challenges the first result; keep the choice disputed.'}}})
    assert not status['isError'],done
    status,report=call({'action':'compare','case_id':data['id'],'from_version':2,'db':str(db)})
    assert report['changed'] and report['reasoning_changes']
    status,updates=call({'action':'updates','db':str(db)})
    assert not updates['checked_online'] and len(updates['updates'])==1
    _,again=call({'action':'updates','db':str(db)})
    assert updates==again
    assert cases.get(data['id'],version=2,db=db)['version']==2


def test_real_mcp_rejects_invalid_arguments_and_execution(tmp_path):
    for args in [{'action':'execute-protocol'},{'action':'resume','run_id':'x','proposal':[]}, {'action':'compare','case_id':'x','from_version':True}, {'action':'updates','live':'true'}]:
        result,body=call({**args,'db':str(tmp_path/'cases.db')})
        assert result['isError'] and 'error' in body


def test_no_raw_experiment_output_in_new_answer_surface(tmp_path):
    data=seed(tmp_path/'cases.db')
    data['experiments']=[{'id':'e','acceptance_source':'PRIVATE_SCRIPT_SENTINEL','runs':[{'output_tail':'PRIVATE_OUTPUT_SENTINEL','exit_code':0}]}]
    output=json.dumps(synthesis.build(data))
    assert 'PRIVATE_SCRIPT_SENTINEL' not in output
    assert 'PRIVATE_OUTPUT_SENTINEL' not in output
