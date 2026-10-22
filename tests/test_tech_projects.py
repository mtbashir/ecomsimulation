"""Technology builds: what went live, what is building, what failed - shown to
the team - and dynamic pricing (11.3) withdrawn, with what was paid refunded."""
from __future__ import annotations

import pytest

from ecomsim.modules.m04_capability import PROJECTS
from ecomsim.web import db, service
from ecomsim.web.app import create_app

AI = {"11.1": True, "11.2": True, "11.4": True, "11.5": True}


@pytest.fixture
def game(tmp_path):
    path = tmp_path / "g.db"
    pw = db.init(path, "G", 6, rounds=12, admin_password="admin-pw", start_mode="going_concern")
    con = db.connect(path)
    return con, path, pw


def _run(con, month, plans=None):
    db.set_game(con, open_round=month)
    for tid, d in (plans or {}).items():
        db.submit(con, month, tid, d, tid)
    service.process_round(con)


def _all_build(con, months=5):
    teams = [f"team_{i:02d}" for i in range(1, 7)]
    for m in range(1, months + 1):
        _run(con, m, {t: {**AI, "12.6": 20_000_000.0} for t in teams} if m == 3 else
             {t: {"12.6": 20_000_000.0} for t in teams})


def test_every_build_ends_as_the_engine_left_it(game):
    con, _, _ = game
    _all_build(con)
    world = db.load_world(con)
    timeline = service.project_timeline(con)
    outcomes = [b["outcome"] for bs in timeline.values() for b in bs]
    assert len(outcomes) == 6 * 4 and "failed" in outcomes and "live" in outcomes
    for tid, builds in timeline.items():
        team = world.teams[tid]
        for b in builds:
            assert b["started"] == 3 and b["capex"] == PROJECTS[b["code"]]["capex"]
            if b["outcome"] == "live":
                assert b["code"] in team.capabilities
                assert b["month"] == 3 + PROJECTS[b["code"]]["lead"]
            elif b["outcome"] == "failed":
                assert b["code"] not in team.capabilities
                assert not any(p["code"] == b["code"] for p in team.projects)


def test_a_failed_build_is_shown_on_the_form_and_in_the_report(game):
    con, path, pw = game
    _all_build(con)
    timeline = service.project_timeline(con)
    tid, failed = next((t, b) for t, bs in timeline.items() for b in bs if b["outcome"] == "failed")
    status = service.ai_status(con, tid)[failed["decision"]]
    assert status.startswith(f"Failed in month {failed['month']}") and "not refunded" in status
    assert "Yes builds it" in status
    db.set_game(con, open_round=6)
    app = create_app(path)
    app.config["TESTING"] = True
    c = app.test_client()
    c.post("/login", data={"username": tid, "password": pw[tid]})
    c.post("/brief")
    page = c.get("/submit").get_data(as_text=True)
    assert f"Failed in month {failed['month']}" in page
    report = c.get("/results/5").get_data(as_text=True)
    assert "technology projects, to month 5" in report.lower()
    assert "the build did not work" in report
    admin = app.test_client()
    admin.post("/login", data={"username": "admin", "password": "admin-pw"})
    assert "technology projects" in admin.get("/admin/console/5").get_data(as_text=True).lower()


def test_building_and_live_say_so(game):
    con, _, _ = game
    _all_build(con, months=3)
    tid = "team_01"
    status = service.ai_status(con, tid)
    assert status["11.1"].startswith("Building: started month 3")       # 2-month build
    for code, b in ((b["decision"], b) for b in service.project_timeline(con)[tid]):
        if b["outcome"] == "live":
            assert status[code].startswith("Yours: live since month")


def test_dynamic_pricing_is_never_open_and_never_built(game):
    con, _, _ = game
    db.set_window(con, "11.3", 3, True)          # even opened by hand
    assert "11.3" not in {s.code for s in service.open_decisions(con, 3)}
    _run(con, 1); _run(con, 2)
    _run(con, 3, {"team_01": {"11.3": True, "12.6": 20_000_000.0}})
    assert not service.project_timeline(con).get("team_01")
    assert "11.3" not in service.ai_status(con, "team_01")


def test_what_was_paid_for_dynamic_pricing_is_refunded_once(game):
    con, _, _ = game
    for m in (1, 2, 3):
        _run(con, m)
    # A game that bought it before it was withdrawn: team_01 paid for a build
    # in month 3; team_02's earlier build went live in month 2 and ran 2 months.
    for m in (1, 2, 3):
        world = db.load_world(con, m)
        world.__dict__.pop("withdrawn_refunded", None)     # saved before the withdrawal
        if m == 1:
            db.save_round(con, m, world, "x")
            continue
        world.teams["team_02"].capabilities.add("dyn_pricing")
        if m == 3:
            world.teams["team_01"].projects.append(
                {"code": "dyn_pricing", "started": 3, "completes": 6, "capex": 3_800_000})
        db.save_round(con, m, world, "x")
    _run(con, 4)
    world = db.load_world(con)
    h1 = world.teams["team_01"].history[-1]["cash_flow"]
    h2 = world.teams["team_02"].history[-1]["cash_flow"]
    assert h1["tech_refund"] == pytest.approx(3_800_000)
    assert h2["tech_refund"] == pytest.approx(2 * PROJECTS["dyn_pricing"]["ongoing"])
    assert world.teams["team_03"].history[-1]["cash_flow"]["tech_refund"] == 0
    assert "dyn_pricing" not in world.teams["team_02"].capabilities
    assert not any(p["code"] == "dyn_pricing" for p in world.teams["team_01"].projects)
    outcome = {b["code"]: b["outcome"] for b in service.project_timeline(con)["team_01"]}
    assert outcome["dyn_pricing"] == "withdrawn"
    _run(con, 5)
    assert db.load_world(con).teams["team_01"].history[-1]["cash_flow"]["tech_refund"] == 0


def test_a_failed_build_of_a_withdrawn_lever_counts_as_refunded(game):
    con, _, _ = game
    for m in (1, 2, 3):
        _run(con, m)
    for m in (1, 2, 3):
        world = db.load_world(con, m)
        world.__dict__.pop("withdrawn_refunded", None)
        if m == 2:      # a build started in month 2 that failed in month 3
            world.teams["team_01"].projects.append(
                {"code": "dyn_pricing", "started": 2, "completes": 3, "capex": 3_800_000})
        db.save_round(con, m, world, "x")
    _run(con, 4)
    (b,) = [b for b in service.project_timeline(con)["team_01"] if b["code"] == "dyn_pricing"]
    assert b["outcome"] == "failed" and b["month"] == 3 and b["refunded"] == 4
    world = db.load_world(con)
    assert world.teams["team_01"].history[-1]["cash_flow"]["tech_refund"] == pytest.approx(3_800_000)
