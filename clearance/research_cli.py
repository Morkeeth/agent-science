"""Research terminal interface. Only this interface permits trusted code execution."""
import argparse
import json
from pathlib import Path

from clearance import research_workflow


def _object(value):
    try:
        result = json.loads(value)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc
    if not isinstance(result, dict):
        raise argparse.ArgumentTypeError('must be a JSON object')
    return result


def add_parser(sub):
    parser = sub.add_parser('research', help='Plan, inspect and continue local research')
    parser.add_argument('--db', default=argparse.SUPPRESS)
    parser.add_argument('--json', action='store_true', default=argparse.SUPPRESS)
    actions = parser.add_subparsers(dest='action', required=True)
    for name in ('start', 'show', 'context', 'resume', 'cancel', 'challenge', 'compare', 'follow', 'update', 'updates', 'experiment-plan', 'protocol', 'execute-protocol'):
        item = actions.add_parser(name)
        item.add_argument('--db', default=argparse.SUPPRESS)
        item.add_argument('--json', action='store_true', default=argparse.SUPPRESS)
        if name == 'start':
            item.add_argument('question')
            item.add_argument('--root')
            item.add_argument('--policy', type=_object)
        elif name == 'show':
            item.add_argument('run_id', nargs='?')
            item.add_argument('--case-id')
            item.add_argument('--version', type=int)
        elif name in ('context', 'resume', 'cancel'):
            item.add_argument('run_id')
            if name == 'resume':
                item.add_argument('--proposal', type=_object)
                item.add_argument('--live', action='store_true')
        elif name in ('challenge', 'compare', 'follow', 'update', 'experiment-plan'):
            item.add_argument('case_id')
            if name == 'compare':
                item.add_argument('--from-version', type=int, required=True)
            if name in ('challenge', 'update'):
                item.add_argument('--policy', type=_object)
            if name == 'experiment-plan':
                item.add_argument('--root')
                item.add_argument('--protocol', type=_object, default={})
                item.add_argument('--protocol-file', type=Path)
                item.add_argument('--protocol-id')
        elif name in ('protocol', 'execute-protocol'):
            item.add_argument('protocol_id')
            item.add_argument('--version', type=int)
            if name == 'execute-protocol':
                item.add_argument('--check', required=True)
                item.add_argument('--trusted', action='store_true', required=True)
    return parser


def run(args):
    arguments = {key: value for key, value in vars(args).items() if value is not None}
    protocol_file = arguments.pop('protocol_file', None)
    if protocol_file:
        arguments['protocol'] = _object(protocol_file.read_text())
    if arguments['action'] in ('protocol', 'execute-protocol'):
        from clearance import research_protocols
        if arguments['action'] == 'protocol':
            result = research_protocols.get(arguments['protocol_id'], version=arguments.get('version'), db=arguments.get('db'))
        else:
            result = research_protocols.execute(arguments['protocol_id'], check=arguments['check'], trusted=arguments['trusted'], version=arguments.get('version'), db=arguments.get('db'))
    else:
        result = research_workflow.handle(arguments)
    # Structured terminal output preserves provenance and missing fields even without --json.
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0
