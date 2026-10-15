"""Preview: the next month's console, run on a copy, nothing saved."""
from __future__ import annotations

import re

import pytest

from ecomsim.web import db, service
from ecomsim.web.app import create_app


@pytest.fixture
def game(tmp_path):
    path = tmp_path / "g.db"
    db.init(path, "G", 4, rounds=12, admin_password="admin-pw", start_mode="going_concern")
    con = db.connect(path)
    for m in (1, 2):
        db.set_game(con, open_round=m)
        service.process_round(con)
    db.set_game(con, open_round=3)
    db.submit(con, 3, "team_01", {"3.1": 400000, "2.2": 0.1}, "team_01")
    app = create_app(path)
    app.config["TESTING"] = True
    admin = app.test_client()
    admin.post("/login", data={"username": "admin", "password": "admin-pw"})
    return con, admin


def _leaderboard(html: str) -> list[str]:
    block = html.split("Leaderboard", 1)[1].split("</section>", 1)[0]
    return re.findall(r"(\d+\.\d)", block)[:8]


def test_a_preview_saves_nothing(game):
    con, admin = game
    audit_before = len(db.audit(con, 500))
    r = admin.get("/admin/preview")
    assert r.status_code == 200
    page = r.get_data(as_text=True)
    assert "Preview of month 3" in page and "nothing has been saved" in page
    g = db.game(con)
    assert g["round"] == 2 and g["open_round"] == 3
    assert db.load_world(con, 3) is None
    assert len(db.audit(con, 500)) == audit_before


def test_the_preview_is_what_run_then_produces(game):
    con, admin = game
    preview = admin.get("/admin/preview").get_data(as_text=True)
    service.process_round(con)
    actual = admin.get("/admin/console/3").get_data(as_text=True)
    assert _leaderboard(preview) == _leaderboard(actual) != []


def test_the_overview_offers_it_and_teams_cannot(game):
    con, admin = game
    assert "/admin/preview" in admin.get("/admin").get_data(as_text=True)
    db.set_password(con, "team_01", "secret-1")
    team = admin.application.test_client()
    team.post("/login", data={"username": "team_01", "password": "secret-1"})
    assert team.get("/admin/preview").status_code == 403
