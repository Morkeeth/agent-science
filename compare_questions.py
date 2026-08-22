"""Ask the same 600 items two different questions. Second run touches no network."""
from clearance import corpus, engine
from clearance.gap_report import render as gap
from clearance.shift import render as shift
from clearance.sources import europeana

items = europeana.load_fixture("europeana-broad.json")


def judge_all(use):
    return [engine.judge(subject_id=i["subject_id"], subject_title=i["subject_title"],
                         instrument_uri=i["instrument_uri"], use=use, holder=i["holder"])
            for i in items]


a = judge_all(engine.AI_TRAINING)
b = judge_all(engine.BROADCAST)

con = corpus.connect()
corpus.remember(con, a + b)

open("fixtures/gap-report-broadcast.md", "w").write(
    gap(b, library="Europeana · 600 moving-image items", use=engine.BROADCAST))
report = shift(a, b, library="Europeana · 600 moving-image items")
open("fixtures/shift-ai-training-vs-broadcast.md", "w").write(report)
print(report)
print(f"corpus now holds {corpus.size(con)} verdicts "
      f"({len(items)} items x 2 questions)")
