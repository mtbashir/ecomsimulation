"""The worked example in docs/00-game-world.md: how orders reach a team and what
goes in them. Month 1 of a six-team going-concern game on default decisions,
two AI competitors; run twice - all default, then team_01 discounting Serum 30ml
(SKU-03) 15%. Deterministic: the same numbers every run.

    python tools/order_example.py
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ecomsim import bootstrap, engine, params as P  # noqa: E402

PARAMS = P.load({"n_teams": 6})
START = bootstrap.new_world(PARAMS, n_teams=6, run_id="order-example", ai_competitors=2)


def month(submissions: dict) -> tuple:
    world = copy.deepcopy(START)
    aov = world.market_avg_aov
    return world, engine.run_round(world, PARAMS, submissions), aov


def show(label: str, world, ctx, aov: float, tid: str = "team_01") -> None:
    pool = world.category_size / aov
    potential, repeat = ctx["potential"], ctx["repeat_demand"]
    contested = {t: potential[t] - repeat.get(t, 0.0) for t in potential}
    ai = sum(v for t, v in contested.items() if t not in world.teams) / sum(contested.values())
    print(f"\n{label}\nMarket: PKR {world.category_size / 1e6:.1f}M / PKR {aov:,.0f} = {pool:,.0f} orders"
          f" (AI competitors win {ai:.1%})")
    for seg in PARAMS.segments:
        won = contested[tid] * ctx["segment_mix"][tid][seg["code"]]
        print(f"  {seg['name']:18} {pool * float(seg['share']):7,.0f} in the pool, {won:5,.0f} won")
    print(f"{tid}: {contested[tid]:,.0f} won + {repeat[tid]:,.0f} repeat = {potential[tid]:,.0f} demand;"
          f" traffic {ctx['traffic_capacity'][tid]:,.0f}, stock {ctx['stock_capacity'][tid]:,.0f}"
          f" -> {ctx['orders'][tid]:,.0f} orders x {PARAMS['units_per_order']} units")
    sales = ctx["sku_sales"][tid]
    units = sum(v["want"] for v in sales.values())
    for code, v in sorted(sales.items(), key=lambda kv: -kv[1]["want"]):
        print(f"  {PARAMS.sku(code)['name']:20} weight {v['base']:.3f}  customer pull {v['seg_pull']:.2f}"
              f"  price pull {v['price_pull']:.2f}  share {v['want'] / units:.3f}  units {v['want']:5,.0f}")


if __name__ == "__main__":
    show("All default", *month({}))
    show("team_01 discounts Serum 30ml 15%",
         *month({"team_01": {"1.1": {"SKU-03": {"discount": 0.15}}}}))
