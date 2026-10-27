"""Every page names a team the same way: its number and its brand."""
from __future__ import annotations

import pytest

from ecomsim import naming
from ecomsim.web import db, service
from ecomsim.web.app import create_app

LABEL = "Team 1 · Tarz".encode()


def test_a_label_is_the_team_number_and_its_brand():
    assert naming.number("team_03") == "Team 3"
    assert naming.label("team_03", "MUSE") == "Team 3 · MUSE"
    assert naming.label("team_12") == "Team 12"
    assert naming.label("team_03", "") == "Team 3"
    assert naming.label("team_03", "Unnamed") == "Team 3", "the founding default is no brand"


@pytest.fixture
def played(tmp_path):
    """A month played by a team that typed a team name and chose a brand."""
    path = tmp_path / "g.db"
    pw = db.init(path, "Test", 3, rounds=12, admin_password="admin-pw")
    con = db.connect(path)
    with con:   # a team name typed before names were settled (no log line)
        con.execute("UPDATE account SET display_name = 'Legends' WHERE team_id = 'team_01'")
    db.set_identity(con, "team_01", {"brand_name": "Tarz"})
    db.mark_briefing_seen(con, "team_01")
    db.set_game(con, open_round=1)
    service.process_round(con)
    app = create_app(path)
    app.config["TESTING"] = True
    return app, pw, con


def _client(app, username, password):
    c = app.test_client()
    c.post("/login", data={"username": username, "password": password})
    return c


def test_the_instructor_sees_the_number_and_the_brand_never_the_team_name(played):
    app, _pw, _con = played
    admin = _client(app, "admin", "admin-pw")
    for page in ("/admin", "/admin/teams", "/admin/console/1", "/admin/report/team_01/1"):
        html = admin.get(page).data
        assert LABEL in html, page
        assert b"Legends" not in html, page
    strategy = admin.get("/admin/strategy").data
    assert b"Team 1" in strategy and b"Tarz" in strategy and b"Legends" not in strategy


def test_a_team_sees_itself_the_same_way(played):
    app, pw, _con = played
    team = _client(app, "team_01", pw["team_01"])
    for page in ("/", "/results/1", "/company", "/brief"):
        html = team.get(page).data
        assert LABEL in html, page
        assert b"Legends" not in html, page


def test_the_workbook_is_named_by_number_and_brand(played):
    _app, _pw, con = played
    _data, filename = service.team_workbook(con, "team_01", 1)
    assert filename == "Team_1_Tarz_month_1.xlsx"


def test_a_team_without_a_brand_is_its_number(played):
    _app, _pw, con = played
    assert service.team_labels(con)["team_02"] == "Team 2"
