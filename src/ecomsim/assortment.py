"""Range changes (decision 1.3): adding a product to the range, or dropping one.

Founding sets the range. From month 3, in a game that allows it
(`world.range_changes`), a team may change it. An added product is ordered when
the change is made - a month of its expected sales, on the supplier's normal
terms - and goes on sale when that order lands. A dropped product stops selling
at once; its stock, and any still on its way, goes back to the supplier for a
refund less a restocking fee. The range stays within the founding bounds.

M0 applies the change at the start of the month, before prices, range breadth
and demand are read; M3 places the order for added products and sends dropped
stock back once the month's deliveries have landed.
"""
from __future__ import annotations

DECISION = "1.3"
MIN_RANGE, MAX_RANGE = 12, 18


def changes(value) -> tuple[list[str], list[str]]:
    """(add, drop) from the decision's value."""
    if not isinstance(value, dict):
        return [], []
    return ([str(c) for c in value.get("add") or []],
            [str(c) for c in value.get("drop") or []])


def size(team) -> int:
    """Products on sale plus those ordered and not yet on sale."""
    return len(team.active_skus) + len(getattr(team, "pending_lines", None) or {})


def start_of_month(team, world, params, ctx, d) -> None:
    """Put landed products on sale, then apply this month's changes."""
    if not getattr(world, "range_changes", False):
        return
    pending = dict(getattr(team, "pending_lines", None) or {})
    for code, month in sorted(pending.items(), key=lambda kv: (kv[1], kv[0])):
        if month <= world.round and code not in team.active_skus:
            team.active_skus.append(code)
    team.pending_lines = {c: m for c, m in pending.items() if m > world.round}

    add, drop = changes(d.get(DECISION))
    known = {s["code"] for s in params.skus}
    n = size(team)
    for code in drop:
        if code in team.active_skus and n > MIN_RANGE:
            team.active_skus.remove(code)
            n -= 1
    added = []
    for code in add:
        if (code in known and code not in team.active_skus
                and code not in team.pending_lines and n < MAX_RANGE):
            _list(team, params, code)
            added.append(code)
            n += 1
    ctx.setdefault("range_adds", {})[team.team_id] = added


def _list(team, params, code: str) -> None:
    """Price and source a new product the way set-up would have.

    A going-concern team set neither, so the catalogue price at its position
    and its blended cost apply, as they do for every product it sells.
    """
    f = getattr(team, "founding", None)
    if f is None:
        return
    from .founding import cost_multiplier, reference_price, sourcing_of
    sku = params.sku(code)
    team.sku_prices.setdefault(code, reference_price(sku, f.tier))
    if team.sku_sourcing:
        how = sourcing_of(f, code)
        team.sku_sourcing.setdefault(code, how)
        team.sku_cost_index.setdefault(code, cost_multiplier(how, f.tier))


def expected_units(team, params) -> float:
    """A month of units at the team's current pace."""
    if team.history and team.history[-1].get("units_sold"):
        return float(team.history[-1]["units_sold"])
    return (params["baseline_team_revenue"] / params["aov_base"]
            * params["units_per_order"])


def listing_units(team, params, added: list[str]) -> dict[str, float]:
    """Each added product's first order: its catalogue share of a month."""
    codes = list(team.active_skus) + list(team.pending_lines) + list(added)
    total = sum(float(params.sku(c)["revenue_weight"]) for c in codes) or 1.0
    month = expected_units(team, params)
    return {c: month * float(params.sku(c)["revenue_weight"]) / total for c in added}
