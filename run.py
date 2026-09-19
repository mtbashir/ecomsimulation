#!/usr/bin/env python3
"""Instructor round-runner.

    python run.py new     --teams 8 --out game/     # start a game
    python run.py template --game game/             # blank decisions file
    python run.py round   --game game/              # process the round
    python run.py preview --game game/ --team team_01   # Round 0 pro-forma

The whole loop is files: a form export goes in, an HTML report per team comes
out (docs/12-solo-delivery-plan.md). No server to own, and students never
touch the engine.
"""
from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path

sys.path.insert(0, "src")

from ecomsim import bootstrap, console, params as P, report, scoring  # noqa: E402
from ecomsim.engine import run_round  # noqa: E402
from ecomsim.io_csv import (  # noqa: E402
    SubmissionError, read_decisions, write_results, write_template,
)


def _state(game: Path) -> Path:
    return game / "state.pkl"


def cmd_new(args) -> int:
    game = Path(args.out)
    game.mkdir(parents=True, exist_ok=True)
    params = P.load({"n_teams": args.teams})
    for warning in params.warnings:
        print(f"  WARNING: {warning}")
    world = bootstrap.new_world(params, run_id=args.name)
    with _state(game).open("wb") as fh:
        pickle.dump({"world": world, "preset": args.preset,
                     "overrides": {"n_teams": args.teams}}, fh)
    (game / "config.json").write_text(json.dumps({
        "name": args.name, "teams": args.teams, "preset": args.preset,
        "config_hash": params.config_hash(),
    }, indent=2))
    print(f"Game '{args.name}' created in {game}/ with {args.teams} teams "
          f"(preset {args.preset}, config {params.config_hash()})")
    print(f"Next: python run.py template --game {game}")
    return 0


def _load(game: Path):
    if not _state(game).exists():
        print(f"No game in {game}/ - run `python run.py new --out {game}` first")
        raise SystemExit(1)
    with _state(game).open("rb") as fh:
        saved = pickle.load(fh)
    return saved, P.load(saved["overrides"])


def cmd_template(args) -> int:
    game = Path(args.game)
    saved, params = _load(game)
    world = saved["world"]
    path = game / f"decisions_r{world.round + 1}.csv"
    write_template(path, list(world.teams), saved["preset"], world.round + 1)
    print(f"Wrote {path} - {len(list(world.teams))} teams, round {world.round + 1}")
    print("Values shown are defaults. Blank means 'use the default'.")
    return 0


def cmd_round(args) -> int:
    game = Path(args.game)
    saved, params = _load(game)
    world = saved["world"]
    nxt = world.round + 1

    path = Path(args.decisions) if args.decisions else game / f"decisions_r{nxt}.csv"
    if path.exists():
        try:
            submissions = read_decisions(path)
        except SubmissionError as exc:
            print(f"Could not read {path}: {exc}")
            return 1
        unknown = set(submissions) - set(world.teams)
        if unknown:
            print(f"Unknown team(s) in {path}: {', '.join(sorted(unknown))}")
            return 1
        missing = set(world.teams) - set(submissions)
        for team in sorted(missing):
            print(f"  no submission from {team} - prior round's decisions stand")
    else:
        print(f"  {path} not found - running every team on defaults")
        submissions = {}

    run_round(world, params, submissions, preset=saved["preset"])
    write_results(game / "results.csv", world)

    out = game / f"round_{world.round}"
    for team in world.teams.values():
        card = scoring.final_score(team, params, world.teams) if world.round >= 2 else None
        report.render(team, world.round, out, card)
    console_path = console.render(world, params, out)
    with _state(game).open("wb") as fh:
        pickle.dump(saved, fh)

    print(f"\nRound {world.round} processed. Reports in {out}/")
    print(f"Instructor console: {console_path}")
    print(f"{'team':<10}{'orders':>8}{'revenue':>12}{'CM':>7}{'cash':>12}  binding")
    for team in world.teams.values():
        h = team.history[-1]
        print(f"{team.team_id:<10}{h['orders']:>8,.0f}{h['revenue_net']:>12,.0f}"
              f"{h['contribution_margin_pct']:>6.1%}{h['cash_balance']:>12,.0f}"
              f"  {h['binding_constraint']}")
    return 0


def cmd_preview(args) -> int:
    from ecomsim.founding import Founding, check_balance, pro_forma, validate

    saved, params = _load(Path(args.game))
    f = Founding.default(params)
    errors = validate(f, params)
    if errors:
        for e in errors:
            print(f"  CANNOT SUBMIT: {e}")
        return 1
    pf = pro_forma(f, params)
    print(f"Pro-forma Round 1 for {args.team}\n")
    for label, key, unit in [
        ("Sessions", "sessions", ""), ("Orders", "orders", ""),
        ("Conversion rate", "conversion_rate", "%"), ("AOV", "aov_net", "PKR"),
        ("Gross revenue", "revenue_gross", "PKR"), ("Gross margin", "gross_margin_pct", "%"),
        ("Contribution margin", "contribution_margin_pct", "%"),
        ("EBITDA", "ebitda", "PKR"), ("CAC", "cac", "PKR"),
        ("Opening cash", "opening_cash", "PKR"), ("Runway (rounds)", "runway_rounds", ""),
    ]:
        v = pf[key]
        shown = f"{v * 100:.2f}%" if unit == "%" else (
            f"PKR {v:,.0f}" if unit == "PKR" else f"{v:,.1f}")
        print(f"  {label:<22}{shown:>16}")
    problems = check_balance(f, params)
    print("\n  " + ("Balanced - submittable." if not problems
                    else "NOT SUBMITTABLE:\n  - " + "\n  - ".join(problems)))
    print("\n  A projection, not a promise: it assumes every rival is an average\n"
          "  operator. Round 1 will differ, and the gap is worth reading.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    new = sub.add_parser("new", help="create a game")
    new.add_argument("--teams", type=int, default=8)
    new.add_argument("--preset", default="advanced",
                     choices=["foundation", "standard", "advanced", "expert"])
    new.add_argument("--name", default="cohort")
    new.add_argument("--out", default="game")
    new.set_defaults(fn=cmd_new)

    tpl = sub.add_parser("template", help="write a blank decisions file")
    tpl.add_argument("--game", default="game")
    tpl.set_defaults(fn=cmd_template)

    rnd = sub.add_parser("round", help="process the next round")
    rnd.add_argument("--game", default="game")
    rnd.add_argument("--decisions")
    rnd.set_defaults(fn=cmd_round)

    pre = sub.add_parser("preview", help="Round 0 pro-forma")
    pre.add_argument("--game", default="game")
    pre.add_argument("--team", default="team_01")
    pre.set_defaults(fn=cmd_preview)

    return ap.parse_args().fn(ap.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
