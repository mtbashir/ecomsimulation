"""Which products sell, to whom, and why.

Until this module the basket was the catalogue: every team sold its range in
the same fixed proportions (revenue_weight), whatever it charged for each line,
whoever its customers were and whatever its campaigns pushed. A sales-by-product
report built on that would have shown every team the same shape, and no
portfolio decision could have shown up in it.

A product's share of the basket now moves with five things a team controls:

1. Who its customers are. Each product has a main and a second buyer segment
   (params/audiences.csv). A team that wins more Quality Loyalists than the
   other stores sells more serum; one that wins Value Seekers sells more oil.
2. Its price against the rest of the range. A line priced or discounted below
   the team's other lines takes a bigger share of the basket - more so when
   its buyers are price-driven.
3. Campaigns that name it. An order a product campaign brings in starts with
   that product; the rest of the basket follows the store's mix.
4. Packs on it. A pack's extra units are units of that product.
5. Its stock. A line that runs out sells what it had.

The neutral case is exact: a team with the market's customer mix, one price
position across the range, no product campaigns and no packs sells in the
catalogue proportions, so the calibration baseline does not move.

The customer mix by product is the team's own data - who bought what, which a
real store reads from what its visitors browse and buy. What each segment
values and how big it is in the market stays hidden, behind MR-06.
"""
from __future__ import annotations

from . import targeting
from .modules.m00_resolve import monthly_discounts, monthly_prices


def active(team, params) -> list[str]:
    return list(team.active_skus or [s["code"] for s in params.skus])


def catalogue_shares(team, params) -> dict[str, float]:
    """Each line's share of units in a typical store selling this range."""
    codes = active(team, params)
    total = sum(float(params.sku(c)["revenue_weight"]) for c in codes) or 1.0
    return {c: float(params.sku(c)["revenue_weight"]) / total for c in codes}


def unit_net_price(team, params, d, code: str) -> float:
    """What one unit sells for this month, after its discount.

    The same order of precedence as the shelf price: this month's price list,
    then the founding price, then the catalogue at the team's tier.
    """
    sku = params.sku(code)
    price = monthly_prices(d).get(
        code, (team.sku_prices or {}).get(
            code, float(sku["list_price"]) * team.price_multiplier))
    discount = monthly_discounts(d).get(code, float(d.get("2.2", 0) or 0))
    return float(price) * (1 - max(0.0, min(0.5, discount)))


TIER_LEAN = {"economy": -1.0, "standard": 0.0, "premium": 1.0}


def affinity(params, code: str) -> dict[str, float]:
    """How strongly each segment buys a product, against an average segment.

    The product's main and second buyers (params/audiences.csv) set the
    shape; its tier tilts it - segments that pay more lean to premium lines
    and segments that pay less lean to economy ones.
    """
    aud = params.audience(code) or {}
    lean = TIER_LEAN.get(str(params.sku(code).get("tier")), 0.0)
    out = {}
    for seg in params.segments:
        s = seg["code"]
        if s == aud.get("segment_1"):
            a = params["mix_affinity_primary"]
        elif s == aud.get("segment_2"):
            a = params["mix_affinity_secondary"]
        else:
            a = params["mix_affinity_other"]
        out[s] = a * float(seg["wtp_index"]) ** lean
    return out


def order_segments(team, params, ctx) -> dict[str, float]:
    """This month's orders by segment.

    New customers come in the proportions M7 won them. Repeat orders lean
    toward the segments that come back, so a store with a loyal base sells
    more to Quality Loyalists than its new-customer mix alone would say.
    """
    tid = team.team_id
    market = {s["code"]: float(s["share"]) for s in params.segments}
    mix = ctx.get("segment_mix", {}).get(tid) or market
    orders = ctx.get("orders", {}).get(tid, 0.0)
    repeat = min(ctx.get("repeat_demand", {}).get(tid, 0.0), orders)
    new = max(0.0, orders - repeat)
    back = {s["code"]: float(s["repeat_propensity"]) for s in params.segments}
    tilt = sum(mix.get(s, 0.0) * back[s] for s in back) or 1.0
    if new + repeat <= 0:
        total = sum(mix.get(s, 0.0) for s in back) or 1.0
        return {s: mix.get(s, 0.0) / total for s in back}
    return {s: (new * mix.get(s, 0.0) + repeat * mix.get(s, 0.0) * back[s] / tilt)
            / (new + repeat) for s in back}


def reference_segments(world, params, ctx) -> dict[str, float]:
    """The customer mix of the online stores in this market, weighted by size.

    Measured against the stores rather than the population, so identical
    teams sell identical baskets - the catalogue mix - and only a team whose
    customers differ from its rivals' sees its product mix move.
    """
    mixes = ctx.get("order_segments", {})
    weights = {tid: max(ctx.get("potential", {}).get(tid, 0.0), 0.0) for tid in mixes}
    total = sum(weights.values())
    if not mixes or total <= 0:
        return {s["code"]: float(s["share"]) for s in params.segments}
    return {s["code"]: sum(weights[t] * mixes[t].get(s["code"], 0.0) for t in mixes)
            / total for s in params.segments}


def demand(team, params, ctx, d, reference: dict[str, float]) -> dict[str, dict]:
    """Per product: what pulled it up or down, and its share of the basket.

    `general` is the share before campaigns and packs: the catalogue share,
    times the pull of the team's customers, times the pull of its price
    against the rest of the range, renormalised over the range.
    """
    tid = team.team_id
    base = catalogue_shares(team, params)
    segs = ctx.get("order_segments", {}).get(tid) or reference
    w_price = {s["code"]: float(s["w_price"]) for s in params.segments}
    rel = {c: unit_net_price(team, params, d, c) / float(params.sku(c)["list_price"])
           for c in base}
    typical = sum(base[c] * rel[c] for c in base)

    out = {}
    for c in base:
        aff = affinity(params, c)
        mine = sum(segs.get(s, 0.0) * a for s, a in aff.items())
        ref = sum(reference.get(s, 0.0) * a for s, a in aff.items())
        buyers = ({s: segs.get(s, 0.0) * a / mine for s, a in aff.items()}
                  if mine > 0 else {})
        # Price-driven buyers move further for the same gap.
        elasticity = params["mix_price_elasticity"] * sum(
            buyers.get(s, 0.0) * w for s, w in w_price.items())
        ratio = rel[c] / typical if typical > 0 else 1.0
        pull = max(0.3, min(3.0, ratio ** -elasticity)) if ratio > 0 else 3.0
        out[c] = {"base": base[c], "seg_pull": mine / ref if ref > 0 else 1.0,
                  "price_pull": pull, "relative_price": ratio - 1,
                  "net_price": unit_net_price(team, params, d, c),
                  "buyers": buyers}
    raw = {c: v["base"] * v["seg_pull"] * v["price_pull"] for c, v in out.items()}
    total = sum(raw.values()) or 1.0
    for c, v in out.items():
        v["general"] = raw[c] / total
    return out


def campaign_orders(team, params, ctx, d) -> list[dict]:
    """Paid orders by campaign, the same way the report attributes them.

    Mirrors targeting.performance - sessions split by spend and quality, the
    month's conversion, channel intent sharing the paid orders out - without
    the A/B draw, which moves orders between a pair and not between products.
    """
    tid = team.team_id
    scored = ctx.get("targeting", {}).get(tid, {})
    sessions = ctx.get("paid_sessions", {}).get(tid, {})
    cr = ctx.get("conversion_rate", {}).get(tid, 0.0)
    capacity = ctx.get("traffic_capacity", {}).get(tid, 0.0)
    orders = ctx.get("orders", {}).get(tid, 0.0)
    realised = min(1.0, orders / capacity) if capacity > 0 else 0.0
    sold = set(active(team, params))
    rows = []
    for ch, dec in targeting.CHANNELS.items():
        spend = float(d.get(dec, 0) or 0)
        if spend <= 0:
            continue
        block = scored.get(ch)
        camps = block["campaigns"] if block else [
            {"spend": spend, "traffic": 1.0, "cvr": 1.0, "skus": [], "name": ""}]
        weight = [c["spend"] * c["traffic"] for c in camps]
        total = sum(weight) or 1.0
        intent = float(params.channel(ch).get("intent_cvr") or 1.0)
        for c, w in zip(camps, weight):
            rows.append({
                "channel": ch, "name": c.get("name") or "",
                "spend": c["spend"], "intent": intent,
                "products": [s for s in c.get("skus") or [] if s in sold],
                "orders": sessions.get(ch, 0.0) * w / total * cr * c["cvr"] * realised,
            })
    paid = sum(r["orders"] for r in rows)
    weighted = sum(r["orders"] * r["intent"] for r in rows)
    k = paid / weighted if weighted > 0 else 1.0
    for r in rows:
        r["orders"] *= r["intent"] * k
    return rows


def basket(team, params, ctx, d, reference: dict[str, float],
           packs: dict[str, tuple[float, float]], uplift: float) -> dict[str, dict]:
    """Each product's share of the units an order carries, all five pulls in.

    Returns the `demand` rows with `push` (units-per-order share from product
    campaigns), `share` (the share of an order's single units) and `pack`
    (this line's share of the pack uplift) added.
    """
    lines = demand(team, params, ctx, d, reference)
    orders = ctx.get("orders", {}).get(team.team_id, 0.0)
    units = orders * params["units_per_order"]
    push = {c: 0.0 for c in lines}
    campaigns = {c: [] for c in lines}
    if units > 0:
        for r in campaign_orders(team, params, ctx, d):
            if not r["products"] or r["orders"] <= 0:
                continue
            g = {c: lines[c]["general"] for c in r["products"]}
            total = sum(g.values()) or 1.0
            for c in r["products"]:
                got = r["orders"] * params["mix_hero_units"] * g[c] / total
                push[c] += got
                campaigns[c].append((r["channel"], r["name"], got, r["spend"] * g[c] / total))
    pushed = sum(push.values()) / units if units > 0 else 0.0
    scale = min(1.0, 0.6 / pushed) if pushed > 0 else 1.0   # never the whole basket
    pushed *= scale
    for c, v in lines.items():
        v["push"] = push[c] * scale / units if units > 0 else 0.0
        v["share"] = v["general"] * (1 - pushed) + v["push"]
        v["pack"] = packs.get(c, (0.0, 1.0))[0]
        v["pack_ratio"] = packs.get(c, (0.0, 1.0))[1]
        v["campaigns"] = [(ch, name, got * scale, spend)
                          for ch, name, got, spend in campaigns[c]]
    return lines


# --- Turning the month into a product P&L -----------------------------------------------

def product_lines(team, params, ctx) -> list[dict]:
    """Sales, gross margin and contribution by product, adding up to the P&L.

    Product cost follows each line's own landed cost. Returns lean toward the
    lines customers send back most; failed deliveries and the prepaid discount
    fall on sales. Delivery, packing and courier costs are shared by items in
    the parcel - a cheap item costs as much to pick and ship as a dear one,
    which is what makes a cheap line thin, and a three-pack is one item,
    which is what a pack does for it. Payment costs and commission follow sales. Marketing
    spent on a product campaign is charged to the products it named; the rest
    of the marketing budget is shared by sales.
    """
    tid = team.team_id
    sales = ctx.get("sku_sales", {}).get(tid) or {}
    pnl = ctx.get("pnl", {}).get(tid)
    if not sales or not pnl:
        return []

    def share(key_of) -> dict[str, float]:
        raw = {c: max(0.0, key_of(c, v)) for c, v in sales.items()}
        total = sum(raw.values())
        return {c: (raw[c] / total if total > 0 else 0.0) for c in raw}

    by_gross = share(lambda c, v: v["gross"])
    by_returns = share(lambda c, v: v["gross"] * float(params.sku(c)["return_propensity"]))
    by_cogs = share(lambda c, v: v["cogs"])
    by_slots = share(lambda c, v: v.get("slots", v["sold"]))

    gross_total = pnl["gross_revenue"] + pnl["prepaid_discount"]
    deductions = pnl["gross_revenue"] - pnl["net_revenue"]
    returns = min(pnl["returns_value"], deductions)
    other = deductions - returns
    product_cost = pnl["net_revenue"] - pnl["gross_profit"]
    cm_pre_total = pnl["contribution"] + pnl["marketing"]
    pay = pnl["payment_costs"] + pnl["commission"]
    logistics = pnl["gross_profit"] - cm_pre_total - pay

    net = {c: gross_total * by_gross[c] - pnl["prepaid_discount"] * by_gross[c]
           - returns * by_returns[c] - other * by_gross[c] for c in sales}
    net_total = sum(net.values())
    by_net = {c: (max(0.0, net[c]) / net_total if net_total > 0 else 0.0) for c in net}

    directed = {c: sum(spend for *_, spend in v.get("campaigns", [])) for c, v in sales.items()}
    directed_total = sum(directed.values())
    if directed_total > pnl["marketing"]:   # cannot charge more than was spent
        k = pnl["marketing"] / directed_total if directed_total > 0 else 0.0
        directed = {c: x * k for c, x in directed.items()}
        directed_total = pnl["marketing"]
    shared = pnl["marketing"] - directed_total

    units_total = sum(v["sold"] for v in sales.values())
    rows = []
    for c, v in sales.items():
        cost = product_cost * by_cogs[c]
        gm = net[c] - cost
        carry = logistics * by_slots[c]
        cm_pre = gm - carry - pay * by_net[c]
        marketing = directed[c] + shared * by_net[c]
        rows.append({
            "code": c, "name": params.sku(c)["name"],
            "category": params.sku(c)["category"],
            "units": v["sold"], "wanted": v["want"],
            "short": max(0.0, v["want"] - v["sold"]),
            "unit_share": v["sold"] / units_total if units_total > 0 else 0.0,
            "typical_share": v["base"],
            "net_sales": net[c], "sales_share": by_net[c],
            "price": v["net_price"], "list_price": float(params.sku(c)["list_price"]),
            "relative_price": v["relative_price"],
            "gross_margin": gm, "gm_pct": gm / net[c] if net[c] > 0 else 0.0,
            "delivery_cost": carry,
            "cm_pre": cm_pre, "cm_pre_pct": cm_pre / net[c] if net[c] > 0 else 0.0,
            "marketing": marketing, "cm": cm_pre - marketing,
            "seg_pull": v["seg_pull"], "price_pull": v["price_pull"],
            "pushed_units": v["pushed_units"], "pack_units": v["pack_units"],
            "campaigns": [name or targeting.CHANNEL_NAMES[ch]
                          for ch, name, *_ in v.get("campaigns", [])],
            "buyers": v["buyers"],
            "return_propensity": float(params.sku(c)["return_propensity"]),
        })
    rows.sort(key=lambda r: -r["net_sales"])
    for r in rows:
        r["why"] = why(r, params)
    return rows


def why(r: dict, params) -> list[str]:
    """The reasons a line sold the way it did, biggest first."""
    out = []
    names = {s["code"]: s["name"] for s in params.segments}
    top = (params.audience(r["code"]) or {}).get("segment_1")
    if r["units"] > 0 and r["pushed_units"] / r["units"] >= 0.08:
        who = ", ".join(dict.fromkeys(r["campaigns"])) or "a product campaign"
        out.append(f"{r['pushed_units'] / r['units']:.0%} of its units came in "
                   f"through {who}")
    if r["units"] > 0 and r["pack_units"] / r["units"] >= 0.08:
        out.append(f"{r['pack_units'] / r['units']:.0%} of its units sold in 3-packs")
    if r["price_pull"] >= 1.08:
        out.append(f"priced {-r['relative_price']:.0%} below the rest of your range")
    elif r["price_pull"] <= 0.92:
        out.append(f"priced {r['relative_price']:.0%} above the rest of your range")
    if top in names and r["seg_pull"] >= 1.08:
        out.append(f"your customers lean to {names[top]}, its main buyers")
    elif top in names and r["seg_pull"] <= 0.92:
        out.append(f"fewer of your customers are {names[top]}, its main buyers, "
                   f"than at other stores")
    if r["wanted"] > 0 and r["short"] / r["wanted"] >= 0.01:
        out.append(f"ran out: {r['short']:,.0f} units short of demand - stock is "
                   f"split by last month's sales and lands a month later, so a line "
                   f"you push needs more stock bought or more safety cover")
    if r["net_sales"] > 0 and r["delivery_cost"] / r["net_sales"] >= 0.25:
        out.append(f"delivery and packing take {r['delivery_cost'] / r['net_sales']:.0%} "
                   f"of what it sells for - it pays as an add-on or a pack, not alone")
    if r["return_propensity"] >= 1.1:
        out.append("sent back more often than most lines")
    return out


# --- What the buyer orders next --------------------------------------------------------

def demand_shares(team, params) -> dict[str, float]:
    """Last month's demand by product, the split a buyer plans stock on.

    Falls back to the catalogue for a month with no product record, and for a
    line that sold nothing because it was not on the shelf.
    """
    base = catalogue_shares(team, params)
    last = (team.history[-1].get("products") if team.history else None) or []
    wanted = {r["code"]: float(r.get("wanted") or 0.0) for r in last if r.get("code") in base}
    total = sum(wanted.values())
    if total <= 0:
        return base
    covered = sum(base[c] for c in wanted)
    raw = {c: wanted[c] / total * covered if c in wanted else base[c] for c in base}
    norm = sum(raw.values()) or 1.0
    return {c: v / norm for c, v in raw.items()}


def allocate(team, params, units: float) -> dict[str, float]:
    """Split a purchase order across the range to fill the gaps demand left.

    Each line is brought toward its share of the position after the order
    arrives - stock on hand plus stock on order - so a line that sold out
    gets more and a line sitting on cover gets less. When every line is
    already proportional this is a plain split by demand.
    """
    shares = demand_shares(team, params)
    position = {c: team.inventory.get(c, 0.0)
                + sum(po["units"].get(c, 0.0) for po in team.open_pos) for c in shares}
    target = sum(position.values()) + units
    need = {c: max(0.0, target * s - position[c]) for c, s in shares.items()}
    total = sum(need.values())
    if total <= 0:
        return {c: units * s for c, s in shares.items()}
    return {c: units * n / total for c, n in need.items()}


# --- Saying it in a sentence -----------------------------------------------------------

def _k(v: float) -> str:
    if abs(v) >= 1e6:
        return f"PKR {v / 1e6:,.2f}M"
    if abs(v) >= 10_000:
        return f"PKR {v / 1e3:,.0f}k"
    return f"PKR {v:,.0f}"


def headline(products: list[dict], segments: dict[str, float],
             names: dict[str, str]) -> list[str]:
    """What sold, what earned, what lost, and who bought - in four lines."""
    if not products:
        return []
    out = []
    top = products[:3]
    out.append("Best sellers: " + ", ".join(
        f"{r['name']} ({r['sales_share']:.0%} of sales)" for r in top) + ".")
    best = max(products, key=lambda r: r["cm"])
    if best["cm"] > 0:
        out.append(f"Most contribution after marketing: {best['name']} "
                   f"({_k(best['cm'])}).")
    losing = [r for r in sorted(products, key=lambda r: r["cm"]) if r["cm"] < 0]
    if losing:
        more = f" and {len(losing) - 3} more" if len(losing) > 3 else ""
        out.append("Losing money after marketing: " + ", ".join(
            f"{r['name']} ({_k(r['cm'])})" for r in losing[:3]) + more + ".")
    else:
        out.append("Every line paid for itself after marketing.")
    movers = sorted((r for r in products if r["typical_share"] > 0
                     and abs(r["unit_share"] / r["typical_share"] - 1) >= 0.15),
                    key=lambda r: -abs(r["unit_share"] / r["typical_share"] - 1))[:3]
    if movers:
        out.append("Selling unlike a typical store: " + "; ".join(
            f"{r['name']} {r['unit_share'] / r['typical_share'] - 1:+.0%}"
            + (f" ({r['why'][0]})" if r.get("why") else "") for r in movers) + ".")
    if segments:
        out.append("Your orders came from " + ", ".join(
            f"{names.get(s, s)} {v:.0%}"
            for s, v in sorted(segments.items(), key=lambda kv: -kv[1])) + ".")
    return out
