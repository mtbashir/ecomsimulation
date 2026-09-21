"""Build a world at Round 0.

`going_concern` seeds every team identically, which is what calibration needs:
an identical start isolates decision effects from founding-configuration effects
(docs/05-start-mode.md). `founding` layers Round 0 on top of this.
"""
from __future__ import annotations

from .state import Cohort, TeamState, WorldState


AI_ROSTER = [
    ("inc_a", "Price leader", "incumbent_a_utility"),
    ("inc_b", "Premium/service", "incumbent_b_utility"),
    ("inc_c", "Value challenger", 0.44),
    ("inc_d", "Niche premium", 0.41),
    ("inc_e", "Regional generalist", 0.47),
    ("inc_f", "Marketplace native", 0.43),
]


def new_world(params, n_teams: int | None = None, run_id: str = "run",
              ai_competitors: int | None = None,
              ai_aggression: float | None = None) -> WorldState:
    n_teams = int(n_teams or params["n_teams"])
    world = WorldState(run_id=run_id)
    world.teams = {
        f"team_{i + 1:02d}": new_team(params, f"team_{i + 1:02d}")
        for i in range(n_teams)
    }

    # How crowded the market is, is the instructor's call. A duopoly under a
    # plain logit is a tug-of-war, so at small N the floor rises: teams need a
    # field to compete against rather than only each other (docs/04).
    count = int(ai_competitors if ai_competitors is not None else 2)
    if n_teams <= 3:
        count = max(count, 4)
    count = max(1, min(len(AI_ROSTER), count))

    aggression = params["incumbent_aggression"] if ai_aggression is None else ai_aggression
    tilt = (aggression - 0.5) * 0.30   # aggressive incumbents are harder to beat

    world.incumbents = []
    for ident, label, utility in AI_ROSTER[:count]:
        base = params[utility] if isinstance(utility, str) else utility
        world.incumbents.append(
            {"id": ident, "name": label, "utility": max(0.05, base + tilt)})
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
    # Scale against a FIXED reference field - two incumbents at base utility -
    # not against the actual one. Scaling against the actual field made the
    # incumbents cancel themselves out exactly: more of them shrank each team's
    # share, and the scale grew the category to compensate. They did nothing.
    # Holding the reference fixed keeps per-team economics N-invariant (T2
    # needs that) while letting a crowded market actually cost a team share.
    # The reference field carries the floor the engine forces at small N, not a
    # flat two. Below four teams the roster is padded to four incumbents so a
    # duopoly is not a tug-of-war; scaling against two while the team actually
    # faced four charged it for a floor it did not ask for, and left N=2 and
    # N=3 short of the baseline while every larger game sat on it. Anything the
    # instructor adds ON TOP of the floor still costs share, which is the point
    # of holding the reference fixed.
    floor = 4 if n <= 3 else 2
    reference = [
        {"utility": params[u] if isinstance(u, str) else u}
        for _, _, u in AI_ROSTER[:floor]
    ]
    seeded_ctx = {
        "price_index": {team.team_id: 1.0},
        "instock_ratio": {team.team_id: 1.0},
        "assortment_fit": {team.team_id: {s["code"]: 0.5 for s in params.segments}},
    }
    team_share = 0.0
    for seg in params.segments:
        u_team = m07_share._utility(team, seg, params, seeded_ctx)
        e_team = math.exp(beta * u_team)
        e_inc = sum(math.exp(beta * i["utility"]) for i in reference)
        team_share += float(seg["share"]) * e_team / (n * e_team + e_inc)

    # Category sizing targets the acquisition pool: repeat demand is added on
    # top in M7, so only the new-customer share is competed for here.
    baseline_orders = (params["baseline_team_revenue"] / params["aov_base"]) * 0.78
    raw_category_orders = (n * params["baseline_team_revenue"] / params["team_share_total"]) / params["aov_base"]
    wanted = baseline_orders * params["potential_headroom"]
    return wanted / max(raw_category_orders * team_share, 1e-9)


def _steady_brand(params) -> tuple[float, float]:
    """Where brand equity and creative quality settle at the default spend.

    A going concern opens mid-life, so it opens where twelve months of the
    default marketing plan would have put it. Seeding both at a flat 0.50 was
    harmless only while M5 could not read a spend decision at all; with that
    wired up, every team spent the game climbing out of a hole the bootstrap
    had dug, and Round 1 came in a third below the baseline it is supposed to
    define.
    """
    from .decisions import REGISTRY

    brand_spend = float(REGISTRY["3.9"].default_when_disabled)
    creative_spend = float(REGISTRY["3.8"].default_when_disabled)
    brand = (params["brand_alpha"] * brand_spend
             / (params["brand_decay"] * params["brand_ref_spend"]))
    creative = (params["creative_kappa"]
                * (creative_spend / params["creative_ref_spend"]) ** 0.5
                / params["creative_decay"])
    return min(1.0, brand), min(1.0, creative)


def new_team(params, team_id: str) -> TeamState:
    team = TeamState(team_id=team_id, cash=params["starting_cash"])
    team.brand_equity, team.creative_quality = _steady_brand(params)
    # The lag in M5 peaks at t-1, so a going concern also opens with three
    # months of that spend behind it rather than a blank history.
    from .decisions import REGISTRY
    team.brand_spend_history = [float(REGISTRY["3.9"].default_when_disabled)] * 3

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
    """Put the team mid-cycle: stock arriving, suppliers owed, COD in transit.

    A going concern is not at a standstill. Seeding discrete lumps - two whole
    purchase orders, each paid in full on one round - produced a large payable
    pile-up a few rounds in, which is a bootstrap artifact rather than anything
    a team did. What it should carry is the STEADY-STATE ledger: in steady
    state a business places a purchase order worth C each round and pays out
    exactly C each round, spread across the rounds its terms span.
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

    # One round of demand already ordered and arriving next round.
    team.open_pos.append({
        "placed": 0, "arrives": 1, "units": dict(alloc),
        "cost": cost, "supplier": "B",
    })

    round_days = 30.44 * params["round_months"]
    lag = params["supplier_terms_days"] / round_days
    frac = lag - int(lag)
    # Owed to suppliers: one round's purchases due next round, plus the tail of
    # the round before that. Under 45-day terms a going concern is always two
    # POs deep, so the opening balance owes 1.48 rounds of purchases and each
    # round then settles one - which is the steady state, not an over-seeding.
    team.payables[1] = cost
    if frac > 0:
        team.payables[2] = cost * frac

    # COD already despatched and not yet remitted.
    cod_lag = params["cod_remit_days"] / round_days
    revenue = params["baseline_team_revenue"] * 0.78
    team.receivables[1] = revenue * params["cod_share_base"] * min(cod_lag, 1.0)
    team.cod_receivable = team.receivables[1]


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
