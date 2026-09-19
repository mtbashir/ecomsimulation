"""M3 - Supply arrival & inventory.

Land arriving POs, compute opening stock, revenue-weighted instock_ratio and
stock_capacity. Lead time is drawn, not fixed.

See docs/07-engine-chain.md.
"""
from __future__ import annotations


def run(world, params, resolved, ctx) -> None:
    raise NotImplementedError("m03_supply: see docs/07-engine-chain.md")
