"""The simulation test runs quoted in the Session 12 deck (Part 2).

The same world as Sessions 9 to 11: six identical teams on every default,
events off, PKR 12M of starting capital (what the Fall-2026 game began on),
new-game rules for full costs, working affiliates and returns. Ten months on
every default, then one team changes course for months 11 and 12 - the last
two decisions of the game - against the same world where it did not.

Scores are shown before decision quality: that pillar is the instructor's, and
a test team earns it for the decisions it submits while its twin submits none.

    python tools/deck/s12_tests.py
"""
import copy, sys
sys.path.insert(0, "src")

from ecomsim import bootstrap, params as P, scoring
from ecomsim.decisions import REGISTRY
from ecomsim.engine import run_round

PARAMS = P.load({"n_teams": 6, "events_enabled": 0, "starting_cash": 12_000_000})
TID = "team_01"
PILLARS = [("p1", "Profitability", 25), ("p2", "Growth", 20), ("p3", "Customer value", 20),
           ("p4", "Operations", 15), ("p5", "Cash", 10)]


def opening(months):
    world = bootstrap.new_world(PARAMS, run_id="deck-tests")
    world.rules_from, world.full_costs, world.loans = 1, True, False
    world.affiliates = world.supplier_returns = True
    for _ in range(months):
        run_round(world, PARAMS, {})
    return world


def finish(world, plan):
    w = copy.deepcopy(world)
    while w.round < 12:
        run_round(w, PARAMS, {TID: dict(plan)} if plan else {})
    return w


def score(w):
    return scoring.final_score(w.teams[TID], PARAMS, w.teams)


weights = scoring._weights(12)
print("Round weights over twelve months:", " ".join(f"m{i + 1} {x:.1%}" for i, x in enumerate(weights)))
print(f"  months 10-12 carry {sum(weights[9:]):.0%}, months 11-12 {sum(weights[10:]):.0%},"
      f" months 1-6 {sum(weights[:6]):.0%}")

ads = {c: 0 for c in ("3.1", "3.2", "3.4", "3.8", "3.9", "6.1")}
double = {c: REGISTRY[c].default_when_disabled * 2 for c in ("3.1", "3.2", "3.4")}
TESTS = [("All default", {}),
         ("Stop all marketing", ads),
         ("20% off everything", {"2.2": 0.20}),
         ("Buy no more stock", {"7.1": 0}),
         ("Double the ad budgets", double),
         ("Prices 10% higher", {"1.1": {s["code"]: {"price": round(float(s["list_price"]) * 1.10)}
                                        for s in PARAMS.skus}})]

ten = opening(10)
base_w = finish(ten, {})
base = score(base_w)
print("\nFinal score, a team on every default, before decision quality:",
      f"{base['total'] - base['p6']:.1f} of 90 ->",
      ", ".join(f"{name} {base[k]:.1f}/{pts}" for k, name, pts in PILLARS))

parts = scoring.breakdown(base_w.teams[TID], PARAMS, base_w.teams)
print("  measure by measure:", "; ".join(
    f"{k} {v['points']:.1f}/{v['max']:g}" + (f" ({v['value']:,.3g})" if v["value"] is not None else "")
    for k, v in parts.items()))

print("\nMonths 11 and 12 changed, against the same team on every default")
print(f"  {'':24} m12 revenue  m11-12 EBITDA  m12 cash  active  score   " + "  ".join(n[:6] for _, n, _ in PILLARS))
for label, plan in TESTS:
    w = finish(ten, plan)
    s, h = score(w), w.teams[TID].history
    print(f"  {label:24} {h[-1]['revenue_net'] / 1e6:8.2f}m {sum(x['ebitda'] for x in h[10:]) / 1e6:+10.2f}m"
          f" {(h[-1]['cash_balance'] - h[-1]['credit_drawn']) / 1e6:8.2f}m {h[-1]['active_customers']:7,.0f}"
          f" {s['total'] - s['p6']:6.1f} " + "  ".join(f"{s[k] - base[k]:+6.2f}" for k, _, _ in PILLARS)
          + f"  stock {h[-1]['inventory_units']:,.0f}u")
