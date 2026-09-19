"""M0 - Resolve decisions.

Apply Resolver to every team's submission and write ctx['resolved'][team_id].
Validate sums and ranges; invalid submissions fall back to the prior round
with a flag raised to the instructor.

See docs/07-engine-chain.md.
"""
from __future__ import annotations


def run(world, params, resolved, ctx) -> None:
    raise NotImplementedError("m00_resolve: see docs/07-engine-chain.md")
