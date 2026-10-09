"""Instructor debrief - what each team decided this month, and what it did.

The console already shows scores and KPI trends. This answers the question an
instructor asks before walking into the room: why is this team at the top and
that one at the bottom? Each team gets its results, the decisions it actually
took (and the ones it left at default), and plain-language observations drawn
from both - what worked, and what to raise.

Only what a team SUBMITTED counts as a decision. Anything else ran on the
default, and saying so is often the most useful line in the debrief.
"""
from __future__ import annotations

from html import escape

from . import mix
from .decisions import REGISTRY
from .modules.m03_supply import purchase_plan
from .modules.m09_basket import BUNDLE_UNITS, _unit_net_price
from .targeting import CHANNELS, CHANNEL_NAMES

AD_CODES = list(CHANNELS.values())                     # Meta, TikTok, Google
DEEP_PACK = 0.88      # deeper than ~12% off three singles, a pack loses money
SOURCING = {"local": "local", "import": "imported", "mixed": "mixed"}


def _money(v: float) -> str:
    v = float(v or 0)
    sign = "&minus;" if v < 0 else ""
    v = abs(v)
    return f"{sign}PKR {v / 1e6:,.2f}m" if v >= 1e6 else f"{sign}PKR {v:,.0f}"


def _default(code: str):
    return REGISTRY[code].default_when_disabled


def _label(code: str) -> str:
    return REGISTRY[code].name if code in REGISTRY else code


def _packs(team, params, sub: dict) -> list[tuple[str, float]]:
    """(product name, pack price / three singles) for each pack offered."""
    raw = sub.get("1.2") or {}
    cells = {c: {} for c in raw} if isinstance(raw, list) else dict(raw)
    out = []
    for code, cell in cells.items():
        try:
            ref = _unit_net_price(team, params, sub, code) * BUNDLE_UNITS
            price = float((cell or {}).get("price") or 0) or ref * 0.9
        except (KeyError, TypeError, ValueError):
            continue
        if ref > 0:
            out.append((str(params.sku(code)["name"]), price / ref))
    return out


def _decisions(team, params, sub: dict) -> list[tuple[str, str]]:
    """The decisions a team actually took, as (label, plain description)."""
    rows = []
    ads = {c: float(sub[c]) for c in AD_CODES if c in sub}
    if ads:
        names = {v: CHANNEL_NAMES[k] for k, v in CHANNELS.items()}
        rows.append(("Ad budgets", " · ".join(
            f"{names[c]} {_money(v)}" for c, v in ads.items())
            + f" &middot; total {_money(sum(ads.values()))}"))
    for code in ("3.8", "3.9", "6.1"):
        if code in sub:
            rows.append((_label(code), _money(sub[code])))
    grid = sub.get("1.1")
    if isinstance(grid, dict) and grid:
        prices = sum(1 for c in grid.values() if isinstance(c, dict) and c.get("price"))
        discs = sum(1 for c in grid.values() if isinstance(c, dict) and c.get("discount"))
        srcs = [c.get("sourcing") for c in grid.values()
                if isinstance(c, dict) and c.get("sourcing")]
        bits = []
        if prices:
            bits.append(f"{prices} price{'s' if prices != 1 else ''} changed")
        if discs:
            bits.append(f"{discs} line discount{'s' if discs != 1 else ''}")
        if srcs:
            kinds = sorted(set(srcs))
            bits.append(f"{len(srcs)} line{'s' if len(srcs) != 1 else ''} sourced "
                        + "/".join(SOURCING.get(k, k) for k in kinds))
        if bits:
            rows.append(("Prices and sourcing", ", ".join(bits)))
    packs = _packs(team, params, sub)
    if packs:
        avg = sum(1 - r for _, r in packs) / len(packs)
        where = (f"on average {avg:.0%} below three singles" if avg >= 0.005 else
                 f"on average {-avg:.0%} above three singles" if avg <= -0.005 else
                 "priced the same as three singles")
        rows.append(("Bundles", f"{len(packs)} pack{'s' if len(packs) != 1 else ''}, {where}"))
    if "2.4" in sub:
        v = float(sub["2.4"] or 0)
        rows.append(("Free delivery above", "every order" if v <= 0 else _money(v)))
    if "2.2" in sub and float(sub["2.2"] or 0):
        rows.append(("Site-wide discount", f"{float(sub['2.2']):.0%}"))
    for code in ("1.5", "8.5", "9.3", "9.1", "7.2"):
        if code in sub and sub[code] not in (None, ""):
            rows.append((_label(code), escape(str(sub[code]))))
    if "9.2" in sub:
        rows.append((_label("9.2"), f"{float(sub['9.2'] or 0):.0%}"))
    bought, lines = purchase_plan(sub.get("7.1"))
    if bought is not None:
        rows.append((_label("7.1"), f"{bought:,.0f} units"
                     + (f", product by product ({sum(1 for u in lines.values() if u > 0)} "
                        "products)" if lines else "")))
    if "7.5" in sub:
        rows.append((_label("7.5"), f"{float(sub['7.5']):g} weeks"))
    if "7.4" in sub:
        rows.append((_label("7.4"), _money(sub["7.4"])))
    if "5.1" in sub:
        rows.append((_label("5.1"), _money(sub["5.1"])))
    if sub.get("12.1"):
        studies = sub["12.1"] if isinstance(sub["12.1"], list) else str(sub["12.1"]).split(";")
        rows.append(("Research", ", ".join(escape(str(s)) for s in studies)))
    memo = str(sub.get("12.5") or "").strip()
    if memo:
        words = len(memo.split())
        cut = memo if len(memo) <= 220 else memo[:217].rsplit(" ", 1)[0] + "..."
        rows.append(("Board memo", f"&ldquo;{escape(cut)}&rdquo; "
                     f'<span class="mute">({words} words)</span>'))
    return rows


def _observations(team, params, sub, h, room, open_codes) -> tuple[list[str], list[str]]:
    """(what worked, what to raise) for one team."""
    good, watch = [], []
    tid = team.team_id

    # What held sales back this month - the label in the card's heading,
    # spelled out (same reading as the team's own report).
    binding = h.get("binding_constraint", "")
    missed = max(0.0, float(h.get("potential", 0) or 0) - float(h.get("orders", 0) or 0))
    lost = max(0.0, float(h.get("sellable", 0) or 0) - float(h.get("orders", 0) or 0))
    if binding == "balanced":
        good.append("Balanced month: demand, traffic and stock were in step, so little "
                    "was left on the table.")
    elif binding == "under_marketing":
        watch.append("Under-marketing: the offer was strong enough for more demand than "
                     "the traffic reached" + (f" (about {missed:,.0f} more orders were there "
                     f"to win)" if missed >= 1 else "") + ". More reach would have sold more.")
    elif binding == "wasted_spend":
        watch.append(f"Wasted spend: plenty of visitors, but rivals' offers took the demand "
                     f"(conversion {h.get('conversion_rate', 0):.2%}). Fix price, range or "
                     f"store before buying more traffic.")
    elif binding == "stock_out":
        watch.append("Stock-out: demand and traffic were both there and the stock ran out"
                     + (f", losing about {lost:,.0f} orders" if lost >= 1 else "") + ".")

    def best(key, label, fmt, low=False):
        vals = [r[key] for r in room.values()]
        if len(vals) < 2:
            return
        target = min(vals) if low else max(vals)
        if h[key] == target and len(set(vals)) > 1:
            good.append(f"{label} in the room ({fmt(h[key])}).")

    best("ebitda", "Highest EBITDA", _money)
    best("gross_margin_pct", "Best gross margin", lambda v: f"{v:.1%}")
    best("aov_net", "Biggest average order", _money)
    best("conversion_rate", "Best conversion", lambda v: f"{v:.2%}")
    if h["cac_blended"] > 0:
        best("cac_blended", "Lowest cost per new customer", _money, low=True)

    ebitdas = sorted(r["ebitda"] for r in room.values())
    if len(ebitdas) > 1 and h["ebitda"] == ebitdas[0] and h["ebitda"] < 0:
        watch.append(f"Biggest loss in the room: EBITDA {_money(h['ebitda'])}.")

    taken = [c for c in sub if c in open_codes] if open_codes else list(sub)
    if open_codes and not sub:
        watch.append("Submitted nothing: the whole month ran on default decisions.")
    elif open_codes and len(taken) <= max(2, len(open_codes) // 4):
        left = [c for c in open_codes if c not in sub]
        watch.append(f"Set only {len(taken)} of {len(open_codes)} open decisions; the "
                     f"rest ran on defaults ({', '.join(_label(c) for c in left[:4])}"
                     f"{'&hellip;' if len(left) > 4 else ''}).")

    default_ads = sum(float(_default(c) or 0) for c in AD_CODES)
    if any(c in sub for c in AD_CODES):
        ads = sum(float(sub.get(c, _default(c)) or 0) for c in AD_CODES)
        cacs = sorted(r["cac_blended"] for r in room.values() if r["cac_blended"] > 0)
        median = cacs[len(cacs) // 2] if cacs else 0
        if ads < 0.4 * default_ads:
            watch.append(f"Cut ad budgets to {_money(ads)} (default {_money(default_ads)}): "
                         f"{h['new_customers']:,.0f} new customers while fixed costs stayed "
                         f"the same.")
        elif ads > 1.6 * default_ads and h["cac_blended"] > median:
            watch.append(f"Spent {_money(ads)} on ads with a cost per new customer of "
                         f"{_money(h['cac_blended'])}, above the room's median.")

    packs = _packs(team, params, sub)
    if len(packs) > 3:
        watch.append(f"Offered {len(packs)} bundles; only the three most attractive "
                     f"count, so the rest add nothing.")
    dear = [(n, r) for n, r in packs if r > 1.0]
    if dear:
        n, r = max(dear, key=lambda x: x[1])
        watch.append(f"{len(dear)} pack{'s' if len(dear) != 1 else ''} priced above three "
                     f"singles (worst: {escape(n)} at {r - 1:.0%} over) - nobody buys a "
                     f"pack dearer than its singles, so {'they do' if len(dear) != 1 else 'it does'} nothing.")
    flat = [n for n, r in packs if 0.995 <= r <= 1.0]
    if flat:
        watch.append(f"{len(flat)} pack{'s' if len(flat) != 1 else ''} priced the same as "
                     f"three singles - with no saving, only a few convenience buyers take it.")
    deep = [(n, r) for n, r in packs if r < DEEP_PACK]
    if deep:
        watch.append(f"{len(deep)} pack{'s' if len(deep) != 1 else ''} discounted more "
                     f"than {1 - DEEP_PACK:.0%} - most pack buyers would have bought the "
                     f"units anyway, so the saving costs more than the extra units earn.")

    if "2.4" in sub and float(sub["2.4"] or 0) <= 0:
        watch.append("Free delivery on every order: a few more orders, but smaller "
                     "baskets carrying the same courier cost each.")
    if sub.get("9.3") == "B":
        watch.append("Cheapest payment gateway: 1 in 6 card payments fails, and "
                     "each failure is a lost order.")
    if sub.get("9.1") == "off":
        watch.append("Cash on delivery switched off: far fewer orders in a COD market.")

    demand_units = h["orders"] * params["units_per_order"]
    bought, _ = purchase_plan(sub.get("7.1"))
    if bought is not None and bought < 0.6 * demand_units:
        watch.append(f"Bought only {bought:,.0f} units against about "
                     f"{demand_units:,.0f} a month of demand: stock-out risk next month.")
    elif h.get("weeks_cover", 99) < 3:
        watch.append(f"Stock covers only {h['weeks_cover']:.1f} weeks of sales.")
    if "7.5" in sub and float(sub["7.5"] or 0) <= 2:
        watch.append(f"Safety stock of {float(sub['7.5']):g} weeks: little buffer "
                     f"if demand rises or a shipment is late.")

    grid = sub.get("1.1") if isinstance(sub.get("1.1"), dict) else {}
    srcs = [c.get("sourcing") for c in grid.values() if isinstance(c, dict)]
    if srcs and all(s == "local" for s in srcs if s) and any(srcs):
        watch.append("Sourced every changed line locally: fastest to restock, "
                     "and the most expensive per unit.")

    if "12.5" in open_codes or not open_codes:
        memo = str(sub.get("12.5") or "").strip()
        words = len(memo.split())
        if not memo:
            watch.append("No board memo (10% of the final score).")
        elif words < 30:
            watch.append(f"Board memo is {words} words: it should say what was decided, "
                         f"why, and the number that will prove it right.")
    return good, watch


TIER_WORD = {"premium": "premium", "mainstream": "mainstream", "standard": "standard",
             "economy": "economy", "value": "value"}


def _ordinal(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def _rank(room: dict, tid: str, key: str, low: bool = False) -> int:
    """Competition rank: ties share a place, the next one skips."""
    mine = room[tid].get(key, 0) or 0
    better = sum(1 for r in room.values()
                 if ((r.get(key, 0) or 0) < mine if low else (r.get(key, 0) or 0) > mine)
                 and abs((r.get(key, 0) or 0) - mine) > 1e-9)
    return better + 1


def _strategy(team, params, sub: dict, h: dict, room: dict) -> str:
    """The team's strategy in a few sentences: what it chose, and what that did.

    Built from its founding position, this month's decisions and where its
    results sit in the room. Each sentence ties a decision to an outcome.
    """
    tid, n = team.team_id, len(room)
    f = getattr(team, "founding", None)
    out = []

    # Position
    tier = str(sub.get("1.5") or (getattr(f, "tier", "") if f else "") or "")
    cats = ", ".join(getattr(f, "categories", []) or []) if f else ""
    segs = getattr(f, "segment_priority", []) if f else []
    pos = []
    if tier:
        pos.append(f"a {TIER_WORD.get(tier, tier)} position")
    if cats:
        pos.append(f"selling {escape(cats)}")
    if segs:
        names = {s["code"]: s["name"] for s in params.segments}
        pos.append("aimed at " + escape(", ".join(names.get(s, s) for s in segs[:2])))
    if pos:
        out.append(("A team with " if tier else "A team ") + " ".join(pos) + ".")

    # Marketing
    default_ads = sum(float(_default(c) or 0) for c in AD_CODES)
    ads = sum(float(sub.get(c, _default(c)) or 0) for c in AD_CODES)
    cac_rank = _rank(room, tid, "cac_blended", low=True) if h["cac_blended"] > 0 else n
    new_rank = _rank(room, tid, "new_customers")
    cost_word = ("the lowest" if cac_rank == 1 else "the highest" if cac_rank == n
                 else f"the {_ordinal(cac_rank)} lowest")
    if not any(c in sub for c in AD_CODES):
        out.append(f"Left ad budgets at the default {_money(default_ads)}: customers cost "
                   f"{_money(h['cac_blended'])} each, {cost_word} in the room.")
    elif ads < 0.4 * default_ads:
        out.append(f"Starved marketing at {_money(ads)} of ads ({ads / default_ads:.0%} of the "
                   f"default), so it won only {h['new_customers']:,.0f} new customers "
                   f"({_ordinal(new_rank)} of {n}) while fixed costs stayed the same.")
    elif ads > 1.6 * default_ads:
        verdict = ("and it paid off" if cac_rank <= n / 2 else
                   "but each customer cost more than most rivals'")
        out.append(f"Spent heavily on ads ({_money(ads)}, {ads / default_ads:.1f}&times; the "
                   f"default), {verdict}: CAC {_money(h['cac_blended'])}, {cost_word} in the room.")
    else:
        verdict = ("an efficient level of spend" if cac_rank <= n / 2 else
                   "though customers cost more than at most rivals")
        out.append(f"Spent {_money(ads)} on ads ({ads / default_ads:.0%} of the default) "
                   f"&mdash; {verdict}: CAC {_money(h['cac_blended'])}, {cost_word} in the room.")

    # Basket
    aov_rank = _rank(room, tid, "aov_net")
    packs = _packs(team, params, sub)
    fair = [r for _, r in packs if r < 0.995]
    threshold = float(sub["2.4"]) if "2.4" in sub else None
    drivers = []
    if fair:
        drivers.append(f"{min(len(fair), 3) if len(fair) > 3 else len(fair)} "
                       f"bundle{'s' if len(fair) != 1 else ''} with a saving"
                       + (f" (of {len(packs)} offered)" if len(packs) > len(fair) or len(packs) > 3 else ""))
    if threshold is not None and threshold > params["aov_base"]:
        drivers.append(f"free delivery only above {_money(threshold)}")
    if drivers:
        out.append(f"{' and '.join(drivers).capitalize()} pushed customers to add to the "
                   f"basket: average order {_money(h['aov_net'])}, {_ordinal(aov_rank)} in the room.")
    elif threshold is not None and threshold <= 0:
        out.append(f"Free delivery on every order gave customers no reason to add more: "
                   f"average order {_money(h['aov_net'])}, {_ordinal(aov_rank)} in the room.")
    elif aov_rank == n and n > 1:
        out.append(f"Nothing pushed basket size (no bundles, no delivery threshold above "
                   f"a typical order): the smallest average order in the room.")

    # Margin
    gm_rank = _rank(room, tid, "gross_margin_pct")
    grid = sub.get("1.1") if isinstance(sub.get("1.1"), dict) else {}
    srcs = {c.get("sourcing") for c in grid.values() if isinstance(c, dict) and c.get("sourcing")}
    why = []
    if tier == "premium":
        why.append("premium pricing")
    if srcs == {"import"}:
        why.append("imported stock")
    if srcs == {"local"}:
        why.append("locally sourced stock")
    if h.get("discount_rate", 0) >= 0.05:
        why.append(f"a {h['discount_rate']:.0%} average discount")
    if gm_rank == 1 and n > 1:
        out.append(f"{(' and '.join(why) or 'Its pricing').capitalize()} gave the best gross "
                   f"margin in the room ({h['gross_margin_pct']:.1%}).")
    elif gm_rank == n and n > 1:
        out.append(f"{(' and '.join(why) or 'Its cost base').capitalize()} left the thinnest "
                   f"gross margin in the room ({h['gross_margin_pct']:.1%}).")

    eb_rank = _rank(room, tid, "ebitda")
    out.append(f"Net result: EBITDA {_money(h['ebitda'])}, {_ordinal(eb_rank)} of {n}.")
    return " ".join(out)


RESULT_LINES = [
    [("Revenue", "revenue_net", _money, False),
     ("Sessions", "sessions", lambda v: f"{v:,.0f}", False),
     ("Orders", "orders", lambda v: f"{v:,.0f}", False),
     ("Conversion", "conversion_rate", lambda v: f"{v:.2%}", False),
     ("Avg order", "aov_net", _money, False),
     ("CAC", "cac_blended", _money, True),
     ("Repeat share", "repeat_order_share", lambda v: f"{v:.0%}", False)],
    [("Gross margin", "gross_margin_pct", lambda v: f"{v:.1%}", False),
     ("Contribution", "contribution_margin_pct", lambda v: f"{v:.1%}", False),
     ("EBITDA", "ebitda", _money, False),
     ("Cash", "cash_balance", _money, False),
     ("Service level", "service_level", lambda v: f"{v:.0%}", False),
     ("Weeks of cover", "weeks_cover", lambda v: f"{v:.1f}", False),
     ("Rating", "rating", lambda v: f"{v:.2f}", False)],
]


def _results(team, h: dict, room: dict, score) -> str:
    """One team's results in two lines, its rank in the room under each figure."""
    tid = team.team_id
    lines = []
    for i, cols in enumerate(RESULT_LINES):
        first = i == 0 and score is not None
        head = ("<th>Score</th>" if first else "<th></th>" if score is not None else "") \
            + "".join(f"<th>{label}</th>" for label, *_ in cols)
        vals = (f"<td><b>{score:.1f}</b></td>" if first else
                "<td></td>" if score is not None else "") \
            + "".join(f"<td>{fmt(h.get(key, 0) or 0)}</td>" for _, key, fmt, _ in cols)
        ranks = ("<td></td>" if score is not None else "") + "".join(
            f"<td>{_ordinal(_rank(room, tid, key, low))}</td>" for _, key, _, low in cols)
        lines.append(f'<tr class="hd">{head}</tr><tr>{vals}</tr><tr class="rk">{ranks}</tr>')
    return ('<table class="t res"><tbody>' + "".join(lines) + "</tbody></table>"
            '<p class="rk-note">Small figures: rank in the room.</p>')

def _campaigns(team, params, sub: dict, h: dict, room: dict, open_codes) -> str:
    """Performance-marketing read for one team: what each channel bought, the
    customer numbers behind it, and the next move, backed by those numbers."""
    from .targeting import CHANNEL_NAMES as NAMES, DECISION as SETUP
    tid, n = team.team_id, len(room)
    rows = h.get("campaigns") or []
    per = {}
    for r in rows:
        c = per.setdefault(r["channel"], {"spend": 0.0, "clicks": 0.0, "orders": 0.0,
                                          "new": 0.0, "broad": True})
        c["spend"] += r["spend"]
        c["clicks"] += r["clicks"]
        c["orders"] += r["orders"]
        c["new"] += r["orders"] * r.get("new_share", 0.0)
        c["broad"] &= str(r.get("name", "")).startswith("Broad")
    parts = []
    for ch, c in per.items():
        cvr = c["orders"] / c["clicks"] if c["clicks"] else 0.0
        c["cac"] = c["spend"] / c["new"] if c["new"] else 0.0
        parts.append(f"{NAMES.get(ch, ch)} {_money(c['spend'])} &rarr; "
                     f"{c['orders']:,.0f} orders, CVR {cvr:.2%}, CAC {_money(c['cac'])}")
    lines = []
    if parts:
        lines.append("Paid channels: " + " &middot; ".join(parts) + ".")
    else:
        lines.append("No paid media this month.")

    def med(key):
        vals = sorted(r.get(key, 0) or 0 for r in room.values())
        return vals[len(vals) // 2] if vals else 0
    lines.append(
        f"New customers {h.get('new_customers', 0):,.0f} "
        f"({_ordinal(_rank(room, tid, 'new_customers'))}); repeat orders "
        f"{h.get('repeat_order_share', 0):.0%} ({_ordinal(_rank(room, tid, 'repeat_order_share'))}); "
        f"store conversion {h.get('conversion_rate', 0):.2%} "
        f"({_ordinal(_rank(room, tid, 'conversion_rate'))} of {n}).")

    nxt = []
    priced = {ch: c for ch, c in per.items() if c["cac"] > 0}
    if len(priced) >= 2:
        best = min(priced, key=lambda ch: priced[ch]["cac"])
        worst = max(priced, key=lambda ch: priced[ch]["cac"])
        if priced[worst]["cac"] > 1.3 * priced[best]["cac"]:
            nxt.append(f"move budget in steps (say 20%) from {NAMES[worst]} (CAC "
                       f"{_money(priced[worst]['cac'])}) to {NAMES[best]} (CAC "
                       f"{_money(priced[best]['cac'])}), watching {NAMES[best]}'s CAC "
                       f"as it scales &mdash; returns fall as a channel grows")
    binding = h.get("binding_constraint", "")
    if binding == "under_marketing" and priced:
        best = min(priced, key=lambda ch: priced[ch]["cac"])
        if nxt and NAMES[best] in nxt[-1]:
            nxt[-1] += (f"; demand outran the traffic, so add to {NAMES[best]} rather "
                        f"than only moving budget into it")
        else:
            nxt.append(f"demand outran the traffic, so add reach first on {NAMES[best]}, "
                       f"the cheapest source of new customers (CAC "
                       f"{_money(priced[best]['cac'])})")
    elif binding == "wasted_spend":
        nxt.append(f"do not buy more traffic yet: conversion is {h.get('conversion_rate', 0):.2%} "
                   f"against a room median of {med('conversion_rate'):.2%}, so fix price, "
                   f"range or store first")
    rep, rep_med = h.get("repeat_order_share", 0), med("repeat_order_share")
    if rep < rep_med - 0.02:
        nxt.append(f"repeat orders are {rep:.0%} against a room median of {rep_med:.0%}: a "
                   f"CRM &amp; retention budget (6.1) wins a repeat order more cheaply than "
                   f"ads win a new customer")
    if per and all(c["broad"] for c in per.values()):
        if SETUP in (open_codes or []):
            nxt.append("every channel still runs one broad campaign: aim each budget at "
                       "the buyers of your products in Campaign setup")
        else:
            nxt.append("budgets run broad until campaign targeting opens in Session 7, so "
                       "for now the levers are how much to spend and where")
    if nxt:
        lines.append("<b>Next:</b> " + "; ".join(nxt[:3]) + ".")
    return " ".join(lines)


def _products(h: dict) -> str:
    """What sold, what earned, what lost and who bought - from the month's
    product P&L, so a portfolio conversation starts from the numbers."""
    lines = mix.headline(h.get("products") or [], h.get("order_segments") or {},
                         h.get("segment_names") or {})
    if not lines:
        return ""
    return (f'<p class="strat prod"><b>Products.</b> '
            f'{escape(" ".join(lines))}</p>')


def _decision_quality(t, h: dict, rejected: set, memo_url) -> str:
    """Rules v2: this month's decision-quality marks, and the memo verdict."""
    from .scoring import KEEP_SHARE, _decision_quality as marks
    d = h.get("decisions")
    if not d:
        return ""
    target = -(-int(d.get("open", 0)) * 3 // 4)
    rnd = int(h.get("round", 0))
    counts = (t.team_id, rnd) not in rejected
    memo = ("no memo" if not d.get("memo") else
            "memo counts (2)" if counts else "memo judged not to match (0)")
    toggle = ""
    if memo_url and d.get("memo"):
        toggle = (f'<form method="post" action="{escape(memo_url(t.team_id, rnd))}" class="mt">'
                  f'<input type="hidden" name="ok" value="{0 if counts else 1}">'
                  f'<button type="submit">{"Memo does not match" if counts else "Memo matches"}</button></form>')
    return (f'<p class="strat dq"><b>Decision quality this month: '
            f'{marks(t, h, rejected):.1f} of 10.</b> {int(d.get("taken", 0))} of '
            f'{int(d.get("open", 0))} decisions taken (full marks at {target}); {memo}.{toggle}</p>')


def section(ranked, params, submissions: dict, open_codes: list[str], name_of,
            scores: dict | None = None, flags: dict | None = None,
            workbook_url=None, memo_rejected: set | None = None, memo_url=None) -> str:
    """The debrief block for the console. Empty when no submissions are known."""
    if submissions is None:
        return ""
    room = {t.team_id: t.history[-1] for t in ranked}
    n = len(ranked)
    cards = []
    for i, t in enumerate(ranked, 1):
        h = t.history[-1]
        sub = submissions.get(t.team_id, {}) or {}
        good, watch = _observations(t, params, sub, h, room, open_codes)
        watch = list((flags or {}).get(t.team_id, [])) + watch
        tag = ("top" if i <= min(3, n // 2) else
               "bottom" if i > n - min(3, n // 2) else "")
        score = (scores or {}).get(t.team_id)
        strategy = _strategy(t, params, sub, h, room)
        took = _decisions(t, params, sub)
        took_html = ("".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in took)
                     if took else "<dt>Decisions</dt><dd>None submitted</dd>")
        defaulted = [c for c in open_codes if c not in sub] if open_codes else []
        left = (f'<p class="note">Left at default: '
                f'{escape(", ".join(_label(c) for c in defaulted))}.</p>'
                if defaulted and sub else "")
        lists = ""
        if good:
            lists += ('<div class="obs good"><b>What worked</b><ul>'
                      + "".join(f"<li>{g}</li>" for g in good) + "</ul></div>")
        if watch:
            lists += ('<div class="obs watch"><b>To raise</b><ul>'
                      + "".join(f"<li>{w}</li>" for w in watch) + "</ul></div>")
        cards.append(
            f'<div class="db {tag}"><h3>{i}. {escape(name_of(t))}'
            f'{"" if name_of(t) == t.team_id else f" <span class=tid>{t.team_id}</span>"}'
            f'{" <span class=pill>top</span>" if tag == "top" else ""}'
            f'{" <span class=pill>bottom</span>" if tag == "bottom" else ""}'
            f'<span class="tid"> &middot; {escape(str(h.get("binding_constraint", "")).replace("_", " "))}</span>'
            + (f' <a class="xl" href="{escape(workbook_url(t.team_id))}">Excel</a>' if workbook_url else '')
            + '</h3>'
            f'{_results(t, h, room, score)}'
            f'<p class="strat"><b>Strategy.</b> {strategy}</p>'
            f'<p class="strat camp"><b>Campaigns &amp; customers.</b> '
            f'{_campaigns(t, params, sub, h, room, open_codes)}</p>'
            f'{_products(h)}'
            f'{_decision_quality(t, h, memo_rejected or set(), memo_url)}'
            f'<div class="cols"><dl>{took_html}</dl>'
            f'<div>{lists}</div></div>{left}</div>')
    return ('<section class="wide"><h2>Debrief &middot; what each team decided '
            'and what it did</h2><p class="note">Ranked by score (shown here from month '
            '1; teams see the leaderboard from month 4). Decisions are what '
            'each team submitted for this month; anything not listed ran on its '
            'default. Observations are generated from the decisions and the '
            'results, for the instructor to check before using.</p>'
            + "".join(cards) + "</section>")


CSS = """
.db{border:1px solid #d6d5ce;border-left:4px solid #898781;border-radius:8px;
padding:14px 16px 8px;margin:0 0 22px;background:#fff}
.db.top{border-left-color:#006300} .db.bottom{border-left-color:#d03b3b}
.db h3{font-size:16px;margin:0 0 4px}
.db .pill{font-size:11px;font-weight:600;padding:1px 7px;border-radius:9px;
background:#e7f3e7;color:#006300;vertical-align:2px}
.db.bottom .pill{background:#fbe9e9;color:#d03b3b}
.db .strat.camp{background:#eef3fb}
.db h3 .xl{float:right;font-size:12px;font-weight:600;color:#2a78d6;text-decoration:none;
border:1px solid #d6d5ce;border-radius:6px;padding:2px 9px}
.db .strat.prod{background:#f3f7ef}
.db .strat.dq{background:#f6f2fb}
.db form.mt{display:inline;margin-left:8px}
.db form.mt button{font-size:12px;padding:2px 9px;border-radius:6px;border:1px solid #d6d5ce;
background:#fff;cursor:pointer}
.db .strat{font-size:14px;line-height:1.55;margin:8px 0 10px;padding:8px 10px;
background:#f3f2ee;border-radius:6px}
table.t.res{margin:6px 0 0;font-size:13px}
table.t.res tr.hd th{color:#52514e;font-weight:600;font-size:12px;border-bottom:none;padding-top:8px}
table.t.res tr.rk td{color:#898781;font-size:11.5px;padding-top:0}
table.t.res td,table.t.res th{text-align:right}
table.t.res td:first-child,table.t.res th:first-child{text-align:left}
.rk-note{font-size:11.5px;color:#898781;margin:2px 0 0}
.db .cols{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:820px){.db .cols{grid-template-columns:1fr}}
.db dl{margin:0;display:grid;grid-template-columns:150px 1fr;gap:3px 10px;font-size:13px}
.db dt{color:#52514e} .db dd{margin:0}
.db .mute{color:#898781}
.obs{font-size:13px;margin:0 0 8px} .obs ul{margin:4px 0 0;padding-left:18px}
.obs.good b{color:#006300} .obs.watch b{color:#d03b3b}
@media(prefers-color-scheme:dark){.db{border-top-color:#3a3a37;border-right-color:#3a3a37;border-bottom-color:#3a3a37;background:#1f1f1d}.db dt{color:#c3c2b7}.db .strat{background:#232321}.db .strat.camp{background:#1e2430}.db .strat.prod{background:#1f261c}}
"""
