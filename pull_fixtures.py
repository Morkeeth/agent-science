"""One-shot: pull REAL items from Europeana and REAL terms from each instrument."""
import sys
from clearance import instruments
from clearance.sources import europeana

query = sys.argv[1] if len(sys.argv) > 1 else "film archive"
rows = int(sys.argv[2]) if len(sys.argv) > 2 else 50

items = europeana.search(query, rows)
p = europeana.save_fixture(items, "europeana-film-archive.json")
print(f"{len(items)} real items -> {p}")

uris = sorted({i["instrument_uri"] for i in items if i["instrument_uri"]})
print(f"\n{len(uris)} distinct instruments. Fetching verbatim terms from each:")
for u in uris:
    got = instruments.fetch(u)
    status = "OK  " if got else "FAIL"
    print(f"  [{status}] {u}")
    if got:
        print(f"         \"{got[:110]}…\"")
