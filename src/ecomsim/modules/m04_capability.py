"""M4 - Capability resolution.

Roll P(success) at COMPLETION, not commitment. Apply obsolescence:
benefit *= max(obsolescence_floor, 1 - obsolescence_per_round * rounds_late).

See docs/07-engine-chain.md.
"""
from __future__ import annotations


def run(world, params, resolved, ctx) -> None:
    raise NotImplementedError("m04_capability: see docs/07-engine-chain.md")
