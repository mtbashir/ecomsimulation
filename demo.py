#!/usr/bin/env python3
"""Play a full 12-round game with six named teams on distinct strategies.

    python demo.py [--out demo/]

Exists so the simulation can be SEEN before anyone commits to running a cohort.
Every team here is a scripted caricature; real teams are messier and better.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, "src")

from ecomsim import bootstrap, console, params as P, report, scoring  # noqa: E402
from ecomsim.engine import run_round  # noqa: E402
from ecomsim.io_csv import write_results  # noqa: E402

BASE = {"3.1": 468_000, "3.2": 234_000, "3.4": 168_000, "3.8": 200_000, "3.9": 267_000}


def scale(m: float) -> dict:
    return {k: v * m for k, v in BASE.items()}


TEAMS = {
    "team_01": ("Meher & Co", "Balanced operator", lambda r: scale(1.15) | {
        "6.1": 180_000, "7.5": 3, "9.2": 0.03, "10.1": 5, "7.4": 120_000,
        "12.1": ["MR-01", "MR-17", "MR-07"] if r % 2 else ["MR-10", "MR-11"],
        **({"11.1": True} if r >= 3 else {})}),
    "team_02": ("Bazaar Deals", "Discount-led", lambda r: scale(1.30) | {
        "2.2": 0.32, "7.5": 2}),
    "team_03": ("Noor Skincare", "Premium, brand-led", lambda r: scale(1.05) | {
        "1.5": "premium", "8.5": "premium", "3.9": BASE["3.9"] * 2.0,
        "3.8": BASE["3.8"] * 1.5, "7.4": 220_000, "10.1": 6, "7.5": 4}),
    "team_04": ("Rahat Retail", "Retention-led", lambda r: scale(0.92) | {
        "6.1": 420_000, "10.1": 6, "10.4": "free", "7.4": 150_000, "7.5": 3,
        "12.1": ["MR-10", "MR-09"]}),
    "team_05": ("Lahore Living", "Growth at all costs", lambda r: scale(2.4) | {
        "3.9": 0, "7.5": 1.5}),
    "team_06": ("Sahil Essentials", "Cash-careful", lambda r: scale(0.55) | {
        "3.9": 0, "6.1": 60_000, "10.1": 3, "7.5": 2}),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="demo")
    ap.add_argument("--rounds", type=int, default=12)
    args = ap.parse_args()

    out = Path(args.out)
    params = P.load({"n_teams": len(TEAMS)})
    world = bootstrap.new_world(params, run_id="demo")

    for tid, (brand, _pitch, _fn) in TEAMS.items():
        world.teams[tid].brand_name = brand

    print(f"Six teams, {args.rounds} rounds, events on. "
          f"Config {params.config_hash()}.\n")
    for _ in range(args.rounds):
        run_round(world, params,
                  {tid: fn(world.round + 1) for tid, (_b, _p, fn) in TEAMS.items()})
        write_results(out / "results.csv", world)
        for team in world.teams.values():
            card = scoring.final_score(team, params, world.teams) if world.round >= 2 else None
            report.render(team, world.round, out / f"round_{world.round}", card)
        console.render(world, params, out / f"round_{world.round}")

    cards = {t.team_id: scoring.final_score(t, params, world.teams)
             for t in world.teams.values()}
    ranked = sorted(world.teams.values(), key=lambda t: -cards[t.team_id]["total"])

    print(f"{'#':<3}{'brand':<20}{'strategy':<24}{'score':>7}{'revenue':>12}"
          f"{'CM':>8}{'repeat':>8}{'cash':>12}")
    for i, team in enumerate(ranked, 1):
        h = team.history[-1]
        brand, pitch, _ = TEAMS[team.team_id]
        print(f"{i:<3}{brand:<20}{pitch:<24}{cards[team.team_id]['total']:>7.1f}"
              f"{h['revenue_net']:>12,.0f}{h['contribution_margin_pct']:>7.1%}"
              f"{h['repeat_order_share']:>8.0%}{h['cash_balance']:>12,.0f}")

    print(f"\nWritten to {out}/ - open {out}/round_{args.rounds}/console_r"
          f"{args.rounds}.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
