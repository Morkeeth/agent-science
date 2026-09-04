"""Exact supported claims reuse across subjects; bounded search failures retry.

Only network and extraction effects are substituted. The verifier and verdict
constructor run, and an external counter measures actual discovery attempts.
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


# Identical assertions in both productions; unsupported claims still retry.
_SCRIPTS = {
    "prodA": [
        _Raw("The Act came into force on 1 April 2024.", None, _MUST_FORCE),
        _Raw("Some Statute establishes the register.", None, _MUST_STATUTE),
    ],
    "prodB": [
        _Raw("The Act came into force on 1 April 2024.",
             None, _MUST_FORCE),
        _Raw("Some Statute establishes the register.", None, _MUST_STATUTE),
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


def test_second_subject_reuses_support_and_retries_unsettled_claim():
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

        # The supported assertion reuses; the unresolved assertion searches again.
        assert net.find_calls == before + 1, \
            f"production 2 hit the network {net.find_calls - before} time(s); reuse failed"
        assert b["parallel_calls"] == 1, b["parallel_calls"]
        assert b["log_hits"] == 1, b["log_hits"]
        assert b["corpus_hits"] == 0, "cross-subject reuse must not read as same-subject"

        by_text = {r["text"]: r for r in b["rows"]}

        # The supported assertion retains its citation and exact identity.
        force = by_text["The Act came into force on 1 April 2024."]
        assert force["label"] == "SOURCED"
        assert force["citation_url"] == _PRIMARY_URL
        assert force.get("cross_subject") is True and force["probe"] == "log_hit"
        assert not force.get("reused_from"), "identical wording must retain its identity"

        # The bounded failure is searched again; this network still has no source.
        statute = by_text["Some Statute establishes the register."]
        assert statute["label"] != "SOURCED"
        assert statute["engine_verdict"] == UNKNOWN
        assert not statute.get("cross_subject")


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
