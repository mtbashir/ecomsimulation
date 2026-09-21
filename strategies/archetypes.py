"""The 20 scripted strategy archetypes (docs/11-validation-harness.md).

A strategy is a pure function (world, round, team_id, v) -> decisions, where v
in [0, 1] is the variation across the archetype's defining parameter. No AI,
no randomness: these must be reproducible.

Six archetypes exist solely to fail - discounter, research_heavy,
research_zero, sandbagger, harvester, overspend. If one of them wins, a
specific design intent has broken, and the invariant names which.
"""
from __future__ import annotations

BASE = {"3.1": 468_000, "3.2": 234_000, "3.4": 168_000, "3.8": 200_000, "3.9": 267_000}
STUDIES_ALL = [f"MR-{i:02d}" for i in range(1, 21)]
# Selective means buying what you will act on, and only where acting pays.
# The earlier rotation bought four studies a month, three of which drove no
# decision at all - research_heavy with a smaller invoice. Measured, one study
# in the catalogue currently earns its price: MR-01, worth +0.24 points net of
# its 40,000 a month. MR-17 is not here because every response to its warning
# loses money - raise cover -0.21, source local -1.03, switch supplier -1.08 -
# and a study whose best available action destroys value is not one a selective
# buyer buys. That is a finding about the engine, not about the study: stock
# binds in 2% of team-rounds, so nothing you learn about supply can pay for
# itself. docs/13 carries the measurement. MR-10 stays as a quarterly
# diagnostic; it changes nothing for a healthy cohort, which is the point.
SELECTIVE_CORE = ["MR-01"]
SELECTIVE_QUARTERLY = "MR-10"


def _selective_basket(r: int) -> list[str]:
    return SELECTIVE_CORE + ([SELECTIVE_QUARTERLY] if r % 3 == 1 else [])


# Blended monthly churn a healthy cohort runs at. MR-10 reports this rate, not
# a share, so the old 0.30 line could never be crossed and the branch below was
# dead code dressed up as an action.
COHORT_ROT_LINE = 0.10


def _scale(mult: float) -> dict:
    return {k: v * mult for k, v in BASE.items()}


def _stock(v: float, lo: float, hi: float) -> float:
    """Safety-stock weeks across an archetype's variation range.

    Inventory is a real decision now, so the suite has to span it - lean
    enough to stock out at one end, heavy enough to tie up cash at the other.
    Without this the operations pillar has nothing to measure.
    """
    return lo + (hi - lo) * v


def _lerp(v: float, lo: float, hi: float) -> float:
    return lo + (hi - lo) * v


# --- The archetypes ------------------------------------------------------------

def baseline(world, r, tid, v):
    return {}


def balanced(world, r, tid, v):
    m = _lerp(v, 1.05, 1.30)
    d = _scale(m)
    d["3.9"] = BASE["3.9"] * _lerp(v, 1.2, 1.6)
    d["6.1"] = _lerp(v, 120_000, 220_000)
    d["7.5"] = _stock(v, 1.5, 4.0)
    d["9.2"] = 0.03
    d["10.1"] = 5
    d["7.4"] = 120_000
    if r >= 3:
        d["11.1"] = True
    return d


def growth_max(world, r, tid, v):
    d = _scale(_lerp(v, 2.0, 4.0))
    d["7.5"] = _stock(v, 0.5, 2.0)   # growth outruns its cover
    d["3.9"] = 0
    d["3.8"] = BASE["3.8"] * 0.5
    return d


def discounter(world, r, tid, v):
    d = _scale(1.3)
    d["7.5"] = _stock(v, 1.0, 3.0)
    d["2.2"] = _lerp(v, 0.15, 0.45)
    return d


def premium(world, r, tid, v):
    d = _scale(1.0)
    d["7.5"] = _stock(v, 2.5, 5.0)
    d["1.5"] = "premium"
    d["2.2"] = 0.0
    d["8.5"] = "premium"
    d["3.9"] = BASE["3.9"] * _lerp(v, 1.6, 2.4)
    d["3.8"] = BASE["3.8"] * 1.5
    d["7.4"] = 200_000
    d["10.1"] = 6
    return d


def retention_led(world, r, tid, v):
    d = _scale(0.9)
    d["6.1"] = _lerp(v, 300_000, 600_000)
    d["10.1"] = 6
    d["10.4"] = "free"
    d["7.4"] = 150_000
    return d


def ops_excellence(world, r, tid, v):
    d = _scale(1.0)
    d["7.5"] = _lerp(v, 3.0, 5.0)
    d["7.4"] = 250_000
    d["8.3"] = {"speed": 0.6, "value": 0.1, "wide": 0.3}
    d["8.5"] = "branded"
    d["10.1"] = 7
    d["9.2"] = 0.05
    return d


def cash_preservation(world, r, tid, v):
    d = _scale(_lerp(v, 0.3, 0.5))
    d["7.5"] = _stock(v, 0.4, 1.4)   # starving stock to hold cash
    d["3.9"] = 0
    d["3.8"] = 0
    d["10.1"] = 3
    d["6.1"] = 0
    return d


def marketplace_first(world, r, tid, v):
    d = _scale(0.7)
    if r >= 3:
        d["4.1"] = "basic"
        d["3.7"] = _lerp(v, 200_000, 400_000)
    return d


def own_site_purist(world, r, tid, v):
    d = _scale(1.1)
    d["7.5"] = _stock(v, 1.0, 4.0)
    d["4.1"] = "off"
    d["5.1"] = _lerp(v, 200_000, 400_000)
    return d


def tech_led(world, r, tid, v):
    d = _scale(1.0)
    d["7.5"] = _stock(v, 1.5, 3.5)
    if r >= 3:
        for k in ("11.1", "11.2", "11.4", "11.5"):
            d[k] = True
        if v > 0.5:
            d["11.3"] = True
    return d


def capability_early(world, r, tid, v):
    d = _scale(1.0)
    if r >= 3:
        d["11.1"] = True
        d["11.2"] = True
    d["7.5"] = 2.5
    return d


def overspend(world, r, tid, v):
    d = _scale(_lerp(v, 2.5, 3.5))
    if r >= 3:
        for k in ("11.1", "11.2", "11.3", "11.4", "11.5"):
            d[k] = True
    d["10.1"] = 8
    return d


def modest_capability(world, r, tid, v):
    d = _scale(1.0)
    d["7.5"] = _stock(v, 1.2, 4.5)
    if r >= 3:
        d["11.1"] = True
    return d


def research_zero(world, r, tid, v):
    return _informed(world, r, tid, v, buy=[])


def research_heavy(world, r, tid, v):
    return _informed(world, r, tid, v, buy=STUDIES_ALL)


def research_selective(world, r, tid, v):
    return _informed(world, r, tid, v, buy=_selective_basket(r))


def sandbagger(world, r, tid, v):
    return cash_preservation(world, r, tid, v) if r <= 6 else growth_max(world, r, tid, v)


def harvester(world, r, tid, v):
    """Build, then strip. The defining parameter is when the stripping starts.

    Two things were wrong here. The strip returned a bare dict, so it did not
    just cut spend - it dropped positioning, discount, COD and every other
    lever back to the engine default, and the archetype stopped measuring
    harvesting. And it ignored v, so all ten variations were the same run
    repeated, which is not what docs/11 says the suite does.
    """
    start = 9 + round(2 * v)                      # strips from R9, R10 or R11
    if r < start:
        return balanced(world, r, tid, v)
    d = balanced(world, r, tid, v)
    d.update({"3.1": 0, "3.2": 0, "3.4": 0, "3.8": 0, "3.9": 0, "6.1": 0,
              "10.1": 2, "7.4": 0, "7.5": 0.5})
    return d


def cod_off(world, r, tid, v):
    d = _scale(1.0)
    d["9.1"] = "off"
    d["9.2"] = _lerp(v, 0.05, 0.10)
    return d


# --- The informed core: acts on what it bought ---------------------------------

def _informed(world, r, tid, v, buy: list[str]) -> dict:
    """balanced() plus actions conditioned on reports actually received.

    This is what makes I7 meaningful: research is pure cost unless someone reads
    it. The three actions below are the mechanically sound ones - pre-build and
    spend into a seasonal peak, pre-build ahead of a lead-time shock, and cut
    discount when the cohort mix is rotting. A team that buys these studies and
    ignores them is research_heavy's real lesson.
    """
    d = balanced(world, r, tid, v)
    d["12.1"] = list(buy)

    team = world.teams[tid]
    latest = team.reports.get(r - 1, {}) if r > 1 else {}

    mr01 = latest.get("MR-01", {}).get("seasonal_index", {})
    peak_ahead = any(idx >= 1.15 for rr, idx in mr01.items() if rr <= r + 1)
    if peak_ahead:
        d["7.5"] = 4.0
        d["3.1"] = d["3.1"] * 1.25

    # Cover the slip; do not buy your way out of it. Supplier C is 9% dearer,
    # which on a 38% gross margin costs more in one month than three months of
    # the shock does. Measured: switching is worth -1.6 points, pre-building
    # +0.9. The wrong response to good information still loses money.
    mr17 = latest.get("MR-17", {}).get("lead_time_forecast", {})
    shock_ahead = any(x["lead_time_mult"] > 1.2 for x in mr17.values())
    if shock_ahead:
        d["7.5"] = 4.5

    mr10 = latest.get("MR-10", {})
    if mr10.get("status") == "ok" and mr10.get("reported", 0) > COHORT_ROT_LINE:
        d["2.2"] = 0.0
        d["6.1"] = d["6.1"] * 1.5

    return d


ARCHETYPES = {
    "baseline": baseline, "balanced": balanced, "growth_max": growth_max,
    "discounter": discounter, "premium": premium, "retention_led": retention_led,
    "ops_excellence": ops_excellence, "cash_preservation": cash_preservation,
    "marketplace_first": marketplace_first, "own_site_purist": own_site_purist,
    "tech_led": tech_led, "capability_early": capability_early,
    "overspend": overspend, "modest_capability": modest_capability,
    "research_heavy": research_heavy, "research_zero": research_zero,
    "research_selective": research_selective, "sandbagger": sandbagger,
    "harvester": harvester, "cod_off": cod_off,
}
MUST_FAIL = {"discounter", "research_heavy", "research_zero", "sandbagger",
             "harvester", "overspend", "growth_max"}
