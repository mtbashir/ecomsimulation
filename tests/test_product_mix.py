"""Sales by product: the mix follows the team's decisions and adds up to the P&L."""
import sys
sys.path.insert(0, "src")

import pytest

from ecomsim import bootstrap, mix, params as P
from ecomsim.engine import run_round

SERUM, OIL, SOAP = "SKU-03", "SKU-08", "SKU-11"
CAMPAIGN = [{"channel": "meta", "name": "Serum hero", "skus": [SERUM],
             "ages": ["25-34"], "gender": "female", "geo": ["T1"],
             "interests": ["beauty"], "objective": "conversions"}]


def _play(plans: list[dict], months: int = 3):
    params = P.load({"n_teams": len(plans), "events_enabled": 0})
    world = bootstrap.new_world(params, run_id="mix")
    ids = list(world.teams)
    for _ in range(months):
        run_round(world, params, dict(zip(ids, plans)))
    return params, [world.teams[t].history[-1] for t in ids]


def _line(record, code):
    return next(r for r in record["products"] if r["code"] == code)


def test_products_add_up_to_the_pnl():
    _, (h, _) = _play([{"1.1": {OIL: {"discount": 0.2}}, "1.2": {SOAP: {}},
                        "3.10": CAMPAIGN}, {}])
    rows, pnl = h["products"], h["pnl"]
    assert sum(r["net_sales"] for r in rows) == pytest.approx(pnl["net_revenue"])
    assert sum(r["gross_margin"] for r in rows) == pytest.approx(pnl["gross_profit"])
    assert sum(r["cm_pre"] for r in rows) == pytest.approx(
        pnl["contribution"] + pnl["marketing"])
    assert sum(r["cm"] for r in rows) == pytest.approx(pnl["contribution"])
    assert sum(r["units"] for r in rows) == pytest.approx(h["units_sold"])
    for r in rows:
        assert sum(r["buyers"].values()) == pytest.approx(1.0)


def test_identical_teams_sell_the_catalogue_mix():
    params, (a, b) = _play([{}, {}])
    for r in a["products"]:
        assert r["unit_share"] == pytest.approx(r["typical_share"], rel=1e-6)
        assert r["why"] == [] or all("ran out" not in w for w in r["why"])


def test_a_price_cut_on_one_line_grows_its_share():
    _, (none, cut) = _play([{}, {"1.1": {OIL: {"discount": 0.2}}}])
    assert _line(cut, OIL)["unit_share"] > _line(none, OIL)["unit_share"] * 1.2
    assert any("below the rest of your range" in w for w in _line(cut, OIL)["why"])


def test_a_dearer_line_sells_less():
    _, (none, dear) = _play([{}, {"1.1": {SERUM: {"price": 3600}}}])
    assert _line(dear, SERUM)["unit_share"] < _line(none, SERUM)["unit_share"]


def test_a_product_campaign_pushes_its_product_and_carries_its_cost():
    _, (none, push) = _play([{}, {"3.10": CAMPAIGN}])
    serum = _line(push, SERUM)
    assert serum["unit_share"] > _line(none, SERUM)["unit_share"] * 1.5
    assert serum["pushed_units"] > 0
    assert any("Serum hero" in w for w in serum["why"])
    # the campaign's spend is charged to the product it named
    others = [r for r in push["products"] if r["code"] != SERUM]
    per_sale = sum(r["marketing"] for r in others) / sum(r["net_sales"] for r in others)
    assert serum["marketing"] / serum["net_sales"] > per_sale


def test_a_pack_sells_its_own_line_and_halves_its_delivery_cost():
    _, (none, pack) = _play([{}, {"1.2": {SOAP: {"price": 450 * 3 * 0.85}}}])
    a, b = _line(none, SOAP), _line(pack, SOAP)
    assert b["unit_share"] > a["unit_share"]
    assert b["pack_units"] > 0 and any("3-packs" in w for w in b["why"])
    assert b["delivery_cost"] / b["units"] < 0.6 * a["delivery_cost"] / a["units"]
    assert b["cm_pre_pct"] > a["cm_pre_pct"]


def test_customers_decide_what_sells():
    """A store that wins more of a product's main buyers sells more of it."""
    params = P.load({})
    base = {s["code"]: float(s["share"]) for s in params.segments}
    loyal = dict(base, quality_loyalists=base["quality_loyalists"] + 0.1,
                 value_seekers=base["value_seekers"] - 0.1)
    world = bootstrap.new_world(params, run_id="seg")
    team = next(iter(world.teams.values()))
    ctx = {"order_segments": {team.team_id: loyal}}
    lines = mix.demand(team, params, ctx, {}, base)
    assert lines[SERUM]["seg_pull"] > 1.05 > 0.95 > lines[OIL]["seg_pull"]


def test_stock_follows_the_team_not_the_catalogue():
    _, (none, cut) = _play([{}, {"1.1": {OIL: {"discount": 0.2}}}], months=5)
    assert _line(cut, OIL)["short"] == pytest.approx(0.0, abs=1.0)


def test_report_form_and_debrief_show_products(tmp_path):
    from ecomsim import report, debrief
    params = P.load({"n_teams": 2, "events_enabled": 0})
    world = bootstrap.new_world(params, run_id="mixr")
    ids = list(world.teams)
    run_round(world, params, {ids[0]: {}, ids[1]: {"1.1": {OIL: {"discount": 0.2}}}})
    team = world.teams[ids[1]]
    html = report.render(team, 1, tmp_path).read_text()
    assert "Sales by product this month" in html and "Who bought each product" in html
    assert "Best sellers:" in html and "MR-06" in html
    assert "Products." in debrief._products(team.history[-1])


def test_records_without_products_still_render(tmp_path):
    from ecomsim import report
    params = P.load({"n_teams": 2, "events_enabled": 0})
    world = bootstrap.new_world(params, run_id="old")
    run_round(world, params, {})
    team = next(iter(world.teams.values()))
    for k in ("products", "order_segments", "segment_names"):
        team.history[-1].pop(k)
    html = report.render(team, 1, tmp_path).read_text()
    assert "Sales by product" not in html
    run_round(world, params, {})        # and the buyer falls back to the catalogue
