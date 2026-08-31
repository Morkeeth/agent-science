"""C3 — the control that cannot be bypassed. Watch it go red on the shapes it misses.

WHAT HAPPENED. Two API keys sit in plaintext in a Cloud Run revision that cannot be
un-written: a rewritten, correct `deploy.sh` was already in the repo and the OLD one was
run anyway. Rotation is the only fix and it is Oscar's click.

A rule that lives in a file gets bypassed. A rule that lives in a test gets caught. That
control was built on 2026-08-30 and it catches the exact line that leaked. This file
audits it rather than rebuilding it, because the interesting question about a red light
is never "does it turn on for the case it was written from" — it is WHICH OTHER WAYS the
same thing can happen, and whether the light is wired to the switch that ships.

Two defects found, both real:

  1. THE CONTROL'S OWN CONTROL TESTED A COPY. `t_the_secret_scanner_actually_catches_one`
     declared the regex a second time, inline. Two copies of a rule are two rules: the
     copy could be repaired while the shipped one stayed broken, and the suite would
     still report green.

  2. IT ONLY SEES SINGLE-LINE SHAPES. Measured 2026-08-31 against the seven ways to hand
     a running service a secret that are collected below: the shipped rule caught 4/7 and
     MISSED 3/7 — the Cloud Run / k8s `env:` / `- name:` / `value:` block, `docker run
     -e`, and a docker-compose `environment:` list. Its body was `[^\n]*?`, which cannot
     cross a newline, so every multi-line shape was invisible to it. The first of those
     three is the DECLARATIVE FORM OF THE EXACT COMMAND THAT LEAKED, and is what
     `gcloud run services replace` consumes.

Run: python3 tests/test_secret_surfaces.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from review import secret_surfaces as S

# Every shape that hands a running service a secret in plaintext. The first is the line
# CURSOR-LOG.md records as having actually run on 2026-08-22.
LEAKS = {
    "gcloud deploy, the line that ran":
        'gcloud run deploy agent-science --set-env-vars="GEMINI_API_KEY=$(cat '
        '~/.config/keys/gemini.key),PARALLEL_API_KEY=$(cat ~/.config/keys/parallel.key)"',
    "gcloud update — same leak, different flag":
        'gcloud run services update agent-science --update-env-vars="PARALLEL_API_KEY=${K}"',
    "Cloud Run / k8s service yaml — the declarative form of the same command":
        "        env:\n        - name: PARALLEL_API_KEY\n          value: \"pk-live-abc\"",
    "docker run -e":
        "docker run -e PARALLEL_API_KEY=pk-live-abc gcr.io/hack-fleet/agent-science",
    "docker compose environment list":
        "services:\n  api:\n    environment:\n      - GEMINI_API_KEY=AIzaSyREAL",
    "Dockerfile ENV":
        "FROM python:3.12\nENV PARALLEL_API_KEY=pk-live-abc\n",
    "shell export":
        'export PARALLEL_API_KEY="$(cat ~/.config/keys/parallel.key)"',
}

SAFE = {
    "Secret Manager — the correct mechanism":
        'gcloud run deploy x --set-secrets="PARALLEL_API_KEY=parallel-api-key:latest"',
    "non-secret env vars, which deploy.sh legitimately passes":
        'gcloud run deploy x --set-env-vars="GEMINI_MODEL=gemini-3.5-flash,'
        'GCP_PROJECT=hack-fleet,CORPUS_DB=/tmp/corpus.db"',
    "k8s secretKeyRef":
        "        env:\n        - name: PARALLEL_API_KEY\n          valueFrom:\n"
        "            secretKeyRef:\n              name: parallel\n              key: k",
    "clearing env vars is the fix, not the leak":
        'gcloud run services update x --clear-env-vars --quiet',
}

passed = failed = 0


def check(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  PASS  {name}")
        passed += 1
    except AssertionError as e:
        print(f"  FAIL  {name}\n        {e}")
        failed += 1


def t_every_way_to_leak_a_secret_is_caught():
    missed = [f"{k}\n           {v.splitlines()[0][:90]}"
              for k, v in LEAKS.items() if not S.scan_text(v, name="probe")]
    assert not missed, (
        f"{len(missed)} of {len(LEAKS)} leak shapes pass the scanner:\n        - "
        + "\n        - ".join(missed))


def t_the_safe_forms_are_not_flagged():
    """A control that cries wolf gets weakened. That is how it gets bypassed."""
    wrong = [f"{k}: {[l.name for l in S.scan_text(v, name='probe')]}"
             for k, v in SAFE.items() if S.scan_text(v, name="probe")]
    assert not wrong, "false positives on the SAFE forms:\n        - " + \
        "\n        - ".join(wrong)


def t_the_live_tree_is_clean():
    leaks = S.scan_tree(ROOT)
    assert not leaks, ("a deploy surface hands a secret over in the clear; use "
                       "--set-secrets or ADC:\n        - "
                       + "\n        - ".join(l.detail for l in leaks))


def t_the_scan_actually_covers_the_deploy_surfaces():
    """A scanner that has quietly stopped looking at deploy.sh is decor."""
    names = {str(p.relative_to(ROOT)) for p in S.surfaces(ROOT)}
    for required in ("deploy.sh", "Dockerfile"):
        assert required in names, \
            f"{required} is no longer in the scanned set — the control has gone blind"
    assert len(names) >= 4, f"only {len(names)} surfaces scanned: {names}"


def t_the_scan_never_wanders_into_dependencies():
    """The scan must not flap on someone else's yaml.

    `.venv-adk/` is a real directory in this tree. It carries no yaml TODAY, so the scan
    passes by luck; one `pip install` of a package shipping a config file and this control
    starts grading a dependency and gets switched off. Bound explicitly.
    """
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / ".venv-adk/lib/site-packages/pkg").mkdir(parents=True)
        (root / ".venv-adk/lib/site-packages/pkg/conf.yaml").write_text(
            "env:\n- name: SOME_API_KEY\n  value: leaked-in-a-dependency\n")
        (root / "deploy.sh").write_text("gcloud run deploy x --set-secrets=A=b:latest\n")
        scanned = {p.name for p in S.surfaces(root)}
        assert "conf.yaml" not in scanned, \
            f"the scan reached into a virtualenv: {scanned}"
        assert "deploy.sh" in scanned, "the scan lost the real surface"
        assert not S.scan_tree(root)


def t_the_control_and_its_control_share_one_rule():
    """The defect that made this file necessary.

    Neither the scan nor any test may carry its own copy of the pattern. Both must call
    the shipped rule, or the self-test can pass while the shipped rule is broken.

    The needles are assembled from fragments so that this control does not match its own
    source — the first version did, and reported the defect against itself. A checker
    that cannot be pointed at the file it lives in is a checker that will be exempted.
    """
    needles = ("set-env-vars" + "|ENV|export", "KEY" + "|TOKEN|" + "SECRET")
    for path in sorted((ROOT / "tests").glob("test_*.py")) + [Path(__file__)]:
        src = path.read_text()
        for needle in needles:
            assert needle not in src, (
                f"{path.name} declares its own copy of the secret pattern ({needle!r}) — "
                "it must call review.secret_surfaces so the rule under test is the rule "
                "that ships")
    shipped = (ROOT / "review/secret_surfaces.py").read_text()
    assert any(n in shipped for n in needles) or "_SECRETISH" in shipped, \
        "review/secret_surfaces.py no longer defines the pattern — where did it go?"


if __name__ == "__main__":
    print("C3 — SECRET SURFACES\n")
    for n, f in list(globals().items()):
        if n.startswith("t_") and callable(f):
            check(n[2:].replace("_", " "), f)
    print(f"\n{passed} passed, {failed} failed")
    raise SystemExit(1 if failed else 0)
