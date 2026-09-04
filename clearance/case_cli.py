"""CLI entry points for a research case and its measured decisions."""
import json
import subprocess
import sqlite3
from clearance import cases, case_review, research, research_search
from pathlib import Path


def run(args):
    try:
        db=args.db
        if args.action=='find':
            result=research_search.find(args.query,db=db,root=args.root,limit=args.limit,offset=args.offset)
            print(json.dumps(result,indent=2) if args.json else research_search.render(result,db=db).rstrip(),end='\n')
            return 0
        elif args.action=='import':
            path=Path(args.file)
            with path.open('rb') as source:
                raw=source.read(500_001)
            if len(raw)>500_000:raise ValueError('report exceeds 500 KB')
            data=research.import_report(args.question,raw.decode('utf-8'),root=args.root,live=args.live,db=db,max_documents=args.max_documents)
        elif args.action=='investigate':
            data=research.investigate(args.case_id,args.version,query=args.query,sources=args.source,providers=args.provider or ['parallel'],live=args.live,limit=args.limit,db=db)
        elif args.action=='assess':
            data=research.assess(args.case_id,args.version,statement=args.statement,relation=args.relation,rationale=args.reason,evidence_id=args.evidence,quote=args.quote,claim_id=args.claim,supersedes=args.supersedes,db=db)
        elif args.action=='brief':
            result=research.brief(cases.get(args.case_id,version=args.version,db=db))
            print(json.dumps(result,indent=2) if args.json else research.render_brief(result),end='\n')
            return 0
        elif args.action=='report':
            result=research.report_source(args.case_id,version=args.version,db=db,offset=args.offset,limit=args.limit)
            if args.json:print(json.dumps(result,indent=2))
            else:
                print(f"Imported report · {result['case_id']} · version {result['version']}\nSHA-256 {result['sha256']}\n{result['meaning']}\n\n{result['text']}")
                if result['next_offset'] is not None:
                    print(f"\nMore report text: repeat with --version {result['version']} --offset {result['next_offset']}")
            return 0
        elif args.action=='create':
            data=cases.create(args.question,root=args.root,live=args.live,sources=args.source,official_domains=args.official_domain,db=db)
        elif args.action=='show':data=cases.get(args.case_id,version=args.version,db=db)
        elif args.action=='source':
            data=cases.source(args.case_id,args.evidence,db=db,version=args.version,offset=args.offset,limit=args.limit)
            if args.json:
                print(json.dumps(data,indent=2))
            else:
                print(f"Source {data['evidence_id']} · case {data['case_id']} · version {data['version']}\n{data['url']}\nSHA-256 {data['sha256']}\nFetched: {data.get('fetched_at') or 'unknown'}\n")
                print(data['text'])
                if data['next_offset'] is not None:
                    print(f"\nMore source text: repeat with --version {data['version']} --offset {data['next_offset']}")
            return 0
        elif args.action=='refresh':data=cases.refresh(args.case_id,live=args.live,db=db)
        elif args.action=='decide':data=cases.decide(args.case_id,args.statement,args.reason,args.evidence,db=db,supersedes=args.supersedes,expected_version=args.version,experiment_ids=args.experiment)
        elif args.action=='experiment':
            from clearance.experiments import compare
            result=compare(args.case_id,repo=args.repo,baseline=args.baseline,candidate=args.candidate,
                           check=args.check,runs=args.runs,timeout=args.timeout,db=db)
            if args.json:
                print(json.dumps(cases.experiment_summary(result),indent=2))
            else:
                print(f"Experiment {result['id']} · case {args.case_id} · evidence v{result['case_version']}\n{result['summary']}\nBaseline: {result['pins']['baseline']}\nCandidate: {result['pins']['candidate']}\nAcceptance SHA-256: {result['acceptance_sha256']}\nThis measures the selected check on these commits, not general practice superiority.")
            return 0 if result['valid'] else 2
        else:
            result=case_review.index(db=db,root=args.root,query=args.query,review_only=args.action=='review',limit=args.limit,offset=args.offset,include_cases=args.json and args.action=='list')
            full_cases=result.pop('case_data',[])
            if args.json:
                # Preserve list's existing JSON array shape. Review is a paginated report.
                print(json.dumps(result if args.action=='review' else ({**result,'cases':full_cases} if args.page_info else full_cases),indent=2))
            else:
                print(case_review.render(result,review_only=args.action=='review',db=db),end='')
            return 0
        print(json.dumps(cases.public_view(data),indent=2) if args.json else cases.format_case(data),end='\n')
        return 0
    except (ValueError, OSError, sqlite3.Error, subprocess.SubprocessError) as exc:
        print(json.dumps({'error':str(exc)}) if args.json else f'Cannot complete case action: {exc}')
        return 2


def add_parser(sub):
    case=sub.add_parser('case',help='research a question, preserve decisions and compare repo revisions')
    actions=case.add_subparsers(dest='action',required=True)
    for action in ('create','show','refresh','decide','list','experiment','source','review','import','investigate','assess','brief','report','find'):
        p=actions.add_parser(action)
        p.add_argument('--db',help='local case database override')
        p.add_argument('--json',action='store_true')
        p.set_defaults(func=run)
        if action not in ('create','list','review','import','find'):p.add_argument('case_id')
        if action=='find':
            p.add_argument('query',help='search saved questions, claims and assessment limits; no web request')
            p.add_argument('--root',help='only cases attached to this exact repo')
            p.add_argument('--limit',type=int,default=5)
            p.add_argument('--offset',type=int,default=0)
        if action in ('list','review'):
            p.add_argument('--root',help='only cases attached to this local repo')
            p.add_argument('--query',default='',help='find saved questions; no web request')
            p.add_argument('--limit',type=int,default=20)
            p.add_argument('--offset',type=int,default=0)
            p.add_argument('--page-info',action='store_true',help='include pagination metadata in JSON list')
        if action=='create':
            p.add_argument('question')
            p.add_argument('--root',help='your repository; only local context hashes are stored')
            p.add_argument('--source',action='append',default=[],help='explicit source URL (repeatable)')
            p.add_argument('--official-domain',action='append',default=[],help='declare the relevant official source domains')
        if action=='import':
            p.add_argument('file',help='Perplexity Markdown/text or Sonar JSON report')
            p.add_argument('--question',required=True)
            p.add_argument('--root')
            p.add_argument('--max-documents',type=int,default=12)
        if action=='investigate':
            p.add_argument('--version',type=int,required=True)
            p.add_argument('--query',default='',help='explicit public search query; report and repo contents are not sent')
            p.add_argument('--source',action='append',default=[],help='read a cited URL directly, without a search (up to 10)')
            p.add_argument('--provider',action='append',choices=['parallel','perplexity'])
            p.add_argument('--limit',type=int,default=5,help='results per provider, 1–10')
        if action=='assess':
            p.add_argument('--version',type=int,required=True)
            p.add_argument('--supersedes',help='active assessment ID on this claim to replace')
            p.add_argument('--claim',help='existing imported/authored claim ID')
            p.add_argument('--statement',help='new claim text when no --claim is supplied')
            p.add_argument('--relation',required=True,choices=['supports','contradicts','context','unresolved'])
            p.add_argument('--reason',required=True)
            p.add_argument('--evidence')
            p.add_argument('--quote',help='exact source passage, 20–4000 characters')
        if action in ('create','refresh','import','investigate'):p.add_argument('--live',action='store_true',help='fetch public sources; create also runs up to three search calls')
        if action in ('show','source','brief','report'):p.add_argument('--version',type=int)
        if action=='source':p.add_argument('--evidence',required=True)
        if action in ('source','report'):
            p.add_argument('--offset',type=int,default=0)
            p.add_argument('--limit',type=int,default=12000)
        if action=='decide':
            p.add_argument('--version',type=int,required=True,help='evidence version you inspected')
            p.add_argument('--supersedes',help='active decision ID this replaces; preserves its history')
            p.add_argument('--statement',required=True)
            p.add_argument('--reason',required=True)
            p.add_argument('--evidence',action='append',default=[],help='verified quote ID (repeatable)')
            p.add_argument('--experiment',action='append',default=[],help='valid measured experiment ID (repeatable)')
        if action=='experiment':
            p.add_argument('--repo',default='.')
            p.add_argument('--baseline',required=True,help='Git ref resolved once before execution')
            p.add_argument('--candidate',required=True,help='different Git ref resolved once before execution')
            p.add_argument('--check',required=True,help='trusted Python acceptance script; captured once and executed in both arms')
            p.add_argument('--runs',type=int,default=3)
            p.add_argument('--timeout',type=int,default=60)
