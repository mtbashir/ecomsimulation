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

import math  # noqa: E402

from ecomsim import bootstrap, engine, params as P  # noqa: E402
from ecomsim.modules import m07_share  # noqa: E402

PARAMS = P.load({"n_teams": 6})
START = bootstrap.new_world(PARAMS, n_teams=6, run_id="order-example", ai_competitors=2)


def month(submissions: dict) -> tuple:
    world = copy.deepcopy(START)
    aov = world.market_avg_aov
    return world, engine.run_round(world, PARAMS, submissions), aov


WEIGHTS = (("price", "w_price"), ("quality", "w_quality"), ("delivery", "w_delivery"),
           ("in stock", "w_availability"), ("brand", "w_brand"), ("range fit", "w_fit"))


def attractiveness(world, ctx, aov: float, tid: str = "team_01") -> list[dict]:
    """M7 for one team, segment by segment, as the engine computes it.

    Recomputed after the month: only M5 moves perception and brand, and it runs
    before M7, so the team's state and ctx hold exactly what M7 read."""
    beta = PARAMS["share_sensitivity"]
    pool = world.category_size / aov
    rows = []
    for seg in PARAMS.segments:
        def u(t):
            return m07_share._utility(world.teams[t], seg, PARAMS, ctx)
        team = world.teams[tid]
        index = max(PARAMS["price_index_floor"],
                    min(PARAMS["price_index_cap"], ctx["price_index"][tid]))
        inputs = {"price": 1 - index, "quality": team.quality_perceived,
                  "delivery": team.delivery_perceived, "in stock": ctx["instock_ratio"][tid],
                  "brand": team.brand_equity, "range fit": ctx["assortment_fit"][tid][seg["code"]]}
        parts = {k: float(seg[w]) * inputs[k] for k, w in WEIGHTS}
        mine = math.exp(beta * u(tid))
        rivals = sum(math.exp(beta * u(t)) for t in world.teams if t != tid)
        ai = sum(math.exp(beta * i["utility"]) for i in world.incumbents)
        share = mine / (mine + rivals + ai)
        rows.append({"segment": seg["name"], "pool": pool * float(seg["share"]),
                     "inputs": inputs, "parts": parts, "penalty": sum(parts.values()) - u(tid),
                     "utility": u(tid), "weight": mine, "rivals": rivals, "ai": ai,
                     "share": share, "won": pool * float(seg["share"]) * share})
    return rows


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
    first = month({})
    show("All default", *first)
    print("\nHow team_01 wins its orders (M7):")
    for r in attractiveness(*first):
        parts = " + ".join(f"{k} {v:.3f}" for k, v in r["parts"].items())
        print(f"  {r['segment']}: {parts} - over-price {r['penalty']:.3f} = U {r['utility']:.3f};"
              f" exp(2U) {r['weight']:.3f} / ({r['weight']:.3f} + rivals {r['rivals']:.3f}"
              f" + AI {r['ai']:.3f}) = {r['share']:.2%} of {r['pool']:,.0f} = {r['won']:,.0f}")
    show("team_01 discounts Serum 30ml 15%",
         *month({"team_01": {"1.1": {"SKU-03": {"discount": 0.15}}}}))
