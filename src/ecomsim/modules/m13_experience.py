"""M13 - Experience, service & ratings.

Backlog carries forward and compounds into next round's ticket volume: a service
problem ignored for two rounds is not twice as bad, it is considerably worse.

Ratings converge at rating_convergence per round in BOTH directions, and feed
only the NEXT round's conversion. Reputation is slow to build and slow to lose.
"""
from __future__ import annotations


def run(world, params, resolved, ctx) -> None:
    for team in world.teams.values():
        tid = team.team_id
        d = ctx["resolved"][tid]

        tickets = (
            ctx["orders"][tid] * params["ticket_rate"]
            + team.cs_backlog
            + ctx["returned_orders"][tid] * params["backlog_return_coef"]
        )
        agents = int(d.get("10.1", team.cs_agents) or team.cs_agents)
        team.cs_agents = agents
        capacity = agents * params["agent_capacity"] * params["round_months"]
        if "ai_cs" in team.capabilities:
            capacity *= params["ai_cs_multiplier"]

        team.cs_backlog = max(0.0, tickets - capacity)
        sla_hit = max(0.0, min(1.0, 1 - team.cs_backlog / max(tickets, 1.0)))

        pending = team.pending_gap_penalties.get(world.round, {})
        target = (
            params["rating_base"]
            + params["rating_aq_coef"] * team.quality_actual
            + params["rating_adr_coef"] * team.delivery_actual
            + params["rating_sla_coef"] * sla_hit
            + params["rating_pack_coef"] * ctx["packaging"][tid]
            - pending.get("rating", 0.0)
        )
        target = max(1.0, min(5.0, target))
        team.rating += params["rating_convergence"] * (target - team.rating)

        team.nps = (
            100 * (0.42 * (team.rating - 3) + 0.30 * sla_hit
                   + 0.28 * team.delivery_actual) - 20
        )

        # Experience failure feeds NEXT round's churn (M12 reads this from ctx,
        # so it lands one round later by construction).
        ctx.setdefault("experience_penalty", {})[tid] = max(
            0.0, (4.0 - team.rating) / 2.0
        )
        ctx.setdefault("retention_effect", {})[tid] = min(
            1.0, (float(d.get("6.1", 0) or 0) / 400_000) ** 0.5
        )
        ctx.setdefault("cs_backlog", {})[tid] = team.cs_backlog
        ctx.setdefault("sla_hit", {})[tid] = sla_hit
        ctx.setdefault("rating", {})[tid] = team.rating
        ctx.setdefault("nps", {})[tid] = team.nps
        ctx.setdefault("cs_cost", {})[tid] = agents * params["cs_cost_per_agent"]
