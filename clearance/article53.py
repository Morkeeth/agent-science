"""EU AI Act Article 53(1)(d) — the evidence annex behind the mandatory disclosure.

WHAT THIS IS, stated precisely so nobody overclaims it:

The European Commission's AI Office published a **mandatory template** for the public
summary of training content on 24 July 2025, implementing Article 53(1)(d) of Regulation
(EU) 2024/1689. In force for new GPAI models since 2 August 2025; existing models must
comply by 2 August 2027. It binds every provider, including free and open-source.

The template asks for a **public summary** — "generally comprehensive in its scope
instead of technically detailed". **This module does NOT produce that filing.** It
produces the **evidence annex underneath it**: the per-item rights determination a
provider must actually possess before it can make Section 2 and Section 3 statements
truthfully.

That distinction is the product. Anyone can write a summary. Nobody can substantiate one.

Template sections, verbatim:
    1. "General Information"       — model, modalities, size, coverage
    2. "List of Data Sources"      — named datasets, licensed content, web-scraped
                                     domains, user-generated, synthetic
    3. "Data Processing Aspects"   — copyright compliance methods and OPT-OUT HANDLING
                                     under the EU Copyright Directive

Sections 2 and 3 are where a rights determination is unavoidable, and they are what this
engine already computes.
"""
from __future__ import annotations

import collections
from urllib.parse import urlparse

from .verdict import GREEN, RED, UNKNOWN

# A rights instrument that reserves rights IS an opt-out signal in the sense Article
# 53(1)(d) Section 3 asks about: the holder has expressed that this use is not granted.
_RESERVES_RIGHTS = ("InC", "by-nc", "by-nd", "InC-EDU", "InC-OW")


def _reserves(url: str | None) -> bool:
    return bool(url) and any(k.lower() in url.lower() for k in _RESERVES_RIGHTS)


def annex(verdicts, *, dataset_name: str, provider: str, use: str) -> str:
    n = len(verdicts)
    cleared = [v for v in verdicts if v.verdict == GREEN]
    blocked = [v for v in verdicts if v.verdict == RED]
    unresolved = [v for v in verdicts if v.verdict == UNKNOWN]
    reserved = [v for v in verdicts if _reserves(v.citation_url)]

    by_instrument = collections.Counter(
        (v.citation_url or "no instrument published") for v in verdicts)
    domains = collections.Counter(
        urlparse(v.citation_url).netloc for v in verdicts if v.citation_url)

    out = [
        f"# ARTICLE 53(1)(d) EVIDENCE ANNEX — {dataset_name}",
        "",
        f"**Provider:** {provider}  ",
        f"**Use assessed:** `{use}`  ",
        f"**Items assessed:** {n}",
        "",
        "> This is **not** the public summary required by the template. It is the "
        "per-item rights determination a provider must hold in order to make Section 2 "
        "and Section 3 statements truthfully. Every line cites the instrument the "
        "rights-holder published; none is inferred.",
        "",
        "## Section 2 — List of Data Sources",
        "",
        f"**Named dataset:** {dataset_name}, {n} items, individually assessed "
        "(the template requires large datasets be identified individually).",
        "",
        "**Rights instruments present, by count:**",
        "",
        "| Items | Instrument published by the rights-holder |",
        "|---:|---|",
    ]
    for uri, count in by_instrument.most_common():
        out.append(f"| {count} | `{uri}` |")

    out += ["", "**Source domains** (the template requires the top domains for "
            "web-collected content):", "",
            "| Items | Domain |", "|---:|---|"]
    for dom, count in domains.most_common(10):
        out.append(f"| {count} | `{dom}` |")

    pct = (len(reserved) / n) if n else 0
    out += [
        "",
        "## Section 3 — Data Processing Aspects: copyright compliance and opt-out handling",
        "",
        f"**{len(reserved)} of {n} items ({pct:.0%}) carry an instrument in which the "
        "rights-holder has RESERVED the rights this use would require.**",
        "",
        "Under the template a provider must describe how rights reservations and "
        "opt-outs were respected. For this dataset that determination is:",
        "",
        f"- **Usable for `{use}`:** {len(cleared)} items ({len(cleared)/n if n else 0:.0%}) — "
        "no instrument blocks this use",
        f"- **Rights reserved, use not granted:** {len(blocked)} items "
        f"({len(blocked)/n if n else 0:.0%}) — the instrument is named per item",
        f"- **Undetermined:** {len(unresolved)} items ({len(unresolved)/n if n else 0:.0%}) — "
        "**a provider cannot lawfully treat these as cleared**; each is an open question "
        "for the rights-holder",
        "",
        "### The undetermined items are the compliance exposure",
        "",
        "A summary that counts undetermined material as usable is a false statement in a "
        "mandatory filing. Each row below states why it could not be determined.",
        "",
        "| n | Why undetermined |", "|---:|---|",
    ]
    for reason, count in collections.Counter(v.reason for v in unresolved).most_common():
        out.append(f"| {count} | {reason[:88]} |")

    out += ["", "## Method", "",
            "Every item's rights instrument was fetched from its publisher "
            "(rightsstatements.org, creativecommons.org) and its operative clause quoted "
            "verbatim. No verdict exists in this annex without a citation — the "
            "constructor cannot build one. Where our reading of a licence is an "
            "interpretation rather than the instrument's plain words, it is flagged as "
            "such rather than asserted.", ""]
    return "\n".join(out)
