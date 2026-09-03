"""Traffic class for query analytics — human vs gate/fleet/demo.

Hosted `/popular` was polluted by gate probes and film demos (ralph loop agentic
110× measured 2026-09-03). Ranking optimization targets from that mix answers the
wrong object. Tag going forward; classify historical rows by known probe/demo lists.
"""
from __future__ import annotations

import contextlib
import contextvars
import os
import re
from typing import Optional

# Request-scoped default so dictionary → ask_registry → log_query inherits a tag
# without rewriting every call site.
_CURRENT_TRAFFIC: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "agent_science_traffic", default=None
)
_CURRENT_SUBJECT: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "agent_science_subject", default=None
)

# Explicit classes agents / scripts may set via traffic= or AGENT_SCIENCE_TRAFFIC.
CLASSES = frozenset({"human", "gate", "fleet", "demo", "unknown"})

# Exact probe strings from gate scripts / tests (re-derived from scripts, not guesswork).
GATE_PROBES = frozenset({
    "xyzzy-nonexistent-claim-99999",
    "science_lookup mcp cursor",
    "science_lookup mcp fleet",
    "science_lookup mcp fleet websearch",
    "science_lookup mcp fleet agents",
})

# Film / demo scout queries that dominate popular when loops re-run visibility.
DEMO_QUERIES = frozenset({
    "ralph loop agentic",
    "ralph loop agentic practice",
    "ralph loop",
    "ralph loop agentic coding",
    "ralph loop agentic engineering",
    "ralph loo",
    "ralph loop one unit commit",
    "geoffrey huntley ralph",
})

_GATE_SUBJECT_RE = re.compile(
    r"^(trial-|longrun-|compound-|watch-|gate-|eval-|partner-)",
    re.I,
)


def normalize_class(raw: Optional[str]) -> str:
    if not raw:
        return "unknown"
    c = str(raw).strip().lower()
    if c in CLASSES:
        return c
    # aliases
    if c in ("test", "probe", "smoke", "ci"):
        return "gate"
    if c in ("film", "scout", "wow"):
        return "demo"
    if c in ("dev", "operator", "user", "oscar"):
        return "human"
    if c in ("agent", "stack", "mcp"):
        return "fleet"
    return "unknown"


def default_from_env() -> str:
    return normalize_class(os.environ.get("AGENT_SCIENCE_TRAFFIC"))


@contextlib.contextmanager
def scoped(*, traffic: Optional[str] = None, subject: Optional[str] = None):
    """Bind traffic/subject for nested log_query calls inside this block."""
    tokens: list[tuple[contextvars.ContextVar, contextvars.Token]] = []
    if traffic is not None:
        tokens.append((_CURRENT_TRAFFIC, _CURRENT_TRAFFIC.set(traffic)))
    if subject is not None:
        tokens.append((_CURRENT_SUBJECT, _CURRENT_SUBJECT.set(subject)))
    try:
        yield
    finally:
        for var, tok in reversed(tokens):
            var.reset(tok)


def classify(
    query: str,
    *,
    traffic: Optional[str] = None,
    subject: Optional[str] = None,
) -> str:
    """Resolve traffic class. Explicit tag wins; else subject prefix; else probe lists."""
    if traffic:
        got = normalize_class(traffic)
        if got != "unknown":
            return got
    ctx = _CURRENT_TRAFFIC.get()
    if ctx:
        got = normalize_class(ctx)
        if got != "unknown":
            return got
    env = default_from_env()
    if env != "unknown":
        return env
    subj = subject if subject is not None else _CURRENT_SUBJECT.get()
    if subj and _GATE_SUBJECT_RE.match(str(subj).strip()):
        return "gate"
    qnorm = re.sub(r"\s+", " ", (query or "").strip().lower())
    if qnorm in GATE_PROBES or qnorm.startswith("xyzzy-"):
        return "gate"
    if qnorm in DEMO_QUERIES or qnorm.startswith("ralph loop"):
        return "demo"
    return "unknown"


def effective_for_row(query: str, stored: Optional[str] = None) -> str:
    """Prefer stored column; else classify historical query text."""
    if stored and normalize_class(stored) != "unknown":
        return normalize_class(stored)
    return classify(query)


def is_non_human(traffic: str) -> bool:
    return traffic in ("gate", "fleet", "demo")


def human_facing(traffic: Optional[str]) -> bool:
    """Rows that may count toward human popular (exclude gate/demo)."""
    t = normalize_class(traffic)
    return t in ("human", "unknown", "fleet")
