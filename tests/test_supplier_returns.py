"""Returning stock to the supplier (decision 7.6): half the cost comes back.

Offered in new games from month 1, and in a game already trading from a month
the instructor picks. The supplier keeps half of the landed cost; the other
half is cash that month. A one-off, never carried into the next month.
"""
import copy, sys
sys.path.insert(0, "src")

import pytest

from ecomsim import bootstrap, params as P
from ecomsim.engine import NOT_CARRIED, run_round
from ecomsim.web import db, service

PARAMS = P.load({"n_teams": 2, "events_enabled": 0})


def _world(on):
    w = bootstrap.new_world(PARAMS, run_id="ret")
    w.rules_from, w.supplier_returns = 1, on
    run_round(w, PARAMS, {})
    return w


def _send(world, units):
    w = copy.deepcopy(world)
    team = list(w.teams.values())[0]
    code = max(team.inventory, key=team.inventory.get)
    held = team.inventory[code]
    run_round(w, PARAMS, {team.team_id: {"7.6": {code: units if units else held * 0.5}}})
    return team, code, held


def test_half_the_cost_comes_back_and_half_is_a_fee():
    world = _world(True)
    team, code, held = _send(world, None)
    h = team.history[-1]
    sent = next(r for r in h["stock"] if r["code"] == code)["to_supplier"]
    assert sent == pytest.approx(held * 0.5, rel=1e-6)
    refund = h["cash_flow"]["supplier_refund"]
    assert refund > 0 and h["pnl"]["restocking"] == pytest.approx(refund, rel=1e-6)


def test_never_more_than_is_on_the_shelf():
    world = _world(True)
    team, code, held = _send(world, 10_000_000)
    r = next(r for r in team.history[-1]["stock"] if r["code"] == code)
    shelf = r["open"] + r["received"] + r.get("returned", 0.0)   # arrivals land first
    assert r["to_supplier"] == pytest.approx(shelf, rel=1e-6) and r["close"] < 1


def test_nothing_goes_back_without_the_switch_and_it_never_carries():
    world = _world(False)
    team, code, _ = _send(world, None)
    assert team.history[-1]["cash_flow"]["supplier_refund"] == 0
    assert "7.6" in NOT_CARRIED


def test_a_running_game_offers_it_from_a_later_month(tmp_path):
    path = tmp_path / "g.db"
    db.init(path, "x", 3, admin_password="admin-pw")
    con = db.connect(path)
    assert db.returns_from(con) == 1 and "7.6" in {s.code for s in service.open_decisions(con, 1)}
    con.execute("UPDATE game SET returns_from = 0, loans_from = 0"); con.commit()
    db.set_game(con, open_round=1)
    service.process_round(con)
    assert "7.6" not in {s.code for s in service.open_decisions(con, 2)}
    db.set_returns_from(con, 3)
    assert "7.6" in {s.code for s in service.open_decisions(con, 3)}
    from ecomsim.web.app import create_app
    app = create_app(path); app.config["TESTING"] = True
    admin = app.test_client()
    admin.post("/login", data={"username": "admin", "password": "admin-pw"})
    assert "Returns to the Supplier" in admin.get("/admin").get_data(as_text=True)


def test_the_team_names_units_product_by_product_on_the_form(tmp_path):
    from ecomsim.web.app import create_app
    path = tmp_path / "g.db"
    pw = db.init(path, "x", 3, admin_password="admin-pw", start_mode="going_concern")
    con = db.connect(path)
    con.execute("UPDATE game SET loans_from = 0"); con.commit()
    db.set_game(con, open_round=1); service.process_round(con)
    db.set_game(con, open_round=2)
    app = create_app(path); app.config["TESTING"] = True
    c = app.test_client()
    c.post("/login", data={"username": "team_01", "password": pw["team_01"]})
    c.post("/brief")
    page = c.get("/submit").get_data(as_text=True)
    assert "Units to Return" in page or "Units to return" in page
    import re
    code = re.search(r'name="ret_([^"]+)"', page).group(1)
    c.post("/submit", data={f"ret_{code}": "50"})
    saved = db.submissions(con, 2).get("team_01") or {}
    assert saved.get("7.6") == {code: 50.0}
