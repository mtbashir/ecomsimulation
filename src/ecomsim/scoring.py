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


def _margin(history: list[dict], key: str) -> float:
    """Aggregate margin over the period, not the mean of monthly percentages.

    A margin percentage is a ratio, and ratios do not average. Reading the
    plain mean let a team stop marketing in Month 10, watch orders halve, take
    a fat margin on what was left, and score above a team that earned a steady
    margin on twice the volume - and the round weights made those three months
    the heaviest of the twelve. Weighting each month by its own net revenue is
    what a P&L does. A margin is an accounting fact about the period, so unlike
    the operating metrics it carries no round tilt: the year earned what it
    earned.
    """
    total = sum(h["revenue_net"] for h in history) or 1.0
    return sum(h["revenue_net"] * h[key] for h in history) / total


def _share(history: list[dict], key: str, base: str) -> float:
    """A share of something, taken over the totals rather than averaged.

    Repeat share rises by itself when a team stops acquiring, so a mean of the
    monthly figures paid a team for giving up. Over the totals it is what it
    claims to be: repeat orders as a share of all the orders placed.
    """
    total = sum(h[base] for h in history) or 1.0
    return sum(h[base] * h[key] for h in history) / total


def final_score(team, params, all_teams: dict) -> dict:
    h = team.history
    T = len(h)
    w = _weights(T)
    first, last = h[0], h[-1]
    insolvent = any(x["insolvent"] for x in h)

    # P1 Profitability (25) - all flow
    p1 = (12 * anchor(_margin(h, "contribution_pre_marketing_pct"), 0.14, 0.24, 0.32)
          + 8 * anchor(_margin(h, "ebitda_margin_pct"), -0.22, -0.11, -0.02)
          + 5 * anchor(_margin(h, "gross_margin_pct"), 0.30, 0.37, 0.44)) / 100

    # P2 Growth (20)
    # Revenue multiple is where the business ended against where it started,
    # as docs/08 specifies: a team that spent nine months building and three
    # months harvesting ends smaller than it began, and this is what says so.
    # Sandbagging used to exploit exactly that reading; it no longer can,
    # because brand equity decays while a team coasts and cannot be bought
    # back inside a quarter - the defence belongs in the engine, not here.
    rev_multiple = last["revenue_net"] / max(first["revenue_net"], 1.0)
    share_change_pp = (_flow(h, "market_share", w) - first["market_share"]) * 100
    baseline_orders = params["baseline_team_revenue"] / params["aov_base"]
    order_growth = _flow(h, lambda x: x["orders"] / baseline_orders - 1, w)
    # 12 monthly rounds of a mature business: 1.9x was a 3-year anchor.
    p2 = (8 * anchor(rev_multiple, 0.65, 1.00, 1.35)
          + 7 * anchor(share_change_pp, -2.0, 0.0, 2.5)
          + 5 * anchor(order_growth, -0.28, -0.06, 0.22)) / 100

    # P3 Customer value (20)
    # LTV is a lifetime figure, so the CAC it is divided by is the lifetime one:
    # every rupee of marketing over every customer it brought in.
    total_marketing = sum(x["pnl"]["marketing"] for x in h)
    total_new = sum(x["orders"] * (1 - x["repeat_order_share"]) for x in h)
    cac_lifetime = total_marketing / max(total_new, 1.0)
    ltv_cac = last["ltv"] / max(cac_lifetime, 1.0)

    # The pillar is customer value, and the value of a customer base is how big
    # and how loyal it is - not how efficient the marketing that built it was.
    # With eight points on the ratio and four on the base, a team could stop
    # acquiring, watch the base shrink, and score better on customer value for
    # having stopped spending. Six and six says what the pillar means.
    p3 = (6 * anchor(ltv_cac, 0.8, 1.9, 3.8)
          + 5 * anchor(_share(h, "repeat_order_share", "orders"), 0.26, 0.355, 0.46)
          + 6 * anchor(last["active_customers"], 22_000, 30_000, 40_000)
          + 3 * anchor(last["nps"], 70, 82, 92)) / 100

    # P4 Operational efficiency (15)
    leak = lambda x: (x["pnl"]["rto_cost"] + x["pnl"]["return_cost"]) / max(x["revenue_net"], 1.0)
    periods = 12 / params["round_months"]
    avg_units = st.mean([x["inventory_units"] for x in h]) or 1.0
    unit_cost = _unit_cost(team, params) * params["cogs_scale"]
    cogs_flow = st.mean([x["pnl"]["cogs"] for x in h])
    turns = cogs_flow * periods / max(avg_units * unit_cost, 1.0)
    # Service level is the one operating metric this business cannot fail at:
    # three weeks of cover absorbs a 16% forecast miss, so every team served
    # essentially all of what it could sell. Four points for an outcome nobody
    # can move is four points of scorecard that says nothing, so it drops to
    # two on a demanding anchor and the weight goes to delivery success - which
    # in a 62%-COD market is the operating number a team actually lives on.
    p4 = (2 * anchor(_flow(h, "service_level", w), 0.94, 0.985, 1.00)
          + 6 * anchor(_flow(h, "delivery_success", w), 0.920, 0.940, 0.958)
          + 4 * anchor(_flow(h, leak, w), 0.055, 0.042, 0.032)
          + 3 * anchor(turns, 8.0, 13.0, 20.0)) / 100

    # P5 Cash & capital (10), as docs/08 specifies it: runway read terminally,
    # not averaged across the year, and the cash the business itself threw off
    # scored separately from the profit it booked. Averaging the runway band
    # let a team that spent the year comfortable and ended on fumes score the
    # same as one that ended able to keep going.
    liquidity = _runway_band(last["runway_rounds"])
    free_cash = ((last["cash_balance"] - params["starting_cash"])
                 - (last["credit_drawn"] - first["credit_drawn"]))
    ccc = _flow(h, lambda x: x["pnl"]["net_profit"] / max(x["revenue_net"], 1.0), w)
    p5 = 0.0 if insolvent else (5 * liquidity
                                + 3 * anchor(free_cash, -15e6, 0.0, 25e6)
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
    if runway < 1.5:
        return 0.0
    if runway < 3.0:
        return 30.0
    if runway <= 9.0:
        return 100.0
    if runway <= 16.0:
        return 60.0
    return 30.0


def _unit_cost(team, params) -> float:
    skus = [params.sku(c) for c in team.active_skus] or params.skus
    return sum(float(s["unit_cost"]) for s in skus) / len(skus)
