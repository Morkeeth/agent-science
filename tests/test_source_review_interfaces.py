"""Real CLI/MCP against a synthetic correction, never live correction evidence."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import test_source_reviews as fixtures
from clearance import cases, synthesis


def mcp(args):
    request={'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'science_research','arguments':args}}
    p=subprocess.run([sys.executable,'-m','clearance.mcp_server'],input=json.dumps(request)+'\n',text=True,capture_output=True,timeout=30)
    assert p.returncode==0,p.stderr
    result=json.loads(p.stdout)['result']
    return result,json.loads(result['content'][0]['text'])


def test_cli_and_mcp_review_preserve_notice_and_flag_decision(tmp_path):
    db=str(tmp_path/'cases.db');data=fixtures.fixture(db)
    cases.decide(data['id'],'Retain the scoped comparator assumption.','A correction must be assessed before accepting this decision.', ['paper'],expected_version=data['version'],db=db)
    result,pending=mcp({'action':'source-reviews','case_id':data['id'],'db':db})
    assert not result['isError'] and len(pending['pending'])==1
    from clearance.mcp_server import TOOLS
    schema=next(t for t in TOOLS if t['name']=='science_research')['inputSchema']['properties']['source_review']
    assert 'notice_identity' in schema['properties']['notices']['items']['required']
    assert set(schema['properties']['disposition']['enum'])=={'unaffected','revise','unresolved'}
    good=fixtures.proposal(data,db);bad=copy.deepcopy(good)
    bad['notices'][0]['quote']='This quote does not occur in the frozen correction notice.'
    result,error=mcp({'action':'source-review','case_id':data['id'],'version':data['version'],'source_review':bad,'db':db})
    assert result['isError'] and 'exact' in error['error']
    assert cases.get(data['id'],db=db)['version']==data['version']
    path=tmp_path/'review.json';path.write_text(json.dumps(good))
    p=subprocess.run([sys.executable,'-m','clearance','research','source-review',data['id'],'--version',str(data['version']),'--review-file',str(path),'--db',db,'--json'],capture_output=True,text=True,timeout=30)
    assert p.returncode==0,p.stderr
    saved=json.loads(p.stdout);assert len(saved['resolved'])==1 and not saved['pending']
    current=cases.get(data['id'],db=db)
    assert current['evidence']==data['evidence']
    assert current['decisions'][0]['review']['state']=='REVIEW_REQUIRED'
    assert synthesis.build(current)['conclusions'][0]['state']=='CURRENT'
    assert synthesis.build(cases.get(data['id'],version=data['version'],db=db))['conclusions'][0]['state']=='REVIEW_REQUIRED'
    result,error=mcp({'action':'source-review','case_id':data['id'],'version':data['version'],'source_review':good,'db':db})
    assert result['isError'] and 'version changed' in error['error']
    # The host can also record unresolved; this does not clear an inspected warning.
    unresolved=copy.deepcopy(good);unresolved.update(disposition='unresolved',notices=[],rationale='The notice interpretation needs another independent source review.')
    result,reopened=mcp({'action':'source-review','case_id':data['id'],'version':current['version'],'source_review':unresolved,'db':db})
    assert not result['isError'] and len(reopened['pending'])==1
    p=subprocess.run([sys.executable,'-m','clearance','research','source-reviews',data['id'],'--db',db],capture_output=True,text=True,timeout=30)
    assert p.returncode==0 and '1 pending' in p.stdout and 'unresolved' in p.stdout


def test_identical_review_does_not_change_decision_or_synthesis(tmp_path):
    from clearance import source_reviews
    db=str(tmp_path/'cases.db');data=fixtures.fixture(db);proposal=fixtures.proposal(data,db)
    source_reviews.review(data['id'],data['version'],proposal,db=db)
    reviewed=cases.get(data['id'],db=db)
    cases.decide(data['id'],'Retain the inspected comparator.','The scoped notice leaves the comparator unchanged.', ['paper'],expected_version=reviewed['version'],db=db)
    source_reviews.review(data['id'],reviewed['version'],proposal,db=db)
    current=cases.get(data['id'],db=db)
    assert current['decisions'][0]['review']['state']=='UNCHANGED_IN_SNAPSHOT'
    assert not synthesis.compare(data['id'],reviewed['version'],db=db)['material_change']


def test_new_registry_notice_does_not_erase_an_earlier_warning(tmp_path):
    from clearance import source_metadata, source_reviews
    db=str(tmp_path/'cases.db');data=fixtures.fixture(db)
    source=data['evidence'][0];prior=copy.deepcopy(source['metadata_review_required'])
    metadata=copy.deepcopy(source['source_metadata'])
    for record in metadata['records']:
        for relation in record['relations']: relation['notice']='doi:10.1234/new-notice'
    updated=source_metadata.apply(data['id'],data['version'],source['id'],metadata,db=db)
    warnings=updated['evidence'][0]['metadata_review_required']
    assert all(w in warnings for w in prior)
    assert {w['notice'] for w in warnings}=={'doi:10.1234/notice','doi:10.1234/new-notice'}
    assert len(source_reviews.list_pending(data['id'],db=db)['pending'][0]['notice_identities'])==2


def test_unavailable_source_can_record_unresolved_through_mcp(tmp_path):
    from clearance import source_reviews
    from clearance.mcp_server import TOOLS
    db=str(tmp_path/'cases.db');data=fixtures.fixture(db)
    data['evidence'][0].update(snapshot_text='',snapshot_hash=None,status='UNAVAILABLE')
    data['version']+=1;cases._save(data,db=db)
    row=source_reviews.list_pending(data['id'],db=db)['pending'][0]
    proposal={key:row[key] for key in ('assessment_id','evidence_id','source_snapshot_hash','warning_fingerprint')}
    proposal.update(disposition='unresolved',notices=[],rationale='The original source is unavailable, so the correction effect remains unresolved.')
    tool=next(t for t in TOOLS if t['name']=='science_research')
    assert 'source-review' in tool['description']
    assert 'null' in tool['inputSchema']['properties']['source_review']['properties']['source_snapshot_hash']['type']
    result,saved=mcp({'action':'source-review','case_id':data['id'],'version':data['version'],'source_review':proposal,'db':db})
    assert not result['isError'],saved
    assert saved['pending'][0]['source_snapshot_hash'] is None
    assert saved['pending'][0]['review']['disposition']=='unresolved'
    assert synthesis.build(cases.get(data['id'],db=db))['conclusions'][0]['state']=='REVIEW_REQUIRED'
    proposal['disposition']='unaffected'
    result,error=mcp({'action':'source-review','case_id':data['id'],'version':saved['version'],'source_review':proposal,'db':db})
    assert result['isError']
    assert cases.get(data['id'],db=db)['version']==saved['version']


def test_mirror_warning_flags_evidence_only_decision(tmp_path):
    db=str(tmp_path/'cases.db');data=fixtures.fixture(db)
    paper=data['evidence'][0]
    mirror={k:v for k,v in paper.items() if k not in ('source_metadata','metadata_review_required')}
    mirror.update(id='mirror',url='https://dx.doi.org/10.1234/paper?download=pdf')
    data['evidence'].append(mirror);data['claims']=[]
    before=copy.deepcopy(data)
    before['evidence'][0].pop('metadata_review_required',None)
    before['evidence'][0].pop('source_metadata',None)
    decision={'evidence_ids':['mirror']}
    review=cases.decision_review(decision,before,data)
    assert review['state']=='REVIEW_REQUIRED'
    assert any(c['kind']=='source_metadata_changed' and c['evidence_id']=='mirror' for c in review['changes'])
    assert cases.decision_review(decision,data,data)['state']=='UNCHANGED_IN_SNAPSHOT'
