"""A team's results as an Excel workbook: P&L, revenue, KPIs, products, stock, cash.

The report shows each number once. This shows how it is made: every subtotal,
margin and KPI that can be rebuilt from the lines beneath it is a live
formula over those lines, so a team can trace a KPI back to its parts - and
change an input to see what moves. Inputs from the simulation are blue,
formulas black, links to another sheet green: the usual model convention.

Every formula is written together with its value, so the file reads
correctly in a phone preview or a viewer that does not recalculate.

Months recorded before a line existed (the product, stock and cash detail
arrived after month 1 of the first live game) still get every line that can
be derived from what they kept; what cannot is left out, never invented.
"""
from __future__ import annotations

import io
from datetime import datetime

import xlsxwriter
from xlsxwriter.utility import xl_col_to_name

FONT = "Arial"
BLUE, GREEN, INK, MUTED, RULE = "#0000FF", "#008000", "#131316", "#6B6B76", "#C9C9D1"
FMT = {
    "pkr": '#,##0;(#,##0);"-"',
    "int": '#,##0;(#,##0);"-"',
    "pct": '0.0%;(0.0%);"-"',
    "pct2": '0.00%;(0.00%);"-"',
    "num1": '0.0;(0.0);"-"',
    "num2": '0.00;(0.00);"-"',
    "text": "@",
}


# --- Formulas that know their own value ------------------------------------------------

class E:
    """An expression with an Excel form (per column) and a Python value
    (per month index), so a formula cell is written with its result."""

    def __init__(self, xl, val):
        self.xl, self.val = xl, val

    @staticmethod
    def of(x):
        return x if isinstance(x, E) else E(lambda c: repr(float(x)), lambda i: float(x))

    def __add__(self, o):
        o = E.of(o)
        return E(lambda c: f"{self.xl(c)}+{o.xl(c)}", lambda i: self.val(i) + o.val(i))

    def __sub__(self, o):
        o = E.of(o)
        return E(lambda c: f"{self.xl(c)}-({o.xl(c)})", lambda i: self.val(i) - o.val(i))

    def __mul__(self, o):
        o = E.of(o)
        return E(lambda c: f"({self.xl(c)})*({o.xl(c)})", lambda i: self.val(i) * o.val(i))

    def __truediv__(self, o):
        o = E.of(o)

        def val(i):
            b = o.val(i)
            return self.val(i) / b if b else 0.0
        return E(lambda c: f"IFERROR(({self.xl(c)})/({o.xl(c)}),0)", val)

    def __neg__(self):
        return E(lambda c: f"-({self.xl(c)})", lambda i: -self.val(i))


class Sheet:
    """A sheet with months across and lines down, each line keyed so later
    lines and other sheets can refer to it."""

    def __init__(self, book, name, months, title, intro, first_col=1):
        self.book, self.name, self.months = book, name, months
        self.ws = book.sheet(name)
        self.rows, self.values = {}, {}
        self.first = first_col
        self.r = 0
        ws = self.ws
        ws.set_column(0, 0, 46)
        ws.set_column(self.first, self.first + len(months) - 1, 13)
        ws.set_column(self.first + len(months), self.first + len(months), 90)
        ws.write(self.r, 0, title, book.f("title"))
        self.r += 1
        ws.write(self.r, 0, intro, book.f("intro"))
        self.r += 2
        ws.write(self.r, 0, "PKR unless stated", book.f("head"))
        for i, m in enumerate(months):
            ws.write(self.r, self.first + i, f"Month {m}", book.f("head_r"))
        ws.write(self.r, self.first + len(months), "How it is calculated", book.f("head"))
        ws.freeze_panes(self.r + 1, self.first)
        self.r += 1

    def col(self, i):
        return xl_col_to_name(self.first + i)

    def ref(self, key, sheet=None):
        row = self.rows[key] + 1
        prefix = f"'{self.name}'!" if sheet is not None and sheet is not self else ""
        return E(lambda c: f"{prefix}{c}{row}", lambda i: self.values[key][i] or 0.0)

    def section(self, label):
        self.r += 1
        self.ws.write(self.r, 0, label.upper(), self.book.f("section"))
        self.r += 1

    def line(self, key, label, source, kind="pkr", note="", bold=False, link=False):
        """One line: `source` is a list of values (inputs, blue) or an E
        (a formula, black; green when it only points at another sheet)."""
        ws, book = self.ws, self.book
        ws.write(self.r, 0, label, book.f("label_b" if bold else "label"))
        vals = []
        for i in range(len(self.months)):
            if isinstance(source, E):
                v = source.val(i)
                role = "link" if link else "calc"
                ws.write_formula(self.r, self.first + i, "=" + source.xl(self.col(i)),
                                 book.f(kind, role, bold), _clean(v))
            else:
                v = source[i]
                if v is None:
                    ws.write_blank(self.r, self.first + i, None, book.f(kind, "input", bold))
                else:
                    ws.write_number(self.r, self.first + i, v, book.f(kind, "input", bold))
            vals.append(v)
        if note:
            ws.write(self.r, self.first + len(self.months), note, book.f("note"))
        self.rows[key], self.values[key] = self.r, vals
        self.r += 1
        return self.ref(key)


def _clean(v):
    try:
        return round(float(v), 10)
    except (TypeError, ValueError):
        return 0.0


def total(*refs):
    out = E.of(0)
    for r in refs:
        out = out + r
    return E(lambda c: "SUM(" + ",".join(r.xl(c) for r in refs) + ")",
             out.val) if refs else out


# --- The workbook ---------------------------------------------------------------------

class Book:
    def __init__(self, buf):
        self.wb = xlsxwriter.Workbook(buf, {"in_memory": True,
                                            "strings_to_numbers": False})
        self._f = {}

    def sheet(self, name):
        """A worksheet set up to read on screen and print on A4."""
        ws = self.wb.add_worksheet(name)
        ws.hide_gridlines(2)
        ws.set_landscape()
        ws.set_paper(9)
        ws.fit_to_pages(1, 0)
        ws.set_margins(0.4, 0.4, 0.5, 0.5)
        return ws

    def f(self, kind, role=None, bold=False):
        key = (kind, role, bold)
        if key in self._f:
            return self._f[key]
        base = {"font_name": FONT, "font_size": 10, "valign": "vcenter"}
        if kind == "title":
            base.update(bold=True, font_size=15, font_color=INK)
        elif kind == "intro":
            base.update(font_color=MUTED, italic=True)
        elif kind in ("head", "head_r"):
            base.update(bold=True, font_color=MUTED, bottom=1, bottom_color=INK,
                        align="right" if kind == "head_r" else "left",
                        text_wrap=True, valign="bottom")
        elif kind == "section":
            base.update(bold=True, font_color="#ED0000", font_size=9)
        elif kind in ("label", "label_b"):
            base.update(bold=kind == "label_b", font_color=INK, indent=0 if kind == "label_b" else 1)
        elif kind == "note":
            base.update(font_color=MUTED, font_size=9, text_wrap=False)
        elif kind == "wrap":
            base.update(font_color=INK, text_wrap=True, valign="top")
        elif kind == "wrap_in":
            base.update(font_color=BLUE, text_wrap=True, valign="top")
        else:
            base["num_format"] = FMT.get(kind, FMT["pkr"])
            base["font_color"] = {"input": BLUE, "link": GREEN}.get(role, INK)
            if bold:
                base.update(bold=True, top=1, top_color=RULE)
            if kind == "text":
                base.pop("num_format")
        fmt = self.wb.add_format(base)
        self._f[key] = fmt
        return fmt


def build(team, params, name: str, round_: int) -> bytes:
    """The team's workbook for months 1..round_, as .xlsx bytes."""
    history = team.history[:round_]
    months = [h.get("round", i + 1) for i, h in enumerate(history)]
    buf = io.BytesIO()
    book = Book(buf)
    _readme(book, name, months)
    pl = _pnl(book, params, history, months)
    _kpis(book, params, history, months, pl)
    latest = history[-1]
    _products(book, latest, months[-1])
    _stock(book, latest, months[-1])
    _products_by_month(book, history, months)
    _cash(book, history, months, pl)
    _campaigns(book, history, months)
    _customers(book, latest, history, months)
    book.wb.close()
    return buf.getvalue()


def _readme(book, name, months):
    ws = book.sheet("Read me")
    ws.set_column(0, 0, 30)
    ws.set_column(1, 1, 110)
    span = f"month {months[0]}" if len(months) == 1 else f"months {months[0]} to {months[-1]}"
    ws.write(0, 0, f"{name} - results workbook", book.f("title"))
    ws.write(1, 0, f"Every month so far ({span}). Generated "
                   f"{datetime.now():%d %b %Y %H:%M}. Simulation figures, not market data.",
             book.f("intro"))
    rows = [
        ("P&L", "The profit and loss, month by month. Every subtotal and margin is a formula over the lines above it."),
        ("KPIs", "Every measure in the monthly report, in the same blocks. Where a KPI can be rebuilt from other lines it is a formula you can click on to see how it is made."),
        ("Products", "Last month, product by product: units, sales, gross margin, contribution before and after marketing, and why each line sold the way it did."),
        ("Stock", "Last month's stock movement by product: opening + received + back from failed deliveries - sold = closing. Weeks of cover, stock value and what is on order."),
        ("Products by month", "The same product and stock figures for every month, as one table - filter it, or build a pivot table from it."),
        ("Cash", "Why cash and profit differ: what came in, what went out, and what is still with couriers or owed to suppliers."),
        ("Campaigns", "Paid media campaign by campaign, every month."),
        ("Customers", "Who your orders came from, by customer segment, and who bought each product last month."),
        ("", ""),
        ("Colours", "Blue numbers come straight from the simulation. Black numbers are formulas over other cells. Green numbers are links to another sheet."),
        ("Signs", "Costs and deductions are negative, shown in brackets, so each subtotal is simply the sum of the lines above it."),
        ("Change a number", "Change a blue input and every formula that depends on it recalculates - a quick way to see what moves a KPI. The simulation itself is not affected."),
        ("Definitions", "The KPI definitions guide (PDF) gives every formula in words, with the simulation's fixed assumptions."),
    ]
    for i, (a, b) in enumerate(rows, start=3):
        ws.write(i, 0, a, book.f("label_b"))
        ws.write(i, 1, b, book.f("wrap"))


# --- P&L -----------------------------------------------------------------------------

def _p(h, key, default=0.0):
    return float((h.get("pnl") or {}).get(key, default) or 0.0)


def _pnl_lines(h, params) -> dict:
    """The P&L lines for one month, derived where the month predates the split."""
    p = h.get("pnl") or {}
    net, gp = _p(h, "net_revenue"), _p(h, "gross_profit")
    gross = _p(h, "gross_revenue")
    out = {
        "gross_sales": gross + _p(h, "prepaid_discount"),
        "prepaid": -_p(h, "prepaid_discount"),
        "returns": -_p(h, "returns_value"),
        "rto": -_p(h, "rto_value"),
        "failed": -(gross - _p(h, "returns_value") - _p(h, "rto_value") - net),
        "rto_cost": -_p(h, "rto_cost"),
        "payment": -_p(h, "payment_costs"),
        "commission": -_p(h, "commission"),
        "research": -_p(h, "research"), "holding": -_p(h, "holding"),
        "ageing": -_p(h, "ageing"), "interest": -_p(h, "interest"),
    }
    if "cogs_sold" in p:
        out.update(cogs_sold=-_p(h, "cogs_sold"), write_off=-_p(h, "write_off"),
                   pick_pack=-_p(h, "pick_pack"), courier=-_p(h, "courier"),
                   return_ship=-_p(h, "return_shipping"),
                   marketing=-_p(h, "marketing_spend"), affiliate=-_p(h, "affiliate"))
        for k in ("payroll", "service_team", "warehouse", "technology", "website",
                  "quality_assurance"):
            out[k] = -_p(h, k)
        out["unsplit"] = None
    else:
        # Recorded before the lines were kept: everything but the overheads
        # follows from the subtotals; the overheads stay as one line.
        affiliate = max(0.0, _p(h, "marketing")
                        - float(h.get("cac_blended") or 0) * float(h.get("new_customers") or 0))
        ret_ship = (gp - _p(h, "fulfilment") - _p(h, "rto_cost") - _p(h, "payment_costs")
                    - _p(h, "marketing") - _p(h, "commission") - _p(h, "contribution"))
        write_off = _p(h, "return_cost") - ret_ship
        pick = float(h.get("orders") or 0) * params["fulfil_pick_pack_cost"]
        out.update(cogs_sold=-(net - gp - write_off), write_off=-write_off,
                   pick_pack=-pick, courier=-(_p(h, "fulfilment") - pick),
                   return_ship=-ret_ship, marketing=-(_p(h, "marketing") - affiliate),
                   affiliate=-affiliate)
        for k in ("payroll", "service_team", "warehouse", "technology", "website",
                  "quality_assurance"):
            out[k] = None
        out["unsplit"] = -(_p(h, "below_line") - _p(h, "research") - _p(h, "holding")
                           - _p(h, "ageing"))
    return out


def _pnl(book, params, history, months):
    lines = [_pnl_lines(h, params) for h in history]
    col = lambda k: [ln[k] for ln in lines]
    s = Sheet(book, "P&L", months, "Profit and loss",
              "Read top to bottom: each subtotal is the sum of the lines above it. "
              "Costs are negative.")

    s.section("Revenue")
    gs = s.line("gross_sales", "Gross sales", col("gross_sales"),
                note="Orders x average order value: every product shipped at its net price, less pack savings")
    pp = s.line("prepaid", "Prepaid discount", col("prepaid"),
                note="The discount you give customers who pay in advance (9.2), on the prepaid share")
    gr = s.line("gross_revenue", "Gross revenue", total(gs, pp), bold=True)
    rt = s.line("returns", "Customer returns", col("returns"),
                note="Orders sent back after delivery (from last month's deliveries) x average order value")
    rto = s.line("rto", "Refused at the door (RTO)", col("rto"),
                 note="Cash-on-delivery parcels the customer refused x average order value")
    fl = s.line("failed", "Failed deliveries", col("failed"),
                note="Parcels the courier could not deliver x average order value")
    net = s.line("net_revenue", "Net revenue", total(gr, rt, rto, fl), bold=True,
                 note="What the business actually earned in sales")

    s.section("Cost of goods")
    cg = s.line("cogs_sold", "Cost of goods kept by customers", col("cogs_sold"),
                note="Landed cost of the units that stayed sold, product by product")
    wo = s.line("write_off", "Returned stock that cannot be resold", col("write_off"),
                note="Returns that are damaged or used are written off at cost")
    gp = s.line("gross_profit", "Gross profit", total(net, cg, wo), bold=True)
    s.line("gm", "Gross margin %", gp / net, kind="pct", note="Gross profit / net revenue")

    s.section("Cost to serve")
    serve = [
        s.line("pick_pack", "Pick and pack", col("pick_pack"),
               note=f"PKR {params['fulfil_pick_pack_cost']:,.0f} an order"),
        s.line("courier", "Outbound courier", col("courier"),
               note="Orders x each courier's cost per parcel, by your courier mix"),
        s.line("rto_cost", "Failed and refused parcels: courier out and back", col("rto_cost"),
               note="Every failed or refused parcel pays the courier twice"),
        s.line("return_ship", "Customer returns: courier back", col("return_ship")),
        s.line("payment", "Payment fees (card gateway and COD handling)", col("payment"),
               note="Gateway fee on prepaid revenue + COD handling fee on COD revenue"),
        s.line("commission", "Marketplace commission", col("commission"),
               note="Commission on the marketplace share of revenue, when you sell on one (4.1)"),
    ]
    cmp_ = s.line("cm_pre", "Contribution before marketing", total(gp, *serve), bold=True,
                  note="What an order earns once it is delivered and paid for")
    s.line("cm_pre_pct", "Contribution before marketing %", cmp_ / net, kind="pct",
           note="Scored: Profitability pillar")

    s.section("Marketing")
    mk = s.line("marketing", "Marketing spend", col("marketing"),
                note="Paid media, creative, brand, CRM and other marketing decisions")
    af = s.line("affiliate", "Affiliate and influencer commission", col("affiliate"),
                note="Commission rate (3.6) x net revenue")
    con = s.line("contribution", "Contribution", total(cmp_, mk, af), bold=True)
    s.line("cm_pct", "Contribution margin %", con / net, kind="pct",
           note="Contribution / net revenue: the report's Contribution margin")

    s.section("Overheads (below the line)")
    keys = [("payroll", "Payroll", "Fixed team cost"),
            ("service_team", "Customer service team", "Grows with orders and the service backlog"),
            ("warehouse", "Warehouse", "Fixed"),
            ("technology", "Technology", "Fixed platform cost plus running cost of AI modules you bought"),
            ("website", "Website and UX spend", "Decision 5.1"),
            ("quality_assurance", "Quality assurance", "Decision 7.4")]
    over = []
    if any(ln["unsplit"] is not None for ln in lines):
        over.append(s.line("unsplit", "Overheads (not split for this month)",
                           [ln["unsplit"] if ln["unsplit"] is not None else 0.0 for ln in lines],
                           note="Recorded before the overheads were kept line by line"))
    for k, label, note in keys:
        over.append(s.line(k, label, [v if v is not None else 0.0 for v in col(k)], note=note))
    over += [s.line("research", "Research studies", col("research"), note="Studies bought this month (12.1)"),
             s.line("holding", "Stock holding cost", col("holding"),
                    note="A monthly charge on the value of all stock you hold"),
             s.line("ageing", "Write-down of ageing stock", col("ageing"),
                    note="Stock held beyond the obsolescence horizon is written down")]
    eb = s.line("ebitda", "EBITDA", total(con, *over), bold=True)
    s.line("ebitda_pct", "EBITDA margin %", eb / net, kind="pct", note="Scored: Profitability pillar")
    it = s.line("interest", "Interest on credit drawn", col("interest"),
                note="Credit drawn x annual rate / 12")
    npf = s.line("net_profit", "Net profit", total(eb, it), bold=True)
    s.line("net_pct", "Net margin %", npf / net, kind="pct")
    return s


# --- KPIs ------------------------------------------------------------------------------

def _v(history, key, default=None):
    return [None if h.get(key) is None and default is None else float(h.get(key) or default or 0.0)
            for h in history]


def _kpis(book, params, history, months, pl):
    s = Sheet(book, "KPIs", months, "Every measure in the report",
              "Same blocks and names as the report. Black and green figures are formulas: "
              "click one to see how the KPI is built.")
    link = lambda key: pl.ref(key, sheet=s)
    split = [h.get("sessions_paid", 0) or h.get("sessions_organic", 0) for h in history]

    s.section("Growth")
    sess = s.line("sessions", "Sessions", _v(history, "sessions"), kind="int",
                  note="Visits to your store: paid + organic + returning")
    s.line("s_paid", "   of which paid", [h.get("sessions_paid") if any(split) else None for h in history],
           kind="int", note="From Meta, TikTok, Google and other paid channels")
    s.line("s_org", "   of which organic", [h.get("sessions_organic") if any(split) else None for h in history],
           kind="int", note="Search, direct and word of mouth, driven by brand and site quality")
    s.line("s_ret", "   of which returning", [h.get("sessions_returning") if any(split) else None for h in history],
           kind="int", note="Customers you already have, coming back")
    orders = s.line("orders", "Orders", _v(history, "orders"), kind="int")
    rep = s.line("repeat_orders", "   of which repeat orders",
                 [h.get("repeat_orders", (h.get("repeat_order_share") or 0) * (h.get("orders") or 0))
                  for h in history], kind="int", note="Orders from customers who bought before")
    s.line("new_orders", "   of which first orders", orders - rep, kind="int",
           note="Orders - repeat orders")
    s.line("cr", "Conversion rate", orders / sess, kind="pct2", note="Orders / sessions")
    gsl = s.line("gross_sales", "Gross sales", link("gross_sales"), link=True, note="From the P&L")
    s.line("aov", "AOV (average order value)", gsl / orders,
           note="Gross sales / orders: before the prepaid discount, returns and failed deliveries")
    s.line("net_revenue", "Net revenue", link("net_revenue"), link=True, note="From the P&L")
    s.line("market_share", "Market share", _v(history, "market_share"), kind="pct",
           note="Your net revenue / all teams' net revenue")

    s.section("Marketing")
    mspend = s.line("mspend", "Marketing spend", -link("marketing"), link=True,
                    note="From the P&L, before affiliate commission")
    newc = s.line("new_customers", "New customers", _v(history, "new_customers"), kind="int")
    cac = s.line("cac", "Blended CAC", mspend / newc, note="Marketing spend / new customers")
    s.line("roas", "Reported ROAS", _v(history, "roas_reported"), kind="num2",
           note="Platform-reported: revenue the ad platforms claim per rupee, over-attributed by 25-40%")
    s.line("creative", "Creative quality", _v(history, "creative_quality"), kind="num2",
           note="0 to 1. Rises with creative spend, fades with time and over-use")
    s.line("brand", "Brand equity", _v(history, "brand_equity"), kind="num2",
           note="0 to 1. Built slowly by brand spend and good experience")

    s.section("Commercial")
    s.line("gm", "Gross margin", link("gm"), kind="pct", link=True, note="From the P&L")
    s.line("cm", "Contribution margin", link("cm_pct"), kind="pct", link=True, note="From the P&L")
    s.line("cm_pre", "Contribution before marketing", link("cm_pre_pct"), kind="pct", link=True,
           note="From the P&L - the margin the scorecard reads")
    s.line("ebitda", "EBITDA", link("ebitda"), link=True, note="From the P&L")
    s.line("disc", "Discount rate", _v(history, "discount_rate"), kind="pct",
           note="Your discounts averaged across products, weighted by how much of each sells")
    s.line("fulfil", "Fulfilment cost", -(link("pick_pack") + link("courier")), link=True,
           note="Pick and pack + outbound courier, from the P&L")
    s.line("pay", "Payment costs", -link("payment"), link=True, note="From the P&L")

    s.section("Operations")
    lost = [h.get("lost_to_stockout") for h in history]
    lst = s.line("lost", "Orders lost to stock-outs", lost, kind="int",
                 note="Orders customers would have placed had the stock been there")
    s.line("service", "Service level", orders / (orders + lst), kind="pct",
           note="Orders / (orders + orders lost to stock-outs)")
    s.line("instock", "In-stock rate", _v(history, "instock_rate"), kind="pct",
           note="Share of your demand whose product had stock at the start of the month")
    s.line("delivery", "Delivery success", _v(history, "delivery_success"), kind="pct",
           note="Share of parcels the courier delivered")
    s.line("rto_rate", "RTO rate", _v(history, "rto_rate"), kind="pct",
           note="Share of cash-on-delivery parcels refused at the door")
    s.line("return_rate", "Return rate", _v(history, "return_rate"), kind="pct",
           note="Share of last month's delivered orders sent back")
    units = s.line("units", "Units sold",
                   [float(h.get("units_sold") or (h.get("orders") or 0) * params["units_per_order"])
                    for h in history], kind="int",
                   note="Units shipped, packs counted as three")
    s.line("upo", "Units per order", units / orders, kind="num2", note="Units sold / orders")
    stock = s.line("stock", "Units in stock at month end", _v(history, "inventory_units"), kind="int")
    s.line("cover", "Weeks of cover", stock * 4.33 / units, kind="num1",
           note="Units in stock x 4.33 weeks / units sold this month: how long stock lasts at this pace")

    s.section("Customer")
    s.line("active", "Active customers", _v(history, "active_customers"), kind="int",
           note="Customers who have bought and not yet lapsed")
    s.line("repeat_share", "Repeat order share", rep / orders, kind="pct",
           note="Repeat orders / orders")
    ltv = s.line("ltv", "LTV", _v(history, "ltv"),
                 note="Contribution before marketing a new customer brings over 12 months, from your cohorts")
    s.line("ltv_cac", "LTV : CAC", ltv / cac, kind="num2", note="LTV / blended CAC")
    s.line("rating", "Rating", _v(history, "rating"), kind="num2",
           note="Stars, 1 to 5. Moves 30% of the way to its target each month")
    s.line("nps", "NPS", _v(history, "nps"), kind="int")
    s.line("backlog", "Service backlog", _v(history, "cs_backlog"), kind="int",
           note="Customer queries not yet answered")

    s.section("Finance")
    s.line("cash", "Cash", _v(history, "cash_balance"), note="See the Cash sheet")
    s.line("runway", "Runway (months)", _v(history, "runway_rounds"), kind="num1",
           note="Cash / this month's cash burn; 99 when not burning cash")
    s.line("cod", "COD in transit", _v(history, "cod_receivable"),
           note="Cash couriers have collected and not yet paid you")
    s.line("credit", "Credit drawn", _v(history, "credit_drawn"))
    s.line("net_profit", "Net profit", link("net_profit"), link=True, note="From the P&L")
    s.line("interest", "Interest paid", -link("interest"), link=True, note="From the P&L")
    return s


# --- Product tables ----------------------------------------------------------------------

def _table(book, ws, top, cols, rows, widths=None):
    """A plain table: header row, data rows, a totals row. `cols` is a list
    of (header, kind, getter) where getter(row_index_in_sheet, item) returns a
    value, or a (formula, value) pair; kind "sum" in the total row sums it."""
    ws.set_row(top, 30)
    for j, (head, kind, _, _) in enumerate(cols):
        ws.write(top, j, head, book.f("head" if kind in ("text", "textwrap") else "head_r"))
        if widths:
            ws.set_column(j, j, widths[j])
    for i, item in enumerate(rows):
        r = top + 1 + i
        for j, (_, kind, get, _) in enumerate(cols):
            v = get(r + 1, item)
            if isinstance(v, tuple):
                ws.write_formula(r, j, "=" + v[0], book.f(kind, "calc"), _clean(v[1]))
            elif v is None:
                ws.write_blank(r, j, None, book.f(kind, "input"))
            elif kind == "text":
                ws.write_string(r, j, str(v), book.f("label") if j == 0 else book.f("text", "input"))
            elif kind == "textwrap":
                ws.write_string(r, j, str(v), book.f("wrap_in"))
            else:
                ws.write_number(r, j, float(v), book.f(kind, "input"))
    return top + 1 + len(rows)


def _products(book, h, month):
    ws = book.sheet("Products")
    rows = h.get("products") or []
    ws.write(0, 0, f"Sales by product, month {month}", book.f("title"))
    if not rows:
        ws.write(1, 0, "Product detail is recorded from month 2 of the first live game onwards.",
                 book.f("intro"))
        return
    ws.write(1, 0, "Each line's units, sales and margins, adding up to the P&L. Costs are positive "
                   "here; margins are sales less costs.", book.f("intro"))
    names = h.get("segment_names") or {}
    top, n = 3, len(rows)
    first, last = top + 2, top + 1 + n
    L = lambda c: xl_col_to_name(c)
    tot_units = sum(r["units"] for r in rows) or 1.0
    tot_net = sum(r["net_sales"] for r in rows) or 1.0

    def f(expr, val):
        return (expr, val)

    cols = [
        ("Product", "text", lambda r, x: x["name"], None),
        ("Category", "text", lambda r, x: str(x["category"]).title(), None),
        ("Units sold", "int", lambda r, x: x["units"], "sum"),
        ("Share of units", "pct", lambda r, x: f(f"IFERROR(C{r}/C${last + 1},0)", x["units"] / tot_units), "sum"),
        ("Typical store share", "pct", lambda r, x: x["typical_share"], "sum"),
        ("vs typical", "pct", lambda r, x: f(f"IFERROR(D{r}/E{r}-1,0)",
                                             x["unit_share"] / x["typical_share"] - 1 if x["typical_share"] else 0), None),
        ("Net sales", "pkr", lambda r, x: x["net_sales"], "sum"),
        ("Avg price a unit", "pkr", lambda r, x: f(f"IFERROR(G{r}/C{r},0)",
                                                   x["net_sales"] / x["units"] if x["units"] else 0), None),
        ("Share of sales", "pct", lambda r, x: f(f"IFERROR(G{r}/G${last + 1},0)", x["net_sales"] / tot_net), "sum"),
        ("Product cost", "pkr", lambda r, x: x["net_sales"] - x["gross_margin"], "sum"),
        ("Gross margin", "pkr", lambda r, x: f(f"G{r}-J{r}", x["gross_margin"]), "sum"),
        ("GM %", "pct", lambda r, x: f(f"IFERROR(K{r}/G{r},0)", x["gm_pct"]), "ratio:K/G"),
        ("Delivery and packing", "pkr", lambda r, x: x["delivery_cost"], "sum"),
        ("Payment and marketplace fees", "pkr",
         lambda r, x: x["gross_margin"] - x["delivery_cost"] - x["cm_pre"], "sum"),
        ("Contribution before mktg", "pkr", lambda r, x: f(f"K{r}-M{r}-N{r}", x["cm_pre"]), "sum"),
        ("CM %", "pct", lambda r, x: f(f"IFERROR(O{r}/G{r},0)", x["cm_pre_pct"]), "ratio:O/G"),
        ("Marketing", "pkr", lambda r, x: x["marketing"], "sum"),
        ("Contribution after mktg", "pkr", lambda r, x: f(f"O{r}-Q{r}", x["cm"]), "sum"),
        ("Units short of demand", "int", lambda r, x: x.get("short", 0.0), "sum"),
        ("Main buyers", "text", lambda r, x: ", ".join(
            f"{names.get(k, k)} {v:.0%}" for k, v in sorted(x["buyers"].items(), key=lambda kv: -kv[1])[:2]), None),
        ("Why it sold the way it did", "textwrap", lambda r, x: "; ".join(x.get("why") or []) or "In line with a typical store", None),
    ]
    widths = [22, 11, 9, 9, 9, 9, 12, 10, 9, 12, 12, 8, 11, 12, 13, 8, 11, 13, 10, 30, 60]
    end = _table(book, ws, top, cols, rows, widths)
    # Totals
    ws.write(end, 0, "All products", book.f("label_b"))
    for j, (_, kind, _, how) in enumerate(cols):
        if how == "sum":
            col = L(j)
            ws.write_formula(end, j, f"=SUM({col}{first}:{col}{last})", book.f(kind, "calc", True),
                             _clean(_sum_of(cols[j], rows, first)))
        elif how and how.startswith("ratio:"):
            a, b = how[6:].split("/")
            ja, jb = ord(a) - 65, ord(b) - 65
            va, vb = _sum_of(cols[ja], rows, first), _sum_of(cols[jb], rows, first)
            ws.write_formula(end, j, f"=IFERROR({a}{end + 1}/{b}{end + 1},0)", book.f(kind, "calc", True),
                             _clean(va / vb if vb else 0))
    ws.freeze_panes(top + 1, 1)
    ws.autofilter(top, 0, last - 1, len(cols) - 1)
    ws.write(end + 2, 0, "How to read it", book.f("label_b"))
    notes = [
        "Net sales: units x net price, less pack savings, less this line's share of returns (weighted by how often it is "
        "sent back), failed deliveries and the prepaid discount.",
        "Product cost: the landed cost of the units that stayed sold, plus write-off of unsellable returns.",
        "Delivery and packing: shared by items in the parcel, so a cheap item carries as much as a dear one; a 3-pack is one item.",
        "Payment and marketplace fees: shared by net sales. Marketing: a product campaign's spend goes to the products it named; "
        "the rest is shared by net sales.",
        "Typical store share: the share of units a store selling the same range, at one price position, to the other stores' "
        "customer mix would sell.",
    ]
    for i, t in enumerate(notes):
        ws.write(end + 3 + i, 0, t, book.f("note"))


def _sum_of(col, rows, first):
    _, kind, get, _ = col
    tot = 0.0
    for i, x in enumerate(rows):
        v = get(first + i, x)
        v = v[1] if isinstance(v, tuple) else v
        tot += float(v or 0.0)
    return tot


def _stock(book, h, month):
    ws = book.sheet("Stock")
    rows = h.get("stock") or []
    ws.write(0, 0, f"Stock by product, month {month}", book.f("title"))
    if not rows:
        ws.write(1, 0, "Stock detail by product is recorded from month 2 of the first live game onwards. "
                       f"Units in stock at month end: {h.get('inventory_units', 0):,.0f}.", book.f("intro"))
        return
    ws.write(1, 0, "Opening + received + back from failed deliveries - sold = closing. Your purchase is split "
                   "across products by last month's demand, topping up lines that ran short first.",
             book.f("intro"))
    top, n = 3, len(rows)
    first, last = top + 2, top + 1 + n
    L = lambda c: xl_col_to_name(c)
    cols = [
        ("Product", "text", lambda r, x: x["name"], None),
        ("Opening stock", "int", lambda r, x: x["open"], "sum"),
        ("Received (purchases landed)", "int", lambda r, x: x["received"], "sum"),
        ("Back from failed deliveries", "int", lambda r, x: x["returned"], "sum"),
        ("Sold", "int", lambda r, x: x["sold"], "sum"),
        ("Closing stock", "int", lambda r, x: (f"B{r}+C{r}+D{r}-E{r}", x["close"]), "sum"),
        ("Demand (units wanted)", "int", lambda r, x: x["wanted"], "sum"),
        ("Short of demand", "int", lambda r, x: (f"MAX(0,G{r}-E{r})", max(0.0, x["wanted"] - x["sold"])), "sum"),
        ("Weeks of cover", "num1", lambda r, x: (f"IFERROR(F{r}*4.33/E{r},0)",
                                                 x["close"] * 4.33 / x["sold"] if x["sold"] else 0), "ratio"),
        ("Landed cost a unit", "pkr", lambda r, x: x["unit_cost"], None),
        ("Stock value", "pkr", lambda r, x: (f"F{r}*J{r}", x["close"] * x["unit_cost"]), "sum"),
        ("Ordered this month", "int", lambda r, x: x["ordered"], "sum"),
        ("On order, not yet landed", "int", lambda r, x: x["on_order"], "sum"),
        ("Next arrival (month)", "int", lambda r, x: x.get("next_arrival"), None),
        ("Back next month (in transit)", "int", lambda r, x: x.get("back_next_month", 0.0), "sum"),
    ]
    widths = [22, 11, 13, 13, 10, 11, 12, 11, 10, 11, 12, 12, 13, 11, 13]
    end = _table(book, ws, top, cols, rows, widths)
    ws.write(end, 0, "All products", book.f("label_b"))
    for j, (_, kind, _, how) in enumerate(cols):
        col = L(j)
        if how == "sum":
            ws.write_formula(end, j, f"=SUM({col}{first}:{col}{last})", book.f(kind, "calc", True),
                             _clean(_sum_of(cols[j], rows, first)))
    sold = sum(x["sold"] for x in rows)
    ws.write_formula(end, 8, f"=IFERROR(F{end + 1}*4.33/E{end + 1},0)", book.f("num1", "calc", True),
                     _clean(sum(x["close"] for x in rows) * 4.33 / sold if sold else 0))
    ws.freeze_panes(top + 1, 1)
    ws.autofilter(top, 0, last - 1, len(cols) - 1)
    notes = [
        "Weeks of cover: closing stock x 4.33 weeks / units sold this month - how long the stock lasts at this pace.",
        "Landed cost: catalogue cost x your supplier's cost index x your sourcing choice. Stock value = closing x landed cost.",
        "Back from failed deliveries: last month's refused and failed parcels, back on the shelf this month (a few are "
        "damaged in transit). Back next month: this month's, still on the way back.",
        "On order: purchases placed and not yet landed, this month's included. Lead time depends on your supplier and sourcing.",
    ]
    for i, t in enumerate(notes):
        ws.write(end + 2 + i, 0, t, book.f("note"))


def _products_by_month(book, history, months):
    ws = book.sheet("Products by month")
    ws.write(0, 0, "Products and stock, every month", book.f("title"))
    ws.write(1, 0, "One row per product per month. Filter it, or insert a pivot table to compare months.",
             book.f("intro"))
    items = []
    for m, h in zip(months, history):
        stock = {s["code"]: s for s in h.get("stock") or []}
        for p in h.get("products") or []:
            items.append((m, p, stock.get(p["code"], {})))
    if not items:
        ws.write(3, 0, "Product detail is recorded from month 2 of the first live game onwards.", book.f("intro"))
        return
    cols = [
        ("Month", "int", lambda r, x: x[0], None),
        ("Product", "text", lambda r, x: x[1]["name"], None),
        ("Category", "text", lambda r, x: str(x[1]["category"]).title(), None),
        ("Units sold", "int", lambda r, x: x[1]["units"], None),
        ("Net sales", "pkr", lambda r, x: x[1]["net_sales"], None),
        ("Product cost", "pkr", lambda r, x: x[1]["net_sales"] - x[1]["gross_margin"], None),
        ("Gross margin", "pkr", lambda r, x: (f"E{r}-F{r}", x[1]["gross_margin"]), None),
        ("Cost to serve", "pkr", lambda r, x: x[1]["gross_margin"] - x[1]["cm_pre"], None),
        ("Contribution before mktg", "pkr", lambda r, x: (f"G{r}-H{r}", x[1]["cm_pre"]), None),
        ("Marketing", "pkr", lambda r, x: x[1]["marketing"], None),
        ("Contribution after mktg", "pkr", lambda r, x: (f"I{r}-J{r}", x[1]["cm"]), None),
        ("Opening stock", "int", lambda r, x: x[2].get("open"), None),
        ("Received", "int", lambda r, x: x[2].get("received"), None),
        ("Back from failed deliveries", "int", lambda r, x: x[2].get("returned"), None),
        ("Closing stock", "int", lambda r, x: x[2].get("close"), None),
        ("On order", "int", lambda r, x: x[2].get("on_order"), None),
        ("Stock value", "pkr", lambda r, x: x[2].get("value"), None),
    ]
    widths = [7, 22, 11, 10, 12, 12, 12, 12, 14, 11, 14, 11, 10, 13, 11, 10, 12]
    end = _table(book, ws, 3, cols, items, widths)
    ws.freeze_panes(4, 2)
    ws.autofilter(3, 0, end - 1, len(cols) - 1)


# --- Cash ---------------------------------------------------------------------------------

def _cash(book, history, months, pl):
    s = Sheet(book, "Cash", months, "Cash: why it is not the same as profit",
              "Profit counts a sale when it is made; cash arrives when the customer or courier pays. "
              "Stock is paid for when the supplier's terms fall due, not when it sells.")
    flows = [h.get("cash_flow") or {} for h in history]
    have = [bool(f) for f in flows]
    get = lambda k, sign=1.0: [sign * float(f.get(k, 0.0)) if ok else None for f, ok in zip(flows, have)]
    s.section("Cash this month")
    op = s.line("opening", "Opening cash", get("opening"))
    rc = s.line("receipts", "Received from customers and couriers", get("receipts"),
                note="Prepaid orders settle within days; COD arrives when couriers remit, weeks later")
    sp = s.line("suppliers", "Paid to suppliers", get("supplier_payments", -1),
                note="Stock bought earlier, paid as the supplier's terms fall due")
    oc = s.line("operating", "Operating costs paid", get("operating", -1),
                note="Delivery, payment fees, marketing, commission, overheads - the P&L's costs below gross profit")
    it = s.line("interest", "Interest", get("interest", -1))
    cx = s.line("capex", "Investments (AI modules, capability)", get("capex", -1))
    cd = s.line("credit", "Credit drawn this month", get("credit_draw"),
                note="Drawn automatically when cash would go below zero, up to the credit limit")
    closing_formula = total(op, rc, sp, oc, it, cx, cd)
    s.ws.write(s.r, 0, "Closing cash", book.f("label_b"))
    vals = []
    for i, h in enumerate(history):
        if have[i]:
            v = closing_formula.val(i)
            s.ws.write_formula(s.r, s.first + i, "=" + closing_formula.xl(s.col(i)),
                               book.f("pkr", "calc", True), _clean(v))
        else:
            v = float(h.get("cash_balance") or 0.0)
            s.ws.write_number(s.r, s.first + i, v, book.f("pkr", "input", True))
        vals.append(v)
    s.ws.write(s.r, s.first + len(months),
               "Opening + received - paid out + credit drawn"
               + ("" if all(have) else ". Months without the lines show the closing balance only"),
               book.f("note"))
    s.rows["closing"], s.values["closing"] = s.r, vals
    s.r += 1

    s.section("Still to come in or go out")
    s.line("cod_transit", "COD in transit (couriers owe you)", _v(history, "cod_receivable"),
           note="Collected from customers, not yet paid to you")
    s.line("owed", "Owed to suppliers", get("owed_to_suppliers"),
           note="Stock already ordered, payment not yet due")
    s.line("ordered", "Stock ordered this month (at cost)", get("purchases_ordered"),
           note="Becomes a supplier payment when the terms fall due")
    s.line("credit_total", "Credit drawn to date", _v(history, "credit_drawn"))

    s.section("Against profit")
    s.line("net_profit", "Net profit (from the P&L)", pl.ref("net_profit", sheet=s), link=True)
    s.line("sales_cod", "Sales on cash on delivery this month", get("sales_cod"),
           note="Booked as revenue now, paid in cash later")
    return s


# --- Campaigns and customers ------------------------------------------------------------

def _campaigns(book, history, months):
    ws = book.sheet("Campaigns")
    ws.write(0, 0, "Paid media, campaign by campaign", book.f("title"))
    ws.write(1, 0, "Clicks are store visits. Orders are attributed from real sessions, so they add up to your paid "
                   "orders, not to what a platform dashboard would claim.", book.f("intro"))
    items = [(m, c) for m, h in zip(months, history) for c in h.get("campaigns") or []]
    if not items:
        ws.write(3, 0, "No paid media yet.", book.f("intro"))
        return
    cols = [
        ("Month", "int", lambda r, x: x[0], None),
        ("Channel", "text", lambda r, x: x[1].get("channel_name", ""), None),
        ("Campaign", "text", lambda r, x: x[1].get("name", ""), None),
        ("Spend", "pkr", lambda r, x: x[1]["spend"], None),
        ("Impressions", "int", lambda r, x: x[1]["impressions"], None),
        ("CPM", "pkr", lambda r, x: (f"IFERROR(D{r}/E{r}*1000,0)", x[1]["cpm"]), None),
        ("Clicks (visits)", "int", lambda r, x: x[1]["clicks"], None),
        ("CTR", "pct2", lambda r, x: (f"IFERROR(G{r}/E{r},0)", x[1]["ctr"]), None),
        ("CPC", "num1", lambda r, x: (f"IFERROR(D{r}/G{r},0)", x[1]["cpc"]), None),
        ("Orders", "int", lambda r, x: x[1]["orders"], None),
        ("CVR", "pct2", lambda r, x: (f"IFERROR(J{r}/G{r},0)", x[1]["cvr"]), None),
        ("Revenue", "pkr", lambda r, x: x[1].get("revenue", 0.0), None),
        ("ROAS", "num2", lambda r, x: (f"IFERROR(L{r}/D{r},0)", x[1].get("roas", 0.0)), None),
        ("CAC", "pkr", lambda r, x: x[1].get("cac", 0.0), None),
    ]
    widths = [7, 15, 30, 12, 13, 9, 13, 8, 8, 9, 8, 12, 8, 10]
    end = _table(book, ws, 3, cols, items, widths)
    ws.freeze_panes(4, 3)
    ws.autofilter(3, 0, end - 1, len(cols) - 1)
    ws.write(end + 1, 0, "CAC: spend / (orders x this month's share of orders from new customers).",
             book.f("note"))


def _customers(book, latest, history, months):
    ws = book.sheet("Customers")
    ws.set_column(0, 0, 26)
    ws.write(0, 0, "Who your orders came from", book.f("title"))
    ws.write(1, 0, "From your own orders - what a store reads from what its visitors browse and buy. How big each "
                   "segment is across the market, and what it values, is what MR-06 sells.", book.f("intro"))
    names = latest.get("segment_names") or {}
    segs = [h.get("order_segments") or {} for h in history]
    codes = list(names) or sorted({k for s in segs for k in s})
    if not codes:
        ws.write(3, 0, "Customer segment detail is recorded from month 2 of the first live game onwards.",
                 book.f("intro"))
        return
    ws.write(3, 0, "Share of orders", book.f("head"))
    for i, m in enumerate(months):
        ws.write(3, 1 + i, f"Month {m}", book.f("head_r"))
        ws.set_column(1 + i, 1 + i, 11)
    for j, c in enumerate(codes):
        ws.write(4 + j, 0, names.get(c, c), book.f("label"))
        for i, s in enumerate(segs):
            if s:
                ws.write_number(4 + j, 1 + i, float(s.get(c, 0.0)), book.f("pct", "input"))
            else:
                ws.write_blank(4 + j, 1 + i, None, book.f("pct", "input"))
    r = 4 + len(codes)
    ws.write(r, 0, "All orders", book.f("label_b"))
    for i, s in enumerate(segs):
        col = xl_col_to_name(1 + i)
        ws.write_formula(r, 1 + i, f"=SUM({col}5:{col}{r})", book.f("pct", "calc", True),
                         _clean(sum(s.values()) if s else 0.0))

    rows = latest.get("products") or []
    if not rows:
        return
    top = r + 3
    ws.write(top - 1, 0, f"Who bought each product, month {months[-1]} (share of the product's units)",
             book.f("label_b"))
    ws.write(top, 0, "Product", book.f("head"))
    for j, c in enumerate(codes):
        ws.write(top, 1 + j, names.get(c, c), book.f("head_r"))
        ws.set_column(1 + j, 1 + j, 17)
    for i, p in enumerate(rows):
        ws.write(top + 1 + i, 0, p["name"], book.f("label"))
        for j, c in enumerate(codes):
            ws.write_number(top + 1 + i, 1 + j, float(p["buyers"].get(c, 0.0)), book.f("pct", "input"))
