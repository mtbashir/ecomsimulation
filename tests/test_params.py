"""T0 - parameter registry integrity.

Catches orphans and typos automatically: every parameter the engine reads must
exist in params/parameters.csv, and nothing may hardcode an economic constant.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from ecomsim import params as P

SRC = Path(__file__).resolve().parents[1] / "src" / "ecomsim"


def test_loads_with_defaults():
    p = P.load()
    assert p.values["saturation_exponent"] == 0.60
    assert p.config_hash()


def test_every_referenced_param_exists():
    """params["..."] anywhere in the engine must resolve to a registry row."""
    p = P.load()
    pattern = re.compile(r'params\[\s*"([a-z0-9_]+)"\s*\]')
    missing = {
        name
        for path in SRC.rglob("*.py")
        for name in pattern.findall(path.read_text(encoding="utf-8"))
        if name not in p.values
    }
    assert not missing, f"referenced but not in parameters.csv: {sorted(missing)}"


def test_hard_band_rejected():
    with pytest.raises(P.BandViolation):
        P.load({"saturation_exponent": 0.99})


def test_amber_band_warns_but_loads():
    p = P.load({"adstock_carryover": 0.60})
    assert any("adstock_carryover" in w for w in p.warnings)


def test_danger_params_always_warn():
    p = P.load({"share_sensitivity": 2.2})
    assert any("most often break" in w for w in p.warnings)


def test_pillar_weights_must_sum_to_100():
    with pytest.raises(P.BandViolation):
        P.load({"weight_profitability": 30})


@pytest.mark.parametrize(
    "pillar", ["weight_customer_value", "weight_cash", "weight_decision_quality"]
)
def test_protected_pillars_may_not_be_zero(pillar):
    """Zeroing these removes the behaviour they protect against (docs/08).

    Rejected twice over: the hard band floors them at 5, and the joint
    constraint catches zero independently if a band is ever widened.
    """
    with pytest.raises(P.BandViolation):
        P.load({pillar: 0, "weight_profitability": 45})


def test_segment_shares_sum_to_one():
    p = P.load()
    assert abs(sum(float(s["share"]) for s in p.segments) - 1.0) < 1e-9


def test_joint_constraint_flags_spend_to_win():
    p = P.load({
        "gross_margin_base": 0.50,
        "cpm_inflation_phi": 0.10,
        "saturation_exponent": 0.75,
    })
    assert any("dominant strategy" in w for w in p.warnings)


def test_deal_cohort_churn_is_the_trap():
    """The single most important row in the engine (docs/07 M12)."""
    p = P.load()
    deal = next(c for c in p.channels if c["code"] == "deal_driven")
    organic = next(c for c in p.channels if c["code"] == "organic")
    assert float(deal["churn_base"]) > 3 * float(organic["churn_base"])
    assert float(deal["freq_per_round"]) < 0.3 * float(organic["freq_per_round"])


def test_csv_rows_are_well_formed():
    """A comma inside a note field silently shifts every later column.

    It cost a debugging cycle once; it should never cost another.
    """
    from pathlib import Path

    root = Path(__file__).resolve().parents[1] / "params"
    for path in sorted(root.glob("*.csv")):
        rows = path.read_text(encoding="utf-8").rstrip().split("\n")
        width = len(rows[0].split(","))
        for i, row in enumerate(rows[1:], start=2):
            assert len(row.split(",")) == width, f"{path.name} line {i}: wrong column count"
