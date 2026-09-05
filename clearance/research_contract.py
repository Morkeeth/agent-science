"""Shared proposal boundaries; interpretations remain explicitly authored."""
SCHEMA_VERSION = 1
CONDITION_FIELDS = ('task','population','model','comparator','dataset','metric','budget','study_design','limitations')
RELATIONS = ('supports','contradicts','context','unresolved','different_scope')
ACTIONS = ('search','read','metadata','finish')


def validate_proposal(proposal, case_version):
    if not isinstance(proposal,dict):
        raise ValueError('reasoning proposal must be an object')
    if type(proposal.get('case_version')) is not int or proposal['case_version'] != case_version:
        raise ValueError('proposal requires the inspected case_version')
    action=proposal.get('next_action')
    if not isinstance(action,dict) or action.get('kind') not in ACTIONS:
        raise ValueError('next_action must be search, read, metadata or finish')
    if not isinstance(action.get('reason'),str) or not action['reason'].strip():
        raise ValueError('next_action needs a reason tied to the research gap')
    if action['kind']=='metadata' and set(action)-{'kind','reason','evidence_id','node_id'}:
        raise ValueError('metadata action accepts only kind, reason, evidence_id and node_id; registry results cannot be supplied by the host')
    if not isinstance(proposal.get('findings',[]),list) or len(proposal.get('findings',[]))>20:
        raise ValueError('findings must be a list of at most 20 entries')
    return proposal
