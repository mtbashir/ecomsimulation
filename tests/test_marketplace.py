"""Selling on the marketplace (4.1): reach, commission, payout and whose customer it is."""
import sys
sys.path.insert(0, "src")

import pytest

from ecomsim import bootstrap, marketplace, params as P
from ecomsim.engine import run_round
from ecomsim.web import db, service

PARAMS = P.load({"n_teams": 4, "events_enabled": 0})


def _play(plans_from_5: dict, months=7):
    world = bootstrap.new_world(PARAMS, run_id="mp")
    ids = list(world.teams)
    for m in range(1, months + 1):
        run_round(world, PARAMS, {ids[i]: v for i, v in plans_from_5.items()} if m >= 5 else {})
    return world, ids


def test_listing_brings_orders_from_the_marketplaces_shoppers():
    off, ids = _play({})
    on, _ = _play({0: {"4.1": "on"}})
    a, b = off.teams[ids[0]].history[-1], on.teams[ids[0]].history[-1]
    assert b["orders"] > a["orders"] * 1.15, "shoppers who would never find the site"
    mp = b["marketplace"]
    assert mp["sessions"] > 0 and 0.15 < mp["share"] < 0.45
    assert "marketplace" not in a


def test_commission_is_charged_on_marketplace_orders_only():
    on, ids = _play({0: {"4.1": "on"}})
    h = on.teams[ids[0]].history[-1]
    assert h["pnl"]["commission"] == pytest.approx(
        h["revenue_net"] * h["marketplace"]["share"] * PARAMS["marketplace_commission"])
    assert all(on.teams[t].history[-1]["pnl"]["commission"] == 0 for t in ids[1:])


def test_the_more_sellers_list_the_smaller_each_slice():
    alone, ids = _play({0: {"4.1": "on"}})
    crowd, _ = _play({i: {"4.1": "on"} for i in range(4)})
    assert (crowd.teams[ids[0]].history[-1]["marketplace"]["orders"]
            < alone.teams[ids[0]].history[-1]["marketplace"]["orders"])


def test_a_cheaper_listing_ranks_higher():
    world, ids = _play({0: {"4.1": "on"}, 1: {"4.1": "on", "2.2": 0.10}}, months=5)
    a, b = (world.teams[ids[i]].history[-1]["marketplace"]["rank"] for i in (0, 1))
    assert b > a


def test_marketplace_buyers_belong_to_the_marketplace():
    world, ids = _play({0: {"4.1": "on"}})
    team = world.teams[ids[0]]
    bought = [c for c in team.cohorts if marketplace.is_marketplace(c)]
    assert bought, "a cohort won on the marketplace"
    own = [c for c in team.cohorts if not marketplace.is_marketplace(c)]
    assert min(c.churn_base for c in bought) > min(c.churn_base for c in own)
    # Off the marketplace, they stop buying from you.
    run_round(world, PARAMS, {ids[0]: {"4.1": "off"}})
    assert "marketplace" not in team.history[-1]
    assert team.history[-1]["pnl"]["commission"] == 0


def test_the_marketplace_pays_out_later():
    on, ids = _play({0: {"4.1": "on"}})
    cf = on.teams[ids[0]].history[-1]["cash_flow"]
    assert cf["sales_marketplace"] > 0
    assert on.teams[ids[0]].receivables, "part of the marketplace's money is still to come"


def test_listing_while_discounting_hands_over_the_margin():
    listed, ids = _play({0: {"4.1": "on", "2.2": 0.15}})
    plain, _ = _play({0: {"2.2": 0.15}})
    a = listed.teams[ids[0]].history[-1]["pnl"]["contribution"]
    b = plain.teams[ids[0]].history[-1]["pnl"]["contribution"]
    assert a < b


def test_not_listed_runs_exactly_as_before():
    one, ids = _play({})
    two, _ = _play({})
    for t in ids:
        assert one.teams[t].history[-1]["orders"] == pytest.approx(two.teams[t].history[-1]["orders"])
        assert one.teams[t].history[-1]["pnl"]["commission"] == 0


def test_it_opens_in_month_five():
    world = bootstrap.new_world(PARAMS, run_id="early")
    tid = next(iter(world.teams))
    for _ in range(4):
        run_round(world, PARAMS, {tid: {"4.1": "on"}})
    assert all("marketplace" not in h for h in world.teams[tid].history)


def test_a_closed_window_switches_a_saved_decision_off(tmp_path):
    path = tmp_path / "g.db"
    db.init(path, "G", 2, start_mode="going_concern")
    con = db.connect(path)
    for m in range(1, 5):
        db.set_game(con, open_round=m)
        service.process_round(con)
    db.set_game(con, open_round=5)
    db.submit(con, 5, "team_01", {"4.1": "on"}, "t")
    db.set_window(con, "4.1", 5, False)
    assert "4.1" not in [s.code for s in service.form_decisions(con, 5)]
    service.process_round(con)
    h = db.load_world(con).teams["team_01"].history[-1]
    assert "marketplace" not in h and h["pnl"]["commission"] == 0
