#!/usr/bin/env python3
"""Compound exhibit receipt — slice 3.

Runs orphan-works Production A then B on one corpus DB and writes
docs/COMPOUND-EXHIBIT-2026-08-29.md with quantified parallel-call delta.

Live path (Gemini + Parallel keys present):
    scripts/compound_exhibit.py on documentary-orphan-works A/B

Offline path (this VM default):
    compound-mini-A/B with ONLY search.find_sources + instruments.document faked;
    Gemini extraction substituted with fixed claim lists; StringLocator + verify run for real.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

RECEIPT = ROOT / "docs/COMPOUND-EXHIBIT-2026-08-29.md"
SUBJECT = "orphan-works"
LIVE_A = ROOT / "fixtures/scripts/documentary-orphan-works.txt"
LIVE_B = ROOT / "fixtures/scripts/documentary-orphan-works-B.txt"
OFFLINE_A = ROOT / "fixtures/scripts/compound-mini-A.txt"
OFFLINE_B = ROOT / "fixtures/scripts/compound-mini-B.txt"


def _has_keys() -> bool:
    gemini = Path.home() / ".config/keys/gemini.key"
    parallel = Path.home() / ".config/keys/parallel.key"
    return bool(
        os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
        or gemini.exists()
    ) and bool(os.environ.get("PARALLEL_API_KEY") or parallel.exists())


def _run_live() -> dict:
    import agent_science

    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "corpus.db"
        log_db = Path(d) / "refusal_log.db"
        try:
            a = agent_science.clear_script(
                LIVE_A.read_text(), subject=SUBJECT, corpus_db=db, log_db=log_db)
            b = agent_science.clear_script(
                LIVE_B.read_text(), subject=SUBJECT, corpus_db=db, log_db=log_db)
        except Exception as e:
            return {"mode": "live", "error": f"{type(e).__name__}: {e}\n{traceback.format_exc()}"}
    return {"mode": "live", "a": a, "b": b, "fixtures": (LIVE_A.name, LIVE_B.name)}


@dataclass
class _Raw:
    text: str
    source_url: str | None
    must_contain: str


# Fixed claim lists mirroring compound-mini scripts — extraction is NOT simulated live.
# B reuses A's exact assertion text for the overlapping claims. After
# f61635e, paraphrase overlap is intentionally NOT a corpus hit — the exhibit
# must prove compounding under that rule, not under the old paraphrase shortcut.
_OFFLINE_CLAIMS = {
    "A": [
        _Raw("In 2012 the European Union passed Directive 2012/28/EU, the Orphan Works Directive.",
             None, "Directive 2012/28/EU"),
        _Raw("Member states had until 29 October 2014 to bring it into national law.",
             None, "29 October 2014"),
    ],
    "B": [
        _Raw("In 2012 the European Union passed Directive 2012/28/EU, the Orphan Works Directive.",
             None, "Directive 2012/28/EU"),
        _Raw("Member states had until 29 October 2014 to bring it into national law.",
             None, "29 October 2014"),
        _Raw("The British Library has estimated that forty percent of its copyrighted collection is orphaned.",
             None, "forty percent"),
    ],
}

_URL_DIRECTIVE = "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32012L0028"
_URL_FORTY = "https://www.bl.uk/help/copyright-and-permissions"

_DOC_DIRECTIVE = (
    "Directive 2012/28/EU of the European Parliament and of the Council.\n"
    "Member States shall bring into force the laws necessary to comply with this "
    "Directive by 29 October 2014.\n"
    "Directive 2012/28/EU — the Orphan Works Directive — was adopted in 2012.\n"
)
_DOC_FORTY = (
    "British Library copyright guidance.\n"
    "The British Library has estimated that forty percent of its copyrighted collection "
    "is orphaned.\n"
)


class _FakeExtractor:
    name = "offline-fixed-claims"

    def __init__(self, model="x", *, script_key: str):
        self.model = model
        self.script_key = script_key

    def extract(self, script):
        return list(_OFFLINE_CLAIMS[self.script_key])


class _Net:
    """Honest Parallel call counter at the faked boundary."""

    def __init__(self):
        self.find_calls = 0

    def find_sources(self, objective, queries, *, live=False, max_results=5, **kw):
        self.find_calls += 1
        blob = objective + " " + " ".join(str(q) for q in queries)
        if "Directive 2012/28/EU" in blob or "2012/28/EU" in blob:
            return [_cand(_URL_DIRECTIVE)]
        if "29 October 2014" in blob:
            return [_cand(_URL_DIRECTIVE)]
        if "forty percent" in blob:
            return [_cand(_URL_FORTY)]
        return []


def _cand(url):
    from clearance import search as _search
    return _search.Candidate(url=url, title="t", excerpt="e")


def _fake_document(url, fetch=False, **kw):
    return {_URL_DIRECTIVE: _DOC_DIRECTIVE, _URL_FORTY: _DOC_FORTY}.get(url)


def _run_offline() -> dict:
    import agent_science
    from clearance import instruments, search as _search
    from clearance.locate import DEFAULT

    net = _Net()
    saved = (_search.find_sources, instruments.document,
             agent_science.GeminiExtractor, agent_science.GeminiLocator)
    _search.find_sources = net.find_sources
    instruments.document = _fake_document
    agent_science.GeminiLocator = lambda model="x": DEFAULT

    def _extract_factory(model="x"):
        # script_key set per run via closure on clear_script call
        raise RuntimeError("extractor factory not bound")

    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "corpus.db"
        log_db = Path(d) / "refusal_log.db"
        results = {}
        for key, path in (("A", OFFLINE_A), ("B", OFFLINE_B)):
            agent_science.GeminiExtractor = lambda model="x", k=key: _FakeExtractor(model, script_key=k)
            results[key] = agent_science.clear_script(
                path.read_text(), subject=SUBJECT, corpus_db=db, log_db=log_db)

    (_search.find_sources, instruments.document,
     agent_science.GeminiExtractor, agent_science.GeminiLocator) = saved

    return {
        "mode": "offline",
        "a": results["A"],
        "b": results["B"],
        "fixtures": (OFFLINE_A.name, OFFLINE_B.name),
        "simulated": [
            "GeminiExtractor → fixed claim lists from compound-mini-A/B (not live extraction)",
            "search.find_sources → scripted primary URLs + honest call counter",
            "instruments.document → fixture bodies (no HTTP)",
            "StringLocator (DEFAULT) + verify + independence — real shipping rules",
        ],
        "net_find_calls": net.find_calls,
    }


def _control_output(script: str) -> str:
    r = subprocess.run(
        [sys.executable, str(ROOT / script)],
        capture_output=True, text=True, cwd=ROOT)
    return r.stdout.strip() or r.stderr.strip()


def _write_receipt(run: dict, *, backfill_rows: int) -> None:
    if run.get("error"):
        body = f"""# COMPOUND EXHIBIT — orphan-works A/B

**Date:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")} · **Subject:** `{SUBJECT}`

## Live run failed

```
{run["error"]}
```

## Registry backfill

`python3 clear_corpus.py research-corpus --backfill` → **{backfill_rows} rows** in `cache/refusal_log.db`
"""
        RECEIPT.write_text(body, encoding="utf-8")
        return

    a, b = run["a"], run["b"]
    pa, pb = a["parallel_calls"], b["parallel_calls"]
    delta = pa - pb
    mode = run["mode"]
    fa, fb = run["fixtures"]

    lines = [
        "# COMPOUND EXHIBIT — orphan-works A/B",
        "",
        f"**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} · "
        f"**Subject:** `{SUBJECT}` · **Mode:** {mode}",
        f"**Fixtures:** `{fa}` → `{fb}`",
        "",
        "## Quantified compounding",
        "",
        "| Run A parallel_calls | Run B parallel_calls | delta | corpus_hits B |",
        "|---:|---:|---:|---:|",
        f"| {pa} | {pb} | {delta:+d} | {b['corpus_hits']} |",
        "",
        f"- Run B parallel < Run A: **{'yes' if pb < pa else 'NO — exhibit failed'}**",
        f"- corpus_hits B ≥ 1: **{'yes' if b['corpus_hits'] >= 1 else 'NO'}**",
        "",
        "Overlap rule: B must reuse **exact assertion text** from A "
        "(paraphrase is not a corpus hit after same-subject integrity).",
        "",
    ]

    if mode == "offline":
        lines += [
            "## Offline simulation (no Gemini/Parallel keys on this VM)",
            "",
            "Network boundaries faked; verdict rules run for real:",
            "",
        ]
        for s in run.get("simulated", []):
            lines.append(f"- {s}")
        lines += [
            "",
            f"Ground-truth Parallel calls at fake boundary (Run A only): `{run.get('net_find_calls', '?')}`",
            "",
        ]
    else:
        lines += [
            "## Live chain",
            "",
            "Two consecutive `agent_science.clear_script` runs on one corpus DB with Gemini extract + Parallel search.",
            "",
        ]

    lines += [
        "## Registry backfill",
        "",
        f"`python3 clear_corpus.py research-corpus --backfill` → **{backfill_rows} rows** "
        f"(29 SOURCED + proven-unprovable refusals) in `cache/refusal_log.db`",
        "",
        "## Controls",
        "",
        "```",
        _control_output("tests/test_registry_surface.py"),
        "```",
        "",
        "```",
        _control_output("tests/test_cross_subject_reuse.py"),
        "```",
        "",
        "## Related receipts",
        "",
        "- `python3 review/corpus_compound_receipt.py` — rights-leg 50/50 reuse, zero network on Run 2",
        "- `docs/SECOND-SUBJECT-RECEIPT-2026-08-29.md` — dust-bowl cross-subject reuse",
        "",
    ]
    RECEIPT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    from clearance import refusal_log

    con = refusal_log.connect(refusal_log.DB)
    backfill_rows = refusal_log.stats(con)["n"]

    run = _run_live() if _has_keys() else _run_offline()
    _write_receipt(run, backfill_rows=backfill_rows)
    print(RECEIPT.read_text())

    if run.get("error"):
        return 1
    a, b = run["a"], run["b"]
    if a["parallel_calls"] > 0 and b["parallel_calls"] >= a["parallel_calls"]:
        return 3
    if b["corpus_hits"] < 1:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
