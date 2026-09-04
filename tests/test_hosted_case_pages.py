"""Hosted page contracts, hostile text, version binding and native form behavior."""
from __future__ import annotations

import copy
import sys
import uuid
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cloud import case_pages as P


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.links, self.forms, self.tags, self.ids = [], [], [], []
        self.current = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        self.tags.append((tag,d))
        if 'id' in d:
            self.ids.append(d['id'])
        if tag == 'a':
            self.links.append(d)
        if tag == 'form':
            self.current = {'attributes':d,'fields':[]}
            self.forms.append(self.current)
        if tag in ('input','textarea','select') and self.current is not None:
            self.current['fields'].append(d)

    def handle_endtag(self, tag):
        if tag == 'form':
            self.current = None


def case_fixture():
    return {'id':'abc123','version':2,'latest_version':2,'question':'Should fresh sessions reduce task errors?',
            'checked_at':'2026-09-04T11:10:00+00:00','evidence':[
                {'id':'source1','title':'An empirical comparison','url':'https://example.org/research','kind':'research_repository',
                 'angle':'research','status':'QUOTE_VERIFIED','quote':'Fresh sessions reduced errors in the measured tasks.',
                 'fetched_at':'2026-09-04T11:09:00+00:00','snapshot_hash':'a'*64},
                {'id':'source2','title':'A practitioner report','url':'https://example.org/report','kind':'web_source',
                 'angle':'practice','status':'UNAVAILABLE','reason':'Source unavailable in this mode','quote':None}],
            'coverage':{'verified_quotes':1,'missing_kinds':['declared_official','web_source']},
            'freshness':{'new_fetches':1,'cached_reads':0},
            'changes':[{'kind':'source_changed','evidence_id':'source1','url':'https://example.org/research',
                        'before_quote':'The sample included ten tasks.','after_quote':'The sample included twelve tasks.'}],
            'trace':[{'route':'discovery','angle':'research','query':'fresh sessions empirical study','outcome':'searched'},
                     {'route':'document','angle':'research','url':'https://example.org/research','outcome':'read','cache_hit':False}],
            'decisions':[{'id':'d1','statement':'Test fresh sessions on our next batch.','rationale':'Evidence is promising but our task mix differs.',
                          'version':1,'evidence_ids':['source1'],'created_at':'2026-09-03T12:00:00+00:00',
                          'review':{'state':'REVIEW_REQUIRED','changes':[{'kind':'source_changed','before_quote':'Ten tasks.','after_quote':'Twelve tasks.'}]}}]}


def test_every_page_is_self_contained_with_no_external_assets_or_scripts():
    case=case_fixture()
    for text in (P.login(), P.dashboard([case], 'csrf', {'used':1,'limit':10,'remaining':9}),
                 P.detail(case,'csrf'), P.source_page('abc123',{'version':2,'evidence_id':'source1','text':'a source','total_characters':8}),
                 P.error_page('Try again')):
        page=Page(text)
        assert '<!doctype html>' in text and 'name="viewport"' in text
        assert not [tag for tag,attrs in page.tags if tag in ('script','iframe','img','link')]
        assert len(page.ids)==len(set(page.ids))
        assert 'Skip to content' in text


def test_new_case_form_contract_csrf_and_allowance_are_explicit():
    text=P.dashboard([], 'a<&"', {'used':3,'limit':12,'remaining':9})
    page=Page(text)
    form=next(f for f in page.forms if f['attributes']['action']=='/cases')
    assert form['attributes']['method']=='post'
    fields={f['name']:f for f in form['fields']}
    assert set(fields)=={'csrf','request_id','question','sources','official_domains','live'}
    assert fields['csrf']['value']=='a<&"'
    uuid.UUID(fields['request_id']['value'])
    assert fields['question']['required'] is None
    assert 'checked' in fields['live']
    assert 'Without live research, a new case stays empty' in text
    assert 'Uses one research run' in text
    assert 'Live research sends your question to the search provider' in text
    assert 'research runs' in text and 'not dollar costs' in text
    assert 'Repository uploads' in P.login()


def test_independent_mutations_get_unique_request_ids_and_pinned_version():
    text=P.detail(case_fixture(),'csrf-secret')
    page=Page(text)
    forms=[f for f in page.forms if f['attributes']['action']!='/logout']
    assert {f['attributes']['action'] for f in forms}=={'/cases/abc123/refresh','/cases/abc123/decisions'}
    ids=[]
    for f in forms:
        fields={i['name']:i for i in f['fields']}
        assert fields['csrf']['value']=='csrf-secret'
        ids.append(fields['request_id']['value'])
        uuid.UUID(ids[-1])
    assert len(ids)==len(set(ids))
    decision=next(f for f in forms if f['attributes']['action'].endswith('/decisions'))
    assert next(x for x in decision['fields'] if x['name']=='version')['value']=='2'
    assert [x['value'] for x in decision['fields'] if x['name']=='evidence_ids']==['source1']


def test_old_snapshot_cannot_submit_a_decision_and_all_source_links_are_pinned():
    case=case_fixture(); case['latest_version']=3
    page=Page(P.detail(case,'csrf'))
    assert not [f for f in page.forms if f['attributes']['action'].endswith('/decisions')]
    links=[a['href'] for a in page.links if '/sources/' in a.get('href','')]
    assert '/cases/abc123/sources/source1?version=2&offset=0' in links
    assert '/cases/abc123/sources/source1?version=1&offset=0' in links
    assert all('version=' in link for link in links)


def test_review_required_cases_are_first_and_differences_have_context():
    urgent=case_fixture(); urgent['question']='Review this first'
    quiet=copy.deepcopy(urgent); quiet['id']='other'; quiet['question']='A quieter case'; quiet['decisions']=[]
    dashboard=P.dashboard([quiet,urgent],'csrf',{})
    assert dashboard.index('Review this first')<dashboard.index('A quieter case')
    detail=P.detail(urgent,'csrf')
    for phrase in ('REVIEW REQUIRED','BEFORE','AFTER','Ten tasks.','Twelve tasks.',
                   'Coverage remains incomplete','relationship not assessed','Cached reads cannot rule out'):
        assert phrase in detail,phrase
    assert 'empirical study' in detail and 'cache hit: False' in detail
    assert '>fits<' not in detail


def test_hostile_text_is_escaped_and_unsafe_links_have_no_href():
    evil='<img src=x onerror="alert(1)"><script>alert(2)</script>'
    case=case_fixture(); case['question']=evil; case['evidence'][0]['title']=evil
    case['evidence'][0]['quote']=evil; case['evidence'][0]['url']='javascript:alert(1)'
    case['decisions'][0]['statement']=evil; case['decisions'][0]['rationale']=evil
    case['trace'][0]['query']=evil; case['changes'][0]['before_quote']=evil
    for text in (P.detail(case,evil,error=evil),P.login(error=evil),P.error_page(evil),
                 P.source_page('abc123',{'evidence_id':'source1','version':1,'text':evil,'total_characters':len(evil),'url':'file:///etc/passwd'})):
        assert evil not in text
        page=Page(text)
        assert not [tag for tag,attrs in page.tags if tag in ('img','script')]
        assert not [a for a in page.links if a.get('href','').startswith(('javascript:','file:','data:'))]
    for bad in ('https://user:pass@example.org','https://user@example.org','//example.org','https://example.org\\@evil.org','https://example.org\n?q=1','http://[broken'):
        assert P.safe_url(bad) is None,bad
    good=Page(P.external('https://example.org/?a=1&b=2')).links[0]
    assert good['target']=='_blank' and set(good['rel'].split())=={'noreferrer','noopener'}


def test_source_pagination_preserves_version_and_full_text_without_truncation():
    text='Line one\n'+'evidence '*2000
    source={'evidence_id':'source1','version':3,'text':text,'offset':12000,'total_characters':40000,
            'next_offset':30009,'sha256':'a'*64,'url':'https://example.org/research'}
    rendered=P.source_page('abc123',source,'csrf')
    assert text in rendered
    hrefs=[x['href'] for x in Page(rendered).links]
    assert '/cases/abc123/sources/source1?version=3&offset=30009' in hrefs
    assert '/cases/abc123/sources/source1?version=3&offset=0' in hrefs
    assert '/cases/abc123?version=3#evidence-source1' in hrefs
    assert 'End of saved source' not in rendered
    source['next_offset']=None
    assert 'End of saved source' in P.source_page('abc123',source)


def test_empty_case_discloses_missing_evidence_and_has_no_decision_form():
    case=case_fixture(); case.update(evidence=[],decisions=[],trace=[],changes=[])
    text=P.detail(case,'csrf')
    assert 'No sources available' in text
    assert 'No route events were recorded' in text
    assert 'Decision recording needs a source quote' in text
    assert not [f for f in Page(text).forms if f['attributes']['action'].endswith('/decisions')]


def test_superseded_decisions_keep_history_and_link_to_the_active_successor():
    case=case_fixture()
    original=case['decisions'][0]
    original['superseded_by']='d2'
    original['review']['state']='SUPERSEDED'
    successor=copy.deepcopy(original)
    successor.update(id='d2',version=2,statement='Use bounded fresh sessions.',supersedes='d1',superseded_by=None,
                     review={'state':'UNCHANGED_IN_SNAPSHOT','changes':[]})
    case['decisions'].append(successor)
    text=P.detail(case,'csrf')
    page=Page(text)
    assert 'SUPERSEDED' in text and 'Evidence changes at the time of review' in text
    assert 'Ten tasks.' in text and 'Twelve tasks.' in text
    assert 'decision-d1' in page.ids and 'decision-d2' in page.ids
    assert '#decision-d2' in [a['href'] for a in page.links]
    assert '#decision-d1' in [a['href'] for a in page.links]
    assert P.review_count(case)==0
    assert 'REVIEW REQUIRED' not in P.dashboard([case],'csrf',{})
    options=[attrs for tag,attrs in page.tags if tag=='option']
    assert [o['value'] for o in options]==['','d2'], options


def test_revision_select_has_escaped_bounded_labels_and_server_statement_limit():
    case=case_fixture()
    case['decisions'][0]['statement']='<script>alert(1)</script>'+'A'*150
    text=P.detail(case,'csrf')
    page=Page(text)
    form=next(f for f in page.forms if f['attributes']['action'].endswith('/decisions'))
    fields={f['name']:f for f in form['fields']}
    assert fields['statement']['maxlength']=='2000'
    assert fields['supersedes']['id']=='supersedes'
    assert '<option value="">New independent decision</option>' in text
    assert 'Replace: &lt;script&gt;alert(1)&lt;/script&gt;' in text
    assert case['decisions'][0]['statement'] not in text
    assert not [tag for tag,attrs in page.tags if tag=='script']
    assert not any('selected' in attrs for tag,attrs in page.tags if tag=='option')
    # A prior snapshot still shows the original review state supplied by the store.
    case['version']=1;case['latest_version']=2
    historical=P.detail(case,'csrf')
    assert 'REVIEW REQUIRED' in historical and 'SUPERSEDED' not in historical
    assert not [tag for tag,attrs in Page(historical).tags if tag=='select']


def test_pages_use_the_hosted_service_cool_palette():
    for token in ('--paper:#e9ecef','--card:#f7f8fa','--ink:#14161c','--rule:#c5cad3'):
        assert token in P.CSS
    for retired in ('#e8e6e1','#f5f4f0','#16181d','#c9c5bd'):
        assert retired not in P.CSS


if __name__=='__main__':
    tests=[fn for name,fn in list(globals().items()) if name.startswith('test_')]
    for test in tests:
        test(); print('PASS',test.__name__)
    print(f'{len(tests)}/{len(tests)} passed')
