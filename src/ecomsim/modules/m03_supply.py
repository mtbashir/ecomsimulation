"""M3 - Supply arrival & inventory.

Stock constrains what can be sold, which is why this runs before M8. Lead time
is drawn, not fixed: forecasting AI does not shorten it, it improves the team's
visibility of it, which is the honest modelling of what forecasting does.
"""
from __future__ import annotations

from .. import rng

SUPPLIER_DEFAULT = "B"


def run(world, params, resolved, ctx) -> None:
    events = ctx.get("events", {})
    round_days = 30.44 * params["round_months"]

    for team in world.teams.values():
        tid = team.team_id
        d = ctx["resolved"][tid]

        _land_arrivals(team, world.round)
        _return_rto_units(team)

        supplier = params.__class__ and _supplier(params, d)
        ctx.setdefault("supplier_quality", {})[tid] = float(supplier["quality_index"])
        ctx.setdefault("supplier", {})[tid] = supplier

        _place_orders(team, world, params, ctx, d, supplier, events, round_days)

        units_available = sum(team.inventory.values())
        ctx.setdefault("stock_capacity", {})[tid] = (
            units_available / params["units_per_order"]
        )
        ctx.setdefault("instock_ratio", {})[tid] = _instock_ratio(team, params)


def _supplier(params, d) -> dict:
    code = str(d.get("7.2", SUPPLIER_DEFAULT))
    try:
        return next(s for s in params.suppliers if s["code"] == code)
    except StopIteration:
        return next(s for s in params.suppliers if s["code"] == SUPPLIER_DEFAULT)


def _land_arrivals(team, round_: int) -> None:
    remaining = []
    for po in team.open_pos:
        if po["arrives"] <= round_:
            for sku, units in po["units"].items():
                team.inventory[sku] = team.inventory.get(sku, 0.0) + units
        else:
            remaining.append(po)
    team.open_pos = remaining


def _return_rto_units(team) -> None:
    """RTO stock rejoins sellable inventory at the start of the next round.

    Structural decision: units are in transit during the round they fail, so
    they cannot be sold again until the next one.
    """
    pending = getattr(team, "_pending_rto_units", None)
    if pending:
        for sku, units in pending.items():
            team.inventory[sku] = team.inventory.get(sku, 0.0) + units
        team._pending_rto_units = {}


def _place_orders(team, world, params, ctx, d, supplier, events, round_days) -> None:
    """Order to the team's safety-stock target, respecting MOQ.

    Structural decision: a PO a team cannot pay for is DELAYED, not cancelled.
    Cancelling compounds a cash problem into a stock-out and accelerates the
    death spiral the scoring design works to avoid.
    """
    # Order up to cycle + pipeline + safety. The decision sets SAFETY stock;
    # cycle and lead-time cover are arithmetic, not a choice. Targeting safety
    # alone leaves every team structurally short by a round of consumption.
    safety_weeks = float(d.get("7.5", 2.0) or 2.0)
    round_weeks = 4.33 * params["round_months"]
    lead_weeks = float(supplier["lead_time_days"]) * events.get("lead_time_mult", 1.0) / 7
    target_weeks = round_weeks + lead_weeks + safety_weeks

    expected_orders = _expected_orders(team, params)
    units_needed_per_week = expected_orders * params["units_per_order"] / round_weeks * (
        round_weeks / 4.33) / params["round_months"]

    on_hand = sum(team.inventory.values())
    on_order = sum(sum(po["units"].values()) for po in team.open_pos)
    gap = target_weeks * units_needed_per_week - (on_hand + on_order)
    if gap <= 0:
        return

    moq = float(supplier["moq_units"])
    units = max(gap, moq)

    lead_days = float(supplier["lead_time_days"]) * events.get("lead_time_mult", 1.0)
    noise = 1 + rng.normal(world.run_id, world.round, team.team_id,
                           "leadtime", 0.0, params["lead_time_noise_sd"])
    lead_days *= max(0.4, noise)
    arrives = world.round + max(1, round(lead_days / round_days))

    skus = team.active_skus or [s["code"] for s in params.skus]
    total_w = sum(float(params.sku(c)["revenue_weight"]) for c in skus) or 1.0
    alloc = {
        c: units * float(params.sku(c)["revenue_weight"]) / total_w for c in skus
    }
    cost = sum(
        alloc[c] * float(params.sku(c)["unit_cost"]) * float(supplier["cost_index"])
        * events.get("import_cogs_mult", 1.0)
        for c in skus
    )

    team.open_pos.append({
        "placed": world.round, "arrives": arrives,
        "units": alloc, "cost": cost, "supplier": supplier["code"],
    })
    ctx.setdefault("po_cost", {})[team.team_id] = \
        ctx.get("po_cost", {}).get(team.team_id, 0.0) + cost


def _expected_orders(team, params) -> float:
    """Forecast from POTENTIAL demand, not realised orders.

    Forecasting on orders you failed to fulfil makes a stock-out
    self-perpetuating: you under-order, stock out again, and under-order
    further. Real bullwhip, but it should be a consequence of a team's safety
    stock policy, not unavoidable in the default case.
    """
    if team.history:
        recent = [max(h["orders"], h.get("sellable", h["orders"]))
                  for h in team.history[-3:]]
        return sum(recent) / len(recent)
    return params["baseline_team_revenue"] / params["aov_base"]


def _instock_ratio(team, params) -> float:
    """Revenue-weighted, not a share of SKUs (docs/10 definitional decisions)."""
    skus = team.active_skus or [s["code"] for s in params.skus]
    total_w = sum(float(params.sku(c)["revenue_weight"]) for c in skus) or 1.0
    in_stock = sum(
        float(params.sku(c)["revenue_weight"])
        for c in skus if team.inventory.get(c, 0.0) > 0
    )
    return in_stock / total_w
