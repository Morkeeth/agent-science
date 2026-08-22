"""One production: its factual claims AND its footage, through one engine."""
from check_pitch import CLAIMS
from clearance import engine
from clearance.facts import judge_claim
from clearance.gap_report import mixed
from clearance.sources import europeana

verdicts = [judge_claim(c) for c in CLAIMS]

# a real slice of footage the production wants to use
items = europeana.load_fixture("europeana-broad.json")
# one of each instrument family, so the report shows the range rather than six
# copies of the commonest row
picks, seen = [], set()
for i in items:
    u = i["instrument_uri"] or ""
    for k in ("InC-OW-EU", "CNE", "InC/1.0", "publicdomain/mark", "by-nc-nd", "by/4.0"):
        if k in u and k not in seen:
            seen.add(k); picks.append(i)
verdicts += [engine.judge(subject_id=i["subject_id"], subject_title=i["subject_title"],
                          instrument_uri=i["instrument_uri"], use=engine.AI_TRAINING,
                          holder=i["holder"]) for i in picks]

r = mixed(verdicts, production="'Cleared' — a documentary about rights clearance")
open("fixtures/clearance-report-mixed.md", "w").write(r)
print(r[:r.find("## The evidence")])
