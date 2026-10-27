"""The simulation test runs quoted in the Session 10 deck (Part 2).

The same world as Session 9's tests: six identical teams, seven months on
every default, events off, PKR 12M of starting capital (what the Fall-2026 game
began on), new-game rules for full costs, working affiliates and returns.
Month 8 is read for a team on every default, then for one team changing one
thing, against the same world where it did not.

    python tools/deck/s10_tests.py
"""
import copy, sys
sys.path.insert(0, "src")

from ecomsim import bootstrap, params as P
from ecomsim.engine import run_round

PARAMS = P.load({"n_teams": 6, "events_enabled": 0, "starting_cash": 12_000_000})


def opening(months):
    world = bootstrap.new_world(PARAMS, run_id="deck-tests")
    world.rules_from, world.full_costs, world.loans = 1, True, False
    world.affiliates = world.supplier_returns = True
    for _ in range(months):
        run_round(world, PARAMS, {})
    return world


def month8(before=None, plan=None):
    """team_01's month-8 record: `before` is its month-7 decision, `plan` its month-8 one."""
    w = copy.deepcopy(SIX)
    tid = list(w.teams)[0]
    run_round(w, PARAMS, {tid: before} if before else {})
    run_round(w, PARAMS, {tid: plan} if plan else {})
    return w.teams[tid].history[-1]


def funnel(h):
    gross = h["pnl"]["gross_revenue"]
    return {"sessions": h["sessions"], "cr": h["conversion_rate"], "orders": h["orders"],
            "aov": gross / h["orders"], "gross": gross, "kept": h["revenue_net"] / gross,
            "net": h["revenue_net"]}


SIX = opening(6)
base = month8()
f0 = funnel(base)

print("Month 8, a team on every default")
print(f"  sessions {f0['sessions']:,.0f} (paid {base['sessions_paid']:,.0f}, organic {base['sessions_organic']:,.0f},"
      f" returning {base['sessions_returning']:,.0f})")
print(f"  x conversion {f0['cr']:.2%} = orders {f0['orders']:,.0f} x average order PKR {f0['aov']:,.0f}"
      f" = gross PKR {f0['gross'] / 1e6:.2f}m x kept {f0['kept']:.1%} = net revenue PKR {f0['net'] / 1e6:.2f}m")
print(f"  new customers {base['new_customers']:,.0f}, repeat share {base['repeat_order_share']:.1%},"
      f" CAC PKR {base['cac_blended']:,.0f}, LTV PKR {base['ltv']:,.0f}, LTV:CAC {base['ltv_cac_ratio']:.2f}")
print(f"  reported ROAS {base['roas_reported']:.2f} against true {base['roas_true']:.2f};"
      f" binding: {base['binding_constraint']}")

pnl, n = base["pnl"], base["orders"]
lines = [("Net revenue", pnl["net_revenue"]),
         ("Product cost", -(pnl["net_revenue"] - pnl["gross_profit"])),
         ("Cost to serve", -(pnl["gross_profit"] - base["contribution_pre_marketing_pct"] * pnl["net_revenue"])),
         ("Marketing", -(base["contribution_pre_marketing_pct"] - base["contribution_margin_pct"]) * pnl["net_revenue"]),
         ("Overheads", -(base["contribution_margin_pct"] * pnl["net_revenue"] - pnl["ebitda"]))]
print("  per order:", " | ".join(f"{k} {v / n:,.0f}" for k, v in lines), f"| EBITDA {pnl['ebitda'] / n:,.0f}")
failed = pnl["gross_revenue"] - pnl["prepaid_discount"] - pnl["returns_value"] - pnl["rto_value"] - pnl["net_revenue"]
print(f"  gross {pnl['gross_revenue'] / n:,.0f} - discount {pnl['prepaid_discount'] / n:,.0f}"
      f" - returns {pnl['returns_value'] / n:,.0f} - refused {pnl['rto_value'] / n:,.0f}"
      f" - failed deliveries {failed / n:,.0f} -> net {pnl['net_revenue'] / n:,.0f}")

from ecomsim.decisions import REGISTRY
half = {c: REGISTRY[c].default_when_disabled * 0.5 for c in ("3.1", "3.2", "3.4")}
dearer = {"1.1": {s["code"]: {"price": round(float(s["list_price"]) * 1.15)} for s in PARAMS.skus}}

tests = [("Ad budgets halved", None, half),
         ("10% off everything", None, {"2.2": 0.10}),
         ("Prices 15% higher", None, dearer),
         ("No stock bought in month 7", {"7.1": 0}, None)]
print("\nMonth 8, one change against the default (revenue change split sessions -> conversion -> basket -> kept)")
print(f"  {'':28} sessions  conv   orders  basket  kept   net rev  binding        lost")
row = lambda label, h, f: print(
    f"  {label:28} {f['sessions']:8,.0f} {f['cr']:6.2%} {f['orders']:6,.0f} {f['aov']:7,.0f} {f['kept']:5.1%}"
    f" {f['net'] / 1e6:6.2f}m  {h['binding_constraint']:14} {h['lost_to_stockout']:5,.0f}")
row("All default", base, f0)
for label, before, plan in tests:
    h = month8(before, plan)
    f = funnel(h)
    row(label, h, f)
    s = (f["sessions"] - f0["sessions"]) * f0["cr"] * f0["aov"] * f0["kept"]
    c = f["sessions"] * (f["cr"] - f0["cr"]) * f0["aov"] * f0["kept"]
    a = f["sessions"] * f["cr"] * (f["aov"] - f0["aov"]) * f0["kept"]
    k = f["sessions"] * f["cr"] * f["aov"] * (f["kept"] - f0["kept"])
    print(f"  {'':28} change {f['net'] / 1e6 - f0['net'] / 1e6:+.2f}m = sessions {s / 1e6:+.2f}"
          f" + conversion {c / 1e6:+.2f} + basket {a / 1e6:+.2f} + kept {k / 1e6:+.2f};"
          f" EBITDA {h['ebitda'] / 1e6:+.2f}m vs {base['ebitda'] / 1e6:+.2f}m")
