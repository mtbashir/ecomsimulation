"""Rules v2: relative profitability, decision quality, levers that keep their setting.

A game under way when the rules changed keeps its earlier months exactly as
published; the new rules apply from the month they start.
"""
import sys
sys.path.insert(0, "src")

import sqlite3

import pytest

from ecomsim import bootstrap, params as P, scoring, version
from ecomsim.engine import carry, run_round
from ecomsim.web import db, service

DEFAULT_META = 468_000


def _world(rules_from=1, n=3):
    params = P.load({"n_teams": n, "events_enabled": 0})
    world = bootstrap.new_world(params, run_id="v2")
    world.rules_from = rules_from
    return params, world, list(world.teams)


def test_a_lever_left_alone_keeps_last_months_setting():
    params, world, ids = _world(rules_from=1)
    run_round(world, params, {ids[0]: {"3.1": 100_000.0}})
    run_round(world, params, {})
    a, b = (world.teams[ids[0]].history[m]["pnl"]["marketing"] for m in (0, 1))
    assert a == pytest.approx(b), "month 2 kept month 1's Meta budget"


def test_before_the_rules_start_a_blank_lever_runs_on_its_default():
    params, world, ids = _world(rules_from=3)
    run_round(world, params, {ids[0]: {"3.1": 100_000.0}})
    run_round(world, params, {})
    a, b = (world.teams[ids[0]].history[m]["pnl"]["marketing"] for m in (0, 1))
    assert b - a == pytest.approx(DEFAULT_META - 100_000), "v1: back to the default"
    assert "rules" not in world.teams[ids[0]].history[1]


def test_repricing_one_line_keeps_the_others():
    merged = carry({"1.1": {"SKU-01": {"price": 999.0}, "SKU-02": {"discount": 0.1}}},
                   {"1.1": {"SKU-02": {"price": 1500.0}, "SKU-03": {"sourcing": "local"}}})
    assert merged["1.1"] == {"SKU-01": {"price": 999.0},
                             "SKU-02": {"discount": 0.1, "price": 1500.0},
                             "SKU-03": {"sourcing": "local"}}


def test_research_memo_stock_orders_and_investments_are_not_carried():
    merged = carry({"12.1": ["MR-01"], "12.5": "memo", "7.1": 5000, "11.1": True,
                    "3.1": 1.0}, {})
    assert merged == {"3.1": 1.0}


def test_decision_quality_marks():
    params, world, ids = _world(rules_from=1)
    team = world.teams[ids[0]]
    rec = {"round": 3, "rules": 2, "decisions": {"taken": 25, "open": 33, "memo": True}}
    assert scoring._decision_quality(team, rec, set()) == pytest.approx(10.0)
    rec["decisions"]["taken"] = 0
    assert scoring._decision_quality(team, rec, set()) == pytest.approx(2.0)
    rec["decisions"].update(taken=12, memo=False)
    assert scoring._decision_quality(team, rec, set()) == pytest.approx(8 * 12 / (0.75 * 33))
    rec["decisions"]["memo"] = True
    assert scoring._decision_quality(team, rec, {(team.team_id, 3)}) == pytest.approx(
        8 * 12 / (0.75 * 33)), "a memo the instructor rejected earns nothing"
    assert scoring._decision_quality(team, {"round": 1}, set()) == 5.0, "v1 months: 5"


def test_coasting_scores_nothing_on_decisions_and_acting_scores_well():
    params, world, ids = _world(rules_from=1)
    every = [c for c in __import__("ecomsim.decisions", fromlist=["REGISTRY"]).REGISTRY]
    for _ in range(2):
        run_round(world, params, {ids[0]: {"3.1": 500_000.0, "7.5": 3.0, "2.2": 0.0,
                                           "8.5": "basic", "9.1": "on", "12.5": "Hold course."},
                                  ids[1]: {}})
    acted, coasted = (scoring.final_score(world.teams[t], params, world.teams) for t in ids[:2])
    assert coasted["p6"] == pytest.approx(0.0)
    assert acted["p6"] > 4.0


def test_profitability_is_marked_against_the_best_team():
    params, world, ids = _world(rules_from=1)
    run_round(world, params, {ids[0]: {"2.2": 0.15}, ids[1]: {}, ids[2]: {}})
    cards = {t: scoring.final_score(world.teams[t], params, world.teams) for t in ids}
    margins = {t: world.teams[t].history[-1]["contribution_pre_marketing_pct"] for t in ids}
    best = max(margins, key=margins.get)
    worst = min(margins, key=margins.get)
    assert cards[best]["p1"] > cards[worst]["p1"]
    # the cm_pre measure scales with the margin against the best
    own = scoring._profit_relative(world.teams[worst], world.teams, [0])
    top = scoring._profit_relative(world.teams[best], world.teams, [0])
    assert own < top <= 25.0 + 1e-9


def test_months_before_the_switch_score_exactly_as_published():
    params, world, ids = _world(rules_from=3)
    run_round(world, params, {ids[0]: {"2.2": 0.1}})
    run_round(world, params, {})
    before = {t: scoring.final_score(world.teams[t], params, world.teams)["total"] for t in ids}
    run_round(world, params, {ids[0]: {"3.1": 300_000.0, "12.5": "Cut Meta."}})
    assert world.teams[ids[0]].history[2]["rules"] == 2
    import copy
    for t in ids:
        early = copy.copy(world.teams[t])
        early.history = world.teams[t].history[:2]
        assert scoring.final_score(early, params, world.teams)["total"] == pytest.approx(before[t])


# --- The live app ------------------------------------------------------------------

@pytest.fixture
def live(tmp_path):
    """A founding game whose first two months ran on rules v1."""
    from ecomsim import founding as F
    path = tmp_path / "g.db"
    pw = db.init(path, "Live", 3, rounds=12, admin_password="admin-pw")
    con = db.connect(path)
    db.set_game(con, rules_from=3)
    params = service.load_params(con)
    for i in (1, 2, 3):
        cfg = F.Founding.default(params)
        cfg.prices = {c: F.reference_price(params.sku(c), cfg.tier) for c in cfg.assortment}
        db.save_founding(con, f"team_{i:02d}", service.founding_to_dict(cfg), "sys", submitted=True)
    db.set_game(con, open_round=1)
    db.submit(con, 1, "team_01", {"3.1": 100_000.0}, "t")
    service.process_round(con)
    db.set_game(con, open_round=2)
    db.submit(con, 2, "team_01", {"3.1": 300_000.0}, "t")
    service.process_round(con)
    db.set_game(con, open_round=3)
    return path, pw, con


def test_month_three_keeps_what_ran_in_month_two(live):
    path, pw, con = live
    service.process_round(con)          # team_01 submits nothing for month 3
    h = db.load_world(con).teams["team_01"].history
    assert h[2]["pnl"]["marketing"] == pytest.approx(h[1]["pnl"]["marketing"])
    assert h[2]["rules"] == 2 and "rules" not in h[1]


def test_keep_tick_records_last_months_setting_as_a_decision(live):
    from ecomsim.web.app import create_app
    path, pw, con = live
    app = create_app(path)
    app.config["TESTING"] = True
    c = app.test_client()
    c.post("/login", data={"username": "team_01", "password": pw["team_01"]})
    c.post("/brief")
    page = c.get("/submit").data.decode()
    assert "Keep last month" in page and "decisions taken this month" in page
    # the form never tells a team how many decisions earn full marks
    assert "full decision marks" not in page and "counts as a decision" not in page
    c.post("/submit", data={"keep_3.1": "1"}, follow_redirects=True)
    assert db.submission(con, 3, "team_01")["3.1"] == pytest.approx(300_000.0)


def test_admin_sees_the_engine_version_and_rules(live):
    from ecomsim.web.app import create_app
    path, pw, con = live
    app = create_app(path)
    app.config["TESTING"] = True
    admin = app.test_client()
    admin.post("/login", data={"username": "admin", "password": "admin-pw"})
    page = admin.get("/admin").data.decode()
    assert f"Engine {version.ENGINE_VERSION}" in page
    assert "rules v2 from month 3; months 1–2 on v1" in page
    service.process_round(con)
    console = admin.get("/admin/console/3").data.decode()
    assert f"Engine {version.ENGINE_VERSION}" in console
    assert "Decision quality this month" in console


def test_memo_verdict_moves_the_score(live):
    from ecomsim.web.app import create_app
    path, pw, con = live
    db.submit(con, 3, "team_01", {"12.5": "We cut Meta to fund stock."}, "t")
    service.process_round(con)
    params = service.load_params(con)
    world = db.load_world(con)
    before = scoring.final_score(world.teams["team_01"], params, world.teams,
                                 db.memo_rejected(con))["p6"]
    app = create_app(path)
    app.config["TESTING"] = True
    admin = app.test_client()
    admin.post("/login", data={"username": "admin", "password": "admin-pw"})
    admin.post("/admin/memo/3/team_01", data={"ok": "0"})
    after = scoring.final_score(world.teams["team_01"], params, world.teams,
                                db.memo_rejected(con))["p6"]
    assert before - after == pytest.approx(2.0 * 3 / 6), "2 memo points, month 3's weight"


def test_an_existing_game_switches_from_its_next_month(tmp_path):
    path = tmp_path / "old.db"
    con = sqlite3.connect(path)
    con.executescript(db.SCHEMA.replace("CREATE TABLE IF NOT EXISTS memo_review", "CREATE TABLE IF NOT EXISTS _x")
                      .split("CREATE TABLE IF NOT EXISTS account")[0])
    con.execute("INSERT INTO game (id, name, round, created_at) VALUES (1, 'old', 2, 'now')")
    con.commit()
    con.close()
    con = db.connect(path)
    with con:
        db.migrate(con)
    assert db.rules_from(con) == 3
    path2 = tmp_path / "new.db"
    db.init(path2, "new", 2)
    assert db.rules_from(db.connect(path2)) == 1
