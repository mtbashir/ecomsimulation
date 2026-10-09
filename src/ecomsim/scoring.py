"""End-of-game scorecard (docs/08-scoring.md).

Flow metrics are weighted by round, w[t] = t / sum(1..T), so Round 12 carries
~15% and Round 1 ~1.3%. Stock metrics are read terminally.

Two rule sets (ecomsim.version). Under rules v1 every anchor is
criterion-referenced, market share is the sole relative metric, and decision
quality is held at 5 of 10. Under rules v2 profitability is marked against the
best team in the room and decision quality is earned from decisions taken and
the board memo. Each month carries the rules it ran under, so a game that
switched mid-semester scores its early months exactly as they were published.
"""
from __future__ import annotations

import statistics as st

from .modules.m17_score import anchor, runway_score

# Net revenue runs ~78% of gross once returns, RTO and failed delivery are out
# (docs/13 judgement 1). Growth anchors are quoted on net, so convert once.
_NET_OF_GROSS = 0.78


# The published scorecard: (pillar, measure key, label, points, (zero, fifty,
# hundred) anchors, unit). final_score reads its anchors from here, and the
# briefing page and the handbook render from here, so what students are told
# and what the engine scores cannot drift apart again. A measure whose
# anchors run downwards (zero above hundred) is "lower is better".
SCORECARD = [
    ("Profitability", 25, "Margins over the whole run, weighted by each month's revenue.", [
        ("cm_pre", "Contribution margin before marketing", 12, (0.14, 0.24, 0.32), "pct"),
        ("ebitda", "EBITDA margin", 8, (-0.22, -0.11, -0.02), "pct"),
        ("gm", "Gross margin", 5, (0.30, 0.37, 0.44), "pct")]),
    ("Growth", 20, "How much bigger you finished, and whether you took share doing it.", [
        ("rev_multiple", "Net revenue, last month against first", 8, (0.65, 1.00, 1.35), "x"),
        ("share_pp", "Market share gained, in percentage points", 7, (-2.0, 0.0, 2.5), "pp"),
        ("order_growth", "Orders against a baseline business", 5, (-0.28, -0.06, 0.22), "pct")]),
    ("Customer value", 20, "Whether you built a customer base or rented one.", [
        ("ltv_cac", "Lifetime value against lifetime acquisition cost", 6, (0.8, 1.9, 3.8), "x"),
        ("repeat", "Repeat order share, over all orders", 5, (0.26, 0.355, 0.46), "pct"),
        ("active", "Active customers at the end", 6, (22_000, 30_000, 40_000), "int"),
        ("nps", "NPS at the end", 3, (70, 82, 92), "int")]),
    ("Operational efficiency", 15, "Whether the business delivered what it sold, cheaply.", [
        ("service", "Service level", 2, (0.94, 0.985, 1.00), "pct"),
        ("delivery", "Delivery success", 6, (0.920, 0.940, 0.958), "pct"),
        ("leak", "Refused and returned parcel costs, as a share of revenue", 4,
         (0.055, 0.042, 0.032), "pct"),
        ("turns", "Stock turns a year", 3, (8.0, 13.0, 20.0), "x")]),
    ("Cash & capital", 10, "Whether the business can keep going, and paid its own way.", [
        ("runway", "Runway at the end", 5, None, "band"),
        ("free_cash", "Cash the business generated itself", 3, (-15e6, 0.0, 25e6), "pkr"),
        ("net_margin", "Net profit margin", 2, (-0.30, -0.14, -0.02), "pct")]),
    ("Decision quality", 10, "Judged by your instructor, not the model: your board "
                             "memos and the reasoning behind your decisions.", []),
]
_ANCHORS = {key: (pts, a) for _, _, _, ms in SCORECARD for key, _, pts, a, _ in ms}


def _fmt(v: float, unit: str) -> str:
    if unit == "pct":
        return f"{v * 100:.1f}%".replace(".0%", "%")
    if unit == "pp":
        return f"{v:+g} points" if v else "no change"
    if unit == "x":
        return f"{v:g}" + ("×" if v < 5 else "")
    if unit == "pkr":
        return "PKR 0" if not v else f"PKR {v / 1e6:+g}m"
    return f"{v:,.0f}"


RUNWAY_BAND = ("under 1.5 months scores nothing; 1.5–3 months 30%; "
               "3–9 months full marks; 9–16 months 60%; more than 16 months 30%. "
               "Too much idle cash is marked down like too little.")


RELATIVE = ("Against the best team in the room: the best earns full marks, every "
            "other team the same share as its margin is of the best's (a negative "
            "margin earns nothing)")


def published(rules_from: int = 1) -> list[tuple]:
    """(pillar, points, summary, [(measure, points, where the marks are)]) for pages.

    `rules_from` is the month this game's rules v2 start: profitability and
    decision quality are described as they are marked from then, with the
    earlier months' rule alongside when the game switched mid-run.
    """
    early = f"months 1–{rules_from - 1}" if rules_from > 1 else ""
    out = []
    for name, pts, summary, measures in SCORECARD:
        rows = []
        for key, label, mpts, a, unit in measures:
            if a is None:
                where = RUNWAY_BAND
            else:
                z, f, h = (_fmt(x, unit) for x in a)
                where = f"{z} scores nothing, {f} half, {h} full"
                if a[2] < a[0]:
                    where += " (lower is better)"
            if name == "Profitability":
                fixed = where
                where = RELATIVE + (f". For {early}: {fixed}" if early else "")
            rows.append((label, mpts, where))
        if name == "Profitability":
            summary = ("Margins over the run, weighted by each month's revenue, marked "
                       "against the best team in the room.")
        if name == "Decision quality":
            summary = ("Earned every month from the decisions you take and your board memo"
                       + (f"; {early} are held at 5 of 10 for every team." if early else "."))
            rows = [("Decisions taken", 8,
                     f"Full marks for taking {int(KEEP_SHARE * 100)}% of the decisions open "
                     "that month - changing a lever, or ticking Keep to confirm last month's "
                     "setting - and in proportion below"),
                    ("Board memo", 2,
                     "2 points when your memo says what you decided this month and why; "
                     "0 if there is none, or if your instructor judges it does not match "
                     "your decisions")]
        out.append((name, pts, summary, rows))
    return out


def _mark(key: str, value: float) -> float:
    """Points earned on one published measure."""
    pts, a = _ANCHORS[key]
    return pts * anchor(value, *a)


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


PROFIT = (("cm_pre", "contribution_pre_marketing_pct"), ("ebitda", "ebitda_margin_pct"),
          ("gm", "gross_margin_pct"))
KEEP_SHARE = 0.75        # rules v2: full decision marks at three-quarters of those open


def _v2(record: dict) -> bool:
    """Whether a month ran on rules v2. A month recorded earlier did not."""
    return int(record.get("rules", 1) or 1) >= 2


def _profit_fixed(months: list[dict]) -> float:
    """Rules v1: margins against the published thresholds."""
    return sum(_mark(key, _margin(months, field)) for key, field in PROFIT) / 100


def _profit_relative(team, all_teams: dict, idx: list[int]) -> float:
    """Rules v2: each margin as a share of the best team's over the same months.

    The best team earns the measure's full points and every other team the
    same fraction of them as its margin is of the best: 10% against a best of
    40% earns a quarter. A negative margin earns nothing. If no team made a
    positive margin there is no best to measure against, and the measure falls
    back to its published thresholds.
    """
    def margins(t):
        months = [t.history[i] for i in idx if i < len(t.history)]
        return {key: _margin(months, field) for key, field in PROFIT} if months else None

    own = margins(team)
    peers = [m for m in (margins(t) for t in (all_teams or {}).values()) if m] + [own]
    total = 0.0
    for key, _ in PROFIT:
        pts = _ANCHORS[key][0]
        best = max(m[key] for m in peers)
        if best > 0:
            total += pts * max(0.0, own[key]) / best
        else:
            total += _mark(key, own[key]) / 100
    return total


def _decision_quality(team, record: dict, rejected: set) -> float:
    """Decision quality for one month, out of 10.

    Rules v1 held it at 5 for everyone. Rules v2: 8 for decisions taken - full
    marks at three-quarters of the decisions open that month, in proportion
    below - and 2 for a board memo, unless the instructor judged it does not
    match the month's decisions.
    """
    if not _v2(record):
        return 5.0
    d = record.get("decisions") or {}
    open_ = float(d.get("open") or 0)
    taken = min(1.0, float(d.get("taken") or 0) / (KEEP_SHARE * open_)) if open_ else 0.0
    key = (getattr(team, "team_id", ""), int(record.get("round", 0)))
    memo = 2.0 if d.get("memo") and key not in rejected else 0.0
    return 8.0 * taken + memo


def final_score(team, params, all_teams: dict, memo_rejected: set | None = None) -> dict:
    h = team.history
    T = len(h)
    w = _weights(T)
    first, last = h[0], h[-1]
    insolvent = any(x["insolvent"] for x in h)

    # P1 Profitability (25) - all flow. Each month is marked on the rules it
    # ran under: months before rules v2 against the fixed thresholds, months
    # from v2 against the best team; the two parts weighted as the months are.
    new = [i for i, x in enumerate(h) if _v2(x)]
    old = [i for i in range(T) if i not in new]
    if not new:
        p1 = _profit_fixed(h)
    else:
        w_old = sum(w[i] for i in old)
        p1 = ((w_old * _profit_fixed([h[i] for i in old]) if old else 0.0)
              + (1 - w_old) * _profit_relative(team, all_teams, new))

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
    p2 = (_mark("rev_multiple", rev_multiple)
          + _mark("share_pp", share_change_pp)
          + _mark("order_growth", order_growth)) / 100

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
    p3 = (_mark("ltv_cac", ltv_cac)
          + _mark("repeat", _share(h, "repeat_order_share", "orders"))
          + _mark("active", last["active_customers"])
          + _mark("nps", last["nps"])) / 100

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
    p4 = (_mark("service", _flow(h, "service_level", w))
          + _mark("delivery", _flow(h, "delivery_success", w))
          + _mark("leak", _flow(h, leak, w))
          + _mark("turns", turns)) / 100

    # P5 Cash & capital (10), as docs/08 specifies it: runway read terminally,
    # not averaged across the year, and the cash the business itself threw off
    # scored separately from the profit it booked. Averaging the runway band
    # let a team that spent the year comfortable and ended on fumes score the
    # same as one that ended able to keep going.
    liquidity = _runway_band(last["runway_rounds"])
    free_cash = ((last["cash_balance"] - params["starting_cash"])
                 - (last["credit_drawn"] - first["credit_drawn"]))
    ccc = _flow(h, lambda x: x["pnl"]["net_profit"] / max(x["revenue_net"], 1.0), w)
    p5 = 0.0 if insolvent else (_ANCHORS["runway"][0] * liquidity
                                + _mark("free_cash", free_cash)
                                + _mark("net_margin", ccc)) / 100

    # P6 Decision quality (10), month by month on the rules each month ran
    # under, weighted as the other flow measures are.
    rejected = memo_rejected or set()
    p6 = sum(w[i] * _decision_quality(team, x, rejected) for i, x in enumerate(h))

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
