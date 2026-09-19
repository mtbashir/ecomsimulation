"""M2 - Events.

Apply Type A/B/C events from docs/09-event-library.md. Events modify
PARAMETERS only - never a team's P&L. Severity scales as
1 + (mult - 1) * event_severity.

See docs/07-engine-chain.md.
"""
from __future__ import annotations


def run(world, params, resolved, ctx) -> None:
    raise NotImplementedError("m02_events: see docs/07-engine-chain.md")
