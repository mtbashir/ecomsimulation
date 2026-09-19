"""M11 - Returns (one-round lag).

returns[t] = delivered[t-1] * return_rate, where return_rate carries the
perception-gap multiplier queued by M5 one round earlier.

See docs/07-engine-chain.md.
"""
from __future__ import annotations


def run(world, params, resolved, ctx) -> None:
    raise NotImplementedError("m11_returns: see docs/07-engine-chain.md")
