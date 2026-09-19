"""M13 - Experience, service & ratings.

Backlog carries forward and compounds into next round's ticket volume.
Rating converges at rating_convergence per round toward target, in both
directions. Feeds NEXT round's conversion only.

See docs/07-engine-chain.md.
"""
from __future__ import annotations


def run(world, params, resolved, ctx) -> None:
    raise NotImplementedError("m13_experience: see docs/07-engine-chain.md")
