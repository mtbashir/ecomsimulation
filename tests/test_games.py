"""Past games: a new cohort starts without losing the last one.

The database holds one game, so starting another used to mean deleting the
file. Now the whole game is saved to an archive first, and stays readable -
standings, reports, consoles and decision files - from the Games page.
"""
from __future__ import annotations

import pytest

from ecomsim.web import db, service
from ecomsim.web.app import create_app


@pytest.fixture
def game(tmp_path):
    path = tmp_path / "g.db"
    passwords = db.init(path, "Autumn cohort", 3, rounds=12,
                        admin_password="admin-pw")
    app = create_app(path)
    app.config["TESTING"] = True
    return app, passwords, path


def _login(app, user, pw):
    c = app.test_client()
    c.post("/login", data={"username": user, "password": pw})
    return c


def _new_game(c, **over):
    data = {"name": "Spring cohort", "teams": "4", "rounds": "10",
            "start_mode": "founding", "keep_overrides": "1",
            "confirm": "NEW GAME"}
    data.update(over)
    return c.post("/admin/games/new", data=data)


def _run_round(path):
    con = db.connect(path)
    try:
        service.process_round(con)
    finally:
        con.close()


def test_a_new_game_saves_the_old_one_and_starts_fresh(game):
    app, pw, path = game
    _run_round(path)
    admin = _login(app, "admin", "admin-pw")

    r = _new_game(admin)
    assert r.status_code == 302 and r.location.endswith("/admin/teams")

    con = db.connect(path)
    g = db.game(con)
    assert (g["name"], g["round"], g["total_rounds"]) == ("Spring cohort", 0, 10)
    assert len(db.accounts(con, "team")) == 4
    assert db.load_world(con) is None
    # The new teams' passwords wait on the Teams page, as on first boot.
    assert all(a["initial_password"] for a in db.accounts(con, "team"))
    con.close()

    past = db.archives(path)
    assert len(past) == 1
    assert (past[0]["name"], past[0]["round"], past[0]["teams"]) == \
        ("Autumn cohort", 1, 3)


def test_the_instructor_stays_signed_in_and_keeps_their_password(game):
    app, _pw, _path = game
    admin = _login(app, "admin", "admin-pw")
    _new_game(admin)
    assert admin.get("/admin").status_code == 200
    assert _login(app, "admin", "admin-pw").get("/admin").status_code == 200


def test_last_terms_teams_are_signed_out_of_the_new_game(game):
    app, pw, _path = game
    student = _login(app, "team_01", pw["team_01"])
    assert student.get("/brief").status_code == 200

    _new_game(_login(app, "admin", "admin-pw"))
    r = student.get("/brief")
    assert r.status_code == 302 and "/login" in r.location
    # And the old password does not open the new team_01.
    assert _login(app, "team_01", pw["team_01"]).get("/brief").status_code == 302


def test_a_sign_in_from_before_this_feature_survives_the_deploy(game):
    app, pw, _path = game
    c = app.test_client()
    with c.session_transaction() as s:
        s.update(user="team_01", role="team", team_id="team_01", name="Team 1")
    assert c.get("/brief").status_code == 200


def test_nothing_happens_without_the_confirmation(game):
    app, _pw, path = game
    admin = _login(app, "admin", "admin-pw")
    for bad in ({"confirm": ""}, {"name": ""}, {"teams": "1"},
                {"rounds": "0"}, {"start_mode": "bogus"}, {"teams": "x"}):
        _new_game(admin, **bad)
    assert db.archives(path) == []
    con = db.connect(path)
    assert db.game(con)["name"] == "Autumn cohort"
    con.close()


def test_parameter_changes_carry_over_only_if_asked(game):
    app, _pw, path = game
    con = db.connect(path)
    db.set_overrides(con, {"aov_base": 2500.0})
    con.close()
    admin = _login(app, "admin", "admin-pw")

    _new_game(admin)
    con = db.connect(path)
    assert db.overrides(con) == {"aov_base": 2500.0}
    con.close()

    _new_game(admin, name="Summer", keep_overrides="")
    con = db.connect(path)
    assert db.overrides(con) == {}
    con.close()
    assert [p["name"] for p in db.archives(path)] == ["Spring cohort",
                                                       "Autumn cohort"]


def test_a_past_game_stays_readable(game):
    app, _pw, path = game
    _run_round(path)
    _run_round(path)
    admin = _login(app, "admin", "admin-pw")
    _new_game(admin)
    gid = db.archives(path)[0]["id"]

    page = admin.get(f"/admin/games/{gid}").get_data(as_text=True)
    assert "Autumn cohort" in page and "Final standings" in page
    assert page.count("report</a>") == 3

    assert admin.get(f"/admin/games/{gid}/console/2").status_code == 200
    assert admin.get(f"/admin/games/{gid}/report/team_01/2").status_code == 200
    csv = admin.get(f"/admin/games/{gid}/export/1.csv")
    assert csv.status_code == 200 and csv.data.startswith(b"team_id,")
    dl = admin.get(f"/admin/games/{gid}/download")
    assert dl.status_code == 200 and dl.data.startswith(b"SQLite format 3")

    listing = admin.get("/admin/games").get_data(as_text=True)
    assert "Autumn cohort" in listing and "2 / 12" in listing


def test_the_archive_is_a_faithful_read_only_copy(game):
    app, _pw, path = game
    _run_round(path)
    _new_game(_login(app, "admin", "admin-pw"))
    con = db.connect_archive(db.archives(path)[0]["path"])
    assert db.game(con)["round"] == 1
    assert db.load_world(con) is not None
    with pytest.raises(Exception):
        con.execute("DELETE FROM round_log")
    con.close()


def test_only_real_archives_can_be_opened(game):
    app, _pw, _path = game
    admin = _login(app, "admin", "admin-pw")
    for bad in ("nope", "..%2Fg", "game-x"):
        assert admin.get(f"/admin/games/{bad}").status_code == 404
        assert admin.get(f"/admin/games/{bad}/download").status_code == 404


def test_games_are_for_the_instructor_only(game):
    app, pw, _path = game
    student = _login(app, "team_01", pw["team_01"])
    assert student.get("/admin/games").status_code == 403
    assert _new_game(student).status_code == 403
