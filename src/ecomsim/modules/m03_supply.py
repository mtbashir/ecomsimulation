"""M3 - Supply arrival & inventory.

Stock constrains what can be sold, which is why this runs before M8. Lead time
is drawn, not fixed: forecasting AI does not shorten it, it improves the team's
visibility of it, which is the honest modelling of what forecasting does.
"""
from __future__ import annotations

from .. import rng

SUPPLIER_DEFAULT = "B"
GAP_DAMPING = 0.5


def run(world, params, resolved, ctx) -> None:
    events = ctx.get("events", {})
    round_days = 30.44 * params["round_months"]

    for team in world.teams.values():
        tid = team.team_id
        d = ctx["resolved"][tid]

        _land_arrivals(team, world.round)
        _return_rto_units(team)

        supplier = dict(_supplier(params, d))
        # The team's founding sourcing strategy and positioning tier scale what
        # a unit lands at, on top of which supplier it buys from. Folding it in
        # here means every downstream cost - the purchase order in M3 and the
        # COGS in M9 - sees the same landed cost.
        supplier["cost_index"] = (float(supplier["cost_index"])
                                  * team.cost_multiplier)
        ctx.setdefault("supplier_quality", {})[tid] = float(supplier["quality_index"])
        ctx.setdefault("supplier", {})[tid] = supplier

        _publish_forecast(team, world, params, ctx)
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


def _publish_forecast(team, world, params, ctx) -> None:
    """The demand forecast a team actually sees - deliberately imperfect.

    Inventory is only a real decision if the team has to judge under
    uncertainty. Perfect hindsight makes ordering arithmetic. The forecasting
    AI module (11.2) narrows this error rather than shortening lead time,
    which is the honest modelling of what forecasting does.
    """
    sd = params["forecast_error_sd"]
    if "forecasting" in team.capabilities:
        sd *= 1 - params["forecast_ai_error_reduction"]
    truth = _expected_orders(team, params)
    noise = rng.normal(world.run_id, world.round, team.team_id, "forecast", 0.0, sd)
    ctx.setdefault("demand_forecast", {})[team.team_id] = max(0.0, truth * (1 + noise))
    ctx.setdefault("forecast_sd", {})[team.team_id] = sd


def _place_orders(team, world, params, ctx, d, supplier, events, round_days) -> None:
    """Place the team's order, or fall back to the order-up-to policy.

    When decision 7.1 is enabled the team names the quantity and lives with it.
    Otherwise the engine orders to cycle + pipeline + safety, working from the
    same imperfect forecast the team would have seen.

    Structural decision: a PO a team cannot pay for is DELAYED, not cancelled.
    Cancelling compounds a cash problem into a stock-out and accelerates the
    death spiral the scoring design works to avoid.
    """
    # Order up to cycle + pipeline + safety. The decision sets SAFETY stock;
    # cycle and lead-time cover are arithmetic, not a choice. Targeting safety
    # alone leaves every team structurally short by a round of consumption.
    manual = d.get("7.1")
    if manual is not None:
        units = max(0.0, float(manual))
        if units > 0:
            _commit_po(team, world, params, ctx, supplier, events, units, round_days)
        return

    safety_weeks = float(d.get("7.5", 2.0) or 2.0)
    round_weeks = 4.33 * params["round_months"]
    lead_weeks = float(supplier["lead_time_days"]) * events.get("lead_time_mult", 1.0) / 7
    # Half a round of cycle stock, not a full one: an order goes out every
    # round, so the position only has to bridge half the review period plus
    # the lead time. A full round of cycle stock on top ties up roughly two
    # months of COGS, which this business cannot fund.
    target_weeks = round_weeks / 2 + lead_weeks + safety_weeks

    expected_orders = ctx["demand_forecast"][team.team_id]
    units_needed_per_week = expected_orders * params["units_per_order"] / round_weeks * (
        round_weeks / 4.33) / params["round_months"]

    on_hand = sum(team.inventory.values())
    on_order = sum(sum(po["units"].values()) for po in team.open_pos)
    gap = target_weeks * units_needed_per_week - (on_hand + on_order)

    # Steady replenishment plus a damped correction. Ordering only when the
    # position dips below target produces a large order every other round and
    # none in between, whipsawing cover and cash for no reason a team chose.
    consumption = units_needed_per_week * 4.33 * params["round_months"]
    units = consumption + GAP_DAMPING * gap
    if units <= 0:
        return
    _commit_po(team, world, params, ctx, supplier, events, units, round_days)


def _commit_po(team, world, params, ctx, supplier, events, units, round_days) -> None:
    units = max(units, float(supplier["moq_units"]))


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
