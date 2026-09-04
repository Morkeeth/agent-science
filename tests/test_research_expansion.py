"""Independent expected outcomes over document effects and real process boundaries."""
import io
import json
import subprocess
import sys
import urllib.error
from pathlib import Path
from unittest.mock import patch
import pytest
from clearance import cases, research, discovery, instruments, case_review

A='https://example.org/study'
B='https://example.net/replication'
QUOTE='Fresh sessions reduced repeated errors on the evaluated maintenance tasks.'
COUNTER='Fresh sessions increased repeated errors on the evaluated maintenance tasks.'
REPORT=f'# Report\n\nFresh sessions reduce errors.[1]\n\nThe result generalizes to every repository.\n\n[1] {A}\n'


def snapshot(url,**kwargs):
    text=QUOTE if url==A else COUNTER
    return {'text':text,'sha256':cases.digest(text),'fetched_at':'2026-09-04T00:00:00Z','cache_hit':True}


def imported(tmp_path):
    db=tmp_path/'cases.db'
    with patch.object(instruments,'document_snapshot',side_effect=snapshot):
        data=research.import_report('Fresh sessions',REPORT,db=db)
    return db,data


def test_import_report_claims_remain_unresolved_and_original_is_inspectable(tmp_path):
    db,data=imported(tmp_path)
    assert len(data['claims'])==2
    assert data['claims'][0]['source_urls']==[A]
    assert data['claims'][1]['source_urls']==[]
    assert all(c['state']=='UNRESOLVED' for c in research.brief(data)['claims'])
    assert 'text' not in cases.public_view(data)['report']
    assert research.report_source(data['id'],db=db)['text']==REPORT
    chunk=research.report_source(data['id'],db=db,limit=10)
    assert chunk['next_offset']==10 and chunk['text']==REPORT[:10]


def test_sonar_json_citations_and_markdown_heading_content():
    result=research.parse_report(json.dumps({'choices':[{'message':{'content':'# Heading\nA report assertion.[1]'}}],'citations':[A]}))
    assert result['passages'][0]['source_urls']==[A]
    assert result['passages'][0]['statement']=='A report assertion.[1]'


def test_import_never_searches_and_reports_unread_citations(tmp_path):
    report=REPORT+'\n[2] '+B+'\n'
    with patch.object(discovery,'find',side_effect=AssertionError('no discovery')),patch.object(instruments,'document_snapshot',side_effect=snapshot):
        data=research.import_report('Fresh sessions',report,max_documents=1,db=tmp_path/'cases.db')
    assert research.brief(data)['unread_report_citations']==[B]
    assert any(e.get('reason')=='case source limit reached' for e in data['trace'])


def test_support_contradiction_stale_refresh_review_and_assessment_replacement(tmp_path):
    db,data=imported(tmp_path);cid=data['id'];claim=data['claims'][0]['id'];eid=data['evidence'][0]['id']
    assessed=research.assess(cid,1,claim_id=claim,statement=None,relation='supports',rationale='The study measured this task type.',evidence_id=eid,quote=QUOTE,db=db)
    assert research.brief(assessed)['claims'][0]['state']=='SUPPORTED_AS_ASSESSED'
    with patch.object(discovery,'find',return_value=[cases.search.Candidate(B,'Replication',COUNTER)]),patch.object(instruments,'document_snapshot',side_effect=snapshot):
        expanded=research.investigate(cid,2,query='fresh sessions replication failures',providers=['parallel','perplexity'],db=db)
    assert len(expanded['evidence'])==2
    assert expanded['evidence'][1]['discovered_by']==['parallel','perplexity']
    opposing=research.assess(cid,3,claim_id=claim,statement=None,relation='contradicts',rationale='The replication measured the opposite direction.',evidence_id=expanded['evidence'][1]['id'],quote=COUNTER,db=db)
    assert research.brief(opposing)['claims'][0]['state']=='CONTESTED'
    with patch.object(instruments,'document_snapshot',return_value=None):refreshed=cases.refresh(cid,db=db)
    brief=research.brief(refreshed)
    assert brief['claims'][0]['state']=='REVIEW_REQUIRED'
    assert case_review.index(db=db,review_only=True)['cases'][0]['claim_review_required']==1
    assert research.brief(cases.get(cid,version=4,db=db))['claims'][0]['state']=='CONTESTED'
    old=refreshed['claims'][0]['assessments'][0]['id']
    changed=research.assess(cid,5,claim_id=claim,statement=None,relation='unresolved',rationale='Source unavailable; withdraw this assessment.',supersedes=old,db=db)
    assert research.brief(changed)['claims'][0]['assessments'][0]['state']=='SUPERSEDED'
    with pytest.raises(ValueError,match='active assessment'):
        research.assess(cid,6,claim_id=claim,statement=None,relation='unresolved',rationale='Duplicate replacement',supersedes=old,db=db)


def test_fabricated_quote_wrong_case_and_stale_write_are_rejected(tmp_path):
    db,data=imported(tmp_path)
    for eid,quote in [(data['evidence'][0]['id'],'Invented evidence from a nonexistent experiment.'),('another-case',QUOTE)]:
        with pytest.raises(ValueError,match='exact'):
            research.assess(data['id'],1,statement='Fresh sessions help',relation='supports',rationale='Test',evidence_id=eid,quote=quote,db=db)
    research.assess(data['id'],1,statement='Uncertain',relation='unresolved',rationale='No matching study',db=db)
    with pytest.raises(ValueError,match='version changed'):
        research.assess(data['id'],1,statement='Stale',relation='unresolved',rationale='No evidence',db=db)
    assert len(cases.get(data['id'],db=db)['claims'])==3


def test_write_race_does_not_overwrite_new_revision(tmp_path):
    db,data=imported(tmp_path);save=research._save
    def racing_save(draft,db):
        cases.refresh(data['id'],db=db)
        return save(draft,db)
    with patch.object(research,'_save',side_effect=racing_save),patch.object(instruments,'document_snapshot',side_effect=snapshot):
        with pytest.raises(ValueError,match='changed during refresh'):
            research.assess(data['id'],1,statement='Race',relation='unresolved',rationale='No data',db=db)
    assert len(cases.get(data['id'],db=db)['claims'])==2


def test_perplexity_wire_contract_and_no_secret_in_trace(monkeypatch):
    monkeypatch.setenv('PERPLEXITY_API_KEY','test-secret-not-real')
    response={'id':'request-123','results':[{'title':'Study','url':A,'snippet':QUOTE,'date':'2026-01-01','last_updated':'2026-09-01'}]}
    requests=[]
    def transport(request,**kwargs):
        requests.append(request)
        return io.BytesIO(json.dumps(response).encode())
    trace=[]
    with patch.object(discovery.urllib.request,'urlopen',side_effect=transport):
        out=discovery.find('perplexity','public query',live=True,limit=3,trace=trace)
    assert out[0].url==A and out[0].excerpt==QUOTE
    assert json.loads(requests[0].data)=={'query':'public query','max_results':3,'search_context_size':'medium'}
    assert requests[0].get_header('Authorization')=='Bearer test-secret-not-real'
    assert trace[0]['search_id']=='request-123' and 'test-secret' not in json.dumps(trace)


def test_perplexity_offline_missing_key_and_failed_response_are_explicit(monkeypatch):
    monkeypatch.delenv('PERPLEXITY_API_KEY',raising=False)
    with patch.object(Path,'is_file',return_value=False),patch.object(discovery.urllib.request,'urlopen',side_effect=AssertionError('no network')):
        trace=[];assert discovery.find('perplexity','q',live=False,trace=trace)==[]
        assert trace[0]['outcome']=='skipped'
        trace=[];assert discovery.find('perplexity','q',live=True,trace=trace)==[]
        assert trace[0]['outcome']=='unavailable'
    monkeypatch.setenv('PERPLEXITY_API_KEY','test-secret')
    with patch.object(discovery.urllib.request,'urlopen',side_effect=urllib.error.HTTPError(A,401,'secret body',{},None)):
        trace=[];assert discovery.find('perplexity','q',live=True,trace=trace)==[]
        assert trace[0]['reason']=='Perplexity HTTP 401' and 'secret' not in json.dumps(trace)


def test_investigation_sends_only_explicit_query_and_preserves_prior_sources(tmp_path):
    db,data=imported(tmp_path);requests=[]
    def find(provider,query,**kwargs):
        requests.append(query);return []
    with patch.object(discovery,'find',side_effect=find):
        expanded=research.investigate(data['id'],1,query='public follow-up',providers=['parallel','perplexity'],db=db)
    assert requests==['public follow-up','public follow-up']
    assert expanded['evidence']==data['evidence'] and expanded['report']==data['report']


def test_cli_import_and_mcp_assessment_actual_processes(tmp_path):
    db=tmp_path/'cases.db';report=tmp_path/'report.md';report.write_text(REPORT)
    cache=tmp_path/'cache.json';cache.write_text(json.dumps({A:{'text':QUOTE,'fetched_at':'2026-09-04'}}))
    launcher="from pathlib import Path;import sys,runpy;from clearance import instruments;instruments.DOCS=Path(sys.argv[1]);sys.argv=['clearance']+sys.argv[2:];runpy.run_module('clearance',run_name='__main__')"
    p=subprocess.run([sys.executable,'-c',launcher,str(cache),'case','import',str(report),'--question','Fresh sessions','--db',str(db),'--json'],capture_output=True,text=True,timeout=20)
    assert p.returncode==0,p.stderr
    data=json.loads(p.stdout);cid=data['id'];claim=data['claims'][0]['id'];eid=data['evidence'][0]['id']
    args=[{'action':'assess','case_id':cid,'version':1,'claim_id':claim,'relation':'supports','rationale':'The cited study evaluates these tasks.','evidence_id':eid,'quote':QUOTE},
          {'action':'assess','case_id':cid,'version':1,'statement':'Stale','relation':'unresolved','rationale':'Stale choice'},
          {'action':'brief','case_id':cid},
          {'action':'report','case_id':cid,'limit':10}]
    messages=[{'jsonrpc':'2.0','id':n,'method':'tools/call','params':{'name':'science_case','arguments':{**a,'db':str(db)}}} for n,a in enumerate(args)]
    p=subprocess.run([sys.executable,'-m','clearance.mcp_server'],input=''.join(json.dumps(m)+'\n' for m in messages),capture_output=True,text=True,timeout=20)
    assert p.returncode==0,p.stderr
    out=[json.loads(line)['result'] for line in p.stdout.splitlines()]
    assert [r['isError'] for r in out]==[False,True,False,False]
    assert json.loads(out[2]['content'][0]['text'])['claims'][0]['state']=='SUPPORTED_AS_ASSESSED'
    assert json.loads(out[3]['content'][0]['text'])['next_offset']==10


def test_uncited_report_refresh_never_triggers_discovery(tmp_path):
    db=tmp_path/'cases.db'
    with patch.object(cases.search,'find_sources',side_effect=AssertionError('report refresh is citation-only')):
        data=research.import_report('A private topic','An unreferenced report passage.',db=db)
        refreshed=cases.refresh(data['id'],live=True,db=db)
    assert refreshed['evidence']==[] and refreshed['trace']==[]


def test_report_refresh_retains_read_budget_and_prior_investigation(tmp_path):
    db=tmp_path/'cases.db';report=REPORT+'\n[2] '+B+'\n'
    with patch.object(instruments,'document_snapshot',side_effect=snapshot):
        data=research.import_report('Fresh sessions',report,max_documents=1,db=db)
        with patch.object(discovery,'find',return_value=[cases.search.Candidate(B,'Replication',COUNTER)]):
            expanded=research.investigate(data['id'],1,query='fresh sessions failure',db=db)
        refreshed=cases.refresh(data['id'],db=db)
    assert len(expanded['evidence'])==2 and len(refreshed['evidence'])==2
    assert refreshed['evidence'][1]['discovered_by']==['parallel']


def test_markdown_named_reference_preserves_citation_mapping():
    report='A cited passage.[1]\n\n[1]: [Study title](https://example.org/study)\n'
    parsed=research.parse_report(report)
    assert len(parsed['passages'])==1
    assert parsed['passages'][0]['source_urls']==[A]


def test_read_unread_citation_directly_without_provider_and_recheck_stale(tmp_path):
    db=tmp_path/'cases.db';report=REPORT+'\n[2] '+B+'\n'
    with patch.object(instruments,'document_snapshot',side_effect=snapshot):
        data=research.import_report('Fresh sessions',report,max_documents=1,db=db)
        assert research.brief(data)['unread_report_citations']==[B]
        with patch.object(discovery,'find',side_effect=AssertionError('direct read must not search')):
            read=research.investigate(data['id'],1,sources=[B],live=True,db=db)
    assert research.brief(read)['unread_report_citations']==[]
    assert len(read['evidence'])==2
    with patch.object(instruments,'document_snapshot',return_value=None):
        changed=research.investigate(data['id'],2,sources=[B],live=True,db=db)
    assert len(changed['evidence'])==2
    assert any(c['kind']=='source_unavailable' for c in changed['changes'])


def test_pdf_source_extracts_visible_text_and_rejects_legacy_binary_cache(tmp_path):
    from pypdf import PdfWriter
    from pypdf.generic import DictionaryObject,NameObject,DecodedStreamObject
    writer=PdfWriter();page=writer.add_blank_page(width=600,height=800)
    font=DictionaryObject({NameObject('/Type'):NameObject('/Font'),NameObject('/Subtype'):NameObject('/Type1'),NameObject('/BaseFont'):NameObject('/Helvetica')})
    page[NameObject('/Resources')]=DictionaryObject({NameObject('/Font'):DictionaryObject({NameObject('/F1'):writer._add_object(font)})})
    stream=DecodedStreamObject();stream.set_data(b'BT /F1 12 Tf 40 700 Td (Fresh sessions reduced repeated errors in the study.) Tj ET')
    page[NameObject('/Contents')]=writer._add_object(stream)
    raw=io.BytesIO();writer.write(raw)
    url='https://example.org/paper.pdf'
    with patch.object(instruments,'DOCS',tmp_path/'docs.json'),patch.object(instruments,'fetch_public',return_value=(raw.getvalue(),url)):
        result=instruments.document_snapshot(url)
    assert result['text']=='Fresh sessions reduced repeated errors in the study.'
    assert not result['text'].startswith('%PDF-')
    legacy=tmp_path/'legacy.json';legacy.write_text(json.dumps({url:{'text':'%PDF-1.7 binary garbage'}}))
    with patch.object(instruments,'DOCS',legacy),patch.object(instruments,'fetch_public',side_effect=AssertionError('offline')):
        assert instruments.document_snapshot(url,fetch=False) is None


def test_report_titled_references_balanced_url_and_sonar_extra_sources():
    url='https://example.org/wiki/Foo_(bar)'
    report='A claim.[1]\n\nCitations:\n[1] Example Study — '+url+'\n'
    parsed=research.parse_report(report)
    assert len(parsed['passages'])==1 and parsed['passages'][0]['source_urls']==[url]
    assert parsed['urls']==[url]
    parsed=research.parse_report('\ufeff'+json.dumps({'content':'Another claim.[1]','search_results':[{'url':url}]}))
    assert parsed['urls']==[url]
    assert parsed['passages'][0]['source_urls']==[]
    assert parsed['passages'][0]['unresolved_citations']==['1']


def test_parallel_sdk_exception_is_recorded_and_search_receipts_stay_private(tmp_path,monkeypatch):
    import httpx
    import parallel
    from clearance import search
    monkeypatch.setenv('AGENT_SCIENCE_SEARCH_DIR',str(tmp_path/'private-search'))
    tracked_receipts=tmp_path/'tracked-receipts.jsonl';tracked_receipts.write_text('existing\n')
    with patch.object(search,'RECEIPTS',tracked_receipts),patch.object(search,'sdk_available',return_value=True),patch.object(search,'_live_search_sdk',side_effect=parallel.APIConnectionError(request=httpx.Request('POST','https://api.parallel.ai/v1/search'))):
        db,data=imported(tmp_path)
        result=research.investigate(data['id'],1,query='A private user query',live=True,db=db)
    assert any(e['outcome']=='error' for e in result['trace'])
    assert tracked_receipts.read_text()=='existing\n'
    with patch.object(search,'RECEIPTS',tracked_receipts),patch.object(search,'_live_search',return_value=({'results':[]},'request-test')):
        result=research.investigate(data['id'],2,query='Another private user query',live=True,db=db)
    assert tracked_receipts.read_text()=='existing\n'
    assert 'Another private user query' in (tmp_path/'private-search/parallel-receipts.jsonl').read_text()


def test_perplexity_incomplete_body_keeps_real_mcp_session_alive(tmp_path):
    db,data=imported(tmp_path)
    code="import os,runpy,urllib.request,http.client;os.environ['PERPLEXITY_API_KEY']='test-secret';urllib.request.urlopen=lambda *a,**k: (_ for _ in ()).throw(http.client.IncompleteRead(b'partial'));runpy.run_module('clearance.mcp_server',run_name='__main__')"
    messages=[{'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'science_case','arguments':{'action':'investigate','case_id':data['id'],'version':1,'query':'public query','providers':['perplexity'],'live':True,'db':str(db)}}}, {'jsonrpc':'2.0','id':2,'method':'tools/list'}]
    proc=subprocess.run([sys.executable,'-c',code],input=''.join(json.dumps(m)+'\n' for m in messages),capture_output=True,text=True,timeout=20)
    assert proc.returncode==0,proc.stderr
    out=[json.loads(line) for line in proc.stdout.splitlines()]
    result=json.loads(out[0]['result']['content'][0]['text'])
    assert result['trace'][0]['outcome']=='error'
    assert len(out[1]['result']['tools'])>0
    assert 'test-secret' not in proc.stdout+proc.stderr


def test_sonar_punctuated_citation_and_titled_commonmark_definition():
    for report in (json.dumps({'content':'Claim.[1]','citations':[A+'.']}),'Claim.[1]\n\n[1]: '+A+' "Study title"\n'):
        result=research.parse_report(report)
        assert len(result['passages'])==1 and result['passages'][0]['source_urls']==[A]


def test_practitioner_lookup_does_not_turn_internal_coaching_rows_into_sources():
    from clearance import visibility
    hits=visibility._practices_hits('verification real agent',full=True)
    assert all(h['who']!='Verification real' for h in hits)
    assert any('Thorsten Ball' in h['who'] for h in hits)
