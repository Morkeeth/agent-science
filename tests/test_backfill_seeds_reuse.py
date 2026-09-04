"""Backfill permits exact supported reuse; unresolved claims remain retryable.

Network effects are substituted; the shipping verifier and verdict rules run.
"""
from __future__ import annotations

import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import agent_science
import clear_corpus as cc
from clearance import instruments, refusal_log, search as _search
from clearance.locate import DEFAULT
from clearance.verdict import GREEN, UNKNOWN, SOURCE_SILENT

# --- The fixture corpus the back-fill reads. One provable claim, one proven-unprovable. -
_URL_GREEN = "https://www.legislation.gov.uk/ukpga/2024/1/section/3"
_URL_SILENT = "https://example.gov/registry-overview"

# No trailing period: _must_contain keeps it when the claim has no split char, and the
# term must be a substring the DOC carries verbatim.
_CLAIM_GREEN = "The Act came into force on 1 April 2024"
_CLAIM_SILENT = "The registry holds two million titles"

_DOC_GREEN = (
    "Explanatory notes to the Act.\n"
    "The Act came into force on 1 April 2024 across England and Wales.\n"
    "Unrelated boilerplate the locator must ignore.\n"
)
_DOC_SILENT = (
    "This overview page describes the service and mentions nothing about how many "
    "titles the registry holds; it is genuinely silent on the figure.\n"
)

# The term the back-fill keys on — derived exactly as the product derives it, never
# hardcoded, so the test stays self-consistent with clear_corpus._must_contain.
_TERM_GREEN = cc._must_contain(_CLAIM_GREEN)
_TERM_SILENT = cc._must_contain(_CLAIM_SILENT)


def _write_corpus(d: Path) -> str:
    (d / "fixture.md").write_text(
        f"[CLAIM] {_CLAIM_GREEN}\n[URL] {_URL_GREEN}\n"
        f"[CLAIM] {_CLAIM_SILENT}\n[URL] {_URL_SILENT}\n",
        encoding="utf-8")
    return str(d)


def _fake_fetch(url, fetch=False, **kw):
    return {_URL_GREEN: _DOC_GREEN, _URL_SILENT: _DOC_SILENT}.get(url)


# The new production asks the exact backfilled assertions.
@dataclass
class _Raw:
    text: str
    source_url: str | None
    must_contain: str


# Only the exact supported assertion can skip discovery.
_PROD = [
    _Raw(_CLAIM_GREEN,
         None, _TERM_GREEN),
    _Raw(_CLAIM_SILENT,
         None, _TERM_SILENT),
]


class _FakeExtractor:
    name = "fake-extractor"

    def __init__(self, model="x"):
        self.model = model

    def extract(self, script):
        return list(_PROD)


class _Net:
    """The faked network boundary, with an honest call counter."""

    def __init__(self):
        self.find_calls = 0

    def find_sources(self, objective, queries, *, live=False, max_results=5, **kw):
        self.find_calls += 1
        return []  # a cold run searches and (here) comes up empty — the point is the CALL

    def document(self, url, fetch=False, **kw):
        return _fake_fetch(url, fetch=fetch)


def _run_production(net, tmp: Path, *, subject: str, corpus_db, log_db) -> dict:
    saved = (_search.find_sources, instruments.document,
             agent_science.GeminiExtractor, agent_science.GeminiLocator)
    _search.find_sources = net.find_sources
    instruments.document = net.document
    agent_science.GeminiExtractor = _FakeExtractor
    agent_science.GeminiLocator = lambda model="x": DEFAULT  # real string locator
    try:
        return agent_science.clear_script(
            "prod", subject=subject, corpus_db=corpus_db, log_db=log_db)
    finally:
        (_search.find_sources, instruments.document,
         agent_science.GeminiExtractor, agent_science.GeminiLocator) = saved


def _backfill(corpus_dir, log_db) -> dict:
    saved = instruments.document
    instruments.document = _fake_fetch
    try:
        return cc.backfill_log(corpus_dir, log_db=log_db, fetch=False)
    finally:
        instruments.document = saved


def test_backfill_writes_the_expected_rows_and_is_idempotent():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        corpus_dir = _write_corpus(tmp)
        log_db = tmp / "refusal_log.db"

        res = _backfill(corpus_dir, log_db)
        con = refusal_log.connect(log_db)
        n = refusal_log.stats(con)["n"]
        assert n == 2, f"expected 2 seeded rows (1 SOURCED + 1 proven-unprovable), got {n}"
        assert res["seeded_green"] == 1 and res["seeded_unsourced"] == 1, res

        # The GREEN row is replayable: it carries the citation and a quoted passage, so
        # the log-hit branch can rebuild a real Verdict without raising.
        g = refusal_log.lookup(con, term=_TERM_GREEN, assertion=_CLAIM_GREEN)
        assert g["verdict"] == GREEN and g["citation_url"] == _URL_GREEN
        assert (g["quoted_terms"] or "").strip(), "a GREEN row with no quote cannot replay"
        # The proven-unprovable row persists as UNKNOWN/source_does_not_state_it.
        s = refusal_log.lookup(con, term=_TERM_SILENT, assertion=_CLAIM_SILENT)
        assert s["verdict"] == UNKNOWN and s["cause"] == SOURCE_SILENT

        # Repeating backfill retains one current row per assertion, plus history.
        _backfill(corpus_dir, log_db)
        assert refusal_log.stats(refusal_log.connect(log_db))["n"] == 2, \
            "a second back-fill duplicated rows"


def test_new_subject_reuses_backfilled_support_but_retries_unknown():
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        corpus_dir = _write_corpus(tmp)

        # (CONTROL — proves the test is not vacuous.) An EMPTY log: the new production
        # cannot reuse anything, so it SEARCHES. This is the fail-without pole.
        cold_net = _Net()
        cold = _run_production(cold_net, tmp, subject="cold",
                               corpus_db=tmp / "cold_corpus.db",
                               log_db=tmp / "cold_log.db")
        assert cold_net.find_calls >= 1, "empty log must fall through to a real search"
        assert cold["parallel_calls"] >= 1 and cold["log_hits"] == 0, cold

        # SEED the log from the proven corpus.
        _backfill(corpus_dir, tmp / "seed_log.db")

        # A fresh subject reuses the exact supported claim and retries the unknown.
        # The network boundary independently counts that one discovery attempt.
        warm_net = _Net()
        warm = _run_production(warm_net, tmp, subject="a-different-subject",
                               corpus_db=tmp / "warm_corpus.db",
                               log_db=tmp / "seed_log.db")
        assert warm_net.find_calls == 1, \
            f"production hit the network {warm_net.find_calls} time(s); reuse failed"
        assert warm["parallel_calls"] == 1, warm["parallel_calls"]
        assert warm["log_hits"] == 1, warm["log_hits"]
        assert warm["corpus_hits"] == 0, "a back-filled reuse must not read as same-subject"

        by_text = {r["text"]: r for r in warm["rows"]}

        # The supported claim preserves its exact wording and original citation.
        force = by_text[_CLAIM_GREEN]
        assert force["label"] == "SOURCED", force
        assert force["citation_url"] == _URL_GREEN
        assert force.get("cross_subject") is True and force["probe"] == "log_hit"
        assert not force.get("reused_from")

        # The unresolved claim is searched again; this network still has no source.
        silent = by_text[_CLAIM_SILENT]
        assert silent["label"] != "SOURCED"
        assert silent["engine_verdict"] == UNKNOWN
        assert not silent.get("cross_subject")


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
