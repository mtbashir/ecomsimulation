"""Full costs: packaging, 3PL and quality positioning cost what they say.

Three decisions promised a cost the engine never charged, so premium
packaging, a big 3PL share and claiming a premium tier were free. New games
charge them; a game already trading charges them from a month the instructor
picks, keeping the months already played as they were.
"""
import sys
sys.path.insert(0, "src")

import pytest

from ecomsim import bootstrap, params as P
from ecomsim.engine import run_round
from ecomsim.modules.m14_pnl import quality_cost_ratio
from ecomsim.web import db, service

PARAMS = P.load({"n_teams": 2, "events_enabled": 0})


def _month(full: bool, plan: dict):
    world = bootstrap.new_world(PARAMS, run_id="costs")
    world.rules_from = 1
    world.full_costs = full
    a, b = list(world.teams)
    run_round(world, PARAMS, {a: plan, b: {}})
    return world.teams[a].history[-1], world.teams[a]


def test_without_the_switch_nothing_changes():
    assert getattr(bootstrap.new_world(PARAMS), "full_costs", False) is False
    plan = {"8.5": "premium", "8.2": 1.0, "1.5": "premium"}
    off, _ = _month(False, plan)
    assert off["pnl"]["packaging"] == off["pnl"]["tpl"] == off["pnl"]["quality_premium"] == 0


def test_packaging_and_3pl_are_charged_on_every_order():
    on, _ = _month(True, {"8.5": "premium", "8.2": 0.5})
    orders = on["orders"]
    assert on["pnl"]["packaging"] == pytest.approx(orders * PARAMS["packaging_cost_premium"])
    assert on["pnl"]["tpl"] == pytest.approx(orders * 0.5 * PARAMS["tpl_cost_per_order"])
    plain, _ = _month(True, {"8.5": "basic", "8.2": 0.0})
    assert plain["pnl"]["packaging"] == plain["pnl"]["tpl"] == 0
    assert on["contribution_pre_marketing_pct"] < plain["contribution_pre_marketing_pct"]


def test_claiming_a_tier_costs_or_saves_the_sourcing_difference():
    for tier, higher in (("premium", True), ("economy", False)):
        h, team = _month(True, {"1.5": tier})
        ratio = quality_cost_ratio(team, PARAMS, {"1.5": tier})
        assert (ratio > 1) == higher
        assert h["pnl"]["quality_premium"] == pytest.approx(h["pnl"]["cogs_sold"] * (ratio - 1))
    auto, team = _month(True, {})
    assert auto["pnl"]["quality_premium"] == 0 and quality_cost_ratio(team, PARAMS, {}) == 1.0


def test_the_extra_costs_are_paid_in_cash():
    plan = {"8.5": "premium", "8.2": 1.0, "1.5": "premium"}
    on, _ = _month(True, plan)
    off, _ = _month(False, plan)
    extra = on["pnl"]["packaging"] + on["pnl"]["tpl"] + on["pnl"]["quality_premium"]
    assert extra > 0
    assert off["cash_balance"] - on["cash_balance"] == pytest.approx(extra, rel=1e-6)


def _trading(path, months=3):
    db.init(path, "x", 3, admin_password="admin-pw")
    con = db.connect(path)
    con.execute("UPDATE game SET costs_from = 0, loans_from = 0")
    con.commit()
    for m in range(1, months + 1):
        db.set_game(con, open_round=m)
        db.submit(con, m, "team_01", {"8.5": "premium", "8.2": 1.0}, "team_01")
        service.process_round(con)
    return con


def test_a_new_game_charges_them_and_a_trading_game_waits_for_a_month(tmp_path):
    db.init(tmp_path / "n.db", "x", 3, admin_password="x")
    new = db.connect(tmp_path / "n.db")
    assert db.costs_from(new) == 1 and db.full_costs(new, 1)
    con = _trading(tmp_path / "t.db")
    con.execute("UPDATE game SET costs_from = NULL"); con.commit()
    db.migrate(con)
    assert db.costs_from(con) == 0
    with pytest.raises(ValueError):
        db.set_costs_from(con, 3)
    db.set_costs_from(con, 4)
    assert not db.full_costs(con, 3) and db.full_costs(con, 4)


def test_switching_from_a_later_month_keeps_the_months_played(tmp_path):
    con = _trading(tmp_path / "t.db")
    before = [h["pnl"]["packaging"] for h in db.load_world(con).teams["team_01"].history]
    db.set_costs_from(con, 4)
    db.set_game(con, open_round=4)
    db.submit(con, 4, "team_01", {"8.5": "premium", "8.2": 1.0}, "team_01")
    service.process_round(con)
    h = db.load_world(con).teams["team_01"].history
    assert [x["pnl"]["packaging"] for x in h[:3]] == before == [0, 0, 0]
    assert h[3]["pnl"]["packaging"] > 0 and h[3]["pnl"]["tpl"] > 0


def test_the_instructor_switches_it_from_the_overview(tmp_path):
    from ecomsim.web.app import create_app
    path = tmp_path / "t.db"
    _trading(path).close()
    app = create_app(path)
    app.config["TESTING"] = True
    admin = app.test_client()
    admin.post("/login", data={"username": "admin", "password": "admin-pw"})
    page = admin.get("/admin").get_data(as_text=True)
    assert "Full Costs" in page and "Full Costs from Month" in page
    admin.post("/admin/costs", data={"month": "5"})
    assert db.costs_from(db.connect(path)) == 5


def test_the_workbook_shows_the_new_lines(tmp_path):
    from ecomsim import workbook
    con = _trading(tmp_path / "t.db", months=1)
    db.set_costs_from(con, 2)
    db.set_game(con, open_round=2)
    db.submit(con, 2, "team_01", {"8.5": "premium", "8.2": 1.0, "1.5": "premium"}, "team_01")
    service.process_round(con)
    world = db.load_world(con)
    data = workbook.build(world.teams["team_01"], service.load_params(con), "T", 2)
    assert data[:2] == b"PK", "a workbook with the packaging, 3PL and sourcing lines"
