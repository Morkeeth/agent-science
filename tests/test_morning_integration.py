"""Real entry points with synthetic local evidence and registry transport fixtures."""
import json
import subprocess
import sys
import pytest
from unittest.mock import patch
from clearance import cases, research, synthesis, night_runs, research_policy, source_metadata, research_evaluation

QUESTION='When do repository context files help coding agents?'
TEXT='Repository context files helped selected maintenance tasks, while the source does not establish general effectiveness.'
LIMITS={'discovery_calls':0,'document_reads':2,'reasoning_calls':0,'rounds':1}


def seed(db):
    with patch('clearance.instruments.document_snapshot',return_value={'text':TEXT,'sha256':cases.digest(TEXT),'cache_hit':True}):
        return research.import_report(QUESTION,'Reported result.[1]\n\n[1] https://doi.org/10.1234/trial',db=db)


def mcp(args):
    msg={'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'science_research','arguments':args}}
    p=subprocess.run([sys.executable,'-m','clearance.mcp_server'],input=json.dumps(msg)+'\n',capture_output=True,text=True,timeout=30)
    assert p.returncode==0,p.stderr
    result=json.loads(p.stdout)['result']
    return result,json.loads(result['content'][0]['text'])


def test_registry_action_reserves_policy_and_updates_decision_without_changing_body(tmp_path):
    db=str(tmp_path/'metadata.db');data=seed(db);e=data['evidence'][0]
    f={'statement':'Repository context can help selected tasks.','relation':'supports','rationale':'Authored artificial interpretation.',
       'evidence_id':e['id'],'quote':TEXT,'strongest_challenge':'A correction could invalidate the reported task outcome.',
       'what_would_change':'A corrected primary result removes the observed task effect.'}
    data=synthesis.apply(data['id'],1,{'findings':[f]},db=db)
    data=cases.decide(data['id'],'Try a controlled context comparison.','Limited to selected tasks.',[e['id']],expected_version=2,db=db)
    run=night_runs.start(QUESTION,case_id=data['id'],policy={**LIMITS,'aggregate':{'id':'fixture','limits':LIMITS}},db=db)
    proposal={'case_version':2,'next_action':{'kind':'metadata','evidence_id':e['id'],'reason':'Check the primary registry for a correction.','metadata':{'retracted':True}}}
    with pytest.raises(ValueError,match='registry results'):
        night_runs.resume(run['id'],proposal=proposal,live=True,db=db)
    proposal['next_action'].pop('metadata')
    with patch.object(source_metadata,'_fetch',side_effect=AssertionError('unapproved request')):
        assert night_runs.resume(run['id'],proposal=proposal,live=True,db=db)['status']=='paused'
    research_policy.approve({'aggregate':{'id':'fixture','limits':LIMITS}},db=db)
    body=json.dumps({'message':{'DOI':'10.1234/trial','updated-by':[{'DOI':'10.1234/correction','type':'correction'}]}}).encode()
    with patch.object(source_metadata,'_fetch',return_value=(body,200)) as fetched:
        done=night_runs.resume(run['id'],proposal=proposal,live=True,db=db)
    assert fetched.call_count==1 and done['usage']['document_reads']==1
    assert done['observed_usage']['metadata_responses']==1
    after=cases.get(data['id'],db=db)
    assert after['version']==3 and after['checked_at']==data['checked_at']
    assert after['evidence'][0]['snapshot_hash']==e['snapshot_hash']
    assert not after['evidence'][0].get('retracted')
    assert after['decisions'][0]['review']['state']=='REVIEW_REQUIRED'
    result,answer=mcp({'action':'show','case_id':data['id'],'db':db})
    assert not result['isError'] and answer['conclusions'][0]['state']=='REVIEW_REQUIRED'
    assert cases.get(data['id'],version=2,db=db)['decisions'][0]['review']['state']=='UNCHANGED_IN_SNAPSHOT'
    assert done['steps'][-1]['elapsed_seconds']>=0
    assert len(done['steps'][-1]['runtime']['source_sha256'])==64
    with patch('clearance.instruments.document_snapshot',return_value={'text':TEXT,'sha256':cases.digest(TEXT),'cache_hit':True}):
        refreshed=cases.refresh(data['id'],db=db)
    assert refreshed['evidence'][0]['metadata_review_required']
    revised=synthesis.apply(data['id'],refreshed['version'],{'findings':[dict(f,statement='This corrected source needs further interpretation.')]},db=db)
    assert all(c['state']=='REVIEW_REQUIRED' for c in synthesis.build(revised)['conclusions'])


def test_evaluation_cli_and_mcp_keep_frozen_denominator_and_unknowns(tmp_path):
    db=str(tmp_path/'evaluation.db')
    spec={'title':'Independent protocol control','authored_by':'fixture author','rubric_provenance':'Written before the fixture answer.',
        'questions':[{'id':'q','topic':'memory','question':QUESTION,'expected_distinctions':['Task scope is not general effectiveness.']}],
        'arms':[{'id':'baseline','kind':'retrieval','baseline_policy':'Retrieve original saved sources only.', 'mode':'snapshot_replay','resource_limits':LIMITS},
                {'id':'candidate','kind':'synthesis','code_ref':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'mode':'snapshot_replay','resource_limits':LIMITS}],
        'repetitions':1,'rubric':{k:'Independently inspect '+k for k in research_evaluation.CRITERIA}}
    path=tmp_path/'spec.json';path.write_text(json.dumps(spec))
    p=subprocess.run([sys.executable,'-m','clearance','research','evaluation-create','--spec-file',str(path),'--db',db,'--json'],text=True,capture_output=True,timeout=30)
    assert p.returncode==0,p.stderr
    campaign=json.loads(p.stdout)
    data=seed(db);run=night_runs.start(QUESTION,case_id=data['id'],policy=LIMITS,db=db)
    run=night_runs.resume(run['id'],proposal={'case_version':1,'next_action':{'kind':'finish','reason':'Artificial source does not establish an effect.'},'findings':[{'statement':'General effectiveness remains unresolved.','relation':'unresolved','rationale':'This fixture does not establish a general effect.'}]},db=db)
    observation={'arm_id':'candidate','question_id':'q','repetition':1,'case_id':data['id'],'case_version':run['case_version'],'run_id':run['id'],
        'question_hash':cases.digest(QUESTION),'mode':'snapshot_replay','resource_limits':LIMITS,'reviewer':'independent fixture reviewer',
        'judgments':{k:{'status':'unknown','rationale':'Not measured in this artificial entry-point test.','anchors':[]} for k in research_evaluation.CRITERIA}}
    result,recorded=mcp({'action':'evaluation-record','evaluation_id':campaign['id'],'observation':observation,'db':db})
    assert not result['isError'],recorded
    assert recorded['coverage']['recorded']==1 and recorded['coverage']['denominator']==2
    assert not recorded['paired_comparability'][0]['comparable_design']
    assert recorded['observations'][0]['operational']['latency_seconds'] is None
    result,error=mcp({'action':'evaluation-record','evaluation_id':campaign['id'],'observation':observation,'db':db})
    assert result['isError'] and 'duplicate' in error['error']
    review={k:observation[k] for k in ('arm_id','question_id','repetition','reviewer','judgments')}
    review['expected_review_version']=0
    review['judgments']['citation_correctness']={'status':'pass','rationale':'Exact fixture passage inspected; no scientific effectiveness claim.',
        'anchors':[{'evidence_id':data['evidence'][0]['id'],'quote':TEXT}]}
    result,reviewed=mcp({'action':'evaluation-review','evaluation_id':campaign['id'],'evaluation_review':review,'db':db})
    assert not result['isError'],reviewed
    assert reviewed['observations'][0]['review_version']==1
    assert reviewed['observations'][0]['judgments']['citation_correctness']['status']=='unknown'
    path=tmp_path/'review.json';path.write_text(json.dumps(review))
    p=subprocess.run([sys.executable,'-m','clearance','research','evaluation-review',campaign['id'],'--review-file',str(path),'--db',db,'--json'],text=True,capture_output=True,timeout=30)
    assert p.returncode==2 and 'version' in p.stderr
    review['expected_review_version']=1;path.write_text(json.dumps(review))
    p=subprocess.run([sys.executable,'-m','clearance','research','evaluation-review',campaign['id'],'--review-file',str(path),'--db',db,'--json'],text=True,capture_output=True,timeout=30)
    assert p.returncode==0,p.stderr
    assert json.loads(p.stdout)['observations'][0]['review_version']==2


def test_metadata_offline_then_live_and_failed_receipt(tmp_path):
    db=str(tmp_path/'retry.db');data=seed(db)
    limits={**LIMITS,'document_reads':1}
    policy={**limits,'aggregate':{'id':'one-read','limits':limits}}
    research_policy.approve(policy,db=db)
    run=night_runs.start(QUESTION,case_id=data['id'],policy=policy,db=db)
    proposal={'case_version':1,'next_action':{'kind':'metadata','evidence_id':data['evidence'][0]['id'],'reason':'Inspect registry status.'}}
    offline=night_runs.resume(run['id'],proposal=proposal,db=db)
    assert offline['case_version']==1 and offline['usage'].get('document_reads',0)==0
    with patch.object(source_metadata,'_fetch',side_effect=OSError('network unavailable')) as fetch:
        online=night_runs.resume(run['id'],proposal=proposal,live=True,db=db)
    assert fetch.call_count==1
    assert online['case_version']==1 and online['usage']['document_reads']==1
    assert online['steps'][-1]['observed_events'][0]['outcome']=='failed'
    assert cases.get(data['id'],db=db)['version']==1


def test_unsupported_metadata_reserves_no_capacity(tmp_path):
    db=str(tmp_path/'unsupported.db')
    data=research.import_report(QUESTION,'Source.[1]\n\n[1] https://example.org/no-identifier',db=db)
    run=night_runs.start(QUESTION,case_id=data['id'],policy=LIMITS,db=db)
    proposal={'case_version':1,'next_action':{'kind':'metadata','evidence_id':data['evidence'][0]['id'],'reason':'Inspect registry status.'}}
    with pytest.raises(ValueError,match='no capacity reserved'):
        night_runs.resume(run['id'],proposal=proposal,live=True,db=db)
    after=night_runs.get(run['id'],db=db)
    assert after['usage']==run['usage'] and after['steps']==run['steps']
    assert cases.get(data['id'],db=db)['version']==1
