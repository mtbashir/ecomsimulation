"""Stock by product: buy in total or line by line, and see each line's cover."""
import sys
sys.path.insert(0, "src")

import pytest

from ecomsim import bootstrap, params as P, report
from ecomsim.engine import run_round
from ecomsim.io_csv import _coerce
from ecomsim.modules.m03_supply import purchase_plan

SERUM, OIL = "SKU-03", "SKU-08"


def _world(n=3):
    params = P.load({"n_teams": n, "events_enabled": 0})
    world = bootstrap.new_world(params, run_id="stock")
    return params, world, list(world.teams)


def _ordered(team, month):
    return {c: u for po in team.open_pos if po["placed"] == month
            for c, u in po["units"].items() if u > 0}


def test_a_total_or_a_product_split_reads_the_same_way():
    assert purchase_plan(None) == (None, None)
    assert purchase_plan("") == (None, None)
    assert purchase_plan(4000.0) == (4000.0, None)
    assert purchase_plan({SERUM: 1500, OIL: "700"}) == (2200.0, {SERUM: 1500.0, OIL: 700.0})
    assert _coerce("7.1", "SKU-03:1,200; SKU-08:800") == {SERUM: 1200.0, OIL: 800.0}
    assert _coerce("7.1", "4000") == 4000.0


def test_bought_product_by_product_lands_as_entered():
    params, world, ids = _world()
    run_round(world, params, {ids[0]: {"7.1": {SERUM: 1500.0, OIL: 700.0}, "7.2": "C"}})
    team = world.teams[ids[0]]
    assert _ordered(team, 1) == pytest.approx({SERUM: 1500.0, OIL: 700.0})
    rec = team.history[-1]
    assert rec["purchase"] == {"asked": 2200.0, "bought": 2200.0, "moq": 500.0,
                               "supplier": "C", "by_product": True}
    lines = {s["code"]: s for s in rec["stock"]}
    assert lines[SERUM]["ordered"] == pytest.approx(1500.0)
    assert lines["SKU-01"]["ordered"] == 0.0, "a line left out gets no new stock"


def test_a_split_below_the_minimum_order_is_scaled_up_in_proportion():
    params, world, ids = _world()
    run_round(world, params, {ids[0]: {"7.1": {SERUM: 300.0, OIL: 100.0, "SKU-99": 50.0}}})
    got = _ordered(world.teams[ids[0]], 1)
    assert sum(got.values()) == pytest.approx(2000.0), "supplier B's minimum"
    assert got[SERUM] / got[OIL] == pytest.approx(3.0)
    assert "SKU-99" not in got, "a code that is not a product is ignored"


def test_buying_nothing_on_every_line_buys_nothing():
    params, world, ids = _world()
    run_round(world, params, {ids[0]: {"7.1": {SERUM: 0.0}}})
    assert _ordered(world.teams[ids[0]], 1) == {}


def test_a_total_still_splits_by_what_sold():
    params, world, ids = _world()
    run_round(world, params, {ids[0]: {"7.1": 4000.0}})
    got = _ordered(world.teams[ids[0]], 1)
    assert sum(got.values()) == pytest.approx(4000.0) and len(got) > 5
    assert world.teams[ids[0]].history[-1]["purchase"]["by_product"] is False


def test_report_shows_closing_stock_and_cover_by_product(tmp_path):
    params, world, ids = _world(2)
    run_round(world, params, {ids[0]: {"7.1": {SERUM: 300.0}}})
    run_round(world, params, {ids[0]: {"7.1": {SERUM: 2500.0, OIL: 900.0}}})
    html = report.render(world.teams[ids[0]], 2, tmp_path).read_text()
    assert "Stock by product, end of month 2" in html
    assert "Closing stock" in html and "Weeks of cover" in html
    serum = next(s for s in world.teams[ids[0]].history[-1]["stock"] if s["code"] == SERUM)
    assert f"{serum['close']:,.0f}" in html and "M3" in html, "on order, and when it lands"
    # month 1 was a 300-unit order on a 2,000 minimum: the report says why it grew
    html1 = report.render(world.teams[ids[0]], 1, tmp_path).read_text()
    assert "you asked for 300 units" in html1


def test_records_without_stock_lines_still_render(tmp_path):
    params, world, ids = _world(2)
    run_round(world, params, {})
    team = world.teams[ids[0]]
    team.history[-1].pop("stock")
    html = report.render(team, 1, tmp_path).read_text()
    assert "Stock by product" not in html


def test_debrief_reads_a_product_split():
    from ecomsim import debrief
    params, world, ids = _world(2)
    sub = {"7.1": {SERUM: 1500.0, OIL: 700.0}}
    run_round(world, params, {ids[0]: sub})
    team = world.teams[ids[0]]
    rows = dict(debrief._decisions(team, params, sub))
    assert rows[debrief._label("7.1")] == "2,200 units, product by product (2 products)"
    _, watch = debrief._observations(team, params, sub, team.history[-1], {}, [])
    assert any("Bought only 2,200 units" in w for w in watch)


# --- The form ----------------------------------------------------------------------

@pytest.fixture
def trading(tmp_path):
    from ecomsim import founding as F
    from ecomsim.web import db, service
    from ecomsim.web.app import create_app
    path = tmp_path / "g.db"
    pw = db.init(path, "Stock", 3, rounds=12, admin_password="admin-pw")
    con = db.connect(path)
    params = service.load_params(con)
    for i in (1, 2, 3):
        cfg = F.Founding.default(params)
        cfg.prices = {c: F.reference_price(params.sku(c), cfg.tier) for c in cfg.assortment}
        db.save_founding(con, f"team_{i:02d}", service.founding_to_dict(cfg), "sys",
                         submitted=True)
    db.set_game(con, open_round=1)
    service.process_round(con)
    db.set_game(con, open_round=2)
    app = create_app(path)
    app.config["TESTING"] = True
    c = app.test_client()
    c.post("/login", data={"username": "team_01", "password": pw["team_01"]})
    c.post("/brief")
    return con, c


def test_the_stock_tile_shows_each_products_stock_and_cover(trading):
    from ecomsim.web import db
    con, c = trading
    page = c.get("/submit").data.decode()
    assert "Product by product" in page and "Total units" in page
    assert "Closing stock" in page and "Weeks of cover" in page and "Sold in month 1" in page
    world = db.load_world(con)
    close = next(s["close"] for s in world.teams["team_01"].history[-1]["stock"]
                 if s["code"] == SERUM)
    assert f"{close:,.0f}" in page
    assert 'name="buy_SKU-03"' in page


def test_buying_product_by_product_from_the_form(trading):
    from ecomsim.web import db, service
    con, c = trading
    c.post("/submit", data={"buy_mode": "lines", "buy_SKU-03": "1,500", "buy_SKU-08": "700",
                            "7.1": "9999"})
    assert db.submission(con, 2, "team_01")["7.1"] == {SERUM: 1500.0, OIL: 700.0}
    page = c.get("/submit").data.decode()
    assert "2,200 units, product by product (2 products)" in page
    assert 'value="1,500"' in page, "the split comes back as entered"
    service.process_round(con)
    team = db.load_world(con).teams["team_01"]
    assert _ordered(team, 2) == pytest.approx({SERUM: 1500.0, OIL: 700.0})


def test_buying_a_total_from_the_form(trading):
    from ecomsim.web import db
    con, c = trading
    c.post("/submit", data={"buy_mode": "total", "7.1": "4,000", "buy_SKU-03": "1500"})
    assert db.submission(con, 2, "team_01")["7.1"] == pytest.approx(4000.0)


def test_a_negative_line_is_refused(trading):
    from ecomsim.web import db
    con, c = trading
    page = c.post("/submit", data={"buy_mode": "lines", "buy_SKU-03": "-5"},
                  follow_redirects=True).data.decode()
    assert "cannot be negative" in page
    assert "7.1" not in (db.submission(con, 2, "team_01") or {})


def test_a_product_split_survives_the_offline_csv(trading, tmp_path):
    from ecomsim.io_csv import read_decisions
    from ecomsim.web import service
    con, c = trading
    c.post("/submit", data={"buy_mode": "lines", "buy_SKU-03": "1500", "buy_SKU-08": "700"})
    path = tmp_path / "decisions.csv"
    path.write_text(service.export_decisions(con, 2))
    assert read_decisions(path)["team_01"]["7.1"] == {SERUM: 1500.0, OIL: 700.0}
