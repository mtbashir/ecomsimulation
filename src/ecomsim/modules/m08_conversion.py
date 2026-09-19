"""M8 - Conversion & order realisation.

The two-sided constraint is the spine of the whole simulation:

    orders = min(potential_demand, traffic_capacity, stock_capacity)

which makes under-marketing, wasted spend and stock-outs separately diagnosable
rather than collapsing them all into "your conversion rate was low".
"""
from __future__ import annotations


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def run(world, params, resolved, ctx) -> None:
    orders: dict[str, float] = {}
    spare: dict[str, float] = {}

    for team in world.teams.values():
        tid = team.team_id
        cr = _conversion_rate(team, params, ctx)
        ctx.setdefault("conversion_rate", {})[tid] = cr

        traffic_capacity = ctx["sessions"][tid] * cr
        stock_capacity = ctx.get("stock_capacity", {}).get(tid, float("inf"))
        potential = ctx["potential"][tid]

        realised = min(potential, traffic_capacity, stock_capacity)
        orders[tid] = realised
        spare[tid] = max(0.0, min(traffic_capacity, stock_capacity) - realised)

        # The diagnosis a debrief actually needs.
        if traffic_capacity < potential:
            binding = "under_marketing"
        elif stock_capacity < min(potential, traffic_capacity):
            binding = "stock_out"
        elif potential < traffic_capacity:
            binding = "wasted_spend"
        else:
            binding = "balanced"
        ctx.setdefault("binding_constraint", {})[tid] = binding

    _redistribute(world, params, ctx, orders, spare)
    ctx["orders"] = orders


def _conversion_rate(team, params, ctx) -> float:
    tid = team.team_id
    price_index = ctx.get("price_index", {}).get(tid, 1.0)
    instock = ctx.get("instock_ratio", {}).get(tid, 0.95)
    gateway = ctx.get("gateway_success", {}).get(tid, 0.91)
    cod_on = ctx.get("cod_enabled", {}).get(tid, True)
    fit = ctx.get("assortment_fit_mean", {}).get(tid, 0.5)

    m_price = _clamp(price_index ** params["price_elasticity"], 0.5, 1.8)
    m_ux = _clamp(1 + params["ux_cr_coef"] * (team.ux_score - 0.5), 0.75, 1.25)
    # Prior round's rating: ratings never affect the round in which they are earned.
    m_rating = _clamp(1 + params["rating_cr_coef"] * (team.rating - 4.0), 0.70, 1.20)
    m_stock = _clamp(1 - params["stockout_cr_penalty"] * (1 - instock), 0.55, 1.0)
    m_pay = gateway * (1 + params["cod_cr_lift"] * (1.0 if cod_on else 0.0))
    m_deliv = _clamp(1 + params["deliv_cr_coef"] * (team.delivery_perceived - 0.5), 0.85, 1.20)
    m_assort = _clamp(1 + params["assort_cr_coef"] * (fit - 0.5), 0.90, 1.12)

    return (params["cr_base"] * m_price * m_ux * m_rating
            * m_stock * m_pay * m_deliv * m_assort)


def _redistribute(world, params, ctx, orders, spare) -> None:
    """Two passes, then residual demand leaks out of the category.

    Not iterated to convergence: real markets lose customers who do not buy at
    all, and unbounded iteration hides the consequence of a stock-out.
    """
    for _ in range(int(params["redistribution_iterations"])):
        unmet = sum(max(0.0, ctx["potential"][t] - orders[t]) for t in orders)
        if unmet <= 1e-6:
            return
        capacity = sum(spare.values())
        if capacity <= 1e-6:
            return
        for tid in orders:
            take = min(spare[tid], unmet * (spare[tid] / capacity))
            orders[tid] += take
            spare[tid] -= take
