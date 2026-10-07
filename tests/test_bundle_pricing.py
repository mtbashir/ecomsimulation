"""Bundle pack prices must matter (decision 1.2)."""
import sys
sys.path.insert(0, "src")

from ecomsim import bootstrap, params as P
from ecomsim.engine import run_round
from ecomsim.modules.m09_basket import _bundle_effect, _unit_net_price

CODES = ["SKU-01", "SKU-06", "SKU-10"]


def _team():
    params = P.load({"n_teams": 2})
    world = bootstrap.new_world(params, run_id="bun")
    return params, world, next(iter(world.teams.values()))


def _packs(team, params, ratio):
    return {c: {"price": _unit_net_price(team, params, {}, c) * 3 * ratio} for c in CODES}


def test_no_bundles_no_effect():
    params, _, team = _team()
    assert _bundle_effect(team, params, {}) == (1.0, 1.0)


def test_overpriced_packs_earn_nothing():
    params, _, team = _team()
    aov, units = _bundle_effect(team, params, {"1.2": _packs(team, params, 1.4)})
    assert aov == 1.0 and units == 1.0


def test_fair_pack_beats_dear_pack():
    params, _, team = _team()
    fair = _bundle_effect(team, params, {"1.2": _packs(team, params, 0.9)})
    dear = _bundle_effect(team, params, {"1.2": _packs(team, params, 1.15)})
    assert fair[1] > dear[1] > 1.0          # more packs taken at a fair price


def test_deep_discount_costs_revenue_per_unit():
    params, _, team = _team()
    fair_aov, fair_units = _bundle_effect(team, params, {"1.2": _packs(team, params, 0.9)})
    deep_aov, deep_units = _bundle_effect(team, params, {"1.2": _packs(team, params, 0.6)})
    assert deep_units >= fair_units
    assert deep_aov / deep_units < fair_aov / fair_units


def test_only_three_packs_count():
    params, _, team = _team()
    three = _bundle_effect(team, params, {"1.2": _packs(team, params, 0.9)})
    more = {c: {"price": _unit_net_price(team, params, {}, c) * 3 * 0.9}
            for c in CODES + ["SKU-02", "SKU-07", "SKU-11"]}
    assert _bundle_effect(team, params, {"1.2": more}) == three


def test_old_list_records_still_work():
    params, _, team = _team()
    aov, units = _bundle_effect(team, params, {"1.2": CODES})
    assert aov > 1.0 and units > 1.0


def test_bundles_add_units_to_cogs():
    params, world, _ = _team()
    ids = list(world.teams)
    run_round(world, params, {ids[0]: {}, ids[1]: {"1.2": CODES}})
    a, b = (world.teams[t].history[-1] for t in ids)
    assert b["aov_net"] > a["aov_net"]
    assert b["pnl"]["cogs"] / b["orders"] > a["pnl"]["cogs"] / a["orders"]


def test_console_carries_the_debrief():
    from pathlib import Path
    import tempfile
    from ecomsim import console
    params, world, _ = _team()
    ids = list(world.teams)
    subs = {ids[0]: {"3.1": 30_000.0, "3.2": 20_000.0, "3.4": 10_000.0,
                     "1.2": {c: {} for c in CODES + ["SKU-02"]}, "2.4": 0.0},
            ids[1]: {}}
    run_round(world, params, subs)
    with tempfile.TemporaryDirectory() as tmp:
        html = console.render(world, params, Path(tmp), submissions=subs,
                              open_codes=["3.1", "3.2", "3.4", "1.2", "2.4", "12.5"]).read_text()
    assert "what each team decided" in html
    assert "Cut ad budgets" in html
    assert "only the three most attractive count" in html
    assert "Free delivery on every order" in html
    assert "Submitted nothing" in html
    with tempfile.TemporaryDirectory() as tmp:          # file runner: no submissions
        plain = console.render(world, params, Path(tmp)).read_text()
    assert "what each team decided" not in plain


def test_debrief_explains_the_binding_constraint():
    from ecomsim import debrief
    params, world, team = _team()
    run_round(world, params, {t: {} for t in world.teams})
    h = dict(team.history[-1])
    room = {t.team_id: t.history[-1] for t in world.teams.values()}
    for code, side, phrase in [("balanced", 0, "Balanced month"),
                               ("under_marketing", 1, "Under-marketing"),
                               ("wasted_spend", 1, "Wasted spend"),
                               ("stock_out", 1, "Stock-out")]:
        h["binding_constraint"] = code
        room[team.team_id] = h
        lists = debrief._observations(team, params, {}, h, room, [])
        assert any(phrase in x for x in lists[side]), code


def test_funnel_and_channel_intent():
    from ecomsim import funnel
    params, world, team = _team()
    run_round(world, params, {t: {} for t in world.teams})
    h = team.history[-1]
    f = funnel.facts(h)
    assert abs(f["paid"] + f["organic"] + f["returning"] - f["sessions"]) < 1e-6 * f["sessions"]
    assert abs(f["conversion"] - h["conversion_rate"]) < 1e-12
    assert abs(f["weeks_cover"] - h["weeks_cover"]) < 1e-9
    rows = {r["channel"]: r for r in h["campaigns"]}
    assert rows["google_search"]["cvr"] > rows["meta"]["cvr"] > rows["tiktok"]["cvr"]
    # intent shares orders out between channels; it never adds any
    paid_cr = sum(r["clicks"] for r in h["campaigns"])
    assert paid_cr > 0
