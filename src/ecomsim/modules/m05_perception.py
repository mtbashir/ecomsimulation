"""M5 - Perception & brand.

Marketing moves perception. Sourcing and operations move reality. The gap
between them is the most valuable number in the sim, and it sits behind a
PKR 300,000 study (docs/03 mechanism 2).
"""
from __future__ import annotations


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def run(world, params, resolved, ctx) -> None:
    for team in world.teams.values():
        _brand_equity(team, params, resolved)
        _creative_quality(team, params, resolved)
        _actual_scores(team, params, resolved, ctx)
        _perceived_scores(team, params, resolved)
        _gap(team, params, world.round, ctx)


def _brand_equity(team, params, resolved) -> None:
    """Distributed lag peaking at t-1, giving the 3-round effect without a hard delay."""
    hist = team.brand_spend_history
    spend = float(resolved.get("3.9", 0) or 0)
    hist.append(spend)
    weighted = (
        0.2 * hist[-1]
        + 0.5 * (hist[-2] if len(hist) > 1 else 0.0)
        + 0.3 * (hist[-3] if len(hist) > 2 else 0.0)
    )
    decay = params["brand_decay"] * team.pending_gap_penalties.get("brand_decay_mult", 1.0) \
        if isinstance(team.pending_gap_penalties.get("brand_decay_mult"), float) else params["brand_decay"]
    gain = params["brand_alpha"] * weighted / params["brand_ref_spend"]
    team.brand_equity = _clamp(team.brand_equity * (1 - decay) + gain)


def _creative_quality(team, params, resolved) -> None:
    spend = float(resolved.get("3.8", 0) or 0)
    gain = params["creative_kappa"] * (spend / params["creative_ref_spend"]) ** 0.5
    cq = team.creative_quality * (1 - params["creative_decay"]) + gain

    # AI creative raises the floor and caps the ceiling: cheap and good enough,
    # never excellent (docs/01 G11).
    if "ai_creative" in team.capabilities and spend < params["creative_ref_spend"]:
        cq = min(cq, params["ai_creative_ceiling"])
    team.creative_quality = _clamp(cq)


def _actual_scores(team, params, resolved, ctx) -> None:
    tier = ctx.get("quality_tier", {}).get(team.team_id, 0.60)
    qa = ctx.get("qa_score", {}).get(team.team_id, 0.55)
    supplier_q = ctx.get("supplier_quality", {}).get(team.team_id, 0.92)
    team.quality_actual = _clamp(0.55 * tier + 0.25 * qa + 0.20 * supplier_q)

    # Value and delivery actuals are written by M9 and M10 of the PRIOR round;
    # on round 1 they hold their seeded values.
    ctx.setdefault("actual_scores", {})[team.team_id] = {
        "quality": team.quality_actual,
        "value": team.value_actual,
        "delivery": team.delivery_actual,
    }


def _perceived_scores(team, params, resolved) -> None:
    lam = params["perception_convergence"]
    rating_norm = _clamp((team.rating - 2.5) / 2.5)

    pq_target = (
        0.30 * team.creative_quality
        + 0.25 * team.brand_equity
        + 0.15 * 0.5      # influencer tier, wired when 3.5 lands
        + 0.10 * 0.5      # packaging tier, wired when 8.5 lands
        + 0.20 * rating_norm
    )
    team.quality_perceived += lam * (pq_target - team.quality_perceived)

    discount = float(resolved.get("2.2", 0) or 0)
    pv_target = _clamp(0.35 + 1.1 * discount)
    team.value_perceived += lam * (pv_target - team.value_perceived)

    pdr_target = _clamp(0.30 * team.brand_equity + 0.45 + 0.25 * rating_norm)
    team.delivery_perceived += lam * (pdr_target - team.delivery_perceived)


def _gap(team, params, round_, ctx) -> None:
    """Both failure modes are punished: over-promising and under-marketing."""
    gaps = [
        team.quality_perceived - team.quality_actual,
        team.value_perceived - team.value_actual,
        team.delivery_perceived - team.delivery_actual,
    ]
    over, under = max(gaps), min(gaps)
    thr = params["gap_threshold"]
    pend = team.pending_gap_penalties

    if over > thr:
        excess = over - thr
        pend[round_ + 1] = {
            "rating": params["gap_rating_coef"] * excess,
            "return_mult": 1 + params["gap_return_coef"] * excess,
        }
        pend[round_ + 2] = {"repeat_mult": 1 - params["gap_repeat_coef"] * excess}
        pend[round_ + 3] = {"brand_decay_mult": 1 + params["gap_brand_decay_coef"] * excess}

    if under < -thr:
        # Immediate, not lagged: you are paying for capability nobody knows about.
        ctx.setdefault("traffic_mult", {})[team.team_id] = \
            1 + params["undermkt_traffic_coef"] * under
        ctx.setdefault("cac_mult", {})[team.team_id] = \
            1 - params["undermkt_cac_coef"] * under

    ctx.setdefault("perception_gap", {})[team.team_id] = over
