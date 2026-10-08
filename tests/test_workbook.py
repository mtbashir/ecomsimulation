"""The results workbook: every line adds up, and every rebuilt KPI is the report's."""
import io
import sys
import zipfile

import pytest

sys.path.insert(0, "src")

from ecomsim import bootstrap, params as P, workbook
from ecomsim.engine import run_round

SHEETS = ["Read me", "P&L", "KPIs", "Products", "Stock", "Products by month",
          "Cash", "Campaigns", "Customers"]


@pytest.fixture(scope="module")
def played():
    params = P.load({"n_teams": 3, "events_enabled": 0})
    world = bootstrap.new_world(params, run_id="wb")
    ids = list(world.teams)
    plan = {ids[0]: {}, ids[1]: {"1.1": {"SKU-08": {"discount": 0.2}},
                                 "1.2": {"SKU-11": {}}, "9.2": 0.03, "3.6": 0.05},
            ids[2]: {"2.2": 0.1}}
    for _ in range(3):
        run_round(world, params, plan)
    return params, world.teams[ids[1]]


def test_stock_moves_add_up(played):
    _, team = played
    for h in team.history:
        for s in h["stock"]:
            assert s["open"] + s["received"] + s["returned"] - s["sold"] == pytest.approx(s["close"])
        assert sum(s["close"] for s in h["stock"]) == pytest.approx(h["inventory_units"])
        assert sum(s["sold"] for s in h["stock"]) == pytest.approx(h["units_sold"])
    for a, b in zip(team.history, team.history[1:]):     # one month's close is the next one's open
        close = {s["code"]: s["close"] for s in a["stock"]}
        assert all(s["open"] == pytest.approx(close[s["code"]]) for s in b["stock"])


def test_pnl_lines_and_cash_add_up(played):
    _, team = played
    for h in team.history:
        p, c = h["pnl"], h["cash_flow"]
        gp = p["net_revenue"] - p["cogs_sold"] - p["write_off"]
        assert gp == pytest.approx(p["gross_profit"])
        contribution = (gp - p["pick_pack"] - p["courier"] - p["rto_cost"] - p["return_shipping"]
                        - p["gateway"] - p["cod_fee"] - p["commission"]
                        - p["marketing_spend"] - p["affiliate"])
        assert contribution == pytest.approx(p["contribution"])
        assert sum(p[k] for k in ("payroll", "service_team", "warehouse", "technology", "website",
                                  "quality_assurance", "research", "holding", "ageing")) \
            == pytest.approx(p["below_line"])
        assert (c["opening"] + c["receipts"] - c["supplier_payments"] - c["operating"]
                - c["interest"] - c["capex"] + c["credit_draw"]) == pytest.approx(c["closing"])
        assert c["closing"] == pytest.approx(h["cash_balance"])


def test_workbook_has_every_sheet(played):
    params, team = played
    data = workbook.build(team, params, "Test Brand", 3)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        book = z.read("xl/workbook.xml").decode()
    for name in SHEETS:
        assert f'name="{name.replace("&", "&amp;")}"' in book


def _rows(data, sheet):
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.load_workbook(io.BytesIO(data), data_only=True)
    return {r[0].value: [c.value for c in r[1:]] for r in wb[sheet].iter_rows() if r[0].value}


def test_rebuilt_kpis_are_the_reports(played):
    params, team = played
    data = workbook.build(team, params, "Test Brand", 3)
    kpi, pl = _rows(data, "KPIs"), _rows(data, "P&L")
    pairs = [("Conversion rate", "conversion_rate"), ("AOV (average order value)", "aov_net"),
             ("Blended CAC", "cac_blended"), ("Service level", "service_level"),
             ("Weeks of cover", "weeks_cover"), ("Repeat order share", "repeat_order_share"),
             ("LTV : CAC", "ltv_cac_ratio"), ("Gross margin", "gross_margin_pct"),
             ("Contribution margin", "contribution_margin_pct"),
             ("Contribution before marketing", "contribution_pre_marketing_pct"),
             ("Net profit", "net_profit")]
    for label, key in pairs:
        for got, h in zip(kpi[label], team.history):
            assert got == pytest.approx(h[key], rel=1e-9, abs=1e-9), label
    for got, h in zip(pl["Net revenue"], team.history):
        assert got == pytest.approx(h["revenue_net"])
    for got, h in zip(pl["EBITDA"], team.history):
        assert got == pytest.approx(h["pnl"]["ebitda"])


def test_months_recorded_before_the_detail_still_add_up(played):
    """The live game's month 1 predates the product, stock, cash and P&L-line
    records; its P&L must still rebuild exactly from what it kept."""
    import copy
    params, team = played
    old = copy.deepcopy(team)
    h = old.history[0]
    for k in ("products", "stock", "cash_flow", "order_segments", "segment_names",
              "sessions_paid", "sessions_organic", "sessions_returning", "units_sold"):
        h.pop(k, None)
    for k in ("cogs_sold", "write_off", "pick_pack", "courier", "return_shipping", "gateway",
              "cod_fee", "marketing_spend", "affiliate", "payroll", "service_team", "warehouse",
              "technology", "website", "quality_assurance"):
        h["pnl"].pop(k)
    for upto in (1, 3):
        data = workbook.build(old, params, "Old", upto)
        pl, kpi = _rows(data, "P&L"), _rows(data, "KPIs")
        assert "Overheads (not split for this month)" in pl
        assert pl["Contribution"][0] == pytest.approx(h["pnl"]["contribution"])
        assert pl["EBITDA"][0] == pytest.approx(h["pnl"]["ebitda"])
        assert kpi["Blended CAC"][0] == pytest.approx(h["cac_blended"])
        # without units sold on record, cover is read on orders x units per order,
        # as the engine itself did before units sold were kept
        assert kpi["Weeks of cover"][0] == pytest.approx(
            h["inventory_units"] * 4.33 / (h["orders"] * params["units_per_order"]))
