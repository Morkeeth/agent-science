#!/usr/bin/env python3
"""Use-path baseline eval — shipping truth layer vs naive arms that can beat us.

Arms:
  shipping_local — dictionary lookup live=false against local REFUSAL_LOG_DB
  shipping_hosted — GET /search?live=false on the public Cloud Run URL (when reachable)
  naive_cite — always invents a Wikipedia URL (looks confident, often wrong)
  always_silent — always NOT_CLEARED / no citation (null that can win honesty)

Scored on fixtures/use-path/cases.json — re-derived at object, never carried from docs.

This eval is allowed to embarrass us. Measured 2026-09-04: naive_cite beat
shipping_local because cheap CELEX fetch cannot SOURCED the flagship query offline
(EUR-Lex blocked); hosted still returns dictionary_exact SOURCED for 2012/28/EU.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import stack_search

CASES = ROOT / "fixtures" / "use-path" / "cases.json"
HOSTED = os.environ.get(
    "AGENT_SCIENCE_URL",
    "https://agent-science-568004190078.us-central1.run.app",
)


def _load_cases() -> list[dict]:
    data = json.loads(CASES.read_text())
    return data["cases"]


def arm_shipping_local(query: str, *, db: Path) -> dict:
    return stack_search.lookup(query, live=False, db=db, traffic="gate")


def arm_shipping_hosted(query: str, *, db: Path) -> dict:
    q = urllib.parse.urlencode({"q": query, "live": "false", "traffic": "gate"})
    url = f"{HOSTED.rstrip('/')}/search?{q}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        return {
            "query": query,
            "label": "NOT_CLEARED",
            "cause": f"hosted_unreachable:{e}",
            "citation_url": None,
            "quoted_terms": None,
        }


def arm_naive_cite(query: str, *, db: Path) -> dict:
    return {
        "query": query,
        "label": "SOURCED",
        "citation_url": "https://en.wikipedia.org/wiki/" + query.replace(" ", "_")[:40],
        "quoted_terms": query,
        "verdict": "GREEN",
        "cause": None,
        "arm": "naive_cite",
    }


def arm_always_silent(query: str, *, db: Path) -> dict:
    return {
        "query": query,
        "label": "NOT_CLEARED",
        "citation_url": None,
        "quoted_terms": None,
        "verdict": None,
        "cause": "always_silent",
        "arm": "always_silent",
    }


def score_case(case: dict, result: dict) -> dict:
    expect = case["expect"]
    label = result.get("label")
    cite = result.get("citation_url")
    span = (result.get("quoted_terms") or "").strip()

    correct_pole = False
    if expect == "sourced":
        correct_pole = label == "SOURCED" and bool(cite)
    elif expect == "refuse":
        correct_pole = label in ("NOT_CLEARED", "UNSOURCED", "UNKNOWN", "REFUTED")
    else:
        correct_pole = True

    no_invented = True
    if expect == "refuse":
        no_invented = not cite

    has_span = True
    if expect == "sourced" and label == "SOURCED":
        has_span = bool(span)
    elif expect == "sourced" and label != "SOURCED":
        has_span = False

    pts = int(correct_pole) + int(no_invented) + int(has_span)
    return {
        "id": case["id"],
        "correct_pole": correct_pole,
        "no_invented_cite": no_invented,
        "has_span": has_span,
        "points": pts,
        "label": label,
    }


def run(*, include_hosted: bool = True) -> dict:
    cases = _load_cases()
    db = Path(tempfile.mkdtemp()) / "eval.db"
    real = Path(os.environ.get("REFUSAL_LOG_DB", ROOT / "cache" / "refusal_log.db"))
    if real.exists():
        db = real

    arms = {
        "shipping_local": arm_shipping_local,
        "naive_cite": arm_naive_cite,
        "always_silent": arm_always_silent,
    }
    if include_hosted:
        arms["shipping_hosted"] = arm_shipping_hosted

    per_arm: dict[str, list] = {k: [] for k in arms}
    for case in cases:
        for name, fn in arms.items():
            res = fn(case["query"], db=db)
            per_arm[name].append(score_case(case, res))

    summary = {}
    for name, rows in per_arm.items():
        n = len(rows)
        summary[name] = {
            "n": n,
            "points": sum(r["points"] for r in rows),
            "max_points": n * 3,
            "correct_pole": sum(1 for r in rows if r["correct_pole"]),
            "no_invented_cite": sum(1 for r in rows if r["no_invented_cite"]),
            "has_span": sum(1 for r in rows if r["has_span"]),
            "rows": rows,
        }

    ranking = sorted(summary.keys(), key=lambda k: (-summary[k]["points"], k))
    return {
        "cases": len(cases),
        "db": str(db),
        "hosted": HOSTED if include_hosted else None,
        "summary": {
            k: {kk: vv for kk, vv in v.items() if kk != "rows"}
            for k, v in summary.items()
        },
        "detail": summary,
        "ranking": ranking,
        "winner": ranking[0],
        "finding": _finding(summary, ranking),
    }


def _finding(summary: dict, ranking: list[str]) -> str:
    win = ranking[0]
    local = summary.get("shipping_local")
    silent = summary["always_silent"]
    naive = summary["naive_cite"]
    hosted = summary.get("shipping_hosted")
    bits = []
    if win == "naive_cite":
        bits.append(
            f"EMBARRASSING: naive always-cite beat the field — naive={naive['points']} "
            f"local={local['points']}"
            + (f" hosted={hosted['points']}" if hosted else "")
            + "."
        )
    elif win == "always_silent":
        bits.append(
            f"EMBARRASSING: always_silent null beat shipping — "
            f"silent={silent['points']} local={local['points']}."
        )
    elif win.startswith("shipping"):
        bits.append(
            f"{win} leads ({summary[win]['points']}/{summary[win]['max_points']})."
        )
    if hosted and local and hosted["points"] > local["points"]:
        bits.append(
            f"Hosted ahead of local ({hosted['points']} vs {local['points']}) — "
            "cold/boot shelf cannot replay SOURCED for flagship without warm exact rows "
            "/ EUR-Lex fetch."
        )
    if local and local["points"] <= silent["points"]:
        bits.append(
            f"Local tied/lost to always_silent ({local['points']} vs {silent['points']})."
        )
    return " ".join(bits) if bits else "no finding"


if __name__ == "__main__":
    skip_hosted = os.environ.get("USE_PATH_EVAL_OFFLINE") == "1"
    out = run(include_hosted=not skip_hosted)
    print(json.dumps({
        "cases": out["cases"],
        "db": out["db"],
        "hosted": out.get("hosted"),
        "summary": out["summary"],
        "ranking": out["ranking"],
        "winner": out["winner"],
        "finding": out["finding"],
    }, indent=2))
    local = out["summary"].get("shipping_local")
    if local and local["correct_pole"] == 0 and out["cases"] > 0:
        sys.exit(2)
    sys.exit(0)
