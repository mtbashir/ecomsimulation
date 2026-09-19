"""Round orchestrator.

    run_round(world, params, submissions, config) -> reports

Determinism is mandatory: the same (state, decisions, config, seed) must produce
identical output, always. That is what makes replay, golden-file testing and
dispute resolution possible (invariant I8).
"""
from __future__ import annotations

from .decisions import Resolver
from .modules import PIPELINE


def run_round(world, params, submissions: dict[str, dict],
              preset: str = "advanced",
              decision_overrides: dict | None = None,
              skip: set[str] | None = None) -> dict:
    """Advance the world by one round. Mutates `world` in place."""
    world.round += 1
    skip = skip or set()

    resolver = Resolver(preset=preset, round_=world.round,
                        overrides=decision_overrides)
    ctx: dict = {
        "resolved": {
            tid: resolver.resolve(submissions.get(tid, {}))
            for tid in world.teams
        }
    }

    for module in PIPELINE:
        name = module.__name__.rsplit(".", 1)[-1]
        if name in skip:
            continue
        module.run(world, params, ctx["resolved"], ctx)

    return ctx


def run_game(world, params, strategy, rounds: int | None = None,
             preset: str = "advanced", skip: set[str] | None = None) -> list[dict]:
    """Run a full game against a scripted strategy. Used by the T3 suite."""
    rounds = int(rounds or params["rounds"])
    out = []
    for _ in range(rounds):
        submissions = {
            tid: strategy(world, world.round + 1, tid) for tid in world.teams
        }
        out.append(run_round(world, params, submissions, preset=preset, skip=skip))
    return out
