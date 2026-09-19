"""M10 - Fulfilment & delivery.

Capacity overflow degrades SLA; SLA degradation raises RTO; prepaid incentive
lowers it. Forward AND reverse shipping is charged on every RTO - that single
line is what teaches COD economics.

See docs/07-engine-chain.md.
"""
from __future__ import annotations


def run(world, params, resolved, ctx) -> None:
    raise NotImplementedError("m10_fulfilment: see docs/07-engine-chain.md")
