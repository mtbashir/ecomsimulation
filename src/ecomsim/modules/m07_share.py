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
    # Who the contested demand came from, not just how much of it there was.
    # A customer won from Quality Loyalists repeats half again as often as one
    # won from Deal Hunters, and M12 cannot know that unless M7 says so.
    by_segment: dict[str, dict[str, float]] = {tid: {} for tid in utilities}
    for seg in params.segments:
        code, seg_share = seg["code"], float(seg["share"])
        exps = {tid: math.exp(beta * u[code]) * _team_focus(world, tid, seg, params, ctx)
                for tid, u in utilities.items()}
        total = sum(exps.values()) or 1.0
        seg_orders = category_orders * seg_share
        for tid, e in exps.items():
            won = seg_orders * (e / total)
            potential[tid] += won
            by_segment[tid][code] = won

    for tid, won in by_segment.items():
        drawn = sum(won.values()) or 1.0
        ctx.setdefault("segment_mix", {})[tid] = {
            code: value / drawn for code, value in won.items()}

    # Repeat demand sits on top of the contested pool.
    for team in world.teams.values():
        repeat = _repeat_demand(team, params, ctx)
        potential[team.team_id] += repeat
        ctx.setdefault("repeat_demand", {})[team.team_id] = repeat

    ctx["potential"] = potential


def _team_focus(world, tid: str, seg, params, ctx) -> float:
    """Incumbents have no founding round, so they carry no focus."""
    team = world.teams.get(tid)
    return _focus_weight(team, seg, params, ctx) if team is not None else 1.0


def _repeat_demand(team, params, ctx) -> float:
    """Orders the installed base will place, from the cohort ledger."""
    uplift = 1 + 0.45 * ctx.get("retention_effect", {}).get(team.team_id, 0.0)
    return sum(
        c.active * c.freq * params["cohort_freq_scale"] * uplift
        for c in team.cohorts
    )


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


def _focus_weight(team, seg, params, ctx) -> float:
    """What the team said it was going after, in Round 0 (D0.3).

    Focus is not extra merit, so it does not belong in the utility - a team
    does not become a better proposition by announcing a target. It is where
    the business points itself: who the creative talks to, which keywords it
    buys, what the shelf looks like. So it multiplies the draw from a segment
    rather than the attractiveness within it, and its size does not depend on
    how sharp the share model happens to be tuned.

    Inside a chosen segment the tilt is scaled by how well the business
    actually fits it, so declaring Premium/Gifting while pricing at value tier
    turns the focus against you. Outside the chosen segments it is always a
    cost: aiming at two groups means showing up less for the other three.

    A going-concern game has no founding record, so there is no focus and
    nothing here changes.
    """
    chosen = list(getattr(getattr(team, "founding", None),
                          "segment_priority", None) or [])
    if not chosen:
        return 1.0

    coef = params["segment_focus_coef"]
    if seg["code"] in chosen:
        fit = ctx.get("assortment_fit", {}).get(
            team.team_id, {}).get(seg["code"], 0.5)
        # fit runs 0..1 and sits at 0.5 for an indifferent match, so a
        # well-fitted focus earns the tilt and a contradictory one pays it.
        return max(0.1, 1 + coef * (2 * fit - 1))
    return max(0.1, 1 - coef * params["segment_focus_spill"])
