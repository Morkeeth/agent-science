"""Retrieval expectations and CLI/MCP privacy boundaries."""
import json
import subprocess
import sys
from unittest.mock import patch

import pytest
from clearance import cases, research, research_search, visibility, instruments


def seed(db, question, statement, *, root=None):
    # No search or fetch: these are explicitly unassessed local fixtures.
    data = research.import_report(question, statement, db=db, root=root)
    return data


def test_user_vocabulary_retrieves_question_and_claim_limits(tmp_path):
    db=tmp_path/'cases.db'
    retrieval=seed(db,'Choosing repository search','Embedding retrieval has task-dependent results.')
    memory=seed(db,'Persistent memory','Context files can preserve mistakes.')
    ux=seed(db,'Human intervention','Opaque loops hinder human-ai collaboration.')
    coordination=seed(db,'Coordination','Multi-agent results depend on the task.')
    for query, expected in [('RAG for my repo',retrieval),('Obsidian',retrieval),('agents.md',memory),('UX',ux),('multiple agents',coordination)]:
        found=research_search.find(query,db=db)
        assert found['cases'][0]['case_id']==expected['id']
        assert found['cases'][0]['claims'][0]['state']=='UNRESOLVED'
        assert found['cases'][0]['match']['topics']
    assert research_search.find('banana cultivation',db=db)['cases']==[]
    assert research_search.find('luxury',db=db)['cases']==[]  # UX must be a whole term.


def test_assessment_limits_searchable_superseded_interpretations_not_indexed(tmp_path):
    db=tmp_path/'cases.db'
    data=seed(db,'Testing methods','A narrow finding.')
    data=research.assess(data['id'],1,claim_id=data['claims'][0]['id'],statement=None,relation='unresolved',rationale='Measured only on zebrafish.',db=db)
    assert research_search.find('zebrafish',db=db)['cases'][0]['match']['fields']==['assessment']
    old=data['claims'][0]['assessments'][0]['id']
    research.assess(data['id'],2,claim_id=data['claims'][0]['id'],statement=None,relation='unresolved',rationale='Withdrawn: wrong population.',supersedes=old,db=db)
    assert research_search.find('zebrafish',db=db)['cases']==[]


def test_root_filter_and_pagination(tmp_path):
    db=tmp_path/'cases.db'
    repo=tmp_path/'repo';repo.mkdir()
    scoped=seed(db,'Memory scoped','Persistent memory.',root=repo)
    seed(db,'Memory global','Persistent memory.')
    assert [r['case_id'] for r in research_search.find('memory',db=db,root=repo)['cases']]==[scoped['id']]
    first=research_search.find('memory',db=db,limit=1)
    second=research_search.find('memory',db=db,limit=1,offset=first['next_offset'])
    assert first['has_more'] and not second['has_more']
    assert first['cases'][0]['case_id']!=second['cases'][0]['case_id']


def test_unselected_source_text_is_not_exposed_or_searchable(tmp_path):
    db=tmp_path/'cases.db'
    secret='SNAPSHOT_ONLY_CONTENT_DO_NOT_RETURN'
    quote='The study reports a task-specific improvement from persistent memory.'
    text=quote+' '+secret
    with patch.object(instruments,'document_snapshot',return_value={'text':text,'sha256':cases.digest(text),'fetched_at':cases.now(),'cache_hit':True}):
        data=seed(db,'Memory sources','Memory claim.[1]\n\n[1] https://example.org/paper')
    research.assess(data['id'],1,claim_id=data['claims'][0]['id'],statement=None,relation='supports',rationale='Limited to the evaluated tasks.',evidence_id=data['evidence'][0]['id'],quote=quote,db=db)
    found=research_search.find('memory',db=db)
    assert secret not in json.dumps(found)
    assert quote in json.dumps(found)
    assert research_search.find(secret,db=db)['cases']==[]


def test_disabled_personal_visibility_never_opens_case_store():
    with patch.object(research_search,'find',side_effect=AssertionError('private store read')),patch('clearance.stack_search.lookup',return_value={}):
        result=visibility.panel('memory',personal=False)
    assert 'saved_research' not in result


def test_cli_and_stdio_mcp_same_saved_find(tmp_path):
    db=tmp_path/'cases.db'
    expected=seed(db,'Repository search','Embedding retrieval.')
    proc=subprocess.run([sys.executable,'-m','clearance','case','find','RAG','--db',str(db),'--json'],capture_output=True,text=True,timeout=20)
    assert proc.returncode==0,proc.stderr
    cli=json.loads(proc.stdout)
    messages=[{'jsonrpc':'2.0','id':1,'method':'tools/call','params':{'name':'science_case','arguments':{'action':'find','query':'RAG','db':str(db)}}}]
    proc=subprocess.run([sys.executable,'-m','clearance.mcp_server'],input=''.join(json.dumps(m)+'\n' for m in messages),capture_output=True,text=True,timeout=20)
    response=json.loads(proc.stdout.strip())
    mcp=json.loads(response['result']['content'][0]['text'])
    assert mcp==cli
    assert mcp['cases'][0]['case_id']==expected['id']


@pytest.mark.parametrize('kwargs',[{'query':''},{'query':'x','limit':True},{'query':'x','offset':-1}])
def test_invalid_search_rejected(tmp_path,kwargs):
    with pytest.raises(ValueError):research_search.find(db=tmp_path/'cases.db',**kwargs)


def test_matching_assessment_not_hidden_behind_five_unrelated_claims(tmp_path):
    db=tmp_path/'cases.db'
    data=seed(db,'Study limitations','\n\n'.join(f'Unrelated statement {n}.' for n in range(8)))
    target=data['claims'][-1]
    research.assess(data['id'],1,claim_id=target['id'],statement=None,relation='unresolved',rationale='Measured only on zebrafish.',db=db)
    result=research_search.find('zebrafish',db=db)
    assert result['cases'][0]['claim_count']==8
    assert result['cases'][0]['claims'][0]['id']==target['id']


def test_search_preserves_contradiction_and_marks_changed_source(tmp_path):
    db=tmp_path/'cases.db'
    quote='The evaluated context files reduced task success in these experiments.'
    def snapshot(url, **kwargs):
        return {'text':quote,'sha256':cases.digest(quote),'fetched_at':cases.now(),'cache_hit':True}
    with patch.object(instruments,'document_snapshot',side_effect=snapshot):
        data=seed(db,'Memory study','Context files always improve results.[1]\n\n[1] https://example.org/study')
    research.assess(data['id'],1,claim_id=data['claims'][0]['id'],statement=None,relation='contradicts',rationale='Only the evaluated tasks; not all agents.',evidence_id=data['evidence'][0]['id'],quote=quote,db=db)
    result=research_search.find('agents.md',db=db)
    assert result['cases'][0]['claims'][0]['state']=='CONTRADICTED_AS_ASSESSED'
    assert result['cases'][0]['inspect']['db']==str(db)
    with patch.object(instruments,'document_snapshot',return_value=None):
        cases.refresh(data['id'],db=db)
    result=research_search.find('agents.md',db=db)
    assert result['cases'][0]['claims'][0]['state']=='REVIEW_REQUIRED'
    assert result['cases'][0]['inspect']['version']==3


def test_personal_visibility_keeps_related_case_separate_from_dictionary_verdict(tmp_path,monkeypatch):
    db=tmp_path/'cases.db';monkeypatch.setenv('AGENT_SCIENCE_CASES_DB',str(db))
    data=seed(db,'Repository search','Embedding retrieval.')
    with patch('clearance.stack_search.lookup',return_value={'label':'NOT_CLEARED'}),patch('clearance.personal_truth.lookup_local',return_value=None),patch('clearance.personal_truth.record_ask',return_value=1):
        panel=visibility.panel('RAG',personal=True)
    assert panel['primary']['label']=='NOT_CLEARED'
    assert panel['saved_research']['cases'][0]['case_id']==data['id']
    rendered=visibility.format_panel(panel)
    assert 'UNRESOLVED' in rendered and 'Embedding retrieval' in rendered


def test_unreadable_case_store_does_not_hide_dictionary_result(tmp_path,monkeypatch):
    db=tmp_path/'broken.db';db.write_text('not a sqlite database')
    monkeypatch.setenv('AGENT_SCIENCE_CASES_DB',str(db))
    with patch('clearance.stack_search.lookup',return_value={'label':'NOT_CLEARED'}),patch('clearance.personal_truth.lookup_local',return_value=None),patch('clearance.personal_truth.record_ask',return_value=1):
        panel=visibility.panel('RAG',personal=True)
    assert panel['primary']['label']=='NOT_CLEARED'
    assert 'error' in panel['saved_research']
    assert 'Saved research unavailable' in visibility.format_panel(panel)


def test_missing_root_is_not_reported_as_empty_research(tmp_path):
    with pytest.raises(ValueError,match='existing directory'):
        research_search.find('memory',root=tmp_path/'typo',db=tmp_path/'cases.db')


def test_mcp_page_options_are_unambiguous(tmp_path):
    from clearance import mcp_server
    db=tmp_path/'cases.db';seed(db,'Memory','Persistent memory.')
    def call(**kwargs):
        return json.loads(mcp_server.handle_tool('science_case',{'action':'find','query':'memory','db':str(db),**kwargs}))
    assert call()['limit']==5
    assert call(limit=1)['limit']==1
    assert call(page_size=2)['limit']==2
    assert 'must agree' in call(limit=1,page_size=20)['error']
    assert 'error' in call(limit=1,page_size=True)
    schema=next(t for t in mcp_server.TOOLS if t['name']=='science_case')['inputSchema']['properties']
    assert 'default' not in schema['page_size']
    assert 'find page size' in schema['limit']['description']


def test_personal_visibility_respects_explicit_repo_scope(tmp_path,monkeypatch):
    db=tmp_path/'cases.db';monkeypatch.setenv('AGENT_SCIENCE_CASES_DB',str(db))
    a=tmp_path/'a';a.mkdir();b=tmp_path/'b';b.mkdir()
    target=seed(db,'Memory A','Persistent memory.',root=a)
    seed(db,'Memory B','Persistent memory.',root=b)
    seed(db,'Memory general','Persistent memory.')
    with patch('clearance.stack_search.lookup',return_value={}),patch('clearance.personal_truth.lookup_local',return_value=None),patch('clearance.personal_truth.record_ask',return_value=1):
        panel=visibility.panel('memory',root=a)
    assert [r['case_id'] for r in panel['saved_research']['cases']]==[target['id']]


def test_generic_phrases_do_not_expand_to_agentic_topics():
    for text in ['lexical scoping in Python closures','the task was delegated to a junior dev','acceptance criteria for a pull request']:
        assert research_search.topics(text)==set()


def test_query_without_searchable_terms_needs_clarification(tmp_path):
    with pytest.raises(ValueError,match='specific topic or keyword'):
        research_search.find('how should my agent use it',db=tmp_path/'cases.db')


def test_ux_query_finds_natural_intervention_question(tmp_path):
    db=tmp_path/'cases.db'
    data=seed(db,'What should an agent show a human, and when should it ask for intervention?', 'Opaque agent loops can hinder collaboration.')
    result=research_search.find('UX for agents',db=db)
    assert result['cases'][0]['case_id']==data['id']
