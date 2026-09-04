"""CLI entry points for a research case and its measured decisions."""
import json
import subprocess
from clearance import cases


def run(args):
    try:
        db=args.db
        if args.action=='create':
            data=cases.create(args.question,root=args.root,live=args.live,sources=args.source,official_domains=args.official_domain,db=db)
        elif args.action=='show':data=cases.get(args.case_id,version=args.version,db=db)
        elif args.action=='source':
            data=cases.source(args.case_id,args.evidence,db=db,version=args.version,offset=args.offset,limit=args.limit)
            print(json.dumps(data,indent=2) if args.json else data['text'])
            return 0
        elif args.action=='refresh':data=cases.refresh(args.case_id,live=args.live,db=db)
        elif args.action=='decide':data=cases.decide(args.case_id,args.statement,args.reason,args.evidence,db=db)
        elif args.action=='experiment':
            from clearance.experiments import compare
            result=compare(args.case_id,repo=args.repo,baseline=args.baseline,candidate=args.candidate,
                           check=args.check,runs=args.runs,timeout=args.timeout,db=db)
            print(json.dumps(cases.experiment_summary(result),indent=2) if args.json else result['summary'])
            return 0
        else:
            rows=cases.recent(db=db)
            print(json.dumps([cases.public_view(r) for r in rows],indent=2) if args.json else '\n'.join(f"{r['id']} · v{r['version']} · {r['question']}" for r in rows))
            return 0
        print(json.dumps(cases.public_view(data),indent=2) if args.json else cases.format_case(data),end='\n')
        return 0
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(f'Cannot complete case action: {exc}')
        return 2


def add_parser(sub):
    case=sub.add_parser('case',help='research a question, preserve decisions and compare repo revisions')
    actions=case.add_subparsers(dest='action',required=True)
    for action in ('create','show','refresh','decide','list','experiment','source'):
        p=actions.add_parser(action)
        p.add_argument('--db',help='local case database override')
        p.add_argument('--json',action='store_true')
        p.set_defaults(func=run)
        if action not in ('create','list'):p.add_argument('case_id')
        if action=='create':
            p.add_argument('question')
            p.add_argument('--root',help='your repository; only local context hashes are stored')
            p.add_argument('--source',action='append',default=[],help='explicit source URL (repeatable)')
            p.add_argument('--official-domain',action='append',default=[],help='declare the relevant official source domains')
        if action in ('create','refresh'):p.add_argument('--live',action='store_true',help='fetch public sources; create also runs up to three search calls')
        if action in ('show','source'):p.add_argument('--version',type=int)
        if action=='source':
            p.add_argument('--evidence',required=True)
            p.add_argument('--offset',type=int,default=0)
            p.add_argument('--limit',type=int,default=12000)
        if action=='decide':
            p.add_argument('--statement',required=True)
            p.add_argument('--reason',required=True)
            p.add_argument('--evidence',action='append',required=True,help='verified quote ID (repeatable)')
        if action=='experiment':
            p.add_argument('--repo',default='.')
            p.add_argument('--baseline',required=True,help='Git ref resolved once before execution')
            p.add_argument('--candidate',required=True,help='different Git ref resolved once before execution')
            p.add_argument('--check',required=True,help='trusted Python acceptance script; captured once and executed in both arms')
            p.add_argument('--runs',type=int,default=3)
            p.add_argument('--timeout',type=int,default=60)
