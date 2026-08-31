"""The rule that fails the build when a deploy surface hands over a secret in the clear.

ONE rule, in ONE place, imported by every control that grades it. That is not tidiness.
The version this replaces lived inside `tests/test_watch_it_go_red.py` and was declared
TWICE — once in the scan and once, inline, in the test that proves the scan works. Two
copies of a rule are two rules: the copy in the self-test could be repaired while the
shipped one stayed broken, and the suite would still report green. A control whose own
control grades a different object is the failure this whole repo is about.

WHAT IT IS FOR. Two API keys sit in plaintext in a Cloud Run revision that cannot be
un-written, because a rewritten and correct `deploy.sh` was already in the repo and the
OLD one ran anyway. Rotation is the only fix and it is Oscar's click. A rule in a file
gets bypassed; a rule in a test gets caught.

WHAT IT IS NOT FOR. It does not look for secret VALUES — no entropy heuristics, no
vendor key prefixes. It looks for a secret-shaped NAME being assigned on a surface that
ships it to a running service. That is deliberate: a value scanner has to be right about
what a key looks like, and is therefore wrong about every vendor whose format it has not
seen. A name scanner only has to be right about English, and the safe mechanisms
(`--set-secrets`, `valueFrom`/`secretKeyRef`) are structurally distinguishable from the
unsafe ones rather than distinguishable by taste.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# A NAME that looks like a secret. Kept as broad as the rule it replaces — the direction
# of error here is: flag one harmless variable and lose a minute, or miss one key and
# lose a rotation. `--set-secrets` and `valueFrom` are excluded structurally below, not
# by adding exceptions here, because an exception list is what erodes.
_SECRETISH = re.compile(r"(KEY|TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL)", re.I)
_NAME = r"[A-Za-z0-9_]+"

# gcloud flags that write PLAINTEXT env vars onto a revision. `--set-secrets`,
# `--update-secrets`, `--clear-env-vars` and `--remove-env-vars` are deliberately absent:
# they are the fix, and a scanner that flags the fix gets switched off.
_ENV_FLAG = re.compile(r"--(?:set|update|add)-env-vars[= ]", re.I)
_DOCKER_E = re.compile(r"(?:^|\s)-e[= ]\s*(" + _NAME + r")=")
_DECL = re.compile(r"^\s*(ENV|export)\s+(" + _NAME + r")\s*[= ]")
_LIST_ITEM = re.compile(r"^\s*-\s+(" + _NAME + r")=")
_YAML_NAME = re.compile(r"^\s*-?\s*name:\s*[\"']?(" + _NAME + r")[\"']?\s*$")
_ASSIGN = re.compile(r"\b(" + _NAME + r")\s*=")

# How far below `- name: X` a literal `value:` may sit and still belong to it.
_YAML_LOOKAHEAD = 4


def is_secret_name(name: str) -> bool:
    return bool(_SECRETISH.search(name or ""))


@dataclass(frozen=True)
class Leak:
    line: int
    name: str
    shape: str
    detail: str


def scan_text(text: str, *, name: str = "<text>") -> list[Leak]:
    """Every plaintext secret hand-off in one deploy surface.

    Line-oriented, with one lookahead. The rule this replaces was a single regex whose
    body was `[^\\n]*?` — it could not cross a newline, so it saw only the shapes written
    on one line. Measured against seven real ways to hand Cloud Run a secret it caught
    four and missed three, and one of the three was `env:` / `- name:` / `value:`: the
    DECLARATIVE FORM OF THE EXACT COMMAND THAT LEAKED, which is what
    `gcloud run services replace` consumes.
    """
    lines = (text or "").splitlines()
    out: list[Leak] = []

    def add(i: int, nm: str, shape: str) -> None:
        out.append(Leak(i + 1, nm, shape,
                        f"{name}:{i + 1} passes {nm} in the clear ({shape})"))

    for i, line in enumerate(lines):
        # 1. gcloud plaintext env flags. Only the flag's own argument is inspected, so a
        #    --set-secrets on the same command line is not mistaken for a leak.
        for m in _ENV_FLAG.finditer(line):
            arg = re.split(r"\s+--", line[m.end():])[0]
            for a in _ASSIGN.finditer(arg):
                if is_secret_name(a.group(1)):
                    add(i, a.group(1), "--set-env-vars")

        # 2. `docker run -e NAME=value` — same leak, no gcloud involved.
        if "docker" in line.lower():
            for m in _DOCKER_E.finditer(line):
                if is_secret_name(m.group(1)):
                    add(i, m.group(1), "docker -e")

        # 3. Dockerfile ENV / shell export: baked into the image, or into the process.
        m = _DECL.match(line)
        if m and is_secret_name(m.group(2)):
            add(i, m.group(2), m.group(1).upper())

        # 4. docker-compose `environment:` list entries.
        m = _LIST_ITEM.match(line)
        if m and is_secret_name(m.group(1)):
            add(i, m.group(1), "compose environment")

        # 5. Cloud Run / Kubernetes `env:` block. A literal `value:` is the leak; a
        #    `valueFrom:` (secretKeyRef) is the correct mechanism and must never be
        #    flagged, or the scanner punishes the fix.
        m = _YAML_NAME.match(line)
        if m and is_secret_name(m.group(1)):
            for follow in lines[i + 1:i + 1 + _YAML_LOOKAHEAD]:
                stripped = follow.strip()
                if stripped.startswith("valueFrom"):
                    break
                if stripped.startswith("value:"):
                    add(i, m.group(1), "yaml env value")
                    break
                if _YAML_NAME.match(follow):
                    break
    return out


# Directories whose contents are not ours. `.venv-adk/` is real in this tree and carries
# no yaml TODAY, so the old scan passed by luck; one `pip install` of a package shipping
# a config file and the control starts grading a dependency, flaps, and gets switched off.
VENDORED = (".git", "venv", "node_modules", "site-packages",
            "__pycache__", ".pytest_cache", "dist", "build")

SURFACE_SUFFIXES = (".sh", ".yaml", ".yml", ".tf")
SURFACE_NAMES = ("Dockerfile", "cloudbuild.yaml", "Procfile", "Makefile",
                 "docker-compose.yml", "docker-compose.yaml")


def surfaces(root: Path) -> list[Path]:
    """The files that can actually ship a secret to a running service.

    A named set, not `grep -r`: a repo-wide grep would match this module, its tests and
    the docs describing the incident, and the only way to keep it green would be to
    weaken the pattern.
    """
    out = []
    for f in Path(root).rglob("*"):
        if not f.is_file():
            continue
        if any(p.startswith(".venv") or p in VENDORED for p in f.parts):
            continue
        if f.suffix in SURFACE_SUFFIXES or f.name in SURFACE_NAMES:
            out.append(f)
    return sorted(out)


def scan_tree(root: Path) -> list[Leak]:
    root = Path(root)
    found = []
    for f in surfaces(root):
        found += scan_text(f.read_text(errors="ignore"), name=str(f.relative_to(root)))
    return found


if __name__ == "__main__":
    import sys
    leaks = scan_tree(Path(__file__).resolve().parents[1])
    for l in leaks:
        print(l.detail)
    print(f"{len(leaks)} plaintext secret hand-off(s)")
    sys.exit(1 if leaks else 0)
