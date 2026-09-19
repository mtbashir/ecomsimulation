#!/usr/bin/env python3
"""Round runner. `python run.py --help`"""
from __future__ import annotations

import argparse
import sys

sys.path.insert(0, "src")

from ecomsim import params as P  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="E-commerce simulation runner")
    ap.add_argument("--teams", type=int, default=8)
    ap.add_argument("--rounds", type=int, default=12)
    ap.add_argument("--preset", default="advanced",
                    choices=["foundation", "standard", "advanced", "expert"])
    ap.add_argument("--set", action="append", default=[], metavar="NAME=VALUE",
                    help="override a parameter, e.g. --set saturation_exponent=0.55")
    args = ap.parse_args()

    overrides = {"n_teams": args.teams, "rounds": args.rounds}
    for item in args.set:
        name, _, value = item.partition("=")
        overrides[name] = float(value)

    try:
        params = P.load(overrides)
    except P.BandViolation as exc:
        print(f"REJECTED: {exc}")
        return 1

    print(f"config_hash={params.config_hash()}  preset={args.preset}  "
          f"teams={args.teams}  rounds={args.rounds}")
    for warning in params.warnings:
        print(f"  WARNING: {warning}")
    if params.warnings:
        print("\n  This configuration is UNVALIDATED. Run the invariant suite "
              "before assigning it to a cohort (docs/11).")

    from ecomsim import bootstrap  # noqa: E402
    from ecomsim.engine import run_game  # noqa: E402

    world = bootstrap.new_world(params, run_id="cli")
    contexts = run_game(world, params, strategy=lambda w, r, t: {},
                        rounds=args.rounds, preset=args.preset)

    team = world.teams["team_01"]
    cols = ("rd", "revenue", "orders", "sessions", "CR", "GM%", "CM%",
            "CAC", "rpt%", "rating", "cash", "binding")
    print(f"\n{cols[0]:>3}{cols[1]:>13}{cols[2]:>8}{cols[3]:>10}{cols[4]:>7}"
          f"{cols[5]:>7}{cols[6]:>8}{cols[7]:>7}{cols[8]:>6}{cols[9]:>7}"
          f"{cols[10]:>13}  {cols[11]}")
    for h in team.history:
        print(f"{h['round']:>3}{h['revenue_net']:>13,.0f}{h['orders']:>8,.0f}"
              f"{h['sessions']:>10,.0f}{h['conversion_rate']*100:>6.2f}%"
              f"{h['gross_margin_pct']*100:>6.1f}%{h['contribution_margin_pct']*100:>7.1f}%"
              f"{h['cac_blended']:>7,.0f}{h['repeat_order_share']*100:>5.0f}%"
              f"{h['rating']:>7.2f}{h['cash_balance']:>13,.0f}  {h['binding_constraint']}")

    warnings = [w for c in contexts for w in c.get("warnings", [])]
    for warning in warnings[:5]:
        print(f"  ENGINE WARNING: {warning}")

    print("\nNOT CALIBRATED. Levels are burst 2 - see tests/test_baseline.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
