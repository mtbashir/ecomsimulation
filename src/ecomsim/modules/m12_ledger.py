"""M12 - Customer ledger.

Cohorts are tracked individually, and churn and frequency are set by the
ACQUISITION CHANNEL, not a global constant. The deal_driven row at churn 0.44
is what makes discounting a trap: the cohort costs the same CAC and returns a
quarter of the lifetime value (docs/07 M12).

LTV is computed from this ledger, never from a formula applied to averages.
"""
from __future__ import annotations

from ..state import Cohort

PAID_DECISIONS = {
    "meta": "3.1", "google_search": "3.2", "tiktok": "3.4",
}
DEAL_THRESHOLD = 0.25


def run(world, params, resolved, ctx) -> None:
    for team in world.teams.values():
        tid = team.team_id
        orders = ctx["orders"][tid]
        pending = team.pending_gap_penalties.get(world.round, {})

        repeat_demand = _age_cohorts(team, params, ctx, pending)
        # Repeat customers are rationed alongside everyone else when supply or
        # traffic binds. If repeat demand routinely exceeds total orders the
        # cohort seed is inconsistent with the baseline, so say so rather than
        # silently reporting 100% repeat and zero CAC.
        repeat_orders = min(repeat_demand, orders)
        if repeat_demand > orders * 1.05:
            ctx.setdefault("warnings", []).append(
                f"{tid} r{world.round}: repeat demand {repeat_demand:,.0f} "
                f"exceeds orders {orders:,.0f} - cohort seed inconsistent"
            )
        new_orders = max(0.0, orders - repeat_orders)
        new_customers = new_orders / params["first_order_units"]

        if new_customers > 0:
            _add_cohort(team, world, params, ctx, new_customers)

        active = sum(c.active for c in team.cohorts)
        ctx.setdefault("repeat_orders", {})[tid] = repeat_orders
        ctx.setdefault("new_orders", {})[tid] = new_orders
        ctx.setdefault("new_customers", {})[tid] = new_customers
        ctx.setdefault("active_customers", {})[tid] = active
        ctx.setdefault("repeat_order_share", {})[tid] = (
            repeat_orders / orders if orders > 0 else 0.0
        )
        ctx.setdefault("ltv", {})[tid] = _ltv(team, params, ctx)


def _age_cohorts(team, params, ctx, pending) -> float:
    """Churn each cohort, then count the repeat orders the survivors place."""
    experience_penalty = ctx.get("experience_penalty", {}).get(team.team_id, 0.0)
    retention_effect = ctx.get("retention_effect", {}).get(team.team_id, 0.0)
    repeat_mult = pending.get("repeat_mult", 1.0)

    repeat_orders = 0.0
    for cohort in team.cohorts:
        churn = (
            cohort.churn_base
            * (1 + params["churn_experience_coef"] * experience_penalty)
            * (1 - params["churn_retention_coef"] * retention_effect)
        )
        cohort.active *= max(0.0, 1 - max(0.0, min(0.95, churn)))
        repeat_orders += cohort.active * cohort.freq * repeat_mult

    team.cohorts = [c for c in team.cohorts if c.active > 1.0]
    return repeat_orders


def _add_cohort(team, world, params, ctx, customers: float) -> None:
    """Stamp the new cohort with the channel mix that acquired it.

    A team discounting past 25% acquires Deal Hunters whatever channel the
    spend went through, and they churn at 0.44.
    """
    if ctx["discount"][team.team_id] > DEAL_THRESHOLD:
        channel = "deal_driven"
    else:
        channel = _dominant_channel(team, ctx)

    ch = params.channel(channel)
    team.cohorts.append(Cohort(
        acquired_round=world.round,
        channel=channel,
        active=customers,
        churn_base=float(ch["churn_base"]),
        freq=float(ch["freq_per_round"]),
    ))


def _dominant_channel(team, ctx) -> str:
    d = ctx["resolved"][team.team_id]
    spends = {c: float(d.get(dec, 0) or 0) for c, dec in PAID_DECISIONS.items()}
    if not any(spends.values()):
        return "organic"
    return max(spends, key=spends.get)


def _ltv(team, params, ctx) -> float:
    """Contribution-margin LTV over the configured horizon, from the ledger."""
    aov = ctx.get("aov", {}).get(team.team_id, params["aov_base"])
    margin = ctx.get("contribution_margin_pct", {}).get(
        team.team_id, params["gross_margin_base"] - 0.29
    )
    horizon = params["ltv_horizon_months"] / params["round_months"]

    active_total = sum(c.active for c in team.cohorts) or 1.0
    ltv = 0.0
    for cohort in team.cohorts:
        weight = cohort.active / active_total
        survival, orders = 1.0, 0.0
        for _ in range(int(horizon)):
            orders += survival * cohort.freq
            survival *= 1 - cohort.churn_base
        ltv += weight * orders * aov * max(margin, 0.01)
    return ltv
