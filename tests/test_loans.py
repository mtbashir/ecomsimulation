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


# --- An order left to the engine is counted ---------------------------------------------

def test_a_blank_stock_order_is_counted_as_the_order_we_place(game):
    """Left blank, Stock to purchase means we order for you. The loan box used
    to read that as last month's order: after a month with no order it showed
    nothing, suggested too small a loan, and the month's order was cut again."""
    con, _, _ = game
    _run(con, 1, {"team_01": {"7.1": 0.0}})          # nothing bought in month 1
    advice = service.loan_advice(con, "team_01", 2, {})
    assert advice["stock_auto"] and advice["stock"] > 0 and advice["stock_units"] > 0
    world = _run(con, 2, {"team_01": {"12.6": advice["suggest"]}})
    h = world.teams["team_01"].history[-1]
    assert h["loan"]["stock_cut"] == 0
    assert h["purchase"]["bought"] == pytest.approx(advice["stock_units"], rel=0.02)
    assert h["cash_flow"]["purchases_ordered"] == pytest.approx(advice["stock"], rel=0.05)


def test_a_blank_stock_order_buys_what_the_month_can_pay_for(game):
    """We order for you as far as cash and loan go: the month is never refused
    for it (a cover target can be more than the bank will lend), the team is
    told what will be bought, and the engine buys exactly that."""
    con, path, pw = game
    _run(con, 1, {"team_01": {"7.1": 0.0}})
    db.set_game(con, open_round=2)
    app = create_app(path)
    app.config["TESTING"] = True
    team = app.test_client()
    team.post("/login", data={"username": "team_01", "password": pw["team_01"]})
    team.post("/brief")
    spend = {"3.1": 4_000_000.0}             # leaves part of the order unpaid for
    bal = service.cash_balance(con, "team_01", 2, spend)
    assert bal["fits"] and bal["auto_short"] > 0 and 0 < bal["auto_units"] < bal["stock_units"]
    r = team.post("/submit", data={"3.1": "4000000"}, follow_redirects=True)
    assert db.submission(con, 2, "team_01") is not None
    assert b"we order for you" in r.data and b"we will buy about" in r.data
    world = _run(con, 2, {})
    h = world.teams["team_01"].history[-1]
    assert h["purchase"]["bought"] == pytest.approx(bal["auto_units"], rel=0.05)


def test_a_cover_target_past_the_credit_limit_still_saves(game):
    con, _, _ = game
    _run(con, 1, {"team_01": {"7.1": 0.0}})
    world = db.load_world(con)
    world.teams["team_01"].credit_drawn = 23_500_000      # almost nothing left to borrow
    db.save_round(con, 1, world, "x")
    bal = service.cash_balance(con, "team_01", 2, {"3.1": 4_000_000.0, "12.6": 500_000.0})
    assert bal["fits"] and bal["auto_short"] > 0
    note = service.auto_order_note(bal)
    assert note and "we order for you" in note


def test_the_loan_box_names_the_order_we_place(game):
    con, path, pw = game
    db.set_game(con, open_round=1)
    app = create_app(path)
    app.config["TESTING"] = True
    team = app.test_client()
    team.post("/login", data={"username": "team_01", "password": pw["team_01"]})
    team.post("/brief")
    page = team.get("/submit").data.decode()
    assert "Stock we order for you this month" in page
    assert "Left blank, we order for you:" in page


# --- Autosave ---------------------------------------------------------------------------

def _team_client(con, path, pw, month):
    db.set_game(con, open_round=month)
    app = create_app(path)
    app.config["TESTING"] = True
    c = app.test_client()
    c.post("/login", data={"username": "team_01", "password": pw["team_01"]})
    c.post("/brief")
    return app, c


def test_every_change_saves_as_it_is_made(game):
    con, path, pw = game
    _, c = _team_client(con, path, pw, 1)
    r = c.post("/submit", data={"3.1": "400000", "_autosave": "1"})
    assert r.is_json and r.get_json()["saved"] is True
    assert db.submission(con, 1, "team_01")["3.1"] == 400_000
    c.post("/submit", data={"3.1": "450000", "_autosave": "1"})
    assert db.submission(con, 1, "team_01")["3.1"] == 450_000
    page = c.get("/submit").get_data(as_text=True)
    assert "Changes save automatically." in page and "Submit Month 1" in page
    log = [a["action"] for a in db.audit(con, 20) if a["actor"] == "team_01"]
    assert log.count("autosave") == 1, "one log line per stretch of editing"


def test_a_change_the_cash_cannot_pay_for_is_kept_as_a_draft(game):
    con, path, pw = game
    app, c = _team_client(con, path, pw, 1)
    c.post("/submit", data={"3.1": "400000", "_autosave": "1"})
    r = c.post("/submit", data={"7.1": "500000", "_autosave": "1"}).get_json()
    assert r["saved"] is False and r["draft"] and "Not enough cash" in r["message"]
    assert db.submission(con, 1, "team_01")["3.1"] == 400_000, "the saved month stands"
    page = c.get("/submit").get_data(as_text=True)
    assert "not submitted" in page and 'value="500,000"' in page
    admin = app.test_client()
    admin.post("/login", data={"username": "admin", "password": "admin-pw"})
    assert "changes\nnot submitted" in admin.get("/admin").get_data(as_text=True)
    c.post("/submit", data={"7.1": "5000", "_autosave": "1"})
    assert db.draft(con, 1, "team_01") is None and db.submission(con, 1, "team_01")["7.1"] == 5000


def test_the_submit_button_still_saves_and_says_so(game):
    con, path, pw = game
    _, c = _team_client(con, path, pw, 1)
    r = c.post("/submit", data={"3.1": "400000"}, follow_redirects=True)
    assert b"Submitted for round 1" in r.data
    assert db.submission(con, 1, "team_01")["3.1"] == 400_000


# --- Research and campaigns are saved by their own pages --------------------------------

def _study_tight_spend(con):
    """A Meta budget that fits the month's cash on its own but not with MR-16
    (PKR 22,000) on top: the case where a study alone blocks the month."""
    standing = service.standing_values(con, "team_01", 1)
    base = {"12.1": ["MR-16"], "3.1": 468_000}
    # A blank stock order is elastic and takes whatever is left, so the test
    # is on the firm spending alone: 10,000 over with the study, 12,000 under without.
    bal = service.cash_balance(con, "team_01", 1, base, standing)
    spend = 468_000 + bal["available"] - bal["spend"] + 10_000
    assert not service.cash_balance(con, "team_01", 1, {**base, "3.1": spend}, standing)["fits"]
    assert service.cash_balance(con, "team_01", 1, {"3.1": spend}, standing)["fits"]
    return spend


def test_a_study_cancelled_on_the_research_desk_does_not_live_on_in_a_draft(game):
    """MUSE, month 8 of the Fall-2026 game: a draft refused for want of cash kept
    the study the team had since cancelled, showed it as commissioned, and put it
    back into every later save - so the team's changes could never fit."""
    con, path, pw = game
    _, c = _team_client(con, path, pw, 1)
    c.post("/research/commission", data={"study": ["MR-16"]})
    assert db.submission(con, 1, "team_01")["12.1"] == ["MR-16"]
    spend = _study_tight_spend(con)
    r = c.post("/submit", data={"3.1": str(spend), "_autosave": "1"}).get_json()
    assert r["saved"] is False and r["draft"], "the study does not fit"
    assert db.draft(con, 1, "team_01")["decisions"]["12.1"] == ["MR-16"]
    assert "1 study commissioned" in c.get("/submit").get_data(as_text=True)

    c.post("/research/commission", data={})              # un-tick it on the desk
    saved = db.submission(con, 1, "team_01")
    assert "12.1" not in saved
    assert db.draft(con, 1, "team_01") is None, "without the study the draft fits"
    assert saved["3.1"] == spend, "and the team's change is submitted"
    page = c.get("/submit").get_data(as_text=True)
    assert "nothing commissioned" in page and "1 study commissioned" not in page


def test_the_form_shows_research_as_saved_while_a_draft_is_pending(game):
    con, path, pw = game
    _, c = _team_client(con, path, pw, 1)
    c.post("/research/commission", data={"study": ["MR-16"]})
    c.post("/submit", data={"7.1": "500000", "_autosave": "1"})   # far past the cash
    c.post("/research/commission", data={})
    pending = db.draft(con, 1, "team_01")
    assert pending is not None and "12.1" not in pending["decisions"], "still too dear"
    page = c.get("/submit").get_data(as_text=True)
    assert "nothing commissioned" in page and 'value="500,000"' in page
    c.post("/submit", data={"7.1": "5000", "_autosave": "1"})
    assert "12.1" not in db.submission(con, 1, "team_01")


def test_saving_the_form_keeps_broad_campaigns(game):
    """Broad ([]) is a setting the campaigns page saves; the form used to drop it,
    so the month inherited last month's campaigns instead."""
    con, path, pw = game
    _, c = _team_client(con, path, pw, 1)
    db.submit(con, 1, "team_01", {"3.10": []}, "team_01")
    c.post("/submit", data={"3.1": "400000", "_autosave": "1"})
    saved = db.submission(con, 1, "team_01")
    assert saved["3.10"] == [] and saved["3.1"] == 400_000
