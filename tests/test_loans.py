"""Working capital loans as a decision (ecomsim.loans).

Borrowing used to happen to a team: the credit line drew itself and was never
repaid. In a game on the loan rules the team approves its loan each month, is
cut back to what it can pay for if it approves too little, and spare cash pays
the loan down.
"""
from __future__ import annotations

import pytest

from ecomsim import bootstrap, loans, params as P
from ecomsim.web import db, service
from ecomsim.web.app import create_app

PARAMS = P.load({})
BIG_ORDER = {"7.1": 40000}          # far more stock than cash can pay for


@pytest.fixture
def game(tmp_path):
    path = tmp_path / "g.db"
    pw = db.init(path, "G", 3, rounds=12, admin_password="admin-pw",
                 start_mode="going_concern")
    con = db.connect(path)
    return con, path, pw


def _run(con, month, plans):
    db.set_game(con, open_round=month)
    for tid, d in plans.items():
        db.submit(con, month, tid, d, tid)
    service.process_round(con)
    return db.load_world(con)


# --- Only where switched on ---------------------------------------------------------

def test_a_new_game_asks_for_loans_and_an_engine_run_does_not(game):
    con, _, _ = game
    assert db.loans_from(con) == 1 and db.loans(con, 1)
    assert bootstrap.new_world(PARAMS).loans is False, "calibration keeps the old line"


def test_a_game_already_trading_keeps_the_automatic_line(game):
    con, _, _ = game
    con.execute("UPDATE game SET round = 3, loans_from = NULL")
    con.commit()
    db.migrate(con)
    assert db.loans_from(con) == 0
    assert "12.6" not in {s.code for s in service.open_decisions(con, 4)}


def test_the_instructor_switches_a_running_game_from_a_later_month(game):
    con, _, _ = game
    con.execute("UPDATE game SET loans_from = 0")
    con.commit()
    _run(con, 1, {})
    with pytest.raises(ValueError):
        db.set_loans_from(con, 1)
    db.set_loans_from(con, 2)
    assert not db.loans(con, 1) and db.loans(con, 2)
    assert "12.6" in {s.code for s in service.open_decisions(con, 2)}


# --- Approving, and not approving ----------------------------------------------------

def test_no_loan_approved_cuts_the_stock_order_before_the_month_runs(game):
    con, _, _ = game
    world = _run(con, 1, {"team_01": BIG_ORDER})
    h = world.teams["team_01"].history[-1]
    loan = h["loan"]
    assert loan["approved"] == 0 and loan["stock_cut"] > 0
    assert h["purchase"]["bought"] < h["purchase"]["asked"]
    assert loan["drawn"] == 0, "nothing approved, nothing planned borrowed"


def test_approving_what_the_month_needs_means_nothing_is_cut(game):
    con, _, _ = game
    need = service.loan_advice(con, "team_01", 1, BIG_ORDER)["suggest"]
    assert need > 0
    world = _run(con, 1, {"team_01": {**BIG_ORDER, "12.6": need * 1.05}})
    loan = world.teams["team_01"].history[-1]["loan"]
    assert loan["stock_cut"] == 0 and loan["spend_cut"] == 0


def test_a_team_that_approves_borrows_and_one_that_does_not_is_cut(game):
    con, _, _ = game
    for m in (1, 2, 3):
        plans = {}
        for tid in ("team_01", "team_02"):
            d = dict(BIG_ORDER)
            if tid == "team_01":
                d["12.6"] = service.loan_advice(con, tid, m, d)["suggest"] * 1.05
            plans[tid] = d
        world = _run(con, m, plans)
    a, b = world.teams["team_01"], world.teams["team_02"]
    bought = lambda t: sum(h["purchase"]["bought"] for h in t.history if "purchase" in h)
    assert bought(a) > bought(b), "the unapproved team bought less stock"
    assert a.credit_drawn > 0, "bills fall due and the approved loan is drawn"
    assert sum(h["loan"]["stock_cut"] for h in b.history) > 0


def _borrowed(con):
    """Three busy months on an approved loan, so the team owes the bank."""
    for m in (1, 2, 3):
        d = {"7.1": 14000}
        d["12.6"] = service.loan_advice(con, "team_01", m, d)["suggest"] * 1.05
        world = _run(con, m, {"team_01": d})
    return world


QUIET = {"7.1": 0, "3.1": 0, "3.2": 0, "3.4": 0, "3.8": 0, "3.9": 0}


def test_spare_cash_repays_the_loan(game):
    con, _, _ = game
    _borrowed(con)
    for m in range(4, 9):
        world = _run(con, m, {"team_01": QUIET})
    team = world.teams["team_01"]
    peak = max(h["credit_drawn"] for h in team.history)
    assert peak > 0 and team.credit_drawn < peak * 0.6, "paid well down from its peak"
    assert sum(h.get("loan", {}).get("repaid", 0) for h in team.history) > 0
    if team.credit_drawn > 0:
        assert team.cash <= loans.fixed_costs(PARAMS) + 1, "only a month's cushion kept"


def test_an_extra_repayment_pays_down_more(game, tmp_path):
    con, path, _ = game
    _borrowed(con)
    import shutil
    twin_path = tmp_path / "twin.db"
    con.commit()
    src = db.connect(path)
    twin = db.connect(twin_path)
    src.backup(twin)
    for c, extra in ((con, 0), (twin, 2_000_000)):
        for m in range(4, 9):
            _run(c, m, {"team_01": {**QUIET, "12.7": extra}})
    a = db.load_world(con).teams["team_01"]
    b = db.load_world(twin).teams["team_01"]
    if a.credit_drawn > 0:
        assert b.credit_drawn < a.credit_drawn
    assert sum(h["loan"]["repaid_by_choice"] for h in b.history if "loan" in h) > 0


# --- What the team sees -----------------------------------------------------------------

def _team(path, pw, who="team_01"):
    app = create_app(path)
    app.config["TESTING"] = True
    c = app.test_client()
    c.post("/login", data={"username": who, "password": pw[who]})
    c.post("/brief")
    return c


def test_the_form_says_what_the_month_needs_and_asks_for_approval(game):
    con, path, pw = game
    db.set_game(con, open_round=1)
    db.submit(con, 1, "team_01", BIG_ORDER, "team_01")
    page = _team(path, pw).get("/submit").get_data(as_text=True)
    assert "Working Capital Loan" in page
    assert "You owe the bank" in page and "Credit You Need Available" not in page \
        and "Credit you need available" in page
    assert "Approve PKR" in page
    assert "Nothing is approved yet" in page, "the banner at the top"


def test_the_report_says_what_was_borrowed_and_cut(game):
    con, path, pw = game
    _run(con, 1, {"team_01": BIG_ORDER})
    db.set_game(con, open_round=2)
    page = _team(path, pw).get("/results/1").get_data(as_text=True)
    assert "Working Capital Loan" in page
    assert "we cut" in page and "your stock order by" in page
    assert "You now owe" in page


def test_the_admin_card_switches_a_running_game(game):
    con, path, _ = game
    con.execute("UPDATE game SET loans_from = 0")
    con.commit()
    _run(con, 1, {})
    app = create_app(path)
    app.config["TESTING"] = True
    admin = app.test_client()
    admin.post("/login", data={"username": "admin", "password": "admin-pw"})
    page = admin.get("/admin").get_data(as_text=True)
    assert "Working Capital Loans" in page and "Loans as a Decision from Month" in page
    admin.post("/admin/loans", data={"month": "2"})
    assert db.loans_from(con) == 2
