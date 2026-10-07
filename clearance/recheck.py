"""Re-read the sources behind saved answers, and flag every answer that depended on them.

The registry reuses a SOURCED claim forever. Reuse is the product, and it is only honest
while the evidence still holds — so something has to go back and look. `cases.refresh`
does this for research cases. This does it for the claim database that the ordinary
websearch, CLI and MCP path actually reads.

Three outcomes per claim, and they are deliberately different facts:

  unchanged             the document hashes to what it hashed to when the span was read
  changed_quote_intact  the document changed; the saved span is still verbatim in it
  changed_quote_absent  the document changed and the saved span is GONE

Only the third moves a verdict. It moves it to UNKNOWN with the engine's existing cause
`source_does_not_state_it` — we opened the document and it does not state this — and the
precise mechanism rides alongside in `refusal_code`. No new cause is invented: the
refusal vocabulary is a closed set in `clearance/verdict.py`, and widening it here would
let the registry say more than the engine can prove.

A source that cannot be read is NOT a source that changed. It reports `unchecked` and
moves nothing. Absence of a fetch is not evidence about a document.

Nothing in this module claims a saved provider call, saved money or saved time.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from clearance import refusal_log

UNCHANGED = "unchanged"
CHANGED_INTACT = "changed_quote_intact"
CHANGED_ABSENT = "changed_quote_absent"
UNCHECKED = "unchecked"
FIRST_BASELINE = "baseline_recorded"

# The precise mechanism, stored beside the coarse cause. `cause` stays inside the
# engine's closed vocabulary; this is what actually happened.
REFUSAL_CODE = "source_changed_quote_absent"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalise(text: str) -> str:
    return " ".join((text or "").split())


def quote_present(quoted_terms: str | None, document_text: str | None) -> bool:
    """Whether the saved span is still verbatim in the document.

    Whitespace is normalised on both sides, because a re-flowed paragraph is not a
    changed sentence. Nothing else is normalised: this is a verbatim test, and a
    fuzzy one would quietly turn "the source still says it" into "something like it
    is still in there".
    """
    span = _normalise(quoted_terms)
    if not span:
        return False
    return span in _normalise(document_text)


def _current_snapshot(url: str, *, live: bool):
    """The document as it is now (live) or as we last saved it (offline).

    live=True fetches; a failed fetch returns None and never silently falls back to the
    cached copy, or "we re-read the source" would be a claim about a fetch that failed.
    """
    from clearance import instruments
    if live:
        return instruments.document_snapshot(url, refresh=True)
    return instruments.document_snapshot(url, fetch=False)


def _carried(row) -> dict:
    """Fields that describe how the claim was established, and must survive a rebind.

    `record()`'s UPDATE branch writes every column, so a rebind that omits `origins` or
    `trail` erases them: an engine-written row loses the locator trail on its first
    recheck, and the shelf then renders "no trail recorded" for a row that had one.
    Re-reading a document is not new knowledge about how the claim was found.
    """
    try:
        origins = json.loads(row.get("origins") or "[]")
    except ValueError:
        origins = []
    return {"origins": origins, "trail": refusal_log.trail_of(row) or None}


def recheck_claim(con, row, *, live: bool, production: str = "recheck") -> dict:
    """Re-read one claim's source. Returns the finding; writes only on a real change."""
    row = dict(row)
    url = row.get("citation_url")
    finding = {
        "assertion": row.get("established"),
        "citation_url": url,
        "was": refusal_log.surface_label(verdict=row.get("verdict"),
                                         cause=row.get("cause")),
        "saved_sha256": row.get("source_sha256"),
        "saved_fetched_at": row.get("source_fetched_at"),
    }
    if not url:
        return {**finding, "status": UNCHECKED,
                "reason": "the claim cites no URL, so there is nothing to re-read"}

    snap = _current_snapshot(url, live=live)
    if not snap:
        return {**finding, "status": UNCHECKED,
                "reason": ("the source could not be read now"
                           if live else
                           "no local snapshot of this source; re-run with live "
                           "re-reading to fetch it"),
                "moved": False}

    now_sha = snap.get("sha256")
    finding["current_sha256"] = now_sha
    finding["current_fetched_at"] = snap.get("fetched_at")

    if not row.get("source_sha256"):
        # No baseline was ever recorded (the row predates the freshness columns). We
        # know what the document says NOW; we do not know what it said then, and
        # pretending otherwise would manufacture an unchanged verdict.
        refusal_log.record(
            con, term=row["term"], assertion=row["established"],
            verdict=row["verdict"], production=row["first_seen_in"],
            basis=row.get("basis"), cause=row.get("cause"),
            citation_url=url, quoted_terms=row.get("quoted_terms"),
            resolves_with=row.get("resolves_with"), refusal_code=row.get("refusal_code"),
            source_fetched_at=snap.get("fetched_at"), source_sha256=now_sha,
            evidence_checked_at=_now(), **_carried(row),
        )
        return {**finding, "status": FIRST_BASELINE, "moved": False,
                "reason": ("no snapshot was recorded when this claim was established, "
                           "so no comparison is possible; today's snapshot is now the "
                           "baseline and the verdict is unchanged")}

    if now_sha == row.get("source_sha256"):
        con.execute("UPDATE claims SET evidence_checked_at=? WHERE term=? AND slot=?",
                    (_now(), row["term"], row["slot"]))
        con.commit()
        return {**finding, "status": UNCHANGED, "moved": False,
                "reason": "the document hashes to the same text the span was read from"}

    intact = quote_present(row.get("quoted_terms"), snap.get("text"))
    if intact:
        # The page moved around the sentence. The evidence still holds, so the verdict
        # does not move — but the snapshot it is bound to does, and that is written down.
        refusal_log.record(
            con, term=row["term"], assertion=row["established"],
            verdict=row["verdict"], production=row["first_seen_in"],
            basis=row.get("basis"), cause=row.get("cause"),
            citation_url=url, quoted_terms=row.get("quoted_terms"),
            resolves_with=row.get("resolves_with"), refusal_code=row.get("refusal_code"),
            source_fetched_at=snap.get("fetched_at"), source_sha256=now_sha,
            evidence_checked_at=_now(), **_carried(row),
        )
        return {**finding, "status": CHANGED_INTACT, "moved": False,
                "reason": "the document changed; the saved span is still verbatim in it"}

    # The span is gone. This is the one case that moves a verdict, and it moves it to
    # uncertainty, never to a contradiction: a missing sentence is not a refutation.
    refusal_log.record(
        con, term=row["term"], assertion=row["established"],
        verdict="UNKNOWN", production=production,
        cause="source_does_not_state_it",
        citation_url=url,
        quoted_terms=(f"re-read {_now()}: {len(snap.get('text') or ''):,} characters; "
                      f"the previously cited span is no longer present"),
        resolves_with=("re-verify against the current source, or cite the archived "
                       f"snapshot {row.get('source_sha256')}"),
        refusal_code=REFUSAL_CODE,
        origins=_carried(row)["origins"],
        source_fetched_at=snap.get("fetched_at"), source_sha256=now_sha,
        evidence_checked_at=_now(),
    )
    return {**finding, "status": CHANGED_ABSENT, "moved": True,
            "now": "UNSOURCED",
            "previous_span": row.get("quoted_terms"),
            "reason": ("the document changed and the span this answer rested on is no "
                       "longer in it; the claim is uncertain again until re-verified"),
            "dependents": refusal_log.dependents(con, url)}


def recheck(*, url: str | None = None, live: bool = False, limit: int = 200,
            db: Path | str | None = None, con=None,
            production: str = "recheck") -> dict:
    """Re-read the sources behind saved SOURCED answers.

    live=False re-reads only documents already cached on this machine and makes no
    network call. live=True re-fetches. Either way, what is reported is a comparison of
    documents — never a claim that anything was saved by not searching.
    """
    owned = con is None
    if owned:
        con = refusal_log.connect(Path(db) if db else refusal_log.DB)
    try:
        sql = "SELECT * FROM claims WHERE verdict='GREEN' AND citation_url IS NOT NULL"
        args: list = []
        if url:
            sql += " AND citation_url = ?"
            args.append(url)
        sql += " ORDER BY reused DESC, first_seen_at DESC LIMIT ?"
        args.append(limit)
        rows = con.execute(sql, args).fetchall()

        sourced_total = con.execute(
            "SELECT COUNT(*) c FROM claims WHERE verdict='GREEN'").fetchone()["c"]
        claims_total = con.execute("SELECT COUNT(*) c FROM claims").fetchone()["c"]

        findings = [recheck_claim(con, r, live=live, production=production) for r in rows]
        counts = {k: sum(1 for f in findings if f["status"] == k)
                  for k in (UNCHANGED, CHANGED_INTACT, CHANGED_ABSENT, UNCHECKED,
                            FIRST_BASELINE)}
        affected = [f for f in findings if f.get("moved")]
        return {
            "mode": "live re-read" if live else "cached snapshots only (no network call)",
            "url": url,
            "checked": len(findings),
            "sourced_claims_in_registry": sourced_total,
            "claims_in_registry": claims_total,
            "counts": counts,
            "findings": findings,
            "answers_flagged": sum(
                f["dependents"]["answers_on_this_url"] for f in affected),
            "answers_in_registry": con.execute(
                "SELECT COUNT(*) c FROM queries").fetchone()["c"],
            "limits": [
                "A verbatim span is evidence that a document contains those words. "
                "It is not entailment and it is not truth.",
                "Only a claim whose saved span has disappeared is moved, and it is "
                "moved to UNKNOWN, never to refuted.",
                "A source that could not be read is reported unchecked. It is not "
                "reported unchanged.",
                "No provider call was made or avoided here; nothing about cost, time "
                "or saved searches is measured by this command.",
            ],
        }
    finally:
        if owned:
            con.close()


def format_report(report: dict) -> str:
    c = report["counts"]
    lines = [
        "# Evidence recheck",
        f"  mode: {report['mode']}",
        f"  re-read {report['checked']} of {report['sourced_claims_in_registry']} "
        f"sourced claims ({report['claims_in_registry']} claims in the registry)",
        f"  unchanged={c[UNCHANGED]}  changed_quote_intact={c[CHANGED_INTACT]}  "
        f"CHANGED_QUOTE_ABSENT={c[CHANGED_ABSENT]}  unchecked={c[UNCHECKED]}  "
        f"baseline_recorded={c[FIRST_BASELINE]}",
        "",
    ]
    for f in report["findings"]:
        if f["status"] == UNCHANGED:
            continue
        lines.append(f"  [{f['status']}] {str(f.get('assertion'))[:70]}")
        lines.append(f"      {f.get('citation_url')}")
        lines.append(f"      {f.get('reason')}")
        if f.get("moved"):
            dep = f["dependents"]
            lines.append(f"      verdict moved: {f['was']} -> {f['now']}")
            lines.append(
                f"      DEPENDENT ANSWERS: {dep['answers_on_this_url']} of "
                f"{dep['answers_total']} logged answers and "
                f"{dep['claims_on_this_url']} of {dep['claims_total']} claims cite "
                f"this URL")
            for a in dep["answers"][:10]:
                lines.append(f"        · {str(a.get('query_text'))[:66]}  "
                             f"[{a.get('result_label')}]  {str(a.get('asked_at'))[:19]}")
    if report["counts"][CHANGED_ABSENT] == 0:
        lines.append("  No saved span has disappeared from its source.")
    lines.append("")
    lines += ["  " + line for line in report["limits"]]
    return "\n".join(lines) + "\n"
