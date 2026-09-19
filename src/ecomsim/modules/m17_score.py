"""M17 - Scoring & persist.

Scorecard per docs/08-scoring.md. Persist state, resolved decisions, seed and
config hash - that quadruple is what makes a round replayable.

See docs/07-engine-chain.md.
"""
from __future__ import annotations


def run(world, params, resolved, ctx) -> None:
    raise NotImplementedError("m17_score: see docs/07-engine-chain.md")
