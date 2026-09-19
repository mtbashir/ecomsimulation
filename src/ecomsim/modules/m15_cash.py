"""M15 - Cash & working capital.

Cash is where most teams actually fail, so the timing is explicit. COD remits
NEXT round; prepaid settles same round. A team growing 30% per round on 62% COD
with advance supplier terms runs out of cash while profitable - the most
valuable finance lesson in the sim, and it falls straight out of this timing.

Structural decision: the credit line draws AUTOMATICALLY when cash would go
negative and headroom exists. Teams should fail through decisions, not through
forgetting to press a button.
"""
from __future__ import annotations


def _schedule(ledger: dict, now: int, amount: float, lag_rounds: float) -> None:
    """Book an amount across the rounds a rolling lag actually spans.

    A 45-day term on a 30-day round is not "next round" - roughly two thirds
    falls in the next round and one third the round after. Rounding it to a
    whole round makes a month of purchasing land in a single lump.
    """
    if amount == 0:
        return
    whole = int(lag_rounds)
    frac = lag_rounds - whole
    ledger[now + whole] = ledger.get(now + whole, 0.0) + amount * (1 - frac)
    if frac > 0:
        ledger[now + whole + 1] = ledger.get(now + whole + 1, 0.0) + amount * frac


def run(world, params, resolved, ctx) -> None:
    round_days = 30.44 * params["round_months"]

    for team in world.teams.values():
        tid = team.team_id
        pnl = ctx["pnl"][tid]
        net_revenue = pnl["net_revenue"]

        prepaid = net_revenue * ctx["prepaid_share"][tid]
        cod = net_revenue * ctx["cod_share"][tid]

        # Prepaid settles in days, so effectively within the round. COD remits
        # on a rolling lag: orders placed early in the round are remitted
        # inside it, later ones are not. The split is the share of the round
        # that lies more than the remittance lag from its end.
        _schedule(team.receivables, world.round, prepaid,
                  params["gateway_settle_days"] / round_days)
        _schedule(team.receivables, world.round, cod,
                  params["cod_remit_days"] / round_days)
        inflow = team.receivables.pop(world.round, 0.0)
        team.cod_receivable = sum(team.receivables.values())

        payable_now = team.payables.pop(world.round, 0.0)
        po_cost = ctx.get("po_cost", {}).get(tid, 0.0)
        _schedule(team.payables, world.round, po_cost,
                  params["supplier_terms_days"] / round_days)

        outflow = (
            payable_now
            + pnl["fulfilment"] + pnl["rto_cost"] + pnl["return_cost"]
            + pnl["payment_costs"] + pnl["marketing"] + pnl["commission"]
            + pnl["below_line"] + pnl["interest"]
            + ctx.get("capex", {}).get(tid, 0.0)
        )

        team.cash += inflow - outflow

        if team.cash < 0:
            headroom = params["credit_ceiling"] - team.credit_drawn
            draw = min(headroom, -team.cash)
            team.credit_drawn += draw
            team.cash += draw

        insolvent = team.cash < 0
        if insolvent:
            team.in_administration = True
        elif team.in_administration and team.credit_drawn < 0.5 * params["credit_ceiling"]:
            team.in_administration = False  # recovered
        operating_cf = inflow - outflow
        runway = team.cash / abs(operating_cf) if operating_cf < 0 else 99.0

        ctx.setdefault("cash", {})[tid] = team.cash
        ctx.setdefault("runway_rounds", {})[tid] = runway
        ctx.setdefault("free_cash_flow", {})[tid] = operating_cf
        ctx.setdefault("insolvent", {})[tid] = insolvent
        ctx.setdefault("credit_drawn", {})[tid] = team.credit_drawn

        # EV-13: terms withdrawn above 80% drawn. The death-spiral accelerator,
        # deliberately included - it is how it works in reality, and the banded
        # runway score exists to make teams avoid getting here.
        if team.credit_drawn > 0.80 * params["credit_ceiling"]:
            ctx.setdefault("terms_withdrawn", {})[tid] = True
