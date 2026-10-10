"""Months recorded before the stock and cash detail: rebuilt exactly, never guessed."""
import copy
import io
import pickle
import sys
sys.path.insert(0, "src")

import pytest

from ecomsim import backfill, bootstrap, founding as F, params as P, workbook
from ecomsim.engine import run_round
from ecomsim.web import db, service

DETAIL = ("stock", "cash_flow")


def _played(months=4):
    """A founded game on rules v1, with the world saved at every month end."""
    params = P.load({"n_teams": 3, "events_enabled": 1})
    world = bootstrap.new_world(params, run_id="bf")
    world.rules_from = 99
    ids = list(world.teams)
    for i, t in enumerate(ids):
        f = F.Founding.default(params)
        f.prices = {c: F.reference_price(params.sku(c), f.tier) for c in f.assortment}
        if i == 1:
            f.sourcing_by_sku = {c: "local" for c in f.assortment}
        F.apply(f, world.teams[t], params)
    saved, subs = {0: copy.deepcopy(world)}, {}
    plans = [{ids[0]: {"7.1": {"SKU-03": 1500.0}, "7.2": "C", "11.1": True},
              ids[1]: {"7.1": 500.0, "7.2": "A", "3.1": 2_500_000.0}},
             {ids[0]: {"1.1": {"SKU-03": {"sourcing": "import"}}},
              ids[2]: {"7.1": 9000.0, "11.2": True}}] + [{}] * (months - 2)
    for m, plan in enumerate(plans, start=1):
        subs[m] = plan
        run_round(world, params, plan)
        saved[m] = pickle.loads(pickle.dumps(world))
    return params, world, saved, subs


def test_rebuilt_detail_is_what_the_engine_recorded():
    params, world, saved, subs = _played()
    bare = copy.deepcopy(world)
    for t in bare.teams.values():
        for h in t.history:
            for k in DETAIL:
                h.pop(k)
    assert backfill.fill(bare, saved, params, subs) == [1, 2, 3, 4]
    for tid, team in world.teams.items():
        for a, b in zip(team.history, bare.teams[tid].history):
            assert b["rebuilt"] == ["stock", "cash_flow"]
            for k, v in b["cash_flow"].items():
                assert v == pytest.approx(a["cash_flow"][k], abs=1e-6), k
            assert [s["code"] for s in a["stock"]] == [s["code"] for s in b["stock"]]
            for s, r in zip(a["stock"], b["stock"]):
                for k, v in s.items():
                    assert r[k] == pytest.approx(v, abs=1e-6), (s["code"], k)


def test_a_month_without_its_saved_positions_is_left_alone():
    params, world, saved, subs = _played(3)
    bare = copy.deepcopy(world)
    for t in bare.teams.values():
        for h in t.history:
            for k in DETAIL:
                h.pop(k)
    del saved[1]                       # month 1's end, and so month 2's start
    assert backfill.fill(bare, saved, params, subs) == [3]
    h = next(iter(bare.teams.values())).history
    assert "stock" not in h[0] and "stock" not in h[1] and h[2]["stock"]


# --- The live app: a game whose first months were saved without the detail ----------

@pytest.fixture
def old_game(tmp_path):
    path = tmp_path / "g.db"
    pw = db.init(path, "Live", 3, rounds=12, admin_password="admin-pw")
    con = db.connect(path)
    db.set_game(con, rules_from=3)
    params = service.load_params(con)
    for i in (1, 2, 3):
        cfg = F.Founding.default(params)
        cfg.prices = {c: F.reference_price(params.sku(c), cfg.tier) for c in cfg.assortment}
        db.save_founding(con, f"team_{i:02d}", service.founding_to_dict(cfg), "sys",
                         submitted=True)
    for m, plan in ((1, {"team_01": {"7.2": "C"}}), (2, {"team_02": {"7.1": 6000.0}})):
        db.set_game(con, open_round=m)
        for tid, values in plan.items():
            db.submit(con, m, tid, values, "t")
        service.process_round(con)
    recorded = {m: db.load_world(con, m) for m in (1, 2)}
    # Strip the detail from every saved month, as the live game's months 1-2 were saved.
    for m in (1, 2):
        w = db.load_world(con, m)
        for t in w.teams.values():
            for h in t.history:
                for k in DETAIL:
                    h.pop(k, None)
        db.save_round(con, m, w, "old")
    return con, pw, path, recorded


def test_the_saved_game_gets_its_detail_back(old_game):
    con, pw, path, recorded = old_game
    assert "stock" not in db.load_world(con).teams["team_01"].history[0]
    world = service.detailed_world(con)
    for tid, team in world.teams.items():
        for a, b in zip(recorded[2].teams[tid].history, team.history):
            assert b["cash_flow"]["opening"] == pytest.approx(a["cash_flow"]["opening"])
            assert b["cash_flow"]["receipts"] == pytest.approx(a["cash_flow"]["receipts"])
            assert [s["close"] for s in b["stock"]] == pytest.approx(
                [s["close"] for s in a["stock"]])
            assert [s["sold"] for s in b["stock"]] == pytest.approx(
                [s["sold"] for s in a["stock"]])
    assert "stock" not in db.load_world(con).teams["team_01"].history[0], "never written back"


def test_a_starting_world_that_does_not_reproduce_month_one_is_not_used(old_game):
    con, *_ = old_game
    params = service.load_params(con)
    start = service.first_world(con, params, db.game(con))
    after = db.load_world(con, 1)
    assert service._opens_month_one(start, after, params)
    start.teams["team_01"].cash += 1_000.0
    assert not service._opens_month_one(start, after, params)


def _sheet(data, name):
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.load_workbook(io.BytesIO(data))
    return {r[0].value: [c.value for c in r[1:]] for r in wb[name].iter_rows() if r[0].value}


def test_workbook_shows_stock_and_the_cash_from_the_first_rupee(old_game):
    con, *_ = old_game
    data, _ = service.team_workbook(con, "team_01", 2)
    cash = _sheet(data, "Cash")
    params = service.load_params(con)
    f = db.load_world(con).teams["team_01"].founding
    assert cash["Starting capital"][0] == params["starting_cash"] == 12_000_000
    assert cash["Opening stock bought"][0] == -f.capital_inventory
    assert str(cash["Cash at the start of month 1"][0]).startswith("=SUM(")
    opening = cash["Opening cash"]
    assert opening[0] == "=B11" and opening[1].startswith("=B"), "openings chain"
    assert any(str(k).startswith("Months 1–2 ran before") for k in cash)
    stock = _sheet(data, "Stock")
    assert "Serum 30ml" in stock and "All products" in stock
    pbm = _sheet(data, "Products by month")
    assert any(v[10] is not None for k, v in pbm.items() if k == 2), "stock columns filled"


def test_setup_lines_add_up_to_month_one_opening():
    params, world, saved, subs = _played(1)
    team = next(iter(world.teams.values()))
    lines = workbook.setup_cash(team, params, team.history)
    assert lines[0] == ("Starting capital", 12_000_000.0, "The capital every team started with")
    assert sum(v for _, v, _ in lines) == pytest.approx(team.history[0]["cash_flow"]["opening"])
    team.history[0]["cash_flow"]["opening"] += 5
    assert workbook.setup_cash(team, params, team.history) is None, "never a block that misleads"


def test_stock_tile_reads_the_rebuilt_month(old_game):
    from ecomsim.web.app import create_app
    con, pw, path, recorded = old_game
    db.set_game(con, open_round=3)
    app = create_app(path)
    app.config["TESTING"] = True
    c = app.test_client()
    c.post("/login", data={"username": "team_01", "password": pw["team_01"]})
    c.post("/brief")
    page = c.get("/submit").data.decode()
    serum = next(s for s in recorded[2].teams["team_01"].history[1]["stock"]
                 if s["code"] == "SKU-03")
    assert f"{serum['close']:,.0f}" in page and "Sold in month 2" in page


def test_the_icon_is_served_and_linked(old_game):
    from ecomsim.web.app import create_app
    con, pw, path, _ = old_game
    app = create_app(path)
    c = app.test_client()
    assert c.get("/favicon.ico").status_code == 200
    assert c.get("/static/favicon.svg").mimetype == "image/svg+xml"
    assert 'href="/static/favicon.svg"' in c.get("/login").data.decode()
