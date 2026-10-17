"""Working affiliates: commission (3.6) that brings partner sales.

It used to be charged on all revenue and bring nothing. In a game on working
affiliates partners bring visitors, their customers churn like affiliate
buyers, and commission is paid only on what they track. A game already
trading switches from a month the instructor picks.
"""
import copy, sys
sys.path.insert(0, "src")

import pytest

from ecomsim import bootstrap, params as P
from ecomsim.engine import run_round
from ecomsim.web import db, service

PARAMS = P.load({"n_teams": 3, "events_enabled": 0})


def _world(on: bool):
    world = bootstrap.new_world(PARAMS, run_id="aff")
    world.rules_from, world.affiliates = 1, on
    run_round(world, PARAMS, {})
    return world


def _month(world, rate):
    w = copy.deepcopy(world)
    tid = list(w.teams)[0]
    run_round(w, PARAMS, {tid: {"3.6": rate}})
    return w.teams[tid]


def test_without_the_switch_it_is_the_old_cost_on_all_revenue():
    assert getattr(bootstrap.new_world(PARAMS), "affiliates", False) is False
    world = _world(False)
    base, aff = _month(world, 0.0).history[-1], _month(world, 0.10).history[-1]
    assert aff["orders"] == pytest.approx(base["orders"])
    assert aff["pnl"]["affiliate"] == pytest.approx(aff["revenue_net"] * 0.10, rel=1e-6)


def test_partners_bring_orders_and_are_paid_only_on_what_they_track():
    world = _world(True)
    base, team = _month(world, 0.0), _month(world, 0.10)
    h = team.history[-1]
    assert h["orders"] > base.history[-1]["orders"]
    assert 0 < h["pnl"]["affiliate"] < h["revenue_net"] * 0.10 * 0.5
    assert h["sessions_organic"] < base.history[-1]["sessions_organic"], "some would have come anyway"
    assert any(c.channel == "affiliate" for c in team.cohorts)


def test_a_higher_rate_brings_more_but_costs_more_per_order():
    world = _world(True)
    lo, hi = (_month(world, r).history[-1] for r in (0.05, 0.30))
    assert hi["orders"] > lo["orders"]
    assert hi["pnl"]["affiliate"] / hi["orders"] > lo["pnl"]["affiliate"] / lo["orders"]


def test_a_running_game_switches_from_a_later_month(tmp_path):
    path = tmp_path / "g.db"
    db.init(path, "x", 3, admin_password="admin-pw")
    con = db.connect(path)
    assert db.affiliates_from(con) == 1
    con.execute("UPDATE game SET affiliates_from = 0, loans_from = 0"); con.commit()
    db.set_game(con, open_round=1)
    service.process_round(con)
    with pytest.raises(ValueError):
        db.set_affiliates_from(con, 1)
    db.set_affiliates_from(con, 2)
    assert not db.affiliates(con, 1) and db.affiliates(con, 2)
    from ecomsim.web.app import create_app
    app = create_app(path); app.config["TESTING"] = True
    admin = app.test_client()
    admin.post("/login", data={"username": "admin", "password": "admin-pw"})
    assert "Working Affiliates" in admin.get("/admin").get_data(as_text=True)
    admin.post("/admin/affiliates", data={"month": "3"})
    assert db.affiliates_from(db.connect(path)) == 3
