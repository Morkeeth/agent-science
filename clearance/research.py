"""Import, investigate and assess research through versioned local cases.

Report statements and assessments are authored claims. Only exact source spans
are mechanically verified. No report instruction can invoke a tool or execute code.
"""
import copy
import json
import re
import uuid
from urllib.parse import urlsplit
from clearance import cases, discovery

URL = re.compile(r'https?://[^\s<>"\]`]+')


def _urls(text):
    urls=[]
    for value in URL.findall(text):
        value=value.rstrip('.,;')
        while value.endswith(')') and value.count(')')>value.count('('):value=value[:-1]
        if value not in urls:urls.append(value)
    return urls


def parse_report(text):
    if not isinstance(text,str) or not text.strip() or len(text.encode())>500_000:
        raise ValueError('report must be nonempty text of at most 500 KB')
    original=text;refs={};extra_urls=[]
    text=text.lstrip('\ufeff')
    if text.lstrip().startswith('{'):
        try:
            obj=json.loads(text)
            text=obj.get('content') or obj['choices'][0]['message']['content']
            if not isinstance(text,str):raise ValueError()
            for i,item in enumerate(obj.get('citations',[]),1):
                url=item if isinstance(item,str) else item.get('url','')
                parsed=_urls(url)
                if len(parsed)==1:refs[str(i)]=parsed[0]
            for item in obj.get('search_results',[]):
                if isinstance(item,dict) and isinstance(item.get('url'),str):extra_urls.extend(_urls(item['url']))
        except (ValueError,KeyError,IndexError,TypeError,AttributeError):
            raise ValueError('JSON report needs content or choices[0].message.content, with optional citations') from None
    body=[];references=False
    for line in text.splitlines():
        if line.strip().lstrip('#').strip().rstrip(':').lower() in ('sources','citations','references'):
            references=True
            continue
        match=re.match(r'^\s*\[(\d+)\]\s*:?\s*(.*)$',line)
        if not match and references:match=re.match(r'^\s*(\d+)\.\s+(.*)$',line)
        urls=_urls(match[2]) if match else []
        if match and urls:refs[match[1]]=urls[0]
        else:body.append(line)
    statements=[]
    for paragraph in re.split(r'\n\s*\n','\n'.join(body)):
        paragraph=paragraph.strip()
        paragraph='\n'.join(line for line in paragraph.splitlines() if not line.lstrip().startswith('#')).strip()
        if not paragraph or re.match(r'^\[\d+\]\s*:?\s*https?://',paragraph):continue
        # Keep report passages verbatim. Extraction is not semantic claim splitting.
        cited=list(dict.fromkeys(_urls(paragraph)+[refs[n] for n in re.findall(r'\[(\d+)\]',paragraph) if n in refs]))
        statements.append({'id':uuid.uuid4().hex[:12],'statement':paragraph,'source_urls':cited,
                           'unresolved_citations':[n for n in re.findall(r'\[(\d+)\]',paragraph) if n not in refs],
                           'origin':'imported_report','assessments':[]})
    urls=list(dict.fromkeys(list(refs.values())+extra_urls+_urls(text)))
    if len(urls)>100 or len(statements)>200:
        raise ValueError('report exceeds 100 citations or 200 passages; split the report')
    return {'text':original,'sha256':cases.digest(original),'passages':statements,'urls':urls,
            'meaning':'Imported passages are unassessed claims, not verified conclusions.'}


def _draft(case_id,version,db):
    data=cases.get(case_id,db=db)
    if version is None:raise ValueError('this action requires the case version you inspected')
    if type(version) is not int or version!=data['version']:
        raise ValueError('case version changed; inspect the latest version before writing')
    return {k:copy.deepcopy(v) for k,v in data.items() if k not in ('decisions','experiments','coverage','freshness')}


def _save(data,db,changes=None):
    data.update(version=data['version']+1,checked_at=cases.now(),changes=changes or [])
    return cases._save(data,db=db)


def import_report(question,text,*,root=None,live=False,db=None,max_documents=12):
    if not isinstance(question,str) or not 1<=len(question.strip())<=1500:
        raise ValueError('question must contain 1–1500 characters')
    if type(max_documents) is not int or not 1<=max_documents<=40:
        raise ValueError('max_documents must be 1–40')
    context=cases.repo_context(root)
    report=parse_report(text)
    # Explicit citations only: importing a report never sends its text to search.
    evidence,trace=(cases._collect(question,live=live,sources=report['urls'],max_documents=max_documents)
                    if report['urls'] else ([],[]))
    data={'id':uuid.uuid4().hex[:12],'version':1,'question':question.strip(),'created_at':cases.now(),
          'checked_at':cases.now(),'repo':context,'official_domains':[],
          'provided_sources':report['urls'],'evidence':evidence,'trace':trace,'changes':[],
          'claims':report.pop('passages'),'report':report,'document_limit':max_documents,
          'limits':['Report passages are unassessed. Citation text must be read and assessed.',
                    'Only the configured number of cited documents is read; brief lists unread citations.']}
    return cases._save(data,db=db)


def investigate(case_id,version,*,query='',sources=(),providers=('parallel',),live=False,limit=5,db=None):
    if not isinstance(providers,(tuple,list)) or not providers or any(p not in discovery.PROVIDERS for p in providers):
        raise ValueError('choose parallel, perplexity, or both providers')
    if not isinstance(query,str) or len(query)>1500:
        raise ValueError('query must be text of at most 1500 characters')
    if not isinstance(sources,(list,tuple)) or len(sources)>10 or any(not isinstance(u,str) for u in sources):
        raise ValueError('provide up to 10 source URLs')
    if not query.strip() and not sources:raise ValueError('provide a public query or explicit sources')
    if type(limit) is not int or not 1<=limit<=10:raise ValueError('limit must be 1–10')
    data=_draft(case_id,version,db);events=[];found={};origins={}
    for provider in dict.fromkeys(providers) if query.strip() else ():
        try:results=discovery.find(provider,query,live=live,limit=limit,trace=events)
        except (RuntimeError,OSError,ValueError):
            events.append({'route':provider,'outcome':'error','reason':'discovery failed'})
            results=[]
        for candidate in results:
            found[candidate.url]=candidate
            origins.setdefault(candidate.url,[]).append(provider)
    prior={e['url']:e for e in data['evidence']}
    before={'evidence':copy.deepcopy(data['evidence']),'repo':data.get('repo')}
    for url in sources:
        found.setdefault(url,cases.search.Candidate(url,prior.get(url,{}).get('title',url),''))
    new_urls=[u for u in found if u not in prior or u in sources]
    evidence,reads=(cases._collect(data['question'],live=live,refresh=live,sources=new_urls,
        official_domains=data['official_domains'],excerpts={u:found[u].excerpt for u in new_urls},
        titles={u:found[u].title for u in new_urls}) if new_urls else ([],[]))
    for e in evidence:
        e['discovered_by']=list(dict.fromkeys(prior.get(e['url'],{}).get('discovered_by',[])+origins.get(e['url'],[])))
        e['discovery_query']=query or prior.get(e['url'],{}).get('discovery_query','')
    for url in prior.keys() & origins.keys():
        prior[url]['discovered_by']=list(dict.fromkeys(prior[url].get('discovered_by',[])+origins[url]))
    for e in evidence:prior[e['url']]=e
    data['evidence']=list(prior.values())
    data['trace']=events+reads
    data.setdefault('investigations',[]).append({'query':query,'providers':list(dict.fromkeys(providers)) if query.strip() else [],
        'sources':list(sources),'at':cases.now(),'trace':copy.deepcopy(data['trace']),
        'new_sources':sum(e['url'] not in {b['url'] for b in before['evidence']} for e in evidence)})
    return _save(data,db,changes=cases.changes(before,data))


def assess(case_id,version,*,statement,relation,rationale,evidence_id=None,quote=None,claim_id=None,supersedes=None,db=None):
    if relation not in ('supports','contradicts','different_scope','context','unresolved'):
        raise ValueError('relation must be supports, contradicts, different_scope, context or unresolved')
    if not isinstance(rationale,str) or not 1<=len(rationale.strip())<=5000:
        raise ValueError('assessment needs a rationale of at most 5000 characters')
    if claim_id and statement is not None:raise ValueError('provide claim_id or a new statement, not both')
    data=_draft(case_id,version,db)
    claims=data.setdefault('claims',[])
    claim=next((c for c in claims if c['id']==claim_id),None) if claim_id else None
    if claim_id and claim is None:raise ValueError('claim not found in this case')
    if claim is None:
        if not isinstance(statement,str) or not 1<=len(statement.strip())<=5000:
            raise ValueError('new claim needs a statement of at most 5000 characters')
        claim={'id':uuid.uuid4().hex[:12],'statement':statement.strip(),'source_urls':[],
               'origin':'authored','assessments':[]}
        claims.append(claim)
    if supersedes and not any(a['id']==supersedes and not any(b.get('supersedes')==supersedes for b in claim['assessments']) for a in claim['assessments']):
        raise ValueError('supersedes must name an active assessment on this claim')
    anchor={}
    if relation!='unresolved' or evidence_id or quote:
        evidence=next((e for e in data['evidence'] if e['id']==evidence_id),None)
        if not evidence or not isinstance(quote,str) or not 20<=len(quote)<=4000 or quote not in evidence.get('snapshot_text',''):
            raise ValueError('assessment requires an exact 20–4000 character quote from this case source snapshot')
        # Lane B gate: qualitative interview designs cannot support causal effectiveness claims.
        if relation == 'supports':
            from clearance import claim_graph, conditions as conditions_mod
            gate = claim_graph.validate_assessment_relation(
                relation, statement=claim['statement'],
                evidence_text=evidence.get('snapshot_text') or '',
                evidence_conditions=conditions_mod.extract(evidence.get('snapshot_text') or '', url=evidence.get('url')),
            )
            if not gate['ok']:
                raise ValueError(gate['reason'])
        anchor={'evidence_id':evidence_id,'quote':quote,'snapshot_hash':evidence['snapshot_hash'],'url':evidence['url']}
    claim['assessments'].append({'id':uuid.uuid4().hex[:12],'relation':relation,'rationale':rationale.strip(),
        'evidence_version':version,'supersedes':supersedes,'at':cases.now(),'authorship':'user_or_agent','anchor':anchor,
        'meaning':'Authored interpretation. Quote occurrence is checked; entailment is not mechanically established.'})
    return _save(data,db)


def brief(data):
    evidence={e['id']:e for e in data['evidence']};rows=[]
    for claim in data.get('claims',[]):
        assessments=[]
        superseded={a.get('supersedes') for a in claim['assessments']}
        for a in claim['assessments']:
            anchor=a['anchor'];source=evidence.get(anchor.get('evidence_id'),{})
            current=not anchor or (source.get('snapshot_hash')==anchor['snapshot_hash'] and source.get('status')!='UNAVAILABLE')
            assessments.append({**a,'state':'SUPERSEDED' if a['id'] in superseded else 'CURRENT' if current else 'REVIEW_REQUIRED'})
        relations={a['relation'] for a in assessments if a['state']=='CURRENT'}
        state=('CONTESTED' if {'supports','contradicts'}<=relations else
               'REVIEW_REQUIRED' if any(a['state']=='REVIEW_REQUIRED' for a in assessments) else
               'SUPPORTED_AS_ASSESSED' if 'supports' in relations else
               'CONTRADICTED_AS_ASSESSED' if 'contradicts' in relations else
               'SCOPED_AS_ASSESSED' if 'different_scope' in relations else 'UNRESOLVED')
        rows.append({**claim,'assessments':assessments,'state':state})
    read_urls={e['url'] for e in data['evidence'] if e.get('snapshot_text')}
    unread=[u for u in data.get('report',{}).get('urls',[]) if u not in read_urls]
    from clearance import claim_graph, study as study_mod
    studies = study_mod.build_studies(data.get('evidence', []))
    graph = claim_graph.from_case(data)
    return {'case_id':data['id'],'version':data['version'],'question':data['question'],'claims':rows,
        'unread_report_citations':unread,'source_hosts':sorted({urlsplit(e['url']).hostname for e in data['evidence'] if urlsplit(e['url']).hostname}),
        'studies':[{'identity':s['identity'],'id':s['id'],'n_documents':len(s['document_refs']),
                    'conditions':{f:(s.get('conditions') or {}).get(f) for f in ('task','population','metric','study_design','limitations')}}
                   for s in studies],
        'claim_graph':{'edge_relations':sorted({e['relation'] for e in graph['edges']}),
                       'n_edges':len(graph['edges']),'n_nodes':len(graph['nodes'])},
        'limits':['Assessments are authored interpretations, not automatic scientific verdicts.',
                  'Different hosts do not establish independent experiments.',
                  'HTML/PDF mirrors of one DOI/arXiv id are one study; titles never merge studies.',
                  'different_scope means task/population mismatch — not an automatic contradiction.',
                  'This compares saved snapshots; refresh explicitly to check the web.'],
        'next_action':'Inspect unresolved or stale claims and cited sources; add a targeted investigation or design a local experiment.'}


def render_brief(result):
    lines=[f"Research brief · {result['case_id']} · version {result['version']}",result['question'],'']
    if result.get('studies'):
        lines.append(f"Studies: {len(result['studies'])}")
        for s in result['studies']:
            task=((s.get('conditions') or {}).get('task') or {}).get('value') or 'task unknown'
            lines.append(f"  [{s['identity']}:{s['id']}] docs={s['n_documents']} · {task[:100]}")
        lines.append('')
    if result.get('claim_graph'):
        g=result['claim_graph']
        lines.append(f"Claim graph: {g.get('n_edges',0)} edges · relations={g.get('edge_relations')}")
        lines.append('')
    for c in result['claims']:
        lines.extend([f"[{c['state']}] {c['id']}",c['statement']])
        for a in c['assessments']:
            lines.append(f"  {a['relation']} · {a['state']}: {a['rationale']}")
            if a['anchor']:lines.extend(['  '+a['anchor']['url'],'  '+a['anchor']['quote']])
        lines.append('')
    if not result['claims']:lines.append('No claims assessed yet. Read a source and add an assessment.')
    if result['unread_report_citations']:lines.append(f"Unread report citations: {len(result['unread_report_citations'])}")
    return '\n'.join(lines+result['limits']+['',result['next_action']])+'\n'


def report_source(case_id, *, version=None, db=None, offset=0, limit=12000):
    data=cases.get(case_id,version=version,db=db)
    if 'report' not in data:raise ValueError('case has no imported report')
    if type(offset) is not int or offset<0 or type(limit) is not int or not 1<=limit<=20000:
        raise ValueError('offset must be nonnegative and limit must be 1–20000')
    text=data['report']['text']
    return {'case_id':case_id,'version':data['version'],'sha256':data['report']['sha256'],
            'text':text[offset:offset+limit],'offset':offset,'total_characters':len(text),
            'next_offset':offset+limit if offset+limit<len(text) else None,
            'meaning':'Original imported report; not verified evidence.'}
