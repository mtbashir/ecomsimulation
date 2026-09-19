"""T0 / I8 - determinism.

Without this, replay, golden files and dispute resolution all fail. Cheap to
test and it catches map-iteration-order bugs before they are expensive.
"""
from __future__ import annotations

from ecomsim import rng


def test_uniform_is_reproducible():
    a = rng.uniform("run1", 3, "team_a", "leadtime", "SKU-04")
    b = rng.uniform("run1", 3, "team_a", "leadtime", "SKU-04")
    assert a == b
    assert 0.0 <= a < 1.0


def test_keys_are_independent():
    """Adding a draw for one purpose must not shift another's sequence."""
    a = rng.uniform("run1", 3, "team_a", "leadtime")
    b = rng.uniform("run1", 3, "team_a", "project")
    assert a != b


def test_research_reports_do_not_reroll():
    """Re-buying a study in the same round returns the identical number.

    docs/02 implementation rule 1: without this, teams re-buy to average out the
    noise and the uncertainty lesson evaporates.
    """
    draws = {rng.normal("run1", 5, "team_b", "study", 0.0, 0.05, "MR-07")
             for _ in range(10)}
    assert len(draws) == 1


def test_normal_is_centred():
    vals = [rng.normal("run1", 1, f"t{i}", "noise", 0.0, 1.0) for i in range(4000)]
    assert abs(sum(vals) / len(vals)) < 0.06
