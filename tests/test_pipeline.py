"""Burst 1 gate: a full game runs end to end without structural pathologies.

This is deliberately NOT a calibration test - levels are burst 2's job. It
asserts only that the mechanisms behave coherently.
"""
from __future__ import annotations

import pytest

from ecomsim import bootstrap, params as P
from ecomsim.engine import run_game


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
