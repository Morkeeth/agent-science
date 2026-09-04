#!/usr/bin/env python3
"""Lane B baseline arms — numbers re-derived at the object every run.

Arms:
  1. naive_title_merge — merges papers by title token overlap (the two-hour mistake)
  2. naive_auto_contradict — any opposite-direction finding is contradicts, ignoring task
  3. always_same_study — collapses every URL into one study (null that can beat us)
  4. shipping — Lane B study identity + scope guard

If a naive or null arm wins a metric, that is the finding — print it loud.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clearance import claim_graph, conditions, study

PAPER_A = """
Task: SWE-bench verified repository repair (Python).
Metric: resolve rate.
Result: Persistent memory increased resolve rate.
Limitation: may not generalize beyond Python repair.
"""
PAPER_B = """
Task: HotpotQA multi-hop question answering (English).
Metric: exact match accuracy.
Result: Persistent memory did not improve exact match.
Limitation: not a causal claim about coding effectiveness.
"""
PAPER_A_MIRRORS = [
    'https://arxiv.org/abs/2401.11111',
    'https://arxiv.org/pdf/2401.11111.pdf',
    'https://arxiv.org/html/2401.11111',
    'https://ar5iv.labs.arxiv.org/html/2401.11111',
    'https://doi.org/10.48550/arXiv.2401.11111',
]
PAPER_B_URL = 'https://arxiv.org/abs/2402.22222'
TITLE_A = 'Persistent memory for coding agents on repository repair'
TITLE_B = 'Persistent memory for coding agents on multi-hop QA'


def naive_title_merge(titles_and_urls):
    """Two-hour baseline: Jaccard on title tokens ≥ 0.4 ⇒ same study."""
    groups = []
    for title, url in titles_and_urls:
        tokens = set(re.findall(r'[a-z0-9]+', title.lower()))
        placed = False
        for g in groups:
            overlap = len(tokens & g['tokens']) / max(1, len(tokens | g['tokens']))
            if overlap >= 0.4:
                g['urls'].append(url)
                g['titles'].append(title)
                g['tokens'] |= tokens
                placed = True
                break
        if not placed:
            groups.append({'urls': [url], 'titles': [title], 'tokens': tokens})
    return groups


def naive_auto_contradict(text_a, text_b):
    """Ignore scope: opposite verbs ⇒ contradicts."""
    neg = bool(re.search(r'\b(did not|not improve|no benefit|fail|increas\w+ (?:error|harm))\b', text_b, re.I))
    pos = bool(re.search(r'\b(increased|improved|helps?|benefit)\b', text_a, re.I))
    if pos and neg:
        return 'contradicts'
    return 'unresolved'


def always_same_study(urls):
    return [{'urls': list(urls), 'identity': 'null_collapse', 'id': 'all'}]


def main():
    # --- Study identity metrics ---
    mirror_urls = PAPER_A_MIRRORS
    shipping_groups = study.group_documents(mirror_urls + [PAPER_B_URL])
    shipping_mirror_count = sum(1 for g in shipping_groups if g['id'] == '2401.11111')
    shipping_total = len(shipping_groups)

    title_rows = (
        [(TITLE_A, u) for u in PAPER_A_MIRRORS] + [(TITLE_B, PAPER_B_URL)]
    )
    naive_groups = naive_title_merge(title_rows)
    null_groups = always_same_study(mirror_urls + [PAPER_B_URL])

    # Correct: 5 mirrors → 1 study; paper B separate → 2 studies total.
    truth_mirror_studies = 1
    truth_total_studies = 2

    def score_identity(n_mirrors_as_one, n_total):
        # 1 point for collapsing mirrors; 1 point for keeping B separate.
        mirror_ok = 1 if n_mirrors_as_one == truth_mirror_studies else 0
        total_ok = 1 if n_total == truth_total_studies else 0
        return mirror_ok + total_ok

    # For naive title merge: all 5 A mirrors share title A → 1 group; B may merge if overlap high.
    naive_a = next((g for g in naive_groups if any(u in PAPER_A_MIRRORS for u in g['urls'])), None)
    naive_mirror_as_one = 1 if naive_a and set(PAPER_A_MIRRORS) <= set(naive_a['urls']) else 0
    # If B was swallowed into A's group, total studies = 1 (wrong).
    naive_total = len(naive_groups)

    shipping_score = score_identity(1 if shipping_mirror_count == 1 else 0, shipping_total)
    # naive: mirrors collapse via same title (good) but may wrongly merge B
    naive_score = score_identity(naive_mirror_as_one, naive_total)
    null_score = score_identity(1 if len(null_groups) == 1 else 0, len(null_groups))

    # --- Scope / contradiction metrics ---
    cond_a = conditions.extract(PAPER_A)
    cond_b = conditions.extract(PAPER_B)
    shipping_rel = claim_graph.relate_findings(
        statement_a='Persistent memory helps coding repair.',
        conditions_a=cond_a,
        statement_b='Persistent memory does not help HotpotQA.',
        conditions_b=cond_b,
        direction_conflict=True,
    )['relation']
    naive_rel = naive_auto_contradict(PAPER_A, PAPER_B)

    # Truth: different_scope (not contradicts)
    shipping_scope_ok = shipping_rel == 'different_scope'
    naive_scope_ok = naive_rel == 'different_scope'  # naive never emits this
    null_scope_ok = False  # null has no scope concept; treat as fail

    result = {
        'identity': {
            'truth': {'mirror_studies': truth_mirror_studies, 'total_studies': truth_total_studies},
            'shipping': {
                'groups': [{'identity': g['identity'], 'id': g['id'], 'n_urls': len(g['urls'])}
                           for g in shipping_groups],
                'score': shipping_score,
            },
            'naive_title_merge': {
                'groups': [{'titles': g['titles'], 'n_urls': len(g['urls'])} for g in naive_groups],
                'score': naive_score,
                'wrongly_merged_b': naive_total < truth_total_studies,
            },
            'always_same_study_null': {
                'groups': null_groups,
                'score': null_score,
            },
        },
        'scope': {
            'truth_relation': 'different_scope',
            'shipping_relation': shipping_rel,
            'naive_auto_contradict_relation': naive_rel,
            'shipping_ok': shipping_scope_ok,
            'naive_ok': naive_scope_ok,
            'null_ok': null_scope_ok,
        },
        'title_merge_refused': study.merge_by_title(TITLE_A, TITLE_B),
        'verdict': {
            'shipping_identity_beats_null': shipping_score > null_score,
            'shipping_identity_vs_naive': shipping_score - naive_score,
            'shipping_scope_beats_naive': shipping_scope_ok and not naive_scope_ok,
            'embarrassing': [],
        },
        'meaning': (
            'Scores re-derived this run. Identity score = mirror-collapse point + separation point. '
            'Scope truth is different_scope for different tasks.'
        ),
    }

    emb = result['verdict']['embarrassing']
    if null_score >= shipping_score:
        emb.append('null always_same_study matched or beat shipping on identity score')
    if naive_score > shipping_score:
        emb.append('naive title-merge beat shipping on identity score')
    if not shipping_scope_ok:
        emb.append('shipping failed to classify different-task papers as different_scope')
    if naive_scope_ok and not shipping_scope_ok:
        emb.append('naive scope arm beat shipping')
    if result['identity']['naive_title_merge']['wrongly_merged_b']:
        # This is expected embarrassment of the naive arm — record as finding about baseline.
        result['verdict']['naive_title_merge_false_positive'] = True

    print(json.dumps(result, indent=2))
    # Exit 0 always when the measurement completed; embarrassment is in the payload.
    if not shipping_scope_ok or shipping_score < 2:
        print('LANE_B_EVAL: shipping missed a required point', file=sys.stderr)
        return 1
    print('LANE_B_EVAL OK', file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
