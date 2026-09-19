"""Round 0 founding round (docs/05-start-mode.md).

The governing principle: Year 0 differentiates STRATEGY, not ENDOWMENT. Teams
should end Round 0 with different shapes of business, not different sizes.
"""
from __future__ import annotations

import pytest

from ecomsim import bootstrap, founding as F, params as P
from ecomsim.engine import run_round
from ecomsim.founding import (
    Founding, FULFILMENT, TECH_STACKS, TIERS, apply, check_balance, pro_forma, validate,
)

PARAMS = P.load({"events_enabled": 0})
CAPITAL = PARAMS["starting_cash"]


def make(alloc=(0.42, 0.24, 0.16), **kw) -> Founding:
    f = Founding.default(PARAMS)
    for k, v in kw.items():
        setattr(f, k, v)
    inv, mkt, tech = alloc
    f.capital_inventory = CAPITAL * inv
    f.capital_marketing = CAPITAL * mkt
    f.capital_technology = CAPITAL * tech
    f.capital_reserve = CAPITAL * (1 - inv - mkt - tech)
    return f


def test_default_is_submittable_and_balanced():
    f = make()
    assert validate(f, PARAMS) == []
    assert check_balance(f, PARAMS) == []


def test_allocations_must_sum_to_capital():
    f = make()
    f.capital_reserve += 1_000_000
    assert any("must equal" in e for e in validate(f, PARAMS))


@pytest.mark.parametrize("alloc,expected", [
    ((0.80, 0.08, 0.02), "inventory"),   # the classic Round-3 insolvency
    ((0.30, 0.55, 0.10), "reserve"),
    ((0.25, 0.10, 0.60), "technology"),
])
def test_capital_floors_and_ceilings(alloc, expected):
    assert any(expected in e for e in validate(make(alloc), PARAMS))


def test_assortment_must_be_twelve_to_eighteen():
    assert any("12-18" in e for e in validate(make(assortment=["SKU-01"] * 4), PARAMS))


def test_capex_must_be_affordable():
    f = make(alloc=(0.60, 0.24, 0.02), tech_stack="custom", fulfilment="own")
    assert any("capex" in e for e in validate(f, PARAMS))


# --- The principle: different shapes, not different sizes ----------------------

DIRECTIONS = {
    "default":     make(),
    "premium":     make((0.36, 0.32, 0.14), tier="premium"),
    "value":       make(tier="value", sourcing="import"),
    "marketplace": make((0.36, 0.32, 0.14), model="marketplace_first"),
    "prepaid":     make((0.40, 0.28, 0.14), cod_enabled=False),
    "lean":        make((0.42, 0.30, 0.08), tech_stack="basic"),
}


@pytest.mark.parametrize("name", list(DIRECTIONS))
def test_every_strategic_direction_is_viable(name):
    """Each defensible direction must have at least one submittable form.

    If premium or marketplace-first cannot be made to balance, that founding
    decision is decoration.
    """
    f = DIRECTIONS[name]
    assert validate(f, PARAMS) == [], name
    assert check_balance(f, PARAMS) == [], name


def test_directions_differ_in_shape():
    """Margin, AOV and CAC must genuinely separate across directions."""
    shapes = {n: pro_forma(f, PARAMS) for n, f in DIRECTIONS.items()}
    cm = [s["contribution_margin_pct"] for s in shapes.values()]
    cac = [s["cac"] for s in shapes.values()]
    aov = [s["aov_net"] for s in shapes.values()]
    assert max(cm) - min(cm) > 0.08, f"contribution margins too alike: {cm}"
    assert max(cac) / min(cac) > 1.5, f"CAC too alike: {cac}"
    assert max(aov) / min(aov) > 1.15, f"AOV too alike: {aov}"


def test_directions_do_not_differ_in_size():
    """...but none may be more than 15% off the baseline (docs/05)."""
    target = PARAMS["baseline_team_revenue"]
    for name, f in DIRECTIONS.items():
        rev = pro_forma(f, PARAMS)["revenue_gross"]
        assert abs(rev - target) / target <= 0.15, f"{name}: {rev:,.0f} vs {target:,.0f}"


def test_bad_pairings_are_rejected():
    """Some combinations should fail - that is what the preview is for."""
    assert check_balance(make(tier="value", sourcing="local"), PARAMS)
    assert check_balance(
        make((0.36, 0.30, 0.14), model="marketplace_first", tier="premium"), PARAMS)


# --- Applying a configuration --------------------------------------------------

def test_apply_charges_capex_and_inventory():
    from ecomsim import bootstrap

    f = make(tech_stack="custom")
    world = bootstrap.new_world(PARAMS, n_teams=2, run_id="apply")
    team = world.teams[next(iter(world.teams))]
    apply(f, team, PARAMS)

    expected = (CAPITAL - TECH_STACKS["custom"][0] - FULFILMENT["3pl"][0]
                - f.capital_inventory)
    assert abs(team.cash - expected) < 1.0
    assert sum(team.inventory.values()) > 0
    assert team.active_skus == f.assortment


def test_tier_moves_price_and_cost():
    from ecomsim import bootstrap

    world = bootstrap.new_world(PARAMS, n_teams=2, run_id="tier")
    tids = list(world.teams)
    apply(make(tier="premium"), world.teams[tids[0]], PARAMS)
    apply(make(tier="value"), world.teams[tids[1]], PARAMS)
    assert world.teams[tids[0]].price_multiplier > world.teams[tids[1]].price_multiplier
    assert TIERS["premium"][1] > TIERS["value"][1]


def test_a_team_is_charged_the_cost_the_setup_page_quoted():
    """A page that quotes a cost the P&L contradicts is worse than no page."""
    from ecomsim.web import service

    params = P.load({"n_teams": 3, "events_enabled": 0})
    f = F.Founding.default(params)
    f.tier, f.sourcing = "premium", "import"
    f.prices = {c: F.reference_price(params.sku(c), "premium") for c in f.assortment}

    rows = {r["code"]: r for r in service.product_catalogue(params, f)}
    world = bootstrap.new_world(params, run_id="cost")
    F.apply(f, world.teams["team_01"], params)
    run_round(world, params, {})

    team = world.teams["team_01"]
    h = team.history[-1]
    quoted = service.blended_margin(list(rows.values()))["gross_margin"]
    realised = h["gross_margin_pct"]
    # Realised is a little lower - the prepaid discount and write-offs land
    # after the shelf - but they must not be telling different stories.
    assert realised < quoted, "realised margin sits below shelf margin"
    assert quoted - realised < 0.04, (
        f"shelf margin {quoted:.1%} and realised {realised:.1%} have diverged")


def test_sourcing_and_positioning_move_what_a_unit_costs():
    """Both were described as cost decisions and only touched opening stock."""
    params = P.load({"n_teams": 3, "events_enabled": 0})

    def cogs_per_unit(tier, sourcing):
        f = F.Founding.default(params)
        f.tier, f.sourcing = tier, sourcing
        world = bootstrap.new_world(params, run_id="cost")
        F.apply(f, world.teams["team_01"], params)
        run_round(world, params, {})
        h = world.teams["team_01"].history[-1]
        return h["pnl"]["cogs"] / max(h["orders"], 1)

    assert cogs_per_unit("mainstream", "import") < cogs_per_unit("mainstream", "mixed")
    assert cogs_per_unit("mainstream", "local") > cogs_per_unit("mainstream", "mixed")
    assert cogs_per_unit("premium", "mixed") > cogs_per_unit("value", "mixed")


def test_a_team_that_prices_its_own_shelf_is_charged_its_own_prices():
    params = P.load({"n_teams": 3, "events_enabled": 0})

    def aov(multiple):
        f = F.Founding.default(params)
        f.prices = {c: F.reference_price(params.sku(c), f.tier) * multiple
                    for c in f.assortment}
        world = bootstrap.new_world(params, run_id="price")
        F.apply(f, world.teams["team_01"], params)
        run_round(world, params, {})
        return world.teams["team_01"].history[-1]["aov_net"]

    assert aov(1.5) > aov(1.0) > aov(0.7), "the price a team set must be the price"


def test_never_pricing_anything_leaves_the_tier_in_charge():
    """A going-concern game, and a team that skipped setup, must be unaffected."""
    params = P.load({"n_teams": 3, "events_enabled": 0})

    def aov(tier):
        f = F.Founding.default(params)
        f.tier = tier
        assert not f.prices, "the default configuration must not price anything"
        world = bootstrap.new_world(params, run_id="tier")
        F.apply(f, world.teams["team_01"], params)
        run_round(world, params, {})
        return world.teams["team_01"].history[-1]["aov_net"]

    assert aov("premium") > aov("mainstream") > aov("value")
