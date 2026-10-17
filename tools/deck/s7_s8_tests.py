"""The simulation test runs quoted in the Session 7 and 8 decks (Part 2).

Six identical teams play the opening months on every default; then one team
changes one decision and keeps it, against the same world where it did not.
Everything else stays on its default, so each line isolates one decision.

    python tools/deck/s7_s8_tests.py
"""
import copy, sys
sys.path.insert(0, "src")

from ecomsim import bootstrap, params as P
from ecomsim.engine import run_round

PARAMS = P.load({"n_teams": 6, "events_enabled": 0})


def opening(months):
    world = bootstrap.new_world(PARAMS, run_id="deck-tests")
    world.rules_from, world.full_costs, world.loans = 1, True, False
    for _ in range(months):
        run_round(world, PARAMS, {})
    return world


def play(world, plan, months):
    w = copy.deepcopy(world)
    tid = list(w.teams)[0]
    for _ in range(months):
        run_round(w, PARAMS, {tid: dict(plan)})
    return w.teams[tid].history


def row(label, h, first, last):
    a, z = h[first], h[last]
    mk = a["pnl"]["marketing"]
    new = max(a["new_customers"], 1)
    contrib = sum(x["pnl"]["contribution"] for x in h[first:last + 1])
    print(f"{label:<34} orders {a['orders']:>6,.0f}  new {a['new_customers']:>6,.0f}  "
          f"CAC {mk / new:>6,.0f}  repeat {a['repeat_order_share']:.1%}  "
          f"| end: active {z['active_customers']:>7,.0f}  repeat {z['repeat_order_share']:.1%}  "
          f"NPS {z['nps']:>4.0f}  organic {z['sessions_organic']:>7,.0f}  "
          f"contrib {contrib / 1e3:>7,.0f}k")


print("Session 7 - marketing opens for month 6 (first month shown, then month 12; contribution months 6-12)")
base = opening(5)
for label, plan in [
        ("All default", {}),
        ("Meta +50% (702k)", {"3.1": 702_000}),
        ("Google moved to TikTok", {"3.2": 0, "3.4": 402_000}),
        ("Brand-building stopped", {"3.9": 0}),
        ("Brand-building doubled", {"3.9": 534_000}),
        ("Creative stopped", {"3.8": 0}),
        ("30% site-wide discount", {"2.2": 0.30})]:
    row(label, play(base, plan, 7), 5, 11)

print("\nSession 8 - retention opens for month 7 (first month shown, then month 12; contribution months 7-12)")
base = opening(6)
for label, plan in [
        ("All default (CRM 60k, 4 agents)", {}),
        ("CRM 400k", {"6.1": 400_000}),
        ("CRM stopped", {"6.1": 0}),
        ("Service team cut to 2", {"10.1": 2}),
        ("Service team 6", {"10.1": 6}),
        ("Free returns", {"10.4": "free"}),
        ("Restocking fee", {"10.4": "restocking"})]:
    row(label, play(base, plan, 6), 6, 11)
