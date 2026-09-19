"""Decision intake and results output.

    Google Form -> decisions.csv -> python run.py -> report_<team>.html

Deliberately file-based (docs/12-solo-delivery-plan.md): no web application to
own, students never touch the engine, and the day a developer arrives the
engine ports unchanged.
"""
from __future__ import annotations

import csv
from pathlib import Path

from .decisions import REGISTRY

# Decisions whose value is a list of codes rather than a scalar.
# Decisions submitted as a list of codes. Courier mix is not one of them:
# it is a split, handled by the "shares" kind.
LIST_DECISIONS = {"12.1", "1.2"}


class SubmissionError(ValueError):
    """A decisions file that cannot be read."""


def read_decisions(path: str | Path) -> dict[str, dict]:
    """Read a long-format decisions file.

        team_id,decision,value
        team_01,3.1,650000
        team_01,12.1,"MR-01;MR-17"

    Long format because a Google Form export is long, and because a wide file
    breaks every time the decision set changes.
    """
    rows = list(csv.DictReader(Path(path).open(newline="", encoding="utf-8")))
    if not rows:
        raise SubmissionError(f"{path} is empty")
    required = {"team_id", "decision", "value"}
    missing = required - set(rows[0])
    if missing:
        raise SubmissionError(
            f"{path} is missing column(s): {', '.join(sorted(missing))}")

    out: dict[str, dict] = {}
    problems: list[str] = []
    for i, row in enumerate(rows, start=2):
        team = (row["team_id"] or "").strip()
        code = (row["decision"] or "").strip()
        raw = (row["value"] or "").strip()
        if not team or not code:
            continue
        if code not in REGISTRY:
            problems.append(f"line {i}: unknown decision {code!r}")
            continue
        out.setdefault(team, {})
        if raw == "":
            # A blank field means "use the default" - the resolver already does
            # exactly that for a decision it is not given, so leave it out.
            continue
        try:
            out[team][code] = _coerce(code, raw)
        except SubmissionError as exc:
            problems.append(f"line {i}: {exc}")

    if problems:
        raise SubmissionError("; ".join(problems[:5]))
    return out


def _coerce(code: str, raw: str):
    spec = REGISTRY[code]
    if spec.kind == "shares":
        # "speed:0.3;value:0.4;wide:0.3" - a split, which is what the engine
        # reads. A bare list of codes here used to parse cleanly and then be
        # silently ignored downstream.
        out = {}
        for part in raw.replace(",", ";").split(";"):
            if not part.strip():
                continue
            name, _, share = part.partition(":")
            if not share:
                raise SubmissionError(
                    f"{code}: {part!r} needs a share, e.g. speed:0.3")
            try:
                out[name.strip()] = float(share.strip().rstrip("%")) / (
                    100 if "%" in share else 1)
            except ValueError:
                raise SubmissionError(f"{code}: {share!r} is not a number")
        total = sum(out.values())
        if out and abs(total - 1.0) > 0.01:
            raise SubmissionError(
                f"{code}: shares add up to {total:.2f}, they must add up to 1")
        return out
    if code in LIST_DECISIONS:
        return [v.strip() for v in raw.replace(",", ";").split(";") if v.strip()]
    kind = spec.kind
    if kind in {"num", "pct", "curr"}:
        try:
            return float(raw.replace(",", "").rstrip("%")) / (
                100 if kind == "pct" and raw.endswith("%") else 1)
        except ValueError:
            raise SubmissionError(f"{code}: {raw!r} is not a number")
    # Only a genuinely yes/no lever converts to a bool. "off" on a lever whose
    # values are "on"/"off" is the string "off": turning it into False made the
    # engine read str(False) and leave the lever switched on.
    if kind == "select" and isinstance(spec.default_when_disabled, bool):
        if raw.lower() in {"true", "yes", "on", "1"}:
            return True
        if raw.lower() in {"false", "no", "off", "0"}:
            return False
    return raw


def write_template(path: str | Path, teams: list[str], preset: str = "advanced",
                   round_: int = 1) -> None:
    """Write a blank decisions file carrying each decision's default."""
    from .decisions import Resolver

    resolver = Resolver(preset=preset, round_=round_)
    with Path(path).open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["team_id", "decision", "value", "name", "group"])
        for team in teams:
            for code, spec in REGISTRY.items():
                if not (resolver.enabled(code) and resolver.unlocked(code)):
                    continue
                default = spec.default_when_disabled
                value = "" if default is None else (
                    ";".join(default) if isinstance(default, list) else default)
                w.writerow([team, code, value, spec.name, spec.group])


def write_results(path: str | Path, world) -> None:
    """Append every team's round to a cumulative results file."""
    fields = ["round", "team_id", "orders", "sessions", "conversion_rate",
              "aov_net", "revenue_net", "gross_margin_pct",
              "contribution_margin_pct", "cac_blended", "repeat_order_share",
              "active_customers", "ltv_cac_ratio", "rating", "nps",
              "service_level", "instock_rate", "delivery_success", "rto_rate",
              "return_rate", "cash_balance", "runway_rounds", "market_share",
              "binding_constraint"]
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        if new:
            w.writeheader()
        for team in world.teams.values():
            row = dict(team.history[-1])
            row["team_id"] = team.team_id
            w.writerow(row)
