"""Which engine and which scoring rules a game runs on.

The engine version moves with any change to how a month is simulated or
scored. Rule sets are what a class is told it is marked on; a game records
the month a rule set started (game.rules_from), so a change made mid-semester
applies from the next month and never rewrites a month already published.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

ENGINE_VERSION = "2.0.0"

RULES = {
    1: "Rules v1: fixed thresholds on every measure; decision quality held at 5 of 10; "
       "a lever left blank runs on its default.",
    2: "Rules v2: profitability marked against the best team in the room; decision "
       "quality from decisions taken (full marks at three-quarters of those open) and a "
       "board memo that matches them; a lever left alone keeps last month's setting.",
}
CURRENT_RULES = 2


def build() -> str:
    """The deployed commit, short. Render sets RENDER_GIT_COMMIT; locally, git."""
    sha = os.environ.get("RENDER_GIT_COMMIT", "")
    if not sha:
        try:
            sha = subprocess.run(
                ["git", "rev-parse", "HEAD"], cwd=Path(__file__).parent,
                capture_output=True, text=True, timeout=2).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            sha = ""
    return sha[:7] or "local"


def rules_label(rules_from: int | None) -> str:
    """One line for the admin footer: engine, build and the rules in force."""
    start = rules_from or 1
    rules = (f"rules v{CURRENT_RULES} from month 1" if start <= 1 else
             f"rules v{CURRENT_RULES} from month {start}; months 1–{start - 1} on v1")
    return f"Engine {ENGINE_VERSION} · build {build()} · {rules}"
