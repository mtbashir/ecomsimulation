"""Strategy grid: every team's choices side by side, for the instructor.

Decisions run down the page and teams across it. A choice decision gets one
row per option with "Yes" under each team that picked it, so the shape of the
field - who went premium, who went marketplace-first, who is alone - reads at
a glance. A number gets one row with each team's value.

Month decisions show what is in force: the last value a team submitted at or
before the month asked for, because a team that does not resubmit keeps its
previous decisions.
"""
from __future__ import annotations

import json

from .. import founding as founding_mod
from ..decisions import REGISTRY
from . import db, service

LONG_LIST = 6

# The setup form's own stages, so the grid reads in the order teams decided.
FOUNDING_GROUPS = [
    ("Who you are", ["Positioning statement", "Board objective"]),
    ("Who you sell to", ["Quality tier", "Categories", "Priority segments"]),
    ("What you sell and where it comes from",
     ["Business model", "Range", "Default sourcing", "Sourcing by product"]),
    ("What you build it on",
     ["Platform", "Fulfilment", "Cash on delivery", "Payment gateway"]),
    ("Where the money and people go", ["Capital split", "Headcount"]),
    ("What you are promising", ["Founding research", "Promised in the plan"]),
]

# Shown as their own product-by-product tables, so not repeated as one line.
OWN_TABLES = {"1.1", "7.1"}


def untouched(block: dict) -> bool:
    """True when no team has made this decision at all."""
    if block["kind"] == "choice":
        return all(r.get("muted") for r in block["rows"] if r["count"])
    return not any(c for r in block["rows"] for c in r["cells"])


def split_unused(blocks: list[dict]) -> tuple[list[dict], list[str]]:
    """Decisions somebody made, and the names of those nobody did - listed in
    one line, so a page of dashes does not bury the choices that differ."""
    used = [b for b in blocks if not untouched(b)]
    return used, [b["title"] for b in blocks if untouched(b)]

def _choice(title: str, options: list[tuple[str, str]], picks: dict[str, set],
            teams: list[str], note: str = "") -> dict:
    """One decision as option rows. `picks` maps team -> set of values chosen.

    Options nobody chose stay in, dashed across: an empty row is information
    too - nobody went premium is worth seeing. Values a team holds that are not
    in `options` (a free-text statement, an old code) get a row of their own.
    """
    known = [v for v, _ in options]
    extra = sorted({v for vs in picks.values() for v in vs} - set(known),
                   key=str)
    labels = dict(options)
    rows = []
    for value in known + extra:
        cells = [value in picks.get(t, set()) for t in teams]
        rows.append({"label": labels.get(value, str(value)),
                     "cells": ["Yes" if c else "" for c in cells],
                     "count": sum(cells)})
    # A long list (products, studies) is read for what was picked; the options
    # nobody took are counted rather than listed. A short one keeps them, since
    # "nobody went premium" is the point.
    if len(rows) > LONG_LIST:
        hidden = sum(1 for r in rows if not r["count"])
        rows = [r for r in rows if r["count"]]
        if hidden:
            note = (note + "; " if note else "") + \
                f"{hidden} option{'' if hidden == 1 else 's'} no team chose"
    unset = [not picks.get(t) for t in teams]
    if any(unset):
        rows.append({"label": "Not set", "cells": ["Yes" if u else "" for u in unset],
                     "count": sum(unset), "muted": True})
    return {"title": title, "kind": "choice", "rows": rows, "note": note}


def _values(title: str, rows: list[tuple[str, dict]], teams: list[str],
            note: str = "") -> dict:
    """One decision, or a set of related numbers, as one row each."""
    return {"title": title, "kind": "value", "note": note,
            "rows": [{"label": label, "cells": [by_team.get(t, "") for t in teams]}
                     for label, by_team in rows]}


def _pkr(x) -> str:
    return service._fmt(float(x), "pkr") if x not in (None, "") else ""


# --- Round 0 ---------------------------------------------------------------------

def founding_blocks(con, teams: list[str], choices: dict) -> list[dict]:
    """The founding round, grouped as the setup form asks it, with the
    decisions no team made named per group. `choices` carries the option labels
    the setup form uses, so the grid says what the team saw."""
    params = service.load_params(con)
    recs = db.foundings(con)
    cfg = {t: (recs.get(t) or {}).get("config") or {} for t in teams}

    def pick(key):
        out = {}
        for t in teams:
            v = cfg[t].get(key)
            if v in (None, "", [], {}):
                continue
            out[t] = set(v) if isinstance(v, list) else {v}
        return out

    def opts(key):
        return [(v, label) for v, label, *_ in choices[key]]

    segments = [(s["code"], s["name"]) for s in params.segments]
    skus = {s["code"]: s for s in params.skus}
    studies = [(s["code"], s["name"]) for s in params.studies]
    chosen_skus = {c for t in teams for c in cfg[t].get("assortment") or []}

    def sourcing_mix(t):
        by = cfg[t].get("sourcing_by_sku") or {}
        if not by:
            return ""
        counts = {}
        for v in by.values():
            counts[v] = counts.get(v, 0) + 1
        return " · ".join(f"{n} {k}" for k, n in sorted(counts.items()))

    b = {}
    for blk in [
        _choice("Positioning statement", [], pick("positioning_statement"), teams,
                "Each team's own words"),
        _choice("Board objective", [(c, label) for c, label, _ in
                                    founding_mod.OBJECTIVES],
                pick("objective"), teams),
        _choice("Quality tier", opts("tier"), pick("tier"), teams),
        _choice("Categories", [(c, c.title()) for c in founding_mod.CATEGORIES],
                pick("categories"), teams, "Two each"),
        _choice("Priority segments", segments, pick("segment_priority"), teams,
                "Two each"),
        _choice("Business model", opts("model"), pick("model"), teams),
        _choice("Default sourcing", opts("sourcing"), pick("sourcing"), teams),
        _values("Sourcing by product", [("Products by source",
                                         {t: sourcing_mix(t) for t in teams})],
                teams),
        _choice("Range", [(c, f'{skus[c]["name"]} ({skus[c]["category"]})')
                          for c in skus if c in chosen_skus],
                pick("assortment"), teams,
                "Products at least one team stocks"),
        _choice("Platform", opts("tech_stack"), pick("tech_stack"), teams),
        _choice("Fulfilment", opts("fulfilment"), pick("fulfilment"), teams),
        _choice("Cash on delivery", [(True, "Accept COD"), (False, "No COD")],
                {t: {bool(cfg[t]["cod_enabled"])} for t in teams
                 if "cod_enabled" in cfg[t]}, teams),
        _choice("Payment gateway", opts("gateway"), pick("gateway"), teams),
        _values("Capital split", [
            (label, {t: _pkr(cfg[t].get(key)) for t in teams if cfg[t]})
            for key, label in [("capital_inventory", "Inventory"),
                               ("capital_marketing", "Marketing"),
                               ("capital_technology", "Technology"),
                               ("capital_reserve", "Reserve")]], teams),
        _values("Headcount", [
            (label, {t: str((cfg[t].get("headcount") or {}).get(key, ""))
                     for t in teams if cfg[t]})
            for key, label in [("marketing", "Marketing"), ("ops", "Operations"),
                               ("cs", "Customer service"),
                               ("analytics", "Analytics")]], teams),
        _choice("Founding research", studies, pick("research"), teams),
        _values("Promised in the plan", [
            ("Repeat order share", {t: f'{float(cfg[t]["target_repeat_share"]):g}%'
                                    for t in teams
                                    if cfg[t].get("target_repeat_share")}),
            ("Cost per new customer", {t: _pkr(cfg[t]["target_cac"]) for t in teams
                                       if cfg[t].get("target_cac")})], teams),
    ]:
        b[blk["title"]] = blk
    out = []
    for group, titles in FOUNDING_GROUPS:
        used, unused = split_unused([b[t] for t in titles])
        out.append({"group": group, "blocks": used, "unused": unused})
    return out


# --- A trading month ---------------------------------------------------------------

def in_force(con, teams: list[str], round_: int) -> dict[str, dict]:
    """Each team's decisions as they stand for `round_`: the latest value it
    submitted for each decision, at or before that month."""
    out = {t: {} for t in teams}
    rows = con.execute(
        "SELECT round, team_id, decisions FROM submission WHERE round <= ? "
        "ORDER BY round", (round_,)).fetchall()
    for r in rows:
        if r["team_id"] in out:
            out[r["team_id"]].update(json.loads(r["decisions"]))
    return out


def month_blocks(con, teams: list[str], round_: int) -> list[dict]:
    """Every decision open this month or set by any team, group by group, with
    the ones no team has made named separately."""
    params = service.load_params(con)
    held = in_force(con, teams, round_)
    open_now = {s.code for s in service.open_decisions(con, round_)}
    groups: dict[str, list[dict]] = {}
    for code, spec in REGISTRY.items():
        if code in OWN_TABLES:
            continue
        values = {t: held[t][code] for t in teams if code in held[t]}
        if code not in open_now and not values:
            continue
        rows = service.catalogue_options(params, spec.catalogue) \
            if spec.catalogue else []
        title = spec.name
        if spec.kind in ("select", "multi"):
            if spec.options:
                options = [(o[0], o[1]) for o in spec.options]
            elif rows:
                options = [(r["value"], r["label"]) for r in rows]
            else:                       # an on/off lever with no listed options
                options = [(True, "On"), (False, "Off")]
            picks = {}
            for t, v in values.items():
                if spec.kind == "multi":
                    picks[t] = set(v or [])
                elif not options or isinstance(options[0][0], bool):
                    picks[t] = {bool(v) if not isinstance(v, str)
                                else v in ("on", "true", "True", "1")}
                else:
                    picks[t] = {"" if v is None else str(v)}
            block = _choice(title, options, picks, teams)
        else:
            # Free text is read in full: a memo cut at 44 characters says nothing.
            summary = {t: (str(v) if spec.kind == "text" else
                           service.decision_summary(spec, v, rows)) or "—"
                       for t, v in values.items()}
            block = _values(title, [("", summary)], teams)
            block["text"] = spec.kind == "text"
        block["code"] = code
        groups.setdefault(spec.group, []).append(block)
    out = []
    for g, blocks in groups.items():
        used, unused = split_unused(blocks)
        out.append({"group": g, "blocks": used, "unused": unused})
    return out


# --- Product by product ------------------------------------------------------------

def _founded(con, params, teams):
    """Each team's founding setup as a Founding, the default where it has none."""
    recs = db.foundings(con)
    out = {}
    for t in teams:
        rec = recs.get(t)
        out[t] = (service.founding_from_dict(rec["config"], params) if rec
                  else founding_mod.Founding.default(params))
    return out


def _range_of(con, params, teams, month, founded) -> dict[str, list[str]]:
    """What each team sells in `month`: its range as the month opened."""
    world = db.load_world(con, month - 1) if month > 1 else None
    out = {}
    for t in teams:
        team = world.teams.get(t) if world is not None else None
        out[t] = list(team.active_skus) if team is not None and team.active_skus \
            else list(founded[t].assortment)
    return out


def _product_rows(params, ranges, teams, cell) -> list[dict]:
    """One row per product any team sells, grouped by category, with
    `cell(team, code)` for each team that sells it and None where it does not."""
    sold = {c for t in teams for c in ranges[t]}
    rows, category = [], None
    for sku in sorted((s for s in params.skus if s["code"] in sold),
                      key=lambda s: (s["category"], -float(s["revenue_weight"]))):
        if sku["category"] != category:
            category = sku["category"]
            rows.append({"category": category.title()})
        rows.append({"label": sku["name"],
                     "cells": [cell(t, sku["code"]) if sku["code"] in ranges[t]
                               else None for t in teams]})
    return rows


def range_table(con, teams: list[str], month: int) -> list[dict]:
    """Regular price and discount, product by product, as they stand for the
    month: the founding price, then each later change to a line, in order."""
    params = service.load_params(con)
    founded = _founded(con, params, teams)
    ranges = _range_of(con, params, teams, month, founded)
    grid = {t: {} for t in teams}
    site = {t: None for t in teams}
    for r in con.execute("SELECT team_id, decisions FROM submission WHERE "
                         "round <= ? ORDER BY round", (month,)).fetchall():
        if r["team_id"] not in grid:
            continue
        d = json.loads(r["decisions"])
        for code, c in (d.get("1.1") or {}).items():
            grid[r["team_id"]].setdefault(code, {}).update(
                {k: v for k, v in (c or {}).items() if v not in (None, "")})
        if d.get("2.2") is not None:
            site[r["team_id"]] = float(d["2.2"])

    def cell(t, code):
        f, c = founded[t], grid[t].get(code) or {}
        price = float(c.get("price") or (f.prices or {}).get(code)
                      or founding_mod.reference_price(params.sku(code), f.tier))
        disc = float(c["discount"]) if c.get("discount") is not None \
            else (site[t] or 0.0)
        return {"price": f"{price:,.0f}",
                "discount": f"{disc * 100:.0f}% off" if disc > 0 else ""}
    return _product_rows(params, ranges, teams, cell)


def stock_table(con, teams: list[str], month: int) -> dict:
    """Stock on hand, weeks of cover and units ordered, product by product.

    A month that has run reports what happened in it. The open month shows the
    stock it starts with and what each team has ordered so far.
    """
    params = service.load_params(con)
    game = db.game(con)
    ran = month <= game["round"]
    world = db.load_world(con, month if ran else None)
    if world is None:
        return {"rows": [], "ran": ran}
    weeks = float(params["round_months"]) * 52 / 12
    held = in_force(con, teams, month) if not ran else {}
    founded = _founded(con, params, teams)
    ranges = _range_of(con, params, teams, month, founded)
    stock = {}
    for t in teams:
        team = world.teams.get(t)
        h = team.history[-1] if team is not None and team.history else {}
        stock[t] = {r["code"]: r for r in h.get("stock") or []}

    def cell(t, code):
        r = stock[t].get(code)
        if r is None:
            return {"stock": "", "cover": "", "ordered": ""}
        on_hand = float(r.get("close", 0.0))
        demand = float(r.get("wanted") or r.get("sold") or 0.0) / weeks
        if ran:
            ordered = float(r.get("ordered") or 0.0)
        else:
            order = (held.get(t) or {}).get("7.1")
            ordered = float(order.get(code, 0.0)) if isinstance(order, dict) \
                else None
        return {"stock": f"{on_hand:,.0f}",
                "cover": f"{on_hand / demand:.1f} wk" if demand > 0 else "",
                "ordered": "" if ordered is None else f"{ordered:,.0f}"}
    rows = _product_rows(params, ranges, teams, cell)

    totals = []
    for t in teams:
        lines = [cell(t, c) for c in ranges[t]]
        on_hand = sum(float(stock[t][c].get("close", 0.0))
                      for c in ranges[t] if c in stock[t])
        if ran:
            ordered = sum(float(stock[t][c].get("ordered") or 0.0)
                          for c in ranges[t] if c in stock[t])
            ordered_s = f"{ordered:,.0f}"
        else:
            order = (held.get(t) or {}).get("7.1")
            total = sum(float(u) for u in order.values()) \
                if isinstance(order, dict) else (float(order) if order else 0.0)
            ordered_s = f"{total:,.0f}" if order else ""
        demand = sum(float(stock[t][c].get("wanted") or 0.0)
                     for c in ranges[t] if c in stock[t]) / weeks
        totals.append({"stock": f"{on_hand:,.0f}" if lines else "",
                       "cover": f"{on_hand / demand:.1f} wk" if demand > 0 else "",
                       "ordered": ordered_s})
    rows.append({"label": "All products", "total": True, "cells": totals})
    return {"rows": rows, "ran": ran}
