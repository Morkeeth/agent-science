#!/usr/bin/env python3
"""Qwen eval gate — every artifact claim measured at its object.

Three arms, identical scorer:

  NULL      always NOT_HELD — refuse every claim (competent silent default)
  BASELINE  believe the doc — emit doc_asserts without opening the object
  OBJECT    open the object (curl / suite / GitHub API / compound receipt)

Gold labels in fixtures/artifact-claims/set.json were written after opening
each object on label night. Re-running probes must match gold; drift fails.

The embarrassment this gate exists to catch: on a docs-heavy claim set, NULL
can beat BASELINE on accuracy when STATUS/SUBMISSION-PACK are stale. That is
not a win for silence — it is a red light on documentation honesty.

Run: python3 scripts/eval_artifact_claims.py
Offline core needs network only for hosted + GitHub probes (read-only GET).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from eval_stats import format_ci, mcnemar_exact  # noqa: E402

SET_PATH = ROOT / "fixtures/artifact-claims/set.json"
HELD, NOT_HELD = "HELD", "NOT_HELD"
UA = "agent-science-artifact-claims/1.0"


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


def _http_get(url: str, *, timeout: float = 30.0, follow: bool = True) -> tuple[int, str, str]:
    """Return (status, final_url, body_text)."""
    handlers = [] if follow else [_NoRedirect()]
    opener = urllib.request.build_opener(*handlers)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with opener.open(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return int(resp.status), str(resp.geturl()), body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return int(e.code), url, body
    except Exception as e:
        return 0, url, f"{type(e).__name__}: {e}"


def _health(host: str) -> dict:
    code, _, body = _http_get(f"{host.rstrip('/')}/health", follow=False)
    if code != 200:
        return {"_http": code, "_error": body[:200]}
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {"_http": code, "_error": "non-json", "_body": body[:200]}


def probe(item: dict, host: str) -> tuple[str, str]:
    """Return (verdict HELD|NOT_HELD, evidence string)."""
    name = item["probe"]
    args = item.get("probe_args") or {}

    if name == "hosted_health_has_key":
        h = _health(host)
        key = args["key"]
        held = key in h and h.get(key) not in (None, "")
        return (HELD if held else NOT_HELD), f"health_keys={sorted(k for k in h if not k.startswith('_'))}"

    if name == "hosted_health_ok":
        h = _health(host)
        held = h.get("ok") is True
        return (HELD if held else NOT_HELD), f"ok={h.get('ok')!r} revision={h.get('revision')!r}"

    if name == "hosted_revision_equals":
        h = _health(host)
        want = args["revision"]
        got = h.get("revision")
        return (HELD if got == want else NOT_HELD), f"revision={got!r} want={want!r}"

    if name == "hosted_partners_json":
        code, final, body = _http_get(f"{host.rstrip('/')}/partners", follow=True)
        try:
            data = json.loads(body)
            held = isinstance(data, dict) and (
                "partners_checklist" in data or "parallel" in data or "gemini" in data
            )
            return (HELD if held else NOT_HELD), f"http={code} json_keys={list(data)[:8]}"
        except json.JSONDecodeError:
            signin = "sign in" in body.lower() or "access token" in body.lower()
            return NOT_HELD, f"http={code} non-json signin={signin} final={final}"

    if name == "hosted_visibility_live_panel":
        code, final, body = _http_get(
            f"{host.rstrip('/')}/visibility/ui?q=ralph+loop", follow=True
        )
        local_only = "local-only research route" in body.lower()
        # A live panel would render angles / sourced / refuse chrome, not the local-only notice.
        live_markers = sum(
            1
            for m in ("SOURCED", "UNSOURCED", "CONTRARY", "angles", "shallow")
            if m.lower() in body.lower()
        )
        held = code == 200 and not local_only and live_markers >= 2
        return (
            HELD if held else NOT_HELD,
            f"http={code} local_only={local_only} live_markers={live_markers}",
        )

    if name == "github_repo_private":
        owner, repo = args["owner"], args["repo"]
        code, _, body = _http_get(
            f"https://api.github.com/repos/{owner}/{repo}", follow=True
        )
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return NOT_HELD, f"http={code} non-json"
        # Claim is "repo is private". HELD iff private==True.
        private = bool(data.get("private"))
        return (HELD if private else NOT_HELD), f"private={private} visibility={data.get('visibility')}"

    if name == "local_suite_count":
        script = ROOT / args["script"]
        proc = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        want_p, want_t = int(args["passed"]), int(args["total"])
        m = re.search(r"(\d+)\s+passed,\s+(\d+)\s+failed", out)
        if m:
            passed, failed = int(m.group(1)), int(m.group(2))
            total = passed + failed
        else:
            m = re.search(r"(\d+)/(\d+)\s+passed", out)
            if not m:
                return NOT_HELD, f"exit={proc.returncode} unparseable"
            passed, total = int(m.group(1)), int(m.group(2))
        held = proc.returncode == 0 and passed == want_p and total == want_t
        return (HELD if held else NOT_HELD), f"measured={passed}/{total} exit={proc.returncode}"

    if name == "offline_compound_pass":
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts/compound_exhibit_receipt.py")],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        receipt = ROOT / "docs/COMPOUND-EXHIBIT-2026-08-29.md"
        text = receipt.read_text() if receipt.exists() else ""
        # Table row: | 2 | 1 | +1 | 2 |
        m = re.search(
            r"\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*[+-]?\d+\s*\|\s*(\d+)\s*\|",
            text,
        )
        if not m:
            return NOT_HELD, f"exit={proc.returncode} no table row"
        a, b, hits = int(m.group(1)), int(m.group(2)), int(m.group(3))
        held = proc.returncode == 0 and b < a and hits >= 1
        return (HELD if held else NOT_HELD), f"A={a} B={b} corpus_hits={hits} exit={proc.returncode}"

    return NOT_HELD, f"unknown probe {name!r}"


def _score(rows: list[dict], gold: dict[str, str]) -> tuple[int, list[dict]]:
    correct = 0
    detail = []
    for row in rows:
        ok = row["label"] == gold[row["id"]]
        correct += int(ok)
        detail.append({**row, "gold": gold[row["id"]], "ok": ok})
    return correct, detail


def main() -> int:
    data = json.loads(SET_PATH.read_text())
    host = os.environ.get("AGENT_SCIENCE_HOST", data.get("host", "")).rstrip("/")
    items = data["items"]
    gold = {it["id"]: it["expected"] for it in items}
    n = len(items)

    null_rows = []
    base_rows = []
    obj_rows = []
    evidence = {}

    for it in items:
        null_rows.append({"id": it["id"], "label": NOT_HELD, "claim": it["claim"]})
        base_rows.append(
            {"id": it["id"], "label": it["doc_asserts"], "claim": it["claim"]}
        )
        verdict, ev = probe(it, host)
        evidence[it["id"]] = ev
        obj_rows.append({"id": it["id"], "label": verdict, "claim": it["claim"], "evidence": ev})

    null_c, null_d = _score(null_rows, gold)
    base_c, base_d = _score(base_rows, gold)
    obj_c, obj_d = _score(obj_rows, gold)

    def discord(a: list[dict], b: list[dict]) -> tuple[int, int]:
        # b_win = a correct & b wrong; c = a wrong & b correct
        bw = c = 0
        for x, y in zip(a, b):
            if x["ok"] and not y["ok"]:
                bw += 1
            elif (not x["ok"]) and y["ok"]:
                c += 1
        return bw, c

    print("ARTIFACT-CLAIMS EVAL — every claim at its object")
    print("NULL arm:     always NOT_HELD")
    print("BASELINE arm: believe doc_asserts (no object open)")
    print("OBJECT arm:   probe hosted/local/GitHub at runtime")
    print(f"Host: {host}")
    print(f"Set:  {SET_PATH.relative_to(ROOT)} labelled_at={data['labelled_at']}")
    print()
    print(f"{'id':<6} {'gold':<10} {'null':<10} {'baseline':<10} {'object':<10} n_ok b_ok o_ok  evidence")
    for nd, bd, od in zip(null_d, base_d, obj_d):
        print(
            f"{nd['id']:<6} {nd['gold']:<10} {nd['label']:<10} {bd['label']:<10} {od['label']:<10} "
            f"{str(nd['ok']):<4} {str(bd['ok']):<4} {str(od['ok']):<4} {evidence[nd['id']][:60]}"
        )

    print()
    print(f"NULL:      {format_ci(null_c, n)}")
    print(f"BASELINE:  {format_ci(base_c, n)}")
    print(f"OBJECT:    {format_ci(obj_c, n)}")
    print(f"Delta (object - baseline): {obj_c - base_c:+d}")
    print(f"Delta (null - baseline):   {null_c - base_c:+d}")

    bw, c = discord(base_d, obj_d)
    p, note = mcnemar_exact(bw, c)
    print(f"McNemar baseline vs object: p={p:.4f} ({note})")

    bw2, c2 = discord(base_d, null_d)
    p2, note2 = mcnemar_exact(bw2, c2)
    print(f"McNemar baseline vs null:   p={p2:.4f} ({note2})")

    # RED control must stay NOT_HELD on object arm
    red = next(r for r in obj_d if r["id"] == "AC10")
    if red["label"] != NOT_HELD:
        print("CONTROL FAIL: AC10 planted key must stay NOT_HELD — probe harness is lying")
        return 2

    if obj_c != n:
        print(f"FINDING: OBJECT arm {obj_c}/{n} — gold drift or live regression; do not tick boxes.")
        # Still a successful measurement run; exit 1 so CI notices drift
        return 1

    if null_c > base_c:
        print(
            "FINDING: NULL beats BASELINE — trusting STATUS/SUBMISSION-PACK without opening "
            "the object is worse than refusing every claim on this set."
        )
    elif base_c < obj_c:
        print(
            f"FINDING: OBJECT beats BASELINE by {obj_c - base_c} — docs disagree with objects."
        )
    else:
        print("FINDING: docs match objects on this set.")

    # false-HELD rate among gold NOT_HELD items (overclaim)
    not_held_ids = [i for i, g in gold.items() if g == NOT_HELD]
    def false_held(detail: list[dict]) -> tuple[int, int]:
        rows = [r for r in detail if r["id"] in not_held_ids]
        bad = sum(1 for r in rows if r["label"] == HELD)
        return bad, len(rows)

    for name, detail in ("NULL", null_d), ("BASELINE", base_d), ("OBJECT", obj_d):
        bad, tot = false_held(detail)
        print(f"False-HELD rate {name}: {bad}/{tot}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
