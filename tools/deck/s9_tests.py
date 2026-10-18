"""The simulation test runs quoted in the Session 9 deck (Part 2).

Six identical teams play seven months on every default; from month 8 one team
changes one decision (kept to month 12, or once where it is a one-off), against
the same world where it did not. Events are off, so each line isolates one
decision. New-game rules: full costs, working affiliates, returns to supplier.

    python tools/deck/s9_tests.py
"""
import copy, sys
sys.path.insert(0, "src")

from ecomsim import bootstrap, params as P
from ecomsim.engine import run_round

PARAMS = P.load({"n_teams": 6, "events_enabled": 0})


def opening(months):
    world = bootstrap.new_world(PARAMS, run_id="deck-tests")
    world.rules_from, world.full_costs, world.loans = 1, True, False
    world.affiliates = world.supplier_returns = True
    for _ in range(months):
        run_round(world, PARAMS, {})
    return world


def play(world, plan, months, once=None):
    """`plan` every month; `once` only in the first (a one-off move)."""
    w = copy.deepcopy(world)
    tid = list(w.teams)[0]
    for i in range(months):
        d = dict(plan)
        if i == 0 and once:
            d.update(once(w.teams[tid]))
        run_round(w, PARAMS, {tid: d})
    return w.teams[tid].history


def row(label, h, first, last):
    a, z = h[first], h[last]
    ebitda = sum(x["pnl"]["ebitda"] for x in h[first:last + 1])
    refused = sum(x["pnl"]["rto_cost"] for x in h[first:last + 1])
    stock_units = sum(r["close"] for r in z.get("stock") or [])
    print(f"{label:<34} orders {a['orders']:>6,.0f}  delivered {a['delivery_success']:.1%}  "
          f"refusal cost {refused / 1e6:>5.2f}m  | m12 stock {stock_units:>7,.0f}  "
          f"cover {z['weeks_cover']:>4.1f}wk  cash {z['cash_balance'] / 1e6:>5.2f}m  "
          f"owed {z['credit_drawn'] / 1e6:>5.2f}m  EBITDA {ebitda / 1e6:>6.2f}m")


def half_back(team):
    return {"7.6": {c: u * 0.5 for c, u in team.inventory.items() if u > 1}}


def double_order(team):
    last = (team.history[-1].get("cash_flow") or {}).get("purchases_ordered", 0.0)
    units = sum(r.get("ordered") or 0 for r in team.history[-1].get("stock") or [])
    return {"7.1": max(units, 1.0) * 2}


print("Session 9 - operations open for month 8 (month 8 shown, then month 12; EBITDA months 8-12)")
base = opening(7)
for label, plan, once in [
        ("All default", {}, None),
        ("Supplier A (cheap, slow)", {"7.2": "A"}, None),
        ("Supplier C (dear, fast)", {"7.2": "C"}, None),
        ("Safety stock 1 week", {"7.5": 1}, None),
        ("Safety stock 8 weeks", {"7.5": 8}, None),
        ("All Speed Express", {"8.3": {"speed": 1.0}}, None),
        ("All Value Logistics", {"8.3": {"value": 1.0}}, None),
        ("Cash on delivery off", {"9.1": "off"}, None),
        ("5% off for paying online", {"9.2": 0.05}, None),
        ("10% off for paying online", {"9.2": 0.10}, None),
        ("All orders through 3PL", {"8.2": 1.0}, None),
        ("QA at PKR 250k", {"7.4": 250_000}, None)]:
    row(label, play(base, plan, 5, once), 7, 11)

print("\nOverstocked in month 8 (8 weeks of cover), then from month 9:")
w = opening(7)
over = copy.deepcopy(w)
run_round(over, PARAMS, {list(over.teams)[0]: {"7.5": 8}})
for label, plan, once in [
        ("Keep 8 weeks of cover", {"7.5": 8}, None),
        ("Back to 3 weeks", {"7.5": 3}, None),
        ("Back to 3 weeks + return half", {"7.5": 3}, half_back)]:
    row(label, play(over, plan, 4, once), 8, 11)
