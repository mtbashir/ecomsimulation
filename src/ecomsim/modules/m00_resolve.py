"""M0 - Resolve decisions.

The engine never reads a decision directly. It reads a resolved value - the
team's input if enabled and unlocked, otherwise the configured default. This
single indirection is what makes presets work (docs/04).

This module also derives the cross-team quantities every later module needs:
price index is relative, so it cannot be computed one team at a time.
"""
from __future__ import annotations

TIER_SCORE = {"economy": 0.38, "standard": 0.62, "premium": 0.88}
PACKAGING_SCORE = {"basic": 0.25, "branded": 0.55, "premium": 0.85}
GATEWAY_SUCCESS = {"A": 0.91, "B": 0.84, "C": 0.96}
RETURN_POLICY_KEY = {
    "free": "policy_mult_free_returns",
    "customer_pays": "policy_mult_customer_pays",
    "restocking": "policy_mult_restocking",
}


DISCRETIONARY = ("3.1", "3.2", "3.3", "3.4", "3.5", "3.7", "3.8", "3.9",
                 "5.1", "6.1", "7.4")
CAPEX = ("11.1", "11.2", "11.3", "11.4", "11.5")


def _administration(team, d) -> None:
    """Halve discretionary spend, block new capex and research.

    Capping at the prior round is no constraint on a team that blew up while
    spending 3x - it just keeps buying growth on the administrator's money.
    """
    if team.in_administration:
        for k in DISCRETIONARY:
            cap = 0.5 * team.last_discretionary.get(k, 0.0)
            d[k] = min(float(d.get(k, 0) or 0), cap)
        for k in CAPEX:
            d[k] = False
        d["12.1"] = []
    team.last_discretionary = {k: float(d.get(k, 0) or 0) for k in DISCRETIONARY}


def run(world, params, resolved, ctx) -> None:
    net_prices: dict[str, float] = {}

    for team in world.teams.values():
        tid = team.team_id
        d = ctx["resolved"][tid]
        _administration(team, d)

        discount = _clamp(float(d.get("2.2", 0) or 0), 0.0, 0.50)
        ctx.setdefault("discount", {})[tid] = discount

        list_price = _basket_list_price(team, params)
        ctx.setdefault("basket_list_price", {})[tid] = list_price
        net_prices[tid] = list_price * (1 - discount)

        ctx.setdefault("quality_tier", {})[tid] = _quality_tier(team, params, d)
        ctx.setdefault("qa_score", {})[tid] = _spend_score(
            float(d.get("7.4", 0) or 0), 250_000
        )
        ctx.setdefault("gateway_success", {})[tid] = GATEWAY_SUCCESS.get(
            str(d.get("9.3", "A")), 0.91
        )
        cod_on = str(d.get("9.1", "on")) != "off"
        ctx.setdefault("cod_enabled", {})[tid] = cod_on
        incentive = float(d.get("9.2", 0) or 0)
        cod_est = max(0.0, (params["cod_share_base"] if cod_on else 0.0) - 2.4 * incentive)
        ctx.setdefault("prepaid_incentive_effect", {})[tid] = incentive * (1 - cod_est)
        ctx.setdefault("packaging", {})[tid] = PACKAGING_SCORE.get(
            str(d.get("8.5", "basic")), 0.25
        )
        ctx.setdefault("return_policy_mult", {})[tid] = params[
            RETURN_POLICY_KEY.get(str(d.get("10.4", "customer_pays")),
                                  "policy_mult_customer_pays")
        ]
        _assortment_fit(team, params, ctx)

    # Price index is relative, so it needs every team's price first. Incumbents
    # sit in the average too - they are part of the market a team is priced against.
    incumbent_price = world.market_avg_price
    all_prices = list(net_prices.values()) + [incumbent_price] * len(world.incumbents)
    market_avg = sum(all_prices) / max(len(all_prices), 1)
    world.market_avg_price = market_avg

    for tid, price in net_prices.items():
        ctx.setdefault("net_unit_price", {})[tid] = price
        ctx.setdefault("price_index", {})[tid] = price / max(market_avg, 1.0)


def _basket_list_price(team, params) -> float:
    """Revenue-weighted average unit list price across the team's active SKUs."""
    skus = [params.sku(c) for c in team.active_skus] or params.skus
    total_w = sum(float(s["revenue_weight"]) for s in skus) or 1.0
    return sum(float(s["list_price"]) * float(s["revenue_weight"]) for s in skus) / total_w


def _quality_tier(team, params, d) -> float:
    """Actual quality is set by what the team sources, not what it says."""
    override = d.get("1.5")
    if isinstance(override, str) and override in TIER_SCORE:
        return TIER_SCORE[override]
    skus = [params.sku(c) for c in team.active_skus] or params.skus
    total_w = sum(float(s["revenue_weight"]) for s in skus) or 1.0
    return sum(
        TIER_SCORE[str(s["tier"])] * float(s["revenue_weight"]) for s in skus
    ) / total_w


def _assortment_fit(team, params, ctx) -> None:
    """How well the active catalogue matches each segment's needs.

    Breadth helps everyone a little; tier alignment is what actually separates
    Premium/Gifting from Value Seekers.
    """
    tid = team.team_id
    breadth = len(team.active_skus) / max(len(params.skus), 1)
    tier = ctx["quality_tier"][tid]
    fits = {}
    for seg in params.segments:
        wtp = float(seg["wtp_index"])
        alignment = 1.0 - abs(tier - _clamp((wtp - 0.6) / 1.1, 0.0, 1.0))
        fits[seg["code"]] = _clamp(0.35 * breadth + 0.65 * alignment, 0.0, 1.0)
    ctx.setdefault("assortment_fit", {})[tid] = fits
    ctx.setdefault("assortment_fit_mean", {})[tid] = sum(fits.values()) / len(fits)


def _spend_score(spend: float, reference: float) -> float:
    """Diminishing-returns score in [0,1] for a discretionary spend line."""
    return min(1.0, (spend / reference) ** 0.5) if spend > 0 else 0.0


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))
