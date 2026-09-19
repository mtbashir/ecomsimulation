"""End-of-game scorecard (docs/08-scoring.md).

Flow metrics are weighted by round, w[t] = t / sum(1..T), so Round 12 carries
~15% and Round 1 ~1.3%. Stock metrics are read terminally. Every anchor is
criterion-referenced; market share is the sole relative metric.

P6 (decision quality) is memo- and prediction-based and cannot be scored in a
scripted harness; it is held at 50/100 for every team here.
"""
from __future__ import annotations

import statistics as st

from .modules.m17_score import anchor, runway_score

# Net revenue runs ~78% of gross once returns, RTO and failed delivery are out
# (docs/13 judgement 1). Growth anchors are quoted on net, so convert once.
_NET_OF_GROSS = 0.78


def _weights(n: int) -> list[float]:
    total = n * (n + 1) / 2
    return [(t + 1) / total for t in range(n)]


def _flow(history: list[dict], key, w: list[float]) -> float:
    return sum(w[i] * (key(h) if callable(key) else h[key]) for i, h in enumerate(history))


def final_score(team, params, all_teams: dict) -> dict:
    h = team.history
    T = len(h)
    w = _weights(T)
    first, last = h[0], h[-1]
    insolvent = any(x["insolvent"] for x in h)

    # P1 Profitability (25) - all flow
    p1 = (12 * anchor(_flow(h, "contribution_margin_pct", w), 0.0, 0.09, 0.18)
          + 8 * anchor(_flow(h, "ebitda_margin_pct", w), -0.22, -0.14, -0.05)
          + 5 * anchor(_flow(h, "gross_margin_pct", w), 0.25, 0.38, 0.50)) / 100

    # P2 Growth (20)
    baseline_net = params["baseline_team_revenue"] * _NET_OF_GROSS
    rev_multiple = last["revenue_net"] / baseline_net
    share_change_pp = (last["market_share"] - first["market_share"]) * 100
    baseline_orders = params["baseline_team_revenue"] / params["aov_base"]
    order_growth = _flow(h, lambda x: x["orders"] / baseline_orders - 1, w)
    # 12 monthly rounds of a mature business: 1.9x was a 3-year anchor.
    p2 = (8 * anchor(rev_multiple, 0.85, 1.30, 2.20)
          + 7 * anchor(share_change_pp, -2.0, 0.5, 4.0)
          + 5 * anchor(order_growth, -0.05, 0.10, 0.45)) / 100

    # P3 Customer value (20)
    total_marketing = sum(x["pnl"]["marketing"] for x in h)
    total_new = sum(x["orders"] * (1 - x["repeat_order_share"]) for x in h)
    cac_lifetime = total_marketing / max(total_new, 1.0)
    ltv_cac = last["ltv"] / max(cac_lifetime, 1.0)

    p3 = (8 * anchor(ltv_cac, 1.0, 2.5, 5.0)
          + 5 * anchor(_flow(h, "repeat_order_share", w), 0.10, 0.22, 0.40)
          + 4 * anchor(last["active_customers"], 20_000, 45_000, 90_000)
          + 3 * anchor(last["nps"], 0, 24, 55)) / 100

    # P4 Operational efficiency (15)
    leak = lambda x: (x["pnl"]["rto_cost"] + x["pnl"]["return_cost"]) / max(x["revenue_net"], 1.0)
    periods = 12 / params["round_months"]
    avg_units = st.mean([x["inventory_units"] for x in h]) or 1.0
    unit_cost = _unit_cost(team, params) * params["cogs_scale"]
    cogs_flow = st.mean([x["pnl"]["cogs"] for x in h])
    turns = cogs_flow * periods / max(avg_units * unit_cost, 1.0)
    p4 = (4 * anchor(_flow(h, "instock_rate", w), 0.955, 0.985, 0.998)
          + 4 * anchor(_flow(h, "delivery_success", w), 0.936, 0.950, 0.964)
          + 4 * anchor(_flow(h, leak, w), 0.115, 0.085, 0.055)
          + 3 * anchor(turns, 4.0, 7.5, 12.0)) / 100

    # P5 Cash & capital (10)
    cum_fcf = last["cash_balance"] - params["starting_cash"]
    ccc = _flow(h, lambda x: x["pnl"]["net_profit"] / max(x["revenue_net"], 1.0), w)
    p5 = 0.0 if insolvent else (5 * _runway_band(last["runway_rounds"])
                                + 3 * anchor(cum_fcf, -24e6, -15e6, -5e6)
                                + 2 * anchor(ccc, -0.30, -0.14, -0.02)) / 100

    # P6 Decision quality (10) - not scorable in a scripted harness
    p6 = 10 * 0.5

    total = p1 + p2 + p3 + p4 + p5 + p6
    return {"total": total, "p1": p1, "p2": p2, "p3": p3, "p4": p4, "p5": p5,
            "p6": p6, "insolvent": insolvent,
            "first_insolvent_round": next((x["round"] for x in h if x["insolvent"]), None)}


def _runway_band(runway: float) -> float:
    """Banded, not monotonic - the shape from docs/08, re-based to the burn.

    A team ending with 10+ rounds of runway in a category still growing has
    under-invested just as surely as one about to run out.
    """
    if runway < 1.0:
        return 0.0
    if runway < 2.5:
        return 30.0
    if runway <= 6.0:
        return 100.0
    if runway <= 10.0:
        return 60.0
    return 30.0


def _unit_cost(team, params) -> float:
    skus = [params.sku(c) for c in team.active_skus] or params.skus
    return sum(float(s["unit_cost"]) for s in skus) / len(skus)
