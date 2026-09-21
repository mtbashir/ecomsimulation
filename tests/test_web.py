"""Team portal and instructor console.

The things that must not break: a team cannot see another team's anything, a
round can always be rolled back and re-run, and the file-based escape hatch
stays available when the app is the problem.
"""
from __future__ import annotations

import pytest
from html import escape

from ecomsim.web import db, service
from ecomsim.web.app import create_app


@pytest.fixture
def game(tmp_path):
    path = tmp_path / "g.db"
    passwords = db.init(path, "Test", 3, rounds=12, admin_password="admin-pw")
    app = create_app(path)
    app.config["TESTING"] = True
    return app, passwords, path


def _client(app, username, password):
    c = app.test_client()
    r = c.post("/login", data={"username": username, "password": password})
    assert r.status_code in (302, 200)
    return c


# --- Authentication --------------------------------------------------------------

def test_everything_requires_a_login(game):
    app, _pw, _p = game
    anon = app.test_client()
    for path in ("/", "/submit", "/admin", "/admin/params", "/results/1"):
        assert anon.get(path).status_code == 302, path


def test_wrong_password_is_refused(game):
    app, _pw, _p = game
    r = app.test_client().post("/login", data={"username": "admin",
                                               "password": "nope"},
                               follow_redirects=True)
    assert b"Wrong username or password" in r.data


def test_a_team_cannot_reach_the_instructor_pages(game):
    app, pw, _p = game
    team = _client(app, "team_01", pw["team_01"])
    for path in ("/admin", "/admin/params", "/admin/decisions", "/admin/teams",
                 "/admin/console/1", "/admin/report/team_02/1",
                 "/admin/export/1.csv"):
        assert team.get(path).status_code == 403, path
    assert team.post("/admin/run").status_code == 403


def test_an_admin_who_opens_the_site_root_first_reaches_the_console(game):
    """The 403 people hit in class: root -> /login?next=/ -> team-only page."""
    app, _pw, _p = game
    c = app.test_client()
    assert c.get("/").headers["Location"].endswith("/login?next=/")
    r = c.post("/login?next=/", data={"username": "admin", "password": "admin-pw"})
    assert r.status_code == 302
    assert c.get(r.headers["Location"], follow_redirects=True).status_code == 200


def test_the_root_page_sends_an_instructor_to_the_console(game):
    app, _pw, _p = game
    admin = _client(app, "admin", "admin-pw")
    assert admin.get("/").headers["Location"].endswith("/admin")


def test_a_team_is_still_sent_where_it_asked_for(game):
    app, pw, _p = game
    c = app.test_client()
    r = c.post("/login?next=/submit", data={"username": "team_01",
                                            "password": pw["team_01"]})
    assert r.headers["Location"].endswith("/submit")


def test_login_will_not_bounce_to_another_site(game):
    """``next`` is attacker-supplied: only same-site paths are honoured."""
    app, _pw, _p = game
    for bad in ("//evil.example.com/", "https://evil.example.com/",
                "/\\evil.example.com/", "/no/such/route"):
        c = app.test_client()
        r = c.post("/login?next=" + bad, data={"username": "admin",
                                               "password": "admin-pw"})
        assert r.headers["Location"].endswith("/admin"), bad


def test_a_team_only_ever_sees_its_own_results(game):
    """There is no route that takes a team id - identity comes from the session."""
    app, pw, path = game
    con = db.connect(path)
    db.set_game(con, open_round=1)
    service.process_round(con)

    one = _client(app, "team_01", pw["team_01"])
    two = _client(app, "team_02", pw["team_02"])
    first = one.get("/results/1").data
    second = two.get("/results/1").data
    assert b"team_01" in first and b"team_02" not in first
    assert b"team_02" in second and b"team_01" not in second


def test_passwords_are_stored_hashed(game):
    _app, pw, path = game
    con = db.connect(path)
    stored = con.execute(
        "SELECT password_hash FROM account WHERE username = 'team_01'").fetchone()[0]
    assert pw["team_01"] not in stored
    assert stored.startswith(("pbkdf2:", "scrypt:"))


# --- Submission ------------------------------------------------------------------

def test_submission_needs_an_open_round(game):
    app, pw, _p = game
    team = _client(app, "team_01", pw["team_01"])
    r = team.get("/submit", follow_redirects=True)
    assert b"Submissions are closed" in r.data


def test_submit_revise_and_blank_means_default(game):
    app, pw, path = game
    con = db.connect(path)
    db.set_game(con, open_round=1)
    team = _client(app, "team_01", pw["team_01"])

    team.post("/submit", data={"3.1": "900000", "2.2": ""}, follow_redirects=True)
    saved = db.submission(con, 1, "team_01")
    assert saved["3.1"] == 900_000
    assert "2.2" not in saved, "a blank field must fall through to the default"

    team.post("/submit", data={"3.1": "500000"}, follow_redirects=True)
    assert db.submission(con, 1, "team_01")["3.1"] == 500_000, "revision must replace"


def test_implausible_values_are_refused(game):
    app, pw, path = game
    db.set_game(db.connect(path), open_round=1)
    team = _client(app, "team_01", pw["team_01"])
    for field, value, message in [
        ("2.2", "150%", b"between 0"),
        ("3.1", "-50000", b"cannot be negative"),
        ("3.1", "900000000", b"looks like a typo"),
        ("3.1", "lots", b"not a number"),
    ]:
        r = team.post("/submit", data={field: value}, follow_redirects=True)
        assert message in r.data, (field, value)


# --- The form a student actually reads -----------------------------------------------

def test_every_open_decision_explains_itself(game):
    """No lever reaches a student as a bare code with no explanation."""
    app, pw, path = game
    con = db.connect(path)
    db.set_game(con, open_round=1)
    team = _client(app, "team_01", pw["team_01"])
    page = team.get("/submit").data.decode()
    for spec in service.open_decisions(con, 1):
        assert spec.help, f"{spec.code} has no help text"
        assert escape(spec.name) in page, spec.code
        assert escape(spec.help[:40]) in page, f"{spec.code} help not rendered"


def test_choices_are_offered_by_name_not_by_code(game):
    """A team picks "Supplier C - 7-day lead time", never types "C"."""
    app, pw, path = game
    db.set_game(db.connect(path), open_round=1)
    team = _client(app, "team_01", pw["team_01"])
    page = team.get("/submit").data.decode()
    assert "Speed Express" in page, "courier names must appear"
    assert escape("Category Demand & Seasonality") in page, "study names must appear"
    assert "Facewash 100ml" in page, "product names must appear"
    assert "Cash on delivery" in page
    assert "MR-01;MR-17" not in page, "no raw-code placeholder anywhere"


def test_a_percentage_field_takes_a_percentage(game):
    """The field says %, so 15 means 15% - not 1500%."""
    app, pw, path = game
    con = db.connect(path)
    db.set_game(con, open_round=1)
    team = _client(app, "team_01", pw["team_01"])
    team.post("/submit", data={"2.2": "15"}, follow_redirects=True)
    assert db.submission(con, 1, "team_01")["2.2"] == pytest.approx(0.15)


def test_a_choice_outside_the_list_is_refused(game):
    app, pw, path = game
    db.set_game(db.connect(path), open_round=1)
    team = _client(app, "team_01", pw["team_01"])
    r = team.post("/submit", data={"9.1": "maybe"}, follow_redirects=True)
    assert b"not one of the choices" in r.data


def test_courier_mix_reaches_the_engine_as_a_mix(game):
    """It is a split across couriers, and the engine reads a split."""
    app, pw, path = game
    con = db.connect(path)
    db.set_game(con, open_round=1)
    team = _client(app, "team_01", pw["team_01"])
    team.post("/submit", data={"8.3__speed": "50", "8.3__value": "20",
                               "8.3__wide": "30"}, follow_redirects=True)
    saved = db.submission(con, 1, "team_01")["8.3"]
    assert saved == {"speed": 0.5, "value": 0.2, "wide": 0.3}


def test_a_courier_mix_that_does_not_add_up_is_refused(game):
    app, pw, path = game
    db.set_game(db.connect(path), open_round=1)
    team = _client(app, "team_01", pw["team_01"])
    r = team.post("/submit", data={"8.3__speed": "50", "8.3__value": "20",
                                   "8.3__wide": "10"}, follow_redirects=True)
    assert b"must add up to 100%" in r.data


def test_research_is_picked_from_the_list_with_its_price(game):
    app, pw, path = game
    con = db.connect(path)
    db.set_game(con, open_round=1)
    team = _client(app, "team_01", pw["team_01"])
    page = team.get("/submit").data.decode()
    assert "150,000" in page, "each study must show what it costs"
    team.post("/submit", data={"12.1": ["MR-01", "MR-03"]}, follow_redirects=True)
    assert db.submission(con, 1, "team_01")["12.1"] == ["MR-01", "MR-03"]


# --- Instructor control ------------------------------------------------------------

def test_instructor_can_open_a_decision_early(game):
    app, _pw, path = game
    con = db.connect(path)
    admin = _client(app, "admin", "admin-pw")
    assert "11.1" not in {s.code for s in service.open_decisions(con, 1)}

    admin.post("/admin/decisions", data={"round": 1, "open": ["11.1", "3.1"]},
               follow_redirects=True)
    codes = {s.code for s in service.open_decisions(con, 1)}
    assert "11.1" in codes, "an override must be able to unlock early"
    assert "2.2" not in codes, "and to hold something back"


def test_parameter_override_outside_its_band_is_refused(game):
    app, _pw, path = game
    admin = _client(app, "admin", "admin-pw")
    r = admin.post("/admin/params", data={"saturation_exponent": "0.99"},
                   follow_redirects=True)
    assert b"Refused" in r.data
    assert db.overrides(db.connect(path)) == {}


def test_ai_competitor_count_is_instructor_controlled(game):
    """The field is set next to the roster it has to balance, not in economics."""
    app, _pw, path = game
    admin = _client(app, "admin", "admin-pw")
    admin.post("/admin/teams",
               data={"action": "field", "ai_competitors": "5",
                     "ai_aggression": "0.7"}, follow_redirects=True)
    row = db.game(db.connect(path))
    assert row["ai_competitors"] == 5 and row["ai_aggression"] == 0.7


def test_rollback_keeps_submissions_so_a_round_can_be_rerun(game):
    app, pw, path = game
    con = db.connect(path)
    admin = _client(app, "admin", "admin-pw")

    for rnd in (1, 2):
        admin.post("/admin/open", data={"round": rnd})
        _client(app, "team_01", pw["team_01"]).post(
            "/submit", data={"3.1": "700000"}, follow_redirects=True)
        admin.post("/admin/run", follow_redirects=True)
    assert db.game(con)["round"] == 2

    admin.post("/admin/rollback", data={"to_round": 1}, follow_redirects=True)
    assert db.game(con)["round"] == 1
    assert db.submission(con, 2, "team_01") is not None, "submissions must survive"
    admin.post("/admin/run", follow_redirects=True)
    assert db.game(con)["round"] == 2


def test_teams_that_do_not_submit_keep_their_previous_decisions(game):
    app, pw, path = game
    con = db.connect(path)
    admin = _client(app, "admin", "admin-pw")
    admin.post("/admin/open", data={"round": 1})
    _client(app, "team_01", pw["team_01"]).post(
        "/submit", data={"3.1": "700000"}, follow_redirects=True)
    admin.post("/admin/run", follow_redirects=True)

    world = db.load_world(con)
    assert all(len(t.history) == 1 for t in world.teams.values()), \
        "a silent team is still played, not skipped"


# --- The escape hatch ---------------------------------------------------------------

def test_decisions_export_matches_the_file_runner_format(game):
    """If the app fails mid-class, this CSV runs the round offline."""
    app, pw, path = game
    db.set_game(db.connect(path), open_round=1)
    _client(app, "team_01", pw["team_01"]).post(
        "/submit", data={"3.1": "900000", "12.1": "MR-01;MR-17"},
        follow_redirects=True)

    csv_text = _client(app, "admin", "admin-pw").get("/admin/export/1.csv").data.decode()
    assert csv_text.splitlines()[0] == "team_id,decision,value"

    from ecomsim.io_csv import read_decisions
    out = path.parent / "d.csv"
    out.write_text(csv_text, encoding="utf-8")
    parsed = read_decisions(out)
    assert parsed["team_01"]["3.1"] == 900_000
    assert parsed["team_01"]["12.1"] == ["MR-01", "MR-17"]
