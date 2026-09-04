#!/usr/bin/env python3
"""Lane B baseline arms — every number re-derived by opening fixtures/lane-b/.

Arms:
  1. naive_title_merge — Jaccard on title tokens (two-hour mistake)
  2. naive_auto_contradict — opposite verbs ⇒ contradicts, ignoring task
  3. always_same_study — collapse every URL into one study (null)
  4. shipping — Lane B study identity + scope guard

If a naive or null arm wins a metric, that is the finding — print it loud.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import claim_graph, conditions, study

FIXTURE = ROOT / 'fixtures' / 'lane-b'
MANIFEST = json.loads((FIXTURE / 'MANIFEST.json').read_text())


def load_papers():
    papers = []
    for row in MANIFEST['papers']:
        text = (FIXTURE / row['text_file']).read_text()
        papers.append({**row, 'text': text})
    return papers


def naive_title_merge(titles_and_urls):
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
    neg = bool(re.search(r'\b(did not|not improve|no benefit|fail|increas\w+ (?:error|harm))\b', text_b, re.I))
    pos = bool(re.search(r'\b(increased|improved|helps?|benefit)\b', text_a, re.I))
    if pos and neg:
        return 'contradicts'
    return 'unresolved'


def always_same_study(urls):
    return [{'urls': list(urls), 'identity': 'null_collapse', 'id': 'all'}]


def main():
    papers = load_papers()
    by_id = {p['id']: p for p in papers}
    swe = by_id['memory-swebench-2401']
    hot = by_id['memory-hotpotqa-2402']
    all_urls = [u for p in papers for u in p['urls']]

    # Truth from the fixture object (manifest), checked against shipping behavior.
    truth_studies = MANIFEST['truth']['unique_studies_from_all_urls']
    truth_mirrors = MANIFEST['truth']['swebench_mirror_count']
    truth_rel = MANIFEST['truth']['swebench_vs_hotpotqa_relation']

    # Re-derive mirror count at the object
    assert len(swe['urls']) == truth_mirrors, (
        f"manifest swebench_mirror_count={truth_mirrors} but fixture lists {len(swe['urls'])} URLs"
    )

    shipping_groups = study.group_documents(all_urls)
    shipping_total = len(shipping_groups)
    shipping_swe = next((g for g in shipping_groups if g['id'] == '2401.11111'), None)
    shipping_mirror_ok = bool(shipping_swe and len(shipping_swe['urls']) == truth_mirrors)

    title_rows = [(p['title'], u) for p in papers for u in p['urls']]
    naive_groups = naive_title_merge(title_rows)
    null_groups = always_same_study(all_urls)

    def score_identity(total, mirror_ok):
        return (1 if mirror_ok else 0) + (1 if total == truth_studies else 0)

    naive_swe = next((g for g in naive_groups if any(u in swe['urls'] for u in g['urls'])), None)
    naive_mirror_ok = bool(naive_swe and set(swe['urls']) <= set(naive_swe['urls']))
    naive_total = len(naive_groups)
    naive_merged_hot = bool(naive_swe and any(u in hot['urls'] for u in naive_swe['urls']))

    shipping_score = score_identity(shipping_total, shipping_mirror_ok)
    naive_score = score_identity(naive_total, naive_mirror_ok)
    null_score = score_identity(len(null_groups), len(null_groups) == 1 and truth_mirrors > 0)

    cond_a = conditions.extract(swe['text'])
    cond_b = conditions.extract(hot['text'])
    shipping_rel = claim_graph.relate_findings(
        statement_a='Persistent memory helps coding repair.',
        conditions_a=cond_a,
        statement_b='Persistent memory does not help HotpotQA.',
        conditions_b=cond_b,
        direction_conflict=True,
    )['relation']
    naive_rel = naive_auto_contradict(swe['text'], hot['text'])

    # Qualitative gate — open the interview fixture
    interview = by_id['interview-memory-qual']
    gate = claim_graph.causal_claim_gate(
        statement='Persistent memory causally improves coding-agent effectiveness.',
        conditions=conditions.extract(interview['text']),
    )

    result = {
        'fixture': str(FIXTURE),
        'identity': {
            'truth': {'total_studies': truth_studies, 'swebench_mirrors': truth_mirrors},
            'shipping': {
                'groups': [{'identity': g['identity'], 'id': g['id'], 'n_urls': len(g['urls'])}
                           for g in shipping_groups],
                'score': shipping_score,
                'mirror_ok': shipping_mirror_ok,
            },
            'naive_title_merge': {
                'n_groups': naive_total,
                'score': naive_score,
                'wrongly_merged_hotpotqa': naive_merged_hot,
            },
            'always_same_study_null': {'n_groups': len(null_groups), 'score': null_score},
        },
        'scope': {
            'truth_relation': truth_rel,
            'shipping_relation': shipping_rel,
            'naive_auto_contradict_relation': naive_rel,
            'shipping_ok': shipping_rel == truth_rel,
            'naive_ok': naive_rel == truth_rel,
        },
        'qualitative_causal_gate': gate,
        'title_merge_refused': study.merge_by_title(swe['title'], hot['title']),
        'verdict': {
            'shipping_identity_beats_null': shipping_score > null_score,
            'shipping_identity_vs_naive': shipping_score - naive_score,
            'shipping_scope_beats_naive': shipping_rel == truth_rel and naive_rel != truth_rel,
            'embarrassing': [],
        },
        'meaning': (
            'Scores re-derived from fixtures/lane-b this run. '
            'Identity score = mirror-collapse point + total-studies point.'
        ),
    }
    emb = result['verdict']['embarrassing']
    if null_score >= shipping_score:
        emb.append('null always_same_study matched or beat shipping on identity score')
    if naive_score > shipping_score:
        emb.append('naive title-merge beat shipping on identity score')
    if not result['scope']['shipping_ok']:
        emb.append('shipping failed swebench vs hotpotqa scope truth')
    if not gate.get('allowed') is False:
        emb.append('qualitative causal gate did not refuse')
    if naive_merged_hot:
        result['verdict']['naive_title_merge_false_positive'] = True

    print(json.dumps(result, indent=2))
    if shipping_score < 2 or not result['scope']['shipping_ok'] or gate.get('allowed') is not False:
        print('LANE_B_EVAL: shipping missed a required point', file=sys.stderr)
        return 1
    print('LANE_B_EVAL OK', file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
