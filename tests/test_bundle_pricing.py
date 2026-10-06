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
