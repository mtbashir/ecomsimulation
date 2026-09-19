"""M16 - Research report generation.

reported = true * bias * (1 + N(0, error_band/2)), seeded on
(run_id, round, team, study_code). The seed must NOT include a purchase
counter, or teams re-buy to average out the noise.

See docs/07-engine-chain.md.
"""
from __future__ import annotations


def run(world, params, resolved, ctx) -> None:
    raise NotImplementedError("m16_research: see docs/07-engine-chain.md")
