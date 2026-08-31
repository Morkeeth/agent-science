#!/usr/bin/env python3
"""Measure the semantic guard. Both directions, or it is not a measurement.

    python3 scripts/eval_semantic_guard.py

A guard that closes 5 false GREENs by refusing 50 true ones is a worse product than the
hole it closed, so this script refuses to report one number. It reports:

  ARM A  guard OFF (CLEARANCE_SEMANTIC_GUARD=0) — the engine that shipped 2026-08-30
  ARM B  guard ON

on two populations:

  GOLD      fixtures/refusal-correctness/set.json, n=6, labelled 2026-08-22 by Cursor
            BEFORE any engine run — the only population here with a right answer.
  REGISTRY  every claim in research-corpus/, re-cleared offline against the document
            cache. This is the population the shipped registry was built from: same
            command, same parser, same locator. It is UNLABELLED, so every verdict that
            changes is PRINTED IN FULL for a human to adjudicate. A count of flips is
            not a count of defects closed and this script never calls it one.

Per-check attribution is separate: each of the three mechanisms is run alone, so no
mechanism can hide inside the total. The coverage threshold is swept, not chosen.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

GUARD_ENV = "CLEARANCE_SEMANTIC_GUARD"
SWEEP = (0.30, 0.40, 0.50, 0.60)


def _arm(on: bool):
    os.environ[GUARD_ENV] = "1" if on else "0"


# ------------------------------------------------------------------ gold population

def gold() -> dict:
    from clearance import instruments
    from clearance.facts import Claim, judge_claim
    from clearance.verdict import GREEN

    SET = json.loads((ROOT / "fixtures/refusal-correctness/set.json").read_text())
    out = {"n": len(SET["items"]), "rows": [], "labelled_at": SET["labelled_at"]}
    saved = instruments.document
    for it in SET["items"]:
        body = (ROOT / it["document"]).read_text()
        url = f"fixture://{it['id']}"

        def fake(u, fetch=False, _b=body, _u=url):
            return _b if u == _u else saved(u, fetch=fetch)

        instruments.document = fake
        try:
            c = Claim(it["id"], it["claim"], url, it["must_contain"])
            off = judge_claim(c, semantic=False)
            on = judge_claim(c, semantic=True)
        finally:
            instruments.document = saved
        out["rows"].append({
            "id": it["id"], "gold": it["expected"],
            "off": "SUPPORTED" if off.verdict == GREEN else "NOT_SUPPORTED",
            "on": "SUPPORTED" if on.verdict == GREEN else "NOT_SUPPORTED",
            "on_reason": (on.quoted_terms or "") if on.verdict != GREEN else "",
        })
    for arm in ("off", "on"):
        out[f"correct_{arm}"] = sum(r[arm] == r["gold"] for r in out["rows"])
    return out


# -------------------------------------------------------------- registry population

def registry() -> dict:
    """Re-clear the whole research corpus in both arms, offline, from the doc cache."""
    import clear_corpus as C

    res = {}
    for name, on in (("off", False), ("on", True)):
        _arm(on)
        r = C.verify_corpus("research-corpus", fetch=False)
        res[name] = r
    rows_off = {(r["file"], r["line"]): r for r in res["off"]["rows"]}
    rows_on = {(r["file"], r["line"]): r for r in res["on"]["rows"]}

    flips = []
    for k, a in rows_off.items():
        b = rows_on.get(k)
        if b and a["verdict"] != b["verdict"]:
            flips.append({"file": a["file"], "line": a["line"],
                          "from": a["verdict"], "to": b["verdict"],
                          "claim": a["text"], "must_contain": a["must_contain"],
                          "span": a.get("quoted_terms") or "",
                          "why": b.get("quoted_terms") or ""})
    # THE EFFECT NOBODY THOUGHT TO COUNT. On this corpus the guard changes almost no
    # VERDICTS — because when it refuses a span the locator offers the next occurrence,
    # and a better one usually exists in the same document. So the guard's real output
    # here is not fewer GREENs, it is BETTER EVIDENCE under the same GREENs. A run that
    # reported only the verdict delta would have reported ~nothing and concluded the
    # guard does nothing, which is the wrong object: the verdict was never the thing
    # that was wrong. The span was.
    respanned = []
    for k, a in rows_off.items():
        b = rows_on.get(k)
        if not b or a["verdict"] != "SOURCED" or b["verdict"] != "SOURCED":
            continue
        if (a.get("quoted_terms") or "") != (b.get("quoted_terms") or ""):
            respanned.append({"file": a["file"], "line": a["line"], "claim": a["text"],
                              "was": a.get("quoted_terms") or "",
                              "now": b.get("quoted_terms") or ""})
    return {
        "total": res["off"]["total"],
        "off": {k: res["off"][k] for k in ("sourced", "refused", "unknown")},
        "on": {k: res["on"][k] for k in ("sourced", "refused", "unknown")},
        "flips": flips,
        "respanned": respanned,
        "rescued": [f for f in flips if f["to"] == "SOURCED"],
    }


# --------------------------------------------------------------------- attribution

def attribution() -> dict:
    """Which mechanism closed what, and how the coverage number behaves when swept."""
    from clearance import semantic as S
    import clear_corpus as C

    _arm(False)
    base = C.verify_corpus("research-corpus", fetch=False)
    greens = [r for r in base["rows"]
              if r["verdict"] == "SOURCED" and (r.get("quoted_terms") or "")]

    per_check = {}
    for check in S.CHECKS:
        hits = []
        for r in greens:
            f = S.inspect(r["quoted_terms"], claim=r["text"],
                          must_contain=r["must_contain"], checks=(check,))
            if f:
                hits.append({"claim": r["text"], "span": r["quoted_terms"],
                             "code": f.code, "detail": f.detail})
        per_check[check] = hits

    sweep = {}
    for th in SWEEP:
        n = sum(1 for r in greens
                if S.inspect(r["quoted_terms"], claim=r["text"],
                             must_contain=r["must_contain"], checks=("coverage",),
                             min_coverage=th) is not None)
        sweep[th] = n
    return {"greens": len(greens), "per_check": per_check, "sweep": sweep}


def main() -> int:
    print("SEMANTIC GUARD — measured both directions\n" + "=" * 74)

    g = gold()
    print(f"\nGOLD  fixtures/refusal-correctness/set.json  n={g['n']}  "
          f"labelled {g['labelled_at']}")
    print(f"  {'id':5} {'gold':14} {'guard OFF':14} {'guard ON':14}")
    for r in g["rows"]:
        mark = "" if r["on"] == r["gold"] else "   <-- WRONG"
        was = " *closed*" if r["off"] != r["on"] else ""
        print(f"  {r['id']:5} {r['gold']:14} {r['off']:14} {r['on']:14}{mark}{was}")
    print(f"  correct: guard OFF {g['correct_off']}/{g['n']}   "
          f"guard ON {g['correct_on']}/{g['n']}")
    for r in g["rows"]:
        if r["off"] != r["on"]:
            print(f"    {r['id']} refusal: {r['on_reason'][:200]}")

    a = attribution()
    print(f"\nATTRIBUTION  over the {a['greens']} GREEN verdicts the shipping engine "
          f"produces on research-corpus/")
    for check, hits in a["per_check"].items():
        print(f"  {check:9} fires on {len(hits):3}/{a['greens']}")
    print(f"  coverage threshold sweep (GREENs refused):")
    for th, n in a["sweep"].items():
        print(f"    min_coverage={th:.2f} -> {n:3}/{a['greens']}")

    r = registry()
    print(f"\nREGISTRY  research-corpus/, n={r['total']} claims, offline replay")
    print(f"  guard OFF  {r['off']}")
    print(f"  guard ON   {r['on']}")
    print(f"  verdicts changed: {len(r['flips'])}/{r['total']} "
          f"({len(r['flips']) / max(1, r['total']):.1%})")
    print(f"  refusals RESCUED to SOURCED: {len(r['rescued'])} "
          f"(must be 0 — the guard may only demote)")
    print(f"  SOURCED on a DIFFERENT span: {len(r['respanned'])}/{r['off']['sourced']} "
          f"— same verdict, better evidence")
    for i, x in enumerate(r["respanned"], 1):
        print(f"\n  (span {i}) {x['file']}:{x['line']}")
        print(f"      claim: {x['claim'][:180]}")
        print(f"      was  : {x['was'][:180]}")
        print(f"      now  : {x['now'][:180]}")
    for i, f in enumerate(r["flips"], 1):
        print(f"\n  [{i}] {f['from']} -> {f['to']}   {f['file']}:{f['line']}")
        print(f"      claim: {f['claim'][:190]}")
        print(f"      span : {f['span'][:190]}")
        print(f"      why  : {f['why'][:230]}")

    out = ROOT / "docs/EVAL-semantic-guard-2026-08-31.json"
    out.write_text(json.dumps({"gold": g, "attribution": a, "registry": r},
                              indent=1, default=str))
    print(f"\nwrote {out.relative_to(ROOT)}")
    return 0 if not r["rescued"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
