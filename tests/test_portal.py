"""The team portal: what a student sees, in the order they see it.

The portal is the whole product for a team. If the first page they meet is a
decision form full of codes, the model behind it does not matter.
"""
from __future__ import annotations

import pytest

from ecomsim import founding as F
from ecomsim.web import db, service
from ecomsim.web.app import create_app


@pytest.fixture
def game(tmp_path):
    path = tmp_path / "g.db"
    passwords = db.init(path, "Test", 3, rounds=12, admin_password="admin-pw")
    app = create_app(path)
    app.config["TESTING"] = True
    return app, passwords, path


def _team(app, pw, who="team_01", read_brief=True):
    c = app.test_client()
    c.post("/login", data={"username": who, "password": pw[who]})
    if read_brief:
        c.post("/brief")
    return c


def _valid_setup(params, **over):
    """A setup that passes validation, as form fields."""
    f = F.Founding.default(params)
    data = {
        "brand_name": "Sehat", "positioning_statement": "Everyday skincare",
        "categories": ["skincare", "haircare"], "tier": "mainstream",
        "model": "d2c", "assortment": f.assortment, "sourcing": "mixed",
        "tech_stack": "standard", "fulfilment": "3pl", "cod_enabled": "on",
        "gateway": "A",
        "capital_inventory": f"{f.capital_inventory:.0f}",
        "capital_marketing": f"{f.capital_marketing:.0f}",
        "capital_technology": f"{f.capital_technology:.0f}",
        "capital_reserve": f"{f.capital_reserve:.0f}",
        "head_marketing": "2", "head_ops": "2", "head_cs": "4",
        "head_analytics": "1",
        "business_plan": "Win on repeat purchase, not on discount.",
        "target_repeat_share": "32", "target_cac": "620",
        "action": "submit",
    }
    data.update(over)
    return data


# --- Arriving for the first time -------------------------------------------------

def test_the_first_thing_a_team_sees_is_the_brief(game):
    app, pw, _p = game
    c = app.test_client()
    c.post("/login", data={"username": "team_01", "password": pw["team_01"]})
    assert c.get("/").headers["Location"].endswith("/brief")

    body = c.get("/brief").data.decode()
    assert "How the game works" in body
    assert "Cash on delivery" in body, "the market must be explained"
    assert "Profitability" in body and "25 points" in body, "so must the marking"
    assert "9%" in body, "the published anchors belong in front of the students"

    # Acknowledging it is what stops the redirect, and it only happens once.
    assert c.post("/brief").status_code == 302
    assert c.get("/").status_code == 200
    assert c.get("/").status_code == 200


def test_the_brief_stays_available_afterwards(game):
    app, pw, _p = game
    team = _team(app, pw)
    assert team.get("/brief").status_code == 200
    assert b"Back to your dashboard" in team.get("/brief").data


# --- The dashboard ---------------------------------------------------------------

def test_the_dashboard_says_what_to_do_now(game):
    app, pw, path = game
    con = db.connect(path)
    team = _team(app, pw)

    # Round 0: build the business.
    body = team.get("/").data.decode()
    assert "Set the business up" in body
    assert "Set up your business" in body
    assert "/found" in body

    # Trading: this month's decisions.
    db.set_game(con, round=1, open_round=2)
    body = team.get("/").data.decode()
    assert "Month 2 is open" in body
    assert "Make your decisions" in body

    # Between rounds: nothing to submit.
    db.set_game(con, open_round=None)
    assert "Nothing to submit right now" in team.get("/").data.decode()


def test_the_dashboard_welcomes_each_round_in_its_own_terms(game):
    app, pw, path = game
    con = db.connect(path)
    team = _team(app, pw)
    seen = set()
    for rnd in (1, 2, 3, 6, 12):
        db.set_game(con, round=rnd - 1, open_round=rnd)
        heading = team.get("/").data.decode()
        seen.add(heading.count("Half time"))
        if rnd == 6:
            assert "Half time" in heading
        if rnd == 12:
            assert "final month" in heading
    assert seen != {0}, "the round framing must actually change"


# --- The founding round ------------------------------------------------------------

def test_a_setup_that_does_not_balance_cannot_be_submitted(game):
    app, pw, path = game
    con = db.connect(path)
    params = service.load_params(con)
    team = _team(app, pw)

    bad = _valid_setup(params, capital_inventory="11000000",
                       capital_marketing="500000",
                       capital_technology="300000", capital_reserve="200000")
    r = team.post("/found", data=bad, follow_redirects=True)
    assert b"must be 25-60%" in r.data or b"at least 10%" in r.data
    assert db.founding(con, "team_01") is None, "nothing may be stored"


def test_a_draft_saves_without_being_a_commitment(game):
    app, pw, path = game
    con = db.connect(path)
    params = service.load_params(con)
    team = _team(app, pw)

    draft = _valid_setup(params, action="save", brand_name="Half Done")
    team.post("/found", data=draft, follow_redirects=True)
    record = db.founding(con, "team_01")
    assert record["config"]["brand_name"] == "Half Done"
    assert record["submitted_at"] is None, "a draft is not a submission"
    assert "Set up your business" in team.get("/").data.decode() or \
           "Continue setting up" in team.get("/").data.decode()


def test_a_submitted_setup_shows_its_projection(game):
    app, pw, path = game
    con = db.connect(path)
    params = service.load_params(con)
    team = _team(app, pw)
    team.post("/found", data=_valid_setup(params), follow_redirects=True)

    assert db.founding(con, "team_01")["submitted_at"] is not None
    page = team.get("/found").data.decode()
    assert "Your first trading month, projected" in page
    assert "Contribution margin" in page and "Runway" in page
    assert "ignores what your rivals are about to do" in page, (
        "a projection presented as a promise is worse than no projection")


def test_the_projection_comes_from_the_engine_not_a_formula(game):
    """Two different businesses must project differently, in the right direction."""
    app, pw, path = game
    con = db.connect(path)
    params = service.load_params(con)

    premium = service.founding_from_form(
        _FakeForm(_valid_setup(params, tier="premium")), params)
    value = service.founding_from_form(
        _FakeForm(_valid_setup(params, tier="value")), params)
    a = service.founding_preview(con, premium)
    b = service.founding_preview(con, value)
    assert a["aov"] > b["aov"], "premium must price higher"
    assert a["orders"] < b["orders"], "and sell less of it"


def test_what_a_team_built_is_what_the_engine_runs(game):
    app, pw, path = game
    con = db.connect(path)
    params = service.load_params(con)
    _team(app, pw, "team_01").post(
        "/found", data=_valid_setup(params, tier="premium", brand_name="Lush"),
        follow_redirects=True)
    _team(app, pw, "team_02").post(
        "/found", data=_valid_setup(params, tier="value", brand_name="Thrift"),
        follow_redirects=True)

    service.process_round(con)
    world = db.load_world(con)
    assert world.teams["team_01"].brand_name == "Lush"
    assert (world.teams["team_01"].history[-1]["aov_net"]
            > world.teams["team_02"].history[-1]["aov_net"]), (
        "the setup a team submitted must be the business it trades")


def test_a_team_that_never_set_up_still_trades(game):
    """Missing setup starts you in the middle. It does not eliminate you."""
    app, _pw, path = game
    con = db.connect(path)
    service.process_round(con)
    world = db.load_world(con)
    assert all(t.history[-1]["orders"] > 0 for t in world.teams.values())


def test_setup_closes_once_trading_starts(game):
    app, pw, path = game
    con = db.connect(path)
    team = _team(app, pw)
    db.set_game(con, round=1)
    r = team.get("/found", follow_redirects=True)
    assert b"Setup is closed" in r.data


def test_a_going_concern_game_has_no_setup_round(tmp_path):
    path = tmp_path / "g.db"
    pw = db.init(path, "Test", 3, rounds=12, admin_password="a",
                 start_mode="going_concern")
    app = create_app(path); app.config["TESTING"] = True
    team = _team(app, pw)
    assert "Set the business up" not in team.get("/").data.decode()
    r = team.get("/found", follow_redirects=True)
    assert b"no setup round" in r.data


# --- Your company ------------------------------------------------------------------

def test_your_company_shows_the_setup_before_trading(game):
    app, pw, path = game
    con = db.connect(path)
    params = service.load_params(con)
    team = _team(app, pw)
    team.post("/found", data=_valid_setup(params, tier="premium"),
              follow_redirects=True)

    body = team.get("/company").data.decode()
    assert "not yet trading" in body
    assert "Premium" in body
    assert "Where the capital went" in body


def test_your_company_shows_the_real_position_once_trading(game):
    app, pw, path = game
    con = db.connect(path)
    params = service.load_params(con)
    team = _team(app, pw)
    team.post("/found", data=_valid_setup(params), follow_redirects=True)
    service.process_round(con)

    body = team.get("/company").data.decode()
    assert "As it stands today" in body
    assert "Owed by couriers" in body, "COD receivable is the cash lesson"
    assert "Active customers" in body


class _FakeForm(dict):
    """Enough of a Werkzeug MultiDict for founding_from_form."""

    def getlist(self, key):
        value = self.get(key, [])
        return value if isinstance(value, list) else [value]


def test_the_instructor_can_see_who_has_set_up(game):
    app, pw, path = game
    con = db.connect(path)
    params = service.load_params(con)
    _team(app, pw, "team_01").post("/found", data=_valid_setup(params),
                                   follow_redirects=True)
    _team(app, pw, "team_02").post(
        "/found", data=_valid_setup(params, action="save", brand_name="Draft Co"),
        follow_redirects=True)

    admin = app.test_client()
    admin.post("/login", data={"username": "admin", "password": "admin-pw"})
    body = admin.get("/admin").data.decode()
    assert "Setup round" in body
    assert "Sehat" in body and "submitted" in body
    assert "Draft Co" in body and "draft" in body
    assert "not started" in body, "team_03 has done nothing and must show it"


def test_an_older_database_gains_the_new_columns(tmp_path):
    """A cohort may be mid-semester when the app is updated."""
    import sqlite3
    path = tmp_path / "old.db"
    db.init(path, "Test", 2, rounds=12, admin_password="a")
    con = sqlite3.connect(path)
    con.executescript(
        "CREATE TABLE t AS SELECT * FROM game;"
        "DROP TABLE game;"
        "CREATE TABLE game (id INTEGER PRIMARY KEY CHECK (id = 1), name TEXT "
        "NOT NULL, preset TEXT NOT NULL DEFAULT 'advanced', round INTEGER NOT "
        "NULL DEFAULT 0, total_rounds INTEGER NOT NULL DEFAULT 12, open_round "
        "INTEGER, ai_competitors INTEGER NOT NULL DEFAULT 2, ai_aggression "
        "REAL NOT NULL DEFAULT 0.5, overrides TEXT NOT NULL DEFAULT '{}', "
        "created_at TEXT NOT NULL);"
        "INSERT INTO game (id, name, round, total_rounds, overrides, created_at) "
        "SELECT 1, name, round, total_rounds, overrides, created_at FROM t;")
    con.commit(); con.close()

    con = db.connect(path)
    with con:
        db.migrate(con)
    assert db.game(con)["start_mode"] == "founding"
    assert "briefing_seen_at" in {
        r["name"] for r in con.execute("PRAGMA table_info(account)")}
