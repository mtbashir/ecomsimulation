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

    print("\nEngine pipeline is incomplete - see tests/test_baseline.py for the "
          "Phase 2 gate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
