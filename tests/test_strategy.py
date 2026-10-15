"""The strategy grid: who chose what, at a glance.

Options run down the page, teams across it, "Yes" where a team picked the
option. The instructor should be able to read the shape of the field - who
went premium, who is alone on the marketplace - without opening a report.
"""
from __future__ import annotations

import re

import pytest

from ecomsim import founding as F
from ecomsim.web import compare, db, service
from ecomsim.web.app import create_app


@pytest.fixture
def game(tmp_path):
    path = tmp_path / "g.db"
    db.init(path, "Test", 3, rounds=12, admin_password="admin-pw")
    app = create_app(path)
    app.config["TESTING"] = True
    con = db.connect(path)
    params = service.load_params(con)
    for tid, tier, model, statement in [
            ("team_01", "premium", "d2c", "Clean beauty for the city"),
            ("team_02", "value", "marketplace_first", "Everyday prices, every day"),
    ]:
        f = F.Founding.default(params)
        f.brand_name, f.tier, f.model = f"Brand {tid[-1]}", tier, model
        f.positioning_statement = statement
        db.save_founding(con, tid, service.founding_to_dict(f), tid,
                         submitted=True)
    con.close()
    admin = app.test_client()
    admin.post("/login", data={"username": "admin", "password": "admin-pw"})
    return app, path, admin


def _row(page: str, label: str) -> list[str]:
    """The cells of the grid row whose option label is `label`."""
    m = re.search(r'<tr class="[^"]*"><td class="opt">' + re.escape(label)
                  + r'</td>(.*?)</tr>', page, re.S)
    assert m, f"no row {label!r}"
    cells = re.findall(r'<td class="(yes|c|v|n)"[^>]*>(.*?)</td>', m.group(1), re.S)
    return ["Yes" if k == "yes" else re.sub(r"<[^>]+>", "", v).strip()
            for k, v in cells]


def _months(page: str) -> str:
    """Only the month section: founding has a gateway row with the same labels."""
    return page.split("<h2>Month decisions</h2>", 1)[1]


def test_each_option_is_a_row_and_each_team_a_column(game):
    _app, _path, admin = game
    page = admin.get("/admin/strategy").get_data(as_text=True)
    assert "Brand 1" in page and "Brand 2" in page
    # Premium, value, mainstream - one row each, Yes under whoever chose it.
    assert _row(page, "Premium") == ["Yes", "–", "–", "1"]
    assert _row(page, "Value") == ["–", "Yes", "–", "1"]
    assert _row(page, "Mainstream")[:3] == ["–", "–", "–"]


def test_every_positioning_statement_gets_its_own_row(game):
    _app, _path, admin = game
    page = admin.get("/admin/strategy").get_data(as_text=True)
    assert _row(page, "Clean beauty for the city")[:3] == ["Yes", "–", "–"]
    assert _row(page, "Everyday prices, every day")[:3] == ["–", "Yes", "–"]


def test_a_team_that_has_not_chosen_is_shown_as_not_set(game):
    _app, _path, admin = game
    page = admin.get("/admin/strategy").get_data(as_text=True)
    assert "Not set" in page


def test_month_decisions_show_what_is_in_force(game):
    _app, path, admin = game
    con = db.connect(path)
    db.submit(con, 1, "team_01", {"9.3": "C", "3.1": 250000}, "team_01")
    db.submit(con, 1, "team_02", {"9.3": "B"}, "team_02")
    # Month 2: team_02 changes its gateway, team_01 does not resubmit.
    db.submit(con, 2, "team_02", {"9.3": "A"}, "team_02")
    db.set_game(con, round=1, open_round=2)
    con.close()

    page = _months(admin.get("/admin/strategy?month=2").get_data(as_text=True))
    assert _row(page, "Gateway C - most reliable")[:3] == ["Yes", "–", "–"]
    assert _row(page, "Gateway A - balanced")[:3] == ["–", "Yes", "–"]

    month1 = _months(admin.get("/admin/strategy?month=1").get_data(as_text=True))
    assert _row(month1, "Gateway B - cheapest")[:3] == ["–", "Yes", "–"]
    assert "PKR 250,000" in month1


def test_in_force_takes_the_latest_submission_up_to_the_month(game):
    _app, path, _admin = game
    con = db.connect(path)
    db.submit(con, 1, "team_01", {"2.2": 0.05}, "team_01")
    db.submit(con, 3, "team_01", {"2.2": 0.10}, "team_01")
    held = compare.in_force(con, ["team_01"], 2)
    assert held["team_01"]["2.2"] == 0.05
    assert compare.in_force(con, ["team_01"], 3)["team_01"]["2.2"] == 0.10
    con.close()


def test_a_nonsense_month_does_not_break_the_page(game):
    _app, _path, admin = game
    for m in ("x", "-4", "999"):
        assert admin.get(f"/admin/strategy?month={m}").status_code == 200


def test_the_grid_is_for_the_instructor_only(game):
    app, _path, _admin = game
    pw = db.connect(_path)
    db.set_password(pw, "team_01", "secret-1")
    pw.close()
    team = app.test_client()
    team.post("/login", data={"username": "team_01", "password": "secret-1"})
    assert team.get("/admin/strategy").status_code == 403
