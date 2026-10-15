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

def founding_blocks(con, teams: list[str],
                    choices: dict) -> tuple[list[dict], list[str]]:
    """The founding round, decision by decision, and the decisions no team
    made. `choices` carries the option labels the setup form uses, so the grid
    says what the team saw."""
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

    blocks = [
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
    ]
    return split_unused(blocks)


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
            summary = {t: service.decision_summary(spec, v, rows) or "—"
                       for t, v in values.items()}
            block = _values(title, [("", summary)], teams)
        block["code"] = code
        groups.setdefault(spec.group, []).append(block)
    out = []
    for g, blocks in groups.items():
        used, unused = split_unused(blocks)
        out.append({"group": g, "blocks": used, "unused": unused})
    return out
