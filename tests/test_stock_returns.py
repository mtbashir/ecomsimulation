"""Stock sent back to the supplier: off the shelf, refunded in cash, never guessed."""
import io
import sys
sys.path.insert(0, "src")

import pytest

from ecomsim import bootstrap, founding as F, params as P
from ecomsim.engine import run_round
from ecomsim.web import db, service

SERUM, OIL = "SKU-03", "SKU-08"


def _world():
    params = P.load({"n_teams": 2, "events_enabled": 0})
    world = bootstrap.new_world(params, run_id="ret")
    return params, world, list(world.teams)


def _identities(h):
    cf = h["cash_flow"]
    walk = (cf["opening"] + cf["receipts"] - cf["supplier_payments"] - cf["operating"]
            - cf["interest"] - cf["capex"] + cf["supplier_refund"] + cf["credit_draw"])
    assert walk == pytest.approx(cf["closing"])
    for s in h["stock"]:
        assert (s["open"] + s["received"] + s["returned"] - s["sold"] - s["to_supplier"]
                == pytest.approx(s["close"]))


def test_returned_stock_leaves_the_shelf_and_is_refunded():
    params, world, ids = _world()
    team = world.teams[ids[0]]
    held = team.inventory[SERUM] + sum(po["units"].get(SERUM, 0.0) for po in team.open_pos
                                       if po["arrives"] <= 1)
    team.stock_returns = {SERUM: {"units": held, "refund": 500_000.0, "fee": 0.0}}
    run_round(world, params, {})
    h = team.history[-1]
    line = next(s for s in h["stock"] if s["code"] == SERUM)
    assert line["to_supplier"] == pytest.approx(held)
    assert h["cash_flow"]["supplier_refund"] == pytest.approx(500_000.0)
    assert h["pnl"]["restocking"] == 0.0
    assert team.stock_returns == {}, "used once"
    _identities(h)
    other = world.teams[ids[1]].history[-1]
    assert other["cash_flow"]["supplier_refund"] == 0.0


def test_a_short_shelf_refunds_only_what_goes_back_and_a_fee_is_a_cost():
    params, world, ids = _world()
    team = world.teams[ids[0]]
    # Returns go after the month's deliveries land, so they count too.
    held = team.inventory[OIL] + sum(po["units"].get(OIL, 0.0) for po in team.open_pos
                                     if po["arrives"] <= 1)
    team.stock_returns = {OIL: {"units": held * 2, "refund": 100_000.0, "fee": 40_000.0}}
    run_round(world, params, {})
    h = team.history[-1]
    assert h["cash_flow"]["supplier_refund"] == pytest.approx(50_000.0)
    assert h["pnl"]["restocking"] == pytest.approx(20_000.0)
    _identities(h)


def test_without_a_return_nothing_moves():
    params, a, ids = _world()
    _, b, _ = _world()
    b.teams[ids[0]].stock_returns = {}
    for w in (a, b):
        run_round(w, params, {})
    assert a.teams[ids[0]].history[-1]["cash_balance"] == pytest.approx(
        b.teams[ids[0]].history[-1]["cash_balance"])


# --- The live game: stock outside each team's range ---------------------------------

@pytest.fixture
def old_opening(tmp_path):
    """Two months on the going-concern opening, one team off the default range."""
    path = tmp_path / "g.db"
    pw = db.init(path, "Live", 2, rounds=12, admin_password="admin-pw")
    con = db.connect(path)
    db.set_game(con, rules_from=3, launch_order=0)
    params = service.load_params(con)
    off = [c for c in F.Founding.default(params).assortment if c not in (SERUM, OIL)]
    off += [s["code"] for s in params.skus if s["code"] not in off and
            s["code"] not in (SERUM, OIL)][:12 - len(off)]
    for i, rng in ((1, off), (2, None)):
        cfg = F.Founding.default(params)
        if rng:
            cfg.assortment = rng
        cfg.prices = {c: F.reference_price(params.sku(c), cfg.tier) for c in cfg.assortment}
        db.save_founding(con, f"team_{i:02d}", service.founding_to_dict(cfg), "sys",
                         submitted=True)
    for m in (1, 2):
        db.set_game(con, open_round=m)
        service.process_round(con)
    db.set_game(con, open_round=3)
    from ecomsim.web.app import create_app
    app = create_app(path)
    app.config["TESTING"] = True
    admin = app.test_client()
    admin.post("/login", data={"username": "admin", "password": "admin-pw"})
    return con, pw, app, admin


def test_off_range_stock_is_listed_at_what_the_opening_order_charged(old_opening):
    con, *_ = old_opening
    held = service.off_range_stock(con)
    (t,) = held["teams"]
    assert t["team_id"] == "team_01"
    assert {l["sku"] for l in t["lines"]} == {SERUM, OIL}
    params = service.load_params(con)
    tmpl = bootstrap.new_team(params, "x").open_pos[0]
    for l in t["lines"]:
        assert l["units"] == pytest.approx(tmpl["units"][l["sku"]])
        sku = params.sku(l["sku"])
        assert l["refund"] == pytest.approx(l["units"] * float(sku["unit_cost"])
                                            * params["cogs_scale"])


def test_admin_schedules_cancels_and_month_three_refunds(old_opening):
    con, pw, app, admin = old_opening
    page = admin.get("/admin").data.decode()
    assert "Stock outside each team" in page and "Return to supplier, refunded in month 3" in page
    admin.post("/admin/returns")
    assert db.stock_returns(con, 3)["team_01"]
    admin.post("/admin/returns", data={"cancel": "1"})
    assert db.stock_returns(con, 3) == {}
    admin.post("/admin/returns")
    expect = service.off_range_stock(con)["teams"][0]["refund"]
    service.process_round(con)
    world = db.load_world(con)
    team = world.teams["team_01"]
    assert all(c in team.active_skus for c, u in team.inventory.items() if u > 0.5)
    h = team.history[-1]
    assert h["cash_flow"]["supplier_refund"] == pytest.approx(expect)
    _identities(h)
    assert world.teams["team_02"].history[-1]["cash_flow"]["supplier_refund"] == 0.0
    assert "Stock outside each team" not in admin.get("/admin").data.decode(), "nothing left"


def test_teams_see_why_and_where_it_went(old_opening):
    con, pw, app, admin = old_opening
    team = app.test_client()
    team.post("/login", data={"username": "team_01", "password": pw["team_01"]})
    team.post("/brief")
    form = team.get("/submit").data.decode()
    assert "products outside your range" in form
    admin.post("/admin/returns")
    service.process_round(con)
    html = service.team_report(con, "team_01", 3)
    assert "not in your range" in html and "Returned to supplier</th>" in html
    assert "went back to the supplier at the start of month 3" in html
    assert "came with the opening stock order" in html


def test_workbook_carries_the_return_and_the_refund(old_opening):
    openpyxl = pytest.importorskip("openpyxl")
    con, pw, app, admin = old_opening
    admin.post("/admin/returns")
    service.process_round(con)
    data, _ = service.team_workbook(con, "team_01", 3)
    wb = openpyxl.load_workbook(io.BytesIO(data))
    cash = {r[0].value: [c.value for c in r[1:]] for r in wb["Cash"].iter_rows() if r[0].value}
    assert cash["Refund for stock returned to the supplier"][2] > 0
    assert "Returned to supplier" in [c.value for c in wb["Stock"][4]]


def test_new_game_clears_one_cohorts_returns_and_memo_verdicts(tmp_path):
    path = tmp_path / "g.db"
    db.init(path, "Old", 2)
    con = db.connect(path)
    db.schedule_returns(con, 3, [{"team_id": "team_01", "sku": SERUM, "units": 1.0,
                                  "refund": 1.0}], "off_range")
    db.set_memo_review(con, 2, "team_01", False, "admin")
    db.new_game(con, path, "Next", 2, 12, "founding", keep_overrides=False)
    assert db.stock_returns(con, 3) == {}
    assert db.memo_rejected(con) == set()
