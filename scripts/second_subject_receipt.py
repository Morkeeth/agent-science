#!/usr/bin/env python3
"""Second-subject pipeline runner — slice 4 receipt generator.

Runs the full clearance chain on dust-bowl (unrelated to orphan-works), captures
honest failures, and writes docs/SECOND-SUBJECT-RECEIPT-2026-08-29.md.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SCRIPT_A = ROOT / "fixtures/scripts/dust-bowl-A.txt"
SCRIPT_B = ROOT / "fixtures/scripts/dust-bowl-B.txt"
RECEIPT = ROOT / "docs/SECOND-SUBJECT-RECEIPT-2026-08-29.md"
SUBJECT = "dust-bowl"


def _env_blockers() -> list[str]:
    blockers = []
    gemini = Path.home() / ".config/keys/gemini.key"
    parallel = Path.home() / ".config/keys/parallel.key"
    if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY") and not gemini.exists():
        blockers.append("no Gemini credential (GEMINI_API_KEY / ~/.config/keys/gemini.key / Vertex ADC)")
    if not os.environ.get("PARALLEL_API_KEY") and not parallel.exists():
        blockers.append("no Parallel credential (PARALLEL_API_KEY / ~/.config/keys/parallel.key)")
    from clearance import instruments
    inc = instruments.document("https://rightsstatements.org/vocab/InC/1.0/")
    if not inc:
        blockers.append("instrument cache empty (cache/instruments.json has no fetched bodies)")
    return blockers


def _try_live_run() -> dict:
    import agent_science
    out = {"a": None, "b": None, "error": None}
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "corpus.db"
        log_db = Path(d) / "refusal_log.db"
        try:
            out["a"] = agent_science.clear_script(
                SCRIPT_A.read_text(), subject=SUBJECT, corpus_db=db, log_db=log_db)
            out["b"] = agent_science.clear_script(
                SCRIPT_B.read_text(), subject=SUBJECT, corpus_db=db, log_db=log_db)
        except Exception as e:
            out["error"] = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
    return out


def _offline_cross_subject_proof() -> dict:
    """Run the shipping cross-subject control as offline proof."""
    import subprocess
    r = subprocess.run(
        [sys.executable, str(ROOT / "tests/test_cross_subject_reuse.py")],
        capture_output=True, text=True, cwd=ROOT)
    return {"exit_code": r.returncode, "stdout": r.stdout, "stderr": r.stderr}


def _test_summary() -> str:
    import subprocess
    r = subprocess.run(
        [sys.executable, str(ROOT / "tests/test_watch_it_go_red.py")],
        capture_output=True, text=True, cwd=ROOT)
    lines = r.stdout.splitlines()
    summary = [l for l in lines if "passed" in l and "failed" in l]
    passed = sum(1 for l in lines if l.strip().startswith("PASS"))
    failed = sum(1 for l in lines if l.strip().startswith("FAIL"))
    crashed = r.returncode != 0 and not summary
    return (summary[-1] if summary else
            f"{passed} passed, {failed} failed" + (" (suite crashed)" if crashed else ""))


def main() -> int:
    blockers = _env_blockers()
    live = _try_live_run() if not blockers else {"skipped": True, "blockers": blockers}
    offline = _offline_cross_subject_proof()
    tests = _test_summary()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# SECOND SUBJECT RECEIPT — dust-bowl",
        "",
        f"**Date:** {now} · **Subject:** `{SUBJECT}` (unrelated to orphan-works)",
        f"**Scripts:** `{SCRIPT_A.name}` → `{SCRIPT_B.name}`",
        "",
        "## Constitution check",
        "",
        "- Verbatim span or REFUSE — pipeline unchanged",
        "- No deploy, no public repo, no secrets in env vars",
        "- Slice 1 keys/deploy: not touched",
        "",
        "## Live full chain",
        "",
    ]

    if live.get("skipped"):
        lines.append("**NOT RUN on this VM.** Blockers:")
        for b in live["blockers"]:
            lines.append(f"- {b}")
        lines += [
            "",
            "Command that would run when keys are present:",
            "",
            "```bash",
            f"python3 agent_science.py {SCRIPT_A.relative_to(ROOT)} --subject {SUBJECT}",
            f"python3 agent_science.py {SCRIPT_B.relative_to(ROOT)} --subject {SUBJECT}",
            "```",
            "",
        ]
    elif live.get("error"):
        lines.append(f"**FAILED.** {live['error']}")
    else:
        a, b = live["a"], live["b"]
        lines += [
            "| | Production A | Production B |",
            "|---|---|---|",
            f"| Claims | {a['claims_extracted']} | {b['claims_extracted']} |",
            f"| SOURCED | {a['sourced']} | {b['sourced']} |",
            f"| UNSOURCED | {a['unsourced']} | {b['unsourced']} |",
            f"| Parallel calls | {a['parallel_calls']} | {b['parallel_calls']} |",
            f"| Corpus hits | {a['corpus_hits']} | {b['corpus_hits']} |",
            f"| Log hits (cross-subject) | {a.get('log_hits', 0)} | {b.get('log_hits', 0)} |",
            "",
        ]
        gaps = [r for r in (b or {}).get("rows", []) if r.get("label") != "SOURCED"]
        if gaps:
            lines += ["### Failures named (Production B)", ""]
            for r in gaps:
                lines.append(f"- **{r['claim_id']}** — {r['label']} (`{r.get('cause')}`): {r.get('why')}")

    lines += [
        "",
        "## Offline proof — cross-subject reuse (dust-bowl ← orphan-works log)",
        "",
        f"Exit code: `{offline['exit_code']}` (0 = pass)",
        "",
        "```",
        offline["stdout"].strip() or "(no stdout)",
        "```",
        "",
        "## Controls on this VM",
        "",
        f"`python3 tests/test_watch_it_go_red.py` → **{tests}**",
        "",
        "Instrument fixtures absent on this VM; several controls are UNMEASURABLE or fail",
        "until `pull_fixtures.py` / key paths are populated.",
        "",
        "## What a stranger can do today (slice 2)",
        "",
        "```bash",
        "python3 clear_corpus.py research-corpus --backfill   # seed registry (urllib only)",
        'python3 ask_registry.py "arxiv:2511.12884"          # → SOURCED span',
        'python3 ask_registry.py "agentlint"                 # → UNSOURCED + named cause',
        "python3 ask_registry.py --browse",
        "python3 ask_registry.py --serve   # http://127.0.0.1:8091/",
        "```",
        "",
    ]

    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text("\n".join(lines), encoding="utf-8")
    print(RECEIPT.read_text())
    return 0 if offline["exit_code"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
