"""M9 - Basket & gross revenue.

Also writes value_actual back to each team, which the NEXT round's M5 compares
against value_perceived. A team discounting heavily builds a perceived-value
score that its actual price/quality position cannot support.
"""
from __future__ import annotations

from . import m03_supply as m03
from .m00_resolve import monthly_discounts, monthly_prices

BUNDLE_UNITS = 3            # a bundle is a three-pack of one product
DEFAULT_PACK_RATIO = 0.90   # a pack offered with no price: 10% under three singles


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

        bundle_aov, bundle_units = _bundle_effect(team, params, d)
        aov *= bundle_aov
        ctx.setdefault("bundle_units_mult", {})[tid] = bundle_units

        ship = _freeship_effect(float(d.get("2.4", 0) or 0), params)
        aov *= ship
        # Reaching for the bar means adding items, and items cost money: the
        # basket's extra value carries its cost of goods, as packs do.
        ctx["bundle_units_mult"][tid] *= ship

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


def _unit_net_price(team, params, d, code: str) -> float:
    """What one unit of a product sells for this month, after its discount.

    The same order of precedence as the shelf price: this month's price list,
    then the founding price, then the catalogue at the team's tier.
    """
    sku = params.sku(code)
    price = monthly_prices(d).get(
        code, (team.sku_prices or {}).get(
            code, float(sku["list_price"]) * team.price_multiplier))
    discount = monthly_discounts(d).get(code, float(d.get("2.2", 0) or 0))
    return float(price) * (1 - discount)


def _bundle_effect(team, params, d) -> tuple[float, float]:
    """(AOV multiplier, units-per-order multiplier) from the packs on offer.

    Each pack is judged against three singles at the team's own net price.
    A pack cheaper than three singles appeals more and is taken up more; one
    dearer than three singles barely sells (shoppers buy the singles instead)
    and never earns more than the singles would. The three most appealing packs set the uptake - the gain flattens past
    three lines. Uptake lifts the basket with real units, so cost of goods
    rises with it, and the pack's saving is given away on the bundled share
    of revenue. Before this, only the NUMBER of packs was read: a pack priced
    at double three singles earned the same lift as a fair one.
    """
    raw = d.get("1.2") or {}
    cells = {c: {} for c in raw} if isinstance(raw, list) else dict(raw)
    sold = set(team.active_skus or [s["code"] for s in params.skus])
    appeal, ratios = [], []
    for code, cell in cells.items():
        if code not in sold:
            continue
        reference = _unit_net_price(team, params, d, code) * BUNDLE_UNITS
        if reference <= 0:
            continue
        try:
            price = float((cell or {}).get("price") or 0)
        except (TypeError, ValueError):
            price = 0.0
        ratio = price / reference if price > 0 else DEFAULT_PACK_RATIO
        if ratio <= 1.0:
            a = 1 + params["bundle_price_sensitivity"] * (1 - ratio)
        else:
            # Dearer than three singles: shoppers buy the singles instead.
            a = 1 - params["bundle_overprice_sensitivity"] * (ratio - 1)
        a = max(0.0, min(params["bundle_appeal_cap"], a))
        appeal.append(a)
        # Nobody pays more for a pack than for its three singles, so a dear
        # pack earns no premium - it simply sells less.
        ratios.append(min(ratio, 1.0))
    if not appeal:
        return 1.0, 1.0
    top = sorted(zip(appeal, ratios), reverse=True)[:3]
    penetration = sum(a for a, _ in top) / 3.0
    weight = sum(a for a, _ in top) or 1.0
    ratio = sum(a * r for a, r in top) / weight      # uptake-weighted pack price
    uplift = params["bundle_aov_coef"] * penetration
    share = params["bundle_revenue_share"] * penetration
    aov_mult = (1 + uplift) * (1 - share * (1 - ratio))
    return aov_mult, 1 + uplift


def _freeship_effect(threshold: float, params) -> float:
    """AOV multiplier from the free-delivery threshold.

    A bar a little above a typical basket makes customers add to reach it (up
    to half a basket above, then no further). Free delivery on everything takes
    the reason away: baskets come in smaller. The conversion side - a bar far
    above the basket loses small orders, free delivery wins some - is in M8
    (freeship_conversion), so the lever is a trade-off, not a free lift.
    """
    if threshold <= 0:
        return 1 - params["freeship_free_aov_drop"]
    gap = (threshold - params["aov_base"]) / params["aov_base"]
    return 1 + params["freeship_coef"] * max(0.0, min(0.5, gap))


def freeship_conversion(threshold: float, params) -> float:
    """Conversion multiplier from the free-delivery threshold.

    Free delivery on every order converts a little better. A bar set more than
    half a basket above a typical order turns small buyers away, more the
    higher it goes. Between the two, delivery terms leave conversion alone.
    """
    if threshold <= 0:
        return 1 + params["freeship_free_cr_lift"]
    gap = (threshold - params["aov_base"]) / params["aov_base"]
    return max(0.70, 1 - params["freeship_cr_penalty"] * max(0.0, gap - 0.5))


def _consume_stock(team, params, orders: float, ctx) -> None:
    units = (orders * params["units_per_order"]
             * ctx.get("bundle_units_mult", {}).get(team.team_id, 1.0))
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
