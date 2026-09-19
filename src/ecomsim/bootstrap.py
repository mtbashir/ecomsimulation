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
    world.category_scale = _category_scale(world, params)
    return world


def _category_scale(world, params) -> float:
    """Size the category so each team's potential demand at baseline is the
    same at N=2 as at N=16, whatever the incumbent configuration.

    A fixed 'teams hold 64%' assumption breaks as soon as the small-N
    adjustment adds incumbents or damps share sensitivity. Deriving the scale
    from the actual logit at seeded state makes invariance a property of the
    construction rather than a hope.
    """
    import math
    from .modules import m07_share

    beta = params["share_sensitivity"]
    n = len(world.teams)
    if n <= 3:
        beta = min(beta, 1.4)
    elif n >= 12:
        beta = max(beta, 2.6)

    team = next(iter(world.teams.values()))
    seeded_ctx = {
        "price_index": {team.team_id: 1.0},
        "instock_ratio": {team.team_id: 1.0},
        "assortment_fit": {team.team_id: {s["code"]: 0.5 for s in params.segments}},
    }
    team_share = 0.0
    for seg in params.segments:
        u_team = m07_share._utility(team, seg, params, seeded_ctx)
        e_team = math.exp(beta * u_team)
        e_inc = sum(math.exp(beta * i["utility"]) for i in world.incumbents)
        team_share += float(seg["share"]) * e_team / (n * e_team + e_inc)

    baseline_orders = params["baseline_team_revenue"] / params["aov_base"]
    raw_category_orders = (n * params["baseline_team_revenue"] / params["team_share_total"]) / params["aov_base"]
    wanted = baseline_orders * params["potential_headroom"]
    return wanted / max(raw_category_orders * team_share, 1e-9)


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
    _seed_pipeline(team, params, active, units)
    return team


def _seed_pipeline(team, params, active, units_per_round) -> None:
    """One round of demand already on order, arriving Round 1, payable Round 1.

    Opening on-hand stock is deliberately thin (~1 week): arrivals land before
    sales in M3, so the pipeline PO serves Round 1. Together they put the
    inventory position just under the order-up-to target, so Round 1 places a
    normal-sized order and cash is smooth from the first round. A going concern
    is mid-cycle, not at a standstill.
    """
    supplier = next(s for s in params.suppliers if s["code"] == "B")
    total_weight = sum(float(s["revenue_weight"]) for s in active)
    alloc = {
        s["code"]: units_per_round * float(s["revenue_weight"]) / total_weight
        for s in active
    }
    cost = sum(
        alloc[s["code"]] * float(s["unit_cost"]) * float(supplier["cost_index"])
        * params["cogs_scale"]
        for s in active
    )
    # Two rounds in flight: a going concern on a 14-day lead and 30-day terms
    # has last month's order arriving and this month's already placed.
    for arrives in (1, 2):
        team.open_pos.append({
            "placed": arrives - 1, "arrives": arrives, "units": dict(alloc),
            "cost": cost, "supplier": "B",
        })
        team.payables[arrives] = team.payables.get(arrives, 0.0) + cost


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
