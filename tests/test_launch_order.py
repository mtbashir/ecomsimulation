"""A founded team opens with its own launch order, not the going-concern pipeline."""
import io
import sqlite3
import sys
sys.path.insert(0, "src")

import pytest

from ecomsim import bootstrap, founding as F, params as P
from ecomsim.engine import run_round
from ecomsim.web import db, service

PARAMS = P.load({"n_teams": 2, "events_enabled": 0})
MONTH_UNITS = (PARAMS["baseline_team_revenue"] / PARAMS["aov_base"]
               * PARAMS["units_per_order"])


def _founded(launch_order=True, **kw):
    world = bootstrap.new_world(PARAMS, run_id="launch")
    f = F.Founding.default(PARAMS)
    for k, v in kw.items():
        setattr(f, k, v)
    for team in world.teams.values():
        F.apply(f, team, PARAMS, launch_order=launch_order)
    return world, f


def _off_range():
    """Homecare and baby: a range the catalogue's default order barely touches."""
    cats = ["homecare", "baby"]
    rng = [s["code"] for s in PARAMS.skus if s["category"] in cats]
    rng += [s["code"] for s in PARAMS.skus if s["code"] not in rng][:12 - len(rng)]
    return dict(categories=cats, assortment=rng)


def test_the_opening_is_the_teams_own_launch_order():
    world, f = _founded()
    team = next(iter(world.teams.values()))
    assert team.receivables == {} and team.cod_receivable == 0.0, "no COD for sales never made"
    (po,) = team.open_pos
    assert po["placed"] == 0 and po["arrives"] == 1 and po.get("launch")
    assert set(po["units"]) == set(f.assortment), "its own range, nothing else"
    assert sum(po["units"].values()) == pytest.approx(MONTH_UNITS)
    alloc, cost = F.launch_order(f, PARAMS)
    assert po["cost"] == pytest.approx(cost)
    assert sum(team.payables.values()) == pytest.approx(cost), "owed once"
    assert team.launch_order["cost"] == pytest.approx(cost)


def test_the_order_costs_what_the_engine_charges_when_it_sells():
    from ecomsim.modules.m03_supply import landed_index
    world, f = _founded(tier="premium")
    team = next(iter(world.teams.values()))
    b = next(s for s in PARAMS.suppliers if s["code"] == "B")
    expect = sum(u * float(PARAMS.sku(c)["unit_cost"]) * float(b["cost_index"])
                 * landed_index(team, c) * PARAMS["cogs_scale"]
                 for c, u in team.open_pos[0]["units"].items())
    assert team.open_pos[0]["cost"] == pytest.approx(expect)


def test_a_range_away_from_the_catalogue_gets_no_dead_stock():
    world, f = _founded(**_off_range())
    team = next(iter(world.teams.values()))
    for _ in range(2):
        run_round(world, PARAMS, {})
    assert all(c in f.assortment for c, u in team.inventory.items() if u > 0.5)


def test_month_one_trades_at_the_same_scale():
    """docs/05: founding choices change the shape of the business, not its size."""
    new, _ = _founded()
    old, _ = _founded(launch_order=False)
    run_round(new, PARAMS, {})
    run_round(old, PARAMS, {})
    for tid in new.teams:
        assert new.teams[tid].history[0]["orders"] == pytest.approx(
            old.teams[tid].history[0]["orders"], rel=1e-9)
    paid_new = new.teams[tid].history[0]["cash_flow"]["supplier_payments"]
    paid_old = old.teams[tid].history[0]["cash_flow"]["supplier_payments"]
    assert paid_new < 0.6 * paid_old, "month 1 pays only its own order's first instalment"


def test_a_game_already_trading_keeps_the_old_opening():
    world, _ = _founded(launch_order=False)
    team = next(iter(world.teams.values()))
    assert team.receivables and sum(team.payables.values()) > team.open_pos[0]["cost"]


# --- The app: which games get it -----------------------------------------------------

def _old_db(path, round_):
    con = sqlite3.connect(path)
    con.executescript(db.SCHEMA.split("CREATE TABLE IF NOT EXISTS account")[0])
    con.execute("INSERT INTO game (id, name, round, created_at) VALUES (1, 'old', ?, 'now')",
                (round_,))
    con.commit()
    con.close()
    con = db.connect(path)
    with con:
        db.migrate(con)
    return con


def test_migration_keeps_a_trading_game_on_its_opening(tmp_path):
    assert db.launch_order(_old_db(tmp_path / "a.db", 2)) is False
    assert db.launch_order(_old_db(tmp_path / "b.db", 0)) is True
    db.init(tmp_path / "c.db", "new", 2)
    assert db.launch_order(db.connect(tmp_path / "c.db")) is True


def test_a_new_game_resets_both_switches(tmp_path):
    path = tmp_path / "g.db"
    db.init(path, "Old cohort", 2)
    con = db.connect(path)
    db.set_game(con, round=4, rules_from=3, launch_order=0)
    db.new_game(con, path, "Next cohort", 2, 12, "founding", keep_overrides=False)
    assert db.rules_from(con) == 1, "the next cohort plays every month on the current rules"
    assert db.launch_order(con) is True
    assert db.range_changes(con) is True


def _founding_game(tmp_path, launch_order):
    path = tmp_path / "g.db"
    pw = db.init(path, "Cohort", 2, rounds=12, admin_password="admin-pw")
    con = db.connect(path)
    db.set_game(con, launch_order=int(launch_order))
    params = service.load_params(con)
    for i in (1, 2):
        cfg = F.Founding.default(params)
        cfg.prices = {c: F.reference_price(params.sku(c), cfg.tier) for c in cfg.assortment}
        db.save_founding(con, f"team_{i:02d}", service.founding_to_dict(cfg), "sys",
                         submitted=True)
    return path, pw, con


@pytest.mark.parametrize("launch", [True, False])
def test_the_first_month_runs_on_the_games_switch(tmp_path, launch):
    path, pw, con = _founding_game(tmp_path, launch)
    db.set_game(con, open_round=1)
    service.process_round(con)
    h = db.load_world(con).teams["team_01"].history[0]
    assert (h["cash_flow"]["receipts"] < h["pnl"]["net_revenue"]) is launch, \
        "only the old opening collects COD for sales made before month 1"
    start = service.first_world(con, service.load_params(con), db.game(con))
    assert bool(start.teams["team_01"].launch_order) is launch


def test_setup_page_and_workbook_show_the_launch_order(tmp_path):
    from ecomsim.web.app import create_app
    openpyxl = pytest.importorskip("openpyxl")
    path, pw, con = _founding_game(tmp_path, True)
    app = create_app(path)
    app.config["TESTING"] = True
    c = app.test_client()
    c.post("/login", data={"username": "team_01", "password": pw["team_01"]})
    c.post("/brief")
    page = c.get("/found").data.decode()
    assert "launch order" in page and f"{MONTH_UNITS:,.0f} units" in page
    db.set_game(con, open_round=1)
    service.process_round(con)
    data, _ = service.team_workbook(con, "team_01", 1)
    wb = openpyxl.load_workbook(io.BytesIO(data))
    notes = [r[0].value for r in wb["Cash"].iter_rows() if r[0].value]
    assert any(str(n).startswith("Also ordered at set-up: a launch order") for n in notes)


def test_a_trading_game_shows_no_launch_order(tmp_path):
    from ecomsim.web.app import create_app
    path, pw, con = _founding_game(tmp_path, False)
    app = create_app(path)
    app.config["TESTING"] = True
    c = app.test_client()
    c.post("/login", data={"username": "team_01", "password": pw["team_01"]})
    c.post("/brief")
    assert "launch order" not in c.get("/found").data.decode()
