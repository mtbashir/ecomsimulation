"""M15 - Cash & working capital.

COD remits NEXT round; prepaid settles same round. A team growing 30% per
round on 62% COD with advance supplier terms runs out of cash while profitable.
That is the most valuable finance lesson in the sim and it falls out of timing.

See docs/07-engine-chain.md.
"""
from __future__ import annotations


def run(world, params, resolved, ctx) -> None:
    raise NotImplementedError("m15_cash: see docs/07-engine-chain.md")
