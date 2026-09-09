#!/usr/bin/env python3
"""Compound economics — exact-claim shipping vs naive paraphrase baseline.

The old compound-mini-B paraphrased A's facts. Under exact-claim integrity that
exhibit fails (measured 2026-09-08: A=2 B=3 corpus_hits=0). A naive two-hour
baseline that reuses by must_contain/term would still "pass". This script runs
both arms on the same offline fakes so the delta is visible.

Arms:
  Baseline — soft: if must_contain matched a prior GREEN A claim, count corpus_hit
  Shipping — agent_science.clear_script exact assertion recall (production path)

Run: python3 scripts/eval_compound_baseline.py
"""
from __future__ import annotations

import importlib
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import agent_science
from clearance import instruments, search as _search
from clearance.locate import DEFAULT
from clearance.verdict import GREEN
from eval_stats import format_ci  # noqa: F401

cer = importlib.import_module("compound_exhibit_receipt")

SUBJECT = cer.SUBJECT
_FakeExtractor = cer._FakeExtractor
_Net = cer._Net
_Raw = cer._Raw
_fake_document = cer._fake_document
OFFLINE_A = cer.OFFLINE_A

_PARAPHRASE_B = [
    _Raw("Europe's answer was Directive 2012/28/EU — known as the Orphan Works Directive —",
         None, "Directive 2012/28/EU"),
    _Raw("and the deadline for national transposition was 29 October 2014.",
         None, "29 October 2014"),
    _Raw("The British Library has estimated that forty percent of its copyrighted collection is orphaned.",
         None, "forty percent"),
]

_EXACT_B = [
    _Raw("In 2012 the European Union passed Directive 2012/28/EU, the Orphan Works Directive.",
         None, "Directive 2012/28/EU"),
    _Raw("Member states had until 29 October 2014 to bring it into national law.",
         None, "29 October 2014"),
    _Raw("The British Library has estimated that forty percent of its copyrighted collection is orphaned.",
         None, "forty percent"),
]


@dataclass
class ArmResult:
    name: str
    parallel_a: int
    parallel_b: int
    corpus_hits_b: int

    @property
    def compounds(self) -> bool:
        return (
            self.parallel_a > 0
            and self.parallel_b < self.parallel_a
            and self.corpus_hits_b >= 1
        )


def _patch_net():
    net = _Net()
    saved = (
        _search.find_sources,
        instruments.document,
        agent_science.GeminiExtractor,
        agent_science.GeminiLocator,
    )
    _search.find_sources = net.find_sources
    instruments.document = _fake_document
    agent_science.GeminiLocator = lambda model="x": DEFAULT
    return net, saved


def _restore(saved):
    (
        _search.find_sources,
        instruments.document,
        agent_science.GeminiExtractor,
        agent_science.GeminiLocator,
    ) = saved


def _run_shipping(claims_b: list) -> ArmResult:
    _net, saved = _patch_net()
    prior = dict(cer._OFFLINE_CLAIMS)
    try:
        cer._OFFLINE_CLAIMS = {"A": prior["A"], "B": list(claims_b)}
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / "c.db"
            log_db = Path(d) / "r.db"
            agent_science.GeminiExtractor = (
                lambda model="x", k="A": _FakeExtractor(model, script_key=k)
            )
            a = agent_science.clear_script(
                OFFLINE_A.read_text(), subject=SUBJECT, corpus_db=db, log_db=log_db
            )
            agent_science.GeminiExtractor = (
                lambda model="x", k="B": _FakeExtractor(model, script_key=k)
            )
            b = agent_science.clear_script(
                "\n".join(c.text for c in claims_b),
                subject=SUBJECT,
                corpus_db=db,
                log_db=log_db,
            )
            return ArmResult(
                "shipping",
                a["parallel_calls"],
                b["parallel_calls"],
                b["corpus_hits"],
            )
    finally:
        cer._OFFLINE_CLAIMS = prior
        _restore(saved)


def _run_soft_baseline(claims_b: list) -> ArmResult:
    """Naive term reuse after a real Run A."""
    _net, saved = _patch_net()
    prior = dict(cer._OFFLINE_CLAIMS)
    try:
        cer._OFFLINE_CLAIMS = {"A": prior["A"], "B": list(claims_b)}
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / "c.db"
            log_db = Path(d) / "r.db"
            agent_science.GeminiExtractor = (
                lambda model="x", k="A": _FakeExtractor(model, script_key=k)
            )
            a = agent_science.clear_script(
                OFFLINE_A.read_text(), subject=SUBJECT, corpus_db=db, log_db=log_db
            )
            soft_terms = {raw.must_contain.lower() for raw in prior["A"]}
            hits = sum(1 for raw in claims_b if raw.must_contain.lower() in soft_terms)
            parallel_b = len(claims_b) - hits
            return ArmResult(
                "baseline-soft-term",
                a["parallel_calls"],
                parallel_b,
                hits,
            )
    finally:
        cer._OFFLINE_CLAIMS = prior
        _restore(saved)


def main() -> int:
    print("COMPOUND BASELINE EVAL — paraphrase subject, exact vs soft term\n")
    print("Scenario: historical paraphrase B (different wording, same must_contain)\n")

    soft = _run_soft_baseline(_PARAPHRASE_B)
    ship_para = _run_shipping(_PARAPHRASE_B)
    ship_exact = _run_shipping(_EXACT_B)

    def line(r: ArmResult) -> str:
        flag = "PASS" if r.compounds else "FAIL"
        return (
            f"{r.name:<22} A={r.parallel_a} B={r.parallel_b} "
            f"corpus_hits={r.corpus_hits_b}  compound={flag}"
        )

    print(line(soft))
    print(line(ship_para))
    print(line(ship_exact))
    print()

    # Gold on paraphrase B: must NOT compound under exact integrity.
    gold_para_compounds = False
    b_ok = int(soft.compounds == gold_para_compounds)
    s_ok = int(ship_para.compounds == gold_para_compounds)
    print(f"On paraphrase B, gold compounds={gold_para_compounds}")
    print(f"Soft baseline correct:  {b_ok}/1")
    print(f"Shipping correct:       {s_ok}/1")
    print(
        f"Exact-claim B (control) compounds={ship_exact.compounds} "
        f"(A={ship_exact.parallel_a}→B={ship_exact.parallel_b}, "
        f"hits={ship_exact.corpus_hits_b})"
    )
    if soft.compounds and not ship_para.compounds:
        print(
            "FINDING: soft-term baseline false-PASS on paraphrase; "
            "shipping refuses silent reuse — integrity earns its keep."
        )
    if not ship_exact.compounds:
        print("FINDING: exact-claim control failed — compound exhibit broken.")
        return 3
    return 0 if s_ok == 1 else 3


if __name__ == "__main__":
    raise SystemExit(main())
