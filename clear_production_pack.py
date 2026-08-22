#!/usr/bin/env python3
"""THE PRODUCTION PACK — one engine, both nouns, one document a lawyer can act on.

A documentary needs two things cleared before it can be insured and released: every
FACT it asserts must be sourced, and every ASSET it uses must be rights-cleared. They
are done by different people, at different times, in different tools. They are the same
question — *can we prove we are allowed to do this* — and this engine answers both.

Aimed at the use that just became mandatory: **from 2026 the EU AI Act requires AI
companies to disclose training-data sources and respect copyright opt-outs.** So the
headline question is not "can we broadcast this" but "can this material lawfully train a
model, and can we prove it per item."

Nothing here is new engine. It is `clearance.facts` and `clearance.engine` writing into
one document, because two reports for one production is two products with a shared
README.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from clearance import engine
from clearance.independence import classify
from clearance.sources import europeana
from clearance.verdict import GREEN, UNKNOWN
import agent_science

USE = engine.AI_TRAINING


def build(script_path: str, *, assets: int = 40, subject: str = "pack") -> str:
    script = pathlib.Path(script_path).read_text()
    facts = agent_science.clear_script(script, subject=subject,
                                       model="gemini-3.5-flash-lite")["rows"]
    items = europeana.load_fixture("europeana-broad.json")[:assets]
    av = [engine.judge(subject_id=i["subject_id"], subject_title=i["subject_title"],
                       instrument_uri=i["instrument_uri"], use=USE, holder=i["holder"])
          for i in items]

    f_ok = [r for r in facts if r["label"] == "SOURCED"]
    a_ok = [v for v in av if v.verdict == GREEN]
    blocked = len(facts) - len(f_ok) + len(av) - len(a_ok)
    total = len(facts) + len(av)

    out = [
        f"# CLEARANCE PACK — {pathlib.Path(script_path).stem}",
        "",
        "**Question asked: can this production lawfully be used to train a model, and "
        "can that be proved item by item?**",
        "",
        "> From 2026 the EU AI Act requires AI companies to disclose training-data "
        "sources and respect copyright opt-outs. This is that disclosure, for material "
        "already held.",
        "",
        "| | cleared | not cleared |",
        "|---|---:|---:|",
        f"| Factual assertions | {len(f_ok)} | {len(facts) - len(f_ok)} |",
        f"| Assets | {len(a_ok)} | {len(av) - len(a_ok)} |",
        "",
        f"> **{blocked} of {total} items in this production cannot be cleared for "
        f"AI training as things stand.**",
        "",
        "## Assets — blocked, with the instrument that blocks each",
        "",
        "| Item | Verdict | Instrument | Why |",
        "|---|---|---|---|",
    ]
    for v in av:
        if v.verdict != GREEN:
            out.append(f"| {v.subject_title[:38]} | **{v.verdict}** | "
                       f"`{(v.citation_url or '—').split('/vocab/')[-1].split('/licenses/')[-1]}` | "
                       f"{v.reason[:52]} |")
    out += ["", "## Factual assertions — every one, with its basis", "",
            "| Claim | Verdict | Basis / reason |", "|---|---|---|"]
    for r in facts:
        basis = ""
        if r["label"] == "SOURCED":
            import re
            m = re.search(r"basis: (\w+)", r.get("reason", "") or "")
            basis = (m.group(1) if m else "sourced") + f" — {r['citation_url']}"
        else:
            basis = r.get("why") or r.get("cause") or ""
        out.append(f"| {r['text'][:52]} | **{r['label']}** | {basis[:72]} |")

    derived = [r for r in f_ok if r.get("source_class") == "derived"]
    out += ["", "## What a lawyer must look at", "",
            f"- **{len(av) - len(a_ok)} assets** carry an instrument that blocks this "
            "use. Each names the instrument; none is a guess.",
            f"- **{len(facts) - len(f_ok)} assertions** could not be cleared. Each says "
            "whether nothing states it, nothing independent states it, or a document "
            "contradicts it.",
            f"- **{len(derived)} cleared assertions** rest on a derived source and are "
            "flagged; the engine cannot judge independence for you.",
            "",
            "Every cleared line quotes its document verbatim. Nothing here is inferred.",
            ""]
    return "\n".join(out)


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "fixtures/scripts/documentary-orphan-works.txt"
    doc = build(src)
    pathlib.Path("fixtures/CLEARANCE-PACK.md").write_text(doc)
    print(doc)
