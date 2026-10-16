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
"""
from __future__ import annotations

APPROVE, REPAY = "12.6", "12.7"
# Discretionary monthly spend, in the order it is protected: marketing first
# reaches customers, so it is the last to be cut within this group.
SPEND = ("3.1", "3.2", "3.4", "3.8", "3.9", "5.1", "6.1", "7.4")


def fixed_costs(params) -> float:
    """What the business costs to keep open for a month, before any choice."""
    return params["payroll_base"] + params["warehouse_fixed_cost"] + params["tech_fixed_cost"]


def stock_estimate(team, params, d) -> float:
    """What this month's stock order will cost: the team's own quantity at
    catalogue cost, or - when it leaves ordering to the engine - what the
    engine ordered last month."""
    from .modules.m03_supply import purchase_plan, purchase_scale
    total, lines = purchase_plan(d.get("7.1"))
    supplier = next((s for s in params.suppliers if s["code"] == str(d.get("7.2") or "B")),
                    params.suppliers[0])
    if total is None:
        last = team.history[-1] if team.history else {}
        return float((last.get("cash_flow") or {}).get("purchases_ordered", 0.0))
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


def need(team, rnd: int, params, d, research: float = 0.0) -> dict:
    """Month `rnd`'s money, line by line, and the loan it calls for. The same
    arithmetic the form shows the team and the engine then applies."""
    due_out = team.payables.get(rnd, 0.0)
    due_in = team.receivables.get(rnd, 0.0)
    interest = team.credit_drawn * params["credit_rate_annual"] * params["round_months"] / 12
    stock = stock_estimate(team, params, d)
    spend = spend_of(d, research)
    fixed = fixed_costs(params)
    out = due_out + fixed + interest + stock + spend
    has = team.cash + due_in
    return {"cash": team.cash, "receipts_due": due_in, "bills_due": due_out,
            "fixed": fixed, "interest": interest, "stock": stock, "spend": spend,
            "outgoings": out, "need": max(0.0, out - has),
            "owed": team.credit_drawn,
            "headroom": max(0.0, params["credit_ceiling"] - team.credit_drawn)}


def fund(team, world, params, d, ctx) -> None:
    """Fit the month's spending to cash plus the approved loan (step 2).

    Mutates the team's resolved decisions so every later module - traffic,
    the P&L, the order itself - sees the spending that could actually be paid.
    """
    tid = team.team_id
    research = ctx.get("research_cost", {}).get(tid, 0.0)
    n = need(team, world.round, params, d, research)
    approved = min(max(0.0, float(d.get(APPROVE) or 0)), n["headroom"])
    available = (n["cash"] + n["receipts_due"] + approved
                 - n["bills_due"] - n["fixed"] - n["interest"])
    shortfall = n["stock"] + n["spend"] - available
    stock_cut = spend_cut = 0.0
    po_budget = None
    if shortfall > 0:
        stock_cut = min(shortfall, n["stock"])
        po_budget = n["stock"] - stock_cut
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
    if po_budget is not None:
        ctx.setdefault("po_budget", {})[tid] = po_budget
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
