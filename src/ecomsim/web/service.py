"""Bridge between the store and the engine.

The engine stays a pure function. Everything stateful - who submitted what,
which decisions are open, which parameters the instructor overrode - lives in
the database and is resolved here into the arguments `run_round` expects.
"""
from __future__ import annotations

import csv
import io

from .. import bootstrap, console, params as P, report, scoring
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
