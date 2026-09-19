"""M10 - Fulfilment & delivery.

Capacity overflow degrades SLA; SLA degradation raises RTO; prepaid incentive
lowers it. Forward AND reverse shipping is charged on every RTO - that single
line is what teaches COD economics.
"""
from __future__ import annotations

DEFAULT_MIX = {"speed": 0.30, "value": 0.40, "wide": 0.30}


def run(world, params, resolved, ctx) -> None:
    events = ctx.get("events", {})

    for team in world.teams.values():
        tid = team.team_id
        d = ctx["resolved"][tid]
        orders = ctx["orders"][tid]

        capacity = team.warehouse_capacity + float(d.get("8.2", 0.4) or 0.4) * 4_000
        overflow = max(0.0, orders - capacity) / max(orders, 1.0)

        mix = d.get("8.3") if isinstance(d.get("8.3"), dict) else DEFAULT_MIX
        success = sum(
            share * float(params.__class__ and _courier(params, code)["success_rate"])
            for code, share in mix.items()
        ) * events.get("courier_success_mult", 1.0)

        sla = max(0.0, 1 - params["sla_overflow_coef"] * overflow)
        sla *= events.get("sla_mult", 1.0)

        cod_share = params["cod_share_base"] if ctx["cod_enabled"][tid] else 0.0
        prepaid_incentive = float(d.get("9.2", 0) or 0)
        # A prepaid incentive shifts the mix as well as lowering RTO on what remains.
        cod_share = max(0.0, cod_share - 2.4 * prepaid_incentive)
        prepaid_share = 1 - cod_share

        rto = (
            params["rto_base"]
            * (1 + params["rto_sla_coef"] * (1 - sla))
            * (1 - params["rto_prepaid_coef"] * min(1.0, prepaid_incentive / 0.10))
            * events.get("rto_mult", 1.0)
        )
        rto = max(0.0, min(0.9, rto))

        delivered = orders * (prepaid_share + cod_share * (1 - rto)) * success
        rto_orders = orders * cod_share * rto * success
        failed = orders * (1 - success)

        _stage_rto_stock(team, params, rto_orders + failed, ctx)

        team.delivery_actual = max(0.0, min(1.0, success * sla))

        ctx.setdefault("delivered", {})[tid] = delivered
        ctx.setdefault("rto_orders", {})[tid] = rto_orders
        ctx.setdefault("failed_orders", {})[tid] = failed
        ctx.setdefault("sla_attainment", {})[tid] = sla
        ctx.setdefault("cod_share", {})[tid] = cod_share
        ctx.setdefault("prepaid_share", {})[tid] = prepaid_share
        ctx.setdefault("rto_rate", {})[tid] = rto
        ctx.setdefault("courier_success", {})[tid] = success
        ctx.setdefault("courier_cost", {})[tid] = orders * sum(
            share * float(_courier(params, code)["cost_per_order"])
            for code, share in mix.items()
        )


def _courier(params, code: str) -> dict:
    try:
        return next(c for c in params.couriers if c["code"] == code)
    except StopIteration:
        return next(c for c in params.couriers if c["code"] == "wide")


def _stage_rto_stock(team, params, rto_orders: float, ctx) -> None:
    """RTO units rejoin sellable stock next round, less those damaged in transit."""
    units = rto_orders * params["units_per_order"] * params["rto_recovery"]
    skus = team.active_skus or [s["code"] for s in params.skus]
    total_w = sum(float(params.sku(c)["revenue_weight"]) for c in skus) or 1.0
    team._pending_rto_units = {
        c: units * float(params.sku(c)["revenue_weight"]) / total_w for c in skus
    }
