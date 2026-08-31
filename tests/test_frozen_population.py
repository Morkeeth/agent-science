"""The measurement population must not be writable by the product that is measured.

THE DEFECT THESE PIN. `clearance/ingest.py::append_markdown` wrote dated claim files into
`research-corpus/` — the same directory `scripts/eval_citation_conflict.py` and
`scripts/eval_semantic_guard.py` replay as their measurement population. So USING the
product moved its own published denominator: the night of 08-30 read n=313 and then
n=314 an hour later, and from a clean checkout the same command reads 312, because two
of "the 314" were untracked files the product had written to itself.

RUN RED FIRST. Against the 08-31 05:30 layout (`_CORPUS = _ROOT / "research-corpus"`),
`t_using_the_product_does_not_move_its_own_denominator` fails:

    FAIL  test_using_the_product_does_not_move_its_own_denominator:
          one append_markdown() call changed the frozen population: 312 -> 313 claims
          (extra: ['2026-08-31-t-frozen-population-probe.md'])

Fixed by pointing ingest at `research-inbox/`, which no published number reads.

The instruction-following writers count too: an agent that reads AGENTS.md or the MCP
tool description and appends research to `research-corpus/` recontaminates the frozen
population tomorrow morning without touching a line of Python. So the prose is pinned
here as well as the code.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import ingest, population as P  # noqa: E402
import clear_corpus as C  # noqa: E402


def test_the_frozen_population_matches_its_manifest():
    v = P.verify()
    assert v["ok"], (f"the population every published number is computed over has "
                     f"drifted: missing={v['missing']} extra={v['extra']} "
                     f"changed={v['changed']}")
    assert v["n_files"] > 0 and v["claims"] > 0, "an empty population is not a measurement"


def test_the_manifest_denominator_is_the_one_the_parser_finds():
    """The manifest carries the number, so a silent parser change shows up in the diff."""
    n = len(C.parse_corpus(P.frozen_dir()))
    assert n == P.manifest()["claims"], (
        f"manifest says {P.manifest()['claims']} claims, parser finds {n}")


def test_the_population_is_committed_so_a_clean_checkout_reproduces():
    import subprocess
    tracked = {Path(p).name for p in subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "research-corpus/*.md"],
        capture_output=True, text=True).stdout.split() if p.endswith(".md")}
    on_disk = {p.name for p in P.FROZEN.glob("*.md")}
    assert on_disk == tracked, (
        f"the eval population is not what a clean checkout has — untracked here: "
        f"{sorted(on_disk - tracked)}; tracked but absent: {sorted(tracked - on_disk)}")


def test_ingest_does_not_write_into_the_measurement_population():
    """Structural: the sink and the population must be different, non-nested trees."""
    sink = ingest._INBOX.resolve()
    frozen = P.FROZEN.resolve()
    assert sink != frozen, f"ingest writes into the measured population: {sink}"
    assert frozen not in sink.parents, f"ingest sink {sink} sits inside {frozen}"
    assert sink not in frozen.parents, f"the population {frozen} sits inside {sink}"


def test_using_the_product_does_not_move_its_own_denominator():
    """Behavioural, and the one that goes RED: ingest a claim, re-count the population.

    This deliberately calls the real writer against the real tree — a structural check
    on a constant would pass the day someone adds a second write path.
    """
    before = P.verify()
    written = None
    try:
        written = ingest.append_markdown(
            "[CLAIM] a probe claim written by the product itself\n"
            "[URL] https://example.invalid/probe\n", slug="t-frozen-population-probe")
        after = P.verify()
        n_after = len(C.parse_corpus(str(P.FROZEN)))
        assert after["ok"], (
            f"one append_markdown() call changed the frozen population: "
            f"{before['claims']} -> {n_after} claims (extra: {after['extra']})")
    finally:
        if written is not None and Path(written).is_file():
            Path(written).unlink()


def test_no_published_number_is_computed_over_the_live_sink():
    """No eval, receipt or surface may point its denominator at the ingest sink."""
    sink = ingest._INBOX.name
    offenders = []
    for d in ("scripts", "."):
        for py in sorted((ROOT / d).glob("*.py")):
            body = py.read_text(encoding="utf-8", errors="replace")
            if ("verify_corpus" in body or "parse_corpus" in body) and \
                    f'"{sink}"' in body and py.name != "freeze_population.py":
                offenders.append(py.name)
    assert not offenders, (
        f"these compute a population count over the live ingest sink {sink!r}: {offenders}")


def test_the_evals_resolve_their_population_through_the_frozen_gate():
    """Not by a bare relative string — which resolves against the caller's cwd and, for a
    directory that is not there, returns zero claims without a word."""
    for name in ("eval_citation_conflict.py", "eval_semantic_guard.py"):
        body = (ROOT / "scripts" / name).read_text()
        assert "population" in body and "frozen_dir()" in body, \
            f"{name} does not resolve its population through clearance.population"
        assert 'verify_corpus("research-corpus"' not in body, \
            f"{name} still replays a bare relative directory"


def test_the_written_instructions_point_at_the_sink_not_the_population():
    """An agent recontaminates a frozen corpus by following prose, not by editing code."""
    frozen, sink = P.FROZEN.name, ingest._INBOX.name
    for doc, needle in (("AGENTS.md", "append"),
                        ("clearance/mcp_server.py", "append to")):
        body = (ROOT / doc).read_text()
        for line in body.splitlines():
            if needle in line.lower() and frozen in line:
                raise AssertionError(
                    f"{doc} tells a writer to append to the FROZEN population: "
                    f"{line.strip()[:120]}  (the sink is {sink}/)")


def test_the_receipt_every_surface_reads_from_is_committed():
    """A skip is not a pass, and a deleted receipt would disarm four controls silently.

    Found while proving the strip control red: with `docs/EVAL-*.json` absent,
    `_measurement_html()` returns "" and every assertion over it passes vacuously. The
    receipt is committed, so the skip branch can only fire on a broken tree — say so
    here rather than let four green lines mean nothing.
    """
    import subprocess
    import ask_registry as A
    tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch",
                              str(A.EVAL_PATH.relative_to(ROOT))],
                             capture_output=True, text=True)
    assert A.EVAL_PATH.is_file(), f"{A.EVAL_PATH.name} is missing — surface controls skip"
    assert tracked.returncode == 0, \
        f"{A.EVAL_PATH.name} is not committed; a clean checkout would skip every " \
        "control that reads the measurement strip"


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
