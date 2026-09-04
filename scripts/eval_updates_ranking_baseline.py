#!/usr/bin/env python3
"""Baseline arm: naive any-change vs effect-ranked updates.

Measures against a fixture we did not specially tune for the shipping arm after
freeze: one cited decision-affecting change + one uncited sidebar change, and a
noise-only case. If ranked loses to naive on precision of material headlines,
that is the finding.
"""
from __future__ import annotations

import sys
from pathlib import Path
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from clearance import cases, instruments, research, updates

SUPPORT = 'https://example.org/fresh-sessions-help'
NOISE = 'https://example.org/sidebar-noise'
SUPPORT_V1 = (
    'Fresh agent sessions reduced the number of repeated errors in our maintenance experiment. '
    'Limitation: the result may not generalize beyond Python repair tasks.'
)
SUPPORT_V2 = (
    'Fresh agent sessions increased the number of repeated errors in our maintenance experiment. '
    'Limitation: the result may not generalize beyond Python repair tasks.'
)
NOISE_V1 = 'Sidebar promo: unrelated archival newsletter signup form for museum visitors only.'
NOISE_V2 = 'Sidebar promo UPDATED: still unrelated archival newsletter signup form.'
Q = 'Do fresh agent sessions reduce repeated errors?'


def snap(mapping):
    def _snap(url, **kwargs):
        text = mapping.get(url)
        if not text:
            return None
        return {
            'text': text,
            'sha256': cases.digest(text),
            'fetched_at': '2026-09-05T00:00:00Z',
            'cache_hit': True,
        }
    return _snap


def build_case(db, *, change_support: bool, change_noise: bool):
    with patch.object(instruments, 'document_snapshot', side_effect=snap({SUPPORT: SUPPORT_V1, NOISE: NOISE_V1})):
        data = cases.create(Q, sources=[SUPPORT, NOISE], db=db)
    eid = next(e['id'] for e in data['evidence'] if e['url'] == SUPPORT)
    quote = next(e['quote'] for e in data['evidence'] if e['url'] == SUPPORT)
    data = research.assess(
        data['id'], data['version'], statement='Fresh sessions reduce repeated errors.',
        relation='supports', rationale='Primary study measured fewer repeated errors.',
        evidence_id=eid, quote=quote, db=db,
    )
    data = cases.decide(
        data['id'],
        statement='Prefer fresh sessions for maintenance repair tasks.',
        rationale='Supported by the verified quote in the primary study.',
        evidence_ids=[eid], expected_version=data['version'], db=db,
    )
    before = cases.get(data['id'], db=db)
    after_map = {
        SUPPORT: SUPPORT_V2 if change_support else SUPPORT_V1,
        NOISE: NOISE_V2 if change_noise else NOISE_V1,
    }
    with patch.object(instruments, 'document_snapshot', side_effect=snap(after_map)):
        after = cases.refresh(data['id'], live=False, db=db)
    return before, after


def score_pair(before, after):
    ranked = updates.score_case_change(before, after)
    naive = updates.naive_any_change(before, after)
    silent = updates.always_silent(before, after)
    support_id = next(e['id'] for e in before['evidence'] if e['url'] == SUPPORT)
    gold_material = any(
        c.get('evidence_id') == support_id and c['kind'] == 'source_changed'
        for c in (after.get('changes') or cases.changes(before, after))
    )
    return {
        'gold_material': gold_material,
        'ranked_material': ranked['material'],
        'naive_material': naive['material'],
        'silent_material': silent['material'],
        'ranked_top': (ranked['material_effects'][0]['kind'] if ranked['material_effects'] else None),
        'naive_count': naive['material_count'],
        'ranked_count': ranked['material_count'],
        'ranked_true_positive': ranked['material'] and gold_material,
        'ranked_false_positive': ranked['material'] and not gold_material,
        'naive_true_positive': naive['material'] and gold_material,
        'naive_false_positive': naive['material'] and not gold_material,
        'silent_true_positive': silent['material'] and gold_material,
        'silent_false_positive': silent['material'] and not gold_material,
        'ranked_decision_first': (
            ranked['material'] and ranked['material_effects']
            and ranked['material_effects'][0]['kind'] == 'decision_review_required'
        ),
    }


def main():
    fixtures = [
        ('decision_and_noise', True, True),
        ('noise_only', False, True),
        ('no_change', False, False),
        ('decision_only', True, False),
    ]
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, ch_s, ch_n in fixtures:
            db = Path(tmp) / f'{name}.db'
            before, after = build_case(db, change_support=ch_s, change_noise=ch_n)
            row = score_pair(before, after)
            row['fixture'] = name
            rows.append(row)

    ranked_fp = sum(1 for r in rows if r['ranked_false_positive'])
    naive_fp = sum(1 for r in rows if r['naive_false_positive'])
    silent_fp = sum(1 for r in rows if r['silent_false_positive'])
    ranked_tp = sum(1 for r in rows if r['ranked_true_positive'])
    naive_tp = sum(1 for r in rows if r['naive_true_positive'])
    silent_tp = sum(1 for r in rows if r['silent_true_positive'])
    decision_first = sum(1 for r in rows if r['ranked_decision_first'])

    print('UPDATES RANKING BASELINE')
    for r in rows:
        print(
            f"  {r['fixture']}: gold={r['gold_material']} "
            f"ranked={r['ranked_material']}(top={r['ranked_top']},n={r['ranked_count']}) "
            f"naive={r['naive_material']}(n={r['naive_count']}) "
            f"silent={r['silent_material']}"
        )
    print(f'ranked_true_positives={ranked_tp} naive_true_positives={naive_tp} silent_true_positives={silent_tp}')
    print(f'ranked_false_positives={ranked_fp} naive_false_positives={naive_fp} silent_false_positives={silent_fp}')
    print(f'ranked_decision_first_when_material={decision_first}')
    ranked_wins = ranked_fp < naive_fp and ranked_tp >= naive_tp and ranked_tp > silent_tp
    print(f'ranked_wins_vs_naive_and_null={ranked_wins}')
    if silent_tp == 0 and ranked_fp > silent_fp and ranked_tp == 0:
        print('FINDING: always-silent null beats ranked (zero FP, equal zero recall) — product is noise.')
        raise SystemExit(1)
    if not ranked_wins:
        print('FINDING: ranked arm did not beat naive on FP precision at equal recall, or lost recall to null.')
        raise SystemExit(1)
    print('BASELINE OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
