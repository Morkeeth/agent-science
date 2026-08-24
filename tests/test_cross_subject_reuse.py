"""Cross-subject reuse through the refusal log — the moat, proven offline.

Two productions on DIFFERENT subjects share two overlapping claims (one provable, one
proven-unprovable), phrased differently but carrying the same distinctive term. The FIRST
production searches; the SECOND must reuse the log and spend NO Parallel call — and the
proven-unprovable claim must stay refused without re-searching.

We fake ONLY the two network boundaries, exactly as tests/test_search_path.py does:
`search.find_sources` (Parallel) and `instruments.document` (the fetch). The locator is
the real shipping StringLocator (DEFAULT) and the verdict rule (`verify`, independence)
runs for real. We substitute EFFECTS (what the network returns), never the RULE (what
counts as verified). Ground truth is the fake's own call count, not the code's self-report.
"""
from __future__ import annotations

import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_science
from clearance import instruments, search as _search
from clearance.gemini import GeminiLocator  # noqa: F401  (patched below)
from clearance.locate import DEFAULT
from clearance.verdict import GREEN, UNKNOWN

_PRIMARY_URL = "https://www.legislation.gov.uk/ukpga/2024/1/section/3"  # classifies primary
_MUST_FORCE = "came into force on 1 April 2024"
_MUST_STATUTE = "Some Statute establishes the register"
_DOC_STATES_FORCE = (
    "Explanatory notes.\n"
    "The Act came into force on 1 April 2024 across England and Wales.\n"
    "Unrelated boilerplate the locator must ignore.\n"
)


@dataclass
class _Raw:
    text: str
    source_url: str | None
    must_contain: str


# Same distinctive term in each pair, DIFFERENT wording between the two productions —
# so the reuse must key on the term, and the wording difference must be FLAGGED.
_SCRIPTS = {
    "prodA": [
        _Raw("The Act came into force on 1 April 2024.", None, _MUST_FORCE),
        _Raw("Some Statute establishes the register.", None, _MUST_STATUTE),
    ],
    "prodB": [
        _Raw("Commencement: the statute came into force on 1 April 2024, per the notes.",
             None, _MUST_FORCE),
        _Raw("Some Statute establishes the register, the archive says.", None, _MUST_STATUTE),
    ],
}


class _FakeExtractor:
    name = "fake-extractor"

    def __init__(self, model="x"):
        self.model = model

    def extract(self, script):
        return list(_SCRIPTS[script])


class _Net:
    """The faked network boundary, with an honest call counter."""

    def __init__(self):
        self.find_calls = 0

    def find_sources(self, objective, queries, *, live=False, max_results=5, **kw):
        self.find_calls += 1
        # The provable claim's term gets a primary source; the unprovable claim gets none.
        if _MUST_FORCE in (objective + " " + " ".join(str(q) for q in queries)):
            return [_search.Candidate(url=_PRIMARY_URL, title="t", excerpt="e")]
        return []  # SEARCH_FOUND_NOTHING -> honest refusal

    def document(self, url, fetch=False, **kw):
        return _DOC_STATES_FORCE if url == _PRIMARY_URL else None


def _run(net, tmp: Path, subject: str, script_key: str) -> dict:
    saved = (_search.find_sources, instruments.document,
             agent_science.GeminiExtractor, agent_science.GeminiLocator)
    _search.find_sources = net.find_sources
    instruments.document = net.document
    agent_science.GeminiExtractor = _FakeExtractor
    agent_science.GeminiLocator = lambda model="x": DEFAULT  # real string locator
    try:
        return agent_science.clear_script(
            script_key, subject=subject,
            corpus_db=tmp / "corpus.db", log_db=tmp / "refusal_log.db")
    finally:
        (_search.find_sources, instruments.document,
         agent_science.GeminiExtractor, agent_science.GeminiLocator) = saved


def test_second_subject_reuses_the_log_and_spends_no_parallel_call():
    net = _Net()
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)

        a = _run(net, tmp, subject="orphan-works", script_key="prodA")
        # Production 1 is cold: both claims searched, nothing reused.
        assert a["parallel_calls"] == 2, a["parallel_calls"]
        assert a["log_hits"] == 0 and a["corpus_hits"] == 0
        assert net.find_calls == 2, net.find_calls  # ground truth: two real searches
        labels_a = {r["text"]: r["label"] for r in a["rows"]}
        assert labels_a["The Act came into force on 1 April 2024."] == "SOURCED"
        assert labels_a["Some Statute establishes the register."] != "SOURCED"

        before = net.find_calls
        b = _run(net, tmp, subject="dust-bowl", script_key="prodB")

        # THE PROOF: a different subject, both claims overlap by distinctive term.
        # No Parallel call is spent — measured at the fake, not just self-reported.
        assert net.find_calls == before, \
            f"production 2 hit the network {net.find_calls - before} time(s); reuse failed"
        assert b["parallel_calls"] == 0, b["parallel_calls"]
        assert b["log_hits"] == 2, b["log_hits"]
        assert b["corpus_hits"] == 0, "cross-subject reuse must not read as same-subject"

        by_text = {r["text"]: r for r in b["rows"]}

        # 1) The proven claim is reused as SOURCED, carries the citation, and FLAGS that
        #    the evidence was established under a different wording.
        force = by_text["Commencement: the statute came into force on 1 April 2024, per the notes."]
        assert force["label"] == "SOURCED"
        assert force["citation_url"] == _PRIMARY_URL
        assert force.get("cross_subject") is True and force["probe"] == "log_hit"
        assert force.get("reused_from"), "different wording must be flagged, not silently served"

        # 2) The proven-UNPROVABLE claim stays refused, with NO re-search.
        statute = by_text["Some Statute establishes the register, the archive says."]
        assert statute["label"] != "SOURCED"
        assert statute["engine_verdict"] == UNKNOWN
        assert statute.get("cross_subject") is True


def test_not_gameable_reuse_carries_the_original_verdict_both_poles():
    """A log that returned GREEN (or UNKNOWN) for everything would pass a one-pole test.
    The same reuse path must carry a GREEN for the provable claim and an UNKNOWN for the
    unprovable one, from ONE production-2 run."""
    net = _Net()
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        _run(net, tmp, subject="s1", script_key="prodA")
        b = _run(net, tmp, subject="s2", script_key="prodB")
        verdicts = sorted(r["engine_verdict"] for r in b["rows"])
        assert verdicts == sorted([GREEN, UNKNOWN]), verdicts


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    bad = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as e:
            bad += 1
            print(f"FAIL  {fn.__name__}: {e}")
    print(f"\n{len(fns) - bad}/{len(fns)} passed")
    sys.exit(1 if bad else 0)
