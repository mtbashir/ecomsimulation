"""T2 - the baseline calibration gate.

    At default decisions, 8 teams, no events: the engine reproduces the Round 0
    baseline to within 2% on every headline metric, and holds it for 12 rounds.

Nothing else is built until this passes. If the engine drifts off baseline with
nobody making decisions, every parameter downstream is being fitted to a broken
foundation (docs/07, docs/11).

Currently xfail: the pipeline is incomplete. Remove the xfail marker as each
module lands - this file is the definition of done for Phase 2.
"""
from __future__ import annotations

import pytest

from ecomsim import params as P

BASELINE = {
    "revenue_net": 12_000_000,
    "orders": 4_000,
    "aov_net": 3_000,
    "sessions": 190_000,
    "conversion_rate": 0.021,
    "gross_margin_pct": 0.38,
    "contribution_margin_pct": 0.09,
    "cac_blended": 850,
    "repeat_order_share": 0.22,
    "rating": 4.1,
}
TOLERANCE = 0.02


@pytest.mark.xfail(reason="pipeline incomplete - this is the Phase 2 gate",
                   strict=False)
@pytest.mark.parametrize("n_teams", [2, 4, 8, 12, 16])
def test_baseline_holds_at_every_team_count(n_teams):
    """Per-team economics must be identical at every N (docs/04)."""
    from ecomsim.engine import run_game
    from ecomsim.state import WorldState, TeamState

    params = P.load({"n_teams": n_teams})
    world = WorldState(run_id="t2-baseline")
    world.teams = {f"team_{i}": TeamState(team_id=f"team_{i}") for i in range(n_teams)}
    world.incumbents = [
        {"id": "inc_a", "utility": 0.42},
        {"id": "inc_b", "utility": 0.46},
    ]

    run_game(world, params, strategy=lambda w, r, t: {}, rounds=12)

    for team in world.teams.values():
        final = team.history[-1]
        for metric, target in BASELINE.items():
            drift = abs(final[metric] - target) / target
            assert drift <= TOLERANCE, (
                f"{team.team_id} {metric}: {final[metric]:.4g} vs {target:.4g} "
                f"({drift:.1%} drift, tolerance {TOLERANCE:.0%})"
            )


def test_category_sizing_is_derived_from_team_count():
    """Per-team share is constant at every N - the check that gates the rest."""
    from ecomsim.modules import m01_market
    from ecomsim.state import WorldState

    per_team = []
    for n in (2, 4, 8, 12, 16):
        params = P.load({"n_teams": n})
        world = WorldState(run_id="sizing", round=1)
        m01_market.run(world, params, {}, {})
        per_team.append(world.category_size / n)

    assert max(per_team) - min(per_team) < 1e-6, "per-team economics must not vary with N"


def test_seasonality_disabled_at_annual_rounds():
    from ecomsim.modules import m01_market
    from ecomsim.state import WorldState

    sizes = []
    for round_ in (1, 7):  # 7 is the 1.45 seasonal peak
        params = P.load({"round_months": 12})
        world = WorldState(run_id="season", round=round_)
        m01_market.run(world, params, {}, {})
        sizes.append(world.category_size / (1 + params["category_growth_per_round"]) ** (round_ - 1))

    assert abs(sizes[0] - sizes[1]) < 1e-6, "seasonality must vanish at annual rounds"
