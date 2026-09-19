"""Chart primitives and the instructor console.

The palette is validated by the dataviz validator, not here; these tests cover
the things a validator cannot see - geometry, direction of meaning, and the
accessibility affordances that must survive a refactor.
"""
from __future__ import annotations

import re

from ecomsim import bootstrap, console, params as P, report
from ecomsim.charts import RAMP_DARK, RAMP_LIGHT, rank_bars, small_multiple, sparkline
from ecomsim.engine import run_round

PARAMS = P.load({"n_teams": 4, "events_enabled": 0})


def _played(rounds=5):
    world = bootstrap.new_world(PARAMS, run_id="charts")
    for _ in range(rounds):
        run_round(world, PARAMS, {"team_01": {"3.1": 900_000},
                                  "team_02": {"2.2": 0.30}})
    return world


# --- Sparkline ------------------------------------------------------------------

def test_sparkline_marks_only_the_current_point():
    """A number on every point is noise; the reader wants 'where is it now'."""
    svg = sparkline([1, 3, 2, 5, 4, 6], label="Revenue")
    assert svg.count("<circle") == 1
    assert svg.count("<path") == 1


def test_sparkline_keeps_the_last_twelve_points():
    svg = sparkline(list(range(40)), label="Orders")
    assert svg.count("L") == 11   # 12 points, first is M


def test_sparkline_survives_degenerate_input():
    assert "<path" not in sparkline([], label="x")
    assert "<path" not in sparkline([5], label="x")
    # A flat series must not divide by a zero span.
    assert "<path" in sparkline([3, 3, 3, 3], label="x")


def test_sparkline_carries_an_accessible_label():
    svg = sparkline([1, 2, 3], label="Net revenue")
    assert 'role="img"' in svg and "aria-label=" in svg and "<title>" in svg
    assert "Net revenue" in svg


def test_sparkline_marker_has_a_surface_ring():
    """Overlapping marks need a 2px surface ring to stay separable."""
    assert 'stroke="var(--surface)"' in sparkline([1, 2, 3], label="x")


# --- Rank bars -------------------------------------------------------------------

def test_rank_bars_are_direct_labelled_and_ordered():
    svg = rank_bars([("A", 50.0), ("B", 30.0), ("C", 10.0)])
    assert svg.count("<rect") == 3
    widths = [float(w) for w in re.findall(r'width="([\d.]+)" height', svg)]
    assert widths == sorted(widths, reverse=True), "bars must descend with value"
    for name in ("A", "B", "C"):
        assert f">{name}<" in svg


def test_rank_bars_handle_negative_values():
    svg = rank_bars([("A", 10.0), ("B", -5.0)])
    assert svg.count("<rect") == 2
    assert "-" not in re.search(r'width="([\d.-]+)"', svg).group(1)


def test_ramps_are_monotone_in_both_modes():
    """The ordinal ramp must read light-to-dark, or rank stops being legible."""
    def luminance(hex_: str) -> float:
        r, g, b = (int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5))
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    assert [luminance(c) for c in RAMP_LIGHT] == sorted(
        (luminance(c) for c in RAMP_LIGHT), reverse=True)
    assert [luminance(c) for c in RAMP_DARK] == sorted(
        luminance(c) for c in RAMP_DARK)


# --- Direction of meaning --------------------------------------------------------

def test_delta_colour_follows_good_not_up():
    """A rising CAC is bad news; colouring it green tells the opposite story."""
    worse = small_multiple("CAC", [400, 500], 500, good_up=False)
    better = small_multiple("Orders", [400, 500], 500, good_up=True)
    assert 'class="dl down"' in worse
    assert 'class="dl up"' in better


def test_report_colours_cac_and_debt_as_bad_when_rising():
    world = _played()
    html = report.render(world.teams["team_01"], 5, "/tmp/ecomsim-test").read_text()
    flags = {label: good for _, metrics in report.BLOCKS
             for label, _k, _f, good in metrics}
    assert flags["Blended CAC"] is False
    assert flags["Credit drawn"] is False
    assert flags["RTO rate"] is False
    assert flags["Net revenue"] is True
    assert html


def test_report_has_no_missing_metrics():
    """Every metric the report asks for must be persisted by M17."""
    world = _played(3)
    record = world.teams["team_01"].history[-1]
    missing = [label for _, metrics in report.BLOCKS for label, key, _f, _g in metrics
               if report._value(record, key) is None]
    assert not missing, f"rendered as em-dashes: {missing}"


# --- Console ----------------------------------------------------------------------

def test_console_withholds_the_leaderboard_until_round_four(tmp_path):
    world = _played(rounds=2)
    html = console.render(world, PARAMS, tmp_path).read_text()
    assert "Withheld until Round 4" in html
    assert "<rect" not in html


def test_console_shows_the_leaderboard_and_a_table_view(tmp_path):
    world = _played(rounds=5)
    html = console.render(world, PARAMS, tmp_path).read_text()
    assert html.count("<rect") == 4              # one bar per team
    assert '<table class="t">' in html           # every chart owes a table view
    assert "of the total weight" in html         # round weighting is stated


def test_console_logs_near_misses_for_threshold_calibration(tmp_path):
    world = _played(rounds=6)
    html = console.render(world, PARAMS, tmp_path).read_text()
    flagged = any(console._near_misses(t, PARAMS) for t in world.teams.values())
    assert ("Near a conditional trigger" in html) == flagged


def test_console_declares_dark_mode_under_both_scopes(tmp_path):
    world = _played(rounds=5)
    html = console.render(world, PARAMS, tmp_path).read_text()
    assert "prefers-color-scheme:dark" in html
    assert '[data-theme="dark"]' in html
