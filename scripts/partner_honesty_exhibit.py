#!/usr/bin/env python3
"""Partner honesty exhibit — shipping compound vs naive non-compound on hosted URL.

Measures against something we did not soft-pass away:

* SHIPPING arm — same subject A/B (compound-fresh shape). Classifies against the
  sealed prediction (STRICT B < A Parallel + corpus_hits ≥ 1) and the softer
  verify gate (B ≤ A + hits). Soft-pass while sealed fails is a finding, not a
  green tick.
* NAIVE arm — overlapping claim text on *different* subjects. A competent team
  that never builds a shelf gets this: no corpus_hits expected on B. If naive
  matches or beats shipping on Parallel economics, that is the finding.

Also stamps ADK fields from the live gap report so partner wiring is proved at
the /clear object, not only /health.

Usage: python3 scripts/partner_honesty_exhibit.py [BASE_URL]
Exit 0 always writes a receipt class; exit 1 only on transport/assert failure.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = "https://agent-science-568004190078.us-central1.run.app"


def _get(url: str, timeout: float = 60) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read())


def _clear(base: str, script: str, subject: str, label: str) -> dict:
    body = json.dumps({"script": script, "subject": subject}).encode()
    req = urllib.request.Request(
        base.rstrip("/") + "/clear",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read())
    keys_summary = [
        "engine",
        "adk_version",
        "adk_tool_calls",
        "model_routing",
        "parallel_calls",
        "parallel_api_calls",
        "search_cache_hits",
        "corpus_hits",
        "log_hits",
        "corpus_remembered",
        "claims_extracted",
        "sourced",
        "unsourced",
    ]
    summary = {k: data.get(k) for k in keys_summary}
    summary["parallel_calls"] = summary.get("parallel_calls") or 0
    summary["parallel_api_calls"] = summary.get("parallel_api_calls")
    summary["corpus_hits"] = summary.get("corpus_hits") or 0
    summary["log_hits"] = summary.get("log_hits") or 0
    summary["elapsed_s"] = round(time.time() - t0, 1)
    print(f"{label} {summary}")
    return summary


def _classify(ap: int, bp: int, bh: int) -> str:
    """Sealed prediction wants STRICT_DROP. Soft verify accepts NON_INCREASE."""
    if ap < 1:
        return "NO_PARALLEL_ON_A"
    if bh < 1:
        return "NO_CORPUS_HIT"
    if bp < ap:
        return "STRICT_DROP"
    if bp <= ap:
        return "SOFT_PASS_FLAT"  # B == A Parallel; hits only — sealed miss
    return "PARALLEL_INCREASE"


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    token = uuid.uuid4().hex[:12]

    print(f"=== Partner honesty exhibit === stamp={stamp}")
    print(f"URL: {base}")

    health = _get(base.rstrip("/") + "/health")
    partners = _get(base.rstrip("/") + "/partners")
    stats = _get(base.rstrip("/") + "/stats")
    print(
        "HEALTH",
        {
            "engine_default": health.get("engine_default"),
            "gemini": health.get("gemini"),
            "parallel": health.get("parallel"),
            "adk_version": health.get("adk_version"),
            "parallel_sdk": health.get("parallel_sdk"),
        },
    )
    print(
        "STATS",
        {
            "n": stats.get("n"),
            "dictionary_hit_rate": stats.get("dictionary_hit_rate"),
            "queries_logged": stats.get("queries_logged"),
            "reuses": stats.get("reuses"),
        },
    )
    checklist = (partners.get("track_checklist") or {})
    print("PARTNERS_CHECKLIST", checklist)

    # --- SHIPPING arm: same subject A/B (compound-fresh) ---
    subject = f"honesty-ship-{token}"
    script_a = (
        f"NARRATOR (V.O.)\n"
        f"In {token[:4]} the Archive of Zephyr-{token} passed Regulation "
        f"Z-{token.upper()} for orphan media.\n"
        f"The Collective-{token} estimated that fifty-one percent of "
        f"pre-contact works lack authorship."
    )
    script_b = (
        f"NARRATOR (V.O.)\n"
        f"In {token[:4]} the Archive of Zephyr-{token} passed Regulation "
        f"Z-{token.upper()} for orphan media.\n"
        f"The Phobos Library-{token} opened digitisation in 2851 with "
        f"forty-two staff members."
    )
    print("--- SHIPPING compound (same subject) ---")
    ship_a = _clear(base, script_a, subject, "SHIP_A")
    ship_b = _clear(base, script_b, subject, "SHIP_B")
    ship_class = _classify(
        ship_a["parallel_calls"], ship_b["parallel_calls"], ship_b["corpus_hits"]
    )
    soft_ok = (
        ship_a["parallel_calls"] >= 1
        and ship_b["corpus_hits"] >= 1
        and ship_b["parallel_calls"] <= ship_a["parallel_calls"]
    )
    sealed_ok = (
        ship_a["parallel_calls"] >= 1
        and ship_b["corpus_hits"] >= 1
        and ship_b["parallel_calls"] < ship_a["parallel_calls"]
    )
    print(
        "SHIPPING",
        {
            "class": ship_class,
            "soft_gate": soft_ok,
            "sealed_strict": sealed_ok,
            "A_parallel": ship_a["parallel_calls"],
            "B_parallel": ship_b["parallel_calls"],
            "B_hits": ship_b["corpus_hits"],
            "engine": ship_a.get("engine"),
            "adk_tool_calls": ship_a.get("adk_tool_calls"),
        },
    )

    # --- NAIVE arm: different subjects + distinct claim tokens ---
    # Distinct tokens matter: Parallel search results cache by claim text on the
    # host (`cache/searches.json`). Reusing shipping's script would zero Parallel
    # on "naive" A via cache hit — a nearer proxy that is not a no-memory baseline.
    naive_token = uuid.uuid4().hex[:12]
    sub_a = f"honesty-naive-a-{naive_token}"
    sub_b = f"honesty-naive-b-{naive_token}"
    naive_script_a = (
        f"NARRATOR (V.O.)\n"
        f"In {naive_token[:4]} the Archive of Zephyr-{naive_token} passed Regulation "
        f"Z-{naive_token.upper()} for orphan media.\n"
        f"The Collective-{naive_token} estimated that fifty-one percent of "
        f"pre-contact works lack authorship."
    )
    naive_script_b = (
        f"NARRATOR (V.O.)\n"
        f"In {naive_token[:4]} the Archive of Zephyr-{naive_token} passed Regulation "
        f"Z-{naive_token.upper()} for orphan media.\n"
        f"The Phobos Library-{naive_token} opened digitisation in 2851 with "
        f"forty-two staff members."
    )
    print("--- NAIVE non-compound (different subjects, distinct tokens) ---")
    naive_a = _clear(base, naive_script_a, sub_a, "NAIVE_A")
    naive_b = _clear(base, naive_script_b, sub_b, "NAIVE_B")
    naive_hits = naive_b["corpus_hits"]
    # Naive should not compound across subjects. Hits on B are a cross-subject leak.
    naive_leaks = naive_hits >= 1
    # With distinct tokens, both naive runs should exercise Parallel (≥1 each).
    # Flat or rising Parallel across A→B with hits=0 is the no-shelf baseline.
    naive_parallel_ok = (
        naive_a["parallel_calls"] >= 1 and naive_b["parallel_calls"] >= 1
    )
    print(
        "NAIVE",
        {
            "A_parallel": naive_a["parallel_calls"],
            "B_parallel": naive_b["parallel_calls"],
            "B_hits": naive_hits,
            "cross_subject_leak": naive_leaks,
            "parallel_both_fired": naive_parallel_ok,
            "engine": naive_a.get("engine"),
        },
    )
    if not naive_parallel_ok:
        print(
            "FINDING_RED: naive arm did not fire Parallel on both runs "
            f"(A={naive_a['parallel_calls']} B={naive_b['parallel_calls']}) — "
            "search-cache or routing short-circuit; baseline is contaminated"
        )

    # Parallel delta comparison — three different free paths can drop Parallel:
    # corpus_hits (same subject), log_hits (cross-subject refusal log), search cache
    # (parallel_api_calls < claims that reached find_sources). Measure all three;
    # do not blame search cache without reading log_hits on the object.
    ship_delta = ship_a["parallel_calls"] - ship_b["parallel_calls"]
    naive_delta = naive_a["parallel_calls"] - naive_b["parallel_calls"]
    naive_log_explains = (
        naive_parallel_ok
        and not naive_leaks
        and naive_delta > 0
        and (naive_b.get("log_hits") or 0) >= 1
    )
    ship_api_a = ship_a.get("parallel_api_calls")
    ship_api_b = ship_b.get("parallel_api_calls")
    naive_api_a = naive_a.get("parallel_api_calls")
    naive_api_b = naive_b.get("parallel_api_calls")
    # Search-cache signal: claim went to search path but live API calls are lower
    # than parallel_calls on that run (cache satisfied some finds).
    def _cache_gap(row: dict) -> int | None:
        api = row.get("parallel_api_calls")
        if api is None:
            return None
        return max(0, (row.get("parallel_calls") or 0) - api)

    parallel_drop_explained_by_log = naive_log_explains
    parallel_drop_explained_by_cache = (
        naive_parallel_ok
        and not naive_leaks
        and naive_delta > 0
        and not naive_log_explains
        and ((_cache_gap(naive_a) or 0) > 0 or (_cache_gap(naive_b) or 0) > 0)
    )
    if naive_log_explains:
        print(
            "FINDING_RED: naive arm Parallel drop explained by cross-subject "
            f"log_hits={naive_b.get('log_hits')} (corpus_hits=0). "
            "Search-cache was a nearer guess — log reuse is the object."
        )
    elif parallel_drop_explained_by_cache:
        print(
            "FINDING_RED: naive arm also dropped Parallel "
            f"(A={naive_a['parallel_calls']}→B={naive_b['parallel_calls']}, hits=0, "
            f"log_hits={naive_b.get('log_hits')}). "
            "No log_hits — inspect parallel_api_calls vs parallel_calls for cache."
        )

    # Who wins on Parallel economics for the overlapping claim path?
    # Shipping wins when sealed_ok against a clean naive (no leak, Parallel fired).
    if sealed_ok and not naive_leaks and naive_parallel_ok:
        if parallel_drop_explained_by_log or parallel_drop_explained_by_cache:
            winner = "shipping_on_corpus_hits_only"
        else:
            winner = "shipping_strict"
    elif soft_ok and not naive_leaks and naive_parallel_ok:
        winner = "shipping_soft_only"
    elif not naive_parallel_ok:
        winner = "naive_baseline_contaminated"
    elif naive_leaks and soft_ok:
        winner = "tie_or_leak"
    elif naive_leaks and not soft_ok:
        winner = "naive_looks_better_or_broken_shelf"
    else:
        winner = "shipping_missed_soft_gate"

    finding = {
        "stamp": stamp,
        "base": base,
        "shipping_class": ship_class,
        "soft_gate": soft_ok,
        "sealed_strict": sealed_ok,
        "naive_cross_subject_leak": naive_leaks,
        "naive_parallel_both_fired": naive_parallel_ok,
        "ship_parallel_delta": ship_delta,
        "naive_parallel_delta": naive_delta,
        "naive_b_log_hits": naive_b.get("log_hits") or 0,
        "ship_b_log_hits": ship_b.get("log_hits") or 0,
        "parallel_drop_explained_by_log_hits": parallel_drop_explained_by_log,
        "parallel_drop_explained_by_search_cache": parallel_drop_explained_by_cache,
        "ship_cache_gap_A": _cache_gap(ship_a),
        "ship_cache_gap_B": _cache_gap(ship_b),
        "naive_cache_gap_A": _cache_gap(naive_a),
        "naive_cache_gap_B": _cache_gap(naive_b),
        "winner": winner,
        "health_engine_default": health.get("engine_default"),
        "shelf_n": stats.get("n"),
        "hit_rate": stats.get("dictionary_hit_rate"),
        "queries_logged": stats.get("queries_logged"),
        "partners_ok": all(
            checklist.get(k)
            for k in (
                "parallel_search_at_runtime",
                "gemini_at_runtime",
                "adk_agent_builder",
            )
        ),
    }
    print("FINDING", finding)

    # Embarrassment flags — print loud so receipts cannot hide them.
    if not sealed_ok and soft_ok:
        print(
            "FINDING_RED: soft verify PASS but sealed prediction (B < A Parallel) FAILED "
            f"— class={ship_class} A={ship_a['parallel_calls']} B={ship_b['parallel_calls']} "
            f"hits={ship_b['corpus_hits']}"
        )
    if naive_leaks:
        print(
            "FINDING_RED: naive different-subject arm got corpus_hits≥1 "
            f"(hits={naive_hits}) — cross-subject collision or warm global shelf"
        )
    if ship_a.get("engine") != "adk":
        print(
            f"FINDING_RED: /clear engine={ship_a.get('engine')!r}, expected adk"
        )

    out = ROOT / "docs" / "RECEIPT-partner-honesty-exhibit-raw-2026-09-04.json"
    out.write_text(
        json.dumps(
            {
                "finding": finding,
                "health": health,
                "stats": {
                    k: stats.get(k)
                    for k in (
                        "n",
                        "cleared",
                        "refused",
                        "reuses",
                        "dictionary_hit_rate",
                        "queries_logged",
                    )
                },
                "shipping": {"A": ship_a, "B": ship_b},
                "naive": {"A": naive_a, "B": naive_b},
                "checklist": checklist,
            },
            indent=2,
        )
        + "\n"
    )
    print(f"WROTE {out.relative_to(ROOT)}")

    # Transport OK; honesty findings are the product, not a nonzero exit.
    # Fail only if partners are not on the path at all.
    if health.get("engine_default") != "adk":
        print("FAIL: engine_default is not adk", file=sys.stderr)
        return 1
    if not health.get("parallel") or not health.get("gemini"):
        print("FAIL: parallel/gemini not live on /health", file=sys.stderr)
        return 1
    if ship_a.get("engine") != "adk":
        print("FAIL: /clear did not stamp engine=adk", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.reason}", file=sys.stderr)
        raise SystemExit(2)
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
        raise SystemExit(2)
