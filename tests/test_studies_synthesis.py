"""Artificial source fixtures: these are control inputs, never research results."""
import copy
from concurrent.futures import ThreadPoolExecutor
import pytest
from clearance import cases, research, studies, synthesis

TEXT = 'Artificial trial: repository coding tasks used Model X with 20 tasks. The comparator was no memory. The metric was accepted changes.'
QUOTE = 'repository coding tasks used Model X with 20 tasks.'

@pytest.fixture
def saved(tmp_path):
    db = tmp_path / 'private-fixture.db'
    evidence = {'id':'e1', 'url':'https://arxiv.org/abs/2501.12345v1', 'title':'Artificial source',
        'snapshot_text':TEXT, 'snapshot_hash':cases.digest(TEXT), 'status':'NO_MATCHED_QUOTE',
        'kind':'research_repository', 'quote':None, 'relation':'not_assessed'}
    data = {'id':'fixture-case', 'version':1, 'question':'Artificial memory question', 'created_at':cases.now(),
        'checked_at':'frozen-source-check', 'repo':None, 'evidence':[evidence], 'trace':[], 'changes':[],
        'official_domains':[], 'provided_sources':[evidence['url']], 'limits':[]}
    return db, cases._save(data, db=db)


def finding(**changes):
    result = {'statement':'Memory in repository coding tasks', 'relation':'supports',
        'rationale':'Authored fixture interpretation; no real effectiveness claim.', 'evidence_id':'e1', 'quote':QUOTE,
        'strongest_challenge':'The result could depend entirely on the selected tasks.',
        'what_would_change':'A matched comparison on new repository tasks reverses the observed result.',
        'category':'empirical_findings', 'conditions':[{'field':'task', 'value':'repository coding tasks', 'evidence_id':'e1', 'quote':QUOTE}]}
    return {**result, **changes}


def test_identity_versions_and_five_mirrors():
    urls = ['https://arxiv.org/abs/2501.12345v1', 'https://arxiv.org/pdf/2501.12345v1.pdf',
            'https://arxiv.org/html/2501.12345v2', 'https://export.arxiv.org/abs/2501.12345',
            'https://mirror.example/paper']
    evidence = [{'id':str(i), 'url':url, **({'arxiv_id':'2501.12345'} if i==4 else {})} for i,url in enumerate(urls)]
    groups = studies.group(evidence)
    assert len(groups)==1 and len(groups[0]['evidence_ids'])==5
    assert groups[0]['versions']==['arxiv:2501.12345v1','arxiv:2501.12345v2']
    assert 'Unknown' in groups[0]['independence']


def test_doi_case_and_uncertain_title_or_citation():
    evidence = [{'id':'1','url':'https://doi.org/10.1234/ABC'}, {'id':'2','url':'https://publisher.example/pdf', 'doi':'10.1234/abc'},
        {'id':'3','url':'https://blog.example/report','title':'same title','snapshot_text':'Cites 10.1234/ABC'},
        {'id':'4','url':'https://other.example/report','title':'same title'}]
    grouped = studies.group(evidence)
    assert len(grouped)==3
    assert next(s for s in grouped if s['id']=='doi:10.1234/abc')['evidence_ids']==['1','2']
    assert next(s for s in grouped if s['evidence_ids']==['3'])['identity_candidates']==['10.1234/ABC']


def test_atomic_apply_brief_and_historical_read(saved):
    db, data = saved
    updated = synthesis.apply(data['id'],1,{'findings':[finding(),finding(relation='different_scope')]},db=db)
    assert updated['version']==2 and updated['checked_at']=='frozen-source-check'
    assert len(updated['claims'])==1 and len(updated['claims'][0]['assessments'])==2
    assert research.brief(updated)['claims'][0]['state']=='SUPPORTED_AS_ASSESSED'
    answer = synthesis.build(updated)
    assert [c['relation'] for c in answer['conclusions']]==['supports','different_scope']
    assert answer['studies'][0]['conditions']['population']==[]
    assert 'claims' not in cases.get(data['id'],version=1,db=db)
    with pytest.raises(ValueError,match='version changed'):
        synthesis.apply(data['id'],1,{'findings':[finding()]},db=db)


@pytest.mark.parametrize('bad', [
    finding(quote='This fabricated passage is absent from source.'),
    finding(statement='Memory improves performance by 90%'),
    finding(strongest_challenge='none'),
    finding(conditions=[{'field':'task','value':'medical diagnosis','evidence_id':'e1','quote':QUOTE}]),
])
def test_invalid_second_finding_rolls_back(saved,bad):
    db,data=saved
    with pytest.raises(ValueError): synthesis.apply(data['id'],1,{'findings':[finding(),bad]},db=db)
    assert cases.get(data['id'],db=db)['version']==1


def test_unavailable_snapshot_is_not_usable(saved):
    db,data=saved
    data['version']=2; data['evidence'][0]['status']='UNAVAILABLE'
    cases._save(data,db=db)
    with pytest.raises(ValueError,match='available source'):
        synthesis.apply(data['id'],2,{'findings':[finding()]},db=db)
    result=synthesis.apply(data['id'],2,{'findings':[finding(relation='unresolved',evidence_id=None,quote=None,conditions=[])]},db=db)
    assert synthesis.build(result)['conclusions'][0]['relation']=='unresolved'


def test_qualitative_causal_claim_guard(saved):
    db,data=saved
    text='Artificial interviews used a qualitative interview study design.'
    data['evidence'][0].update(snapshot_text=text,snapshot_hash=cases.digest(text));data['version']=2
    cases._save(data,db=db)
    bad=finding(statement='Memory improves coding effectiveness',quote=text,
        conditions=[{'field':'study_design','value':'qualitative interview study','evidence_id':'e1','quote':text}])
    with pytest.raises(ValueError,match='qualitative study'):
        synthesis.apply(data['id'],2,{'findings':[bad]},db=db)


def test_version_diff_distinguishes_availability_and_interpretation(saved):
    db,data=saved
    synthesis.apply(data['id'],1,{'findings':[finding()]},db=db)
    report=synthesis.compare(data['id'],1,db=db)
    assert report['evidence_changes']==[]
    assert report['reasoning_changes'][0]['kind']=='interpretation_added'
    current=cases.get(data['id'],db=db);current['version']=3
    current['evidence'][0]['status']='UNAVAILABLE';cases._save(current,db=db)
    assert synthesis.build(cases.get(data['id'],db=db))['conclusions'][0]['state']=='REVIEW_REQUIRED'
    current['version']=4;current['evidence'][0]['status']='NO_MATCHED_QUOTE';cases._save(current,db=db)
    assert synthesis.compare(data['id'],3,db=db)['evidence_changes'][0]['kind']=='source_newly_available'


def test_concurrent_same_version_has_one_writer(saved):
    db,data=saved
    def write():
        try:return synthesis.apply(data['id'],1,{'findings':[finding()]},db=db)['version']
        except ValueError:return 'stale'
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes=list(pool.map(lambda _:write(),range(2)))
    assert sorted(map(str,outcomes))==['2','stale']
    assert cases.get(data['id'],db=db)['version']==2


def test_challenge_can_replace_an_interpretation_without_erasing_history(saved):
    db,data=saved
    original=synthesis.apply(data['id'],1,{'findings':[finding()]},db=db)
    claim=original['claims'][0];old_id=claim['assessments'][0]['id']
    changed=synthesis.apply(data['id'],2,{'findings':[finding(relation='contradicts',
        claim_id=claim['id'],supersedes=old_id,rationale='An authored challenge changes the interpretation of the same evidence.')]},db=db)
    assert synthesis.build(changed)['conclusions'][0]['relation']=='contradicts'
    assert len(synthesis.build(changed)['conclusions'])==1
    assert len(changed['claims'][0]['assessments'])==2
    assert synthesis.build(cases.get(data['id'],version=2,db=db))['conclusions'][0]['relation']=='supports'
    report=synthesis.compare(data['id'],2,db=db)
    assert report['material_change'] and report['affected_claim_ids']==[claim['id']]


def test_cross_source_condition_goes_stale(saved):
    db,data=saved
    second=copy.deepcopy(data['evidence'][0]);second.update(id='e2',url='https://example.org/second')
    data['evidence'].append(second);data['version']=2;cases._save(data,db=db)
    condition={'field':'task','value':'repository coding tasks','evidence_id':'e2','quote':QUOTE}
    revised=synthesis.apply(data['id'],2,{'findings':[finding(conditions=[condition])]},db=db)
    revised['version']=4;revised['evidence'][1]['snapshot_hash']='changed';cases._save(revised,db=db)
    answer=synthesis.build(cases.get(data['id'],db=db))
    assert answer['conclusions'][0]['state']=='REVIEW_REQUIRED'
    assert answer['conclusions'][0]['conditions'][0]['state']=='REVIEW_REQUIRED'
    assert synthesis.compare(data['id'],3,db=db)['material_change']


def test_retraction_metadata_disables_prior_conclusion(saved):
    db,data=saved
    revised=synthesis.apply(data['id'],1,{'findings':[finding()]},db=db)
    revised['version']=3;revised['evidence'][0]['retracted']=True;cases._save(revised,db=db)
    assert synthesis.build(cases.get(data['id'],db=db))['conclusions'][0]['state']=='REVIEW_REQUIRED'
    assert synthesis.compare(data['id'],2,db=db)['evidence_changes'][0]['kind']=='source_metadata_changed'
    with pytest.raises(ValueError):synthesis.apply(data['id'],3,{'findings':[finding()]},db=db)


def test_numerical_substring_does_not_count_as_source_result(saved):
    db,data=saved
    with pytest.raises(ValueError,match='numerical assertion'):
        synthesis.apply(data['id'],1,{'findings':[finding(statement='There were 2 tasks')]},db=db)


def test_contradiction_can_name_a_different_number_and_is_contested(saved):
    db,data=saved
    revised=synthesis.apply(data['id'],1,{'findings':[finding(statement='The study used 20 tasks'),
        finding(statement='The study used 20 tasks',relation='contradicts',quote=TEXT)]},db=db)
    assert {c['claim_state'] for c in synthesis.build(revised)['conclusions']}=={'CONTESTED'}
    assert synthesis.build(revised)['conclusions'][0]['competing_interpretations']
    with pytest.raises(ValueError,match='numerical assertion'):
        synthesis.apply(data['id'],2,{'findings':[finding(statement='The study used 90 tasks',relation='contradicts')]},db=db)


def test_interpretation_change_flags_decision(saved):
    db,data=saved
    # Existing decision API requires QUOTE_VERIFIED source; fixture explicitly sets it.
    data['version']=2;data['evidence'][0].update(status='QUOTE_VERIFIED',quote=QUOTE);cases._save(data,db=db)
    cases.decide(data['id'],'Use a memory trial','Authored fixture rationale',['e1'],expected_version=2,db=db)
    synthesis.apply(data['id'],2,{'findings':[finding()]},db=db)
    report=synthesis.compare(data['id'],2,db=db)
    assert len(report['affected_decision_ids'])==1
    assert report['affected_decisions'][0]['review']['state']=='REVIEW_REQUIRED'


def test_local_measurements_remove_script_and_output(saved):
    _,data=saved
    data['experiments']=[{'id':'test-run','acceptance_source':'private script',
        'runs':[{'output_tail':'private output','exit_code':0}]}]
    measurement=synthesis.build(data)['local_measurements'][0]
    assert 'acceptance_source' not in measurement and 'output_tail' not in measurement['runs'][0]


@pytest.mark.parametrize('relation,reason', [('context','unresolved relationship'), ('different_scope','unresolved scope')])
def test_context_only_conclusion_exposes_unresolved_gap(saved,relation,reason):
    db,data=saved
    updated=synthesis.apply(data['id'],1,{'findings':[finding(relation=relation)]},db=db)
    answer=synthesis.build(updated)
    assert answer['conclusions'][0]['claim_state']=='UNRESOLVED'
    assert answer['conclusions'][0]['relation']==relation
    assert reason in {g['reason'] for g in answer['gaps']}
    if relation=='different_scope':
        assert 'not evidence of no effect' in next(g['meaning'] for g in answer['gaps'] if g['reason']==reason)


def test_source_data_without_interpretation_exposes_gap(saved):
    _,data=saved
    answer=synthesis.build(data)
    assert answer['conclusions']==[]
    assert {'reason':'unassessed evidence','evidence_ids':['e1'],
        'meaning':'Saved sources have no active authored interpretation; their relationship to the question is unresolved.'} in answer['gaps']


@pytest.mark.parametrize('context_relation', ['context','different_scope'])
def test_support_plus_context_preserves_supported_claim_state(saved,context_relation):
    db,data=saved
    updated=synthesis.apply(data['id'],1,{'findings':[finding(),finding(relation=context_relation)]},db=db)
    answer=synthesis.build(updated)
    assert {c['claim_state'] for c in answer['conclusions']}=={'SUPPORTED_AS_ASSESSED'}
    assert {c['relation'] for c in answer['conclusions']}=={'supports',context_relation}
    assert 'unresolved relationship' not in {g['reason'] for g in answer['gaps']}
    assert ('unresolved scope' in {g['reason'] for g in answer['gaps']}) == (context_relation=='different_scope')


def test_numerical_contradiction_requires_existing_current_anchored_target(saved):
    db,data=saved
    text='Artificial result: completion fell by 37% in the trial.'
    other=copy.deepcopy(data['evidence'][0]);other.update(id='e37',url='https://example.org/37',snapshot_text=text,snapshot_hash=cases.digest(text))
    data['evidence'].append(other);data['version']=2;cases._save(data,db=db)
    statement='Completion fell by 37% in the trial.'
    with pytest.raises(ValueError,match='numerical assertion'):
        synthesis.apply(data['id'],2,{'findings':[finding(statement=statement,relation='contradicts')]},db=db)
    prior=synthesis.apply(data['id'],2,{'findings':[finding(statement=statement,quote=text,evidence_id='e37',conditions=[])]},db=db)
    target=prior['claims'][0]['id']
    revised=synthesis.apply(data['id'],3,{'findings':[finding(statement=statement,relation='contradicts',claim_id=target)]},db=db)
    assert synthesis.build(revised)['conclusions'][-1]['claim_state']=='CONTESTED'
    for bad in ('UNAVAILABLE','retracted','superseded_by','snapshot_hash'):
        altered=copy.deepcopy(revised);altered['version']=cases.get(data['id'],db=db)['version']+1
        source=altered['evidence'][1]
        if bad=='UNAVAILABLE':source['status']='UNAVAILABLE'
        elif bad=='snapshot_hash':source[bad]='newhash'
        else:source[bad]=True
        cases._save(altered,db=db)
        with pytest.raises(ValueError,match='numerical assertion'):
            synthesis.apply(data['id'],altered['version'],{'findings':[finding(statement=statement,relation='contradicts',claim_id=target)]},db=db)


def test_unassessed_import_cannot_bootstrap_numeric_target(saved):
    db,data=saved
    data['claims']=[{'id':'imported','statement':'Completion fell by 37%','origin':'imported_report','assessments':[]}]
    data['version']=2;cases._save(data,db=db)
    with pytest.raises(ValueError,match='numerical assertion'):
        synthesis.apply(data['id'],2,{'findings':[finding(statement='Completion fell by 37%',relation='context',claim_id='imported')]},db=db)


def test_decision_review_shares_interpretation_state_and_preserves_history(saved):
    db,data=saved
    data['version']=2;data['evidence'][0].update(status='QUOTE_VERIFIED',quote=QUOTE)
    other=copy.deepcopy(data['evidence'][0]);other.update(id='unrelated',url='https://example.org/unrelated')
    data['evidence'].append(other);cases._save(data,db=db)
    prior=synthesis.apply(data['id'],2,{'findings':[finding()]},db=db)
    cases.decide(data['id'],'Related decision','Fixture rationale',['e1'],expected_version=3,db=db)
    cases.decide(data['id'],'Unrelated decision','Fixture rationale',['unrelated'],expected_version=3,db=db)
    claim=prior['claims'][0]
    updated=synthesis.apply(data['id'],3,{'findings':[finding(claim_id=claim['id'],supersedes=claim['assessments'][0]['id'],
        rationale='An authored change in scope changes the relevance of this result.')]},db=db)
    states={d['statement']:d['review']['state'] for d in updated['decisions']}
    assert states=={'Related decision':'REVIEW_REQUIRED','Unrelated decision':'UNCHANGED_IN_SNAPSHOT'}
    assert all(d['review']['state']=='UNCHANGED_IN_SNAPSHOT' for d in cases.get(data['id'],version=3,db=db)['decisions'])
    assert [d['statement'] for d in synthesis.compare(data['id'],3,db=db)['affected_decisions']]==['Related decision']
    # A replacement with identical semantic content must not invalidate a later decision.
    cases.decide(data['id'],'Fresh decision','Fixture rationale',['e1'],expected_version=4,db=db)
    claim=updated['claims'][0];active=claim['assessments'][-1]
    unchanged=synthesis.apply(data['id'],4,{'findings':[finding(claim_id=claim['id'],supersedes=active['id'],rationale=active['rationale'])]},db=db)
    assert next(d for d in unchanged['decisions'] if d['statement']=='Fresh decision')['review']['state']=='UNCHANGED_IN_SNAPSHOT'


def test_decision_review_tracks_conditions_and_ignores_authored_clock(saved):
    _,data=saved
    anchor={'evidence_id':'e1','quote':QUOTE,'snapshot_hash':data['evidence'][0]['snapshot_hash'],'url':data['evidence'][0]['url']}
    data['claims']=[{'id':'claim','statement':'Fixture statement','assessments':[{'id':'a','relation':'context','rationale':'Fixture',
        'anchor':{},'conditions':[{'field':'task','value':'repository coding tasks','anchor':anchor,'evidence_version':1}],'at':'before'}]}]
    current=copy.deepcopy(data);current['claims'][0]['assessments'][0]['at']='after'
    current['claims'][0]['assessments'][0]['conditions'][0]['evidence_version']=2
    decision={'evidence_ids':['e1']}
    assert cases.decision_review(decision,data,current)['state']=='UNCHANGED_IN_SNAPSHOT'
    current['claims'][0]['assessments'][0]['conditions'][0]['value']='changed authored condition'
    assert cases.decision_review(decision,data,current)['state']=='REVIEW_REQUIRED'
