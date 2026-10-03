"""Website investment (5.1) must improve the store, a month after the spend."""
import sys
sys.path.insert(0, "src")

from ecomsim import bootstrap, params as P
from ecomsim.engine import run_round


def _play(spend_from_round2):
    params = P.load({"n_teams": 4})
    world = bootstrap.new_world(params, run_id="ux")
    ids = list(world.teams)
    for r in range(1, 4):   # by month 4 default teams run short of stock
        dec = {t: {} for t in ids}
        if r >= 2:
            dec[ids[1]] = {"5.1": spend_from_round2}
        run_round(world, params, dec)
    return world.teams[ids[0]], world.teams[ids[1]]


def test_spend_raises_ux_and_conversion():
    base, spender = _play(300_000)
    assert spender.ux_score > base.ux_score
    assert spender.ux_score <= spender.ux_ceiling + 1e-9
    assert spender.history[-1]["conversion_rate"] > base.history[-1]["conversion_rate"]


def test_no_spend_leaves_ux_alone():
    base, other = _play(0)
    assert abs(base.ux_score - other.ux_score) < 1e-9


def test_improvement_lands_next_month():
    params = P.load({"n_teams": 2})
    world = bootstrap.new_world(params, run_id="ux2")
    ids = list(world.teams)
    run_round(world, params, {t: {} for t in ids})
    run_round(world, params, {ids[0]: {"5.1": 400_000}, ids[1]: {}})
    a, b = (world.teams[t].history[-1]["conversion_rate"] for t in ids)
    assert abs(a - b) < 1e-9          # same month: no effect yet
    assert world.teams[ids[0]].ux_score > world.teams[ids[1]].ux_score
