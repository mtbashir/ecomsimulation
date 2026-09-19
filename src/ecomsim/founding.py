"""Round 0 - the founding round (docs/05-start-mode.md).

Every team receives identical capital and constraints, then makes fourteen
founding choices that produce different but balanced starting positions.

    Year 0 differentiates STRATEGY, not ENDOWMENT.

Teams should end Round 0 with different shapes of business, not different
sizes. Premium positioning yields lower volume, higher margin, higher repeat,
higher CAC, slower growth; value positioning the inverse. Neither is correct,
and the balance constraints below make sure neither is fatal either.
"""
from __future__ import annotations

from dataclasses import dataclass, field

CATEGORIES = ["skincare", "haircare", "hygiene", "homecare", "baby"]
TIERS = {
    # tier -> (price multiplier, unit-cost multiplier, rating bonus, CAC multiplier)
    "value":      (0.86, 0.90, -0.08, 0.88),
    "mainstream": (1.00, 1.00, 0.00, 1.00),
    "premium":    (1.24, 1.13, 0.12, 1.22),
}
MODELS = {
    # model -> (own-site traffic mult, marketplace share, commission exposure)
    "d2c":              (1.12, 0.00, 0.00),
    "hybrid":           (1.00, 0.35, 0.35),
    "marketplace_first": (0.82, 0.65, 0.65),
}
SOURCING = {
    # strategy -> (cost index, lead-time days, FX exposure)
    "local": (1.06, 9, 0.0),
    "mixed": (1.00, 14, 0.5),
    "import": (0.91, 22, 1.0),
}
TECH_STACKS = {
    # stack -> (capex, ux ceiling, rounds to launch, ongoing per round)
    "basic":    (400_000, 0.55, 0, 40_000),
    "standard": (1_200_000, 0.75, 0, 90_000),
    "custom":   (2_800_000, 0.92, 2, 180_000),
}
FULFILMENT = {"3pl": (0, 1.00), "own": (2_400_000, 0.82)}
GATEWAYS = ["A", "B", "C"]

FOUNDING_RESEARCH = ["MR-01", "MR-06", "MR-11", "MR-15"]
FOUNDING_RESEARCH_DISCOUNT = 0.50


def reference_price(sku: dict, tier: str) -> float:
    """What the catalogue suggests for this product at this positioning.

    The starting point in the form, and the fallback for a product a team
    never priced. Teams are free to ignore it - that is the decision.
    """
    return round(float(sku["list_price"]) * TIERS.get(tier, TIERS["mainstream"])[0])


def cost_multiplier(sourcing: str, tier: str) -> float:
    """How a team's sourcing strategy and positioning scale its landed cost."""
    return (SOURCING.get(sourcing, SOURCING["mixed"])[0]
            * TIERS.get(tier, TIERS["mainstream"])[1])


def unit_cost(sku: dict, sourcing: str, tier: str, params=None,
              supplier_index: float = 1.0) -> float:
    """What one unit will actually cost, as the P&L will charge it.

    Must agree with M9: catalogue cost times the global cogs scale, the
    supplier's index, and the team's founding cost multiplier. A page that
    quotes a cost the P&L then contradicts is worse than quoting none.
    """
    scale = float(params["cogs_scale"]) if params is not None else 1.0
    return (float(sku["unit_cost"]) * scale * supplier_index
            * cost_multiplier(sourcing, tier))


class FoundingError(ValueError):
    """A founding configuration that cannot be submitted."""


@dataclass
class Founding:
    """The fourteen Round 0 decisions."""
    brand_name: str = "Unnamed"                       # D0.1
    positioning_statement: str = ""                   # D0.1
    categories: list[str] = field(default_factory=lambda: ["skincare", "haircare"])  # D0.2
    segment_priority: list[str] = field(default_factory=list)                        # D0.3
    tier: str = "mainstream"                          # D0.4
    model: str = "d2c"                                # D0.5
    assortment: list[str] = field(default_factory=list)                              # D0.6
    prices: dict[str, float] = field(default_factory=dict)                           # D0.6
    sourcing: str = "mixed"                           # D0.7
    capital_inventory: float = 0.0                    # D0.8
    capital_marketing: float = 0.0
    capital_technology: float = 0.0
    capital_reserve: float = 0.0
    tech_stack: str = "standard"                      # D0.9
    fulfilment: str = "3pl"                           # D0.10
    cod_enabled: bool = True                          # D0.11
    gateway: str = "A"
    headcount: dict[str, int] = field(                # D0.12
        default_factory=lambda: {"marketing": 2, "ops": 2, "cs": 4, "analytics": 1})
    research: list[str] = field(default_factory=list)                                # D0.13
    business_plan: str = ""                           # D0.14
    target_repeat_share: float = 0.0                  # stated in the plan
    target_cac: float = 0.0

    @classmethod
    def default(cls, params) -> "Founding":
        """A viable middle-of-the-road configuration, used as the fallback."""
        capital = params["starting_cash"]
        f = cls()
        f.capital_inventory = capital * 0.42
        f.capital_marketing = capital * 0.24
        f.capital_technology = capital * 0.16
        f.capital_reserve = capital * 0.18
        f.assortment = [s["code"] for s in sorted(
            params.skus, key=lambda s: -float(s["revenue_weight"]))[:14]]
        # Deliberately no prices. A team that never opened the form should be
        # priced by its positioning tier, the way a going-concern game is;
        # prices belong to teams that actually set them.
        f.segment_priority = [s["code"] for s in params.segments[:2]]
        return f


# --- Validation ----------------------------------------------------------------

def validate(f: Founding, params) -> list[str]:
    """Structural errors. Returns a list; empty means submittable."""
    capital = params["starting_cash"]
    errors: list[str] = []

    if len(f.categories) != 2 or any(c not in CATEGORIES for c in f.categories):
        errors.append("D0.2: pick exactly two categories from " + ", ".join(CATEGORIES))
    if len(f.segment_priority) != 2:
        errors.append(
            f"D0.3: choose exactly two priority segments "
            f"(got {len(f.segment_priority)})")
    if f.tier not in TIERS:
        errors.append(f"D0.4: tier must be one of {', '.join(TIERS)}")
    if f.model not in MODELS:
        errors.append(f"D0.5: model must be one of {', '.join(MODELS)}")
    if not 12 <= len(f.assortment) <= 18:
        errors.append(f"D0.6: opening assortment must be 12-18 SKUs (got {len(f.assortment)})")
    for code, price in (f.prices or {}).items():
        if code not in f.assortment:
            continue
        ref = float(params.sku(code)["list_price"])
        if price <= 0:
            errors.append(f"D0.6: {params.sku(code)['name']} needs a price")
        elif price > ref * 4:
            errors.append(
                f"D0.6: {params.sku(code)['name']} at {price:,.0f} is more than "
                f"four times the market reference of {ref:,.0f}")
    if f.sourcing not in SOURCING:
        errors.append(f"D0.7: sourcing must be one of {', '.join(SOURCING)}")
    if f.tech_stack not in TECH_STACKS:
        errors.append(f"D0.9: stack must be one of {', '.join(TECH_STACKS)}")
    if f.fulfilment not in FULFILMENT:
        errors.append("D0.10: fulfilment must be 3pl or own")
    if f.gateway not in GATEWAYS:
        errors.append("D0.11: gateway must be A, B or C")

    allocated = (f.capital_inventory + f.capital_marketing
                 + f.capital_technology + f.capital_reserve)
    if abs(allocated - capital) > 1:
        errors.append(
            f"D0.8: allocations total {allocated:,.0f}, must equal {capital:,.0f}")
    if allocated > 0:
        # Floors and ceilings exist because, given a free hand, roughly a third
        # of teams put ~80% of capital into stock and are insolvent by Round 3.
        # That is a real lesson, better taught by a Round 4 squeeze than by
        # elimination in Round 3.
        inv = f.capital_inventory / capital
        if not 0.25 <= inv <= 0.60:
            errors.append(f"D0.8: inventory is {inv:.0%} of capital, must be 25-60%")
        if f.capital_reserve / capital < 0.10:
            errors.append(
                f"D0.8: reserve is {f.capital_reserve / capital:.0%}, must be at least 10%")
        if f.capital_technology / capital > 0.55:
            errors.append(
                f"D0.8: technology is {f.capital_technology / capital:.0%}, at most 55%")

    capex = TECH_STACKS[f.tech_stack][0] if f.tech_stack in TECH_STACKS else 0
    capex += FULFILMENT[f.fulfilment][0] if f.fulfilment in FULFILMENT else 0
    if capex > f.capital_technology + f.capital_reserve:
        errors.append(
            f"D0.9/D0.10: chosen stack and fulfilment need {capex:,.0f} of capex, "
            f"but technology plus reserve is only "
            f"{f.capital_technology + f.capital_reserve:,.0f}")
    return errors


# --- Applying a founding configuration -----------------------------------------

def apply(f: Founding, team, params) -> None:
    """Turn founding choices into a starting position, in place.

    Differences show up as the SHAPE of the business - assortment, price tier,
    channel mix, cost base, opening stock - never as more or less endowment.
    """
    price_mult, cost_mult, rating_bonus, _cac = TIERS[f.tier]
    _traffic, mp_share, _comm = MODELS[f.model]
    _cost_index, lead_days, _fx = SOURCING[f.sourcing]
    capex, ux_ceiling, launch_rounds, _ongoing = TECH_STACKS[f.tech_stack]
    fulfil_capex, _fulfil_mult = FULFILMENT[f.fulfilment]

    team.active_skus = list(f.assortment)
    team.sku_prices = {c: float(p) for c, p in (f.prices or {}).items()
                       if c in f.assortment and float(p) > 0}
    team.founding = f
    team.price_multiplier = price_mult
    # Sourcing and positioning were described as cost decisions and only ever
    # touched the opening stock purchase. They follow the team now.
    team.cost_multiplier = _cost_index * cost_mult
    team.traffic_multiplier = _traffic
    team.rating = max(1.0, min(5.0, team.rating + rating_bonus))
    team.ux_score = min(ux_ceiling, 0.62 if launch_rounds == 0 else 0.42)
    team.cs_agents = f.headcount.get("cs", 4)

    # Capex is paid at founding, in full, and is not refundable.
    team.cash = params["starting_cash"] - capex - fulfil_capex
    if f.fulfilment == "own":
        team.warehouse_capacity = 6_000.0

    # Opening stock is bought with the inventory allocation, not handed over.
    unit_cost = _basket_cost(f, params) * team.cost_multiplier
    units = f.capital_inventory / max(unit_cost, 1.0)
    weights = {c: float(params.sku(c)["revenue_weight"]) for c in f.assortment}
    total_w = sum(weights.values()) or 1.0
    team.inventory = {c: units * w / total_w for c, w in weights.items()}
    team.cash -= f.capital_inventory


# --- Pro-forma preview ---------------------------------------------------------

def pro_forma(f: Founding, params) -> dict:
    """Projected Round 1 position, by RUNNING THE ENGINE for one round.

    This is what makes the founding round safe rather than a blind lottery:
    teams iterate against it before committing. Running the real engine means
    the preview cannot drift from the thing it previews - an approximation
    maintained alongside eighteen modules would.

    It is still a PROJECTION, not a promise: every rival is assumed to be an
    average operator, so Round 1 will deviate. That gap is the first lesson of
    the run, and it lands far better than being blindsided.
    """
    from . import bootstrap
    from .engine import run_round

    p = params
    world = bootstrap.new_world(p, n_teams=4, run_id="proforma")
    tid = next(iter(world.teams))
    apply(f, world.teams[tid], p)

    decisions = {tid: _founding_decisions(f, p)}
    ctx = run_round(world, p, decisions)
    team = world.teams[tid]
    h = team.history[-1]

    capex = TECH_STACKS[f.tech_stack][0] + FULFILMENT[f.fulfilment][0]
    burn = max(-h["pnl"]["ebitda"], 1.0)
    return {
        "sessions": h["sessions"],
        "orders": h["orders"],
        "conversion_rate": h["conversion_rate"],
        "aov_net": h["aov_net"],
        "revenue_gross": h["orders"] * h["aov_net"],
        "revenue_net": h["revenue_net"],
        "gross_margin_pct": h["gross_margin_pct"],
        "contribution_margin_pct": h["contribution_margin_pct"],
        "contribution": h["pnl"]["contribution"],
        "fixed_costs": h["pnl"]["below_line"],
        "ebitda": h["pnl"]["ebitda"],
        "monthly_marketing": h["pnl"]["marketing"],
        "cac": h["cac_blended"],
        "capex": capex,
        "opening_cash": h["cash_balance"],
        "runway_rounds": min(40.0, max(h["cash_balance"], 0.0) / burn),
        "service_level": h["service_level"],
        "binding_constraint": h["binding_constraint"],
    }


def _founding_decisions(f: Founding, params) -> dict:
    """The operating decisions a founding configuration implies for Round 1."""
    capital = params["starting_cash"]
    intensity = (f.capital_marketing / capital) / 0.24
    base = {"3.1": 468_000, "3.2": 234_000, "3.4": 168_000,
            "3.8": 200_000, "3.9": 267_000}
    d = {k: v * intensity for k, v in base.items()}
    d["7.2"] = {"local": "C", "mixed": "B", "import": "A"}[f.sourcing]
    d["1.5"] = {"value": "economy", "mainstream": "standard",
                "premium": "premium"}[f.tier]
    d["9.1"] = "on" if f.cod_enabled else "off"
    d["9.3"] = f.gateway
    d["10.1"] = f.headcount.get("cs", 4)
    d["4.1"] = "off" if f.model == "d2c" else "basic"
    d["12.1"] = list(f.research)
    return d


def check_balance(f: Founding, params) -> list[str]:
    """Balance constraints on the projection (docs/05).

    Every valid configuration must be viable. Teams should differ in the SHAPE
    of their business, not in whether it can survive.
    """
    pf = pro_forma(f, params)
    target = params["baseline_team_revenue"]
    problems: list[str] = []

    deviation = (pf["revenue_gross"] - target) / target
    if abs(deviation) > 0.15:
        problems.append(
            f"projected revenue {pf['revenue_gross']:,.0f} is {deviation:+.0%} "
            f"against the {target:,.0f} baseline (limit +/-15%)")
    if pf["contribution_margin_pct"] < 0.04:
        problems.append(
            f"projected contribution margin {pf['contribution_margin_pct']:.1%} "
            "is below the 4% floor")
    if pf["runway_rounds"] < 8:
        problems.append(f"projected runway {pf['runway_rounds']:.1f} rounds is below 8")
    return problems


def _basket_price(f: Founding, params) -> float:
    skus = [params.sku(c) for c in f.assortment] or params.skus
    w = sum(float(s["revenue_weight"]) for s in skus) or 1.0
    return sum(float(s["list_price"]) * float(s["revenue_weight"]) for s in skus) / w


def _basket_cost(f: Founding, params) -> float:
    skus = [params.sku(c) for c in f.assortment] or params.skus
    w = sum(float(s["revenue_weight"]) for s in skus) or 1.0
    return sum(float(s["unit_cost"]) * float(s["revenue_weight"])
               for s in skus) / w * params["cogs_scale"]
