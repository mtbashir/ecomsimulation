"""Campaign settings under the ad budgets (decision 3.10).

What must hold: doing nothing plays the engine exactly as before, a broad
campaign is worth exactly what no campaign is, aiming at the real buyers pays
and aiming away from them costs, and every point given or taken can be put
into a sentence for the report.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

from ecomsim import bootstrap, params as P, targeting as T
from ecomsim.decisions import REGISTRY
from ecomsim.engine import run_game

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from strategies import campaigns  # noqa: E402

SPEND = {"meta": 468_000, "tiktok": 168_000, "google_search": 234_000}
HAIR_OIL_RIGHT = {"channel": "meta", "skus": ["SKU-08"], "ages": ["25-34", "35-44"],
                  "gender": "female", "geo": ["T2", "Rest"], "interests": ["home"],
                  "language": "urdu", "format": "feed", "objective": "conversions"}
HAIR_OIL_WRONG = {"channel": "meta", "skus": ["SKU-08"], "ages": ["18-24"],
                  "gender": "male", "geo": ["T1"], "interests": ["fashion"],
                  "language": "english", "format": "reels"}


@pytest.fixture(scope="module")
def p():
    return P.load()


def _all(p):
    return [s["code"] for s in p.skus]


def _quality(p, raw, sold=None):
    sold = sold or _all(p)
    cs = T.clean([raw], sold)
    return T.channel_scores(cs, SPEND, p, sold)[raw["channel"]]


def _play(strategy, rounds=5, overrides=None):
    p = P.load(overrides or {})
    world = bootstrap.new_world(p, run_id="targeting")
    run_game(world, p, strategy=strategy, rounds=rounds)
    return world


# --- The truth it scores against -------------------------------------------------

def test_every_product_has_an_audience_and_every_code_is_known(p):
    assert {a["code"] for a in p.audiences} == {s["code"] for s in p.skus}
    for a in p.audiences:
        assert a["core_age"] in T.AGES and (not a["second_age"] or a["second_age"] in T.AGES)
        assert 0 <= float(a["female_share"]) <= 1
        assert all(t in T.TIERS for t in str(a["geo"]).split("|"))
        assert a["interest_1"] in T.INTERESTS
        assert not a["interest_2"] or a["interest_2"] in T.INTERESTS
        assert a["language"] in T.LANGUAGES and a["format"] in T.FORMATS
        assert a["purchase"] in T.OBJECTIVE_FIT["conversions"]
        assert a["channel_1"] in T.CHANNELS
        assert a["mistake"], "the debrief needs the usual mistake for every product"


def test_platform_pools_add_up(p):
    for ch in T.CHANNELS:
        pool = p.platform(ch)
        assert sum(float(pool[c]) for c in T.AGES.values()) == pytest.approx(1.0)
        assert sum(float(pool[c]) for c in T.TIERS.values()) == pytest.approx(1.0)


# --- Neutrality -------------------------------------------------------------------

def test_broad_campaign_scores_exactly_one(p):
    for ch in T.CHANNELS:
        row = _quality(p, {"channel": ch})
        assert row["quality"] == pytest.approx(1.0, abs=1e-9)
        assert row["traffic"] == pytest.approx(1.0, abs=1e-9)
        assert row["cvr"] == pytest.approx(1.0, abs=1e-9)


def test_broad_campaigns_play_the_same_game_as_none():
    broad = [{"channel": ch} for ch in T.CHANNELS]
    none = _play(lambda w, r, t: {})
    aimed = _play(lambda w, r, t: {"3.10": broad})
    for tid in none.teams:
        a, b = none.teams[tid].history[-1], aimed.teams[tid].history[-1]
        assert b["revenue_net"] == pytest.approx(a["revenue_net"], rel=1e-9)
        assert b["cash_balance"] == pytest.approx(a["cash_balance"], rel=1e-9)


def test_zero_slope_switches_the_whole_layer_off():
    sharp_all = lambda w, r, t: {"3.10": campaigns.sharp(w_params[0], w.teams[t].active_skus)}
    w_params = [P.load()]
    none = _play(lambda w, r, t: {}, overrides={"targeting_traffic_slope": 0,
                                                "targeting_cvr_slope": 0})
    aimed = _play(sharp_all, overrides={"targeting_traffic_slope": 0,
                                        "targeting_cvr_slope": 0})
    for tid in none.teams:
        assert (aimed.teams[tid].history[-1]["revenue_net"]
                == pytest.approx(none.teams[tid].history[-1]["revenue_net"], rel=1e-9))


def test_campaigns_only_count_once_the_decision_opens():
    """Unlocked from round 3 on the default schedule: a setup submitted
    earlier is ignored, not half-applied."""
    assert REGISTRY["3.10"].unlock_round == 3
    wrong = [dict(HAIR_OIL_WRONG, skus=[])]
    none = _play(lambda w, r, t: {}, rounds=2)
    early = _play(lambda w, r, t: {"3.10": wrong}, rounds=2)
    for tid in none.teams:
        assert (early.teams[tid].history[-1]["revenue_net"]
                == none.teams[tid].history[-1]["revenue_net"])


# --- It pays to be right -----------------------------------------------------------

def test_aiming_at_the_buyers_beats_aiming_away_from_them(p):
    right, wrong = _quality(p, HAIR_OIL_RIGHT), _quality(p, HAIR_OIL_WRONG)
    assert right["quality"] > 1.5 > 1.0 > 0.5 > wrong["quality"]
    assert right["traffic"] > 1.0 > wrong["traffic"]
    assert right["cvr"] > 1.0 > wrong["cvr"]


def test_the_effect_is_bounded(p):
    right, wrong = _quality(p, HAIR_OIL_RIGHT), _quality(p, HAIR_OIL_WRONG)
    for row in (right, wrong):
        assert abs(row["traffic"] - 1) <= p["targeting_traffic_cap"] + 1e-9
        assert abs(row["cvr"] - 1) <= p["targeting_cvr_cap"] + 1e-9


def test_one_campaign_for_products_with_different_buyers_loses_to_splitting(p):
    oil_and_serum = ["SKU-08", "SKU-09"]
    lumped = _quality(p, {"channel": "meta", "skus": oil_and_serum,
                          "ages": ["35-44"], "gender": "female", "geo": ["T2"]})
    split = T.channel_scores(T.clean([
        dict(HAIR_OIL_RIGHT, share=0.5),
        {"channel": "meta", "share": 0.5, "skus": ["SKU-09"], "ages": ["18-24", "25-34"],
         "gender": "female", "geo": ["T1"], "interests": ["beauty"],
         "language": "english", "format": "reels", "objective": "conversions"},
    ], _all(p)), SPEND, p, _all(p))["meta"]
    assert split["quality"] > lumped["quality"]


def test_too_narrow_an_audience_tires(p):
    narrow = dict(HAIR_OIL_RIGHT, ages=["35-44"], interests=["home"])
    small = T.channel_scores(T.clean([narrow], _all(p)), {"meta": 50_000}, p, _all(p))
    large = T.channel_scores(T.clean([narrow], _all(p)), {"meta": 2_000_000}, p, _all(p))
    assert small["meta"]["campaigns"][0]["fatigue"] == 1.0
    assert large["meta"]["campaigns"][0]["fatigue"] < 0.8


def test_retargeting_everything_is_worse_than_retargeting_some(p):
    all_in = T.channel_scores(T.clean([{"channel": "meta", "objective": "retargeting"}]),
                              SPEND, p, _all(p))["meta"]
    some = T.channel_scores(T.clean([
        {"channel": "meta", "objective": "retargeting", "share": 0.25},
        {"channel": "meta", "share": 0.75}]), SPEND, p, _all(p))["meta"]
    assert some["quality"] > 1.0 > all_in["quality"]


def test_sharp_beats_careless_in_a_real_game():
    p = P.load()

    def play(how):
        def strategy(w, r, t):
            return {"3.10": getattr(campaigns, how)(p, w.teams[t].active_skus)} if how else {}
        return _play(strategy, rounds=6)
    none, sharp, careless = play(None), play("sharp"), play("careless")
    rev = lambda w: sum(t.history[-1]["revenue_net"] for t in w.teams.values())
    assert rev(sharp) > rev(none) > rev(careless)


# --- The submitted value -------------------------------------------------------------

def test_clean_drops_what_it_does_not_know_and_normalises_shares():
    out = T.clean([
        {"channel": "meta", "share": 3, "ages": ["18-24", "99+"], "gender": "robots",
         "interests": ["beauty", "fashion", "home", "deals"], "objective": "fame"},
        {"channel": "meta", "share": 1},
        {"channel": "myspace", "share": 1},
        "not a campaign",
    ], sold=["SKU-01"])
    assert [c["channel"] for c in out] == ["meta", "meta"]
    assert [c["share"] for c in out] == [0.75, 0.25]
    first = out[0]
    assert first["ages"] == ["18-24"] and first["gender"] == "all"
    assert first["objective"] == "traffic" and len(first["interests"]) == T.MAX_INTERESTS
    assert T.clean("junk") == []


def test_clean_keeps_at_most_three_campaigns_a_channel_and_only_products_sold():
    out = T.clean([{"channel": "tiktok", "skus": ["SKU-01", "SKU-02"]}] * 5, sold=["SKU-01"])
    assert len(out) == T.MAX_PER_CHANNEL
    assert all(c["skus"] == ["SKU-01"] for c in out)


# --- Explaining it ------------------------------------------------------------------------

def test_findings_name_the_mistake_and_the_buyer(p):
    row = _quality(p, dict(HAIR_OIL_WRONG, name="Oil to lads"))
    text = " ".join(T.findings(row["campaigns"][0], p, row))
    assert "“Oil to lads” targets men" in text
    assert "70% of hair oil buyers are women" in text
    assert "Tier 2" in text and "Urdu" in text


def test_a_good_campaign_is_told_so(p):
    row = _quality(p, dict(HAIR_OIL_RIGHT, name="Oil"))
    text = " ".join(T.findings(row["campaigns"][0], p, row))
    assert "reaches the people who buy hair oil" in text


def test_a_broad_campaign_is_not_nagged(p):
    for ch in T.CHANNELS:
        row = _quality(p, {"channel": ch})
        assert T.findings(row["campaigns"][0], p, row) == []


def test_every_paid_channel_reports_its_numbers_even_without_campaigns():
    world = _play(lambda w, r, t: {}, rounds=3)
    for team in world.teams.values():
        rows = team.history[-1]["campaigns"]
        assert {r["channel"] for r in rows} == set(T.CHANNELS)
        for r in rows:
            assert r["impressions"] > 0 and r["clicks"] > 0 and r["orders"] > 0
            assert 0 < r["ctr"] < 1 and 0 < r["cvr"] < 1 and r["roas"] > 0


def test_campaign_spend_adds_up_to_the_budget():
    p = P.load()
    world = _play(lambda w, r, t: {"3.10": campaigns.sharp(p, w.teams[t].active_skus)},
                  rounds=4)
    for team in world.teams.values():
        rows = team.history[-1]["campaigns"]
        for ch, budget in (("meta", 468_000), ("tiktok", 168_000),
                           ("google_search", 234_000)):
            assert sum(r["spend"] for r in rows if r["channel"] == ch) == pytest.approx(budget)


def test_debrief_reads_the_table(p):
    d = T.debrief(p, "SKU-08")
    assert d["age"].startswith("35-44") and "Tier 2" in d["where"]
    assert d["mistake"]


# --- A/B tests ---------------------------------------------------------------------

def _ab(a, b, share_a=0.5, channel="meta"):
    return [dict(a, channel=channel, name="A", test="A", share=share_a),
            dict(b, channel=channel, name="B", test="B", share=1 - share_a)]


def _ab_game(a, b, rounds=6, share_a=0.5, run_id="ab"):
    p = P.load()
    world = bootstrap.new_world(p, run_id=run_id)
    run_game(world, p, rounds=rounds, strategy=lambda w, r, t:
             {"3.10": _ab(a, b, share_a)} if t == "team_01" and r >= 3 else {})
    return world.teams["team_01"]


def test_a_test_is_exactly_one_a_against_one_b():
    assert [c.get("test") for c in T.clean(_ab({}, {}))] == ["A", "B"]
    lone = T.clean([{"channel": "meta", "test": "A"}, {"channel": "meta"}])
    assert all("test" not in c for c in lone)
    twins = T.clean([{"channel": "meta", "test": "A"}, {"channel": "meta", "test": "A"}])
    assert all("test" not in c for c in twins)
    split = T.clean([{"channel": "meta", "test": "A"}, {"channel": "tiktok", "test": "B"}])
    assert all("test" not in c for c in split), "a test compares within one channel"


def test_marking_a_test_changes_nothing_but_the_report():
    """The flag only adds sampling noise to how the pair's orders are
    reported. The business, the cash and every other team are untouched."""
    p = P.load()
    a, b = {"gender": "female"}, {}
    plain = lambda w, r, t: ({"3.10": [dict(c, test="") for c in _ab(a, b)]}
                             if t == "team_01" and r >= 3 else {})
    tested = lambda w, r, t: {"3.10": _ab(a, b)} if t == "team_01" and r >= 3 else {}
    x, y = _play(plain, rounds=5), _play(tested, rounds=5)
    for tid in x.teams:
        hx, hy = x.teams[tid].history[-1], y.teams[tid].history[-1]
        assert hy["revenue_net"] == hx["revenue_net"]
        assert hy["cash_balance"] == hx["cash_balance"]
    rows_x = {r["name"]: r for r in x.teams["team_01"].history[-1]["campaigns"]}
    rows_y = {r["name"]: r for r in y.teams["team_01"].history[-1]["campaigns"]}
    assert (rows_y["A"]["orders"] + rows_y["B"]["orders"]
            == pytest.approx(rows_x["A"]["orders"] + rows_x["B"]["orders"]))
    assert rows_y["A"]["orders"] != pytest.approx(rows_x["A"]["orders"], rel=1e-6), \
        "a test's orders are a draw, not the average"


def test_the_draw_is_deterministic():
    a = _ab_game({"gender": "female"}, {}, rounds=4)
    b = _ab_game({"gender": "female"}, {}, rounds=4)
    assert a.history[-1]["ab_tests"] == b.history[-1]["ab_tests"]


def test_unchanged_months_pool_and_an_edit_restarts_the_count():
    p = P.load()
    world = bootstrap.new_world(p, run_id="pool")
    def strat(w, r, t):
        if t != "team_01" or r < 3:
            return {}
        b = {} if r < 5 else {"language": "urdu"}
        return {"3.10": _ab({"gender": "female"}, b)}
    run_game(world, p, strategy=strat, rounds=6)
    months = [rec["ab_tests"][0]["months"] for rec in world.teams["team_01"].history[2:]]
    assert months == [1, 2, 1, 2]


def test_an_identical_pair_is_called_a_test_of_chance():
    t = _ab_game({"objective": "conversions"}, {"objective": "conversions"}).history[-1]
    verdict = t["ab_tests"][0]
    assert verdict["call"] == "none" and verdict["diffs"] == []
    assert "tests nothing but chance" in verdict["verdict"]


def test_changing_several_things_at_once_is_called_out():
    t = _ab_game({"gender": "female", "language": "urdu", "format": "feed"}, {})
    verdict = t.history[-1]["ab_tests"][0]
    assert verdict["diffs"] == ["gender", "language", "format"]
    assert "Test one thing at a time" in verdict["verdict"]


def test_a_big_real_difference_is_found_and_a_sliver_of_budget_is_not_enough():
    right = {"gender": "female", "ages": ["25-34", "35-44"], "objective": "conversions"}
    wrong = {"gender": "male", "ages": ["18-24"], "objective": "conversions"}
    fair = _ab_game(right, wrong, rounds=5).history[-1]["ab_tests"][0]
    assert fair["call"] == "A" and fair["confidence"] >= 0.95
    tiny = _ab_game(right, {"gender": "female", "ages": ["25-34", "35-44"],
                            "objective": "traffic"},
                    rounds=4, share_a=0.05).history[-1]["ab_tests"][0]
    assert tiny["call"] in ("open", "leaning")
