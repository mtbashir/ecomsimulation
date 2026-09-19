"""M14 - Costs & P&L.

RTO cost is its own line, never folded into fulfilment. Teams must see it to
reason about COD, and it is the number most Pakistani operators have never had
to look at directly.

Contribution margin boundary per docs/10: marketing and commission sit ABOVE
the line; payroll, warehouse, technology and research sit below.
"""
from __future__ import annotations

MARKETING_DECISIONS = ["3.1", "3.2", "3.3", "3.4", "3.5", "3.7", "3.8", "3.9"]


def _inventory_costs(team, params, ctx, tid: str) -> tuple[float, float]:
    """Holding cost on all stock, plus a write-down on cover beyond the
    obsolescence horizon.

    Without these, ordering far too much costs only tied-up cash, and a team
    that floods its warehouse looks identical to one that plans.
    """
    units = sum(team.inventory.values())
    if units <= 0:
        return 0.0, 0.0
    unit_cost = (sum(float(params.sku(c)["unit_cost"]) for c in team.active_skus)
                 / max(len(team.active_skus), 1)) * params["cogs_scale"]
    value = units * unit_cost
    holding = value * params["inventory_holding_rate"]

    demand_units = max(ctx["orders"][tid] * params["units_per_order"], 1.0)
    cover_rounds = units / demand_units
    excess = max(0.0, cover_rounds - params["inventory_obsolescence_rounds"])
    ageing = min(value, excess * demand_units * unit_cost) * 0.10
    return holding, ageing


def run(world, params, resolved, ctx) -> None:
    for team in world.teams.values():
        tid = team.team_id
        d = ctx["resolved"][tid]

        gross_revenue = ctx["gross_revenue"][tid]
        aov = ctx["aov"][tid]
        # The prepaid incentive is a discount given to the prepaid share.
        prepaid_disc = gross_revenue * ctx["prepaid_share"][tid] * float(d.get("9.2", 0) or 0)
        gross_revenue -= prepaid_disc

        returns_value = ctx["returned_orders"][tid] * aov
        rto_value = ctx["rto_orders"][tid] * aov
        failed_value = ctx["failed_orders"][tid] * aov
        net_revenue = gross_revenue - returns_value - rto_value - failed_value

        # COGS is charged on units that stayed sold. Units that came back and
        # were resellable return to stock and carry no cost; units that came
        # back and were not are written off.
        cogs_per_order = ctx["cogs"][tid] / max(orders_placed := ctx["orders"][tid], 1.0)
        sold = orders_placed - ctx["returned_orders"][tid] - ctx["rto_orders"][tid] \
            - ctx["failed_orders"][tid]
        scrapped = ctx["returned_orders"][tid] - ctx["returns_recovered"][tid]
        cogs = max(0.0, sold) * cogs_per_order
        write_off = scrapped * cogs_per_order
        gross_profit = net_revenue - cogs - write_off

        orders = orders_placed
        pick_pack = orders * params["fulfil_pick_pack_cost"]
        courier_forward = ctx["courier_cost"][tid]
        # Forward AND reverse on every RTO, plus reverse on every return.
        rto_shipping = (ctx["rto_orders"][tid] + ctx["failed_orders"][tid]) * 2 * (
            courier_forward / max(orders, 1.0)
        )
        return_shipping = ctx["returned_orders"][tid] * (
            courier_forward / max(orders, 1.0)
        )

        gateway_cost = (
            net_revenue * ctx["prepaid_share"][tid] * params["gateway_fee"]
        )
        cod_cost = net_revenue * ctx["cod_share"][tid] * params["cod_handling_fee"]

        marketing = sum(float(d.get(k, 0) or 0) for k in MARKETING_DECISIONS)
        marketing += float(d.get("6.1", 0) or 0)  # CRM is marketing (docs/10)
        affiliate = net_revenue * float(d.get("3.6", 0) or 0)
        commission = 0.0
        if d.get("4.1") and str(d.get("4.1")) != "off":
            commission = net_revenue * 0.35 * params["marketplace_commission"]

        contribution = (
            gross_profit - pick_pack - courier_forward - rto_shipping
            - return_shipping - gateway_cost - cod_cost
            - marketing - affiliate - commission
        )

        holding, ageing = _inventory_costs(team, params, ctx, tid)
        research = float(ctx.get("research_cost", {}).get(tid, 0.0))
        below_line = (
            params["payroll_base"] + ctx["cs_cost"][tid]
            + params["warehouse_fixed_cost"]
            + params["tech_fixed_cost"] + ctx.get("ongoing_tech_cost", {}).get(tid, 0.0)
            + research
            + float(d.get("5.1", 0) or 0) + float(d.get("7.4", 0) or 0)
            + holding + ageing
        )
        ebitda = contribution - below_line
        interest = team.credit_drawn * params["credit_rate_annual"] * (
            params["round_months"] / 12
        )
        net_profit = ebitda - interest

        ctx.setdefault("pnl", {})[tid] = {
            "gross_revenue": gross_revenue,
            "prepaid_discount": prepaid_disc,
            "returns_value": returns_value,
            "rto_value": rto_value,
            "net_revenue": net_revenue,
            "cogs": cogs,
            "gross_profit": gross_profit,
            "fulfilment": pick_pack + courier_forward,
            "rto_cost": rto_shipping,          # its own line, deliberately
            "return_cost": return_shipping + write_off,
            "payment_costs": gateway_cost + cod_cost,
            "marketing": marketing + affiliate,
            "commission": commission,
            "contribution": contribution,
            "below_line": below_line,
            "ebitda": ebitda,
            "interest": interest,
            "net_profit": net_profit,
            "research": research,
            "holding": holding,
            "ageing": ageing,
        }
        ctx.setdefault("gross_margin_pct", {})[tid] = (
            gross_profit / net_revenue if net_revenue > 0 else 0.0
        )
        ctx.setdefault("contribution_margin_pct", {})[tid] = (
            contribution / net_revenue if net_revenue > 0 else 0.0
        )
        ctx.setdefault("net_revenue", {})[tid] = net_revenue
        ctx.setdefault("cac_blended", {})[tid] = (
            marketing / ctx["new_customers"][tid]
            if ctx["new_customers"][tid] > 0 else 0.0
        )
