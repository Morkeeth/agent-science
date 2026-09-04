"""Research terminal interface. Only this interface permits trusted code execution."""
import argparse
import json
import shlex
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
        item.set_defaults(func=run)
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
                host = item.add_mutually_exclusive_group()
                host.add_argument('--proposal', type=_object)
                host.add_argument('--reasoner', choices=['configured', 'gemini'])
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
    if arguments['action'] == 'resume' and arguments.get('reasoner'):
        from clearance import night_runs, reasoning
        result = night_runs.resume(arguments['run_id'], reasoner=reasoning.configured(),
                                   live=arguments.get('live', False), db=arguments.get('db'))
    elif arguments['action'] in ('protocol', 'execute-protocol'):
        from clearance import research_protocols
        if arguments['action'] == 'protocol':
            result = research_protocols.get(arguments['protocol_id'], version=arguments.get('version'), db=arguments.get('db'))
        else:
            result = research_protocols.execute(arguments['protocol_id'], check=arguments['check'], trusted=arguments['trusted'], version=arguments.get('version'), db=arguments.get('db'))
    else:
        result = research_workflow.handle(arguments)
    print(json.dumps(result, indent=2, ensure_ascii=False) if arguments.get('json') else render(result, db=arguments.get('db')))
    return 0


def render(result, *, db=None):
    """Compact terminal view; --json retains the full inspectable object."""
    suffix = ' --db ' + shlex.quote(str(db)) if db else ''
    if 'updates' in result:
        lines = [result['message']]
        for item in result['updates']:
            lines.append(f"{item['case_id']}: v{item['from_version']} → v{item['version']}; {len(item['affected_decisions'])} decisions need review")
        return '\n'.join(lines)
    if 'result' in result and 'experiment_id' in result:
        return f"{result['result']['summary']}\nExperiment: {result['experiment_id']}\nProtocol: {result['protocol_id']} v{result['protocol_version']}"
    if 'missing' in result and 'case_version' in result:
        lines = [f"Protocol {result['id']} v{result['version']}: {result['status']}",
                 f"Case: {result['case_id']} v{result['case_version']}"]
        if result['missing']:
            lines.append('Required: ' + ', '.join(result['missing']))
        else:
            lines.append('Plan saved. No experiment has run in this plan creation step.')
        lines.extend(f"Execution: {r['state']} ({r.get('experiment_id') or 'no recorded result'})" for r in result.get('executions', []))
        return '\n'.join(lines)
    if 'question_map' in result and 'status' in result:
        lines = [f"Research {result['id']}: {result['status']}", f"Case: {result['case_id']} v{result['case_version']}"]
        if result.get('stop_reason'):
            lines.append('Reason: ' + str(result['stop_reason']))
        lines.append('Completed steps: ' + str(sum(s.get('state') in ('completed', 'COMPLETED') for s in result.get('steps', []))))
        for node in result['question_map']:
            lines.append(f"{node.get('question', '')}: {node.get('gap', 'unresolved')}")
        lines.append(f"Answer: agent-science research show --case-id {result['case_id']}{suffix}")
        lines.append(f"Inspect: agent-science research context {result['id']}{suffix}")
        lines.append(f"Continue: agent-science research resume {result['id']}{suffix}")
        lines.append(f"Cancel: agent-science research cancel {result['id']}{suffix}")
        return '\n'.join(lines)
    if 'conclusions' in result:
        lines = [f"{result.get('question', 'Research answer')} (v{result['version']})"]
        if not result['conclusions']:
            lines.append('No assessed conclusion yet.')
        for conclusion in result['conclusions']:
            lines.append(f"[{conclusion.get('claim_state', conclusion['state'])}; {conclusion['relation']}] {conclusion['statement']}")
            lines.append('Rationale: ' + conclusion['rationale'])
            for condition in conclusion.get('conditions', []):
                lines.append(f"Scope — {condition['field']}: {condition['value']}")
            lines.append('Strongest challenge: ' + str(conclusion.get('strongest_challenge') or 'not specified'))
            anchor = conclusion.get('anchor', {})
            if anchor:
                lines.append(f"Source: {anchor.get('url')} — {anchor.get('quote')}")
            lines.append('What would change this: ' + str(conclusion.get('what_would_change') or 'not specified'))
        lines.append(f"Unresolved gaps: {len(result.get('gaps', []))}. Interpretations are authored; source occurrence does not prove entailment.")
        return '\n'.join(lines)
    if 'from_version' in result and 'evidence_changes' in result:
        return f"Case {result['case_id']}: v{result['from_version']} → v{result['version']}\nEvidence changes: {len(result['evidence_changes'])}; reasoning changes: {len(result['reasoning_changes'])}\n{result['meaning']}"
    if 'followed_at' in result:
        return f"Following {result['case_id']} from v{result['version']}. Run research updates to inspect saved changes."
    return json.dumps(result, indent=2, ensure_ascii=False)
