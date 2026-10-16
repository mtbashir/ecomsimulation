"""Score impact and coaching: one record of how decisions move the score.

The handbook tells teams how each decision moves their score; the scoring
guide links each measure back to those decisions; the instructor's console
says where a team's points went and which of its own decisions to look at.
All three read web/handbook.SCORE_IMPACT and scoring.breakdown.
"""
import sys
sys.path.insert(0, "src")

import pytest

from ecomsim import bootstrap, params as P, scoring
from ecomsim.engine import run_round


def _played(rules_from, months=5, n=3):
    params = P.load({"n_teams": n, "events_enabled": 0})
    world = bootstrap.new_world(params, run_id="coach")
    world.rules_from = rules_from
    ids = list(world.teams)
    plans = [{ids[0]: {"3.1": 900_000.0, "6.1": 300_000.0, "12.5": "Why we did it"},
              ids[1]: {"3.4": 600_000.0, "2.2": 0.3}}] * months
    for p in plans:
        run_round(world, params, p)
    return params, world


@pytest.mark.parametrize("rules_from", [1, 3, 99])
def test_the_breakdown_adds_up_to_the_final_score(rules_from):
    params, world = _played(rules_from)
    rejected = {(list(world.teams)[0], 2)}
    for team in world.teams.values():
        card = scoring.final_score(team, params, world.teams, rejected)
        parts = scoring.breakdown(team, params, world.teams, rejected)
        assert set(parts) == set(scoring.PILLAR_OF)
        for p in ("p1", "p2", "p3", "p4", "p5", "p6"):
            got = sum(v["points"] for k, v in parts.items() if scoring.PILLAR_OF[k] == p)
            assert got == pytest.approx(card[p], abs=1e-9), p


def test_every_decision_says_how_it_moves_the_score():
    from ecomsim.decisions import REGISTRY
    from ecomsim.web import handbook as hb
    assert set(hb.SCORE_IMPACT) == set(REGISTRY)
    for code, lines in hb.SCORE_IMPACT.items():
        assert lines, code
        for measure, sign, why in lines:
            assert measure in scoring.PILLAR_OF and sign in "+-" and why, code


def test_every_measure_has_a_decision_that_can_raise_it():
    from ecomsim.web import handbook as hb
    for key in scoring.PILLAR_OF:
        if key != "decisions":           # raised by filling in any decision
            assert hb.levers_for(key, "+"), key


def test_the_console_shows_each_team_where_its_points_went(tmp_path):
    from ecomsim import coach, console
    params, world = _played(1)
    subs = {t: {} for t in world.teams}
    html = console.render(world, params, tmp_path, submissions=subs).read_text()
    assert html.count('class="coach"') == len(world.teams)
    assert "Biggest Gaps" in html or "Biggest gaps" in html
    assert 'href="/admin/playbook#customer-value"' in html
    assert 'href="/handbook#d' in html, "levers open their handbook entries"


def test_a_gap_names_the_teams_own_decision():
    from ecomsim import coach
    params, world = _played(1)
    tid = list(world.teams)[1]                     # TikTok-heavy, 30% off
    team = world.teams[tid]
    d = {**team.standing, "3.4": 600_000.0, "3.1": 100_000.0, "2.2": 0.3, "6.1": 0}
    parts = scoring.breakdown(team, params, world.teams)
    text = " ".join(coach._diagnose("repeat", team, params, d, parts["repeat"]))
    assert "TikTok" in text and "deal-driven" in text and "CRM" in text
    runway = dict(parts["runway"], value=99.0)
    assert "30%" in " ".join(coach._diagnose("runway", team, params, d, runway))
