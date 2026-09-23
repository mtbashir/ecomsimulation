"""Bridge between the store and the engine.

The engine stays a pure function. Everything stateful - who submitted what,
which decisions are open, which parameters the instructor overrode - lives in
the database and is resolved here into the arguments `run_round` expects.
"""
from __future__ import annotations

import csv
import io
import json

from dataclasses import asdict

from .. import (bootstrap, console, founding as founding_mod, params as P,
                report, scoring, targeting)
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
    if spec.kind == "bundles":
        # {sku: {"price": float}} - the packs the team is offering.
        if not isinstance(raw, dict):
            return None
        out = {}
        for sku, cell in raw.items():
            price = str(cell.get("price") or "").replace(",", "").strip()
            try:
                out[sku] = {"price": float(price)} if price else {}
            except ValueError:
                raise ValueError(f"{sku}: {price!r} is not a price")
        return out or None
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
            disc = str(cell.get("discount") or "").replace("%", "").strip()
            if disc:
                try:
                    entry["discount"] = float(disc) / 100
                except ValueError:
                    raise ValueError(f"{sku}: {disc!r} is not a discount")
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
            disc = cell.get("discount")
            if disc is not None and not 0 <= disc <= 0.6:
                return (f"{spec.name}: {sku} at {disc * 100:,.0f}% discount - "
                        f"anything past 60% is not a promotion, it is a mistake")
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


# Where the handbook lives. A decision tile cites a reference; this is what a
# team follows when the one-line help is not enough.
HANDBOOK = {
    "url": "https://github.com/mtbashir/ecomsimulation/blob/main/docs/"
           "01-decision-list.md",
    "title": "Decision handbook",
}


def handbook_entry(spec) -> dict:
    """What a hovered reference shows: what the lever is, and where it sits."""
    return {
        "code": spec.code,
        "name": spec.name,
        "help": spec.help,
        "guide": spec.guide,
        "group": spec.group,
        "url": f"{HANDBOOK['url']}#{spec.code.replace('.', '')}",
    }


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
        active, tier, f = world.teams[team_id].active_skus, "mainstream", None
    else:
        # A going-concern game, or a team that never opened the setup form.
        # The shelf is the catalogue at the middle tier - the same position the
        # engine gives a team that decided nothing.
        active, tier, f = [sku["code"] for sku in params.skus], "mainstream", None

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
        discount = float((grid.get(code) or {}).get("discount") or 0.0)
        net = price * (1 - discount)
        rows.append({
            "code": code, "name": sku["name"], "category": sku["category"],
            "sourcing": sourcing, "cost": cost, "price": price,
            "discount": discount, "net": net,
            "weight": float(sku["revenue_weight"]),
            "standing": standing,
            "reference": founding_mod.reference_price(sku, tier),
            "cost_local": founding_mod.unit_cost(sku, "local", tier, params, supplier),
            "cost_import": founding_mod.unit_cost(sku, "import", tier, params, supplier),
            "cost_mixed": founding_mod.unit_cost(sku, "mixed", tier, params, supplier),
            "margin": (net - cost) / net if net > 0 else 0.0,
            "changed": code in grid,
        })
    # Grouped by category so the grid reads like a range review rather than a
    # SKU dump; within a category the biggest sellers come first.
    rows.sort(key=lambda r: (r["category"], -r["weight"], r["name"]))
    return rows


def shelf_totals(rows: list[dict]) -> dict:
    """What the shelf adds up to, weighted by each line's share of volume."""
    weight = sum(r["weight"] for r in rows) or 1.0
    net = sum(r["net"] * r["weight"] for r in rows)
    cost = sum(r["cost"] * r["weight"] for r in rows)
    return {
        "lines": len(rows),
        "avg_price": sum(r["price"] * r["weight"] for r in rows) / weight,
        "avg_net": net / weight,
        "avg_cost": cost / weight,
        "discount": sum(r["discount"] * r["weight"] for r in rows) / weight,
        "gross_margin": (net - cost) / net if net > 0 else 0.0,
    }


BUNDLE_UNITS = 3          # a bundle is a three-pack of one product


def bundle_rows(con, team_id: str, current: dict) -> list[dict]:
    """The pack a team can build from each line it sells.

    COGS is three units landed; the reference is three singles at today's
    price. What the team charges against that reference is the pack saving.
    """
    shelf = monthly_catalogue(con, team_id, current)
    chosen = current.get("1.2") or {}
    if isinstance(chosen, list):        # records written before packs were priced
        chosen = {code: {} for code in chosen}
    rows = []
    for line in shelf:
        cost = line["cost"] * BUNDLE_UNITS
        reference = line["net"] * BUNDLE_UNITS
        cell = chosen.get(line["code"])
        price = float((cell or {}).get("price") or round(reference * 0.9))
        rows.append({
            "code": line["code"],
            "name": f"{line['name']} · {BUNDLE_UNITS}-pack",
            "cost": cost, "reference": reference, "price": price,
            "saving": (reference - price) / reference if reference else 0.0,
            "margin": (price - cost) / price if price > 0 else 0.0,
            "offered": line["code"] in chosen,
        })
    return rows


def decision_summary(spec, value, catalogue_rows=None) -> str:
    """One line describing where a decision stands, for the tile face."""
    if value is None or value == "" or value == [] or value == {}:
        return ""
    if spec.kind == "grid":
        changed = len(value)
        return f"{changed} line{'' if changed == 1 else 's'} changed"
    if spec.kind == "bundles":
        offered = len(value)
        return f"{offered} pack{'' if offered == 1 else 's'} offered"
    if spec.kind == "shares":
        return " · ".join(f"{k} {v * 100:.0f}%" for k, v in value.items())
    if spec.kind == "campaigns":
        return campaign_summary(value)
    if spec.code == "12.1":
        # Named, two studies of five fit on a tile face and the rest becomes an
        # ellipsis. A count says the same thing and leaves room for the help.
        n = len(value)
        return f"{n} stud{'y' if n == 1 else 'ies'} commissioned"
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
    n_submitted = len(submitted)   # before standing campaigns are carried in
    for team_id in world.teams:
        _carry_campaigns(con, submitted, team_id, nxt)
    run_round(world, params, submitted, preset=g["preset"])

    db.save_round(con, nxt, world, params.config_hash())
    db.set_game(con, round=nxt, open_round=None)
    with con:
        db.log(con, actor, "round.run",
               f"r{nxt}: {n_submitted}/{len(world.teams)} submitted")

    if out_dir is not None:
        for team in world.teams.values():
            card = scoring.final_score(team, params, world.teams) if nxt >= 2 else None
            report.render(team, nxt, out_dir / f"round_{nxt}", card)
        console.render(world, params, out_dir / f"round_{nxt}")

    return {"round": nxt, "submitted": n_submitted, "teams": len(world.teams)}


def standing_campaigns(con, team_id: str, round_: int):
    """The campaign setup in force for `round_`: this month's if the team set
    one, otherwise the last one it set. None means it never has.

    Campaigns are a standing arrangement, the way an ads account is - they run
    until someone changes them. Resetting to broad stores an empty list, which
    is a setting too, so it carries forward as well.
    """
    for rnd in range(round_, 0, -1):
        value = (db.submission(con, rnd, team_id) or {}).get(targeting.DECISION)
        if value is not None:
            return value
    return None


def _carry_campaigns(con, submitted: dict, team_id: str, round_: int) -> None:
    if targeting.DECISION in submitted.get(team_id, {}):
        return
    standing = standing_campaigns(con, team_id, round_ - 1)
    if standing is not None:
        submitted.setdefault(team_id, {})[targeting.DECISION] = standing


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

    brands = {tid: (rec.get("config") or {}).get("brand_name")
              for tid, rec in db.foundings(con).items()}
    rows = []
    for tid, team in world.teams.items():
        h = team.history[-1] if team.history else {}
        brand = brands.get(tid)
        rows.append({"team_id": tid,
                     "name": brand if brand and brand != "Unnamed" else team.brand_name,
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
    # The world blob keeps the brand it was built with. Reading the current one
    # here means a rename shows on every report without rewriting a result.
    brand = (db.founding(con, team_id) or {}).get("config", {}).get("brand_name")
    if brand and brand != "Unnamed":
        team.brand_name = brand
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
    submitted = db.submissions(con, round_)
    # Campaigns run until changed, so the file carries the standing setup the
    # app would run - otherwise an offline month silently goes back to broad.
    for row in db.accounts(con, "team"):
        _carry_campaigns(con, submitted, row["team_id"], round_)
    for team_id, decisions in sorted(submitted.items()):
        for code, value in sorted(decisions.items()):
            if code == targeting.DECISION:
                value = json.dumps(value)
            elif isinstance(value, list):
                value = ";".join(str(v) for v in value)
            w.writerow([team_id, code, value])
    return buf.getvalue()


# --- The research desk ---------------------------------------------------------
#
# M16 has always written real findings to team.reports and nothing has ever read
# them. A team bought MR-07 for 75,000, the P&L charged it, the engine computed a
# perception gap - and the student saw no number. Everything below is the reading
# half of a mechanism that was only ever half built.
#
# A finding needs three things to be worth the money: what it says, how much to
# trust it, and which decision it bears on. The table carries all three, because
# a number with no decision attached is trivia.

STUDY_READS = {
    "MR-01": dict(kind="seasonal", asks="How big is the category about to get?",
                  bears_on=["3.1", "3.2", "7.5", "7.1"],
                  read="An index above 1.0 is a month the whole category buys "
                       "more. It does not move YOUR share - it moves the pool "
                       "your share is taken from. Spend and stock into a peak "
                       "you can actually serve; a peak you cannot serve is "
                       "someone else's month."),
    "MR-02": dict(kind="pkr", asks="What is the market really charging, net of promo?",
                  bears_on=["1.1", "1.5"],
                  read="This is the average basket price across the category, "
                       "after discounts. Your own price against it is your real "
                       "position - not the one on your website."),
    "MR-03": dict(kind="pct", asks="What share of the category is yours?",
                  bears_on=["3.1", "3.2", "3.4", "1.5"],
                  read="Share is the only number here you can only win by "
                       "taking it from somebody. Rising share on falling margin "
                       "is a decision, not an accident."),
    "MR-04": dict(kind="pkr", asks="What are rivals spending to get it?",
                  bears_on=["3.1", "3.2", "3.4", "3.9"],
                  read="Estimated from the outside, and understated on purpose - "
                       "outside-in spend estimates always are. Treat it as a "
                       "floor, not a figure."),
    "MR-05": dict(kind="warning", asks="What is about to happen to the category?",
                  bears_on=["7.5", "7.1", "3.1", "12.5"],
                  read="It catches about three events in five. Silence is not "
                       "an all-clear."),
    "MR-06": dict(kind="segments", asks="What do the segments actually trade off?",
                  bears_on=["1.5", "1.1", "2.2", "3.4"],
                  read="The weights are what each segment cares about, and they "
                       "are the only place the trade-offs are written down. A "
                       "segment that weights price at 0.42 will not pay for "
                       "quality you added at a cost."),
    "MR-07": dict(kind="gap", asks="What does the market think of you, against what you deliver?",
                  bears_on=["3.9", "3.8", "7.4", "1.5"],
                  read="Positive means you are over-promising: marketing has run "
                       "ahead of the product and the returns and ratings will "
                       "follow. Negative means you are under-selling something "
                       "you already do well, which is the cheapest gap to close."),
    "MR-08": dict(kind="index", asks="Is brand spend building anything?",
                  bears_on=["3.9", "3.8"],
                  read="Brand equity carries most of your organic traffic and it "
                       "decays every month you do not feed it. Slow to move, "
                       "expensive to rebuild."),
    "MR-09": dict(kind="score", asks="What do customers say after the parcel arrives?",
                  bears_on=["10.1", "7.4", "8.3", "7.2"],
                  read="The cheapest early warning in the catalogue. It turns "
                       "before your revenue does, because unhappy customers stop "
                       "reordering before they stop ordering."),
    "MR-10": dict(kind="pct", asks="How fast is the customer base leaking?",
                  bears_on=["6.1", "2.2", "3.4"],
                  read="A blended monthly churn rate. It climbs when you buy "
                       "customers with discounts: a deal-driven cohort churns at "
                       "more than twice the rate of an organic one, so the mix "
                       "you acquired shows up here months later."),
    "MR-11": dict(kind="pkr", asks="What does a customer cost the rest of the market?",
                  bears_on=["3.1", "3.2", "3.4"],
                  read="Market-level, not yours. Paying well above it means your "
                       "creative or your targeting is doing the work badly; well "
                       "below it usually means you are buying a cheaper customer "
                       "than you think."),
    "MR-12": dict(kind="roas", asks="What did marketing actually contribute?",
                  bears_on=["3.1", "3.2", "3.4", "3.6"],
                  read="The platforms report the number on the left for free and "
                       "over-attribute it by about a third. The number on the "
                       "right is what your marketing really returned. Budgets "
                       "set on the free number are set on someone else's "
                       "marketing material."),
    "MR-13": dict(kind="pct", asks="Where do you rank on the marketplace?",
                  bears_on=["4.1", "1.1", "1.5"],
                  read="Only means anything while you are listed."),
    "MR-14": dict(kind="index", asks="Is the creative any good, before you back it?",
                  bears_on=["3.8", "3.1", "11.3"],
                  read="Twenty thousand to find out before you spend four hundred "
                       "thousand pushing it. Creative quality multiplies every "
                       "paid rupee that follows it."),
    "MR-15": dict(kind="pct", asks="Is the courier doing what it promised?",
                  bears_on=["8.2", "8.3", "9.1"],
                  read="Stated service levels and actual ones are different "
                       "numbers. In a COD market the gap between them is paid "
                       "for twice - once in the failed delivery and again in the "
                       "customer who does not come back."),
    "MR-16": dict(kind="pct", asks="Why are parcels coming back?",
                  bears_on=["7.4", "1.5", "8.5", "3.8"],
                  read="A quality return and an expectation return need opposite "
                       "fixes: one is the product, the other is what your "
                       "marketing led people to expect."),
    "MR-17": dict(kind="leadtime", asks="Is the supply chain about to slip?",
                  bears_on=["7.1", "7.5", "7.2", "1.1"],
                  read="It catches about seven shocks in ten. A multiplier above "
                       "1.0 is a month your orders may not land. Note what the "
                       "defence costs before you mount it - cover is cheaper "
                       "than switching supplier, and both are often dearer than "
                       "the shock."),
    "MR-18": dict(kind="index", asks="Does the range fit what people want?",
                  bears_on=["1.1", "1.5", "11.1"],
                  read="Assortment fit against the segments you are actually "
                       "drawing. A low score with high traffic means you are "
                       "bringing the wrong people to the right shop, or the "
                       "reverse."),
    "MR-19": dict(kind="dossier", asks="Everything the competition will tell you from outside.",
                  bears_on=["3.1", "1.1", "1.5", "7.5"],
                  read="Price, share, rival spend and how much stock the field "
                       "is sitting on. Thin cover across the field is a month "
                       "somebody runs out; deep cover is a month somebody "
                       "discounts."),
    "MR-20": dict(kind="index", asks="Could you actually run quick commerce?",
                  bears_on=["8.2", "7.5", "8.3"],
                  read="Readiness is delivery speed and stock depth together. "
                       "Entering without both is a promise you will break in "
                       "public."),
}


def _finding(code: str, payload: dict, params, history: dict | None) -> dict | None:
    """One study, rendered as something a student can act on in ten seconds."""
    meta = STUDY_READS.get(code)
    study = next((s for s in params.studies if s["code"] == code), None)
    if meta is None or study is None or payload is None:
        return None

    out = {
        "code": code, "name": study["name"],
        "asks": meta["asks"], "read": meta["read"], "kind": meta["kind"],
        "tier": study["tier"],
        "as_of": payload.get("as_of_round"),
        "lagged": payload.get("status") == "lagged",
        "no_data": payload.get("status") == "no_data",
        "band": payload.get("error_band"),
        "bears_on": [{"code": c, "name": REGISTRY[c].name}
                     for c in meta["bears_on"] if c in REGISTRY],
    }
    if out["no_data"]:
        out["headline"] = "No data"
        out["detail"] = ("Nothing to measure yet - this study needs the "
                         "decision it reports on to be switched on.")
        return out

    kind, value = meta["kind"], payload.get("reported")
    if kind == "seasonal":
        idx = payload.get("seasonal_index", {})
        months = [(int(r), v) for r, v in sorted(idx.items(), key=lambda kv: int(kv[0]))]
        peak = max(months, key=lambda m: m[1]) if months else None
        out["headline"] = (f"Month {peak[0]} peaks at {peak[1]:.2f}x"
                           if peak else "No forecast")
        out["series"] = [{"label": f"Month {m}", "value": f"{v:.2f}x",
                          "hot": v >= 1.15, "cold": v <= 0.95} for m, v in months]
    elif kind == "leadtime":
        view = payload.get("lead_time_forecast", {})
        months = [(int(r), v.get("lead_time_mult", 1.0))
                  for r, v in sorted(view.items(), key=lambda kv: int(kv[0]))]
        worst = max(months, key=lambda m: m[1]) if months else None
        out["headline"] = ("No slip forecast" if not worst or worst[1] <= 1.05
                           else f"Month {worst[0]}: lead times {worst[1]:.1f}x")
        out["series"] = [{"label": f"Month {m}",
                          "value": "normal" if v <= 1.05 else f"{v:.1f}x slower",
                          "hot": v > 1.05, "cold": False} for m, v in months]
    elif kind == "warning":
        warn = payload.get("warning")
        out["headline"] = (f"{warn['event']} expected in month {warn['round']}"
                           if warn else "Nothing flagged")
        out["quiet"] = warn is None
    elif kind == "segments":
        segs = payload.get("segments", [])
        out["headline"] = f"{len(segs)} segments, with their trade-offs"
        out["segments"] = [
            {"name": s["name"], "share": f"{s['share']:.0%}",
             "repeat": f"{s['repeat_propensity']:.2f}x",
             "weights": sorted(((k.replace("_", " "), v)
                                for k, v in s["weights"].items()),
                               key=lambda kv: -kv[1])[:3]}
            for s in segs]
    elif kind == "dossier":
        parts = payload.get("bundles", {})
        out["parts"] = [f for f in
                        (_finding(c, p, params, history) for c, p in parts.items())
                        if f]
        cover = payload.get("competitor_stock")
        out["headline"] = (f"The field holds {cover:.1f} weeks of stock"
                           if cover is not None else "Four readings on the field")
        if cover is not None:
            out["verdict"] = ("Thin - somebody is about to run out"
                              if cover < 2.5 else
                              "Deep - somebody is about to discount"
                              if cover > 6.0 else
                              "Normal cover across the field")
    elif kind == "roas":
        free = (history or {}).get("roas_reported")
        out["headline"] = f"{value:.2f}x actually returned"
        out["compare"] = ({"label": "What the platforms report",
                           "value": f"{free:.2f}x",
                           "label2": "What it truly returned",
                           "value2": f"{value:.2f}x",
                           "delta": f"over-attributed by {free / value - 1:.0%}"}
                          if free and value else None)
    elif kind == "gap":
        out["headline"] = f"{value:+.1%}"
        out["verdict"] = ("Over-promising" if value > 0.03
                          else "Under-selling" if value < -0.03
                          else "Promise and delivery are in line")
    elif kind == "pkr":
        out["headline"] = f"PKR {value:,.0f}"
    elif kind == "pct":
        out["headline"] = f"{value:.1%}"
    elif kind == "score":
        out["headline"] = f"{value:.0f}"
    elif kind == "index":
        out["headline"] = f"{value:.2f}"
        out["scale"] = "on a 0 to 1 scale"
    else:
        out["headline"] = f"{value:.2f}"

    if out.get("band"):
        out["confidence"] = f"plus or minus {out['band']:.0%}"
    return out


def research_desk(con, team_id: str) -> dict:
    """Every finding this team has paid for, and what is still on the shelf."""
    params = load_params(con)
    game = db.game(con)
    world = db.load_world(con)
    team = (world.teams.get(team_id) if world else None)
    history = team.history[-1] if team and team.history else None

    findings, seen = [], set()
    reports = dict(getattr(team, "reports", {}) or {}) if team else {}
    for rnd in sorted(reports, reverse=True):
        for code, payload in sorted(reports[rnd].items()):
            if code in seen:
                continue                     # the latest reading is the reading
            seen.add(code)
            found = _finding(code, payload, params, history)
            if found:
                found["bought_round"] = rnd
                findings.append(found)

    order = {"market": 0, "customer": 1, "channel": 2, "operations": 3, "premium": 4}
    findings.sort(key=lambda f: (order.get(f["tier"], 9), f["code"]))

    # What this month's order already contains. Distinct from "owned": a team
    # can hold a reading from month 2 and have commissioned nothing since.
    open_round = game["open_round"]
    ordered = set((db.submission(con, open_round, team_id) or {}).get("12.1") or []) \
        if open_round else set()

    shelf = []
    for s in params.studies:
        code, min_round = s["code"], int(s["min_round"])
        # min_round has sat in studies.csv unread since the catalogue was
        # written. A team could commission Q-Commerce Readiness in month 1 and
        # get a reading on a business that cannot yet be ready for anything.
        locked = open_round is not None and min_round > open_round
        shelf.append({
            "code": code, "name": s["name"], "price": float(s["price"]),
            "tier": s["tier"], "lag": int(s["lag_rounds"]),
            "band": float(s["error_band"]), "min_round": min_round,
            "asks": STUDY_READS.get(code, {}).get("asks", s["note"]),
            "owned": code in seen,
            "ordered": code in ordered,
            "locked": locked,
            "can_order": open_round is not None and not locked,
        })
    return {"findings": findings, "shelf": shelf,
            "round": game["round"], "open_round": open_round,
            "ordered_cost": sum(r["price"] for r in shelf if r["ordered"]),
            "roas_reported": (history or {}).get("roas_reported"),
            "spent": _research_spend(con, team_id, params, game["round"])}


def _research_spend(con, team_id: str, params, upto: int) -> float:
    """What research has actually cost, not what the shelf lists.

    A study bought in three separate months is paid for three times, and the
    founding round is half price. Listing each study once at list price would
    understate a team that re-buys and overstate one that bought at founding.
    """
    price = {s["code"]: float(s["price"]) for s in params.studies}
    total = 0.0
    record = db.founding(con, team_id)
    for code in ((record or {}).get("config", {}) or {}).get("research", []):
        total += price.get(code, 0.0) * founding_mod.FOUNDING_RESEARCH_DISCOUNT
    for rnd in range(1, (upto or 0) + 1):
        for code in (db.submission(con, rnd, team_id) or {}).get("12.1", []) or []:
            total += price.get(code, 0.0)
    return total


# --- Campaign setup (3.10) ---------------------------------------------------------
#
# The budgets stay on the decision form. This desk decides how each one is
# spent, next to the numbers last month's campaigns produced, which is the only
# place the choice makes sense - the same reasoning that put studies on the
# research desk.

SLOTS = targeting.MAX_PER_CHANNEL


def campaign_summary(value) -> str:
    if value is None:
        return ""
    if not value:
        return "Broad on every channel"
    counts: dict[str, int] = {}
    for c in value:
        counts[c["channel"]] = counts.get(c["channel"], 0) + 1
    return " · ".join(f"{targeting.CHANNEL_NAMES[ch]} {n}"
                      for ch, n in counts.items())


def _budget(con, team_id: str, round_: int, code: str) -> float:
    for rnd in range(round_, 0, -1):
        value = (db.submission(con, rnd, team_id) or {}).get(code)
        if value not in (None, ""):
            return float(value)
    return float(REGISTRY[code].default_when_disabled)


def campaign_form(form, sold: list[str]) -> tuple[list[dict], list[str], list[dict]]:
    """Read the desk's slots into a campaign list, and say what is wrong.

    The third value is the form as typed, shares unscaled, so a refused save
    can be shown back instead of wiping everything the team entered."""
    raw, errors = [], []
    for ch in targeting.CHANNELS:
        used = []
        for i in range(SLOTS):
            key = f"{ch}_{i}"
            if not form.get(f"use_{key}"):
                continue
            share = (form.get(f"share_{key}") or "").replace("%", "").strip()
            try:
                share_v = float(share) if share else 0.0
            except ValueError:
                errors.append(f"{targeting.CHANNEL_NAMES[ch]} campaign {i + 1}: "
                              f"{share!r} is not a percentage")
                continue
            c = {"channel": ch, "name": (form.get(f"name_{key}") or "").strip()
                 or f"{targeting.CHANNEL_NAMES[ch]} {i + 1}",
                 "share": share_v / 100, "skus": form.getlist(f"skus_{key}"),
                 "_slot": i}
            if ch == "google_search":
                c |= {"keywords": form.get(f"keywords_{key}"),
                      "match": form.get(f"match_{key}")}
            else:
                interests = form.getlist(f"interests_{key}")
                if len(interests) > targeting.MAX_INTERESTS:
                    errors.append(f"{c['name']}: pick at most "
                                  f"{targeting.MAX_INTERESTS} interests")
                c |= {"objective": form.get(f"objective_{key}"),
                      "ages": form.getlist(f"ages_{key}"),
                      "gender": form.get(f"gender_{key}"),
                      "geo": form.getlist(f"geo_{key}"),
                      "interests": interests,
                      "language": form.get(f"language_{key}") or "",
                      "format": form.get(f"format_{key}") or ""}
            used.append(c)
        if form.get(f"ab_{ch}"):
            slots = {int(c["_slot"]) for c in used}
            if {0, 1} <= slots:
                for c in used:
                    if c["_slot"] in (0, 1):
                        c["test"] = "AB"[c["_slot"]]
            else:
                errors.append(f"{targeting.CHANNEL_NAMES[ch]}: an A/B test needs "
                              f"campaigns 1 and 2 both running")
        for c in used:
            c.pop("_slot", None)
        total = sum(c["share"] for c in used) * 100
        if used and abs(total - 100) > 0.5:
            errors.append(f"{targeting.CHANNEL_NAMES[ch]}: the campaigns share "
                          f"{total:.0f}% of the budget; they must share 100%")
        raw.extend(used)
    return (targeting.clean(raw, sold), errors,
            targeting.clean(raw, sold, normalise=False))


def campaign_desk(con, team_id: str, draft: list[dict] | None = None) -> dict:
    """Everything the campaign page shows: the setup, the budgets it splits,
    last month's numbers per campaign, and whether it can be changed now."""
    params = load_params(con)
    game = db.game(con)
    open_round = game["open_round"]
    can_edit = bool(open_round) and any(
        s.code == targeting.DECISION for s in open_decisions(con, open_round))
    at = open_round or game["round"]
    current = standing_campaigns(con, team_id, at) if at else None
    if draft is not None:
        current = draft
    this_month = (db.submission(con, open_round, team_id) or {}) if open_round else {}

    shelf = monthly_catalogue(con, team_id, this_month)
    sold = [r["code"] for r in shelf]
    channels = []
    for ch, code in targeting.CHANNELS.items():
        mine = [c for c in (current or []) if c["channel"] == ch]
        slots = []
        for i in range(SLOTS):
            c = mine[i] if i < len(mine) else None
            slots.append({"key": f"{ch}_{i}", "used": c is not None,
                          "c": c or targeting.blank(ch)
                               | {"name": "", "share": 0.0}})
        channels.append({"code": ch, "name": targeting.CHANNEL_NAMES[ch],
                         "decision": code, "decision_name": REGISTRY[code].name,
                         "budget": _budget(con, team_id, at or 1, code),
                         "slots": slots, "social": ch in targeting.SOCIAL,
                         "broad": not mine,
                         "ab": any(c.get("test") for c in mine)})

    world = db.load_world(con)
    team = world.teams.get(team_id) if world else None
    last = team.history[-1] if team and team.history else None
    return {
        "open_round": open_round, "round": game["round"], "can_edit": can_edit,
        "unlock_round": REGISTRY[targeting.DECISION].unlock_round,
        "set_this_month": targeting.DECISION in this_month,
        "ever_set": current is not None,
        "channels": channels, "shelf": shelf,
        "categories": sorted({r["category"] for r in shelf}),
        "last": (last or {}).get("campaigns") or [], "last_round": game["round"],
        "tests": (last or {}).get("ab_tests") or [],
        "choices": {"ages": list(targeting.AGES), "genders": targeting.GENDERS,
                    "tiers": targeting.TIER_NAMES, "interests": targeting.INTERESTS,
                    "objectives": targeting.OBJECTIVES,
                    "languages": targeting.LANGUAGES, "formats": targeting.FORMATS,
                    "keywords": targeting.KEYWORDS, "matches": targeting.MATCHES},
    }
