"""M4 - Capability resolution.

Success is rolled at COMPLETION, not commitment: a team lives with the
uncertainty for the whole build, which is what makes buying up P(success) with
budget a real decision (docs/03 mechanism 3).
"""
from __future__ import annotations

from .. import rng

PROJECTS = {
    "recsys":       {"capex": 3_000_000, "lead": 2, "ongoing": 250_000, "p": 0.85,
                     "benefit": (0.06, 0.09), "first_available": 3, "decision": "11.1"},
    "forecasting":  {"capex": 2_200_000, "lead": 2, "ongoing": 180_000, "p": 0.80,
                     "benefit": (0.30, 0.45), "first_available": 3, "decision": "11.2"},
    "dyn_pricing":  {"capex": 3_800_000, "lead": 3, "ongoing": 300_000, "p": 0.70,
                     "benefit": (0.015, 0.030), "first_available": 3, "decision": "11.3"},
    "ai_cs":        {"capex": 1_800_000, "lead": 1, "ongoing": 120_000, "p": 0.90,
                     "benefit": (1.0, 1.0), "first_available": 3, "decision": "11.4"},
    "ai_creative":  {"capex": 1_200_000, "lead": 1, "ongoing": 90_000, "p": 0.75,
                     "benefit": (0.5, 0.5), "first_available": 3, "decision": "11.5"},
}


def run(world, params, resolved, ctx) -> None:
    for team in world.teams.values():
        _commit(team, world, ctx)
        _complete(team, world, params, ctx)
        ctx.setdefault("ongoing_tech_cost", {})[team.team_id] = sum(
            PROJECTS[c]["ongoing"] for c in team.capabilities if c in PROJECTS
        )


def _commit(team, world, ctx) -> None:
    d = ctx["resolved"][team.team_id]
    in_flight = {p["code"] for p in team.projects}
    for code, spec in PROJECTS.items():
        if code in team.capabilities or code in in_flight:
            continue
        if not d.get(spec["decision"]):
            continue
        # Capex is paid at commitment, in full, and is non-refundable.
        team.projects.append({
            "code": code, "started": world.round,
            "completes": world.round + spec["lead"], "capex": spec["capex"],
        })
        ctx.setdefault("capex", {})[team.team_id] = \
            ctx.get("capex", {}).get(team.team_id, 0.0) + spec["capex"]


def _complete(team, world, params, ctx) -> None:
    still_running = []
    for project in team.projects:
        if project["completes"] > world.round:
            still_running.append(project)
            continue

        spec = PROJECTS[project["code"]]
        success = rng.chance(spec["p"], world.run_id, world.round,
                             team.team_id, "project", project["code"])
        if not success:
            ctx.setdefault("project_failed", {}).setdefault(
                team.team_id, []).append(project["code"])
            continue

        low, high = spec["benefit"]
        draw = rng.uniform(world.run_id, world.round, team.team_id,
                           "benefit", project["code"])
        benefit = low + (high - low) * draw

        # Obsolescence: built at first availability it delivers fully; six
        # rounds later, about 60%. Early commitment under uncertainty beats late
        # commitment under certainty.
        late = max(0, world.round - spec["lead"] - spec["first_available"])
        benefit *= max(
            params["obsolescence_floor"],
            1 - params["obsolescence_per_round"] * late,
        )

        team.capabilities.add(project["code"])
        ctx.setdefault("capability_benefit", {}).setdefault(
            team.team_id, {})[project["code"]] = benefit

    team.projects = still_running
