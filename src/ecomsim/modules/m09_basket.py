"""M9 - Basket & gross revenue.

Also writes value_actual back to each team, which the NEXT round's M5 compares
against value_perceived. A team discounting heavily builds a perceived-value
score that its actual price/quality position cannot support.
"""
from __future__ import annotations

from . import m03_supply as m03


def run(world, params, resolved, ctx) -> None:
    aovs: dict[str, float] = {}

    for team in world.teams.values():
        tid = team.team_id
        d = ctx["resolved"][tid]
        discount = ctx["discount"][tid]

        # AOV follows from the basket, not from a free parameter. If price and
        # COGS come from different places they disagree, and gross margin is
        # whatever the disagreement happens to be.
        basket = ctx["basket_list_price"][tid] * params["units_per_order"]
        aov = basket * (1 - discount)

        bundles = d.get("1.2") or []
        penetration = min(1.0, len(bundles) / 3.0) if bundles else 0.0
        aov *= 1 + params["bundle_aov_coef"] * penetration

        aov *= _freeship_effect(float(d.get("2.4", 0) or 0), params)

        recsys = ctx.get("capability_benefit", {}).get(tid, {}).get("recsys")
        if recsys is None and "recsys" in team.capabilities:
            recsys = 0.07
        aov *= 1 + (recsys or 0.0)
        aov *= 1 - ctx["prepaid_incentive_effect"][tid]

        aovs[tid] = aov
        orders = ctx["orders"][tid]
        ctx.setdefault("aov", {})[tid] = aov
        ctx.setdefault("gross_revenue", {})[tid] = orders * aov

        _consume_stock(team, params, orders, ctx)
        _write_value_actual(team, params, ctx, aov)

    if aovs:
        world.market_avg_aov = sum(aovs.values()) / len(aovs)


def _freeship_effect(threshold: float, params) -> float:
    """A threshold slightly above natural basket lifts AOV.

    Far above it kills conversion instead, which M8 already handles through the
    price multiplier - so this only ever lifts.
    """
    if threshold <= 0:
        return 1.0
    gap = (threshold - params["aov_base"]) / params["aov_base"]
    return 1 + params["freeship_coef"] * max(0.0, min(0.5, gap))


def _consume_stock(team, params, orders: float, ctx) -> None:
    units = orders * params["units_per_order"]
    skus = team.active_skus or [s["code"] for s in params.skus]
    total_w = sum(float(params.sku(c)["revenue_weight"]) for c in skus) or 1.0
    cogs = 0.0
    supplier = ctx.get("supplier", {}).get(team.team_id, {"cost_index": 1.0})
    served_w = 0.0
    for code in skus:
        weight = float(params.sku(code)["revenue_weight"]) / total_w
        want = units * weight
        taken = min(team.inventory.get(code, 0.0), want)
        team.inventory[code] = team.inventory.get(code, 0.0) - taken
        served_w += weight * (taken / want if want > 0 else 1.0)
        # The currency shock is charged where it has always been charged - on
        # the purchase order in M3, which is where a rupee move hits first and
        # hardest. Putting it here as well moved baseline contribution margin
        # by five points and is a recalibration, not a sourcing feature.
        cogs += (taken * float(params.sku(code)["unit_cost"])
                 * float(supplier.get("cost_index", 1.0))
                 * m03.landed_index(team, code, ctx["resolved"][team.team_id])
                 * params["cogs_scale"])
    # Units served over units wanted. instock_ratio reads opening stock - what
    # a customer sees on the listing page, and the right input to conversion -
    # but it cannot see a round that sold out, so it is not an operational
    # quality measure. This is.
    ctx.setdefault("fill_rate", {})[team.team_id] = served_w
    ctx.setdefault("cogs", {})[team.team_id] = cogs
    ctx.setdefault("units_sold", {})[team.team_id] = units


def _write_value_actual(team, params, ctx, aov: float) -> None:
    """Actual value is what the customer gets for the price, versus the market."""
    price_index = ctx["price_index"][team.team_id]
    quality = ctx["quality_tier"][team.team_id]
    team.value_actual = max(0.0, min(1.0, 0.5 + 0.6 * (quality - price_index * 0.62)))
