"""M17 - Scoring & persist.

Criterion-referenced anchors, not cohort normalisation: 9% contribution margin
scores 50 whether rivals hit 12% or 4%. That keeps scores comparable across
cohorts and stable from 2 to 16 teams (docs/08).

Flow metrics are weighted by round and accumulated in M17 of each round; stock
metrics are read terminally. Market share is the sole relative metric, because
it is the only genuinely zero-sum one.
"""
from __future__ import annotations

from .. import targeting


def anchor(value: float, zero: float, fifty: float, hundred: float) -> float:
    """Map a value onto 0-100 through published anchors, clamped."""
    if hundred > zero:
        if value <= zero:
            return 0.0
        if value <= fifty:
            return 50.0 * (value - zero) / (fifty - zero)
        return min(100.0, 50.0 + 50.0 * (value - fifty) / (hundred - fifty))
    if value >= zero:
        return 0.0
    if value >= fifty:
        return 50.0 * (zero - value) / (zero - fifty)
    return min(100.0, 50.0 + 50.0 * (fifty - value) / (fifty - hundred))


def runway_score(runway: float) -> float:
    """Banded, not monotonic.

    A team sitting on 14+ rounds of runway in a growing category has failed at
    capital allocation as surely as one about to run out. Making "most cash
    wins" the rule would teach exactly the wrong thing.
    """
    if runway < 2:
        return 0.0
    if runway < 4:
        return 25.0
    if runway <= 8:
        return 100.0
    if runway <= 14:
        return 60.0
    return 30.0


def run(world, params, resolved, ctx) -> None:
    total_revenue = sum(ctx["net_revenue"].values()) or 1.0

    for team in world.teams.values():
        tid = team.team_id
        pnl = ctx["pnl"][tid]

        from .m12_ledger import _ltv
        ctx["ltv"][tid] = _ltv(team, params, ctx)

        record = {
            "round": world.round,
            "orders": ctx["orders"][tid],
            "potential": ctx["potential"][tid],
            "sellable": ctx["sellable"][tid],
            "sessions": ctx["sessions"][tid],
            "conversion_rate": ctx["orders"][tid] / max(ctx["sessions"][tid], 1.0),
            "aov_net": ctx["aov"][tid],
            "revenue_net": ctx["net_revenue"][tid],
            "gross_margin_pct": ctx["gross_margin_pct"][tid],
            "contribution_margin_pct": ctx["contribution_margin_pct"][tid],
            "contribution_pre_marketing_pct":
                ctx["contribution_pre_marketing_pct"][tid],
            "ebitda_margin_pct": pnl["ebitda"] / max(pnl["net_revenue"], 1.0),
            "cac_blended": ctx["cac_blended"][tid],
            "repeat_order_share": ctx["repeat_order_share"][tid],
            "active_customers": ctx["active_customers"][tid],
            "ltv": ctx["ltv"][tid],
            "ltv_cac_ratio": (
                ctx["ltv"][tid] / ctx["cac_blended"][tid]
                if ctx["cac_blended"][tid] > 0 else 0.0
            ),
            "rating": ctx["rating"][tid],
            "nps": ctx["nps"][tid],
            "instock_rate": ctx["instock_ratio"][tid],
            "fill_rate": ctx["fill_rate"][tid],
            "service_level": ctx["service_level"][tid],
            "lost_to_stockout": max(0.0, ctx["sellable"][tid] - ctx["orders"][tid]),
            "inventory_units": sum(team.inventory.values()),
            "demand_forecast": ctx["demand_forecast"][tid],
            "forecast_error": abs(ctx["demand_forecast"][tid] - ctx["orders"][tid])
                              / max(ctx["orders"][tid], 1.0),
            "weeks_cover": sum(team.inventory.values()) * 4.33
                           / max(ctx["orders"][tid] * params["units_per_order"], 1.0),
            "cs_backlog": ctx["cs_backlog"][tid],
            "delivery_success": ctx["courier_success"][tid],
            "rto_rate": ctx["rto_rate"][tid],
            "return_rate": ctx["return_rate"][tid],
            "cash_balance": ctx["cash"][tid],
            "runway_rounds": ctx["runway_rounds"][tid],
            "credit_drawn": ctx["credit_drawn"][tid],
            "market_share": ctx["net_revenue"][tid] / total_revenue,
            "binding_constraint": ctx["binding_constraint"][tid],
            "perception_gap": ctx["perception_gap"].get(tid, 0.0),
            "roas_reported": ctx["roas_reported"][tid],
            "roas_true": ctx["roas_true"][tid],
            "creative_quality": team.creative_quality,
            "brand_equity": team.brand_equity,
            "new_customers": ctx["new_customers"][tid],
            "discount_rate": ctx["discount"][tid],
            "cod_receivable": team.cod_receivable,
            "credit_drawn": ctx["credit_drawn"][tid],
            "ebitda": pnl["ebitda"],
            "net_profit": pnl["net_profit"],
            "insolvent": ctx["insolvent"][tid],
            "events": ctx.get("event_codes", []),
            "pnl": pnl | {"cogs": ctx["cogs"][tid]},
            "campaigns": targeting.performance(team, params, ctx,
                                               ctx["resolved"][tid]),
        }
        team.history.append(record)
        ctx.setdefault("scorecard", {})[tid] = _scorecard(team, params, record)


def _scorecard(team, params, record) -> dict:
    """Round-level pillar scores. Weighted aggregation happens at run end."""
    p1 = (
        12 / 25 * anchor(record["contribution_pre_marketing_pct"],
                         0.14, 0.24, 0.32)
        + 8 / 25 * anchor(record["ebitda_margin_pct"], -0.10, 0.0, 0.10)
        + 5 / 25 * anchor(record["gross_margin_pct"], 0.25, 0.38, 0.50)
    )
    p3 = (
        8 / 20 * anchor(record["ltv_cac_ratio"], 0.8, 1.9, 3.8)
        + 5 / 20 * anchor(record["repeat_order_share"], 0.26, 0.355, 0.46)
        + 4 / 20 * anchor(record["active_customers"], 22_000, 30_000, 40_000)
        + 3 / 20 * anchor(record["nps"], 70, 82, 92)
    )
    p4 = (
        4 / 15 * anchor(record["instock_rate"], 0.80, 0.93, 0.99)
        + 4 / 15 * anchor(record["delivery_success"], 0.75, 0.87, 0.95)
        + 4 / 15 * anchor(
            (record["pnl"]["rto_cost"] + record["pnl"]["return_cost"])
            / max(record["revenue_net"], 1.0), 0.14, 0.08, 0.03)
        + 3 / 15 * 50.0  # inventory turns - terminal, scored at run end
    )
    p5 = 0.0 if record["insolvent"] else runway_score(record["runway_rounds"])

    return {"p1": p1, "p3": p3, "p4": p4, "p5": p5}
