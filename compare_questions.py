"""Ask the same 600 items two different questions. Second run touches no network.

Default second use is NONCOMMERCIAL_REUSE — the pack / pitch claim (247/600).
Pass `broadcast` to reproduce the old nearer-proxy arm (9/600).

  python3 compare_questions.py
  python3 compare_questions.py broadcast
  python3 scripts/eval_second_buyer_shift.py   # both arms + fixture cross-check
"""
import sys
from clearance import corpus, engine
from clearance.gap_report import render as gap
from clearance.shift import render as shift
from clearance.sources import europeana

items = europeana.load_fixture("europeana-broad.json")

_SECOND = {
    "noncommercial_reuse": engine.NONCOMMERCIAL_REUSE,
    "noncommercial": engine.NONCOMMERCIAL_REUSE,
    "broadcast": engine.BROADCAST,
}
second_key = (sys.argv[1] if len(sys.argv) > 1 else "noncommercial_reuse").lower()
if second_key not in _SECOND:
    raise SystemExit(
        f"unknown second use {second_key!r}; expected one of {sorted(_SECOND)}"
    )
second_use = _SECOND[second_key]


def judge_all(use):
    return [engine.judge(subject_id=i["subject_id"], subject_title=i["subject_title"],
                         instrument_uri=i["instrument_uri"], use=use, holder=i["holder"])
            for i in items]


a = judge_all(engine.AI_TRAINING)
b = judge_all(second_use)

con = corpus.connect()
corpus.remember(con, a + b)

if second_use == engine.BROADCAST:
    open("fixtures/gap-report-broadcast.md", "w").write(
        gap(b, library="Europeana · 600 moving-image items", use=engine.BROADCAST))
    out_path = "fixtures/shift-ai-training-vs-broadcast.md"
else:
    open("fixtures/gap-report-600.md", "w").write(
        gap(a, library="Europeana · 600 moving-image items", use=engine.AI_TRAINING))
    out_path = "fixtures/shift-ai-training-vs-noncommercial.md"

report = shift(a, b, library="Europeana · 600 moving-image items")
open(out_path, "w").write(report)
print(report)
print(f"wrote {out_path}")
print(f"corpus now holds {corpus.size(con)} verdicts "
      f"({len(items)} items x 2 questions)")
print(
    "NOTE: for a side-by-side of both second buyers without rewriting fixtures, "
    "run python3 scripts/eval_second_buyer_shift.py"
)
