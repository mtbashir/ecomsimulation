"""Round orchestrator.

    run_round(world, params, submissions, config) -> reports

Determinism is mandatory: the same (state, decisions, config, seed) must produce
identical output, always. That is what makes replay, golden-file testing and
dispute resolution possible (invariant I8).
"""
from __future__ import annotations

from .decisions import REGISTRY, Resolver
from .modules import PIPELINE

MEMO = "12.5"
# Not standing settings, so never carried into the next month: research and the
# memo are this month's; a stock order and an AI investment are one-off buys.
NOT_CARRIED = {"12.1", MEMO, "7.1", "11.1", "11.2", "11.3", "11.4", "11.5"}


def carry(standing: dict, submitted: dict) -> dict:
    """Last month's settings under this month's decisions.

    The price grid merges line by line: re-pricing one product this month
    leaves every other line where it was, not back at its founding price.
    """
    merged = {k: v for k, v in standing.items() if k not in NOT_CARRIED}
    for code, value in submitted.items():
        held = merged.get(code)
        if code == "1.1" and isinstance(value, dict) and isinstance(held, dict):
            grid = {c: dict(cell or {}) for c, cell in held.items()}
            for c, cell in value.items():
                grid[c] = {**grid.get(c, {}), **(cell or {})}
            merged[code] = grid
        else:
            merged[code] = value
    return merged


def run_round(world, params, submissions: dict[str, dict],
              preset: str = "advanced",
              decision_overrides: dict | None = None,
              skip: set[str] | None = None,
              open_codes: list[str] | None = None) -> dict:
    """Advance the world by one round. Mutates `world` in place.

    From the month a game's rules v2 start (world.rules_from; 1 for a new
    game), a lever a team leaves alone keeps last month's setting instead of
    returning to its default, and each month records how many of the open
    decisions the team actually took - what decision quality is marked on.
    Before that month nothing here changes, so a month already played on the
    old rules replays exactly.
    """
    world.round += 1
    skip = skip or set()

    resolver = Resolver(preset=preset, round_=world.round,
                        overrides=decision_overrides)
    v2 = world.round >= getattr(world, "rules_from", 1)
    if open_codes is None:
        open_codes = [c for c in REGISTRY if resolver.enabled(c) and resolver.unlocked(c)]
    counted = [c for c in open_codes if c != MEMO]
    resolved, decisions = {}, {}
    for tid, team in world.teams.items():
        sub = submissions.get(tid, {}) or {}
        merged = sub
        if v2:
            merged = carry(getattr(team, "standing", None) or {}, sub)
        resolved[tid] = resolver.resolve(merged)
        if v2:
            team.standing = {k: v for k, v in resolved[tid].items() if k not in NOT_CARRIED}
        decisions[tid] = {
            "taken": sum(1 for c in counted if c in sub),
            "open": len(counted),
            "memo": bool(str(sub.get(MEMO) or "").strip()),
        }
    ctx: dict = {"resolved": resolved, "decisions": decisions, "rules": 2 if v2 else 1}

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
