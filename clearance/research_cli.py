"""CLI for adaptive research runs: research / challenge / resume / follow / updates / experiment-plan."""
import argparse
import json
import sqlite3
from clearance import research_run

KNOWN = frozenset({
    'start', 'challenge', 'resume', 'show', 'list', 'cancel',
    'follow', 'unfollow', 'updates', 'experiment-plan',
})


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
            print(json.dumps(research_run.public_run(result), indent=2) if args.json
                  else research_run.render_run(result), end='\n')
            return 0
        if args.action == 'challenge':
            result = research_run.start_challenge(
                args.case_id, version=getattr(args, 'version', None),
                live=live, db=db, limits=limits, providers=providers,
                execute=not plan_only, max_steps=max_steps,
            )
            print(json.dumps(research_run.public_run(result), indent=2) if args.json
                  else research_run.render_run(result), end='\n')
            return 0
        if args.action == 'resume':
            result = research_run.resume(args.run_id, live=live, db=db, max_steps=max_steps)
            print(json.dumps(research_run.public_run(result), indent=2) if args.json
                  else research_run.render_run(result), end='\n')
            return 0
        if args.action == 'show':
            result = research_run.get_run(args.run_id, db=db)
            print(json.dumps(research_run.public_run(result), indent=2) if args.json
                  else research_run.render_run(result), end='\n')
            return 0
        if args.action == 'list':
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
        if args.action == 'cancel':
            result = research_run.cancel(args.run_id, db=db)
            print(json.dumps(research_run.public_run(result), indent=2) if args.json
                  else research_run.render_run(result), end='\n')
            return 0

        # --- Lane C: follow / updates / experiment-plan ---
        if args.action == 'follow':
            from clearance import follow as follow_mod
            if getattr(args, 'list', False) or not getattr(args, 'case_id', None):
                rows = follow_mod.list_followed(db=db, limit=getattr(args, 'limit', 50))
                print(json.dumps(rows, indent=2) if args.json else follow_mod.render(rows), end='')
                return 0
            result = follow_mod.follow(args.case_id, db=db, note=getattr(args, 'note', '') or '')
            print(json.dumps(follow_mod.public_follow(result), indent=2) if args.json
                  else follow_mod.render([result]), end='')
            return 0
        if args.action == 'unfollow':
            from clearance import follow as follow_mod
            result = follow_mod.unfollow(getattr(args, 'case_id', None), follow_id=getattr(args, 'follow_id', None), db=db)
            print(json.dumps(follow_mod.public_follow(result), indent=2) if args.json
                  else follow_mod.render([result]), end='')
            return 0
        if args.action == 'updates':
            from clearance import updates
            if getattr(args, 'show', None):
                result = updates.get_run(args.show, db=db)
            else:
                result = updates.run_updates(
                    db=db, case_id=getattr(args, 'case_id', None),
                    live=live, refresh=not getattr(args, 'no_refresh', False),
                    limit=getattr(args, 'limit', 50),
                )
            print(json.dumps(updates.public_run(result), indent=2) if args.json
                  else updates.render_run(result), end='')
            return 0
        if args.action == 'experiment-plan':
            from clearance import experiment_protocol as proto
            if getattr(args, 'execute', False):
                result = proto.execute(args.protocol_id, db=db, version=getattr(args, 'version', None))
            elif getattr(args, 'show', None):
                result = proto.get(args.show, version=getattr(args, 'version', None), db=db)
            elif getattr(args, 'list', False):
                rows = proto.list_protocols(case_id=getattr(args, 'case_id', None), db=db)
                if args.json:
                    print(json.dumps(rows, indent=2))
                else:
                    for p in rows:
                        print(f"{p['id']} · v{p['version']} · {p['status']} · {p['kind']} · case {p['case_id']}")
                        print(f"  {p['hypothesis'][:100]}")
                return 0
            else:
                budget = None
                if getattr(args, 'runs', None) or getattr(args, 'timeout', None):
                    budget = {}
                    if args.runs is not None:
                        budget['paired_runs'] = args.runs
                    if args.timeout is not None:
                        budget['timeout_seconds'] = args.timeout
                result = proto.create(
                    args.case_id,
                    hypothesis=args.hypothesis,
                    kind=getattr(args, 'kind', 'code_change') or 'code_change',
                    claim_ids=getattr(args, 'claim', None) or (),
                    repo=getattr(args, 'root', None) or getattr(args, 'repo', None),
                    baseline_ref=getattr(args, 'baseline', None),
                    intervention_ref=getattr(args, 'intervention', None),
                    tasks=getattr(args, 'task', None) or (),
                    outcome_definition=getattr(args, 'outcome', '') or '',
                    comparison_budget=budget,
                    stopping_rule=getattr(args, 'stopping_rule', '') or '',
                    acceptance_check=getattr(args, 'check', None),
                    db=db,
                )
            print(json.dumps(proto.public_protocol(result), indent=2) if args.json
                  else proto.render(result), end='')
            return 0

        raise ValueError(f'unknown research action: {args.action}')
    except (ValueError, OSError, sqlite3.Error) as exc:
        print(json.dumps({'error': str(exc)}) if getattr(args, 'json', False)
              else f'Cannot complete research action: {exc}')
        return 2


def add_parser(sub):
    research = sub.add_parser(
        'research',
        help='adaptive investigation: research, challenge, follow, updates, experiment-plan',
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

    p = actions.add_parser('follow', help='track a case for day-two update reports')
    _common(p)
    p.add_argument('case_id', nargs='?', help='case to follow (omit with --list)')
    p.add_argument('--note', default='')
    p.add_argument('--list', action='store_true', help='list followed questions')
    p.add_argument('--limit', type=int, default=50)

    p = actions.add_parser('unfollow', help='stop tracking a followed question')
    _common(p)
    p.add_argument('case_id', nargs='?')
    p.add_argument('--follow-id')

    p = actions.add_parser('updates', help='explicit update run: ranked change report for followed questions')
    _common(p)
    p.add_argument('--case-id', help='limit to one followed case')
    p.add_argument('--live', action='store_true', help='fetch sources on the web')
    p.add_argument('--no-refresh', action='store_true', help='compare saved versions only; no re-collect')
    p.add_argument('--show', help='show a prior update run id')
    p.add_argument('--limit', type=int, default=50)

    p = actions.add_parser('experiment-plan', help='record a versioned experiment protocol (plan, not a result)')
    _common(p)
    p.add_argument('case_id', nargs='?', help='case this protocol belongs to')
    p.add_argument('--hypothesis', default='')
    p.add_argument('--kind', choices=sorted(['code_change', 'observation', 'manual']), default='code_change')
    p.add_argument('--claim', action='append', default=[], help='claim id to pin (repeatable)')
    p.add_argument('--root', help='repository root (must match case repo when set)')
    p.add_argument('--repo', help='alias for --root')
    p.add_argument('--baseline', help='baseline git ref')
    p.add_argument('--intervention', help='intervention/candidate git ref')
    p.add_argument('--check', help='trusted acceptance .py script')
    p.add_argument('--task', action='append', default=[], help='fixed task description (repeatable)')
    p.add_argument('--outcome', default='')
    p.add_argument('--stopping-rule', default='')
    p.add_argument('--runs', type=int, help='paired runs budget')
    p.add_argument('--timeout', type=int, help='per-run timeout seconds')
    p.add_argument('--list', action='store_true')
    p.add_argument('--show', help='show protocol id')
    p.add_argument('--execute', action='store_true', help='run a compatible code_change protocol')
    p.add_argument('--protocol-id', help='protocol id for --execute')
    p.add_argument('--version', type=int, help='protocol version for show/execute')
