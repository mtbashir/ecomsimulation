"""M1 - Market & seasonality. Category size is derived, never fixed."""
from __future__ import annotations

SEASON = [1.00, 1.05, 1.18, 0.92, 0.95, 1.30, 1.45, 0.88, 1.10, 1.22, 1.00, 1.15]


def run(world, params, resolved, ctx) -> None:
    n_teams = int(params["n_teams"])
    base = (n_teams * params["baseline_team_revenue"]) / params["team_share_total"]

    growth = (1 + params["category_growth_per_round"]) ** max(0, world.round - 1)

    # Seasonality flattens as round length rises; at annual rounds it is gone.
    if params["round_months"] > 3:
        season = 1.0
    else:
        raw = SEASON[(world.round - 1) % len(SEASON)]
        season = 1.0 + (raw - 1.0) * params["seasonality_amplitude"]

    world.category_size = base * growth * season * world.category_scale
    ctx["season"] = season
