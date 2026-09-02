#!/usr/bin/env python3
"""Scrub local home paths from tracked text files. Run once, then privacy_grep.sh.

Patterns match any /Users/<name>/CODE/... path so this file itself carries no home path."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = re.compile(r"\.(png|jpg|jpeg|gif|webp)$|cache/documents\.json$|fixtures/scripts/")

REPLACEMENTS = [
    (re.compile(r"/Users/[^/\s]+/CODE/cleared"), "agent-science"),
    (re.compile(r"~/CODE/cleared"), "agent-science"),
    (re.compile(r"bash ~/CODE/cleared/"), "bash "),
    (re.compile(r"cd ~/CODE/cleared"), "cd agent-science"),
    (re.compile(r"open ~/CODE/cleared/"), "open "),
    (re.compile(r"node ~/CODE/zup/"), "node "),
    (re.compile(r"python3 ~/CODE/"), "python3 "),
    (re.compile(r"~/CODE/hack-fleet-ata"), "github.com/Morkeeth/hack-fleet-ata"),
    (re.compile(r"~/CODE/hack-agent-science"), "github.com/Morkeeth/agent-science"),
    (re.compile(r"~/CODE/agent-attack"), "github.com/Morkeeth/agent-attack"),
    (re.compile(r"~/CODE/mountain-of-helicon"), "github.com/Morkeeth/mountain-of-helicon"),
    (re.compile(r"~/CODE/zup"), "github.com/Morkeeth/zup"),
    (re.compile(r"~/CODE/aistrava"), "aistrava (external corpus)"),
    (re.compile(r"~/CODE/fleet-ops"), "fleet-ops (internal)"),
    (re.compile(r"~/CODE/flipbook"), "flipbook (sibling repo)"),
    (re.compile(r"~/CODE/voice-generation"), "voice-generation (sibling repo)"),
    (re.compile(r"~/CODE/[^\s`\"']+"), "<external-repo>"),
    (re.compile(r"/Users/[^/\s]+/CODE/[^\s`\"']+"), "<external-repo>"),
    (re.compile(r"hack-agent-science"), "agent-science"),
    (re.compile(r"Morkeeth/hack-agent-science"), "Morkeeth/agent-science"),
    (re.compile(r"vault `01 Projects/Hackathons/hack-ideation-2026-08-22.md`"), "hackathon ideation notes (2026-08-22)"),
    (re.compile(r'"cwd": "/Users/[^/\s]+/CODE/cleared"'), '"cwd": "<path-to-clone>"'),
    (re.compile(r"Repo `/Users/[^/\s]+/CODE/cleared`"), "Repo `agent-science`"),
    (re.compile(r"repo `/Users/[^/\s]+/CODE/cleared`"), "repo `agent-science`"),
    (re.compile(r"Repo `~/CODE/cleared`"), "Repo `agent-science`"),
    (re.compile(r"in `~/CODE/cleared`"), "in `agent-science`"),
    (re.compile(r"L5, Agent Science, `~/CODE/cleared`"), "L5, Agent Science, `agent-science`"),
    (re.compile(r"git clone --branch [^\s]+ ~/CODE/cleared"), "git clone --branch <branch> agent-science"),
    (re.compile(r"ingest writes into the measured population: /Users/[^/\s]+/CODE/cleared/research-corpus"),
     "ingest writes into the measured population: research-corpus"),
    (re.compile(r"PITCH\.md line 58-61, `~/CODE/hack-fleet-ata/PITCH\.md`"),
     "PITCH.md line 58-61, hack-fleet-ata PITCH.md"),
    (re.compile(r"source: `~/CODE/"), "source: `"),
    (re.compile(r"\[REPO\] ~/CODE/[^\n]+"), "[REPO] external fleet repos"),
    (re.compile(r"verified against ~/CODE/agent-attack"), "verified against agent-attack repo"),
    (re.compile(r"For: `~/CODE/hack-fleet-ata/"), "For: hack-fleet-ata "),
    (re.compile(r"`~/CODE/hack-fleet-ata/"), "`hack-fleet-ata/"),
]


def tracked_files() -> list[Path]:
    out = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True)
    paths = []
    for line in out.splitlines():
        if EXCLUDE.search(line):
            continue
        p = ROOT / line
        if p.is_file() and p.suffix in {".md", ".sh", ".py", ".txt", ".json", ".html", ".env", ".tape"}:
            try:
                p.read_bytes()[:4]
            except OSError:
                continue
            paths.append(p)
    return paths


def main() -> int:
    changed = 0
    for path in tracked_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        orig = text
        for pat, repl in REPLACEMENTS:
            text = pat.sub(repl, text)
        if text != orig:
            path.write_text(text, encoding="utf-8")
            changed += 1
            print(f"scrubbed {path.relative_to(ROOT)}")
    print(f"done — {changed} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
