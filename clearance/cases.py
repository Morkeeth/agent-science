"""Versioned research cases and the decisions that depend on them.

Quotes prove document occurrence, not entailment. Decisions are explicitly authored.
Private repo context stays in the local case store and is never a search query.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from clearance import instruments, search, stack_fit


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def connect(db=None):
    path = Path(db or os.environ.get('AGENT_SCIENCE_CASES_DB', Path.home()/'.agent-science/cases.db'))
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, timeout=10)
    con.row_factory = sqlite3.Row
    con.executescript('''
        CREATE TABLE IF NOT EXISTS cases(id TEXT PRIMARY KEY, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS revisions(case_id TEXT, version INTEGER, body TEXT NOT NULL,
            PRIMARY KEY(case_id,version));
        CREATE TABLE IF NOT EXISTS decisions(id TEXT PRIMARY KEY,case_id TEXT,version INTEGER,
            statement TEXT,rationale TEXT,evidence_ids TEXT,created_at TEXT);
        CREATE TABLE IF NOT EXISTS experiments(id TEXT PRIMARY KEY,case_id TEXT,body TEXT NOT NULL);
    ''')
    return con


def get(case_id, *, db=None, version=None):
    with connect(db) as con:
        row = con.execute('SELECT body FROM revisions WHERE case_id=? AND (? IS NULL OR version=?) ORDER BY version DESC LIMIT 1',
                          (case_id, version, version)).fetchone()
        if row is None:
            raise ValueError('case or version not found')
        out = json.loads(row['body'])
        out['decisions'] = [dict(r) for r in con.execute('SELECT * FROM decisions WHERE case_id=? AND version<=? ORDER BY created_at',(case_id,out['version']))]
        for d in out['decisions']:
            d['evidence_ids'] = json.loads(d['evidence_ids'])
            original = con.execute('SELECT body FROM revisions WHERE case_id=? AND version=?',(case_id,d['version'])).fetchone()
            old = json.loads(original['body']) if original else {}
            d['review'] = decision_review(d, old, out)
        out['coverage'] = coverage(out['evidence'])
        reads=[e for e in out['trace'] if e['route']=='document' and e['outcome']=='read']
        out['freshness']={'new_fetches':sum(not e.get('cache_hit',False) for e in reads),
            'cached_reads':sum(bool(e.get('cache_hit')) for e in reads),
            'meaning':'Only new_fetches checks sources on the web. Cached reads cannot rule out external changes.'}
        out['experiments'] = [e for r in con.execute('SELECT body FROM experiments WHERE case_id=?',(case_id,)) if (e := json.loads(r['body'])).get('case_version',1) <= out['version']]
        return out


def recent(*, db=None, limit=20):
    with connect(db) as con:
        ids = [r['id'] for r in con.execute('SELECT id FROM cases ORDER BY created_at DESC LIMIT ?', (max(1,min(limit,100)),))]
    return [get(i, db=db) for i in ids]


def repo_context(root):
    if root is None:
        return None
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError('repo root must be an existing directory')
    context = stack_fit.detect_stack(root)
    context['files'] = {}
    # Store hashes, not file contents. No private instructions leave the machine.
    for name in ('AGENTS.md','CLAUDE.md','package.json','package-lock.json','requirements.txt','pyproject.toml','uv.lock','Cargo.lock','go.sum'):
        p = root/name
        if p.is_file() and not p.is_symlink() and p.stat().st_size < 2_000_000:
            context['files'][name] = hashlib.sha256(p.read_bytes()).hexdigest()
    try:
        context['commit'] = subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],stderr=subprocess.DEVNULL,text=True,timeout=5).strip()
    except (subprocess.SubprocessError, OSError):
        context['commit'] = None
    context['assessment'] = 'context captured; benefit requires an experiment'
    return context


def _quote(question, candidate, text):
    excerpt = candidate.excerpt.strip()
    if 20 <= len(excerpt) <= 400 and excerpt in text:
        return excerpt
    terms = set(re.findall(r'[a-zA-Z]{4,}', question.lower())) - {'should','would','could','with','that','this','what','does','have','from','which'}
    spans = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if 25 <= len(s.strip()) <= 400]
    ranked = sorted(spans, key=lambda s: len(terms & set(re.findall(r'[a-zA-Z]{4,}',s.lower()))), reverse=True)
    if ranked and terms & set(re.findall(r'[a-zA-Z]{4,}',ranked[0].lower())):
        return ranked[0]
    return None


def _kind(url, official_domains):
    host = (urlparse(url).hostname or '').lower()
    if any(host == d or host.endswith('.'+d) for d in ('arxiv.org','acm.org','ieee.org','openreview.net','nature.com')):
        return 'research_repository'
    if any(host == d or host.endswith('.'+d) for d in official_domains):
        return 'declared_official'
    return 'web_source'


def _collect(question, *, live=False, refresh=False, sources=(), official_domains=(), max_per_angle=2, excerpts=None, titles=None, origin_angles=None, include_discovery=False):
    evidence, trace, seen = [], [], set()
    angles = [
        ('research', 'Find empirical research with methods, sample sizes and limitations relevant to: '+question, question+' empirical study'),
        ('official_docs', 'Find official documentation describing behavior and limitations relevant to: '+question, question+' official documentation'),
        ('practice', 'Find practitioner reports and working implementations, including failures, relevant to: '+question, question+' implementation experience limitations'),
    ]
    candidates = [('revisit' if url in (origin_angles or {}) else 'provided', search.Candidate(url,(titles or {}).get(url) or ((urlparse(url).hostname or '')+urlparse(url).path),(excerpts or {}).get(url) or '')) for url in sources]
    if not sources or include_discovery:
        for angle, objective, query in angles:
            events = []
            try:
                found = search.find_sources(objective,[query[:190]],live=live,refresh=refresh,max_results=max_per_angle,trace=events) or []
                candidates.extend((angle,c) for c in found)
            except (RuntimeError, OSError, ValueError) as exc:
                events.append({'route':'discovery','outcome':'error','reason':type(exc).__name__})
            trace.extend({**event,'angle':angle} for event in events)
    for angle, candidate in candidates:
        if candidate.url in seen:
            trace.append({'route':'document','angle':angle,'url':candidate.url,'outcome':'skipped','reason':'duplicate URL'})
            continue
        seen.add(candidate.url)
        entry = {'id': digest(candidate.url)[:16], 'url':candidate.url,'title':candidate.title,
                 'angle':(origin_angles or {}).get(candidate.url,angle),'kind':_kind(candidate.url,official_domains),'relation':'not_assessed'}
        try:
            # Offline mode reads only a pre-existing document; it never fetches.
            snapshot = instruments.document_snapshot(candidate.url,refresh=refresh,fetch=live)
            if not snapshot:
                raise ValueError('source unavailable in this mode')
            quote = _quote(question,candidate,snapshot['text'])
            entry.update(snapshot_hash=snapshot['sha256'],fetched_at=snapshot.get('fetched_at'),
                         final_url=snapshot.get('final_url',candidate.url),quote=quote,
                         status='QUOTE_VERIFIED' if quote else 'NO_MATCHED_QUOTE')
            # Exact document text is retained so a later decision remains reviewable.
            entry['snapshot_text'] = snapshot['text']
            if quote:
                assert quote in snapshot['text']
            trace.append({'route':'document','angle':angle,'url':candidate.url,'outcome':'read',
                          'cache_hit':snapshot.get('cache_hit',False),'sha256':snapshot['sha256']})
        except (OSError, ValueError, RuntimeError) as exc:
            entry.update(status='UNAVAILABLE',quote=None,reason=str(exc)[:180])
            trace.append({'route':'document','angle':angle,'url':candidate.url,'outcome':'error','reason':type(exc).__name__})
        evidence.append(entry)
    return evidence, trace


def _save(data, *, db=None):
    with connect(db) as con:
        con.execute('INSERT OR IGNORE INTO cases VALUES(?,?)',(data['id'],data['created_at']))
        try:
            con.execute('INSERT INTO revisions VALUES(?,?,?)',(data['id'],data['version'],json.dumps(data)))
        except sqlite3.IntegrityError:
            raise ValueError('case changed during refresh; reload and retry') from None
    return get(data['id'],db=db)


def create(question, *, root=None, live=False, sources=(), official_domains=(), db=None):
    question = question.strip()
    if not question or len(question)>1500:
        raise ValueError('question must contain 1–1500 characters')
    if len(sources)>12:
        raise ValueError('at most 12 provided sources per case')
    official_domains = [d.lower().strip() for d in official_domains]
    if any(not re.fullmatch(r'[a-z0-9.-]+',d) or '.' not in d for d in official_domains):
        raise ValueError('official domains must be hostnames')
    context = repo_context(root)
    evidence, trace = _collect(question,live=live,sources=sources,official_domains=official_domains)
    data = {'id':uuid.uuid4().hex[:12],'version':1,'question':question,'created_at':now(),
            'checked_at':now(),'repo':context,'official_domains':official_domains,'provided_sources':list(sources),
            'evidence':evidence,'trace':trace,'limits':['A verified quote proves occurrence in a source; its relationship to the question still needs assessment.',
                'Search angles are intentions; source kind is assigned separately. Multiple URLs may share an origin.'],
            'changes':[]}
    return _save(data,db=db)


def changes(old, new):
    before={e['id']:e for e in old['evidence']}; after={e['id']:e for e in new['evidence']}
    out=[]
    for eid in sorted(before.keys() | after.keys()):
        a,b=before.get(eid),after.get(eid)
        if not a: kind='source_added'
        elif not b: kind='not_returned' # discovery absence is not a source retraction
        elif b['status']=='UNAVAILABLE':
            if a['status']=='UNAVAILABLE': continue
            kind='source_unavailable'
        elif a.get('snapshot_hash') != b.get('snapshot_hash'): kind='source_changed'
        elif a.get('status')=='QUOTE_VERIFIED' and b.get('status')!='QUOTE_VERIFIED': kind='quote_unavailable'
        else: continue
        out.append({'evidence_id':eid,'url':(b or a)['url'],'kind':kind,
                    'before_quote':a.get('quote') if a else None,'after_quote':b.get('quote') if b else None})
    if old.get('repo') != new.get('repo'):
        out.append({'kind':'repo_changed','reason':'repo revision or tracked context changed'})
    return out


def refresh(case_id, *, live=False, db=None):
    old=get(case_id,db=db)
    # Revisit every cited URL even if the discovery rankings have changed.
    sources=list(dict.fromkeys(old['provided_sources']+[e['url'] for e in old['evidence']]))
    evidence,trace=_collect(old['question'],live=live,refresh=live,sources=sources,official_domains=old['official_domains'],
        excerpts={e['url']:e.get('quote') for e in old['evidence']},titles={e['url']:e.get('title') for e in old['evidence']},origin_angles={e['url']:e.get('angle') for e in old['evidence']},include_discovery=not old['provided_sources'])
    new={k:v for k,v in old.items() if k not in ('decisions','experiments','coverage','freshness')}
    new.update(version=old['version']+1,checked_at=now(),evidence=evidence,trace=trace)
    if old.get('repo'):
        try: new['repo']=repo_context(old['repo']['root'])
        except ValueError: new['repo']={**old['repo'],'assessment':'repo unavailable'}
    new['changes']=changes(old,new)
    return _save(new,db=db)


def decision_review(decision, original, current):
    delta=changes(original,current) if original else []
    relevant=[c for c in delta if c.get('evidence_id') in decision['evidence_ids'] or c['kind']=='repo_changed']
    return {'state':'REVIEW_REQUIRED' if relevant else 'UNCHANGED_IN_SNAPSHOT', 'changes':relevant,
            'meaning':'This compares saved evidence versions. Check freshness.new_fetches to see whether the web was checked. Changes require review, not automatic reversal.'}


def decide(case_id, statement, rationale, evidence_ids, *, db=None):
    data=get(case_id,db=db)
    if not statement.strip() or not rationale.strip() or not evidence_ids:
        raise ValueError('a decision needs a statement, rationale and at least one evidence ID')
    available={e['id'] for e in data['evidence'] if e['status']=='QUOTE_VERIFIED'}
    if not set(evidence_ids)<=available:
        raise ValueError('each evidence ID must name a verified quote in this case version')
    did=uuid.uuid4().hex[:12]
    with connect(db) as con:
        con.execute('INSERT INTO decisions VALUES(?,?,?,?,?,?,?)',
            (did,case_id,data['version'],statement.strip(),rationale.strip(),json.dumps(list(dict.fromkeys(evidence_ids))),now()))
    return get(case_id,db=db)


def record_experiment(case_id, result, *, db=None):
    get(case_id,db=db)
    result={**result,'id':uuid.uuid4().hex[:12],'case_id':case_id,'recorded_at':now()}
    with connect(db) as con:
        con.execute('INSERT INTO experiments VALUES(?,?,?)',(result['id'],case_id,json.dumps(result)))
    return result


def source(case_id, evidence_id, *, db=None, version=None, offset=0, limit=12000):
    data=get(case_id,db=db,version=version)
    e=next((e for e in data['evidence'] if e['id']==evidence_id),None)
    if not e or 'snapshot_text' not in e:
        raise ValueError('source snapshot not found in this case version')
    if offset<0 or not 1<=limit<=20000:
        raise ValueError('offset must be nonnegative; limit must be 1–20000 characters')
    text=e['snapshot_text']
    return {'case_id':case_id,'version':data['version'],'evidence_id':evidence_id,
            'url':e['url'],'sha256':e['snapshot_hash'],'fetched_at':e.get('fetched_at'),
            'offset':offset,'total_characters':len(text),'text':text[offset:offset+limit],
            'next_offset':offset+limit if offset+limit<len(text) else None}


def coverage(evidence):
    kinds=('research_repository','declared_official','web_source')
    counts={kind:sum(e['kind']==kind and e['status']=='QUOTE_VERIFIED' for e in evidence) for kind in kinds}
    return {'verified_quotes':sum(counts.values()),'by_kind':counts,
            'missing_kinds':[kind for kind,count in counts.items() if not count],
            'note':'Source categories do not establish independence or support for the question.'}


def experiment_summary(result):
    return {**{k:v for k,v in result.items() if k!='acceptance_source'},
            'runs':[{k:v for k,v in row.items() if k!='output_tail'} for row in result['runs']]}


def public_view(data):
    """Compact local tool output, not a public export of private case data."""
    return {**data,'evidence':[{k:v for k,v in e.items() if k!='snapshot_text'} for e in data['evidence']],
            'experiments':[experiment_summary(e) for e in data.get('experiments',[])]}


def format_case(data):
    lines=[f"Case {data['id']} · version {data['version']}", data['question'],
           f"Case revision: {data['checked_at']}",f"Web fetches: {data.get('freshness',{}).get('new_fetches',0)} · cached reads: {data.get('freshness',{}).get('cached_reads',0)}",'Cached reads do not check for web changes.','']
    if data.get('repo'):
        lines += [f"Repo: {data['repo']['root']} · {data['repo'].get('commit') or 'no commit'}",'']
    cov=coverage(data['evidence'])
    lines += [f"Verified quotes: {cov['verified_quotes']} · missing source types: {', '.join(cov['missing_kinds']) or 'none'}",'']
    for e in data['evidence']:
        lines += [f"[{e['status']}] {e['id']} · {e['kind']}",e['url']]
        if e.get('quote'): lines += [e['quote']]
        if e.get('reason'):lines += [e['reason']]
        lines += [f"Source read: {e.get('fetched_at') or 'unknown (legacy cache)'}",'']
    if not data['evidence']:lines += ['No evidence retrieved. Enable live research or provide source URLs.','']
    for d in data.get('decisions',[]):
        lines += [f"Decision {d['id']} · {d['review']['state']}",d['statement'],d['rationale']]
        for c in d['review']['changes']:lines += [f"  {c['kind']}: {c.get('url',c.get('reason',''))}"]
    for e in data.get('experiments',[]):
        lines += [f"Experiment {e['id']}: {e['summary']}"]
    lines += ['','Actual attempts:']
    for event in data['trace']:
        lines += [f"  {event.get('angle','')} / {event['route']}: {event['outcome']}" + (f" · {event['reason']}" if event.get('reason') else '')]
    lines += ['','Quote occurrence is verified. Support, contradiction and applicability are not inferred from a quote alone.']
    return '\n'.join(lines)+'\n'
