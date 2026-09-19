"""Decision intake, results output and the per-team report.

The delivery surface: form export in, HTML report out (docs/12).
"""
from __future__ import annotations

import csv

import pytest

from ecomsim import bootstrap, params as P, report
from ecomsim.engine import run_round
from ecomsim.io_csv import SubmissionError, read_decisions, write_results, write_template

PARAMS = P.load({"n_teams": 3, "events_enabled": 0})


def _write(tmp_path, rows):
    path = tmp_path / "d.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["team_id", "decision", "value"])
        w.writerows(rows)
    return path


def test_template_round_trips(tmp_path):
    path = tmp_path / "t.csv"
    write_template(path, ["team_01", "team_02"])
    got = read_decisions(path)
    assert set(got) == {"team_01", "team_02"}
    assert got["team_01"]["3.1"] == 468_000


def test_blank_means_use_the_default(tmp_path):
    """A team that leaves a field blank gets the default, not an error."""
    got = read_decisions(_write(tmp_path, [["team_01", "3.1", ""],
                                           ["team_01", "2.2", "0.1"]]))
    assert "3.1" not in got["team_01"]
    assert got["team_01"]["2.2"] == 0.1


def test_percentages_and_thousands_separators(tmp_path):
    got = read_decisions(_write(tmp_path, [["team_01", "2.2", "25%"],
                                           ["team_01", "3.1", "1,250,000"]]))
    assert got["team_01"]["2.2"] == 0.25
    assert got["team_01"]["3.1"] == 1_250_000


def test_list_decisions_split_on_either_separator(tmp_path):
    got = read_decisions(_write(tmp_path, [["team_01", "12.1", "MR-01;MR-07"],
                                           ["team_02", "12.1", "MR-01, MR-17"]]))
    assert got["team_01"]["12.1"] == ["MR-01", "MR-07"]
    assert got["team_02"]["12.1"] == ["MR-01", "MR-17"]


def test_unknown_decision_is_reported_with_its_line(tmp_path):
    with pytest.raises(SubmissionError, match="9.9"):
        read_decisions(_write(tmp_path, [["team_01", "9.9", "1"]]))


def test_non_numeric_value_is_reported(tmp_path):
    with pytest.raises(SubmissionError, match="3.1"):
        read_decisions(_write(tmp_path, [["team_01", "3.1", "lots"]]))


def test_missing_columns_are_reported(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("team,decision\nteam_01,3.1\n", encoding="utf-8")
    with pytest.raises(SubmissionError, match="team_id"):
        read_decisions(path)


def test_results_accumulate_across_rounds(tmp_path):
    world = bootstrap.new_world(PARAMS, run_id="io")
    out = tmp_path / "results.csv"
    for _ in range(2):
        run_round(world, PARAMS, {})
        write_results(out, world)
    rows = list(csv.DictReader(out.open()))
    assert len(rows) == 6                      # 3 teams x 2 rounds
    assert {r["round"] for r in rows} == {"1", "2"}


def test_report_renders_and_names_the_binding_constraint(tmp_path):
    world = bootstrap.new_world(PARAMS, run_id="io")
    run_round(world, PARAMS, {})
    team = world.teams["team_01"]
    path = report.render(team, 1, tmp_path)
    html = path.read_text(encoding="utf-8")

    assert path.exists()
    assert "Contribution margin" in html and "Service level" in html
    # The diagnosis is the point of the report, not the numbers.
    assert any(v[0] in html for v in report.BINDING.values())
    # Biased and purchased metrics must be marked.
    assert "over-attributed" in html and "purchased study" in html


def test_report_shows_movement_against_the_prior_round(tmp_path):
    world = bootstrap.new_world(PARAMS, run_id="io")
    run_round(world, PARAMS, {})
    run_round(world, PARAMS, {"team_01": {"3.1": 1_200_000}})
    html = report.render(world.teams["team_01"], 2, tmp_path).read_text(encoding="utf-8")
    assert 'class="d' in html
