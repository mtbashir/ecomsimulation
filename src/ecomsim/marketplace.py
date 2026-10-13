"""The marketplace (decision 4.1): selling on Daraz as well as on your own site.

docs/07 specifies it; this is that design, in the engine's own terms.

- Reach. The marketplace has its own shoppers, who would never find your site.
  Each month a pool of them (`mp_pool_sessions`) is shared between the sellers
  listed there, by a rank score built from price and rating. Your teams are not
  the only sellers: the rest of the marketplace counts as `mp_rival_weight`
  average sellers, so listing earns a slice, and a smaller one the more of the
  class lists too. Marketplace shoppers arrive ready to buy (`mp_cr_mult`).
- Cannibalisation. Some of your own buyers find you there instead
  (`mp_cannibalisation`): the same order, now paying commission.
- Money. Commission (`marketplace_commission`) on every marketplace order, the
  marketplace collects the payment (no gateway or COD fee of your own), and it
  pays out `mp_payout_days` later.
- Customers. A buyer won on the marketplace belongs to it: such a cohort
  churns faster and buys less often (the `marketplace_ads` row of channels.csv),
  your CRM cannot reach it, and its repeat orders come back through the
  marketplace, paying commission again - only while you are listed.

Nothing here runs for a team that is not listed, and a cohort acquired on the
marketplace is the only state it leaves behind.
"""
from __future__ import annotations

DECISION = "4.1"
CHANNEL = "marketplace_ads"          # the cohort profile of a marketplace buyer


def listed(d) -> bool:
    """Whether this month's decisions put the team on the marketplace."""
    value = (d or {}).get(DECISION)
    return bool(value) and str(value) != "off"


def is_marketplace(cohort) -> bool:
    return getattr(cohort, "channel", "") == CHANNEL


def rank_score(team, ctx) -> float:
    """How well a listing ranks: half price, half rating.

    Price is the team's price index against the market (1.0 = average); a
    cheaper listing ranks higher. Rating is last month's store rating.
    Sponsored listings (3.7, which the scripted strategies use) lift it by up
    to half again; teams have no such lever, so for them this term is zero.
    """
    price_index = ctx.get("price_index", {}).get(team.team_id, 1.0)
    price = max(0.0, min(1.0, 1.6 - price_index))           # 1.0 at index 0.6 or lower
    rating = max(0.0, min(1.0, (team.rating - 1.0) / 4.0))  # 1.0 at five stars
    ads = float(ctx["resolved"][team.team_id].get("3.7", 0) or 0)
    return (0.5 * price + 0.5 * rating) * (1 + 0.5 * min(1.0, ads / 400_000))


def share_sessions(world, params, ctx) -> None:
    """Split the marketplace's shoppers between the listed teams (M6)."""
    scores = {tid: rank_score(team, ctx) for tid, team in world.teams.items()
              if listed(ctx["resolved"][tid])}
    if not scores:
        return
    typical = rank_score_typical()
    denominator = sum(scores.values()) + params["mp_rival_weight"] * typical
    for tid, score in scores.items():
        ctx.setdefault("mp_sessions", {})[tid] = (
            params["mp_pool_sessions"] * score / max(denominator, 1e-9))
        ctx.setdefault("mp_rank", {})[tid] = score


def rank_score_typical() -> float:
    """An average seller: priced at the market, rated 4.1."""
    return 0.5 * 0.6 + 0.5 * (4.1 - 1.0) / 4.0


def repeat_demand(team, params) -> float:
    """Orders the team's marketplace buyers place this month, through the
    marketplace. Your CRM does not reach them, so there is no retention lift."""
    return sum(c.active * c.freq * params["cohort_freq_scale"]
               for c in team.cohorts if is_marketplace(c))


def take_orders(world, params, ctx, orders: dict[str, float]) -> None:
    """Add marketplace orders to each listed team's own-site orders (M8).

    New marketplace demand is the team's share of shoppers at its conversion
    rate, plus its marketplace buyers coming back; it sells from the same
    stock, after the own site. A share of own-site orders moves to the
    marketplace (cannibalisation): no extra orders, but commission on them.
    """
    for tid, team in world.teams.items():
        if not listed(ctx["resolved"][tid]):
            continue
        cr = ctx["conversion_rate"][tid]
        fresh = ctx.get("mp_sessions", {}).get(tid, 0.0) * cr * params["mp_cr_mult"]
        back = repeat_demand(team, params)
        own = orders[tid]
        room = max(0.0, ctx.get("stock_capacity", {}).get(tid, float("inf")) - own)
        served = min(fresh + back, room)
        new = served * (fresh / (fresh + back)) if fresh + back > 0 else 0.0
        orders[tid] = own + served
        moved = params["mp_cannibalisation"] * own
        ctx.setdefault("mp_orders", {})[tid] = served + moved
        ctx.setdefault("mp_new_orders", {})[tid] = new
        ctx.setdefault("mp_repeat_orders", {})[tid] = served - new
        ctx.setdefault("mp_demand", {})[tid] = fresh + back


def order_share(ctx, tid: str) -> float:
    """Marketplace orders as a share of all the team's orders this month."""
    total = ctx.get("orders", {}).get(tid, 0.0)
    mp = ctx.get("mp_orders", {}).get(tid, 0.0)
    return min(1.0, mp / total) if total > 0 else 0.0
