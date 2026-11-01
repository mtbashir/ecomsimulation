"""How each month's orders were shared, for the instructor.

The market's orders (M1, M7), each store's attractiveness to each customer
segment (M7), each team's visitors and conversion (M6, M8), and the orders it
realised (M8) - from the engine's own numbers for the month, recorded in ctx
while it ran. `capture` turns one month's ctx into a record; `build` writes a
game's months as an Excel workbook, from the decisions that ran to the orders
they won.

Nothing here feeds back into the engine.
"""
from __future__ import annotations

import io
import math

SCORES = (("price", "Price"), ("over_price", "Over what the segment pays"),
          ("quality", "Perceived quality"), ("delivery", "Perceived delivery"),
          ("instock", "In stock"), ("brand", "Brand"), ("fit", "Range fit"))
CR_PARTS = (("base", "Base rate"), ("price", "Price"), ("website", "Website"),
            ("rating", "Customer rating"), ("stock", "In stock"),
            ("payment", "Payment and cash on delivery"), ("delivery", "Perceived delivery"),
            ("range", "Range fit"), ("free_delivery", "Free-delivery threshold"))
BOUND = {"under_marketing": "Traffic (too few visitors)", "stock_out": "Stock",
         "wasted_spend": "Demand (more visitors than buyers)", "balanced": "Balanced"}


def capture(world, params, ctx) -> dict:
    """One month's allocation, from the ctx of the run that made it."""
    sd = ctx["share_detail"]
    pools = sd["pools"]
    market = {
        "month": world.round,
        "category_size": sd["category_size"],
        "avg_order": sd["avg_order"],
        "orders": sd["orders"],
        "beta": sd["beta"],
        "season": ctx.get("season", 1.0),
        "events": list(ctx.get("event_codes", []) or []),
        "pools": dict(pools),
        "segments": [(s["code"], s["name"]) for s in params.segments],
        "ai": [{"id": inc["id"], "name": inc.get("name", inc["id"]),
                "utility": inc["utility"], "won": dict(sd["won"][inc["id"]]),
                "total": sum(sd["won"][inc["id"]].values())}
               for inc in world.incumbents],
    }
    teams = {}
    for tid, team in world.teams.items():
        won = sd["won"][tid]
        split = ctx.get("sessions_split", {}).get(tid, {})
        own_sessions = sum(split.get(k, 0.0) for k in ("paid", "organic", "returning", "affiliate"))
        own = ctx["orders_own"][tid]
        reoffered = ctx["orders_reoffered"][tid]
        stock_cap = ctx.get("stock_capacity", {}).get(tid, math.inf)
        teams[tid] = {
            "inputs": sd["inputs"][tid],
            "parts": sd["parts"][tid],
            "utility": dict(sd["utility"][tid]),
            "focus": dict(sd["focus"][tid]),
            "won": dict(won),
            "share": {k: won[k] / pools[k] if pools[k] else 0.0 for k in won},
            "contested": sum(won.values()),
            "repeat": ctx["repeat_demand"][tid],
            "potential": ctx["potential"][tid],
            "retention_effect": ctx.get("retention_effect", {}).get(tid, 0.0),
            "discount": ctx.get("discount", {}).get(tid, 0.0),
            "creative_quality": team.creative_quality,
            "sessions": {k: split.get(k, 0.0) for k in
                         ("paid", "organic", "returning", "affiliate", "marketplace")},
            "own_sessions": own_sessions,
            "cr": dict(ctx.get("cr_parts", {}).get(tid, {})),
            "conversion_rate": ctx["conversion_rate"][tid],
            "cold_cr": ctx.get("cold_cr", {}).get(tid, ctx["conversion_rate"][tid]),
            "paid_cvr_mult": ctx.get("paid_cvr_mult", {}).get(tid, 1.0),
            "traffic_capacity": ctx["traffic_capacity"][tid],
            "stock_capacity": None if math.isinf(stock_cap) else stock_cap,
            "own": own,
            "reoffered": reoffered - own,
            "marketplace": ctx["orders"][tid] - reoffered,
            "orders": ctx["orders"][tid],
            "binding": ctx.get("binding_constraint", {}).get(tid, ""),
            "decisions": dict(ctx["resolved"][tid]),
            "products": len(getattr(team, "active_skus", None) or []),
        }
    return {"market": market, "teams": teams}


# --- The workbook --------------------------------------------------------------------

# The decisions that move orders, in the order of the chain they feed.
# (code, what it drives)
DRIVERS = [
    ("1.1", "Price index and range fit (prices, discounts and the range)"),
    ("1.5", "Quality tier: range fit by segment, and real quality"),
    ("2.4", "Conversion (free-delivery threshold) and basket size"),
    ("3.1", "Paid visitors (Meta)"),
    ("3.2", "Paid visitors (Google Search)"),
    ("3.4", "Paid visitors (TikTok)"),
    ("3.10", "Paid visitors and their conversion (campaign aim)"),
    ("3.6", "Affiliate visitors"),
    ("3.8", "Creative quality: perceived quality and ad efficiency"),
    ("3.9", "Brand: attractiveness, organic visitors, perception"),
    ("4.1", "Marketplace orders"),
    ("5.1", "Website score: conversion and organic visitors, from next month"),
    ("6.1", "Repeat demand from existing customers"),
    ("7.1", "Stock: what can be sold, once it lands"),
    ("7.4", "Real quality, then rating and perception"),
    ("8.5", "Rating, through packaging"),
    ("9.1", "Conversion (payment)"),
    ("9.2", "Payment mix"),
    ("9.3", "Conversion (payment success)"),
    ("10.1", "Rating, through service"),
    ("10.4", "Conversion and returns"),
    ("11.1", "Basket size, once live"),
    ("11.4", "Service capacity, once live"),
]


def build(months: list[dict], labels: dict[str, str], describe, checks: dict | None = None,
          game: str = "") -> bytes:
    """The game's allocation, month by month, as an xlsx.

    months: capture() records in month order; labels: team id -> "Team 1 · Tarz";
    describe(code, value) -> text for a decision's setting; checks: month ->
    (ok, note) on whether the rebuilt month matches the one recorded."""
    import xlsxwriter

    buf = io.BytesIO()
    book = xlsxwriter.Workbook(buf, {"in_memory": True})
    f = _formats(book)
    checks = checks or {}
    order = sorted({tid for m in months for tid in m["teams"]})
    segs = months[0]["market"]["segments"] if months else []

    _readme(book, f, game, months, checks)
    _market_sheet(book, f, months, segs, labels, checks)
    _orders_sheet(book, f, months, order, labels, segs)
    _attract_sheet(book, f, months, order, labels, segs)
    _conversion_sheet(book, f, months, order, labels)
    for tid in order:
        _team_sheet(book, f, months, tid, labels.get(tid, tid), segs, describe)
    book.close()
    return buf.getvalue()


def _formats(book):
    base = {"font_name": "Arial", "font_size": 10}
    mk = lambda **kw: book.add_format({**base, **kw})
    return {
        "title": mk(bold=True, font_size=14),
        "h": mk(bold=True, bg_color="#131316", font_color="#FFFFFF", text_wrap=True, valign="top"),
        "grp": mk(bold=True, bg_color="#EDEDF0"),
        "txt": mk(text_wrap=True, valign="top"),
        "b": mk(bold=True),
        "note": mk(italic=True, font_color="#6B6B76", text_wrap=True, valign="top"),
        "int": mk(num_format='#,##0;(#,##0);"-"'),
        "pkr": mk(num_format='#,##0;(#,##0);"-"'),
        "m": mk(num_format='#,##0.0,,"M";(#,##0.0,,"M");"-"'),
        "pct": mk(num_format='0.0%;(0.0%);"-"'),
        "n3": mk(num_format='0.000;(0.000);"-"'),
        "n2": mk(num_format='0.00;(0.00);"-"'),
        "ok": mk(font_color="#006300"),
        "bad": mk(font_color="#D03B3B", bold=True),
    }


def _readme(book, f, game, months, checks):
    ws = book.add_worksheet("Read me")
    ws.set_column(0, 0, 110)
    lines = [
        (f"How the market's orders were shared{' - ' + game if game else ''}", "title"),
        ("", None),
        ("Every month the engine makes the market's orders and shares them out in this order "
         "(docs/00-game-world.md and docs/07-engine-chain.md):", "txt"),
        ("1. Market size (M1): PKR, grown each month, times the seasonal index, after any event.", "txt"),
        ("2. Orders: market size divided by last month's average order value.", "txt"),
        ("3. Segments: those orders split by customer segment (fixed shares).", "txt"),
        ("4. Attractiveness (M7): each store, team or AI competitor, gets a utility per segment = "
         "sum of weight x score for price, perceived quality, perceived delivery, in stock, brand and "
         "range fit, less a penalty for pricing above what the segment pays. The segment's orders "
         "are shared in proportion to exp(sensitivity x utility) x the team's founding focus.", "txt"),
        ("5. Repeat demand: each team's own customers coming back, not contested. "
         "Demand = contested orders won + repeat demand.", "txt"),
        ("6. Orders realised (M8): the smallest of demand, traffic capacity (visitors x conversion) "
         "and stock. Unserved demand is offered twice to teams with room; the rest is lost.", "txt"),
        ("7. Marketplace orders (listed teams) come on top, from the marketplace's own shoppers.", "txt"),
        ("", None),
        ("Sheets", "b"),
        ("Market: the market each month - size, orders, segments, what the AI competitors and the "
         "teams won, and what was lost.", "txt"),
        ("Orders by team: each team's contested orders by segment, repeat demand, traffic and "
         "stock capacity, orders, and what bound.", "txt"),
        ("Attractiveness: the six scores each team had, its utility and share in each segment.", "txt"),
        ("Conversion: visitors by source and the conversion rate, factor by factor.", "txt"),
        ("One sheet per team: the decisions that ran each month, the factors they produced, and "
         "the orders - top to bottom, decision to order.", "txt"),
        ("", None),
        ("How these numbers were made", "b"),
        ("Each month is rebuilt by running the engine again from the saved game at the end of the "
         "month before, with the decisions that ran. A month whose rebuilt orders, demand and "
         "visitors match the ones recorded at the time is marked as matching on the Market sheet; "
         "one that does not (the engine changed after the month was played) is flagged, and its "
         "factors are today's engine's reading of that month.", "txt"),
        ("These are the simulation's numbers, not market data.", "note"),
    ]
    for i, (text, fmt) in enumerate(lines):
        ws.write(i, 0, text, f[fmt] if fmt else None)


def _hdr(ws, f, row, heads, widths=None):
    for c, h in enumerate(heads):
        ws.write(row, c, h, f["h"])
    if widths:
        for c, w in enumerate(widths):
            ws.set_column(c, c, w)
    ws.set_row(row, 42)


def _market_sheet(book, f, months, segs, labels, checks):
    ws = book.add_worksheet("Market")
    ais = months[0]["market"]["ai"] if months else []
    heads = (["Month", "Market size (PKR)", "Seasonal index", "Events", "Average order last month (PKR)",
              "Contested orders"]
             + [f"{n} orders" for _, n in segs]
             + [f"Won by {a['name']}" for a in ais]
             + ["Won by teams", "Repeat demand (teams)", "Teams' demand", "Orders served (teams)",
                "of which marketplace", "Demand not served", "Rebuilt month matches the record?"])
    _hdr(ws, f, 0, heads, [7, 15, 9, 14, 13, 12] + [12] * len(segs) + [14] * len(ais)
         + [12, 12, 12, 12, 11, 12, 40])
    ws.freeze_panes(1, 1)
    for r, m in enumerate(months, start=1):
        mk, t = m["market"], m["teams"].values()
        ws.write(r, 0, mk["month"], f["int"])
        ws.write(r, 1, mk["category_size"], f["pkr"])
        ws.write(r, 2, mk["season"], f["n2"])
        ws.write(r, 3, ", ".join(mk["events"]) or "-", f["txt"])
        ws.write(r, 4, mk["avg_order"], f["pkr"])
        ws.write(r, 5, mk["orders"], f["int"])
        c = 6
        for code, _ in segs:
            ws.write(r, c, mk["pools"].get(code, 0.0), f["int"]); c += 1
        for a in mk["ai"]:
            ws.write(r, c, a["total"], f["int"]); c += 1
        won = sum(x["contested"] for x in t)
        repeat = sum(x["repeat"] for x in t)
        demand = sum(x["potential"] for x in t)
        served = sum(x["orders"] for x in t)
        mp = sum(x["marketplace"] for x in t)
        for v in (won, repeat, demand, served, mp, max(0.0, demand - (served - mp))):
            ws.write(r, c, v, f["int"]); c += 1
        ok, note = checks.get(mk["month"], (None, ""))
        ws.write(r, c, note or ("Yes" if ok else ""), f["ok"] if ok else f["bad"])


def _orders_sheet(book, f, months, order, labels, segs):
    ws = book.add_worksheet("Orders by team")
    heads = (["Month", "Team"] + [f"Won: {n}" for _, n in segs]
             + ["Contested orders won", "Share of contested orders", "Repeat demand", "Demand",
                "Visitors (own site)", "Conversion rate", "Traffic capacity", "Stock capacity",
                "Orders before re-offer", "From demand re-offered", "Marketplace orders",
                "Orders", "What bound"])
    _hdr(ws, f, 0, heads, [7, 24] + [12] * len(segs) + [12] * 12 + [26])
    ws.freeze_panes(1, 2)
    r = 1
    for m in months:
        for tid in order:
            x = m["teams"].get(tid)
            if x is None:
                continue
            ws.write(r, 0, m["market"]["month"], f["int"])
            ws.write(r, 1, labels.get(tid, tid), f["txt"])
            c = 2
            for code, _ in segs:
                ws.write(r, c, x["won"].get(code, 0.0), f["int"]); c += 1
            vals = [(x["contested"], "int"), (x["contested"] / max(m["market"]["orders"], 1.0), "pct"),
                    (x["repeat"], "int"), (x["potential"], "int"), (x["own_sessions"], "int"),
                    (x["conversion_rate"], "pct"), (x["traffic_capacity"], "int")]
            for v, fm in vals:
                ws.write(r, c, v, f[fm]); c += 1
            if x["stock_capacity"] is None:
                ws.write(r, c, "no limit", f["txt"])
            else:
                ws.write(r, c, x["stock_capacity"], f["int"])
            c += 1
            for v in (x["own"], x["reoffered"], x["marketplace"], x["orders"]):
                ws.write(r, c, v, f["int"]); c += 1
            ws.write(r, c, BOUND.get(x["binding"], x["binding"]), f["txt"])
            r += 1


def _attract_sheet(book, f, months, order, labels, segs):
    ws = book.add_worksheet("Attractiveness")
    heads = (["Month", "Team", "Price index", "Perceived quality", "Perceived delivery", "In stock",
              "Brand"]
             + [f"Range fit: {n}" for _, n in segs]
             + [f"Utility: {n}" for _, n in segs]
             + [f"Focus: {n}" for _, n in segs]
             + [f"Share: {n}" for _, n in segs])
    _hdr(ws, f, 0, heads, [7, 24] + [10] * (5 + 4 * len(segs)))
    ws.freeze_panes(1, 2)
    r = 1
    for m in months:
        for tid in order:
            x = m["teams"].get(tid)
            if x is None:
                continue
            i = x["inputs"]
            ws.write(r, 0, m["market"]["month"], f["int"])
            ws.write(r, 1, labels.get(tid, tid), f["txt"])
            c = 2
            for k in ("price_index", "quality", "delivery", "instock", "brand"):
                ws.write(r, c, i[k], f["n3"]); c += 1
            for block, fm in ((i["fit"], "n3"), (x["utility"], "n3"), (x["focus"], "n2"),
                              (x["share"], "pct")):
                for code, _ in segs:
                    ws.write(r, c, block.get(code, 0.0), f[fm]); c += 1
            r += 1
        # The AI competitors, for comparison: a fixed utility in every segment.
        for a in m["market"]["ai"]:
            ws.write(r, 0, m["market"]["month"], f["int"])
            ws.write(r, 1, a["name"] + " (AI)", f["note"])
            c = 2 + 5 + len(segs)
            for code, _ in segs:
                ws.write(r, c, a["utility"], f["n3"]); c += 1
            c += len(segs)
            for code, _ in segs:
                pool = m["market"]["pools"].get(code, 0.0)
                ws.write(r, c, a["won"].get(code, 0.0) / pool if pool else 0.0, f["pct"]); c += 1
            r += 1


def _conversion_sheet(book, f, months, order, labels):
    ws = book.add_worksheet("Conversion")
    heads = (["Month", "Team", "Paid visitors", "Organic visitors", "Returning visitors",
              "Affiliate visitors", "Visitors (own site)"]
             + [n for _, n in CR_PARTS]
             + ["Conversion rate", "Campaign aim (paid visitors)", "Cold-visitor conversion",
                "Traffic capacity", "Website score", "Customer rating"])
    _hdr(ws, f, 0, heads, [7, 24] + [11] * (5 + len(CR_PARTS) + 6))
    ws.freeze_panes(1, 2)
    r = 1
    for m in months:
        for tid in order:
            x = m["teams"].get(tid)
            if x is None:
                continue
            ws.write(r, 0, m["market"]["month"], f["int"])
            ws.write(r, 1, labels.get(tid, tid), f["txt"])
            c = 2
            for k in ("paid", "organic", "returning", "affiliate"):
                ws.write(r, c, x["sessions"][k], f["int"]); c += 1
            ws.write(r, c, x["own_sessions"], f["int"]); c += 1
            for k, _ in CR_PARTS:
                v = x["cr"].get(k)
                ws.write(r, c, v if v is not None else "", f["pct"] if k == "base" else f["n3"]); c += 1
            ws.write(r, c, x["conversion_rate"], f["pct"]); c += 1
            ws.write(r, c, x["paid_cvr_mult"], f["n3"]); c += 1
            ws.write(r, c, x["cold_cr"], f["pct"]); c += 1
            ws.write(r, c, x["traffic_capacity"], f["int"]); c += 1
            ws.write(r, c, x["cr"].get("ux_score", ""), f["n3"]); c += 1
            ws.write(r, c, x["cr"].get("rating_value", ""), f["n2"]); c += 1
            r += 1


def _sheet_name(label: str, used: set) -> str:
    bad = '[]:*?/\\'
    name = "".join("-" if ch in bad else ch for ch in label)[:31]
    base, n = name, 2
    while name.lower() in used:
        name = f"{base[:28]} {n}"; n += 1
    used.add(name.lower())
    return name



def _team_sheet(book, f, months, tid, label, segs, describe):
    ws = book.add_worksheet(_sheet_name(label, {s.name.lower() for s in book.worksheets()}))
    present = [m for m in months if tid in m["teams"]]
    ws.set_column(0, 0, 44)
    ws.set_column(1, 1, 46)
    ws.set_column(2, 2 + len(present), 13)
    ws.write(0, 0, label, f["title"])
    ws.write(1, 0, "From the decisions that ran to the orders they won, month by month. "
                   "Decisions carried from an earlier month count as the ones that ran.", f["note"])
    _hdr(ws, f, 3, ["", "What it drives"] + [f"Month {m['market']['month']}" for m in present])
    ws.freeze_panes(4, 2)
    r = 4

    def group(title):
        nonlocal r
        ws.merge_range(r, 0, r, 1 + len(present), title, f["grp"])
        r += 1

    def row(name, drives, values, fmt):
        nonlocal r
        ws.write(r, 0, name, f["txt"])
        ws.write(r, 1, drives, f["note"])
        for j, v in enumerate(values):
            if v is None or v == "":
                ws.write(r, 2 + j, "")
            elif isinstance(v, str):
                ws.write(r, 2 + j, v, f["txt"])
            else:
                ws.write(r, 2 + j, v, f[fmt])
        r += 1

    X = [m["teams"][tid] for m in present]

    group("1 · Decisions that ran")
    row("Products on sale", "Range fit (breadth)", [x["products"] for x in X], "int")
    row("Average discount", "Price index", [x["discount"] for x in X], "pct")
    for code, drives in DRIVERS:
        vals = [describe(code, x["decisions"].get(code)) for x in X]
        if not any(vals):
            continue
        row(f"{code} {_name(code)}", drives, vals, "txt")

    group("2 · Factors the engine read (M5, M6, M7, M8)")
    row("Price index (1.00 = market average)", "1.1 prices and discounts, against every store",
        [x["inputs"]["price_index"] for x in X], "n3")
    row("Perceived quality (0-1)", "3.8 creative, 3.9 brand, customer rating",
        [x["inputs"]["quality"] for x in X], "n3")
    row("Perceived delivery (0-1)", "3.9 brand, customer rating", [x["inputs"]["delivery"] for x in X], "n3")
    row("In stock (share of the range)", "7.1 stock bought in earlier months",
        [x["inputs"]["instock"] for x in X], "pct")
    row("Brand equity (0-1)", "3.9 brand spend, last three months", [x["inputs"]["brand"] for x in X], "n3")
    row("Creative quality (0-1)", "3.8 creative production", [x["creative_quality"] for x in X], "n3")
    for code, name in segs:
        row(f"Range fit: {name}", "1.1 range breadth, 1.5 quality tier",
            [x["inputs"]["fit"].get(code, 0.5) for x in X], "n3")
    row("Website score (0-1)", "5.1 website spend, the month before", [x["cr"].get("ux_score") for x in X], "n3")
    row("Customer rating (1-5)", "Service, delivery, packaging, quality", [x["cr"].get("rating_value") for x in X], "n2")
    row("Retention effect (0-1)", "6.1 CRM and retention", [x["retention_effect"] for x in X], "n3")

    group("3 · Attractiveness and the orders won in each segment (M7)")
    for code, name in segs:
        row(f"Utility: {name}", "Sum of weight x score, less over-price penalty",
            [x["utility"].get(code, 0.0) for x in X], "n3")
    for code, name in segs:
        row(f"Founding focus: {name}", "Segments chosen at founding (x1 if none)",
            [x["focus"].get(code, 1.0) for x in X], "n2")
    for code, name in segs:
        row(f"Share of {name}", "exp(sensitivity x utility) x focus, against every store",
            [x["share"].get(code, 0.0) for x in X], "pct")
    for code, name in segs:
        row(f"Orders won: {name}", "Share x the segment's orders", [x["won"].get(code, 0.0) for x in X], "int")
    row("Contested orders won", "All segments", [x["contested"] for x in X], "int")
    row("Repeat demand", "Customers kept (6.1 CRM, service, rating)", [x["repeat"] for x in X], "int")
    row("Demand", "Contested + repeat", [x["potential"] for x in X], "int")

    group("4 · Visitors and conversion (M6, M8)")
    row("Paid visitors", "3.1-3.4 budgets, 3.10 campaigns, 3.8 creative", [x["sessions"]["paid"] for x in X], "int")
    row("Organic visitors", "3.9 brand, 5.1 website", [x["sessions"]["organic"] for x in X], "int")
    row("Returning visitors", "Existing customers", [x["sessions"]["returning"] for x in X], "int")
    row("Affiliate visitors", "3.6 commission", [x["sessions"]["affiliate"] for x in X], "int")
    for k, name in CR_PARTS:
        row(f"Conversion factor: {name}", _CR_DRIVES.get(k, ""), [x["cr"].get(k) for x in X],
            "pct" if k == "base" else "n3")
    row("Conversion rate", "Base x every factor", [x["conversion_rate"] for x in X], "pct")
    row("Traffic capacity", "Visitors x conversion", [x["traffic_capacity"] for x in X], "int")

    group("5 · Orders (M8)")
    row("Stock capacity", "Orders the stock on hand could fill", [
        x["stock_capacity"] if x["stock_capacity"] is not None else "no limit" for x in X], "int")
    row("Orders before re-offer", "Smallest of demand, traffic capacity, stock", [x["own"] for x in X], "int")
    row("From demand re-offered", "Other teams' unserved demand", [x["reoffered"] for x in X], "int")
    row("Marketplace orders", "4.1", [x["marketplace"] for x in X], "int")
    row("Orders", "", [x["orders"] for x in X], "int")
    row("What bound", "The smallest of the three", [BOUND.get(x["binding"], x["binding"]) for x in X], "txt")


_CR_DRIVES = {
    "base": "The market's base rate",
    "price": "Price index (1.1)",
    "website": "Website score (5.1, the month before)",
    "rating": "Customer rating, the month before",
    "stock": "In stock (7.1)",
    "payment": "9.1 cash on delivery, 9.3 gateway",
    "delivery": "Perceived delivery",
    "range": "Range fit",
    "free_delivery": "2.4 free-delivery threshold",
}


def _name(code: str) -> str:
    from .decisions import REGISTRY
    spec = REGISTRY.get(code)
    return spec.name if spec else ""
