"""EU AI Act Article 53(1)(d) — the evidence annex behind the mandatory disclosure.

WHAT THIS IS, stated precisely so nobody overclaims it:

The European Commission's AI Office published a **mandatory template** for the public
summary of training content on 24 July 2025, implementing Article 53(1)(d) of Regulation
(EU) 2024/1689. In force for new GPAI models since 2 August 2025; existing models must comply by
2 August 2027; **enforcement begins 2 August 2026**. It binds every provider, including
free and open-source.

**THE FILING IS NARRATIVE, NOT ITEM-BY-ITEM, AND THAT CUTS AGAINST A NAIVE VERSION OF
THIS PRODUCT.** Verified at the Commission's own FAQ: the template "requires narrative
summaries, not item-by-item listings", deliberately, to protect trade secrets. **A
regulator will never read this annex.** Anyone selling "we generate your item-by-item AI
Act disclosure" is selling something the regulation does not ask for.

**What the regulation DOES ask for is the thing that needs this.** Rightsholders are to
be told *"to what extent the conditions for lawful text and data mining, as provided for
in the Copyright in the Digital Single Market Directive, have been respected."*

**You cannot state an EXTENT truthfully without having measured it.** The narrative
sentence is one line; the measurement behind it is this annex. So this module does not
produce the filing and never should — it produces the **record that the measurement was
actually performed**, which is what makes the narrative statement true and what a
provider has nothing else to fall back on if challenged.

The stakes, verbatim from the Commission: *"Non-compliance may result in fines of up to
3% of the provider's annual total worldwide turnover in the preceding financial year, or
15 000 000 Euros, whichever is higher."* **Enforcement begins 2 August 2026.**

And the summary *"should be updated at six-month intervals, or sooner if the new data
used for further training requires a materially significant update"* — so the
measurement is **recurring**, which is precisely the repeat customer the compounding
curve measured.

Anyone can write the summary. Nobody can substantiate one.

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
        "> **This is not the filing.** The Commission's template requires a NARRATIVE "
        "summary, not an item-by-item listing, and no regulator will read this document. "
        "It is the measurement behind one sentence of that filing: the extent to which "
        "text-and-data-mining conditions were respected. An extent cannot be stated "
        "truthfully without being measured. Every line cites the instrument the "
        "rights-holder published; none is inferred.",
        "",
        "> Non-compliance: fines up to **3% of worldwide turnover or EUR 15,000,000, "
        "whichever is higher**. Enforcement begins **2 August 2026**. The summary must be "
        "updated every **six months**.",
        "",
        "## Section 2 — List of Data Sources",
        "",
        f"**Named dataset:** {dataset_name}, {n} items, individually assessed. "
        "The template asks that large datasets be identified individually; the "
        "per-item assessment below is the evidence, not the disclosure.",
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
