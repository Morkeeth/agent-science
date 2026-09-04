"""Local case discovery and decision review. Never performs network research."""
from contextlib import closing
from pathlib import Path
import shlex

from clearance import cases, research


def index(*, db=None, root=None, query='', review_only=False, limit=20, offset=0, include_cases=False):
    if type(limit) is not int or not 1 <= limit <= 100 or type(offset) is not int or offset < 0:
        raise ValueError('limit must be 1–100; offset must be nonnegative')
    if not isinstance(query,str) or len(query)>1500:
        raise ValueError('query must be text of at most 1500 characters')
    root = str(Path(root).resolve()) if root is not None else None
    with closing(cases.connect(db)) as con:
        con.create_function("casefold",1,lambda value:(value or "").casefold())
        # Select all candidates before review filtering: old unresolved cases must
        # not disappear behind the first page of newer, uneventful cases.
        ids = [r[0] for r in con.execute('''
          SELECT c.id FROM cases c JOIN revisions r ON r.case_id=c.id
          WHERE r.version=(SELECT MAX(version) FROM revisions WHERE case_id=c.id)
          AND (? IS NULL OR json_extract(r.body,'$.repo.root')=?)
          AND instr(casefold(json_extract(r.body,'$.question')),?)>0
          AND (?=0 OR EXISTS (
            SELECT 1 FROM decisions d WHERE d.case_id=c.id AND d.version<r.version
            AND NOT EXISTS (SELECT 1 FROM decisions successor WHERE successor.supersedes=d.id))
            OR json_array_length(json_extract(r.body,'$.claims'))>0)
          ORDER BY c.created_at DESC,c.id DESC''',(root,root,query.casefold(),int(review_only)))]
    rows=[];full_cases=[];matched=0
    for cid in ids:
        data=cases.get(cid,db=db)
        affected=[d for d in data['decisions'] if d['review']['state']=='REVIEW_REQUIRED']
        stale_claims=[c for c in research.brief(data)['claims'] if any(a['state']=='REVIEW_REQUIRED' for a in c['assessments'])]
        if review_only and not affected and not stale_claims:
            continue
        if matched >= offset:
            if include_cases:
                full_cases.append(cases.public_view(data))
            rows.append({'id':cid,'question':data['question'],'version':data['version'],
                'checked_at':data['checked_at'],'root':(data.get('repo') or {}).get('root'),
                'review_required':len(affected),'claim_review_required':len(stale_claims),
                'claims':[{'id':c['id'],'statement':c['statement'],'reason':'Cited snapshot changed or is unavailable in this saved version; inspect freshness and source history.'} for c in stale_claims],
                'decisions':[{'id':d['id'],'version':d['version'],'statement':d['statement'],
                              'review':d['review']} for d in affected],
                'evidence_count':len(data['evidence']), 'experiment_count':len(data['experiments']),
                'freshness':data['freshness']})
        matched+=1
        if len(rows)>limit:
            break
    return {**({'case_data':full_cases[:limit]} if include_cases else {}),'cases':rows[:limit],'offset':offset,'limit':limit,'has_more':len(rows)>limit,
            'next_offset':offset+limit if len(rows)>limit else None,
            'basis':'Saved evidence versions only. This command does not check the web or your current repo.'}


def render(result, *, review_only=False, db=None):
    db_flag = " --db "+shlex.quote(str(db)) if db is not None else ""
    rows=result['cases']
    if not rows:
        return ('No decisions or claim assessments require review in the matching saved cases.' if review_only else 'No matching saved cases.')+'\n'+result['basis']+'\n'
    lines=[('DECISIONS AND CLAIMS TO REVIEW' if review_only else 'SAVED CASES'),result['basis'],'']
    for row in rows:
        lines.append(f"{row['id']} · v{row['version']} · {row['question']}")
        lines.append(f"  {row['review_required']} decisions and {row.get('claim_review_required',0)} claims need review · {row['evidence_count']} sources · {row['experiment_count']} experiments")
        for decision in row['decisions']:
            lines.append(f"  {decision['id']} · from v{decision['version']} · {decision['statement']}")
            for change in decision['review']['changes']:
                lines.append(f"    {change['kind']}: {change.get('url',change.get('reason',''))}")
        for claim in row.get('claims',[]):
            lines.append(f"  Claim {claim['id']} needs review: {claim['statement']}")
            lines.append('    '+claim['reason'])
        lines.append(f"  Inspect: python3 -m clearance case show {row['id']}{db_flag}")
        lines.append('')
    if result['has_more']:
        lines.append(f"More matching cases: repeat with --offset {result['next_offset']}")
    return '\n'.join(lines).rstrip()+'\n'
