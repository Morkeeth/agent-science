"""Judge a real library and print the gap report."""
import sys
from clearance import corpus, engine
from clearance.gap_report import render
from clearance.sources import europeana

use = sys.argv[1] if len(sys.argv) > 1 else engine.AI_TRAINING
items = europeana.load_fixture("europeana-film-archive.json")

con = corpus.connect()
before = corpus.size(con)

verdicts, reused = [], 0
for it in items:
    hit = corpus.recall(con, it["subject_id"], use)
    if hit:
        reused += 1
        verdicts.append(hit)
        continue
    verdicts.append(engine.judge(
        subject_id=it["subject_id"], subject_title=it["subject_title"],
        instrument_uri=it["instrument_uri"], use=use, holder=it["holder"],
    ))
corpus.remember(con, verdicts)

print(render(verdicts, library="Europeana · query 'film archive'", use=use))
print(f"---\ncorpus: {before} -> {corpus.size(con)} verdicts  |  "
      f"reused from memory this run: {reused}/{len(items)}")
