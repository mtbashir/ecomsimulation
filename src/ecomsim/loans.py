"""Working capital: borrowing as a decision, not something that happens to you.

Before this, the credit line drew itself whenever cash would go below zero and
was never paid back: a team could run the year on the bank's money without
noticing, and kept paying 22% on every rupee it had ever drawn. In a game on
the loan rules (world.loans):

1. Each month the team is told what it needs - bills due, the stock it is
   ordering, its marketing and fixed costs, less the cash it holds and the
   money coming in - and approves a loan (decision 12.6). Nothing approved
   means no new borrowing.
2. If cash plus the approved loan cannot pay for the month, the stock order is
   cut first, then marketing and the other discretionary spend, before the
   month runs. The team trades smaller, and the report says what was cut.
3. At month end the bank lends no more than approved. Only if a month still
   ends below zero - sales cost more to serve than the estimate allowed - does
   it cover the gap, reported as unplanned borrowing.
4. Spare cash repays: anything above a month of fixed costs goes to the loan
   automatically, and the team may repay more on purpose (decision 12.7).

Spending never runs past the cash (`check`, `fund`): stock, marketing, the
other monthly budgets, research and technology projects must fit within cash
in hand, plus customer money due this month, plus the loan applied for, less
the bills and running costs the month must pay anyway. The form refuses a
month that does not fit; the engine cuts one that still gets through. A game
on the automatic credit line counts what is left on the line as applied for.
"""
from __future__ import annotations

APPROVE, REPAY = "12.6", "12.7"
# Discretionary monthly spend, in the order it is protected: marketing first
# reaches customers, so it is the last to be cut within this group.
SPEND = ("3.1", "3.2", "3.4", "3.8", "3.9", "5.1", "6.1", "7.4")


def fixed_costs(params) -> float:
    """What the business costs to keep open for a month, before any choice."""
    return params["payroll_base"] + params["warehouse_fixed_cost"] + params["tech_fixed_cost"]


def automatic_order(team, params, d, world=None, rnd: int | None = None) -> tuple[float, float]:
    """(units, cost) of the order the engine places when 7.1 is left blank:
    "we order for you" - to the cover target, from this month's demand
    forecast, at the supplier's minimum or more. (0, 0) when the shelf and
    the orders already placed cover the target.

    It used to be read as whatever the engine ordered last month, so a month
    whose order had been cut for want of cash showed the next one as costing
    nothing: the loan suggested was too small, the form let the month
    through, and the order was cut again.
    """
    from .modules.m03_supply import (_expected_orders, automatic_units, demand_forecast,
                                     priced_order, purchase_scale)
    supplier = next((s for s in params.suppliers if s["code"] == str(d.get("7.2") or "B")),
                    params.suppliers[0])
    expected = (demand_forecast(team, params, world.run_id, rnd)[0]
                if world is not None and rnd else _expected_orders(team, params))
    units = automatic_units(team, params, d, supplier, expected)
    if units <= 0:
        return 0.0, 0.0
    units = max(units, float(supplier["moq_units"]))
    scale = purchase_scale(world, params) if world is not None else params["cogs_scale"]
    return units, priced_order(team, params, d, supplier, units, scale=scale)[1]


def stock_estimate(team, params, d, world=None, rnd: int | None = None) -> float:
    """What this month's stock order will cost: the team's own quantity at
    catalogue cost, or - when it leaves ordering to the engine - the order
    the engine will place (`automatic_order`)."""
    from .modules.m03_supply import purchase_plan
    total, lines = purchase_plan(d.get("7.1"))
    supplier = next((s for s in params.suppliers if s["code"] == str(d.get("7.2") or "B")),
                    params.suppliers[0])
    if total is None:
        return automatic_order(team, params, d, world, rnd)[1]
    if total <= 0:
        return 0.0
    units = max(total, float(supplier["moq_units"]))
    if lines:
        known = {s["code"]: s for s in params.skus}
        picked = {c: u for c, u in lines.items() if c in known and u > 0}
        avg = (sum(float(known[c]["unit_cost"]) * u for c, u in picked.items())
               / max(sum(picked.values()), 1.0)) if picked else 0.0
    else:
        skus = [params.sku(c) for c in team.active_skus] or params.skus
        w = sum(float(s["revenue_weight"]) for s in skus) or 1.0
        avg = sum(float(s["unit_cost"]) * float(s["revenue_weight"]) for s in skus) / w
    world_scale = params["cogs_scale"]          # new-rules games cost orders at scale
    return units * avg * float(supplier["cost_index"]) * world_scale


def spend_of(d, research: float = 0.0) -> float:
    return sum(float(d.get(k, 0) or 0) for k in SPEND) + research


def projects_of(team, d) -> float:
    """Technology projects started this month, paid in full when committed."""
    from .modules.m04_capability import PROJECTS
    started = {p["code"] for p in team.projects} | set(team.capabilities)
    return sum(float(spec["capex"]) for code, spec in PROJECTS.items()
               if code not in started and d.get(spec["decision"]))


def need(team, rnd: int, params, d, research: float = 0.0, world=None) -> dict:
    """Month `rnd`'s money, line by line, and the loan it calls for. The same
    arithmetic the form shows the team and the engine then applies. `world`
    (the one the month runs from) prices an order left to the engine exactly."""
    from .modules.m03_supply import purchase_plan
    due_out = team.payables.get(rnd, 0.0)
    due_in = team.receivables.get(rnd, 0.0)
    interest = team.credit_drawn * params["credit_rate_annual"] * params["round_months"] / 12
    stock = stock_estimate(team, params, d, world, rnd)
    auto = purchase_plan(d.get("7.1"))[0] is None
    spend = spend_of(d, research)
    projects = projects_of(team, d)
    fixed = fixed_costs(params)
    out = due_out + fixed + interest + stock + spend + projects
    has = team.cash + due_in
    return {"cash": team.cash, "receipts_due": due_in, "bills_due": due_out,
            "fixed": fixed, "interest": interest, "stock": stock, "stock_auto": auto,
            "stock_units": (automatic_order(team, params, d, world, rnd)[0] if auto else None),
            "spend": spend,
            "projects": projects,
            "outgoings": out, "need": max(0.0, out - has),
            "owed": team.credit_drawn,
            "headroom": max(0.0, params["credit_ceiling"] - team.credit_drawn)}


def approved_of(n, d, on_loans: bool) -> float:
    """The loan this month's spending may lean on: what the team applied for
    under the loan rules, else whatever is left on the automatic line."""
    if not on_loans:
        return n["headroom"]
    return min(max(0.0, float(d.get(APPROVE) or 0)), n["headroom"])


def check(n, approved: float) -> dict:
    """The month's cash balance: what is available to spend, what the team's
    decisions spend, and what is left - negative when they do not fit."""
    available = (n["cash"] + n["receipts_due"] + approved
                 - n["bills_due"] - n["fixed"] - n["interest"])
    planned = n["stock"] + n["spend"] + n["projects"]
    return {"available": available, "planned": planned,
            "left": available - planned, "approved": approved,
            "fits": planned <= max(available, 0.0) + 1.0}


def fund(team, world, params, d, ctx) -> None:
    """Fit the month's spending to cash plus the approved loan (step 2).

    Mutates the team's resolved decisions so every later module - traffic,
    the P&L, the order itself - sees the spending that could actually be paid.
    Runs in every game: on the automatic line the loan is what the line has left.
    """
    tid = team.team_id
    research = ctx.get("research_cost", {}).get(tid, 0.0)
    n = need(team, world.round, params, d, research, world)
    approved = approved_of(n, d, getattr(world, "loans", False))
    # Projects are committed first: the form refuses a month they do not fit.
    available = check(n, approved)["available"] - n["projects"]
    shortfall = n["stock"] + n["spend"] - available
    stock_cut = spend_cut = 0.0
    # The order itself is capped, not just the estimate: an order left to the
    # engine can come out larger than last month's.
    po_budget = max(0.0, available - n["spend"])
    if shortfall > 0:
        stock_cut = min(shortfall, n["stock"])
        rest = shortfall - stock_cut
        if rest > 0 and n["spend"] > 0:
            spend_cut = min(rest, n["spend"])
            keep = 1 - spend_cut / n["spend"]
            for k in SPEND:
                if d.get(k):
                    d[k] = float(d[k]) * keep
            if keep < 1 and research:
                d["12.1"] = []
                ctx.setdefault("research_cost", {})[tid] = 0.0
    ctx.setdefault("po_budget", {})[tid] = po_budget
    if not getattr(world, "loans", False):
        # The automatic line: no loan record (its presence marks the loan
        # rules in the reports), only what had to be cut, if anything.
        if stock_cut or spend_cut:
            ctx.setdefault("funding", {})[tid] = {
                "available": available, "stock_cut": stock_cut, "spend_cut": spend_cut}
        return
    ctx.setdefault("loan", {})[tid] = {
        **n, "approved": approved, "stock_cut": stock_cut, "spend_cut": spend_cut,
        "drawn": 0.0, "unplanned": 0.0, "repaid": 0.0, "repaid_by_choice": 0.0}


def settle(team, params, d, ctx) -> float:
    """Month end (steps 3 and 4). Returns the amount drawn this month."""
    tid = team.team_id
    loan = ctx.get("loan", {}).get(tid) or {"approved": 0.0}
    draw = 0.0
    if team.cash < 0:
        headroom = params["credit_ceiling"] - team.credit_drawn
        planned = min(-team.cash, loan["approved"], headroom)
        team.cash += planned
        team.credit_drawn += planned
        # The gap the estimate missed. Leaving it would put the team in
        # administration for an error in the bank's arithmetic, not its own.
        unplanned = min(max(0.0, -team.cash), headroom - planned)
        team.cash += unplanned
        team.credit_drawn += unplanned
        draw = planned + unplanned
        loan.update(drawn=planned, unplanned=unplanned)
    elif team.credit_drawn > 0:
        chosen = min(max(0.0, float(d.get(REPAY) or 0)), team.cash, team.credit_drawn)
        team.cash -= chosen
        team.credit_drawn -= chosen
        sweep = min(max(0.0, team.cash - fixed_costs(params)), team.credit_drawn)
        team.cash -= sweep
        team.credit_drawn -= sweep
        loan.update(repaid=chosen + sweep, repaid_by_choice=chosen)
    loan["owed_after"] = team.credit_drawn
    ctx.setdefault("loan", {})[tid] = loan
    return draw
