"""M3 - Supply arrival & inventory.

Stock constrains what can be sold, which is why this runs before M8. Lead time
is drawn, not fixed: forecasting AI does not shorten it, it improves the team's
visibility of it, which is the honest modelling of what forecasting does.
"""
from __future__ import annotations

import math

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
        ctx.setdefault("supplier_quality", {})[tid] = float(supplier["quality_index"])
        ctx.setdefault("supplier", {})[tid] = supplier

        _publish_forecast(team, world, params, ctx)
        _learn_lead_time(team, events)
        _place_orders(team, world, params, ctx, d, supplier, events, round_days)

        units_available = sum(team.inventory.values())
        ctx.setdefault("stock_capacity", {})[tid] = (
            units_available / params["units_per_order"]
        )
        ctx.setdefault("instock_ratio", {})[tid] = _instock_ratio(team, params)


def landed_index(team, code: str, d=None) -> float:
    """How this team's own choices scale the cost of one product.

    Sourcing is chosen per product - at founding, and again any month the team
    wants to move a line. This month's choice wins; otherwise the founding one
    stands. A going-concern team chose neither, so it lands at 1.0 and nothing
    below it changes.
    """
    from ..founding import cost_multiplier
    from .m00_resolve import monthly_sourcing

    switched = monthly_sourcing(d or {}).get(code)
    if switched:
        tier = getattr(getattr(team, "founding", None), "tier", "mainstream")
        return cost_multiplier(switched, tier)
    return team.sku_cost_index.get(code, team.cost_multiplier)


def sourcing_of(team, code: str, d=None) -> str:
    """Where this product is coming from this month."""
    from .m00_resolve import monthly_sourcing
    return (monthly_sourcing(d or {}).get(code)
            or team.sku_sourcing.get(code, "mixed"))


def fx_multiplier(team, code: str, events, d=None) -> float:
    """A currency shock hits imported lines and leaves local ones alone.

    A team that never chose where its stock comes from - any going-concern
    game - takes the shock in full, exactly as it did before sourcing became a
    per-product decision. Choosing is what earns the shelter.
    """
    shock = events.get("import_cogs_mult", 1.0)
    if shock == 1.0 or not team.sku_sourcing:
        return shock
    from ..founding import fx_exposure
    return 1 + (shock - 1) * fx_exposure(sourcing_of(team, code, d))


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


def _learn_lead_time(team, events) -> None:
    """Move the buyer's assumption toward what deliveries are actually doing.

    Half the gap a month: a slip that lands in month 5 is half absorbed by
    month 6 and mostly gone by month 7, which is roughly how long it takes a
    real buyer to stop treating a late shipment as a one-off. Forewarning is
    worth something precisely because this lag exists.
    """
    actual = events.get("lead_time_mult", 1.0)
    team.lead_time_belief += 0.5 * (actual - team.lead_time_belief)


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
    # Plan against the lead time the team BELIEVES, not the one the event is
    # about to impose. Reading the shock multiplier here made the policy
    # clairvoyant: the month a supplier slipped, the order already covered the
    # slip, so a lead-time shock cost nothing and no warning about one could be
    # worth buying. A buyer finds out late, which is the whole point of MR-17.
    lead_weeks = (float(supplier["lead_time_days"]) * team.lead_time_multiplier
                  * team.lead_time_belief / 7)
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


    lead_days = (float(supplier["lead_time_days"]) * team.lead_time_multiplier
                 * events.get("lead_time_mult", 1.0))
    noise = 1 + rng.normal(world.run_id, world.round, team.team_id,
                           "leadtime", 0.0, params["lead_time_noise_sd"])
    lead_days *= max(0.4, noise)
    # Ceiling, not rounding. Rounding let a 44-day shipment land inside a
    # 30-day month, so doubling a supplier's lead time changed nothing and the
    # whole lead-time dimension - sourcing, supplier choice, the EV-03 shock -
    # was invisible. A PO that takes longer than the month misses the month.
    arrives = world.round + max(1, math.ceil(lead_days / round_days))

    skus = team.active_skus or [s["code"] for s in params.skus]
    total_w = sum(float(params.sku(c)["revenue_weight"]) for c in skus) or 1.0
    alloc = {
        c: units * float(params.sku(c)["revenue_weight"]) / total_w for c in skus
    }
    d = ctx["resolved"][team.team_id]
    cost = sum(
        alloc[c] * float(params.sku(c)["unit_cost"]) * float(supplier["cost_index"])
        * landed_index(team, c, d) * fx_multiplier(team, c, events, d)
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
