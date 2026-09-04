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
