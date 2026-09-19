"""Build a world at Round 0.

`going_concern` seeds every team identically, which is what calibration needs:
an identical start isolates decision effects from founding-configuration effects
(docs/05-start-mode.md). `founding` layers Round 0 on top of this.
"""
from __future__ import annotations

from .state import Cohort, TeamState, WorldState


def new_world(params, n_teams: int | None = None, run_id: str = "run") -> WorldState:
    n_teams = int(n_teams or params["n_teams"])
    world = WorldState(run_id=run_id)
    world.teams = {
        f"team_{i + 1:02d}": new_team(params, f"team_{i + 1:02d}")
        for i in range(n_teams)
    }
    world.incumbents = [
        {"id": "inc_a", "name": "Price leader", "utility": params["incumbent_a_utility"]},
        {"id": "inc_b", "name": "Premium/service", "utility": params["incumbent_b_utility"]},
    ]
    # A duopoly under a plain logit is a tug-of-war; teams need a field to
    # compete against rather than only each other (docs/04).
    if n_teams <= 3:
        world.incumbents += [
            {"id": "inc_c", "name": "Value challenger", "utility": 0.44},
            {"id": "inc_d", "name": "Niche premium", "utility": 0.41},
        ]
    world.market_avg_aov = params["aov_base"]
    world.market_avg_price = params["aov_base"] / params["units_per_order"]
    return world


def new_team(params, team_id: str) -> TeamState:
    team = TeamState(team_id=team_id, cash=params["starting_cash"])

    active = _active_skus(params)
    team.active_skus = [s["code"] for s in active]

    # Opening stock at the configured weeks of cover.
    baseline_orders = params["baseline_team_revenue"] / params["aov_base"]
    units = baseline_orders * params["units_per_order"]
    weeks = params["starting_inventory_weeks"]
    total_weight = sum(float(s["revenue_weight"]) for s in active)
    for sku in active:
        share = float(sku["revenue_weight"]) / total_weight
        team.inventory[sku["code"]] = units * share * (weeks / 4.33)

    team.cohorts = _seed_cohorts(params)
    return team


def _active_skus(params) -> list[dict]:
    """The highest-revenue-weight SKUs, so the baseline basket is representative."""
    ranked = sorted(params.skus, key=lambda s: -float(s["revenue_weight"]))
    return ranked[: int(params["active_sku_count"])]


def _seed_cohorts(params) -> list[Cohort]:
    """Seed the customer base with a realistic channel mix.

    Channel matters, not just size: a base acquired through TikTok churns at
    more than twice the rate of one acquired organically (docs/07 M12).
    """
    mix = {
        "organic": 0.26, "google_search": 0.14, "meta": 0.34,
        "tiktok": 0.12, "influencer": 0.09, "marketplace": 0.05,
    }
    total = params["starting_active_customers"]
    cohorts: list[Cohort] = []
    for code, share in mix.items():
        ch = params.channel(code if code != "marketplace" else "marketplace_ads")
        cohorts.append(Cohort(
            acquired_round=0,
            channel=code,
            active=total * share,
            churn_base=float(ch["churn_base"]),
            freq=float(ch["freq_per_round"]),
        ))
    return cohorts
