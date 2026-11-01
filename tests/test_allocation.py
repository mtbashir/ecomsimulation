"""How the market's orders were shared: the instructor's allocation workbook.

The engine records what M7 and M8 read while it runs, and the console rebuilds
a month from the saved game. What must hold: the record adds up to the orders
the engine gave, recording it changes nothing, and a rebuilt month is the
month that was played.
"""
from __future__ import annotations

import io
import math

import openpyxl
import pytest

from ecomsim import allocation, bootstrap, engine, params as P
from ecomsim.modules import m07_share
from ecomsim.web import db, service
from ecomsim.web.app import create_app


def _month(submissions=None):
    params = P.load({"n_teams": 4})
    world = bootstrap.new_world(params, n_teams=4, run_id="alloc", ai_competitors=2)
    ctx = engine.run_round(world, params, submissions or {})
    return world, params, ctx


def test_the_record_adds_up_to_the_orders_the_engine_gave():
    world, params, ctx = _month({"team_01": {"2.2": 0.10}, "team_02": {"3.9": 700_000}})
    rec = allocation.capture(world, params, ctx)
    mk = rec["market"]
    # Every segment's orders go somewhere: to the teams or the AI competitors.
    for code, pool in mk["pools"].items():
        taken = (sum(x["won"][code] for x in rec["teams"].values())
                 + sum(a["won"][code] for a in mk["ai"]))
        assert taken == pytest.approx(pool)
    assert sum(mk["pools"].values()) == pytest.approx(mk["orders"])
    for tid, x in rec["teams"].items():
        assert x["contested"] + x["repeat"] == pytest.approx(x["potential"])
        assert x["own"] == pytest.approx(min(x["potential"], x["traffic_capacity"],
                                             x["stock_capacity"] or math.inf))
        assert x["own"] + x["reoffered"] + x["marketplace"] == pytest.approx(x["orders"])
        assert x["orders"] == world.teams[tid].history[-1]["orders"]
        cr = x["cr"]
        product = math.prod(cr[k] for k, _ in allocation.CR_PARTS)
        assert product == pytest.approx(x["conversion_rate"])


def test_utility_parts_add_up_to_the_utility_the_engine_used():
    world, params, ctx = _month({"team_01": {"2.2": 0.20}})
    sd = ctx["share_detail"]
    for tid, parts in sd["parts"].items():
        for code, terms in parts.items():
            assert sum(terms.values()) == pytest.approx(sd["utility"][tid][code], abs=1e-12)


def test_recording_the_detail_changes_nothing():
    """The share is the logit over utilities times focus, exactly as before."""
    world, params, ctx = _month({"team_03": {"3.1": 900_000}})
    sd = ctx["share_detail"]
    for code, pool in sd["pools"].items():
        weights = {tid: math.exp(sd["beta"] * u[code]) * sd["focus"][tid][code]
                   for tid, u in sd["utility"].items()}
        total = sum(weights.values())
        for tid, w in weights.items():
            assert sd["won"][tid][code] == pytest.approx(pool * w / total)
    assert m07_share.utility_parts       # the reporting helper stays public


@pytest.fixture
def played(tmp_path):
    path = tmp_path / "g.db"
    db.init(path, "Allocation", 3, rounds=12, admin_password="admin-pw")
    con = db.connect(path)
    for m in (1, 2, 3):
        db.submit(con, m, "team_01", {"2.2": "0.1", "12.6": "10000000"}, "t")
        db.submit(con, m, "team_02", {"3.9": "600000", "5.1": "400000", "12.6": "10000000"}, "t")
        db.submit(con, m, "team_03", {"9.1": "off", "12.6": "10000000"}, "t")
        service.process_round(con)
    return path, con


def test_a_rebuilt_month_is_the_month_that_was_played(played):
    _, con = played
    months, checks = service.allocation_months(con)
    assert [m["market"]["month"] for m in months] == [1, 2, 3]
    assert all(ok for ok, _ in checks.values()), checks
    saved = db.load_world(con, 3)
    for tid, x in months[2]["teams"].items():
        assert x["orders"] == pytest.approx(saved.teams[tid].history[2]["orders"])


def test_rebuilding_a_month_writes_nothing(played):
    _, con = played
    before = [bytes(r["world_blob"]) for r in con.execute("SELECT world_blob FROM round_log")]
    service.allocation_months(con)
    after = [bytes(r["world_blob"]) for r in con.execute("SELECT world_blob FROM round_log")]
    assert before == after
    assert db.game(con)["round"] == 3


def test_the_workbook_goes_from_decisions_to_orders(played):
    _, con = played
    data, name = service.allocation_workbook(con)
    assert name == "order_allocation_months_1-3.xlsx"
    book = openpyxl.load_workbook(io.BytesIO(data))
    assert book.sheetnames[:5] == ["Read me", "Market", "Orders by team", "Attractiveness",
                                   "Conversion"]
    assert len(book.sheetnames) == 5 + 3          # one sheet per team
    market = book["Market"]
    assert market.cell(2, 1).value == 1 and market.cell(4, 1).value == 3
    assert market.cell(2, market.max_column).value == "Yes"
    team = book[book.sheetnames[5]]
    first = [team.cell(r, 1).value for r in range(1, team.max_row + 1)]
    for group in ("1 · Decisions that ran", "2 · Factors the engine read (M5, M6, M7, M8)",
                  "5 · Orders (M8)"):
        assert group in first
    assert first.index("1 · Decisions that ran") < first.index("Orders")


def test_the_console_shows_the_month_and_links_the_workbook(played):
    path, _ = played
    app = create_app(path)
    app.config["TESTING"] = True
    c = app.test_client()
    c.post("/login", data={"username": "admin", "password": "admin-pw"})
    page = c.get("/admin/console/2").get_data(as_text=True)
    assert "Orders Were Shared" in page
    assert "/admin/allocation/2.xlsx" in page
    r = c.get("/admin/allocation/2.xlsx")
    assert r.status_code == 200
    assert r.headers["Content-Disposition"].endswith('order_allocation_months_1-2.xlsx"')
    assert "/admin/allocation/3.xlsx" in c.get("/admin").get_data(as_text=True)


def test_a_team_cannot_download_the_allocation(played):
    path, con = played
    app = create_app(path)
    app.config["TESTING"] = True
    c = app.test_client()
    pw = "team-pw"
    db.set_password(con, "team_01", pw)
    c.post("/login", data={"username": "team_01", "password": pw})
    r = c.get("/admin/allocation/3.xlsx")
    assert r.status_code in (302, 403)


def test_an_ai_entrant_mid_game_does_not_shift_the_market_columns(played):
    import copy
    _, con = played
    months, checks = service.allocation_months(con)
    late = copy.deepcopy(months[2])
    late["market"]["ai"].append({"id": "entrant", "name": "Funded entrant", "utility": 0.58,
                                 "won": {}, "total": 123.0})
    data = allocation.build(months[:2] + [late], {}, lambda c, v: "", checks)
    ws = openpyxl.load_workbook(io.BytesIO(data))["Market"]
    head = [c.value for c in ws[1]]
    assert "Won by Funded entrant" in head
    assert ws.cell(4, head.index("Won by Funded entrant") + 1).value == 123.0
    assert ws.cell(2, head.index("Won by Funded entrant") + 1).value is None
    assert ws.cell(4, len(head)).value == "Yes"        # the check stays in its column


def test_the_check_tells_a_marketplace_change_from_a_store_change(played):
    import copy
    _, con = played
    record, (ok, _) = service.replay_month(con, 2)
    assert ok
    after = db.load_world(con, 2)
    mp = copy.deepcopy(record)
    x = mp["teams"]["team_01"]
    x["marketplace"] += 100.0
    x["orders"] += 100.0
    ok, note = service._matches(mp, after, 2, {})
    assert not ok and note.startswith("On the store, yes")
    store = copy.deepcopy(record)
    store["teams"]["team_02"]["potential"] *= 1.2
    ok, note = service._matches(store, after, 2, {"team_02": "Team 2 · Brand"})
    assert not ok and "Team 2 · Brand, demand" in note
