"""M9 - Basket & gross revenue.

Also writes value_actual back to each team, which the NEXT round's M5 compares
against value_perceived. A team discounting heavily builds a perceived-value
score that its actual price/quality position cannot support.
"""
from __future__ import annotations

from .. import mix
from . import m03_supply as m03

BUNDLE_UNITS = 3            # a bundle is a three-pack of one product
DEFAULT_PACK_RATIO = 0.90   # a pack offered with no price: 10% under three singles


def run(world, params, resolved, ctx) -> None:
    aovs: dict[str, float] = {}

    # Who bought, before what they bought: a product's share of the basket is
    # read against the customer mix of the other stores, so it needs them all.
    for team in world.teams.values():
        ctx.setdefault("order_segments", {})[team.team_id] = \
            mix.order_segments(team, params, ctx)
    reference = mix.reference_segments(world, params, ctx)

    for team in world.teams.values():
        tid = team.team_id
        d = ctx["resolved"][tid]
        orders = ctx["orders"][tid]

        # AOV follows from the basket, not from a free parameter. If price and
        # COGS come from different places they disagree, and gross margin is
        # whatever the disagreement happens to be. The basket is now the
        # team's own product mix at its own net prices (ecomsim.mix): a store
        # selling more serum has a dearer basket and a dearer cost of goods.
        terms = _pack_terms(team, params, d)
        ship = _freeship_effect(float(d.get("2.4", 0) or 0), params)
        # Reaching for the bar means adding items, and items cost money: the
        # basket's extra value carries its cost of goods, as packs do.
        ctx.setdefault("bundle_units_mult", {})[tid] = (1 + terms["uplift"]) * ship
        lines = mix.basket(team, params, ctx, d, reference, terms["packs"],
                           terms["uplift"])

        recsys = ctx.get("capability_benefit", {}).get(tid, {}).get("recsys")
        if recsys is None and "recsys" in team.capabilities:
            recsys = 0.07
        lift = (1 + (recsys or 0.0)) * (1 - ctx["prepaid_incentive_effect"][tid])

        # Revenue is what was shipped, product by product: a line that ran out
        # sells what it had, and the order goes out without it. With the
        # catalogue mix, one price position and no packs this is exactly the
        # old basket price x units x delivery effect.
        _consume_stock(team, params, orders, ctx, lines, terms, ship)
        sales = ctx["sku_sales"][tid]
        for v in sales.values():
            v["gross"] = v["value"] * lift
        gross = sum(v["gross"] for v in sales.values())
        aov = gross / orders if orders > 0 else (
            sum(v["share"] * v["net_price"] for v in lines.values())
            * params["units_per_order"] * ship * lift)
        aovs[tid] = aov
        ctx.setdefault("aov", {})[tid] = aov
        ctx.setdefault("gross_revenue", {})[tid] = gross

        _write_value_actual(team, params, ctx, aov)

    if aovs:
        world.market_avg_aov = sum(aovs.values()) / len(aovs)


def _unit_net_price(team, params, d, code: str) -> float:
    """What one unit of a product sells for this month, after its discount."""
    return mix.unit_net_price(team, params, d, code)


def _pack_terms(team, params, d) -> dict:
    """The packs that count this month: the three most appealing.

    {"uplift": extra units per order as a share, "share": the share of
    revenue sold as packs, "ratio": the uptake-weighted pack price against
    three singles, "packs": {product: (its share of the pack uptake, its
    price ratio)}}.
    """
    raw = d.get("1.2") or {}
    cells = {c: {} for c in raw} if isinstance(raw, list) else dict(raw)
    sold = set(team.active_skus or [s["code"] for s in params.skus])
    offered = []
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
        # Nobody pays more for a pack than for its three singles, so a dear
        # pack earns no premium - it simply sells less.
        offered.append((a, min(ratio, 1.0), code))
    if not offered:
        return {"uplift": 0.0, "share": 0.0, "ratio": 1.0, "packs": {}}
    top = sorted(offered, reverse=True)[:3]
    penetration = sum(a for a, _, _ in top) / 3.0
    weight = sum(a for a, _, _ in top)
    ratio = sum(a * r for a, r, _ in top) / (weight or 1.0)   # uptake-weighted pack price
    return {"uplift": params["bundle_aov_coef"] * penetration,
            "share": params["bundle_revenue_share"] * penetration,
            "ratio": ratio,
            "packs": {code: (a / weight if weight > 0 else 0.0, r)
                      for a, r, code in top}}


def _bundle_effect(team, params, d) -> tuple[float, float]:
    """(AOV multiplier, units-per-order multiplier) from the packs on offer.

    Each pack is judged against three singles at the team's own net price.
    A pack cheaper than three singles appeals more and is taken up more; one
    dearer than three singles barely sells (shoppers buy the singles instead)
    and never earns more than the singles would. The three most appealing
    packs set the uptake - the gain flattens past three lines. Uptake lifts
    the basket with real units of the packed products, so cost of goods rises
    with it, and the pack's saving is given away on the bundled share of
    revenue. Before this, only the NUMBER of packs was read: a pack priced at
    double three singles earned the same lift as a fair one.
    """
    t = _pack_terms(team, params, d)
    if not t["packs"]:
        return 1.0, 1.0
    aov_mult = (1 + t["uplift"]) * (1 - t["share"] * (1 - t["ratio"]))
    return aov_mult, 1 + t["uplift"]


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


def _consume_stock(team, params, orders: float, ctx, lines: dict, terms: dict,
                   ship: float) -> None:
    """Take this month's units out of stock, product by product.

    Units per product are the order's single units in the team's own mix,
    plus the pack uplift on the packed lines, all scaled by the free-delivery
    basket effect. Each line's value is what it shipped, so a line that ran
    out earns only what it had.
    """
    tid = team.team_id
    d = ctx["resolved"][tid]
    base_units = orders * params["units_per_order"]
    uplift = terms["uplift"]
    pack_reach = (params["bundle_revenue_share"] / params["bundle_aov_coef"]
                  if params["bundle_aov_coef"] > 0 else 0.0)
    supplier = ctx.get("supplier", {}).get(tid, {"cost_index": 1.0})

    wanted_units = shipped_units = cogs = 0.0
    sales = {}
    for code, v in lines.items():
        want = base_units * ship * (v["share"] + uplift * v["pack"])
        taken = min(team.inventory.get(code, 0.0), want)
        team.inventory[code] = team.inventory.get(code, 0.0) - taken
        fill = taken / want if want > 0 else 1.0
        # The pack saving is given away on the units sold in packs of this
        # line - never more of them than the line sold. Most pack buyers
        # would have bought several singles anyway, so units in packs run
        # well ahead of the extra units packs add (bundle_revenue_share
        # against bundle_aov_coef); with three packs on mid-sized lines this
        # is the range-wide saving the pack levers were calibrated on.
        price = v["net_price"]
        extra = base_units * ship * uplift * v["pack"]
        in_packs = min(0.85 * want, extra * pack_reach)   # some still buy one
        saving = in_packs * price * (1 - v["pack_ratio"])
        value = (want * price - saving) * fill
        # The currency shock is charged where it has always been charged - on
        # the purchase order in M3, which is where a rupee move hits first and
        # hardest. Putting it here as well moved baseline contribution margin
        # by five points and is a recalibration, not a sourcing feature.
        line_cogs = (taken * float(params.sku(code)["unit_cost"])
                     * float(supplier.get("cost_index", 1.0))
                     * m03.landed_index(team, code, d)
                     * params["cogs_scale"])
        cogs += line_cogs
        wanted_units += want
        shipped_units += taken
        pushed = base_units * ship * v["push"] * fill
        packed = in_packs * fill
        sales[code] = {
            "want": want, "sold": taken, "value": value, "cogs": line_cogs,
            # A pack is picked, packed and shipped as one item.
            "slots": taken - packed * (BUNDLE_UNITS - 1) / BUNDLE_UNITS,
            "base": v["base"], "net_price": price,
            "relative_price": v["relative_price"],
            "seg_pull": v["seg_pull"], "price_pull": v["price_pull"],
            "pushed_units": pushed, "pack_units": packed,
            "campaigns": v.get("campaigns", []), "buyers": v["buyers"],
        }
    # Units served over units wanted. instock_ratio reads opening stock - what
    # a customer sees on the listing page, and the right input to conversion -
    # but it cannot see a round that sold out, so it is not an operational
    # quality measure. This is.
    ctx.setdefault("fill_rate", {})[tid] = (
        shipped_units / wanted_units if wanted_units > 0 else 1.0)
    ctx.setdefault("cogs", {})[tid] = cogs
    ctx.setdefault("units_sold", {})[tid] = shipped_units
    ctx.setdefault("sku_sales", {})[tid] = sales


def _write_value_actual(team, params, ctx, aov: float) -> None:
    """Actual value is what the customer gets for the price, versus the market."""
    price_index = ctx["price_index"][team.team_id]
    quality = ctx["quality_tier"][team.team_id]
    team.value_actual = max(0.0, min(1.0, 0.5 + 0.6 * (quality - price_index * 0.62)))
