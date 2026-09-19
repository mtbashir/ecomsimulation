"""M7 - Demand & share allocation.

Logit attractiveness over hidden segment weights. share_sensitivity above 4.5
produces winner-take-all: a small Round 2 lead compounds to total share by
Round 6 and the rest of the class disengages (docs/04).
"""
from __future__ import annotations

import math


def run(world, params, resolved, ctx) -> None:
    beta = params["share_sensitivity"]

    # N<=3 is a tug-of-war under a plain logit; damp it and add incumbents.
    if len(world.teams) <= 3:
        beta = min(beta, 1.4)
    elif len(world.teams) >= 12:
        beta = max(beta, 2.6)

    category_orders = world.category_size / max(world.market_avg_aov, 1.0)

    utilities: dict[str, dict[str, float]] = {}
    for team in world.teams.values():
        utilities[team.team_id] = {
            seg["code"]: _utility(team, seg, params, ctx) for seg in params.segments
        }
    for inc in world.incumbents:
        utilities[inc["id"]] = {
            seg["code"]: inc["utility"] for seg in params.segments
        }

    potential: dict[str, float] = {tid: 0.0 for tid in utilities}
    for seg in params.segments:
        code, seg_share = seg["code"], float(seg["share"])
        exps = {tid: math.exp(beta * u[code]) for tid, u in utilities.items()}
        total = sum(exps.values()) or 1.0
        seg_orders = category_orders * seg_share
        for tid, e in exps.items():
            potential[tid] += seg_orders * (e / total)

    ctx["potential"] = potential


def _utility(team, seg, params, ctx) -> float:
    price_index = ctx.get("price_index", {}).get(team.team_id, 1.0)
    price_index = max(params["price_index_floor"],
                      min(params["price_index_cap"], price_index))
    instock = ctx.get("instock_ratio", {}).get(team.team_id, 0.95)
    fit = ctx.get("assortment_fit", {}).get(team.team_id, {}).get(seg["code"], 0.5)

    return (
        float(seg["w_price"]) * (1 - price_index)
        + float(seg["w_quality"]) * team.quality_perceived
        + float(seg["w_delivery"]) * team.delivery_perceived
        + float(seg["w_availability"]) * instock
        + float(seg["w_brand"]) * team.brand_equity
        + float(seg["w_fit"]) * fit
    )
