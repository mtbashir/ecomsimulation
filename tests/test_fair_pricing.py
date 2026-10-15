"""Like-for-like pricing: for games set up from now on.

Three things let a team win by pricing high, all found by playing the game:

1. The price index compared rupees across different products, so a shelf of
   Rs 600 dish liquid looked cheap next to one of Rs 2,900 serum - premium
   homecare topped the table by looking like a bargain.
2. Conversion had a floor at half, so beyond ~1.5x the market a higher price
   cost nothing more.
3. Price was judged without the segment's willingness to pay, so Quality
   Loyalists took a price 45% over market almost as happily as Value Seekers.

A game already trading keeps the model it started with.
"""
from __future__ import annotations

import pytest

from ecomsim import bootstrap, founding as F, params as P, scoring
from ecomsim.engine import run_round
from ecomsim.modules import m07_share, m08_conversion
from ecomsim.web import db, service

PARAMS = P.load({})


# --- Only for new games ---------------------------------------------------------

def test_a_new_game_prices_like_for_like(tmp_path):
    path = tmp_path / "g.db"
    db.init(path, "x", 3, admin_password="x")
    con = db.connect(path)
    assert db.fair_pricing(con) is True
    assert bootstrap.new_world(PARAMS).fair_pricing is True


def test_a_game_already_trading_keeps_its_price_model(tmp_path):
    path = tmp_path / "g.db"
    db.init(path, "x", 3, admin_password="x")
    con = db.connect(path)
    # As a database from before the column: trading, and no value recorded.
    con.execute("UPDATE game SET round = 4, fair_pricing = NULL")
    con.commit()
    db.migrate(con)
    assert db.fair_pricing(con) is False


def test_starting_the_next_game_turns_it_on(tmp_path):
    path = tmp_path / "g.db"
    db.init(path, "x", 3, admin_password="x")
    con = db.connect(path)
    con.execute("UPDATE game SET round = 4, fair_pricing = 0")
    con.commit()
    db.new_game(con, path, name="Next", teams=3, rounds=12,
                start_mode="founding", keep_overrides=False)
    assert db.fair_pricing(con) is True


def test_an_old_saved_world_reads_the_old_model():
    world = bootstrap.new_world(PARAMS)
    del world.__dict__["fair_pricing"]          # as unpickled from before
    assert getattr(world, "fair_pricing", False) is False


# --- The three mechanisms ----------------------------------------------------------

def _priced_world(fair: bool):
    """Two teams: one sells cheap homecare at premium prices, one sells the
    usual skincare at catalogue price."""
    world = bootstrap.new_world(PARAMS, n_teams=2)
    world.fair_pricing = fair
    home = [s["code"] for s in PARAMS.skus if s["category"] == "homecare"]
    skin = [s["code"] for s in PARAMS.skus if s["category"] == "skincare"]
    a, b = world.teams.values()
    a.active_skus, b.active_skus = home, skin
    a.sku_prices = {c: float(PARAMS.sku(c)["list_price"]) * 1.5 for c in home}
    return world, a.team_id, b.team_id


@pytest.mark.parametrize("fair", [False, True])
def test_a_marked_up_cheap_range_is_seen_as_expensive_only_like_for_like(fair):
    from ecomsim.modules import m00_resolve
    world, home, skin = _priced_world(fair)
    ctx = {"resolved": {t: {} for t in world.teams}}
    m00_resolve.run(world, PARAMS, {}, ctx)
    index = ctx["price_index"]
    if fair:
        assert index[home] > 1.2, "50% over catalogue is expensive, whatever it sells"
        assert index[home] > index[skin]
    else:
        assert index[home] < index[skin], "the old model judged the rupee level"


def test_conversion_keeps_falling_past_one_and_a_half_times_the_market():
    team = bootstrap.new_world(PARAMS, n_teams=1).teams["team_01"]

    def cr(index, fair):
        ctx = {"price_index": {team.team_id: index}, "fair_pricing": fair}
        return m08_conversion._conversion_rate(team, PARAMS, ctx)

    assert cr(2.0, False) == pytest.approx(cr(1.6, False)), "the old floor"
    assert cr(2.0, True) < cr(1.6, True) * 0.75


def test_price_above_what_a_segment_will_pay_drives_it_away():
    team = bootstrap.new_world(PARAMS, n_teams=1).teams["team_01"]
    seg = {s["code"]: s for s in PARAMS.segments}

    def drop(code, fair):
        """Utility lost going from market price to 1.45x, in this segment."""
        u = {i: m07_share._utility(team, seg[code], PARAMS,
                                   {"price_index": {team.team_id: i},
                                    "fair_pricing": fair})
             for i in (1.0, 1.45)}
        return u[1.0] - u[1.45]

    # Premium/Gifting will pay 1.6x: no extra penalty. Quality Loyalists 1.25x.
    assert drop("premium_gifting", True) == pytest.approx(drop("premium_gifting", False))
    assert drop("quality_loyalists", True) > drop("quality_loyalists", False)
    assert drop("value_seekers", True) - drop("value_seekers", False) > \
        drop("quality_loyalists", True) - drop("quality_loyalists", False)


# --- The scenario that found it ----------------------------------------------------

def _class(path, niche_prices: float):
    """Six teams in the usual skincare and haircare, one taking homecare and
    hygiene nobody else stocks - at premium prices."""
    db.init(path, "x", 7, admin_password="x")
    con = db.connect(path)
    params = service.load_params(con)
    skus = {s["code"]: s for s in params.skus}
    usual = [c for c, s in sorted(skus.items(), key=lambda kv: -float(kv[1]["revenue_weight"]))
             if s["category"] != "homecare"][:14]
    niche = [c for c, s in skus.items() if s["category"] in ("homecare", "hygiene", "baby")] \
        + [c for c, s in skus.items() if s["category"] == "skincare"][:1]
    focus = [["urban_convenience", "quality_loyalists"], ["quality_loyalists", "premium_gifting"],
             ["urban_convenience", "deal_hunters"], ["premium_gifting", "urban_convenience"],
             ["deal_hunters", "quality_loyalists"], ["urban_convenience", "premium_gifting"]]
    for i in range(7):
        f = F.Founding.default(params)
        if i < 6:
            f.assortment, f.segment_priority = usual, focus[i]
        else:
            f.tier, f.assortment = "premium", niche
            f.segment_priority = ["value_seekers", "deal_hunters"]
            f.prices = {c: F.reference_price(skus[c], "premium") * niche_prices for c in niche}
        db.save_founding(con, f"team_{i + 1:02d}", service.founding_to_dict(f),
                         "x", submitted=True)
    for _ in range(12):
        service.process_round(con)
    world = db.load_world(con)
    scores = {t: scoring.final_score(team, params, world.teams)["total"]
              for t, team in world.teams.items()}
    return sorted(scores, key=lambda t: -scores[t]).index("team_07") + 1


def test_premium_homecare_no_longer_wins_by_looking_cheap(tmp_path):
    assert _class(tmp_path / "g.db", 1.25) >= 5, \
        "a marked-up niche nobody else is in should not top the table"


# --- Category focus is read off the shelf ----------------------------------------

def test_category_focus_is_what_the_range_actually_sells():
    home = [s["code"] for s in PARAMS.skus if s["category"] == "homecare"]
    hyg = [s["code"] for s in PARAMS.skus if s["category"] == "hygiene"]
    baby = [s["code"] for s in PARAMS.skus if s["category"] == "baby"][:1]
    assert set(F.categories_of(home + hyg + baby, PARAMS)) == {"homecare", "hygiene"}
    assert F.categories_of([], PARAMS) == []


def test_a_ticked_category_the_range_does_not_sell_is_ignored(tmp_path):
    from werkzeug.datastructures import MultiDict
    path = tmp_path / "g.db"
    db.init(path, "x", 3, admin_password="x")
    params = service.load_params(db.connect(path))
    skin = [s["code"] for s in params.skus if s["category"] in ("skincare", "haircare")]
    form = MultiDict([("categories", "homecare"), ("categories", "baby")]
                     + [("assortment", c) for c in skin])
    f = service.founding_from_form(form, params)
    assert set(f.categories) == {"skincare", "haircare"}
