"""Stock and cash detail for months recorded before the engine kept it.

The first live game's early months were recorded before a month's record
carried its stock movement by product and its cash flow line by line. Both are
rebuilt here from the world saved at the end of each month - stock on the
shelf, purchase orders, parcels on their way back, money owed each way - with
the same arithmetic the engine now records. Nothing is estimated: a month whose
saved positions are missing is left as it was.

Rebuilt detail is for reading (reports, workbooks, the stock tile). It is never
written back, and the engine never sees it.
"""
from __future__ import annotations

from . import mix
from .modules import m03_supply as m03

CASH_COSTS = ("fulfilment", "rto_cost", "return_cost", "payment_costs", "marketing",
              "commission", "below_line")


def fill(world, saved: dict, params, decisions: dict | None = None) -> list[int]:
    """Add stock and cash detail to every record that lacks it.

    `saved` maps a month to the world as it stood at the end of that month,
    with 0 for the world before month 1. `decisions` maps a month to each
    team's submission, for the supplier and sourcing that set landed cost.
    Returns the months that gained detail.
    """
    done = set()
    for tid, team in world.teams.items():
        for i, h in enumerate(team.history):
            month = int(h.get("round", i + 1))
            prev = _team(saved.get(month - 1), tid)
            now = _team(saved.get(month), tid)
            if prev is None or now is None:
                continue
            if not h.get("stock"):
                d = ((decisions or {}).get(month) or {}).get(tid) or {}
                h["stock"] = stock(prev, now, h, params, d, month)
                h.setdefault("rebuilt", []).append("stock")
                done.add(month)
            if not h.get("cash_flow"):
                h["cash_flow"] = cash(prev, now, h, month)
                h.setdefault("rebuilt", []).append("cash_flow")
                done.add(month)
    return sorted(done)


def _team(world, tid):
    return world.teams.get(tid) if world is not None else None


def stock(prev, now, record: dict, params, d: dict, month: int) -> list[dict]:
    """One month's stock movement by product, as mix.stock_lines records it.

    Opening is last month's closing; received is every order due by this
    month; back from failed deliveries is what last month sent back. Sold is
    what balances them against this month's closing - the engine's own
    identity, since nothing else moves stock.
    """
    received: dict[str, float] = {}
    for po in prev.open_pos:
        if po["arrives"] <= month:
            for c, u in po["units"].items():
                received[c] = received.get(c, 0.0) + u
    returned = dict(getattr(prev, "_pending_rto_units", None) or {})
    pending = dict(getattr(now, "_pending_rto_units", None) or {})
    wanted = {p["code"]: p.get("short", 0.0) for p in record.get("products") or []}
    supplier = m03._supplier(params, d)
    codes = list(dict.fromkeys(mix.active(now, params) + list(now.inventory)))
    rows = []
    for c in codes:
        opening = prev.inventory.get(c, 0.0)
        close = now.inventory.get(c, 0.0)
        sold = max(0.0, opening + received.get(c, 0.0) + returned.get(c, 0.0) - close)
        cost = (float(params.sku(c)["unit_cost"]) * float(supplier["cost_index"])
                * m03.landed_index(now, c, d) * params["cogs_scale"])
        rows.append({
            "code": c, "name": params.sku(c)["name"],
            "category": params.sku(c)["category"],
            "open": opening, "received": received.get(c, 0.0),
            "returned": returned.get(c, 0.0),
            "sold": sold, "wanted": sold + wanted.get(c, 0.0), "close": close,
            "ordered": sum(po["units"].get(c, 0.0) for po in now.open_pos
                           if po.get("placed") == month),
            "on_order": sum(po["units"].get(c, 0.0) for po in now.open_pos),
            "next_arrival": min((po["arrives"] for po in now.open_pos
                                 if po["units"].get(c, 0.0) > 0), default=None),
            "back_next_month": pending.get(c, 0.0),
            "unit_cost": cost, "value": close * cost,
            "weeks_cover": close * 4.33 / sold if sold > 0 else None,
        })
    return rows


def cash(prev, now, record: dict, month: int) -> dict:
    """One month's cash flow, line by line, as M15 records it.

    Opening and closing are the saved balances; supplier payments are what
    last month's ledger had falling due; operating costs are the P&L's cash
    costs; investments are projects started this month; credit is the change
    in the amount drawn. Received from customers is what balances them.
    """
    pnl = record["pnl"]
    opening, closing = float(prev.cash), float(now.cash)
    suppliers = float(prev.payables.get(month, 0.0))
    operating = sum(float(pnl.get(k, 0.0)) for k in CASH_COSTS)
    interest = float(pnl.get("interest", 0.0))
    capex = float(sum(p["capex"] for p in now.projects if p.get("started") == month))
    draw = float(now.credit_drawn - prev.credit_drawn)
    return {
        "opening": opening,
        "receipts": closing - draw - opening + suppliers + operating + interest + capex,
        "supplier_payments": suppliers, "operating": operating,
        "interest": interest, "capex": capex, "credit_draw": draw, "closing": closing,
        "purchases_ordered": float(sum(po["cost"] for po in now.open_pos
                                       if po.get("placed") == month)),
        "owed_to_suppliers": float(sum(now.payables.values())),
        "cod_in_transit": float(now.cod_receivable),
    }
