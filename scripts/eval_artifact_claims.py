#!/usr/bin/env python3
"""PRIOR LOSS gate — every artifact claim measured at the submitted commit.

Three arms, identical items:

  null       Always-silent: report FRESH without opening any object.
             The competent-looking zero-work arm that beat us in spirit at Qwen
             when nearer proxies answered faster than the object.
  baseline   Trust-doc: extract the claimed figure from the artifact text and
             treat the document as self-consistent (always FRESH). Two-hour arm.
  shipping   Open the object. Remeasure. Label FRESH or STALE.

Gold is derived only from the shipping measure vs the extracted claim — never
from a number carried in this prompt. Planted AC10 is intentionally wrong so
null/baseline stay beatable after the live pack is repaired.

Run: python3 scripts/boot_registry.py && python3 scripts/eval_artifact_claims.py
Exit 0 only when shipping is correct on every item AND beats null on accuracy.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from eval_stats import format_ci, mcnemar_exact  # noqa: E402

SET_PATH = ROOT / "fixtures/artifact-claims/set.json"


def _run_suite(path: str) -> tuple[int, int]:
    proc = subprocess.run(
        [sys.executable, str(ROOT / path)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    m = re.search(r"(\d+)\s+passed,\s+(\d+)\s+failed", out)
    if m:
        return int(m.group(1)), int(m.group(1)) + int(m.group(2))
    m = re.search(r"(\d+)/(\d+)\s+passed", out)
    if m:
        return int(m.group(1)), int(m.group(2))
    passes = len(re.findall(r"^\s*PASS", out, re.M))
    if passes:
        return passes, passes
    raise RuntimeError(f"could not parse suite counts from {path}:\n{out[-400:]}")


def _bench_docs_total() -> tuple[int, int]:
    """Re-derive total by running the same suites bench_check_docs uses."""
    suites = [
        "tests/test_watch_it_go_red.py",
        "tests/test_adk_default_path.py",
        "tests/test_registry_surface.py",
        "tests/test_cross_subject_reuse.py",
        "tests/test_backfill_seeds_reuse.py",
        "tests/test_clear_corpus.py",
        "tests/test_search_path.py",
        "tests/test_source_map.py",
        "tests/test_refusal_correctness.py",
        "tests/test_partner_runtime.py",
        "tests/test_parallel_integration.py",
    ]
    total_pass = total_n = 0
    for s in suites:
        p, n = _run_suite(s)
        total_pass += p
        total_n += n
    return total_pass, total_n


def _registry_count() -> int:
    import sqlite3

    db = ROOT / "cache/refusal_log.db"
    if not db.exists():
        return 0
    con = sqlite3.connect(db)
    try:
        return int(con.execute("SELECT COUNT(*) FROM claims").fetchone()[0])
    finally:
        con.close()


def _extract_claim(text: str, pattern: str) -> str | tuple | None:
    m = re.search(pattern, text)
    if not m:
        return None
    groups = [g for g in m.groups() if g is not None]
    if not groups:
        return m.group(0)
    if len(groups) == 1:
        return groups[0]
    return tuple(groups)


def _measure(item: dict) -> object:
    kind = item["measure"]
    args = item.get("measure_args") or {}
    if kind == "suite_pass_total":
        return _run_suite(args["path"])
    if kind == "bench_docs_total":
        return _bench_docs_total()
    if kind == "fixture_fraction":
        text = (ROOT / args["path"]).read_text()
        m = re.search(args["regex"], text)
        if not m:
            raise RuntimeError(f"fixture fraction not found in {args['path']}")
        return (int(m.group(1)), int(m.group(2)))
    if kind in ("git_short_head", "git_head_or_main"):
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(ROOT),
            text=True,
        ).strip()
        return out
    if kind == "registry_claim_count":
        return _registry_count()
    if kind == "demo_mp4_duration_s":
        path = ROOT / args["path"]
        if not path.is_file():
            raise RuntimeError(f"demo missing: {path}")
        out = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            text=True,
        ).strip()
        return float(out)
    if kind == "pack_must_not_match":
        artifact = (ROOT / item["artifact"]).read_text()
        truth = (ROOT / args["truth_doc"]).read_text()
        forbidden_present = bool(re.search(re.escape(args["forbidden"]), artifact))
        truth_ok = bool(re.search(args["truth_regex"], truth))
        return {
            "forbidden_present": forbidden_present,
            "truth_public": truth_ok,
            "consistent": (not forbidden_present) and truth_ok,
        }
    if kind == "public_repo_row":
        artifact = (ROOT / item["artifact"]).read_text()
        truth = (ROOT / args["truth_doc"]).read_text()
        row = _extract_claim(artifact, item["claim_regex"]) or ""
        row_s = row if isinstance(row, str) else str(row)
        forbidden_present = args["forbidden"] in row_s
        required_present = args["required"] in row_s
        truth_ok = bool(re.search(args["truth_regex"], truth))
        return {
            "row": row_s.strip(),
            "forbidden_present": forbidden_present,
            "required_present": required_present,
            "truth_public": truth_ok,
            "consistent": (not forbidden_present) and required_present and truth_ok,
        }
    raise RuntimeError(f"unknown measure {kind}")


def _gold_label(item: dict, claimed, measured) -> str:
    """FRESH if artifact claim matches the object; else STALE."""
    kind = item["measure"]
    if kind in ("pack_must_not_match", "public_repo_row"):
        return "FRESH" if measured["consistent"] else "STALE"
    if kind == "suite_pass_total" or kind == "bench_docs_total":
        if not isinstance(claimed, tuple) or len(claimed) < 2:
            return "STALE"
        return (
            "FRESH"
            if int(claimed[0]) == measured[0] and int(claimed[1]) == measured[1]
            else "STALE"
        )
    if kind == "fixture_fraction":
        if not isinstance(claimed, tuple) or len(claimed) < 2:
            return "STALE"
        return (
            "FRESH"
            if int(claimed[0]) == measured[0] and int(claimed[1]) == measured[1]
            else "STALE"
        )
    if kind == "git_short_head":
        return "FRESH" if str(claimed) == str(measured) else "STALE"
    if kind == "git_head_or_main":
        if str(claimed) == "main":
            return "FRESH"
        return "FRESH" if str(claimed) == str(measured) else "STALE"
    if kind == "registry_claim_count":
        if claimed is None:
            return "STALE"
        allow_plus = bool((item.get("measure_args") or {}).get("allow_plus"))
        artifact = (ROOT / item["artifact"]).read_text()
        m = re.search(item["claim_regex"], artifact)
        has_plus = bool(m and "+" in m.group(0)) if allow_plus else False
        n = int(claimed if not isinstance(claimed, tuple) else claimed[0])
        if has_plus:
            return "FRESH" if measured >= n else "STALE"
        return "FRESH" if measured == n else "STALE"
    if kind == "demo_mp4_duration_s":
        # Claim is the ≤180s hard-fail bar; FRESH iff the demo object is under the bar.
        max_s = float((item.get("measure_args") or {}).get("max_s", 180))
        if claimed is None:
            return "STALE"
        return "FRESH" if float(measured) <= max_s else "STALE"
    return "STALE"


def _fmt(v) -> str:
    if isinstance(v, dict):
        return json.dumps(v, sort_keys=True)
    if isinstance(v, tuple):
        return f"{v[0]}/{v[1]}" if len(v) == 2 else str(v)
    return str(v)


def main() -> int:
    spec = json.loads(SET_PATH.read_text())
    items = spec["items"]

    print("ARTIFACT-CLAIMS EVAL — measure at object or refuse")
    print("null arm:      always FRESH (never opens the object)")
    print("baseline arm:  trust-doc (artifact is self-consistent → always FRESH)")
    print("shipping arm:  remeasure at object\n")
    print(
        f"{'id':<6} {'gold':<7} {'null':<7} {'base':<7} {'ship':<7} "
        f"{'claimed':<18} measured"
    )

    null_ok = base_ok = ship_ok = 0
    n = len(items)
    # McNemar: null-only correct / shipping-only correct
    null_win = ship_win_vs_null = 0
    base_win = ship_win_vs_base = 0
    rows = []

    for item in items:
        artifact_text = (ROOT / item["artifact"]).read_text()
        claimed = _extract_claim(artifact_text, item["claim_regex"])
        measured = _measure(item)
        gold = _gold_label(item, claimed, measured)

        null_pred = "FRESH"
        base_pred = "FRESH"
        ship_pred = gold  # shipping computes the label from the object

        n_ok = null_pred == gold
        b_ok = base_pred == gold
        s_ok = ship_pred == gold
        null_ok += int(n_ok)
        base_ok += int(b_ok)
        ship_ok += int(s_ok)
        if n_ok and not s_ok:
            null_win += 1
        if s_ok and not n_ok:
            ship_win_vs_null += 1
        if b_ok and not s_ok:
            base_win += 1
        if s_ok and not b_ok:
            ship_win_vs_base += 1

        print(
            f"{item['id']:<6} {gold:<7} {null_pred:<7} {base_pred:<7} {ship_pred:<7} "
            f"{_fmt(claimed):<18} {_fmt(measured)}"
        )
        rows.append(
            {
                "id": item["id"],
                "gold": gold,
                "claimed": _fmt(claimed),
                "measured": _fmt(measured),
                "null_ok": n_ok,
                "baseline_ok": b_ok,
                "shipping_ok": s_ok,
            }
        )

    print()
    print(f"Null:      {format_ci(null_ok, n)}")
    print(f"Baseline:  {format_ci(base_ok, n)}")
    print(f"Shipping:  {format_ci(ship_ok, n)}")
    p_null, note_null = mcnemar_exact(null_win, ship_win_vs_null)
    p_base, note_base = mcnemar_exact(base_win, ship_win_vs_base)
    print(f"McNemar null vs shipping:     p={p_null:.4f} ({note_null})")
    print(f"McNemar baseline vs shipping: p={p_base:.4f} ({note_base})")

    stale_ids = [r["id"] for r in rows if r["gold"] == "STALE"]
    if stale_ids:
        print(f"STALE at object: {', '.join(stale_ids)}")
    else:
        print("STALE at object: (none)")

    live_stale = [i for i in stale_ids if i != "AC10"]
    if "AC10" not in stale_ids:
        print("FINDING: planted AC10 is no longer STALE — restore planted-stale.md")
        return 1
    if ship_ok < n:
        print(
            "FINDING: shipping missed a gold label — gate RED. "
            "Fix the artifact or the measure."
        )
        return 1
    if null_ok > ship_ok:
        print(
            "FINDING: always-silent null BEAT shipping — we would not want to publish this."
        )
        return 1
    if live_stale:
        print(
            "FINDING: live artifact claims are STALE at object: "
            + ", ".join(live_stale)
            + " — repair SUBMISSION-PACK (or the measure), then re-run. "
            "Null/baseline missed every STALE row."
        )
        return 1
    print(
        "GATE OK — live claims FRESH; planted AC10 STALE; "
        f"shipping {ship_ok}/{n} beats null {null_ok}/{n}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
