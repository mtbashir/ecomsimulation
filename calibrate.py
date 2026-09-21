#!/usr/bin/env python3
"""Burst 2 calibration harness.

Solves parameters numerically against the Round 0 baseline rather than by hand.
Reusable: rerun it whenever a benchmark replaces a reasoned figure.
"""
from __future__ import annotations

import sys

sys.path.insert(0, "src")

from ecomsim import bootstrap, params as P  # noqa: E402
from ecomsim.engine import run_game  # noqa: E402

# revenue_gross is orders x AOV. revenue_net is after returns, RTO and failed
# delivery, which in a 62%-COD market is a materially different number - and
# noticing that gap is itself part of what the sim teaches.
TARGETS = {
    "revenue_gross": 12_000_000, "orders": 4_000, "aov_net": 3_000,
    "sessions": 190_000, "conversion_rate": 0.021, "gross_margin_pct": 0.38,
    "contribution_margin_pct": 0.09, "repeat_order_share": 0.35, "rating": 4.1,
}


def measure(overrides=None, rounds=12, team="team_01"):
    p = P.load({"events_enabled": 0} | (overrides or {}))
    w = bootstrap.new_world(p, run_id="calib")
    run_game(w, p, strategy=lambda wo, r, t: {}, rounds=rounds)
    hist = w.teams[team].history
    settled = hist[max(0, len(hist) - 6):]
    for h in settled:
        h.setdefault("revenue_gross", h["orders"] * h["aov_net"])
    return {k: sum(h[k] for h in settled) / len(settled) for k in TARGETS} | {
        "revenue_net": sum(h["revenue_net"] for h in settled) / len(settled),
        "cac_blended": sum(h["cac_blended"] for h in settled) / len(settled),
        "active_customers": settled[-1]["active_customers"],
        "drift": max(abs(hist[-1][k] - hist[len(hist) // 2][k]) / max(abs(hist[-1][k]), 1e-9)
                     for k in ("revenue_net", "orders")),
    }


def report(result, label=""):
    print(f"\n{label}")
    print(f"{'metric':<26}{'engine':>14}{'target':>14}{'gap':>9}")
    for key, target in TARGETS.items():
        got = result[key]
        gap = (got - target) / target
        flag = "ok" if abs(gap) <= 0.02 else ""
        print(f"{key:<26}{got:>14,.4g}{target:>14,.4g}{gap:>8.0%}  {flag}")
    print(f"{'revenue_net':<26}{result['revenue_net']:>14,.4g}{'(derived)':>14}")
    print(f"{'cac_blended':<26}{result['cac_blended']:>14,.0f}"
          f"{'(derived)':>14}")
    print(f"{'active_customers':<26}{result['active_customers']:>14,.0f}"
          f"{'(derived)':>14}")


if __name__ == "__main__":
    report(measure(), "BASELINE, current defaults")


def solve(knob: str, metric: str, target: float, lo: float, hi: float,
          base: dict, tol: float = 0.004, iters: int = 26) -> float:
    """Bisect one parameter against one metric. Monotone knobs only."""
    for _ in range(iters):
        mid = (lo + hi) / 2
        got = measure(base | {knob: mid})[metric]
        if abs(got - target) / target < tol:
            return mid
        if got < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def autocalibrate(passes: int = 4) -> dict:
    """Knobs interact, so sweep them repeatedly until they stop moving."""
    found: dict[str, float] = {}
    for _ in range(passes):
        found["channel_k_scale"] = solve(
            "channel_k_scale", "sessions", TARGETS["sessions"], 0.2, 3.0, found)
        found["cr_base"] = solve(
            "cr_base", "conversion_rate", TARGETS["conversion_rate"], 0.004, 0.06, found)
        found["cogs_scale"] = solve(
            "cogs_scale", "gross_margin_pct", TARGETS["gross_margin_pct"],
            1.25, 0.70, found)
        found["rating_base"] = solve(
            "rating_base", "rating", TARGETS["rating"], 1.0, 3.5, found)
        found["cohort_freq_scale"] = solve(
            "cohort_freq_scale", "repeat_order_share",
            TARGETS["repeat_order_share"], 0.3, 2.5, found)
    return found
