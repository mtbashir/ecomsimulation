"""Bridge between the store and the engine.

The engine stays a pure function. Everything stateful - who submitted what,
which decisions are open, which parameters the instructor overrode - lives in
the database and is resolved here into the arguments `run_round` expects.
"""
from __future__ import annotations

import csv
import io

from dataclasses import asdict

from .. import (bootstrap, console, founding as founding_mod, params as P,
                report, scoring)
from ..decisions import REGISTRY, Resolver
from ..engine import run_round
from ..io_csv import LIST_DECISIONS
from . import db


def load_params(con):
    """Parameters with the instructor's overrides applied.

    Band violations raise, so a configuration that would break the model never
    reaches a cohort (docs/04).
    """
    g = db.game(con)
    over = dict(db.overrides(con))
    over["n_teams"] = len(db.accounts(con, "team"))
    return P.load(over)


def open_decisions(con, round_: int) -> list:
    """Decisions a team may set this round.

    The preset and unlock schedule give the default; the instructor's window
    overrides win either way, so a decision can be opened early or held back.
    """
    g = db.game(con)
    resolver = Resolver(preset=g["preset"], round_=round_)
    manual = db.windows(con, round_)
    out = []
    for code, spec in REGISTRY.items():
        by_preset = resolver.enabled(code) and resolver.unlocked(code)
        if manual.get(code, by_preset):
            out.append(spec)
    return sorted(out, key=_reading_order)


def _reading_order(spec):
    """Groups and codes in the order a person counts, not in string order.

    Plain sorting puts G12 Finance second, between G1 and G2, and 2.10 before
    2.2 - which is how the form ended up opening on market research.
    """
    return (int(spec.group[1:]),
            tuple(int(part) for part in spec.code.split(".")))


def catalogue_options(params, name: str) -> list[dict]:
    """Readable choices for a decision backed by a reference table.

    The catalogues already carry names, prices and lead times. A student should
    see "Speed Express - PKR 210 per order, 97.5% delivered, 2.1 days", not the
    code ``speed``.
    """
    if name == "skus":
        return [{"value": r["code"], "label": r["name"],
                 "note": f'PKR {float(r["list_price"]):,.0f} - {r["tier"]}'}
                for r in params.skus]
    if name == "studies":
        return [{"value": r["code"], "label": r["name"],
                 "note": (f'PKR {float(r["price"]):,.0f}'
                          + (" - arrives next month"
                             if int(r["lag_rounds"]) else " - arrives this month")
                          + f' - +/- {float(r["error_band"]) * 100:.0f}%'
                          + (f' - {r["note"]}' if r.get("note") else ""))}
                for r in params.studies]
    if name == "couriers":
        return [{"value": r["code"], "label": r["name"],
                 "note": (f'PKR {float(r["cost_per_order"]):,.0f} per order - '
                          f'{float(r["success_rate"]) * 100:.1f}% delivered - '
                          f'{float(r["avg_days"]):.1f} days - '
                          f'{float(r["rural_reach"]) * 100:.0f}% rural reach')}
                for r in params.couriers]
    if name == "suppliers":
        return [{"value": r["code"], "label": r["name"],
                 "note": (f'cost index {float(r["cost_index"]):.2f} - '
                          f'{int(r["lead_time_days"])}-day lead time - '
                          f'minimum order {int(r["moq_units"]):,} units')}
                for r in params.suppliers]
    return []


def standing_choice(spec, previous, options) -> str:
    """How to describe "change nothing" for a choice, in that team's terms.

    "leave unchanged" tells a student nothing when they have never set the
    lever. Naming what they are actually on - last month's pick, or the
    standing default - does.
    """
    value = previous.get(spec.code, spec.default_when_disabled)
    if value is True:
        return "it switched on"
    if value is False or value in (None, ""):
        return "it as it is" if value is not False else "it switched off"
    labels = {o["value"]: o["label"] for o in options}
    labels.update({o[0]: o[1] for o in spec.options})
    return labels.get(str(value), str(value))


def default_shares(params, name: str) -> dict[str, float]:
    """An even-ish starting split, so the shares widget is never blank."""
    from ..modules.m10_fulfilment import DEFAULT_MIX
    if name == "couriers":
        return dict(DEFAULT_MIX)
    rows = catalogue_options(params, name)
    return {r["value"]: 1 / len(rows) for r in rows} if rows else {}


def coerce(code: str, raw):
    """Turn a form value into what the engine expects."""
    spec = REGISTRY[code]
    if spec.kind == "grid":
        # {sku: {"price": float, "sourcing": str}} - only the lines the team
        # actually filled in, so a blank grid falls through to the founding
        # prices rather than overwriting them with zeros.
        if not isinstance(raw, dict):
            return None
        out = {}
        for sku, cell in raw.items():
            entry = {}
            price = str(cell.get("price") or "").replace(",", "").strip()
            if price:
                try:
                    entry["price"] = float(price)
                except ValueError:
                    raise ValueError(f"{sku}: {price!r} is not a price")
            if cell.get("sourcing"):
                entry["sourcing"] = str(cell["sourcing"])
            if entry:
                out[sku] = entry
        return out or None
    if spec.kind == "shares":
        if not isinstance(raw, dict):
            return None
        shares = {k: float(str(v).replace("%", "").strip() or 0) for k, v in raw.items()}
        # Accept either 0-1 or 0-100; a team typing "30" means 30 per cent.
        if sum(shares.values()) > 1.5:
            shares = {k: v / 100 for k, v in shares.items()}
        return shares if sum(shares.values()) > 0 else None
    if code in LIST_DECISIONS:
        if isinstance(raw, list):
            return [v for v in raw if v]
        return [v.strip() for v in str(raw).replace(",", ";").split(";") if v.strip()]
    if raw in (None, ""):
        return None
    if spec.kind in {"num", "pct", "curr"}:
        text = str(raw).replace(",", "").strip()
        if spec.kind == "pct":
            # The field is labelled "%" and shows its current value as a
            # percentage, so a percentage is what comes back: 15 means 15%,
            # not 1500%. The file runner keeps the 0.15 convention; this is
            # the form, where nobody should have to know that.
            return float(text.rstrip("%")) / 100
        if text.endswith("%"):
            return float(text[:-1]) / 100
        return float(text)
    if spec.kind == "select" and isinstance(spec.default_when_disabled, bool):
        return str(raw).lower() in {"true", "yes", "on", "1"}
    return raw


def validate(code: str, value) -> str | None:
    """Per-decision sanity, so a typo does not become a silent catastrophe."""
    spec = REGISTRY[code]
    if value is None:
        return None
    if spec.kind == "grid":
        for sku, cell in value.items():
            price = cell.get("price")
            if price is None:
                continue
            if price <= 0:
                return f"{spec.name}: {sku} needs a price above zero"
            ref = float(params_sku_price(sku))
            if ref and price > ref * 4:
                return (f"{spec.name}: {sku} at {price:,.0f} is more than four "
                        f"times the market reference of {ref:,.0f}")
        return None
    if spec.kind == "shares":
        total = sum(float(v) for v in value.values())
        if abs(total - 1.0) > 0.01:
            return (f"{spec.name}: shares add up to {total * 100:.0f}%, "
                    f"they must add up to 100%")
        if any(float(v) < 0 for v in value.values()):
            return f"{spec.name}: a share cannot be negative"
        return None
    if spec.kind == "select" and spec.options:
        allowed = {o[0] for o in spec.options}
        if str(value) not in allowed:
            return f"{spec.name}: {value!r} is not one of the choices offered"
        return None
    if spec.kind == "pct" and not 0 <= float(value) <= 1:
        return f"{spec.name}: must be between 0% and 100%"
    if spec.kind in {"curr", "num"} and float(value) < 0:
        return f"{spec.name}: cannot be negative"
    if spec.kind == "curr" and float(value) > 50_000_000:
        return f"{spec.name}: {float(value):,.0f} looks like a typo"
    return None


# --- The founding round ------------------------------------------------------------

def founding_from_form(form, params) -> founding_mod.Founding:
    """Build a Round 0 configuration from submitted form fields.

    Anything the team has not filled in keeps the default configuration's
    value, so a half-finished draft is still a valid object to price.
    """
    f = founding_mod.Founding.default(params)

    def text(name, fallback=""):
        return (form.get(name) or fallback).strip()

    def money(name, fallback=0.0):
        raw = str(form.get(name) or "").replace(",", "").strip()
        try:
            return float(raw)
        except ValueError:
            return fallback

    f.brand_name = text("brand_name", f.brand_name)
    f.positioning_statement = text("positioning_statement")
    f.categories = form.getlist("categories") or f.categories
    f.segment_priority = form.getlist("segment_priority") or f.segment_priority
    f.tier = text("tier", f.tier)
    f.model = text("model", f.model)
    f.assortment = form.getlist("assortment") or f.assortment
    f.sourcing = text("sourcing", f.sourcing)
    f.tech_stack = text("tech_stack", f.tech_stack)
    f.fulfilment = text("fulfilment", f.fulfilment)
    f.cod_enabled = text("cod_enabled", "on") != "off"
    f.gateway = text("gateway", f.gateway)
    f.sourcing_by_sku = {}
    for key in form:
        if key.startswith("sourcing_"):
            code = key[len("sourcing_"):]
            how = (form.get(key) or "").strip()
            if how in founding_mod.SOURCING:
                f.sourcing_by_sku[code] = how
    f.prices = {}
    for key in form:
        if not key.startswith("price_"):
            continue
        code = key[len("price_"):]
        try:
            value = float(str(form.get(key) or "").replace(",", "").strip())
        except ValueError:
            continue
        if value > 0:
            f.prices[code] = value
    f.research = form.getlist("research")
    f.business_plan = text("business_plan")

    capital = params["starting_cash"]
    for slot in ("inventory", "marketing", "technology", "reserve"):
        if f"capital_{slot}" in form:
            setattr(f, f"capital_{slot}",
                    money(f"capital_{slot}", getattr(f, f"capital_{slot}")))
    for role in ("marketing", "ops", "cs", "analytics"):
        if f"head_{role}" in form:
            try:
                f.headcount[role] = int(float(form.get(f"head_{role}") or 0))
            except ValueError:
                pass
    f.target_repeat_share = money("target_repeat_share") / 100
    f.target_cac = money("target_cac")
    del capital
    return f


def founding_to_dict(f: founding_mod.Founding) -> dict:
    return {k: v for k, v in asdict(f).items()}


def founding_from_dict(d: dict, params) -> founding_mod.Founding:
    f = founding_mod.Founding.default(params)
    for key, value in (d or {}).items():
        if hasattr(f, key):
            setattr(f, key, value)
    return f


def product_catalogue(params, f: founding_mod.Founding) -> list[dict]:
    """The shelf a team is choosing from, priced and described.

    Cost moves with how the team sources and positions, so the catalogue is
    built against this team's current choices rather than being a static list.
    Demand share is the product's weight within the category - which is what a
    category manager would actually be handed.
    """
    total_weight = sum(float(s["revenue_weight"]) for s in params.skus) or 1.0
    # Round 0 has no supplier decision yet, so quote the default one - the same
    # supplier the team will be buying from in month 1 unless it changes 7.2.
    baseline_supplier = float(next(
        sp for sp in params.suppliers if sp["code"] == "B")["cost_index"])
    rows = []
    for sku in params.skus:
        code = sku["code"]
        sourcing = founding_mod.sourcing_of(f, code)
        cost = founding_mod.unit_cost(sku, sourcing, f.tier, params,
                                      baseline_supplier)
        reference = founding_mod.reference_price(sku, f.tier)
        price = float((f.prices or {}).get(code) or reference)
        share = float(sku["revenue_weight"]) / total_weight
        returns = float(sku["return_propensity"])
        rows.append({
            "code": code, "name": sku["name"], "category": sku["category"],
            "tier": sku["tier"], "cost": cost, "reference": reference,
            "sourcing": sourcing,
            # Both costs, so the page can move the figure the moment the team
            # changes where a product comes from.
            "cost_local": founding_mod.unit_cost(
                sku, "local", f.tier, params, baseline_supplier),
            "cost_import": founding_mod.unit_cost(
                sku, "import", f.tier, params, baseline_supplier),
            "cost_mixed": founding_mod.unit_cost(
                sku, "mixed", f.tier, params, baseline_supplier),
            "lead_days": founding_mod.SOURCING[sourcing][1],
            "price": price, "chosen": code in f.assortment,
            "demand_share": share,
            "demand": ("a large share of the category" if share >= 0.075
                       else "a mid-sized line" if share >= 0.045
                       else "a small line"),
            # Worded so it cannot be misread as customer loyalty. This is the
            # parcel coming back, not the customer.
            "returns": ("sent back more often than average" if returns >= 1.1
                        else "average rate of returns" if returns >= 0.9
                        else "seldom sent back"),
            "margin": (price - cost) / price if price > 0 else 0.0,
        })
    return rows


def blended_margin(rows: list[dict]) -> dict:
    """Gross margin across what the team has actually selected."""
    chosen = [r for r in rows if r["chosen"]]
    weight = sum(r["demand_share"] for r in chosen) or 1.0
    revenue = sum(r["price"] * r["demand_share"] for r in chosen)
    cost = sum(r["cost"] * r["demand_share"] for r in chosen)
    imported = sum(r["demand_share"] for r in chosen
                   if r["sourcing"] == "import")
    return {
        "lines": len(chosen),
        "avg_price": revenue / weight,
        "avg_cost": cost / weight,
        "gross_margin": (revenue - cost) / revenue if revenue > 0 else 0.0,
        "imported_share": imported / weight if weight else 0.0,
        "avg_lead_days": (sum(r["lead_days"] * r["demand_share"] for r in chosen)
                          / weight) if chosen else 0.0,
    }


def founding_preview(con, f: founding_mod.Founding) -> dict | None:
    """What this setup would produce in its first trading month.

    Run through the real engine rather than a parallel formula, so the preview
    cannot drift away from the game. Rivals are left at their defaults, which
    is exactly the caveat to put on it: this assumes an average market and
    ignores what everyone else is about to do.
    """
    if founding_mod.validate(f, load_params(con)):
        return None
    params = load_params(con)
    g = db.game(con)
    world = bootstrap.new_world(
        params, run_id=f"preview-{g['name']}",
        ai_competitors=g["ai_competitors"], ai_aggression=g["ai_aggression"])
    subject = next(iter(world.teams))
    founding_mod.apply(f, world.teams[subject], params)
    run_round(world, params, {}, preset=g["preset"])
    h = world.teams[subject].history[-1]
    burn = -min(0.0, h["ebitda"])
    return {
        "orders": h["orders"], "aov": h["aov_net"],
        "revenue": h["pnl"]["net_revenue"],
        "gross_margin_pct": h["gross_margin_pct"],
        "contribution_margin_pct": h["contribution_margin_pct"],
        "ebitda": h["ebitda"], "cash": h["cash_balance"],
        "conversion_rate": h["conversion_rate"],
        "runway": (h["cash_balance"] / burn) if burn > 0 else None,
    }


def apply_foundings(con, world, params) -> None:
    """Give every team the business it set up in Round 0.

    A team that never submitted keeps the default configuration. That is a
    deliberate choice: a team that misses setup should start at a plausible
    middle, not be eliminated before the first month.
    """
    saved = db.foundings(con)
    for row in db.accounts(con, "team"):
        team = world.teams.get(row["team_id"])
        if team is None:
            continue
        record = saved.get(row["team_id"])
        f = (founding_from_dict(record["config"], params) if record
             else founding_mod.Founding.default(params))
        if not founding_mod.validate(f, params):
            founding_mod.apply(f, team, params)
        team.brand_name = (f.brand_name if record and f.brand_name != "Unnamed"
                           else row["display_name"])


def monthly_catalogue(con, team_id: str, current: dict) -> list[dict]:
    """The team's shelf as it stands this month: price, sourcing, cost, margin.

    Founding set the opening shelf; each month the team may re-price a line or
    move it between local and imported. What is shown is what would be charged
    if the team submitted now.
    """
    params = load_params(con)
    record = db.founding(con, team_id)
    world = db.load_world(con)
    grid = current.get("1.1") or {}

    if record is not None:
        f = founding_from_dict(record["config"], params)
        active, tier = f.assortment, f.tier
    elif world is not None and team_id in world.teams:
        active = world.teams[team_id].active_skus
        tier = "mainstream"
        f = None
    else:
        return []

    supplier = float(next(sp for sp in params.suppliers
                          if sp["code"] == "B")["cost_index"])
    rows = []
    for code in active:
        sku = params.sku(code)
        founded = founding_mod.sourcing_of(f, code) if f else "mixed"
        sourcing = (grid.get(code) or {}).get("sourcing") or founded
        cost = founding_mod.unit_cost(sku, sourcing, tier, params, supplier)
        standing = ((f.prices or {}).get(code) if f else None) \
            or founding_mod.reference_price(sku, tier)
        price = float((grid.get(code) or {}).get("price") or standing)
        rows.append({
            "code": code, "name": sku["name"], "category": sku["category"],
            "sourcing": sourcing, "cost": cost, "price": price,
            "standing": standing,
            "reference": founding_mod.reference_price(sku, tier),
            "cost_local": founding_mod.unit_cost(sku, "local", tier, params, supplier),
            "cost_import": founding_mod.unit_cost(sku, "import", tier, params, supplier),
            "cost_mixed": founding_mod.unit_cost(sku, "mixed", tier, params, supplier),
            "margin": (price - cost) / price if price > 0 else 0.0,
            "changed": code in grid,
        })
    return rows


def decision_summary(spec, value, catalogue_rows=None) -> str:
    """One line describing where a decision stands, for the tile face."""
    if value is None or value == "" or value == [] or value == {}:
        return ""
    if spec.kind == "grid":
        changed = len(value)
        return f"{changed} line{'' if changed == 1 else 's'} changed"
    if spec.kind == "shares":
        return " · ".join(f"{k} {v * 100:.0f}%" for k, v in value.items())
    if spec.kind == "multi":
        names = {r["value"]: r["label"] for r in (catalogue_rows or [])}
        picked = [names.get(v, v) for v in value]
        if not picked:
            return ""
        head = ", ".join(picked[:2])
        return head + (f" +{len(picked) - 2} more" if len(picked) > 2 else "")
    if spec.kind == "pct":
        return f"{float(value) * 100:,.4g}%"
    if spec.kind == "curr":
        return f"PKR {float(value):,.0f}"
    if spec.kind == "num":
        return f"{float(value):,.4g}{' ' + spec.unit if spec.unit else ''}"
    if spec.kind == "select":
        if isinstance(value, bool):
            return "Yes" if value else "No"
        labels = {o[0]: o[1] for o in spec.options}
        labels.update({r["value"]: r["label"] for r in (catalogue_rows or [])})
        return labels.get(str(value), str(value))
    if spec.kind == "text":
        text = str(value)
        return text[:44] + ("…" if len(text) > 44 else "")
    return str(value)


def params_sku_price(code: str) -> float:
    """The catalogue reference for one product, for validating a typed price."""
    global _SKU_PRICES
    if _SKU_PRICES is None:
        _SKU_PRICES = {s["code"]: float(s["list_price"]) for s in P.load().skus}
    return _SKU_PRICES.get(code, 0.0)


_SKU_PRICES: dict[str, float] | None = None


def process_round(con, actor: str = "admin", out_dir=None) -> dict:
    """Run the next round and persist everything needed to replay or roll back."""
    g = db.game(con)
    params = load_params(con)
    nxt = g["round"] + 1

    world = db.load_world(con)
    if world is None:
        world = bootstrap.new_world(
            params, run_id=g["name"],
            ai_competitors=g["ai_competitors"], ai_aggression=g["ai_aggression"])
        if g["start_mode"] == "founding":
            apply_foundings(con, world, params)
        else:
            for row in db.accounts(con, "team"):
                team = world.teams.get(row["team_id"])
                if team is not None:
                    team.brand_name = row["display_name"]

    submitted = db.submissions(con, nxt)
    run_round(world, params, submitted, preset=g["preset"])

    db.save_round(con, nxt, world, params.config_hash())
    db.set_game(con, round=nxt, open_round=None)
    with con:
        db.log(con, actor, "round.run",
               f"r{nxt}: {len(submitted)}/{len(world.teams)} submitted")

    if out_dir is not None:
        for team in world.teams.values():
            card = scoring.final_score(team, params, world.teams) if nxt >= 2 else None
            report.render(team, nxt, out_dir / f"round_{nxt}", card)
        console.render(world, params, out_dir / f"round_{nxt}")

    return {"round": nxt, "submitted": len(submitted), "teams": len(world.teams)}


# The five figures a team leads with. (label, key, format, up_is_good)
HEADLINE = [
    ("Net revenue", "revenue_net", "pkr", True),
    ("Contribution margin", "contribution_margin_pct", "pct", True),
    ("Cost per new customer", "cac_blended", "pkr", False),
    ("Repeat orders", "repeat_order_share", "pct", True),
    ("Cash", "cash_balance", "pkr", True),
]


def _fmt(value, kind: str) -> str:
    if value is None:
        return "—"
    if kind == "pkr":
        return (f"{value / 1e6:,.1f}M" if abs(value) >= 1e6
                else f"{value / 1e3:,.0f}k" if abs(value) >= 10_000
                else f"{value:,.0f}")
    if kind == "pct":
        return f"{value * 100:,.1f}%"
    return f"{value:,.0f}"


def headline_kpis(con, team_id: str) -> list[dict]:
    """The top row: where each figure is, which way it is going, and whether
    that direction is good news. A rising cost of acquisition is not green."""
    world = db.load_world(con)
    if world is None or team_id not in world.teams:
        return []
    history = world.teams[team_id].history
    if not history:
        return []
    out = []
    for label, key, kind, up_good in HEADLINE:
        series = [h.get(key) for h in history if h.get(key) is not None]
        now = series[-1] if series else None
        prev = series[-2] if len(series) > 1 else None
        delta = direction = None
        if now is not None and prev not in (None, 0):
            change = (now - prev) / abs(prev)
            delta = f"{change:+.1%}" if kind != "pct" else f"{(now - prev) * 100:+.1f}pp"
            rising = now > prev
            direction = "up" if rising == up_good else "dn"
            if abs(change) < 0.002:
                direction = "flat"
        out.append({"label": label, "value": _fmt(now, kind), "series": series,
                    "delta": delta, "direction": direction,
                    "rising_is_good": up_good})
    return out


def plan_meters(con, team_id: str) -> list[dict]:
    """What the team promised in Round 0, against what it has delivered.

    The founding plan is the most valuable thing a team writes and it has been
    invisible since the month it was written. Nothing here is shown unless the
    team actually committed to a number.
    """
    record = db.founding(con, team_id)
    world = db.load_world(con)
    if record is None or world is None or team_id not in world.teams:
        return []
    history = world.teams[team_id].history
    if not history:
        return []
    now = history[-1]
    f = founding_from_dict(record["config"], load_params(con))

    meters = []
    if f.target_repeat_share:
        meters.append(_meter("Repeat order share", now.get("repeat_order_share", 0.0),
                             f.target_repeat_share, 0.10, 0.40, "pct",
                             "You committed to %s by month 12."))
    if f.target_cac:
        meters.append(_meter("Cost per new customer", now.get("cac_blended", 0.0),
                             f.target_cac, 300.0, 1000.0, "pkr",
                             "You committed to PKR %s.", lower_is_better=True))
    return meters


def _meter(label, actual, target, lo, hi, kind, blurb, lower_is_better=False) -> dict:
    def place(v):
        return max(0.0, min(1.0, (v - lo) / (hi - lo))) * 100
    hit = actual <= target if lower_is_better else actual >= target
    return {
        "label": label, "actual": _fmt(actual, kind), "target": _fmt(target, kind),
        "blurb": blurb % _fmt(target, kind),
        "fill": place(actual), "mark": place(target), "hit": hit,
        "lo": _fmt(lo, kind), "hi": _fmt(hi, kind),
    }


def agenda(con, team_id: str) -> list[dict]:
    """What this team should deal with, in order of how much it costs to ignore.

    Everything here is read off the team's own state - nothing a team has not
    paid to see, and nothing invented to fill the list.
    """
    game = db.game(con)
    params = load_params(con)
    world = db.load_world(con)
    items: list[dict] = []
    rnd = game["open_round"]

    if world is not None and team_id in world.teams:
        team = world.teams[team_id]
        h = team.history[-1] if team.history else {}

        if team.in_administration:
            items.append({"title": "You are in administration",
                          "note": "Trading continues, but recovery is slow and expensive. "
                                  "Fix the cash position before anything else.",
                          "flag": "crit", "label": "Act now"})

        cover = h.get("weeks_cover")
        if cover is not None and cover < 2.5:
            items.append({"title": "Stock cover is thin",
                          "note": f"{cover:,.1f} weeks of cover. A good month will "
                                  f"stock you out.",
                          "flag": "crit", "label": "Act now"})

        cacs = [x.get("cac_blended") for x in team.history[-3:]
                if x.get("cac_blended")]
        if len(cacs) == 3 and cacs[-1] > cacs[0] * 1.15:
            items.append({"title": "Acquisition is getting dearer",
                          "note": f"Cost per customer up {(cacs[-1] / cacs[0] - 1):.0%} "
                                  f"over three months.",
                          "flag": "warn", "label": "Decide"})

        runway = h.get("runway_rounds")
        if runway is not None and runway < 4:
            items.append({"title": "Runway is short",
                          "note": f"{runway:,.1f} months at this burn.",
                          "flag": "crit", "label": "Act now"})

        bought = (db.submission(con, game["round"], team_id) or {}).get("12.1") or []
        for code in bought[:2]:
            row = next((st for st in params.studies if st["code"] == code), None)
            if row:
                items.append({"title": row["name"],
                              "note": f"Bought last month · ±{float(row['error_band']):.0%} "
                                      f"margin of error.",
                              "flag": "ok", "label": "Read"})

        if game["round"]:
            items.append({"title": f"Month {game['round']} report",
                          "note": "Where the month was won and lost.",
                          "flag": "ok", "label": "Read"})

    if rnd:
        submitted = db.submission(con, rnd, team_id)
        items.append({
            "title": f"Submit month {rnd}",
            "note": (f"{len(submitted)} decisions entered. You can revise until the "
                     f"month closes." if submitted
                     else "Nothing entered. Submit nothing and last month's decisions stand."),
            "flag": "ok" if submitted else "",
            "label": "Done" if submitted else "Pending"})
    return items


def standings(con, team_id: str) -> dict | None:
    """The field - but only what this team has paid to know.

    Share comes from the Market Share Report. Without it a team sees its own
    position and an invitation to go and buy the study, which is the lesson.
    """
    game = db.game(con)
    world = db.load_world(con)
    if world is None or not game["round"]:
        return None
    bought = any("MR-03" in ((db.submission(con, r, team_id) or {}).get("12.1") or [])
                 for r in range(1, game["round"] + 1))
    if not bought:
        return {"bought": False}

    rows = []
    for tid, team in world.teams.items():
        h = team.history[-1] if team.history else {}
        rows.append({"team_id": tid, "name": team.brand_name,
                     "share": h.get("market_share", 0.0),
                     "you": tid == team_id})
    rows.sort(key=lambda r: -r["share"])
    for i, row in enumerate(rows, 1):
        row["rank"] = i
    return {"bought": True, "rows": rows,
            "error_band": next((float(s["error_band"]) for s in load_params(con).studies
                                if s["code"] == "MR-03"), 0.05)}


def company_position(con, team_id: str) -> dict | None:
    """What this team owns right now, in the terms a founder would use.

    Before the first round is processed there is no world yet, so the answer
    comes from the founding setup instead. Either way the team gets a straight
    answer to "what have I actually got".
    """
    params = load_params(con)
    world = db.load_world(con)
    if world is not None and team_id in world.teams:
        team = world.teams[team_id]
        h = team.history[-1] if team.history else {}
        return {
            "source": "trading",
            "brand": team.brand_name,
            "cash": team.cash,
            "credit_drawn": team.credit_drawn,
            "inventory_units": sum(team.inventory.values()),
            "inventory_value": sum(
                units * float(params.sku(code)["unit_cost"])
                for code, units in team.inventory.items() if units),
            "skus": [params.sku(c)["name"] for c in team.active_skus],
            "rating": getattr(team, "rating", None),
            "nps": h.get("nps"),
            "active_customers": h.get("active_customers"),
            "cs_agents": team.cs_agents,
            "capabilities": sorted(team.capabilities),
            "cod_receivable": team.cod_receivable,
            "in_administration": team.in_administration,
        }

    record = db.founding(con, team_id)
    if record is None:
        return None
    f = founding_from_dict(record["config"], params)
    return {
        "source": "founding",
        "brand": f.brand_name,
        "cash": params["starting_cash"],
        "categories": f.categories,
        "tier": f.tier,
        "model": f.model,
        "skus": [params.sku(c)["name"] for c in f.assortment],
        "shelf": [r for r in product_catalogue(params, f) if r["chosen"]],
        "margin": blended_margin(product_catalogue(params, f)),
        "allocation": {"Inventory": f.capital_inventory,
                       "Marketing": f.capital_marketing,
                       "Technology": f.capital_technology,
                       "Reserve": f.capital_reserve},
        "headcount": dict(f.headcount),
        "submitted_at": record["submitted_at"],
    }


def endowment(con) -> dict:
    """The identical starting hand every team is dealt (docs/05)."""
    params = load_params(con)
    return {
        "capital": params["starting_cash"],
        "catalogue": len(params.skus),
        "rounds": db.game(con)["total_rounds"],
        "credit_facility": params["credit_ceiling"],
        "credit_rate": params["credit_rate_annual"],
        "payroll": params["payroll_base"],
    }


def team_report(con, team_id: str, round_: int) -> str | None:
    """Render one team's report as HTML, without touching disk."""
    world = db.load_world(con, round_)
    if world is None or team_id not in world.teams:
        return None
    import tempfile
    from pathlib import Path

    params = load_params(con)
    team = world.teams[team_id]
    card = scoring.final_score(team, params, world.teams) if round_ >= 2 else None
    with tempfile.TemporaryDirectory() as tmp:
        return report.render(team, round_, Path(tmp), card).read_text(encoding="utf-8")


def instructor_console(con, round_: int) -> str | None:
    world = db.load_world(con, round_)
    if world is None:
        return None
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp:
        return console.render(world, load_params(con), Path(tmp)).read_text(
            encoding="utf-8")


def export_decisions(con, round_: int) -> str:
    """The escape hatch: the same CSV the file-based runner reads.

    If the app fails mid-class, download this and run the round offline. That
    path is kept working on purpose - nobody is on call.
    """
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["team_id", "decision", "value"])
    for team_id, decisions in sorted(db.submissions(con, round_).items()):
        for code, value in sorted(decisions.items()):
            if isinstance(value, list):
                value = ";".join(str(v) for v in value)
            w.writerow([team_id, code, value])
    return buf.getvalue()
