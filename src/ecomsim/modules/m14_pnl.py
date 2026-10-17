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


# Positioning (1.5) as founding.TIERS names the same tiers.
CLAIMED_TIER = {"economy": "value", "standard": "mainstream", "premium": "premium"}


def quality_cost_ratio(team, params, d) -> float:
    """What sourcing to the quality tier the team claims (1.5) costs, against
    the tier its products are actually sourced at: 1.0 on automatic.

    Positioning lifts quality - rating, returns - so in a full-cost game it
    also moves cost, as the decision says: premium costs more to source,
    economy less.
    """
    from ..founding import TIERS
    claimed = CLAIMED_TIER.get(str(d.get("1.5") or ""))
    if claimed is None:
        return 1.0
    f = getattr(team, "founding", None)
    base = getattr(f, "tier", None) if f else None
    if base not in TIERS:
        # A going concern: the tier its product mix is sourced at.
        from .m00_resolve import TIER_SCORE, _quality_tier
        q = _quality_tier(team, params, {})
        base = CLAIMED_TIER[min(TIER_SCORE, key=lambda k: abs(TIER_SCORE[k] - q))]
    return TIERS[claimed][1] / TIERS[base][1]


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
        # Full-cost games (world.full_costs) charge what three decisions say
        # they cost: sourcing to the claimed quality tier, packaging above a
        # plain box, and orders handled by the 3PL over your own warehouse.
        quality_premium = packaging = tpl = 0.0
        if getattr(world, "full_costs", False):
            quality_premium = cogs * (quality_cost_ratio(team, params, d) - 1)
            pack = str(d.get("8.5") or "basic")
            per_pack = params[f"packaging_cost_{pack}"] if pack in ("branded", "premium") else 0.0
            packaging = ctx["orders"][tid] * per_pack
            tpl = (ctx["orders"][tid] * min(1.0, max(0.0, float(d.get("8.2", 0) or 0)))
                   * params["tpl_cost_per_order"])
        gross_profit = net_revenue - cogs - write_off - quality_premium

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

        # Marketplace orders are paid to the marketplace, which pays the seller
        # net of commission: no gateway or COD fee of the team's own on them.
        from .. import marketplace
        mp_share = marketplace.order_share(ctx, tid)
        own_revenue = net_revenue * (1 - mp_share)
        gateway_cost = (
            own_revenue * ctx["prepaid_share"][tid] * params["gateway_fee"]
        )
        cod_cost = own_revenue * ctx["cod_share"][tid] * params["cod_handling_fee"]

        marketing = sum(float(d.get(k, 0) or 0) for k in MARKETING_DECISIONS)
        marketing += float(d.get("6.1", 0) or 0)  # CRM is marketing (docs/10)
        affiliate = net_revenue * float(d.get("3.6", 0) or 0)
        commission = net_revenue * mp_share * params["marketplace_commission"]

        contribution = (
            gross_profit - pick_pack - packaging - tpl - courier_forward - rto_shipping
            - return_shipping - gateway_cost - cod_cost
            - marketing - affiliate - commission
        )

        holding, ageing = _inventory_costs(team, params, ctx, tid)
        restocking = float(ctx.get("restocking_fee", {}).get(tid, 0.0))
        research = float(ctx.get("research_cost", {}).get(tid, 0.0))
        below_line = (
            params["payroll_base"] + ctx["cs_cost"][tid]
            + params["warehouse_fixed_cost"]
            + params["tech_fixed_cost"] + ctx.get("ongoing_tech_cost", {}).get(tid, 0.0)
            + research
            + float(d.get("5.1", 0) or 0) + float(d.get("7.4", 0) or 0)
            + holding + ageing + restocking
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
            "fulfilment": pick_pack + packaging + tpl + courier_forward,
            "quality_premium": quality_premium,
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
            "restocking": restocking,
            # The lines behind each subtotal, so a workbook can show the sum.
            "cogs_sold": cogs,
            "write_off": write_off,
            "pick_pack": pick_pack,
            "packaging": packaging,
            "tpl": tpl,
            "courier": courier_forward,
            "return_shipping": return_shipping,
            "gateway": gateway_cost,
            "cod_fee": cod_cost,
            "marketing_spend": marketing,
            "affiliate": affiliate,
            "payroll": params["payroll_base"],
            "service_team": ctx["cs_cost"][tid],
            "warehouse": params["warehouse_fixed_cost"],
            "technology": params["tech_fixed_cost"]
                          + ctx.get("ongoing_tech_cost", {}).get(tid, 0.0),
            "website": float(d.get("5.1", 0) or 0),
            "quality_assurance": float(d.get("7.4", 0) or 0),
        }
        ctx.setdefault("gross_margin_pct", {})[tid] = (
            gross_profit / net_revenue if net_revenue > 0 else 0.0
        )
        ctx.setdefault("contribution_margin_pct", {})[tid] = (
            contribution / net_revenue if net_revenue > 0 else 0.0
        )
        # The same margin one line higher, before a rupee of marketing. This is
        # the economics of fulfilling an order - product, shipping, payment,
        # returns, commission - and nothing a team spends to win the order.
        # docs/08 asks the three scored margins to sit at different levels of
        # the P&L so that no single lever moves all three; with marketing
        # inside contribution, cutting marketing moved contribution and EBITDA
        # together, which is 20 of profitability's 25 points on one lever.
        ctx.setdefault("contribution_pre_marketing_pct", {})[tid] = (
            (contribution + marketing + affiliate) / net_revenue
            if net_revenue > 0 else 0.0
        )
        ctx.setdefault("net_revenue", {})[tid] = net_revenue
        ctx.setdefault("cac_blended", {})[tid] = (
            marketing / ctx["new_customers"][tid]
            if ctx["new_customers"][tid] > 0 else 0.0
        )
