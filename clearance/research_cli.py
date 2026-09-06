"""Research terminal interface. Only this interface permits trusted code execution."""
import argparse
import sqlite3
import json
import shlex
import sys
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
    for name in ('desk', 'open', 'save', 'seen', 'start', 'show', 'context', 'resume', 'cancel', 'reconcile', 'challenge', 'compare', 'follow', 'update', 'updates', 'experiment-plan', 'protocol', 'policy', 'execute-protocol', 'evaluation-prepare', 'evaluation-create', 'evaluation-show', 'evaluation-record','evaluation-review','source-reviews','source-review','context-trials','context-trial-create','context-trial-show','context-trial-prepare','context-trial-complete','context-trial-abort'):
        item = actions.add_parser(name)
        item.set_defaults(func=run)
        item.add_argument('--db', default=argparse.SUPPRESS)
        item.add_argument('--json', action='store_true', default=argparse.SUPPRESS)
        if name == 'desk':
            item.add_argument('--query', default='')
            item.add_argument('--offset', type=int, default=0)
        elif name in ('open', 'save', 'seen'):
            item.add_argument('case_id')
            if name == 'open':
                item.add_argument('--claim', dest='claim_id')
                item.add_argument('--version', type=int)
            if name == 'seen':
                item.add_argument('--version', type=int, required=True)
        elif name == 'start':
            item.add_argument('question')
            item.add_argument('--case-id',help='continue research from this saved case without copying its evidence')
            item.add_argument('--root')
            item.add_argument('--policy', type=_object)
        elif name == 'show':
            item.add_argument('run_id', nargs='?')
            item.add_argument('--case-id')
            item.add_argument('--version', type=int)
        elif name in ('context', 'resume', 'cancel', 'reconcile'):
            item.add_argument('run_id')
            if name == 'reconcile':
                item.add_argument('--operation-id',required=True)
                item.add_argument('--case-version',type=int,required=True)
                item.add_argument('--acknowledgement',required=True,choices=['retain-reservation-and-do-not-retry'])
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
        elif name in ('evaluation-prepare', 'evaluation-create'):
            item.add_argument('--spec-file',type=Path,required=True)
        elif name in ('evaluation-show','evaluation-record','evaluation-review'):
            item.add_argument('evaluation_id')
            if name=='evaluation-record':
                item.add_argument('--observation-file',type=Path,required=True)
            if name=='evaluation-review':
                item.add_argument('--review-file',type=Path,required=True)
        elif name in ('source-review','source-reviews'):
            item.add_argument('case_id')
            if name=='source-review':
                item.add_argument('--version',type=int,required=True)
                item.add_argument('--review-file',type=Path,required=True,help='JSON: assessment_id, evidence_id, source_snapshot_hash, warning_fingerprint (from source-reviews), disposition (unaffected/revise/unresolved), rationale, notices [{notice_identity,evidence_id,quote,snapshot_hash}]. Inspect notice sources first.')
        elif name == 'context-trials':
            item.add_argument('case_id')
            item.add_argument('--case-version',type=int)
        elif name == 'context-trial-create':
            item.add_argument('--trial-file',type=Path,required=True)
        elif name in ('context-trial-show','context-trial-prepare','context-trial-complete','context-trial-abort'):
            item.add_argument('trial_id')
            if name!='context-trial-show':
                item.add_argument('--expected-version',type=int,required=True)
                item.add_argument('--trusted',action='store_true',required=True)
            if name=='context-trial-prepare':
                item.add_argument('--task',dest='task_id',required=True)
                item.add_argument('--arm',dest='arm_id',required=True)
                item.add_argument('--repetition',type=int,required=True)
            elif name in ('context-trial-complete','context-trial-abort'):
                item.add_argument('--attempt',dest='attempt_id',required=True)
                if name=='context-trial-abort':item.add_argument('--reason',required=True)
        elif name == 'policy':
            item.add_argument('--policy-file',type=Path,required=True)
            item.add_argument('--approve',action='store_true',required=True)
        elif name in ('protocol', 'execute-protocol'):
            item.add_argument('protocol_id')
            item.add_argument('--version', type=int)
            if name == 'execute-protocol':
                item.add_argument('--check', required=True)
                item.add_argument('--trusted', action='store_true', required=True)
    return parser


def run(args):
    try:
        return _run(args)
    except (ValueError, OSError, sqlite3.Error, argparse.ArgumentTypeError) as exc:
        error = {'error': str(exc), 'action': args.action}
        print(json.dumps(error) if getattr(args, 'json', False) else 'Research error: ' + str(exc), file=sys.stderr)
        return 2


def _run(args):
    arguments = {key: value for key, value in vars(args).items() if value is not None}
    for file_key,object_key in (('spec_file','evaluation_spec'),('observation_file','observation'),('review_file','evaluation_review'),('trial_file','trial_spec')):
        path=arguments.pop(file_key,None)
        if path:
            if file_key=='review_file' and arguments['action']=='source-review': object_key='source_review'
            arguments[object_key]=_object(path.read_text())
    protocol_file = arguments.pop('protocol_file', None)
    if protocol_file:
        arguments['protocol'] = _object(protocol_file.read_text())
    if arguments['action'] == 'policy':
        from clearance import research_policy
        result=research_policy.approve(_object(arguments['policy_file'].read_text()), db=arguments.get('db'))
    elif arguments['action'] in ('context-trial-prepare','context-trial-complete','context-trial-abort'):
        from clearance import context_trials
        kwargs={'expected_version':arguments['expected_version'],'trusted':arguments['trusted'],'db':arguments.get('db')}
        if arguments['action']=='context-trial-prepare':
            result=context_trials.prepare(arguments['trial_id'],task_id=arguments['task_id'],arm_id=arguments['arm_id'],repetition=arguments['repetition'],**kwargs)
        elif arguments['action']=='context-trial-complete':
            result=context_trials.complete(arguments['trial_id'],arguments['attempt_id'],**kwargs)
        else:
            result=context_trials.abort(arguments['trial_id'],arguments['attempt_id'],reason=arguments['reason'],**kwargs)
    elif arguments['action'] == 'resume' and arguments.get('reasoner'):
        from clearance import night_runs, reasoning
        result = night_runs.resume(arguments['run_id'], reasoner=reasoning.configured(),
                                   live=arguments.get('live', False), db=arguments.get('db'))
    elif arguments['action'] in ('protocol', 'execute-protocol'):
        from clearance import research_protocols
        if arguments['action'] == 'protocol':
            result = research_protocols.get(arguments['protocol_id'], version=arguments.get('version'), db=arguments.get('db'))
        else:
            result = research_protocols.execute(arguments['protocol_id'], check=arguments['check'], trusted=arguments['trusted'], version=arguments.get('version'), db=arguments.get('db'))
    elif arguments['action'] == 'evaluation-prepare':
        from clearance import research_evaluation
        result = research_evaluation.prepare(arguments['evaluation_spec'], db=arguments.get('db'))
    else:
        result = research_workflow.handle(arguments)
    print(json.dumps(result, indent=2, ensure_ascii=False) if arguments.get('json') else render(result, db=arguments.get('db')))
    return 0


def render(result, *, db=None):
    if result.get('object_type', '').startswith('investigation_'):
        from clearance import investigation_desk
        return investigation_desk.render(result, db=db)
    """Compact terminal view; --json retains the full inspectable object."""
    suffix = ' --db ' + shlex.quote(str(db)) if db else ''
    if result.get('object_type')=='source_reviews':
        lines=[f"Source reviews for {result['case_id']} v{result['version']}: {len(result['pending'])} pending; {len(result['resolved'])} resolved as authored"]
        for row in result['pending']+result['resolved']:
            lines.append(f"{row['assessment_id']} / {row['evidence_id']}: {row['state']}")
            lines.append(row['statement'])
            if row.get('warning_inherited_from'): lines.append('Warning also recorded on: '+', '.join(row['warning_inherited_from']))
            if row.get('non_rehabilitable'): lines.append('Cannot clear by acknowledgment: '+', '.join(row['non_rehabilitable']))
            if row['notice_identities']: lines.append('Inspect notices: '+', '.join(row['notice_identities']))
            if row.get('review'):
                lines.append('Authored disposition: '+row['review']['disposition'])
                if not row.get('review_binding_current',True): lines.append('Saved review no longer matches the current evidence.')
            for failure in row.get('notice_failures',[]):
                lines.append(failure['notice_identity']+': '+failure['reason'].replace('_',' '))
        if not result['pending'] and not result['resolved']: lines.append('No active source warnings attached to assessed conclusions.')
        lines.append('Registry notices remain on the source. A resolved review is an authored interpretation, not proof of correctness.')
        return '\n'.join(lines)
    if result.get('object_type')=='case_context_trials':
        lines=[f"Context trials for {result['case_id']} through case v{result['case_version']}"]
        for trial in result['trials']:
            summary=trial['summary']
            lines.append(f"{trial['id']}: {summary['finished']}/{summary['denominator']} finished; {summary['accepted']} accepted by frozen checks; protocol {trial['protocol_id']} v{trial['protocol_version']}")
        if not result['trials']: lines.append('No context trials recorded for this case version.')
        return '\n'.join(lines)
    if result.get('object_type')=='context_trial':
        summary=result['summary'];manifest=result['manifest']
        lines=[f"Context trial {result['id']} v{result['version']}: {summary['finished']}/{summary['denominator']} attempts finished",
               f"Accepted by frozen checks: {summary['accepted']}; prepared: {summary['prepared']}"]
        for arm in manifest['arms']:
            rows=[a for a in result['attempts'] if a['arm_id']==arm['id']]
            lines.append(f"{arm['id']}: {sum(a['state']=='ACCEPTED' for a in rows)} accepted / {len(manifest['tasks'])*manifest['repetitions']} planned attempts")
        for attempt in result['attempts']:
            if attempt['state'] in ('AWAITING_HOST','PREPARING','CHECKING','UNKNOWN'):
                lines.append(f"{attempt['id']}: {attempt['task_id']} / {attempt['arm_id']} / repetition {attempt['repetition']} — {attempt['state']}")
                lines.append('Worktree: '+attempt['worktree'])
        lines.append('Inspect tasks and receipts: agent-science research context-trial-show '+result['id']+suffix+' --json')
        lines.append('Selected-task acceptance only. Host isolation is not independently verified; token use and billing remain unknown.')
        return '\n'.join(lines)
    if 'manifest_hash' in result and 'coverage' in result:
        coverage=result['coverage'];reviews=result.get('review_coverage',{})
        lines=[f"Evaluation {result['id']}: {coverage['recorded']}/{coverage['denominator']} outcomes recorded",
               f"Independent reviews: {reviews.get('observations_with_reviews',0)}/{coverage['recorded']} recorded outcomes",
               'Unknown scientific judgments: '+str(sum(len(row['criteria']) for row in reviews.get('unknown_remaining',[]))),
               'Frozen manifest: '+result['manifest_hash']]
        for pair in result.get('paired_comparability',[]):
            lines.append('Comparison: '+('matched design' if pair.get('comparable_design') else 'unmatched design')+'; '+('matched recorded execution' if pair.get('comparable_execution') else 'execution comparability not established'))
        lines.append('Full evidence and review history: agent-science research evaluation-show '+result['id']+suffix+' --json')
        lines.append('Authored reviews are not automatic measures of truth.')
        return '\n'.join(lines)
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
        if result['status']=='stale':
            lines.append(f"Start from current evidence: agent-science research start {shlex.quote(result['question'])} --case-id {result['case_id']}{suffix}")
        elif result['status']=='needs_reconciliation':
            lines.append('Recovery: inspect the unknown operation and current case version, then use research reconcile. Capacity stays reserved.')
        elif result['status']=='stopped':
            lines.append('A fresh host finish proposal can save a bounded conclusion; external work remains stopped.')
        elif result['status'] not in ('completed','cancelled'):
            lines.append(f"Continue: agent-science research resume {result['id']}{suffix}")
            lines.append(f"Cancel: agent-science research cancel {result['id']}{suffix}")
        return '\n'.join(lines)
    if 'conclusions' in result:
        lines = [f"{result.get('question', 'Research answer')} (v{result['version']})"]
        if not result['conclusions']:
            lines.append('No assessed conclusion yet.')
        categories={'empirical_findings':'Empirical findings','official_constraints':'Official constraints',
            'field_adoption':'Field adoption — reported use, not measured effectiveness','unclassified':'Unclassified evidence'}
        ordered=sorted(result['conclusions'],key=lambda c:list(categories).index(c.get('category','unclassified')))
        previous_category=None
        for conclusion in ordered:
            category=conclusion.get('category','unclassified')
            if category!=previous_category:
                lines.append(categories[category]);previous_category=category
            lines.append(f"[{conclusion.get('claim_state', conclusion['state'])}; {conclusion['relation']}] {conclusion['statement']}")
            lines.append('Evidence class: ' + conclusion.get('category','unclassified'))
            if conclusion.get('practical_consequence'):
                lines.append('Practical consequence (inference): ' + conclusion['practical_consequence'])
            lines.append('Rationale: ' + conclusion['rationale'])
            for condition in conclusion.get('conditions', []):
                lines.append(f"Scope — {condition['field']}: {condition['value']}")
            lines.append('Strongest challenge: ' + str(conclusion.get('strongest_challenge') or 'not specified'))
            anchor = conclusion.get('anchor', {})
            if anchor:
                lines.append(f"Source: {anchor.get('url')} — {anchor.get('quote')}")
            lines.append('What would change this: ' + str(conclusion.get('what_would_change') or 'not specified'))
        for gap in result.get('gaps', [])[:10]:
            lines.append('Gap: ' + str(gap.get('reason','unresolved')) + (' — '+gap['meaning'] if gap.get('meaning') else ''))
        lines.append(f"Unresolved gaps: {len(result.get('gaps', []))}. Interpretations are authored; source occurrence does not prove entailment.")
        return '\n'.join(lines)
    if 'from_version' in result and 'evidence_changes' in result:
        return f"Case {result['case_id']}: v{result['from_version']} → v{result['version']}\nEvidence changes: {len(result['evidence_changes'])}; reasoning changes: {len(result['reasoning_changes'])}\n{result['meaning']}"
    if 'followed_at' in result:
        return f"Following {result['case_id']} from v{result['version']}. Run research updates to inspect saved changes."
    return json.dumps(result, indent=2, ensure_ascii=False)
