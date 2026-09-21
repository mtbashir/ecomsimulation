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

    # Trading: this month's decisions, with the way in.
    db.set_game(con, round=1, open_round=2)
    body = team.get("/").data.decode()
    assert "Enter month 2 decisions" in body
    assert "/submit" in body

    # Between rounds: nothing to submit, and it says so rather than offering a
    # button that would only refuse.
    db.set_game(con, open_round=None)
    closed = team.get("/").data.decode()
    assert "Submissions are closed" in closed
    assert "Enter month" not in closed


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


# --- Segment focus (D0.3) ----------------------------------------------------------

def test_exactly_two_segments_or_it_is_not_a_choice(game):
    app, pw, path = game
    con = db.connect(path)
    params = service.load_params(con)
    team = _team(app, pw)
    r = team.post("/found", data=_valid_setup(
        params, segment_priority=["value_seekers"]), follow_redirects=True)
    assert b"exactly two priority segments" in r.data
    assert db.founding(con, "team_01") is None


def test_the_segment_choice_is_explained_in_business_terms(game):
    app, pw, path = game
    team = _team(app, pw)
    page = team.get("/found").data.decode()
    assert "Quality Loyalists" in page
    assert "comes back far more often than average" in page, (
        "the reason to choose them must be on the page"
    )
    assert "18% of the market" in page
    assert "cares most about quality" in page


def test_each_product_carries_its_own_sourcing_choice(game):
    app, pw, path = game
    con = db.connect(path)
    params = service.load_params(con)
    team = _team(app, pw)

    page = team.get("/found").data.decode()
    assert "Source from" in page
    assert "Local &middot; 9 days" in page or "Local · 9 days" in page
    assert "Imported" in page

    f = F.Founding.default(params)
    data = _valid_setup(params)
    for i, code in enumerate(f.assortment):
        data[f"sourcing_{code}"] = "import" if i % 2 else "local"
        data[f"price_{code}"] = str(F.reference_price(params.sku(code), "mainstream"))
    team.post("/found", data=data, follow_redirects=True)

    saved = db.founding(con, "team_01")["config"]["sourcing_by_sku"]
    assert saved[f.assortment[0]] == "local"
    assert saved[f.assortment[1]] == "import"


def test_a_locally_sourced_product_costs_more_than_an_imported_one(game):
    """The margin on the page has to move with the sourcing choice."""
    app, pw, path = game
    con = db.connect(path)
    params = service.load_params(con)
    f = F.Founding.default(params)
    code = f.assortment[0]

    f.sourcing_by_sku = {code: "local"}
    local = next(r for r in service.product_catalogue(params, f) if r["code"] == code)
    f.sourcing_by_sku = {code: "import"}
    imported = next(r for r in service.product_catalogue(params, f) if r["code"] == code)

    assert local["cost"] > imported["cost"]
    assert local["margin"] < imported["margin"], (
        "cheaper stock at the same price is a better margin")


# --- The rebuilt shell -------------------------------------------------------------

def test_a_team_only_sees_the_field_it_paid_to_see(game):
    """Rivals' share is a purchased study. Without it, you do not get a table."""
    app, pw, path = game
    con = db.connect(path)
    params = service.load_params(con)
    for i in (1, 2, 3):
        cfg = F.Founding.default(params)
        db.save_founding(con, f"team_{i:02d}", service.founding_to_dict(cfg),
                         "sys", submitted=True)
    db.set_game(con, open_round=1)
    db.submit(con, 1, "team_02", {"12.1": ["MR-03"]}, "sys")
    service.process_round(con)

    blind = service.standings(con, "team_01")
    assert blind["bought"] is False, "you have not bought the study"
    informed = service.standings(con, "team_02")
    assert informed["bought"] is True
    assert len(informed["rows"]) == 3
    assert any(r["you"] for r in informed["rows"])

    team = _team(app, pw, "team_01")
    body = team.get("/").data.decode()
    assert "have not bought the Market Share Report" in body
    assert "Thrift" not in body


def test_a_rising_cost_of_acquisition_is_not_good_news(game):
    """Direction, not sign: the arrow colour has to follow the meaning."""
    app, pw, path = game
    con = db.connect(path)
    params = service.load_params(con)
    db.save_founding(con, "team_01",
                     service.founding_to_dict(F.Founding.default(params)),
                     "sys", submitted=True)
    for _ in range(2):
        service.process_round(con)

    kpis = {k["label"]: k for k in service.headline_kpis(con, "team_01")}
    assert kpis, "the dashboard needs figures once a month has run"
    cac = kpis["Cost per new customer"]
    assert cac["rising_is_good"] is False
    if cac["delta"] and cac["delta"].startswith("+"):
        assert cac["direction"] == "dn", "rising CAC must not read as good news"


def test_the_plan_meters_only_appear_once_a_team_has_promised_something(game):
    app, pw, path = game
    con = db.connect(path)
    params = service.load_params(con)

    bare = F.Founding.default(params)
    db.save_founding(con, "team_01", service.founding_to_dict(bare), "sys", submitted=True)
    promised = F.Founding.default(params)
    promised.target_repeat_share, promised.target_cac = 0.32, 620
    db.save_founding(con, "team_02", service.founding_to_dict(promised), "sys",
                     submitted=True)
    service.process_round(con)

    assert service.plan_meters(con, "team_01") == []
    meters = service.plan_meters(con, "team_02")
    assert {m["label"] for m in meters} == {"Repeat order share",
                                            "Cost per new customer"}
    assert all(0 <= m["fill"] <= 100 and 0 <= m["mark"] <= 100 for m in meters)


def test_the_agenda_reports_real_trouble_not_filler(game):
    app, pw, path = game
    con = db.connect(path)
    params = service.load_params(con)
    db.save_founding(con, "team_01",
                     service.founding_to_dict(F.Founding.default(params)),
                     "sys", submitted=True)
    db.set_game(con, open_round=1)
    db.submit(con, 1, "team_01", {"12.1": ["MR-01"]}, "sys")
    service.process_round(con)
    db.set_game(con, open_round=2)

    titles = [a["title"] for a in service.agenda(con, "team_01")]
    assert "Category Demand & Seasonality" in titles, "research bought must be listed"
    assert "Month 1 report" in titles
    assert "Submit month 2" in titles


def test_the_month_form_is_reachable_while_setup_is_still_the_current_round(game):
    """Month 1 opens while the game is on round 0. Both links must be there."""
    app, pw, path = game
    con = db.connect(path)
    db.set_game(con, open_round=1)
    team = _team(app, pw)
    body = team.get("/").data.decode()
    assert "/found" in body, "setup is still open"
    assert "/submit" in body, "and month 1 is taking submissions"


# --- The decision page as tiles ------------------------------------------------------

def _trading(app, path, months=1):
    """A founded team, some months in, with month N+1 open."""
    con = db.connect(path)
    params = service.load_params(con)
    for i in (1, 2, 3):
        cfg = F.Founding.default(params)
        cfg.prices = {c: F.reference_price(params.sku(c), cfg.tier)
                      for c in cfg.assortment}
        cfg.sourcing_by_sku = {c: "local" for c in cfg.assortment}
        db.save_founding(con, f"team_{i:02d}", service.founding_to_dict(cfg),
                         "sys", submitted=True)
    for r in range(1, months + 1):
        db.set_game(con, open_round=r)
        service.process_round(con)
    db.set_game(con, open_round=months + 1)
    return con


def test_a_decision_not_taken_is_marked_and_counted(game):
    app, pw, path = game
    con = _trading(app, path)
    team = _team(app, pw)

    page = team.get("/submit").data.decode()
    assert "changed this month" in page
    assert "carried forward" in page, "an untouched lever says so on its face"
    assert page.count('class="tile set"') == 0, "nothing has been changed yet"

    team.post("/submit", data={"3.1": "750000"}, follow_redirects=True)
    page = team.get("/submit").data.decode()
    assert page.count('class="tile set"') == 1
    assert ">1</b> of" in page, "the tally counts what was changed"


def test_the_tile_face_says_where_a_decision_stands(game):
    app, pw, path = game
    con = _trading(app, path)
    team = _team(app, pw)
    team.post("/submit", data={"2.2": "12", "8.5": "branded"}, follow_redirects=True)

    page = team.get("/submit").data.decode()
    assert "12%" in page, "a percentage shows as a percentage"
    assert "Branded" in page, "a choice shows its label, not its code"


def test_this_months_prices_reach_the_engine(game):
    """Re-pricing is a monthly lever, not only a founding one."""
    app, pw, path = game
    con = _trading(app, path)
    team = _team(app, pw)

    shelf = service.monthly_catalogue(con, "team_01", {})
    data = {f"price_{r['code']}": f"{r['standing'] * 1.25:.0f}" for r in shelf}
    data.update({f"sourcing_{r['code']}": r["sourcing"] for r in shelf})
    team.post("/submit", data=data, follow_redirects=True)

    saved = db.submission(con, 2, "team_01")["1.1"]
    assert len(saved) == len(shelf), "every line was re-priced"
    assert all("price" in cell for cell in saved.values())

    before = db.load_world(con).teams["team_01"].history[-1]["aov_net"]
    service.process_round(con)
    after = db.load_world(con).teams["team_01"].history[-1]["aov_net"]
    assert after > before * 1.1, "a 25% price rise must reach the basket"


def test_switching_a_line_to_imported_this_month_cuts_its_cost(game):
    app, pw, path = game
    con = _trading(app, path)
    team = _team(app, pw)
    shelf = service.monthly_catalogue(con, "team_01", {})
    assert all(r["sourcing"] == "local" for r in shelf)

    data = {f"sourcing_{r['code']}": "import" for r in shelf}
    data.update({f"price_{r['code']}": f"{r['standing']:.0f}" for r in shelf})
    team.post("/submit", data=data, follow_redirects=True)

    moved = service.monthly_catalogue(con, "team_01", db.submission(con, 2, "team_01"))
    assert all(r["sourcing"] == "import" for r in moved)
    assert moved[0]["cost"] < shelf[0]["cost"], "imported lands cheaper"
    assert moved[0]["margin"] > shelf[0]["margin"], "so the margin improves"


def test_leaving_the_shelf_exactly_as_it_was_is_not_a_change(game):
    """Submitting the form without touching it must not read as 33 decisions."""
    app, pw, path = game
    con = _trading(app, path)
    team = _team(app, pw)
    shelf = service.monthly_catalogue(con, "team_01", {})

    data = {f"price_{r['code']}": f"{r['standing']:,.0f}" for r in shelf}
    data.update({f"sourcing_{r['code']}": r["sourcing"] for r in shelf})
    team.post("/submit", data=data, follow_redirects=True)

    assert "1.1" not in (db.submission(con, 2, "team_01") or {}), (
        "re-submitting the standing shelf is not a decision")


# --- Roster, names, branding ---------------------------------------------------------

def test_the_instructor_can_add_and_remove_teams_before_trading(game):
    app, _pw, path = game
    con = db.connect(path)
    admin = app.test_client()
    admin.post("/login", data={"username": "admin", "password": "admin-pw"})

    admin.post("/admin/teams", data={"action": "add", "count": "2"},
               follow_redirects=True)
    ids = [r["team_id"] for r in db.accounts(con, "team")]
    assert len(ids) == 5 and "team_05" in ids

    admin.post("/admin/teams", data={"action": "remove", "team_id": "team_05"},
               follow_redirects=True)
    assert "team_05" not in [r["team_id"] for r in db.accounts(con, "team")]

    # And a market needs somebody to be a market.
    for tid in ("team_04", "team_03"):
        admin.post("/admin/teams", data={"action": "remove", "team_id": tid},
                   follow_redirects=True)
    r = admin.post("/admin/teams", data={"action": "remove", "team_id": "team_02"},
                   follow_redirects=True)
    assert b"at least two teams" in r.data
    assert len(db.accounts(con, "team")) == 2


def test_the_roster_is_fixed_once_the_market_has_been_sized(game):
    """The world is built on the first run. A seat added later has no company."""
    app, _pw, path = game
    con = db.connect(path)
    service.process_round(con)
    admin = app.test_client()
    admin.post("/login", data={"username": "admin", "password": "admin-pw"})

    r = admin.post("/admin/teams", data={"action": "add", "count": "1"},
                   follow_redirects=True)
    assert b"roster is fixed" in r.data
    assert len(db.accounts(con, "team")) == 3


def test_adding_a_team_grows_the_market_it_trades_in(game):
    app, _pw, path = game
    con = db.connect(path)
    admin = app.test_client()
    admin.post("/login", data={"username": "admin", "password": "admin-pw"})
    admin.post("/admin/teams", data={"action": "add", "count": "3"},
               follow_redirects=True)

    service.process_round(con)
    assert len(db.load_world(con).teams) == 6, "everyone on the roster trades"


def test_a_team_names_itself_its_company_and_its_brand(game):
    """Three names doing three jobs, and the mandate they are playing to."""
    app, pw, path = game
    con = db.connect(path)
    params = service.load_params(con)
    db.save_founding(con, "team_01",
                     service.founding_to_dict(F.Founding.default(params)),
                     "sys", submitted=True)
    team = _team(app, pw)
    team.post("/setup", data={"team_name": "The Cartel",
                              "company_name": "Sehat Holdings",
                              "brand_name": "Sehat",
                              "objective": "loyal_base"}, follow_redirects=True)

    config = db.founding(con, "team_01")["config"]
    assert db.account(con, "team_01")["display_name"] == "The Cartel"
    assert config["company_name"] == "Sehat Holdings"
    assert config["brand_name"] == "Sehat"
    assert config["objective"] == "loyal_base"
    assert "Sehat" in team.get("/").data.decode(), "the brand leads the sidebar"


def test_an_objective_the_board_never_set_is_refused(game):
    app, pw, path = game
    con = db.connect(path)
    team = _team(app, pw)
    team.post("/setup", data={"objective": "win at all costs"},
              follow_redirects=True)
    assert (db.founding(con, "team_01") or {}).get("config", {}) \
        .get("objective", "") == ""


def test_a_rename_reaches_the_report_without_rewriting_the_result(game):
    app, pw, path = game
    con = db.connect(path)
    params = service.load_params(con)
    cfg = F.Founding.default(params)
    cfg.brand_name = "Old Name"
    db.save_founding(con, "team_01", service.founding_to_dict(cfg), "sys",
                     submitted=True)
    service.process_round(con)
    assert "Old Name" in service.team_report(con, "team_01", 1)

    db.set_identity(con, "team_01", {"brand_name": "New Name"})
    assert "New Name" in service.team_report(con, "team_01", 1)
    assert db.load_world(con).teams["team_01"].brand_name == "Old Name", (
        "the stored result is not rewritten")


def test_the_logo_is_on_every_page_and_the_picker_only_in_setup(game):
    app, pw, path = game
    db.set_game(db.connect(path), open_round=1)
    team = _team(app, pw)
    anon = app.test_client()
    for client, path_ in [(anon, "/login"), (team, "/"), (team, "/company"),
                          (team, "/brief"), (team, "/submit")]:
        body = client.get(path_).data.decode()
        assert "consulytics.png" in body, path_

    assert 'data-set-theme="consulytics"' in team.get("/brief").data.decode()
    # The switcher script ships everywhere; the buttons only exist in setup.
    for path_ in ("/", "/company", "/submit"):
        assert 'data-set-theme="' not in team.get(path_).data.decode(), path_


def test_the_default_theme_is_the_brand_one(game):
    app, pw, _p = game
    body = app.test_client().get("/login").data.decode()
    assert 'data-theme="consulytics"' in body


# --- Pricing by product, bundles, and the handbook -----------------------------------

def test_discount_is_the_average_of_what_actually_sells(game):
    """A deep cut on a line nobody buys is not a promotion."""
    app, pw, path = game
    con = _trading(app, path)
    params = service.load_params(con)
    shelf = service.monthly_catalogue(con, "team_01", {})
    by_weight = sorted(shelf, key=lambda r: r["weight"])

    def discount_on(rows, pct):
        grid = {r["code"]: {"discount": pct} for r in rows}
        world = db.load_world(con)
        team = world.teams["team_01"]
        from ecomsim.modules.m00_resolve import _discount
        return _discount(team, params, {"1.1": grid})

    small = discount_on(by_weight[:3], 0.50)
    big = discount_on(by_weight[-3:], 0.50)
    assert big > small * 1.3, (
        f"cutting the big lines has to cost more: {big:.1%} vs {small:.1%}")
    assert discount_on(shelf, 0.20) == pytest.approx(0.20), (
        "the same cut everywhere is that cut")


def test_a_team_that_sets_no_per_product_discount_keeps_the_site_wide_one(game):
    """The file runner and the archetypes still drive the single lever."""
    app, pw, path = game
    con = _trading(app, path)
    params = service.load_params(con)
    from ecomsim.modules.m00_resolve import _discount
    team = db.load_world(con).teams["team_01"]
    assert _discount(team, params, {"2.2": 0.18}) == pytest.approx(0.18)


def test_a_discount_past_sixty_per_cent_is_refused(game):
    app, pw, path = game
    con = _trading(app, path)
    team = _team(app, pw)
    shelf = service.monthly_catalogue(con, "team_01", {})
    data = {f"price_{r['code']}": f"{r['standing']:.0f}" for r in shelf}
    data.update({f"sourcing_{r['code']}": r["sourcing"] for r in shelf})
    data[f"discount_{shelf[0]['code']}"] = "80"
    r = team.post("/submit", data=data, follow_redirects=True)
    assert b"not a promotion" in r.data


def test_bundles_are_priced_and_still_counted_by_the_engine(game):
    app, pw, path = game
    con = _trading(app, path)
    team = _team(app, pw)
    rows = service.bundle_rows(con, "team_01", {})
    assert rows and rows[0]["cost"] == pytest.approx(
        service.monthly_catalogue(con, "team_01", {})[0]["cost"] * 3)

    picked = [r["code"] for r in rows[:2]]
    data = {f"bundle_{c}": "1" for c in picked}
    data.update({f"bundleprice_{c}": "2500" for c in picked})
    team.post("/submit", data=data, follow_redirects=True)

    saved = db.submission(con, 2, "team_01")["1.2"]
    assert set(saved) == set(picked)
    assert saved[picked[0]]["price"] == pytest.approx(2500)

    before = db.load_world(con).teams["team_01"].history[-1]["aov_net"]
    service.process_round(con)
    after = db.load_world(con).teams["team_01"].history[-1]["aov_net"]
    assert after > before, "offering packs lifts basket size"


def test_positioning_is_asked_before_pricing(game):
    app, pw, path = game
    _trading(app, path)
    page = _team(app, pw).get("/submit").data.decode()
    assert page.index("Product quality positioning") < page.index("Range, prices"), (
        "what you claim to be comes before what you charge")


def test_every_decision_carries_a_handbook_entry_you_can_open(game):
    app, pw, path = game
    con = _trading(app, path)
    page = _team(app, pw).get("/submit").data.decode()
    assert "Open the handbook" in page
    for spec in service.open_decisions(con, 2):
        if spec.code == "2.2":
            continue
        entry = service.handbook_entry(spec)
        assert entry["help"], spec.code
        assert entry["url"].endswith(spec.code.replace(".", "")), spec.code


def test_appearance_is_remembered_against_the_account_not_the_browser(game):
    """Two teams on one lab machine must not share one colour scheme."""
    app, pw, _ = game
    one, two = _team(app, pw, "team_01"), _team(app, pw, "team_02")
    one.post("/theme", data={"theme": "dark"})
    assert 'data-theme="dark"' in one.get("/brief").data.decode()
    assert 'data-theme="consulytics"' in two.get("/brief").data.decode(), (
        "the second team still gets the default")

    fresh = app.test_client()          # a new browser, no storage of its own
    fresh.post("/login", data={"username": "team_01", "password": pw["team_01"]})
    assert 'data-theme="dark"' in fresh.get("/brief").data.decode()


def test_the_instructor_can_set_their_own_appearance(game):
    app, _, _ = game
    c = app.test_client()
    c.post("/login", data={"username": "admin", "password": "admin-pw"})
    assert 'action="/theme"' in c.get("/admin").data.decode()
    c.post("/theme", data={"theme": "slate"})
    assert 'data-theme="slate"' in c.get("/admin").data.decode()


def test_a_made_up_theme_is_ignored_rather_than_stored(game):
    app, pw, _ = game
    c = _team(app, pw)
    c.post("/theme", data={"theme": "neon"})
    assert 'data-theme="consulytics"' in c.get("/brief").data.decode()


def test_the_range_grid_is_grouped_by_category(game):
    """Teams review a range category by category, not in SKU-code order."""
    app, pw, path = game
    con = _trading(app, path)
    rows = service.monthly_catalogue(con, "team_01", {})
    seen = [r["category"] for r in rows]
    assert seen == sorted(seen), "each category's lines sit together"
    page = _team(app, pw).get("/submit").data.decode()
    assert "<th class=\"c-cat\">Category</th>" in page
