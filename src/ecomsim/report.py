"""Per-team round report.

One self-contained HTML file per team per round - no server, no build step, and
it opens on a phone. Mirrors the six dashboard blocks from
docs/10-kpi-dictionary.md, with biased and purchased metrics marked.
"""
from __future__ import annotations

import math
from html import escape
from pathlib import Path

from . import funnel, mix
from .charts import CSS_TOKENS, sparkline

# (label, key, format, up_is_good). The last field is not decoration: a rising
# CAC and a rising debt balance are both bad news, and colouring them green
# tells a team the opposite of the truth.
BLOCKS = [
    ("Growth", "revenue_net", [
        ("Net revenue", "revenue_net", "pkr", True), ("Orders", "orders", "int", True),
        ("Sessions", "sessions", "int", True),
        ("Conversion rate", "conversion_rate", "pct2", True),
        ("AOV", "aov_net", "pkr", True), ("Market share", "market_share", "pct1*", True),
    ]),
    ("Marketing", "cac_blended", [
        ("Blended CAC", "cac_blended", "pkr", False),
        ("Reported ROAS", "roas_reported", "x!", True),
        ("Creative quality", "creative_quality", "score", True),
        ("New customers", "new_customers", "int", True),
        ("Marketing spend", "pnl.marketing", "pkr", True),
        ("Brand equity", "brand_equity", "score", True),
    ]),
    ("Commercial", "contribution_margin_pct", [
        ("Gross margin", "gross_margin_pct", "pct1", True),
        ("Contribution margin", "contribution_margin_pct", "pct1", True),
        ("EBITDA", "ebitda", "pkr", True),
        ("Discount rate", "discount_rate", "pct1", False),
        ("Fulfilment cost", "pnl.fulfilment", "pkr", False),
        ("Payment costs", "pnl.payment_costs", "pkr", False),
    ]),
    ("Operations", "service_level", [
        ("Service level", "service_level", "pct1", True),
        ("In-stock rate", "instock_rate", "pct1", True),
        ("Delivery success", "delivery_success", "pct1", True),
        ("RTO rate", "rto_rate", "pct1", False),
        ("Return rate", "return_rate", "pct1", False),
        ("Weeks of cover", "weeks_cover", "num1", True),
    ]),
    ("Customer", "repeat_order_share", [
        ("Active customers", "active_customers", "int", True),
        ("Repeat order share", "repeat_order_share", "pct1", True),
        ("LTV : CAC", "ltv_cac_ratio", "num2", True), ("Rating", "rating", "num2", True),
        ("NPS", "nps", "int", True), ("Service backlog", "cs_backlog", "int", False),
    ]),
    ("Finance", "cash_balance", [
        ("Cash", "cash_balance", "pkr", True),
        ("Runway (months)", "runway_rounds", "num1", True),
        ("COD in transit", "cod_receivable", "pkr", True),
        ("Credit drawn", "credit_drawn", "pkr", False),
        ("Net profit", "net_profit", "pkr", True),
        ("Interest paid", "pnl.interest", "pkr", False),
    ]),
]

# The three lines on the run chart. Different units, so they are indexed to
# month 1 - never two y-scales.
RUN_SERIES = [
    ("Net revenue", "revenue_net", "--s1"),
    ("Cost per customer", "--s2", "--s2"),
    ("Contribution margin", "contribution_margin_pct", "--s3"),
]
RUN_LINES = [("Net revenue", "revenue_net", "--s1"),
             ("Cost per customer", "cac_blended", "--s2"),
             ("Contribution margin", "contribution_margin_pct", "--s3")]

# (key in the scorecard dict, label, weight) - docs/08.
PILLARS = [("p1", "Profitability", 25), ("p2", "Growth", 20),
           ("p3", "Customer value", 20), ("p4", "Operational efficiency", 15),
           ("p5", "Cash &amp; capital", 10), ("p6", "Decision quality", 10)]

FOOTNOTES = {
    "Growth": "1 · purchased study, margin of error as sold",
    "Marketing": "1 · platform-reported, over-attributed by 25–40%",
}


BINDING = {
    "under_marketing": ("Under-marketing",
                        "Your proposition was strong enough for more demand than you "
                        "reached. Not enough people saw it."),
    "wasted_spend": ("Wasted spend",
                     "You had plenty of traffic and a weaker proposition than rivals. "
                     "They took the demand."),
    "stock_out": ("Stock-out",
                  "Demand and traffic were both sufficient. You ran out of stock."),
    "balanced": ("Balanced", "Demand, traffic and stock were broadly in step."),
}


def _fmt(value, kind: str) -> str:
    if value is None:
        return "&mdash;"
    k = kind.rstrip("*!")
    try:
        if k == "pkr":
            if abs(value) >= 1e6:
                return f"{value / 1e6:,.2f}M"
            if abs(value) >= 10_000:
                return f"{value / 1e3:,.0f}k"
            return f"{value:,.0f}"
        if k == "int":
            return f"{value:,.0f}"
        if k == "pct1":
            return f"{value * 100:.1f}%"
        if k == "pct2":
            return f"{value * 100:.2f}%"
        if k == "num1":
            return f"{value:.1f}"
        if k == "num2":
            return f"{value:.2f}"
        if k == "score":
            return f"{value:.2f}"
        if k == "x":
            return f"{value:.2f}x"
    except (TypeError, ValueError):
        return str(value)
    return str(value)


def _value(record: dict, key: str):
    """A metric by key. "pnl.x" reaches into the P&L; a bare key is top level."""
    if record is None:
        return None
    if key.startswith("pnl."):
        return record.get("pnl", {}).get(key[4:])
    if key in record:
        return record[key]
    return record.get("pnl", {}).get(key)


def _nice_bounds(lo: float, hi: float) -> tuple[float, float]:
    """Axis bounds a person would have chosen: 25, 50, 75, 100 - not 33, 56, 78.

    Snaps the range outward to a round step so the four gridlines land on
    numbers worth printing.
    """
    span = max(hi - lo, 1.0)
    raw = span / 4
    magnitude = 10 ** math.floor(math.log10(raw))
    for option in (1, 2, 2.5, 5, 10):
        step = option * magnitude
        if step >= raw:
            break
    bottom = math.floor(lo / step) * step
    return bottom, bottom + step * 4


def _run_chart(series: list[dict]) -> str:
    """The run so far, indexed to month 1 = 100.

    Three measures in three different units, which is exactly when a second
    y-axis is tempting and wrong. Indexing to a common base is the honest way
    to put them on one axis. Labels are placed, then pushed apart, because
    three lines finishing close together is the normal case and unreadable
    labels are worse than none.
    """
    if len(series) < 2:
        return ""
    months = len(series)
    plotted = []
    for name, key, colour in RUN_LINES:
        raw = [_value(h, key) for h in series]
        base = next((v for v in raw if v not in (None, 0)), None)
        if base is None:
            continue
        plotted.append((name, colour,
                        [None if v is None else v / base * 100 for v in raw]))
    if not plotted:
        return ""

    flat = [v for _, _, vals in plotted for v in vals if v is not None]
    lo, hi = min(flat + [95.0]), max(flat + [105.0])
    pad = max(4.0, (hi - lo) * 0.12)
    lo, hi = _nice_bounds(lo - pad, hi + pad)
    x0, x1, y0, y1 = 56, 856, 24, 190

    def px(i):
        return x0 + (x1 - x0) * (i / max(months - 1, 1))

    def py(v):
        return y1 - (v - lo) / (hi - lo) * (y1 - y0)

    parts = []
    step = (hi - lo) / 4
    for tick in range(5):
        v = lo + step * tick
        y = py(v)
        parts.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" '
                     f'stroke="var(--grid)"/>')
        parts.append(f'<text x="{x0 - 10}" y="{y + 4:.1f}" font-size="11" '
                     f'fill="var(--muted)" text-anchor="end">{v:.0f}</text>')
    for i in range(months):
        if months <= 8 or i % 2 == 0 or i == months - 1:
            parts.append(f'<text x="{px(i):.1f}" y="{y1 + 22}" font-size="11" '
                         f'fill="var(--muted)" text-anchor="middle">M{i + 1}</text>')

    ends = sorted(((py(v[-1]), n, c, v[-1]) for n, c, v in plotted
                   if v[-1] is not None))
    placed = []
    for at, name, colour, value in ends:
        if placed and at - placed[-1][0] < 19:
            at = placed[-1][0] + 19
        placed.append((at, name, colour, value))

    for name, colour, vals in plotted:
        pts = " ".join(f"{px(i):.1f},{py(v):.1f}"
                       for i, v in enumerate(vals) if v is not None)
        parts.append(f'<polyline fill="none" stroke="var({colour})" stroke-width="2" '
                     f'stroke-linejoin="round" stroke-linecap="round" points="{pts}"/>')
        if vals[-1] is not None:
            parts.append(f'<circle cx="{px(months - 1):.1f}" cy="{py(vals[-1]):.1f}" '
                         f'r="4.5" fill="var({colour})" stroke="var(--surface)" '
                         f'stroke-width="2"/>')
    for at, name, colour, value in placed:
        true_y = next(py(v[-1]) for n, c, v in plotted if n == name)
        if abs(at - true_y) > 1:
            parts.append(f'<line x1="{px(months - 1) + 6:.1f}" y1="{true_y:.1f}" '
                         f'x2="{x1 + 12}" y2="{at:.1f}" stroke="var({colour})" '
                         f'stroke-width="1" opacity=".45"/>')
        parts.append(f'<text x="{x1 + 18}" y="{at + 4:.1f}" font-size="12.5" '
                     f'font-weight="600" fill="var(--ink)">{escape(name)} '
                     f'<tspan fill="var(--muted)" font-weight="400">'
                     f'{value:.0f}</tspan></text>')

    legend = " ".join(
        f'<span class="lg"><i style="background:var({c})"></i>{escape(n)}</span>'
        for n, _, c in RUN_LINES)
    return (f'<section class="run"><div class="runhead"><div>'
            f'<h2>The run so far</h2><p class="cap">Indexed to month 1 = 100, so three '
            f'different units share one axis.</p></div><div class="legend">{legend}'
            f'</div></div>'
            f'<svg viewBox="0 0 1060 220" width="100%" height="220" role="img">'
            f'{"".join(parts)}</svg></section>')


TREND_KEYS = {"revenue_net", "orders", "conversion_rate", "cac_blended",
              "contribution_margin_pct", "service_level", "rating",
              "repeat_order_share", "cash_balance", "active_customers"}


def _campaigns(record: dict) -> str:
    """The month's paid media, campaign by campaign, with the reasons.

    Every paid channel appears whether or not the team set campaigns, so the
    performance-marketing numbers are there to learn from from month 1.
    """
    rows = record.get("campaigns") or []
    if not rows:
        return ""
    body = []
    for r in rows:
        lift = r["lift"]
        cls = "flat" if abs(lift) < 0.005 else ("up" if lift > 0 else "down")
        body.append(
            f'<tr><th><span class="chn">{escape(r["channel_name"])}</span> '
            + (f'<span class="abt">{r["test"]}</span> ' if r.get("test") else '')
            + f'{escape(r["name"])}</th>'
            f'<td class="v">{r["spend"]:,.0f}</td><td class="v">{r["impressions"]:,.0f}</td>'
            f'<td class="v">{r["cpm"]:,.0f}</td><td class="v">{r["clicks"]:,.0f}</td>'
            f'<td class="v">{r["ctr"]:.2%}</td><td class="v">{r["cpc"]:,.1f}</td>'
            f'<td class="v">{r["orders"]:,.0f}</td><td class="v">{r["cvr"]:.2%}</td>'
            f'<td class="v">{r["roas"]:.1f}</td><td class="v">{r["cac"]:,.0f}</td>'
            f'<td class="v"><span class="d {cls}">{lift:+.0%}</span></td></tr>')
        for f in r.get("findings") or []:
            body.append(f'<tr class="why"><td colspan="12"><div class="wt">{escape(f)}</div></td></tr>')
    return (
        '<h2 class="sec">Paid media, campaign by campaign</h2>'
        '<section class="camps"><div class="sx"><table class="perf">'
        '<tr><th>Campaign</th><th class="v">Spend</th><th class="v">Impressions</th>'
        '<th class="v">CPM</th><th class="v">Clicks</th><th class="v">CTR</th>'
        '<th class="v">CPC</th><th class="v">Orders</th><th class="v">CVR</th>'
        '<th class="v">ROAS</th><th class="v">CAC</th><th class="v">vs broad</th></tr>'
        f'{"".join(body)}</table></div>'
        '<p class="fn">Clicks are store visits; CVR is orders per click; CAC is spend '
        'per new customer. <em>vs broad</em> is how much harder each rupee worked than '
        'one broad campaign would have. Orders are attributed from real sessions and '
        'the month\'s real conversion, so the rows add up to your paid orders, not '
        'to what a platform dashboard would claim. CVR differs by channel because buying '
        'intent does: a Google search for a product converts better than a TikTok scroll. '
        'Paid CVR is measured on paid visitors only; your store conversion also counts '
        'returning customers, who convert far better and cost nothing to bring back. '
        '<a href="/guide/marketing" target="_top">How to read this table</a>.</p></section>')


def _products(record: dict) -> str:
    """Sales, margin and contribution by product, why each line sold the way
    it did, and who bought it. Adds up to the P&L, so a portfolio decision -
    re-price, push, pack or drop a line - can be read against the money."""
    rows = record.get("products") or []
    if not rows:
        return ""
    names = record.get("segment_names") or {}
    segments = record.get("order_segments") or {}

    def money(v):
        return _fmt(v, "pkr")

    def pct(v):
        return f"{v * 100:.0f}%"

    def tone(v):
        return "down" if v < 0 else ""

    body = []
    for r in rows:
        vs = (r["unit_share"] / r["typical_share"] - 1) if r["typical_share"] else 0.0
        cls = "flat" if abs(vs) < 0.05 else ("up" if vs > 0 else "down")
        body.append(
            f'<tr><th><span class="chn">{escape(str(r["category"]).title())}</span> '
            f'{escape(r["name"])}</th>'
            f'<td class="v">{r["units"]:,.0f}</td>'
            f'<td class="v">{r["unit_share"]:.1%} <span class="d {cls}">{vs:+.0%}</span></td>'
            f'<td class="v">{money(r["net_sales"])}</td><td class="v">{pct(r["sales_share"])}</td>'
            f'<td class="v {tone(r["gross_margin"])}">{money(r["gross_margin"])}</td>'
            f'<td class="v {tone(r["gm_pct"])}">{pct(r["gm_pct"])}</td>'
            f'<td class="v {tone(r["cm_pre"])}">{money(r["cm_pre"])}</td>'
            f'<td class="v {tone(r["cm_pre_pct"])}">{pct(r["cm_pre_pct"])}</td>'
            f'<td class="v">{money(r["marketing"])}</td>'
            f'<td class="v {tone(r["cm"])}">{money(r["cm"])}</td></tr>')
        if r.get("why"):
            text = "; ".join(r["why"])
            body.append(f'<tr class="why"><td colspan="11"><div class="wt">'
                        f'{escape(text[0].upper() + text[1:])}.</div></td></tr>')

    net = sum(r["net_sales"] for r in rows) or 1.0
    tot = {k: sum(r[k] for r in rows) for k in
           ("units", "net_sales", "gross_margin", "cm_pre", "marketing", "cm")}
    body.append(
        f'<tr class="tot"><th>All products</th><td class="v">{tot["units"]:,.0f}</td>'
        f'<td class="v">100%</td><td class="v">{money(tot["net_sales"])}</td>'
        f'<td class="v">100%</td><td class="v">{money(tot["gross_margin"])}</td>'
        f'<td class="v">{pct(tot["gross_margin"] / net)}</td>'
        f'<td class="v">{money(tot["cm_pre"])}</td><td class="v">{pct(tot["cm_pre"] / net)}</td>'
        f'<td class="v">{money(tot["marketing"])}</td>'
        f'<td class="v {tone(tot["cm"])}">{money(tot["cm"])}</td></tr>')

    lead = "".join(f"<li>{escape(x)}</li>" for x in mix.headline(rows, segments, names))
    sales = (
        '<h2 class="sec">Sales by product this month</h2>'
        f'<section class="prods"><ul class="lead">{lead}</ul>'
        '<div class="sx"><table class="perf">'
        '<tr><th>Product</th><th class="v">Units</th><th class="v">Share of units '
        '&middot; vs typical</th><th class="v">Net sales</th><th class="v">Share</th>'
        '<th class="v">Gross margin</th><th class="v">GM %</th>'
        '<th class="v">Contribution before mktg</th><th class="v">CM %</th>'
        '<th class="v">Marketing</th><th class="v">Contribution after mktg</th></tr>'
        f'{"".join(body)}</table></div>'
        '<p class="fn">Net sales are after returns, failed deliveries and the prepaid '
        'discount. Gross margin takes off each line\'s own landed cost. Contribution '
        'before marketing also takes off delivery, packing and courier - shared by '
        'items in the parcel, so a cheap item carries as much as a dear one and a '
        '3-pack counts as one item - and payment and marketplace fees, shared by sales. '
        'A product campaign\'s spend is charged to the products it named; the rest of '
        'marketing is shared by sales. Every column adds up to your P&amp;L. '
        '<em>vs typical</em> compares each line\'s share of units with a store selling '
        'the same range, at one price position, to the same customers as the other '
        'stores.</p></section>')

    codes = [c for c in names] or sorted({s for r in rows for s in r["buyers"]})

    def cell(v):
        return (f'<td class="v seg" style="background:linear-gradient(90deg,'
                f'rgba(42,120,214,.20) {v * 100:.0f}%,transparent {v * 100:.0f}%)">'
                f'{v:.0%}</td>')

    seg_rows = [f'<tr class="tot"><th>All your orders</th>'
                + "".join(cell(segments.get(c, 0.0)) for c in codes) + '</tr>'] if segments else []
    for r in rows:
        seg_rows.append(f'<tr><th>{escape(r["name"])}</th>'
                        + "".join(cell(r["buyers"].get(c, 0.0)) for c in codes) + '</tr>')
    buyers = (
        '<h2 class="sec">Who bought each product</h2>'
        '<section class="prods"><div class="sx"><table class="perf segs">'
        '<tr><th>Product</th>'
        + "".join(f'<th class="v">{escape(names.get(c, c))}</th>' for c in codes)
        + f'</tr>{"".join(seg_rows)}</table></div>'
        '<p class="fn">Share of each product\'s units bought by each customer segment, '
        'from your own orders - what a store reads from what its visitors browse and '
        'buy. Each row adds to 100%. How big each segment is across the market, and '
        'what it values most, is what MR-06 sells.</p></section>')
    return sales + buyers


def _stock(record: dict) -> str:
    """Each product's stock: what came in, what sold, what is left and how
    long it lasts - the shelf a portfolio and buying decision starts from."""
    lines = record.get("stock") or []
    if not lines:
        return ""
    order = {r["code"]: i for i, r in enumerate(record.get("products") or [])}
    lines = sorted(lines, key=lambda r: (order.get(r["code"], len(order)), r["name"]))
    month = int(record.get("round") or 0)

    def n(v):
        return f"{v:,.0f}" if abs(v) >= 0.5 else "&ndash;"

    body = []
    for r in lines:
        cover, tone = mix.cover_state(r)
        missed = max(0.0, r.get("wanted", r["sold"]) - r["sold"])
        lands = (f' <span class="d flat">M{r["next_arrival"]}</span>'
                 if r.get("next_arrival") and r["on_order"] >= 0.5 else "")
        body.append(
            f'<tr><th><span class="chn">{escape(str(r["category"]).replace("_", " ").title())}'
            f'</span> {escape(r["name"])}</th>'
            f'<td class="v">{n(r["open"])}</td><td class="v">{n(r["received"])}</td>'
            f'<td class="v">{n(r["returned"])}</td><td class="v">{n(r["sold"])}</td>'
            f'<td class="v {"down" if missed >= 0.5 else ""}">{n(missed)}</td>'
            f'<td class="v">{n(r["close"])}</td>'
            f'<td class="v {tone}">{cover}</td>'
            f'<td class="v">{n(r["on_order"])}{lands}</td>'
            f'<td class="v">{_fmt(r["value"], "pkr")}</td></tr>')
    tot = {k: sum(r.get(k, 0.0) for r in lines)
           for k in ("open", "received", "returned", "sold", "close", "on_order", "value")}
    tot["missed"] = sum(max(0.0, r.get("wanted", r["sold"]) - r["sold"]) for r in lines)
    weeks = tot["close"] * 4.33 / tot["sold"] if tot["sold"] > 0 else None
    body.append(
        f'<tr class="tot"><th>All products</th><td class="v">{n(tot["open"])}</td>'
        f'<td class="v">{n(tot["received"])}</td><td class="v">{n(tot["returned"])}</td>'
        f'<td class="v">{n(tot["sold"])}</td><td class="v">{n(tot["missed"])}</td>'
        f'<td class="v">{n(tot["close"])}</td>'
        f'<td class="v">{"&mdash;" if weeks is None else f"{weeks:.1f}"}</td>'
        f'<td class="v">{n(tot["on_order"])}</td>'
        f'<td class="v">{_fmt(tot["value"], "pkr")}</td></tr>')

    bought = record.get("purchase") or {}
    note = ""
    if bought and bought.get("bought", 0) > bought.get("asked", 0) + 0.5:
        note = (f' This month you asked for {bought["asked"]:,.0f} units; Supplier '
                f'{escape(str(bought["supplier"]))}\'s minimum order is '
                f'{bought["moq"]:,.0f}, so {bought["bought"]:,.0f} were bought'
                + (', each product scaled up in the same proportion.'
                   if bought.get("by_product") else '.'))
    return (
        f'<h2 class="sec">Stock by product, end of month {month}</h2>'
        '<section class="prods"><div class="sx"><table class="perf">'
        '<tr><th>Product</th><th class="v">Opening</th><th class="v">Received</th>'
        '<th class="v">Back from failed deliveries</th><th class="v">Sold</th>'
        '<th class="v">Demand missed</th><th class="v">Closing stock</th>'
        '<th class="v">Weeks of cover</th><th class="v">On order &middot; lands</th>'
        '<th class="v">Stock value</th></tr>'
        f'{"".join(body)}</table></div>'
        '<p class="fn">Opening + received + back from failed deliveries &minus; sold = '
        'closing stock. Weeks of cover is closing stock &divide; units sold a week this '
        'month (sold &divide; 4.33): how long the shelf lasts at this month\'s pace. '
        'Under 2 weeks is shown in red, over 12 weeks - cash sitting on the shelf - in '
        'amber. Demand missed is units customers wanted that were not in stock. On order '
        'is stock bought and not yet landed, with the month it lands. Stock value is '
        f'closing stock at landed cost.{note}</p></section>')


def _tests(record: dict) -> str:
    out = []
    for t in record.get("ab_tests") or []:
        rows = "".join(
            f'<tr><th><span class="abt">{k}</span> {escape(t["names"][k])}</th>'
            f'<td class="v">{t["spend"][k]:,.0f}</td><td class="v">{t["clicks"][k]:,.0f}</td>'
            f'<td class="v">{t["orders"][k]:,.0f}</td><td class="v">{t["cvr"][k]:.2%}</td>'
            f'<td class="v">{t["per_1000"][k]:.2f}</td></tr>' for k in ("A", "B"))
        out.append(
            f'<section class="abx"><h2>A/B test on {escape(t["channel_name"])} &middot; '
            f'{t.get("sure", format(t["confidence"], ".0%"))} confident after {t["months"]} month'
            f'{"s" if t["months"] != 1 else ""}</h2>'
            f'<p class="cap" style="max-width:90ch">{escape(t["verdict"])}</p>'
            f'<table class="perf"><tr><th>Campaign</th><th class="v">Spend</th>'
            f'<th class="v">Clicks</th><th class="v">Orders</th><th class="v">CVR</th>'
            f'<th class="v">Orders per PKR 1,000</th></tr>{rows}</table>'
            f'<p class="fn">Pooled over every month both sides ran unchanged. 95% '
            f'confidence is the usual bar for calling a winner.</p></section>')
    return "".join(out)


def _funnel(record: dict, launch: bool = False) -> str:
    """Visitors to orders, and stock against sales, with the arithmetic shown
    so a team can check how conversion and cover are calculated."""
    f = funnel.facts(record, launch=launch)
    def tile(label, value, note=""):
        return (f'<div class="ft"><div class="l">{label}</div><div class="n">{value}</div>'
                f'<div class="u">{note}</div></div>')
    arrow = '<div class="fa">&rarr;</div>'
    op = lambda s: f'<div class="fa">{s}</div>'
    split = ("store and listing visits" if not (f["paid"] or f["organic"] or f["returning"])
             else f"paid {f['paid']:,.0f} · organic {f['organic']:,.0f} · launch month, "
                  f"no returning customers yet" if launch
             else f"paid {f['paid']:,.0f} · organic {f['organic']:,.0f} · "
                  f"returning {f['returning']:,.0f}")
    row1 = (tile("Sessions (visits)", f"{f['sessions']:,.0f}", split)
            + arrow + tile("Orders", f"{f['orders']:,.0f}",
                           f"new customers {f['new_customers']:,.0f} · repeat "
                           f"{f['repeat_orders']:,.0f}")
            + op("=") + tile("Conversion", f"{f['conversion']:.2%}", "orders &divide; sessions"))
    row2 = (tile("Units in stock", f"{f['units_in_stock']:,.0f}", "at the end of the month")
            + op("&divide;") + tile("Units sold a week", f"{f['weekly_units']:,.0f}",
                                    f"{f['units_sold']:,.0f} this month &divide; 4.33")
            + op("=") + tile("Weeks of cover", f"{f['weeks_cover']:.1f}",
                             "how long the stock lasts at this pace")
            + tile("Lost to stock-outs", f"{f['lost_to_stockout']:,.0f}", "orders you could not fill"))
    return (f'<h2 class="sec">Funnel and stock this month</h2>'
            f'<section class="funnel"><div class="frow">{row1}</div>'
            f'<div class="frow">{row2}</div></section>')


def render(team, round_: int, out_dir: str | Path, scorecard: dict | None = None,
           download: str | None = None) -> Path:
    record = team.history[round_ - 1]
    prior = team.history[round_ - 2] if round_ > 1 else None
    series = team.history[:round_]
    name = (team.brand_name
            or getattr(team.founding, "brand_name", None) or team.team_id)

    cards = []
    for title, headline_key, metrics in BLOCKS:
        rows = []
        for label, key, kind, up_is_good in metrics:
            now = _value(record, key)
            was = _value(prior, key) if prior else None
            delta = '<span class="d flat">&mdash;</span>'
            if isinstance(now, (int, float)) and isinstance(was, (int, float)) and was:
                change = (now - was) / abs(was)
                cls = "flat" if abs(change) < 0.005 else (
                    "up" if (change > 0) == up_is_good else "down")
                delta = f'<span class="d {cls}">{change:+.0%}</span>'
            mark = ""
            if kind.endswith("!") or kind.endswith("*"):
                cls = "warn" if kind.endswith("!") else ""
                mark = f'<sup class="mk {cls}">1</sup>'
            rows.append(f'<tr><th>{label}{mark}</th>'
                        f'<td class="v">{_fmt(now, kind)}</td>'
                        f'<td class="c">{delta}</td></tr>')

        trend = ""
        points = [_value(h, headline_key) for h in series]
        if len([v for v in points if v is not None]) >= 2:
            trend = sparkline(points, width=86, height=28)
        headline = next(m[0] for m in metrics if m[1] == headline_key)
        note = FOOTNOTES.get(title, "&nbsp;")
        cards.append(
            f'<section class="block"><div class="blockhead"><div><h2>{title}</h2>'
            f'<p class="cap">{headline} over {len(series)} month'
            f'{"s" if len(series) != 1 else ""}</p></div>{trend}</div>'
            f'<table>{"".join(rows)}</table>'
            f'<p class="fn">{note}</p></section>')

    run_chart = _run_chart(series)

    verdict, explanation = BINDING.get(
        record.get("binding_constraint", "balanced"), BINDING["balanced"])
    against = f" against month {round_ - 1}" if prior else ""
    missed = (record.get("potential") or 0) - (record.get("orders") or 0)
    missed_html = ""
    if missed > 1:
        missed_html = (f'<div class="big"><div class="l">Demand you could not serve</div>'
                       f'<div class="n">{missed:,.0f}</div><div class="u">orders</div></div>')
    events = record.get("events") or []
    events_html = (f'<p class="ev"><strong>Events this round:</strong> '
                   f'{", ".join(events)}</p>') if events else ""
    score_html = ""
    scorecard_section = ""
    if scorecard:
        rows = []
        for key, label, weight in PILLARS:
            got = scorecard.get(key)
            if got is None:
                continue
            rows.append(
                f'<tr><th>{label}</th><td class="v">{weight}</td>'
                f'<td class="v">{got:.1f}</td>'
                f'<td class="bar"><div class="meter"><i style="width:'
                f'{min(100, got / weight * 100):.0f}%"></i></div></td></tr>')
        scorecard_section = (
            f'<h2 class="sec">Scorecard, as it stands</h2>'
            f'<section><table class="score"><tr><th>Pillar</th>'
            f'<th class="v">Weight</th><th class="v">You</th>'
            f'<th class="bar">Against the published anchors</th></tr>'
            f'{"".join(rows)}'
            f'<tr><th><strong>Total</strong></th><td class="v"></td>'
            f'<td class="v"><strong>{scorecard["total"]:.1f}</strong></td>'
            f'<td class="bar"></td></tr></table>'
            f'<p class="fn">Criterion-referenced: you are marked against published '
            f'anchors, not against the cohort. Every team in the room can score '
            f'well.</p></section>')

    html = f"""<!doctype html>
<html lang="en" data-theme="consulytics"><head><meta charset="utf-8">
<link rel="icon" href="/static/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/static/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/static/apple-touch-icon.png">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(name)} &mdash; Month {round_}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root,[data-theme="consulytics"]{{--page:#f5f5f6;--surface:#ffffff;--panel-2:#f3f3f5;
--grid:#e4e4e7;--line:#e4e4e7;--ink:#131316;--dim:#55555f;--muted:#86868f;
--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--mark:#2a78d6;--good:#0a7d0a;--bad:#b3231e;
--warn:#8a6414;--accent:#ed0000;--critical:#c62828;color-scheme:light}}
[data-theme="dark"]{{--page:#0d0d0c;--surface:#1a1a19;--panel-2:#222220;
--grid:#2c2c2a;--line:#2c2c2a;--ink:#fff;--dim:#c3c2b7;--muted:#898781;
--s1:#3987e5;--s2:#d95926;--s3:#199e70;--good:#5fd35f;--bad:#ef8a8a;--warn:#e0a92a;
--accent:#3987e5;--mark:#3987e5;--critical:#d03b3b;color-scheme:dark}}
[data-theme="slate"]{{--page:#15171b;--surface:#22242a;--panel-2:#2a2d34;
--grid:#353942;--line:#353942;--ink:#f2f4f7;--dim:#b9bfc9;--muted:#858c99;
--s1:#3987e5;--s2:#d95926;--s3:#199e70;--good:#5fd35f;--bad:#ef8a8a;--warn:#e0a92a;
--accent:#3987e5;--mark:#3987e5;--critical:#d03b3b;color-scheme:dark}}
[data-theme="light"]{{--page:#f4f5f7;--surface:#fcfcfb;--panel-2:#f2f3f5;
--grid:#e8eaee;--line:#e3e5e9;--ink:#0f1115;--dim:#545962;--muted:#878c96;
--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--good:#0a7d0a;--bad:#b73030;--warn:#8a6414;
--accent:#2a78d6;--mark:#2a78d6;--critical:#d03b3b;color-scheme:light}}
body{{background:var(--page);color:var(--ink);padding:26px 18px 50px;
font:14px/1.55 Inter,-apple-system,Segoe UI,Roboto,sans-serif}}
.wrap{{max-width:1180px;margin:0 auto}}
h1{{font-size:25px;letter-spacing:-.022em;margin:0 0 4px}}
.sub{{color:var(--dim);font-size:14px;margin:0 0 18px}}
section{{background:var(--surface);border:1px solid var(--line);border-radius:11px;
padding:15px 16px}}
h2{{font-size:14px;font-weight:650;margin:0}}
.cap{{color:var(--dim);font-size:12.5px;margin:3px 0 0}}
.verdict{{display:flex;gap:18px;align-items:flex-start;
border-left:3px solid var(--critical);margin:0 0 13px}}
.verdict .big{{margin-left:auto;text-align:right;flex:0 0 auto}}
.verdict .big .n{{font-size:25px;font-weight:600;
font-family:"JetBrains Mono",monospace;font-variant-numeric:tabular-nums}}
.verdict .big .l{{color:var(--dim);font-size:12px}}
.verdict .big .u{{color:var(--muted);font-size:11.5px}}
.run{{margin:0 0 13px}} .run svg{{overflow:visible}}
.runhead{{display:flex;align-items:flex-start;gap:20px;margin-bottom:8px}}
.legend{{margin-left:auto;display:flex;gap:15px;color:var(--dim);font-size:12px;
flex-wrap:wrap}}
.lg{{display:inline-flex;align-items:center;gap:6px}}
.lg i{{width:10px;height:10px;border-radius:2px;display:inline-block}}
.sec{{font-size:11.5px;letter-spacing:.09em;text-transform:uppercase;
color:var(--muted);font-weight:600;margin:20px 0 10px}}
.grid{{display:grid;gap:12px;grid-template-columns:repeat(3,1fr)}}
.block{{display:flex;flex-direction:column}}
.blockhead{{display:flex;align-items:flex-start;gap:12px;padding-bottom:11px;
border-bottom:1px solid var(--line);margin-bottom:2px}}
.blockhead .spark{{flex:0 0 auto;margin:0}}
table{{width:100%;border-collapse:collapse;table-layout:fixed}}
th,td{{padding:0;height:37px;font-size:12.5px;border-top:1px solid var(--line);
white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
tr:first-child th,tr:first-child td{{border-top:0}}
th{{text-align:left;font-weight:400;color:var(--dim)}}
td.v{{text-align:right;font-weight:600;font-family:"JetBrains Mono",monospace;
font-variant-numeric:tabular-nums}}
td.c{{text-align:right;width:74px;font-family:"JetBrains Mono",monospace;
font-variant-numeric:tabular-nums}}
.d{{font-size:11.5px;font-weight:600}}
.up{{color:var(--good)}} .down{{color:var(--bad)}} .flat{{color:var(--muted)}}
.mk{{font-size:9.5px;font-weight:700;color:var(--muted);margin-left:3px;
vertical-align:super}}
.mk.warn{{color:var(--warn)}}
.fn{{margin-top:auto;padding-top:10px;color:var(--muted);font-size:11px;min-height:14px}}
.ev{{margin:11px 0 0;color:var(--dim);font-size:13px}}
.score{{table-layout:auto}}
.sx{{overflow-x:auto}}
.perf{{table-layout:auto}}
.perf th,.perf td{{padding:0 8px}}
.perf tr:first-child th{{color:var(--muted);font-size:11px;font-weight:600}}
.perf th .chn{{display:inline-block;padding:1px 7px;border-radius:5px;
background:var(--panel-2);color:var(--dim);font-size:11px;font-weight:600;margin-right:4px}}
.abt{{display:inline-grid;place-items:center;width:18px;height:18px;border-radius:5px;
background:var(--ink);color:var(--surface);font-size:10.5px;font-weight:700;margin-right:3px}}
.abx{{margin-top:12px;border-left:3px solid var(--s1)}}
.perf tr.why td{{border-top:0;height:auto;padding:0 8px 7px 18px;white-space:normal;
color:var(--dim);font-size:12.5px}}
.score th{{color:var(--ink);font-weight:400}}
.score tr:first-child th{{color:var(--muted);font-size:11px;letter-spacing:.05em;
text-transform:uppercase;font-weight:600}}
.score td.bar{{width:38%;padding-left:16px}}
.meter{{height:7px;background:var(--grid);border-radius:4px;position:relative}}
.meter i{{position:absolute;left:0;top:0;bottom:0;border-radius:4px;
background:var(--s1)}}
.themebar{{display:flex;gap:7px;margin:22px 0 0;align-items:center}}
.themebar span{{color:var(--muted);font-size:11px;letter-spacing:.09em;
text-transform:uppercase;font-weight:600;margin-right:4px}}
.sw{{width:24px;height:24px;border-radius:7px;border:1px solid var(--line);cursor:pointer;
padding:0}}
.sw[aria-pressed="true"]{{outline:2px solid var(--accent);outline-offset:1.5px}}
.sw-consulytics{{background:linear-gradient(135deg,#fff 52%,#ff0000 52%)}}
.sw-dark{{background:#0d0d0c}}.sw-slate{{background:#22242a}}.sw-light{{background:#f4f5f7}}
.perf tr.why .wt{{position:sticky;left:8px;max-width:calc(100vw - 96px)}}
.sub .xl{{display:inline-block;margin-left:10px;padding:3px 10px;border:1px solid var(--line);
border-radius:7px;background:var(--surface);color:var(--s1);font-size:12.5px;font-weight:600;
text-decoration:none}}
.sub .xl:hover{{border-color:var(--s1)}}
.prods .lead{{margin:0 0 10px 18px;color:var(--ink);font-size:13px;line-height:1.6}}
.perf tr.tot th,.perf tr.tot td{{font-weight:700;border-top:2px solid var(--line)}}
.perf tr.tot th{{color:var(--ink)}}
td.v.down{{color:var(--bad)}}
td.v.warn{{color:var(--warn)}}
.segs td.seg{{min-width:92px}}
.funnel{{padding:14px 18px}}
.frow{{display:flex;align-items:stretch;gap:10px;flex-wrap:wrap}}
.frow+.frow{{margin-top:12px;padding-top:12px;border-top:1px solid var(--line, #e1e0d9)}}
.ft{{flex:1 1 150px;min-width:140px}}
.ft .l{{font-size:12px;color:var(--dim,#52514e)}}
.ft .n{{font:600 22px/1.25 inherit;font-variant-numeric:tabular-nums}}
.ft .u{{font-size:11.5px;color:var(--dim,#898781)}}
.fa{{flex:0 0 auto;align-self:center;font-size:20px;color:var(--dim,#898781);padding:0 2px}}
{CSS_TOKENS}
@media(max-width:1380px){{.wrap{{max-width:100%}}}}
@media(max-width:1180px){{.grid{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:820px){{.grid{{grid-template-columns:1fr}}
.verdict{{flex-direction:column;gap:12px}}.verdict .big{{margin-left:0;text-align:left}}}}
</style></head><body class="viz"><div class="wrap">
<h1>{escape(name)}</h1>
<p class="sub">Month {round_} &middot; {team.team_id} &middot; where the month was won and lost
{f'<a class="xl" href="{escape(download)}">Download every month as Excel: P&amp;L, KPIs, products, stock, cash</a>' if download else ''}</p>
<section class="verdict">
  <div><h2>{verdict}</h2><p class="cap" style="max-width:82ch">{explanation}</p>
  {events_html}{score_html}</div>
  {missed_html}
</section>
{_funnel(record, funnel.from_scratch_launch(team, record))}
{run_chart}
<h2 class="sec">Every measure, month {round_}{against}</h2>
<div class="grid">{"".join(cards)}</div>
{_products(record)}
{_stock(record)}
{_campaigns(record)}
{_tests(record)}
{scorecard_section}
<div class="themebar"><span>Appearance</span>
  <button class="sw sw-consulytics" data-set-theme="consulytics"
          title="Consulytics"></button>
  <button class="sw sw-dark" data-set-theme="dark" title="Dark"></button>
  <button class="sw sw-slate" data-set-theme="slate" title="Slate"></button>
  <button class="sw sw-light" data-set-theme="light" title="Light"></button>
</div>
</div><script>
(function () {{
  var KEY = "ecomsim-theme";
  var initial = document.documentElement.getAttribute("data-theme") || "consulytics";
  var saved = initial;
  try {{ saved = localStorage.getItem(KEY) || initial; }} catch (e) {{}}
  function apply(t) {{
    document.documentElement.setAttribute("data-theme", t);
    document.querySelectorAll("[data-set-theme]").forEach(function (b) {{
      b.setAttribute("aria-pressed", b.dataset.setTheme === t);
    }});
  }}
  apply(saved);
  document.querySelectorAll("[data-set-theme]").forEach(function (b) {{
    b.addEventListener("click", function () {{
      apply(b.dataset.setTheme);
      try {{ localStorage.setItem(KEY, b.dataset.setTheme); }} catch (e) {{}}
    }});
  }});
}})();
</script></body></html>"""

    out = Path(out_dir) / f"report_{team.team_id}_r{round_}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out
