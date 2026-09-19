"""M12 - Customer ledger.

Per-cohort churn and frequency by ACQUISITION CHANNEL (params/channels.csv).
The deal_driven row at churn 0.44 is what makes discounting a trap.
LTV is computed from this ledger, never from averages.

See docs/07-engine-chain.md.
"""
from __future__ import annotations


def run(world, params, resolved, ctx) -> None:
    raise NotImplementedError("m12_ledger: see docs/07-engine-chain.md")
