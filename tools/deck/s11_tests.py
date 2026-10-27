"""The simulation test runs quoted in the Session 11 deck (Part 2).

The same world as Sessions 9 and 10: six identical teams on every default,
events off, PKR 12M of starting capital (what the Fall-2026 game began on),
new-game rules for full costs, working affiliates and returns. One team commits
to one AI build - with the operating change the build is meant to allow -
against the same world where it did not, and both play to month 12.

Each build is committed twice: in month 3, when the builds opened in the
Fall-2026 game, and in month 10, the decision this session takes. Whether a
build works is a roll fixed by the game, so each one is also tried in twenty
games to show how often it works and what it is worth on average.

    python tools/deck/s11_tests.py
"""
import copy, statistics as st, sys
sys.path.insert(0, "src")

from ecomsim import bootstrap, params as P, scoring
from ecomsim.engine import run_round
from ecomsim.modules.m04_capability import PROJECTS

PARAMS = P.load({"n_teams": 6, "events_enabled": 0, "starting_cash": 12_000_000})
TID = "team_01"


def opening(months, run_id="deck-tests"):
    world = bootstrap.new_world(PARAMS, run_id=run_id)
    world.rules_from, world.full_costs, world.loans = 1, True, False
    world.affiliates = world.supplier_returns = True
    for _ in range(months):
        run_round(world, PARAMS, {})
    return world


def play(world, build, plan, to=12):
    """Commit `build` in the next month, keep `plan` every month to `to`."""
    w = copy.deepcopy(world)
    first = True
    while w.round < to:
        d = dict(plan)
        if first and build:
            d[PROJECTS[build]["decision"]] = True
        run_round(w, PARAMS, {TID: d})
        first = False
    return w


def before_dq(w):
    """The final score less decision quality: the instructor's pillar, and a
    test team earns it for the decisions it submits while its twin submits none."""
    s = scoring.final_score(w.teams[TID], PARAMS, w.teams)
    return s["total"] - s["p6"]


def summary(w, start):
    h = w.teams[TID].history
    months = h[start - 1:]
    return {"net": sum(x["revenue_net"] for x in months),
            "ebitda": sum(x["ebitda"] for x in months),
            "cash": h[-1]["cash_balance"] - h[-1]["credit_drawn"],
            "score": before_dq(w),
            "live": None, "h": h}


BUILDS = [  # (build, label, the operating change it allows)
    ("recsys", "Recommendations (11.1)", {}),
    ("forecasting", "AI forecasting (11.2)", {}),
    ("forecasting", "AI forecasting + 2 weeks' safety stock", {"7.5": 2}),
    ("ai_cs", "AI customer service (11.4)", {}),
    ("ai_cs", "AI customer service + 2 agents", {"10.1": 2}),
    ("ai_creative", "AI creative (11.5)", {}),
    ("ai_creative", "AI creative + PKR 290k production", {"3.8": 290_000}),
]
NONE = [("", "No build, 2 weeks' safety stock", {"7.5": 2}),
        ("", "No build, 2 agents", {"10.1": 2}),
        ("", "No build, PKR 290k production", {"3.8": 290_000})]


def compare(start, run_id="deck-tests"):
    before = opening(start - 1, run_id)
    base = summary(play(before, None, {}), start)
    rows = []
    for build, label, plan in BUILDS + NONE:
        w = play(before, build or None, plan)
        s = summary(w, start)
        s["live"] = build in w.teams[TID].capabilities if build else None
        rows.append((build, label, s))
    return base, rows


for start in (3, 10):
    base, rows = compare(start)
    print(f"\nCommitted in month {start}, months {start}-12 against a team on every default"
          f" (default: net revenue {base['net'] / 1e6:.2f}m, EBITDA {base['ebitda'] / 1e6:+.2f}m,"
          f" cash less loan {base['cash'] / 1e6:.2f}m, score before decision quality {base['score']:.1f})")
    print(f"  {'':42} worked  net rev   EBITDA   cash    score")
    for build, label, s in rows:
        ok = "-" if s["live"] is None else ("yes" if s["live"] else "FAILED")
        print(f"  {label:42} {ok:6} {(s['net'] - base['net']) / 1e6:+6.2f}m {(s['ebitda'] - base['ebitda']) / 1e6:+6.2f}m"
              f" {(s['cash'] - base['cash']) / 1e6:+6.2f}m {s['score'] - base['score']:+6.1f}")

# What each build does once live: month 12 of the month-3 commitment.
base, rows = compare(3)
b12 = base["h"][-1]
print("\nOnce live, month 12 (committed in month 3):")
print(f"  default: basket {b12['aov_net']:,.0f}, forecast error {st.mean(x['forecast_error'] for x in base['h'][2:]):.1%},"
      f" lost to stock-outs {sum(x['lost_to_stockout'] for x in base['h'][2:]):,.0f}, cover {b12['weeks_cover']:.1f}wk,"
      f" backlog {b12['cs_backlog']:,.0f}, rating {b12['rating']:.2f}, NPS {b12['nps']:.0f},"
      f" creative {b12['creative_quality']:.3f}, tech {b12['pnl']['technology']:,.0f}")
for build, label, s in rows:
    z, h = s["h"][-1], s["h"][2:]
    print(f"  {label:42} basket {z['aov_net']:,.0f}, forecast error {st.mean(x['forecast_error'] for x in h):.1%},"
          f" lost {sum(x['lost_to_stockout'] for x in h):,.0f}, cover {z['weeks_cover']:.1f}wk,"
          f" stock {z['inventory_units']:,.0f}u, backlog {z['cs_backlog']:,.0f}, rating {z['rating']:.2f},"
          f" NPS {z['nps']:.0f}, creative {z['creative_quality']:.3f}, tech {z['pnl']['technology']:,.0f}")

# Chance: the same build, committed in month 3 and in month 10, in twenty games.
def chance(start, build, plan, games=20):
    worked, d_ebitda, d_cash, d_score = 0, [], [], []
    for g in range(games):
        before = opening(start - 1, f"ai-{g}")
        base = summary(play(before, None, {}), start)
        w = play(before, build, plan)
        s = summary(w, start)
        worked += build in w.teams[TID].capabilities
        d_ebitda.append(s["ebitda"] - base["ebitda"])
        d_cash.append(s["cash"] - base["cash"])
        d_score.append(s["score"] - base["score"])
    return worked, st.mean(d_ebitda), st.mean(d_cash), st.mean(d_score)


for start in (3, 10):
    print(f"\nCommitted in month {start}, in twenty games: how often it worked, and its average effect to month 12")
    for build, label, plan in BUILDS:
        worked, e, c, s = chance(start, build, plan)
        print(f"  {label:42} worked {worked:2}/20 (p {PROJECTS[build]['p']:.0%})  EBITDA {e / 1e6:+.2f}m"
              f"  cash {c / 1e6:+.2f}m  score {s:+.2f}")
