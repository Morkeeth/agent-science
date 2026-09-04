"""Claim relationships: support, contradiction, different scope, context, unresolved.

Authorship is preserved. Different tasks are not automatic contradictions.
Qualitative interview designs cannot authorize causal effectiveness claims.
"""
from __future__ import annotations

import re
import uuid

from clearance import conditions as conditions_mod
from clearance import study as study_mod

RELATIONS = (
    'supports',
    'contradicts',
    'different_scope',
    'context',
    'unresolved',
)

_QUALITATIVE = re.compile(
    r'\b(qualitative interview|semi-structured interview|interview study|'
    r'exploratory interview|thematic analysis)\b',
    re.I,
)
_CAUSAL = re.compile(
    r'\b(causally?|causes?|causal (?:claim|effect|impact)|improves? effectiveness|'
    r'increases? (?:effectiveness|performance) causally)\b',
    re.I,
)


def relate_findings(*, statement_a, conditions_a, statement_b, conditions_b,
                    direction_conflict=False):
    """Propose a relation between two findings. Never auto-contradict across tasks."""
    scope = conditions_mod.scopes_compatible(conditions_a, conditions_b, require=('task',))
    if scope['compatible'] is False:
        return {
            'relation': 'different_scope',
            'scope_fields': scope['scope_fields'],
            'unknown_fields': scope['unknown_fields'],
            'direction_conflict': bool(direction_conflict),
            'meaning': (
                'Effect directions were not compared as contradiction because required '
                'scope fields differ. Different tasks are not automatic contradictions.'
            ),
        }
    if direction_conflict and scope['compatible'] is True:
        return {
            'relation': 'contradicts',
            'scope_fields': [],
            'unknown_fields': scope['unknown_fields'],
            'direction_conflict': True,
            'meaning': 'Same known task scope with conflicting effect direction — authored contradiction candidate.',
        }
    if direction_conflict and scope['compatible'] is None:
        # Unknown scope does not prove different_scope. A challenge may still record
        # contradicts from an explicit contrary cue; it is not an automatic cross-task merge.
        return {
            'relation': 'contradicts',
            'scope_fields': [],
            'unknown_fields': scope['unknown_fields'],
            'direction_conflict': True,
            'meaning': (
                'Effect directions conflict and task scope is unknown on at least one side. '
                'Recorded as contradicts from the contrary cue; different_scope requires a known task mismatch.'
            ),
        }
    return {
        'relation': 'context' if not direction_conflict else 'unresolved',
        'scope_fields': scope['scope_fields'],
        'unknown_fields': scope['unknown_fields'],
        'direction_conflict': bool(direction_conflict),
        'meaning': 'No scoped contradiction established.',
    }


def causal_claim_gate(*, statement, conditions):
    """Refuse promoting a qualitative interview study into a causal effectiveness claim."""
    design = (conditions.get('study_design') or {})
    limitations = (conditions.get('limitations') or {})
    design_text = ' '.join(filter(None, [design.get('value'), design.get('span'),
                                         limitations.get('value'), limitations.get('span')]))
    if _CAUSAL.search(statement or '') and _QUALITATIVE.search(design_text or ''):
        return {
            'allowed': False,
            'reason': 'qualitative_design_not_causal',
            'meaning': (
                'A qualitative interview study cannot become a causal claim about effectiveness. '
                'Record as context or unresolved, not supports for a causal statement.'
            ),
        }
    if _CAUSAL.search(statement or '') and design.get('status') != 'known':
        return {
            'allowed': False,
            'reason': 'unknown_design_for_causal_claim',
            'meaning': 'Causal effectiveness claims require a known study design span.',
        }
    return {'allowed': True, 'reason': None, 'meaning': 'Gate does not refuse this statement.'}


def validate_assessment_relation(relation, *, statement, evidence_text, evidence_conditions=None):
    """Guard before recording an assessment. Fabricated quotes are handled by research.assess."""
    if relation not in RELATIONS:
        return {'ok': False, 'reason': f'relation must be one of {RELATIONS}'}
    evidence_conditions = evidence_conditions or conditions_mod.extract(evidence_text or '')
    if relation == 'supports':
        gate = causal_claim_gate(statement=statement, conditions=evidence_conditions)
        if not gate['allowed']:
            return {'ok': False, 'reason': gate['reason'], 'gate': gate}
    return {'ok': True, 'reason': None, 'conditions': evidence_conditions}


def from_case(data):
    """Build a claim graph from a case: nodes = claims + studies; edges = assessments + scope links."""
    studies = study_mod.build_studies(data.get('evidence', []))
    study_by_eid = {}
    for s in studies:
        for ref in s['document_refs']:
            if ref.get('evidence_id'):
                study_by_eid[ref['evidence_id']] = s

    nodes = []
    for claim in data.get('claims', []):
        nodes.append({
            'id': claim['id'],
            'type': 'claim',
            'statement': claim.get('statement'),
        })
    for s in studies:
        nodes.append({
            'id': f"study:{s['identity']}:{s['id']}",
            'type': 'study',
            'identity': s['identity'],
            'study_id': s['id'],
            'conditions': s.get('conditions'),
        })

    edges = []
    evidence = {e['id']: e for e in data.get('evidence', [])}
    for claim in data.get('claims', []):
        superseded = {a.get('supersedes') for a in claim.get('assessments', [])}
        for a in claim.get('assessments', []):
            if a['id'] in superseded:
                continue
            anchor = a.get('anchor') or {}
            eid = anchor.get('evidence_id')
            edge = {
                'id': a['id'],
                'from': claim['id'],
                'to': eid,
                'relation': a['relation'],
                'rationale': a.get('rationale'),
                'authorship': a.get('authorship'),
                'evidence_version': a.get('evidence_version'),
                'at': a.get('at'),
            }
            if eid and eid in study_by_eid:
                edge['study_key'] = study_by_eid[eid]['canonical_key']
            edges.append(edge)

    # Cross-study scope edges: when two studies have findings assessed on claims,
    # record different_scope rather than implying contradiction.
    claim_study_conds = []
    for claim in data.get('claims', []):
        superseded = {a.get('supersedes') for a in claim.get('assessments', [])}
        for a in claim.get('assessments', []):
            if a['id'] in superseded:
                continue
            eid = (a.get('anchor') or {}).get('evidence_id')
            if not eid or eid not in evidence:
                continue
            e = evidence[eid]
            cond = conditions_mod.extract(e.get('snapshot_text') or '', url=e.get('url'))
            claim_study_conds.append((claim, a, cond, e))

    for i, (c1, a1, cond1, e1) in enumerate(claim_study_conds):
        for c2, a2, cond2, e2 in claim_study_conds[i + 1:]:
            if e1['url'] == e2['url']:
                continue
            direction_conflict = (
                {a1['relation'], a2['relation']} >= {'supports', 'contradicts'}
                or (a1['relation'] == 'supports' and a2['relation'] == 'supports'
                    and c1['id'] != c2['id'])
            )
            # Only emit scope edges when effect-bearing assessments exist.
            if a1['relation'] not in ('supports', 'contradicts') and a2['relation'] not in ('supports', 'contradicts'):
                continue
            proposed = relate_findings(
                statement_a=c1.get('statement', ''),
                conditions_a=cond1,
                statement_b=c2.get('statement', ''),
                conditions_b=cond2,
                direction_conflict=True,
            )
            if proposed['relation'] == 'different_scope':
                edges.append({
                    'id': uuid.uuid4().hex[:12],
                    'from': c1['id'],
                    'to': c2['id'],
                    'relation': 'different_scope',
                    'scope_fields': proposed['scope_fields'],
                    'evidence_urls': [e1['url'], e2['url']],
                    'authorship': 'lane_b_scope_guard',
                    'meaning': proposed['meaning'],
                })

    return {
        'nodes': nodes,
        'edges': edges,
        'studies': studies,
        'meaning': (
            'Edges are authored assessments plus scope-guard links. '
            'Quote occurrence is verified elsewhere; entailment is not mechanical.'
        ),
    }


def challenge_relation_for_new_evidence(*, claim_statement, claim_support_conditions,
                                        new_evidence_text, new_evidence_url=None,
                                        suggests_conflict=False):
    """Used by challenge loop: choose contradicts vs different_scope vs unresolved."""
    new_cond = conditions_mod.extract(new_evidence_text or '', url=new_evidence_url)
    return relate_findings(
        statement_a=claim_statement,
        conditions_a=claim_support_conditions or conditions_mod.extract(''),
        statement_b=claim_statement,
        conditions_b=new_cond,
        direction_conflict=suggests_conflict,
    ), new_cond
