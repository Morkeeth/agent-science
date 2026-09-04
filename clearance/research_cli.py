"""CLI for adaptive research runs: research / challenge / resume / compare / synthesize."""
import argparse
import json
import sqlite3
from clearance import cases, research_run, synthesis

KNOWN = frozenset({'start', 'challenge', 'resume', 'show', 'list', 'cancel', 'compare', 'synthesize'})


def preprocess_argv(argv):
    """Map `research \"question\"` to `research start \"question\"` without eating subcommands."""
    if argv is None:
        return None
    argv = list(argv)
    if len(argv) >= 2 and argv[0] == 'research' and argv[1] not in KNOWN and not argv[1].startswith('-'):
        return [argv[0], 'start', *argv[1:]]
    return argv


def run(args):
    try:
        db = args.db
        live = getattr(args, 'live', False)
        max_steps = getattr(args, 'max_steps', None)
        limits = {}
        if getattr(args, 'max_discovery', None) is not None:
            limits['max_discovery_calls'] = args.max_discovery
        if getattr(args, 'max_reads', None) is not None:
            limits['max_document_reads'] = args.max_reads
        if getattr(args, 'max_rounds', None) is not None:
            limits['max_rounds'] = args.max_rounds
        limits = limits or None
        plan_only = getattr(args, 'plan_only', False)
        providers = tuple(getattr(args, 'provider', None) or ['parallel'])

        if args.action == 'start':
            result = research_run.start_research(
                args.question, root=getattr(args, 'root', None),
                sources=getattr(args, 'source', None) or (),
                live=live, db=db, limits=limits, providers=providers,
                official_domains=getattr(args, 'official_domain', None) or (),
                execute=not plan_only, max_steps=max_steps,
            )
        elif args.action == 'challenge':
            result = research_run.start_challenge(
                args.case_id, version=getattr(args, 'version', None),
                live=live, db=db, limits=limits, providers=providers,
                execute=not plan_only, max_steps=max_steps,
            )
        elif args.action == 'resume':
            result = research_run.resume(args.run_id, live=live, db=db, max_steps=max_steps)
        elif args.action == 'show':
            result = research_run.get_run(args.run_id, db=db)
        elif args.action == 'list':
            rows = research_run.list_runs(
                case_id=getattr(args, 'case_id', None), db=db,
                limit=getattr(args, 'limit', 20),
            )
            if args.json:
                print(json.dumps(rows, indent=2))
            else:
                for r in rows:
                    print(f"{r['id']} · {r['kind']} · {r['status']} · case {r['case_id']} · {r['question'][:70]}")
            return 0
        elif args.action == 'cancel':
            result = research_run.cancel(args.run_id, db=db)
        elif args.action == 'synthesize':
            data = cases.get(args.case_id, version=getattr(args, 'version', None), db=db)
            run = None
            if getattr(args, 'run_id', None):
                run = research_run.get_run(args.run_id, db=db)
            result = synthesis.synthesize(data, run=run)
            print(json.dumps(result, indent=2) if args.json else synthesis.render_synthesis(result), end='\n')
            return 0
        elif args.action == 'compare':
            latest = cases.get(args.case_id, db=db)
            from_version = args.from_version
            if from_version is None:
                raise ValueError('--from-version is required for compare')
            older = cases.get(args.case_id, version=from_version, db=db)
            to_version = getattr(args, 'to_version', None)
            newer = cases.get(args.case_id, version=to_version, db=db) if to_version else latest
            result = synthesis.diff_answers(older, newer)
            print(json.dumps(result, indent=2) if args.json else synthesis.render_diff(result), end='\n')
            return 0
        else:
            raise ValueError(f'unknown research action: {args.action}')

        print(json.dumps(research_run.public_run(result), indent=2) if args.json
              else research_run.render_run(result), end='\n')
        return 0
    except (ValueError, OSError, sqlite3.Error) as exc:
        print(json.dumps({'error': str(exc)}) if getattr(args, 'json', False)
              else f'Cannot complete research action: {exc}')
        return 2


def add_parser(sub):
    research = sub.add_parser(
        'research',
        help='adaptive investigation: research a question, challenge a pinned answer, resume a run',
    )
    actions = research.add_subparsers(dest='action', required=True)

    def _common(p):
        p.add_argument('--db')
        p.add_argument('--json', action='store_true')
        p.set_defaults(func=run)

    p = actions.add_parser('start', help='start an investigation')
    _common(p)
    p.add_argument('question')
    p.add_argument('--live', action='store_true')
    p.add_argument('--plan-only', action='store_true')
    p.add_argument('--max-steps', type=int)
    p.add_argument('--max-discovery', type=int)
    p.add_argument('--max-reads', type=int)
    p.add_argument('--max-rounds', type=int)
    p.add_argument('--root')
    p.add_argument('--source', action='append', default=[])
    p.add_argument('--official-domain', action='append', default=[])
    p.add_argument('--provider', action='append', choices=['parallel', 'perplexity'])

    p = actions.add_parser('challenge', help='new investigation against a pinned case version')
    _common(p)
    p.add_argument('case_id')
    p.add_argument('--version', type=int, help='pin this case version (default: latest)')
    p.add_argument('--live', action='store_true')
    p.add_argument('--plan-only', action='store_true')
    p.add_argument('--max-steps', type=int)
    p.add_argument('--max-discovery', type=int)
    p.add_argument('--max-reads', type=int)
    p.add_argument('--max-rounds', type=int)
    p.add_argument('--provider', action='append', choices=['parallel', 'perplexity'])

    p = actions.add_parser('resume', help='continue a paused run without losing completed evidence')
    _common(p)
    p.add_argument('run_id')
    p.add_argument('--live', action='store_true')
    p.add_argument('--max-steps', type=int)

    p = actions.add_parser('show', help='show a research run')
    _common(p)
    p.add_argument('run_id')

    p = actions.add_parser('list', help='list recent research runs')
    _common(p)
    p.add_argument('--case-id')
    p.add_argument('--limit', type=int, default=20)

    p = actions.add_parser('cancel', help='cancel a run')
    _common(p)
    p.add_argument('run_id')

    p = actions.add_parser('synthesize', help='Lane B synthesis: separated kinds + challenges')
    _common(p)
    p.add_argument('case_id')
    p.add_argument('--version', type=int)
    p.add_argument('--run-id', help='optional research run to bind gaps/challenges')

    p = actions.add_parser('compare', help='diff answer versions: changed vs new vs reinterpretation')
    _common(p)
    p.add_argument('case_id')
    p.add_argument('--from-version', type=int, required=True)
    p.add_argument('--to-version', type=int, help='default: latest')
