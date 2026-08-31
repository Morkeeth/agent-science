#!/usr/bin/env python3
"""Measure the citation check. Three arms, two populations, or it is not a measurement.

    python3 scripts/eval_citation_conflict.py

WHY THREE ARMS. The mechanism has two possible gates and only one of them ships:

  BASE      polarity only — the engine as it shipped 2026-08-31 04:00
  CONFLICT  + the carrier clause cites a RIVAL provision with the same head noun
  ABSENCE   + the span never names the claim's provision at all

ABSENCE is the tempting one and it is the one this repo has been burned by twice:
`binding` and `coverage` were both built, measured and CUT as gates because they refuse
ordinary prose whose subject sits in the previous sentence. So the absence arm is built,
run, and its cost printed here — and it does not ship unless this number says it should.
A gate argued for rather than measured would be the one unforgivable commit in this repo.

POPULATIONS
  GOLD      fixtures/refusal-correctness/set.json, n=6, labelled 2026-08-22 BEFORE any
            engine run. The only population here with a right answer. A new gate that
            moves this number is rejected outright.
  REGISTRY  every claim in research-corpus/, re-cleared offline against the document
            cache — the population the shipped registry was built from. UNLABELLED, so
            every changed verdict is PRINTED IN FULL for a human to adjudicate. A count
            of flips is not a count of defects closed and this script never calls it one.
  WEDGE     the one case the mechanism was built for, run through judge_claim against
            the live-fetched regulation. Both directions: the false claim must refuse and
            the true claim must clear. Needs network; skipped and SAID SO when offline.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from clearance import semantic as S  # noqa: E402

BASE = ("polarity",)
CONFLICT = ("polarity", "citation")
ARMS = {"BASE": BASE, "CONFLICT": CONFLICT, "ABSENCE": CONFLICT}


class arm:
    """Swap the process-default checks (and, for ABSENCE, the citation gate) in place.

    The engine reads DEFAULT_CHECKS at every verify() call site, so this reconfigures
    all three doors into GREEN at once. Restoring in `finally` is not politeness: an
    arm that leaked would make every later arm measure the wrong engine.
    """

    def __init__(self, name: str):
        self.name, self.checks = name, ARMS[name]

    def __enter__(self):
        self._saved = S.DEFAULT_CHECKS
        self._fn = S._BY_NAME["citation"]
        S.DEFAULT_CHECKS = self.checks
        if self.name == "ABSENCE":
            base = self._fn
            S._BY_NAME["citation"] = (
                lambda p, **kw: base(p, **{**kw, "gate_absence": True}))
        return self

    def __exit__(self, *exc):
        S.DEFAULT_CHECKS = self._saved
        S._BY_NAME["citation"] = self._fn
        return False


# ------------------------------------------------------------------ gold population

def gold() -> dict:
    from clearance import instruments
    from clearance.facts import Claim, judge_claim
    from clearance.verdict import GREEN

    SET = json.loads((ROOT / "fixtures/refusal-correctness/set.json").read_text())
    out = {"n": len(SET["items"]), "labelled_at": SET["labelled_at"], "rows": []}
    saved = instruments.document
    for it in SET["items"]:
        body = (ROOT / it["document"]).read_text()
        url = f"fixture://{it['id']}"

        def fake(u, fetch=False, _b=body, _u=url):
            return _b if u == _u else saved(u, fetch=fetch)

        row = {"id": it["id"], "gold": it["expected"]}
        instruments.document = fake
        try:
            for name in ARMS:
                with arm(name):
                    v = judge_claim(Claim(it["id"], it["claim"], url,
                                          it["must_contain"]), semantic=True)
                row[name] = "SUPPORTED" if v.verdict == GREEN else "NOT_SUPPORTED"
                row[name + "_code"] = v.refusal_code or ""
        finally:
            instruments.document = saved
        out["rows"].append(row)
    for name in ARMS:
        out["correct_" + name] = sum(r[name] == r["gold"] for r in out["rows"])
    return out


# -------------------------------------------------------------- registry population

def registry() -> dict:
    """Re-clear research-corpus/ in every arm, offline, from the document cache."""
    import clear_corpus as C

    res = {}
    for name in ARMS:
        with arm(name):
            res[name] = C.verify_corpus("research-corpus", fetch=False)
    key = lambda r: (r["file"], r["line"])  # noqa: E731
    base = {key(r): r for r in res["BASE"]["rows"]}

    out = {"total": res["BASE"]["total"],
           "counts": {n: {k: res[n][k] for k in ("sourced", "refused", "unknown")}
                      for n in ARMS},
           "flips": {}}
    for name in ("CONFLICT", "ABSENCE"):
        rows = {key(r): r for r in res[name]["rows"]}
        flips = []
        for k, a in base.items():
            b = rows.get(k)
            if b and a["verdict"] != b["verdict"]:
                flips.append({"file": a["file"], "line": a["line"], "claim": a["text"],
                              "from": a["verdict"], "to": b["verdict"],
                              "was_span": a.get("quoted_terms") or "",
                              "why": b.get("quoted_terms") or ""})
        out["flips"][name] = flips
    return out


# --------------------------------------------------------------------- attribution

def attribution() -> dict:
    """How many of the shipping engine's GREEN spans does each arm of the check refuse?

    Run over the spans the BASE engine actually produced, so the number is a cost in
    real cleared claims, not a rate on a fixture.
    """
    import clear_corpus as C

    with arm("BASE"):
        base = C.verify_corpus("research-corpus", fetch=False)
    greens = [r for r in base["rows"]
              if r["verdict"] == "SOURCED" and (r.get("quoted_terms") or "")]
    cites = [r for r in greens if S.provisions(r["text"])]

    hits = {"CONFLICT": [], "ABSENCE": []}
    for r in cites:
        for name, absent in (("CONFLICT", False), ("ABSENCE", True)):
            f = S.check_citation(r["quoted_terms"], claim=r["text"],
                                 must_contain=r["must_contain"], gate_absence=absent)
            if f is not None:
                hits[name].append({"claim": r["text"], "span": r["quoted_terms"],
                                   "code": f.code, "detail": f.detail})
    return {"greens": len(greens), "cite_a_provision": len(cites), "hits": hits}


# --------------------------------------------------------------------------- wedge

def wedge() -> dict:
    from clearance import instruments, wedge as W
    from clearance.facts import Claim, judge_claim

    body = instruments.document(W.URL, fetch=True)
    if not body:
        return {"skipped": "no network and no cached document for the exhibit"}
    out = {"document_chars": len(body), "cases": []}
    for c in W.CASES:
        with arm("CONFLICT"):
            v = judge_claim(Claim(c.case_id, c.claim, W.URL, c.must_contain), fetch=True)
        with arm("BASE"):
            b = judge_claim(Claim(c.case_id, c.claim, W.URL, c.must_contain), fetch=True)
        out["cases"].append({
            "id": c.case_id, "expect": c.expect, "base": b.verdict, "ships": v.verdict,
            "code": v.refusal_code or "", "trail": len(v.trail),
            "ok": (v.verdict == "GREEN") == (c.expect == "SOURCED")})
    return out


def main() -> int:
    print("THE CITATION CHECK — three arms, measured\n" + "=" * 76)

    g = gold()
    print(f"\nGOLD  fixtures/refusal-correctness/set.json  n={g['n']}  "
          f"labelled {g['labelled_at']}")
    print(f"  {'id':5} {'gold':15} " + " ".join(f"{n:15}" for n in ARMS))
    for r in g["rows"]:
        print(f"  {r['id']:5} {r['gold']:15} "
              + " ".join(f"{r[n]:15}" for n in ARMS)
              + ("   <-- moved" if len({r[n] for n in ARMS}) > 1 else ""))
    for n in ARMS:
        print(f"  correct {n:9} {g['correct_' + n]}/{g['n']}")

    a = attribution()
    print(f"\nATTRIBUTION  over the {a['greens']} GREEN verdicts the BASE engine "
          f"produces on research-corpus/,")
    print(f"             {a['cite_a_provision']} of which cite a provision at all")
    for name, hits in a["hits"].items():
        print(f"  {name:9} would refuse {len(hits)} of those {a['cite_a_provision']}")
        for h in hits[:8]:
            print(f"      claim: {h['claim'][:96]}")
            print(f"      why  : {h['detail'][:150]}")

    r = registry()
    print(f"\nREGISTRY  research-corpus/, {r['total']} claims, offline, doc cache")
    for n in ARMS:
        c = r["counts"][n]
        print(f"  {n:9} sourced {c['sourced']:4}  refused {c['refused']:4}  "
              f"unknown {c['unknown']:4}")
    for name in ("CONFLICT", "ABSENCE"):
        fl = r["flips"][name]
        print(f"  {name} changes {len(fl)} verdict(s) vs BASE"
              + (":" if fl else " — the corpus does not exercise it"))
        for f in fl[:10]:
            print(f"      {f['from']} -> {f['to']}  {f['claim'][:88]}")
            print(f"      why: {f['why'][:170]}")

    w = wedge()
    print("\nWEDGE  the case the mechanism was built for, via judge_claim, live document")
    if w.get("skipped"):
        print(f"  SKIPPED — {w['skipped']}")
    else:
        print(f"  document: {w['document_chars']:,} characters fetched")
        for c in w["cases"]:
            print(f"  {c['id']:6} expect {c['expect']:10} BASE {c['base']:8} "
                  f"SHIPS {c['ships']:8} {c['code']:26} "
                  f"trail={c['trail']}  {'OK' if c['ok'] else 'WRONG'}")

    out = {"gold": g, "attribution": a, "registry": r, "wedge": w}
    dest = ROOT / "docs/EVAL-citation-conflict-2026-08-31.json"
    dest.write_text(json.dumps(out, indent=1))
    print(f"\nwritten: {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
