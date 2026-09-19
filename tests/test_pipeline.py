"""Burst 1 gate: a full game runs end to end without structural pathologies.

This is deliberately NOT a calibration test - levels are burst 2's job. It
asserts only that the mechanisms behave coherently.
"""
from __future__ import annotations

import pytest

from ecomsim import bootstrap, params as P
from ecomsim.engine import run_game, run_round


@pytest.fixture(scope="module")
def played():
    p = P.load()
    world = bootstrap.new_world(p, run_id="pipeline")
    contexts = run_game(world, p, strategy=lambda w, r, t: {}, rounds=12)
    return world, p, contexts


def test_every_module_runs(played):
    world, _, _ = played
    assert all(len(t.history) == 12 for t in world.teams.values())


def test_no_cohort_seed_inconsistency(played):
    """Repeat demand must not routinely exceed total orders."""
    _, _, contexts = played
    warnings = [w for c in contexts for w in c.get("warnings", [])]
    assert not warnings, warnings[:3]


def test_new_customers_are_acquired(played):
    """If new_customers is always zero, CAC and LTV:CAC are meaningless."""
    world, _, _ = played
    team = world.teams["team_01"]
    acquiring = [h for h in team.history if h["cac_blended"] > 0]
    assert len(acquiring) >= 9


def test_no_reorder_oscillation(played):
    """Forecasting off realised orders makes stock-outs self-perpetuating.

    Guards the M3 fix: round-on-round order swings should not exceed 60%.
    """
    world, _, _ = played
    orders = [h["orders"] for h in world.teams["team_01"].history[2:]]
    swings = [abs(b - a) / a for a, b in zip(orders, orders[1:]) if a > 0]
    assert max(swings) < 0.60, f"max swing {max(swings):.0%}"


def test_share_conserves(played):
    """I6 - a pure correctness check on M7 redistribution."""
    world, _, _ = played
    for round_ in range(12):
        total = sum(t.history[round_]["market_share"] for t in world.teams.values())
        assert abs(total - 1.0) < 1e-9


def test_rates_stay_in_bounds(played):
    world, _, _ = played
    for team in world.teams.values():
        for h in team.history:
            assert 0 <= h["conversion_rate"] <= 0.5
            assert 0 <= h["rto_rate"] <= 0.9
            assert 0 <= h["return_rate"] <= 0.6
            assert 0 <= h["instock_rate"] <= 1.0
            assert 1.0 <= h["rating"] <= 5.0


def test_cash_never_goes_below_zero_with_headroom(played):
    """The credit line draws automatically; teams fail through decisions."""
    world, _, _ = played
    for team in world.teams.values():
        assert all(h["cash_balance"] >= 0 for h in team.history)


def test_pnl_identity_holds(played):
    world, _, _ = played
    for h in world.teams["team_01"].history:
        p = h["pnl"]
        assert abs(p["ebitda"] - (p["contribution"] - p["below_line"])) < 1e-6
        assert abs(p["net_profit"] - (p["ebitda"] - p["interest"])) < 1e-6


def test_rto_cost_is_its_own_line(played):
    """Teams must be able to see it; folding it into fulfilment hides it."""
    world, _, _ = played
    assert "rto_cost" in world.teams["team_01"].history[0]["pnl"]


def test_binding_constraint_is_diagnosed(played):
    world, _, _ = played
    valid = {"under_marketing", "wasted_spend", "stock_out", "balanced"}
    for team in world.teams.values():
        assert all(h["binding_constraint"] in valid for h in team.history)


def test_research_is_actually_charged_to_the_pl():
    """M16 runs after M14, so a cost computed there was never billed.

    Research was free for every team in every round: M16 wrote research_cost
    into ctx after the P&L had already read it.
    """
    params = P.load({"n_teams": 3, "events_enabled": 0})
    world = bootstrap.new_world(params, run_id="charge")
    studies = ["MR-01", "MR-07", "MR-10"]
    expected = sum(float(params.study(c)["price"]) for c in studies)

    run_round(world, params, {"team_01": {"12.1": studies}})
    billed = world.teams["team_01"].history[-1]["pnl"]["research"]
    assert billed == pytest.approx(expected), "studies must be paid for"
    assert world.teams["team_02"].history[-1]["pnl"]["research"] == 0


def test_a_lagged_study_arrives_late_but_arrives():
    """Lag-1 studies used to be queued and then dropped on the same line."""
    params = P.load({"n_teams": 3, "events_enabled": 0})
    world = bootstrap.new_world(params, run_id="lag")
    run_round(world, params, {"team_01": {"12.1": ["MR-06"]}})
    team = world.teams["team_01"]
    assert "MR-06" not in team.reports.get(1, {}), "it must not arrive early"

    run_round(world, params, {})
    landed = team.reports.get(2, {}).get("MR-06")
    assert landed is not None, "a study bought and paid for must arrive"
    assert landed["status"] == "lagged"
    assert landed["segments"], "and must carry the data it was bought for"


def test_every_study_reports_something():
    """Ten of twenty studies returned no_data: paid for, and silent."""
    params = P.load({"n_teams": 3, "events_enabled": 0})
    world = bootstrap.new_world(params, run_id="all")
    codes = [s["code"] for s in params.studies]
    # Marketplace participation unlocks in round 3, and MR-13 has nothing to
    # rank until it is on - so run far enough in for every study to apply.
    decisions = {"team_01": {"12.1": codes, "4.1": "on"}}
    for _ in range(4):
        run_round(world, params, decisions)

    silent = [c for c, r in world.teams["team_01"].reports[4].items()
              if r.get("status") == "no_data"]
    assert not silent, f"studies that report nothing: {silent}"
