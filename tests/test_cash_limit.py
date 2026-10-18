"""Spending never runs past the cash (ecomsim.loans.check and fund).

A team could order stock worth twice the credit limit: stock is bought on
supplier terms, so nothing stopped the order until its bill fell due and the
team went into administration. Now the form refuses a month whose stock,
marketing and other spending come to more than cash plus the loan applied for
(or what is left on the automatic line), and the engine cuts one that still
gets through.
"""
from __future__ import annotations

import pytest

from ecomsim import bootstrap, params as P
from ecomsim.engine import run_round
from ecomsim.web import db, service
from ecomsim.web.app import create_app

HUGE = {"7.1": 500_000}         # tens of millions of stock


@pytest.fixture
def game(tmp_path):
    path = tmp_path / "g.db"
    pw = db.init(path, "G", 3, rounds=12, admin_password="admin-pw")
    con = db.connect(path)
    db.set_game(con, open_round=1)
    app = create_app(path)
    app.config["TESTING"] = True
    team = app.test_client()
    team.post("/login", data={"username": "team_01", "password": pw["team_01"]})
    return con, team


def test_a_stock_order_past_the_credit_limit_is_refused_even_with_the_whole_loan(game):
    con, team = game
    r = team.post("/submit", data={"12.6": "24000000", "7.1": "500000"},
                  follow_redirects=True)
    assert b"Not enough cash" in r.data
    assert db.submission(con, 1, "team_01") is None, "nothing is saved"


def test_applying_for_a_loan_makes_the_cash_available(game):
    con, team = game
    order = {"7.1": "10000"}
    r = team.post("/submit", data=order, follow_redirects=True)
    assert b"Not enough cash" in r.data and b"bigger working capital loan" in r.data
    assert db.submission(con, 1, "team_01") is None
    team.post("/submit", data={**order, "12.6": "20000000"}, follow_redirects=True)
    assert db.submission(con, 1, "team_01")["7.1"] == 10_000


def test_the_opening_months_defaults_fit_the_starting_capital(game):
    con, _ = game
    assert service.cash_balance(con, "team_01", 1, {})["fits"]


def test_cutting_spending_instead_of_borrowing_also_works(game):
    con, team = game
    over = {"3.1": "3000000"}
    r = team.post("/submit", data=over, follow_redirects=True)
    assert b"Not enough cash" in r.data
    cut = {k: "0" for k in ("3.2", "3.4", "3.8", "3.9", "5.1", "6.1", "7.4")}
    team.post("/submit", data={"3.1": "1000000", **cut}, follow_redirects=True)
    assert db.submission(con, 1, "team_01") is not None


def test_a_game_already_trading_keeps_its_starting_capital(tmp_path):
    path = tmp_path / "old.db"
    db.init(path, "Old", 3)
    con = db.connect(path)
    with con:
        con.execute("UPDATE game SET round = 6, capital = NULL")
    db.migrate(con)
    assert service.load_params(con)["starting_cash"] == db.OLD_CAPITAL
    fresh = tmp_path / "new.db"
    db.init(fresh, "New", 3)
    assert service.load_params(db.connect(fresh))["starting_cash"] == 13_000_000


def test_the_form_shows_the_cash_balance(game):
    _, team = game
    page = team.get("/submit").data
    assert b"Cash available this month" in page and b"Your decisions spend" in page


def test_the_automatic_line_counts_as_applied_for(game):
    con, team = game
    with con:
        con.execute("UPDATE game SET loans_from = 0")
    team.post("/submit", data={"7.1": "10000"}, follow_redirects=True)
    assert db.submission(con, 1, "team_01")["7.1"] == 10_000
    r = team.post("/submit", data=HUGE, follow_redirects=True)
    assert b"Not enough cash" in r.data


def test_the_engine_cuts_an_order_that_gets_past_the_form():
    params = P.load({"n_teams": 3, "events_enabled": 0})
    world = bootstrap.new_world(params, run_id="cash-limit")
    world.loans = False                  # the automatic credit line
    tid = list(world.teams)[0]
    run_round(world, params, {tid: HUGE})
    team = world.teams[tid]
    rec = team.history[-1]
    assert rec["funding"]["stock_cut"] > 0
    assert rec["cash_flow"]["purchases_ordered"] <= params["credit_ceiling"] + 12_000_000
    assert team.credit_drawn <= params["credit_ceiling"]
