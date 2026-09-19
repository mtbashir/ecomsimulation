"""I9 monotonicity and I10 no-free-lunch (docs/11).

Sign errors are the most common engine bug and the hardest to spot in aggregate
output. Each lever is moved up from default with everything else held, events
off, and the named metric must move the named way.
"""
from __future__ import annotations

import pytest

from ecomsim import bootstrap, params as P
from ecomsim.engine import run_game, run_round


def settled(overrides: dict, decisions: dict, rounds: int = 10):
    p = P.load({"events_enabled": 0} | overrides)
    w = bootstrap.new_world(p, run_id="mono")
    # Only team_01 moves. Moving every team shifts the market average with it,
    # which is a general-equilibrium question, not a sign check.
    run_game(w, p, strategy=lambda wo, r, t: dict(decisions) if t == "team_01" else {},
             rounds=rounds)
    h = w.teams["team_01"].history[5:]
    return {k: sum(x[k] for x in h) / len(h) for k in h[0] if isinstance(h[0][k], (int, float))}


BASE = settled({}, {})

# (decision, higher value, metric that must rise, metric that must fall)
LEVERS = [
    ("3.1", 1_200_000, "sessions", None),
    ("2.2", 0.20, "conversion_rate", "gross_margin_pct"),
    ("7.5", 5.0, "inventory_units", "cash_balance"),
    ("9.2", 0.08, None, "rto_rate"),
    ("10.1", 1, "cs_backlog", "rating"),      # fewer agents -> backlog, rating falls
    ("7.2", "C", None, "gross_margin_pct"),   # faster supplier costs margin
]


@pytest.mark.parametrize("decision,value,up,down", LEVERS)
def test_monotone(decision, value, up, down):
    moved = settled({}, {decision: value})
    if up:
        assert moved[up] > BASE[up] * 1.001, f"{decision}={value}: {up} did not rise"
    if down:
        assert moved[down] < BASE[down] * 0.999, f"{decision}={value}: {down} did not fall"


# I10: every lever must cost something. A decision with no downside is a
# dominant strategy waiting for a student to find it in Round 3.
COST_OF = {
    "3.1": "contribution_margin_pct", "3.9": "contribution_margin_pct",
    "2.2": "gross_margin_pct", "7.5": "cash_balance", "6.1": "contribution_margin_pct",
    "7.4": "contribution_margin_pct", "10.1": "ebitda_margin_pct",
    "9.2": "aov_net",
}


@pytest.mark.parametrize("decision,metric", list(COST_OF.items()))
def test_no_free_lunch(decision, metric):
    high = {"3.1": 1_500_000, "3.9": 900_000, "2.2": 0.25, "7.5": 6.0,
            "6.1": 500_000, "7.4": 400_000, "10.1": 10, "9.2": 0.10}[decision]
    moved = settled({}, {decision: high})
    assert moved[metric] < BASE[metric], f"{decision}={high} has no cost on {metric}"


def test_focus_wins_more_of_the_segments_you_chose():
    """A stated focus must actually redirect demand, not just be recorded."""
    from ecomsim import founding as F
    from ecomsim.modules import m07_share

    params = P.load({"n_teams": 3, "events_enabled": 0})
    world = bootstrap.new_world(params, run_id="focus")
    for tid, focus in [("team_01", ["quality_loyalists", "premium_gifting"]),
                       ("team_02", ["value_seekers", "deal_hunters"])]:
        f = F.Founding.default(params)
        f.tier = "premium"
        f.segment_priority = focus
        F.apply(f, world.teams[tid], params)

    mixes = {}
    original = m07_share.run

    def capture(w, p, r, ctx):
        original(w, p, r, ctx)
        mixes.update({k: dict(v) for k, v in ctx["segment_mix"].items()})

    m07_share.run = capture
    try:
        run_round(world, params, {})
    finally:
        m07_share.run = original

    market = {s["code"]: float(s["share"]) for s in params.segments}
    assert mixes["team_01"]["quality_loyalists"] > market["quality_loyalists"], (
        "focusing on a segment you fit must draw more of it than the market")
    assert mixes["team_01"]["value_seekers"] < market["value_seekers"], (
        "and less of the segments you turned away from")


def test_focus_on_a_segment_your_pricing_contradicts_does_not_pay():
    """Declaring Premium/Gifting while pricing at value tier must not help."""
    from ecomsim import founding as F

    params = P.load({"n_teams": 3, "events_enabled": 0})

    def cohort_quality(tier, focus):
        world = bootstrap.new_world(params, run_id="coherence")
        f = F.Founding.default(params)
        f.tier = tier
        f.segment_priority = focus
        F.apply(f, world.teams["team_01"], params)
        for _ in range(3):
            run_round(world, params, {})
        team = world.teams["team_01"]
        return sum(c.freq * c.active for c in team.cohorts) / sum(
            c.active for c in team.cohorts)

    coherent = cohort_quality("premium", ["quality_loyalists", "premium_gifting"])
    incoherent = cohort_quality("value", ["quality_loyalists", "premium_gifting"])
    assert coherent > incoherent, (
        "a focus the positioning supports must produce better customers than "
        "the same focus with contradictory pricing")


def test_a_team_with_no_founding_round_is_untouched_by_focus():
    """going_concern games have no D0.3, and must be exactly as they were."""
    params = P.load({"n_teams": 4, "events_enabled": 0})
    world = bootstrap.new_world(params, run_id="none")
    run_round(world, params, {})
    for team in world.teams.values():
        assert not hasattr(team, "founding") or team.founding is None
        assert team.history[-1]["orders"] > 0
