"""Range changes (1.3): add a product or drop one, in a game that allows it."""
import sys
sys.path.insert(0, "src")

import pytest

from ecomsim import assortment, bootstrap, founding as F, params as P
from ecomsim.engine import run_round
from ecomsim.web import db, service

PARAMS = P.load({"n_teams": 2, "events_enabled": 0})


def _game(on=True, months=2):
    world = bootstrap.new_world(PARAMS, run_id="range")
    world.range_changes = on
    f = F.Founding.default(PARAMS)
    for team in world.teams.values():
        F.apply(f, team, PARAMS)
    for _ in range(months):
        run_round(world, PARAMS, {})
    tid = next(iter(world.teams))
    team = world.teams[tid]
    outside = [s["code"] for s in PARAMS.skus if s["code"] not in team.active_skus]
    return world, tid, team, outside


def _change(world, tid, **value):
    run_round(world, PARAMS, {tid: {assortment.DECISION: value}})
    return world.teams[tid].history[-1]


def test_an_added_product_is_ordered_now_and_sells_when_it_lands():
    world, tid, team, outside = _game()
    new = outside[0]
    h = _change(world, tid, add=[new])
    assert new not in team.active_skus and team.pending_lines[new] > world.round
    (po,) = [p for p in team.open_pos if p.get("listing")]
    assert set(po["units"]) == {new} and po["cost"] > 0
    line = next(s for s in h["stock"] if s["code"] == new)
    assert line["on_order"] == pytest.approx(po["units"][new])
    assert new not in {r["code"] for r in h["products"]}, "not on sale yet"
    while team.pending_lines:
        run_round(world, PARAMS, {})
    assert new in team.active_skus
    sold = next(r for r in team.history[-1]["products"] if r["code"] == new)
    assert sold["units"] > 0 and sold["net_sales"] > 0
    f = team.founding
    assert team.sku_prices[new] == pytest.approx(
        F.reference_price(PARAMS.sku(new), f.tier)), "priced as set-up would"


def test_a_dropped_product_stops_selling_and_its_stock_goes_back_less_the_fee():
    world, tid, team, _ = _game()
    gone = team.active_skus[0]
    h = _change(world, tid, drop=[gone])
    assert gone not in team.active_skus
    assert gone not in {r["code"] for r in h["products"]}
    line = next(s for s in h["stock"] if s["code"] == gone)
    assert line["sold"] == 0 and line["close"] == 0 and line["to_supplier"] > 0
    refund, fee = h["cash_flow"]["supplier_refund"], h["pnl"]["restocking"]
    assert fee == pytest.approx((refund + fee) * PARAMS["range_restocking_fee"])
    cf = h["cash_flow"]
    assert (cf["opening"] + cf["receipts"] - cf["supplier_payments"] - cf["operating"]
            - cf["interest"] - cf["capex"] + cf["supplier_refund"] + cf["credit_draw"]
            ) == pytest.approx(cf["closing"])


def test_stock_of_a_dropped_product_still_on_its_way_goes_back_when_it_lands():
    world, tid, team, _ = _game()
    gone = team.active_skus[0]
    on_way = sum(p["units"].get(gone, 0.0) for p in team.open_pos
                 if p["arrives"] > world.round + 1)
    _change(world, tid, drop=[gone])
    for _ in range(3):
        run_round(world, PARAMS, {})
    assert team.inventory.get(gone, 0.0) < 0.5
    if on_way:
        assert any(s["to_supplier"] > 0 for h in team.history[-3:] for s in h["stock"]
                   if s["code"] == gone)


def test_the_range_stays_within_twelve_and_eighteen():
    world, tid, team, outside = _game()
    team.active_skus = team.active_skus[:12]
    _change(world, tid, drop=team.active_skus[:3])
    assert len(team.active_skus) == 12, "no drop below twelve"
    _change(world, tid, add=outside[:9])
    assert assortment.size(team) == 18, "no add above eighteen"


def test_a_change_is_made_once_not_carried():
    world, tid, team, outside = _game()
    world.rules_from = 1
    _change(world, tid, add=[outside[0]])
    run_round(world, PARAMS, {})
    assert sum(1 for p in team.open_pos if p.get("listing")) <= 1
    assert assortment.DECISION not in (team.standing or {})


def test_a_game_without_range_changes_ignores_the_decision():
    world, tid, team, outside = _game(on=False)
    before = list(team.active_skus)
    h = _change(world, tid, add=[outside[0]], drop=[before[0]])
    assert team.active_skus == before and not team.pending_lines
    assert not any(p.get("listing") for p in team.open_pos)
    # ...and decision quality does not count a lever the game does not offer
    on, tid_on, _, _ = _game(on=True)
    h_on = _change(on, tid_on)
    assert h["decisions"]["open"] == h_on["decisions"]["open"] - 1


# --- The app --------------------------------------------------------------------

def _app_game(tmp_path, on=True):
    path = tmp_path / "g.db"
    pw = db.init(path, "Next", 2, rounds=12, admin_password="admin-pw")
    con = db.connect(path)
    db.set_game(con, range_changes=int(on))
    params = service.load_params(con)
    for i in (1, 2):
        cfg = F.Founding.default(params)
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
    c = app.test_client()
    c.post("/login", data={"username": "team_01", "password": pw["team_01"]})
    c.post("/brief")
    return con, c


def test_the_tile_offers_the_range_and_the_catalogue_from_month_three(tmp_path):
    con, c = _app_game(tmp_path)
    assert "1.3" not in [s.code for s in service.form_decisions(con, 2)]
    page = c.get("/submit").data.decode()
    assert "Range changes" in page and 'name="range_add"' in page and 'name="range_drop"' in page
    assert "20% restocking fee" in page


def test_a_change_from_the_form_runs_and_the_grid_follows(tmp_path):
    con, c = _app_game(tmp_path)
    team = db.load_world(con).teams["team_01"]
    new = next(s["code"] for s in service.load_params(con).skus
               if s["code"] not in team.active_skus)
    gone = team.active_skus[-1]
    # The loan approves the order we place for the blank stock line.
    c.post("/submit", data={"range_add": new, "range_drop": gone, "12.6": "20000000"})
    assert db.submission(con, 3, "team_01")["1.3"] == {"add": [new], "drop": [gone]}
    assert "1 added, 1 dropped" in c.get("/submit").data.decode()
    service.process_round(con)
    db.set_game(con, open_round=4)
    world = db.load_world(con)
    assert gone not in world.teams["team_01"].active_skus
    shelf = {r["code"] for r in service.monthly_catalogue(con, "team_01", {})}
    assert gone not in shelf, "the price grid shows the range as it is now"


def test_a_change_that_breaks_the_range_size_is_refused(tmp_path):
    con, c = _app_game(tmp_path)
    team = db.load_world(con).teams["team_01"]
    drops = team.active_skus[:3]
    page = c.post("/submit", data={"range_drop": drops}, follow_redirects=True).data.decode()
    assert "must stay between 12 and 18" in page
    assert "1.3" not in (db.submission(con, 3, "team_01") or {})


def test_a_game_already_trading_never_offers_it(tmp_path):
    con, c = _app_game(tmp_path, on=False)
    assert "1.3" not in [s.code for s in service.form_decisions(con, 3)]
    assert "Range changes" not in c.get("/submit").data.decode()


def test_new_game_switches_range_changes_on(tmp_path):
    path = tmp_path / "g.db"
    db.init(path, "Old", 2)
    con = db.connect(path)
    db.set_game(con, round=4, range_changes=0)
    assert db.range_changes(con) is False
    db.new_game(con, path, "Next", 2, 12, "founding", keep_overrides=False)
    assert db.range_changes(con) is True
