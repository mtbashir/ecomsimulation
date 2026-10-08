"""M11 - Returns (one-round lag).

Returns come from LAST round's deliveries, carrying the perception-gap
multiplier M5 queued a round earlier. Free returns raise the return rate and
also raise conversion and repeat rate - the net is genuinely ambiguous and
depends on margin, which is the point.
"""
from __future__ import annotations

from .. import mix


def run(world, params, resolved, ctx) -> None:
    for team in world.teams.values():
        tid = team.team_id
        pending = team.pending_gap_penalties.get(world.round, {})

        rate = (
            params["return_base"]
            * pending.get("return_mult", 1.0)
            * (1 + params["return_quality_coef"] * (1 - team.quality_actual))
            * ctx["return_policy_mult"][tid]
            * _sku_propensity(team, params)
        )
        rate = max(0.0, min(0.6, rate))

        returned_orders = team.delivered_prev * rate
        recovered = returned_orders * params["resell_rate"]

        ctx.setdefault("return_rate", {})[tid] = rate
        ctx.setdefault("returned_orders", {})[tid] = returned_orders
        ctx.setdefault("returns_recovered", {})[tid] = recovered

        # Set after the calculation: this round's deliveries drive next round's returns.
        team.delivered_prev = ctx["delivered"][tid]


def _sku_propensity(team, params) -> float:
    """Return propensity of what was delivered last month, by its product mix:
    a store selling more serum takes more back."""
    shares = mix.demand_shares(team, params)
    return sum(float(params.sku(c)["return_propensity"]) * s for c, s in shares.items())
