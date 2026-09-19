"""M16 - Research report generation.

    reported = true * bias * (1 + N(0, error_band/2))

seeded on (run_id, round, team, study_code). The seed must NOT include a
purchase counter: re-buying a study in the same round returns the identical
number, or teams re-buy to average out the noise and the uncertainty lesson
evaporates (docs/02, implementation rule 1).

Bias is separate from noise and never corrects on re-purchase, because bias is
a property of the SOURCE. Platform-reported ROAS is the worked example every
team meets for free.
"""
from __future__ import annotations

from .. import rng

PLATFORM_ROAS_BIAS = 1.32  # over-attributed by 25-40%


def run(world, params, resolved, ctx) -> None:
    for team in world.teams.values():
        tid = team.team_id
        d = ctx["resolved"][tid]

        purchased = d.get("12.1") or []
        cost = sum(float(params.study(c)["price"]) for c in purchased
                   if _exists(params, c))
        ctx.setdefault("research_cost", {})[tid] = cost

        reports: dict[str, dict] = {}
        for code in purchased:
            if not _exists(params, code):
                continue
            study = params.study(code)
            if int(study["lag_rounds"]) > 0:
                ctx.setdefault("queued_reports", {}).setdefault(tid, []).append(
                    {"code": code, "as_of": world.round,
                     "deliver": world.round + int(study["lag_rounds"])}
                )
                continue
            reports[code] = _generate(world, params, ctx, tid, study)

        # Lag-1 studies bought earlier land now, stamped with their as-of round.
        due = [q for q in ctx.get("queued_reports", {}).get(tid, [])
               if q["deliver"] <= world.round]
        for q in getattr(team, "_queued", []):
            if q["deliver"] <= world.round:
                reports[q["code"]] = {"as_of_round": q["as_of"], "status": "lagged"}
        team._queued = [q for q in getattr(team, "_queued", []) if q["deliver"] > world.round]
        team._queued += due

        ctx.setdefault("reports", {})[tid] = reports
        team.reports[world.round] = reports

        # Free but biased - the most instructive line in the sim.
        marketing = ctx["pnl"][tid]["marketing"]
        true_roas = ctx["net_revenue"][tid] / marketing if marketing > 0 else 0.0
        ctx.setdefault("roas_true", {})[tid] = true_roas
        ctx.setdefault("roas_reported", {})[tid] = true_roas * PLATFORM_ROAS_BIAS


def _exists(params, code: str) -> bool:
    return any(s["code"] == code for s in params.studies)


def _generate(world, params, ctx, tid: str, study: dict) -> dict:
    code = str(study["code"])
    forward = _forward_view(world, params, tid, code)
    if forward is not None:
        return forward | {"as_of_round": world.round, "status": "ok"}

    true_value = _true_value(world, params, ctx, tid, code)
    if true_value is None:
        return {"status": "no_data"}

    biased = true_value * float(study["bias"])
    band = float(study["error_band"])
    epsilon = rng.normal(world.run_id, world.round, tid, "study",
                         0.0, band / 2, study["code"]) if band > 0 else 0.0
    return {
        "as_of_round": world.round,
        "reported": biased * (1 + epsilon),
        "error_band": band,
        "status": "ok",
    }


def _forward_view(world, params, tid: str, code: str):
    """Studies whose value is what they say about the NEXT rounds.

    This is what makes research worth buying: MR-01 shows the seasonal peaks,
    MR-17 shows the lead-time shock coming, MR-05 names the events it catches.
    Forewarning is probabilistic and seeded, so it cannot be re-rolled.
    """
    from .m01_market import SEASON
    from .m02_events import SCHEDULED

    if code == "MR-01":
        idx = {}
        for ahead in (1, 2, 3):
            r = world.round + ahead
            raw = SEASON[(r - 1) % len(SEASON)]
            eps = rng.normal(world.run_id, world.round, tid, "study", 0.0, 0.04, code, r)
            idx[r] = round(raw * (1 + eps), 3)
        return {"seasonal_index": idx}

    if code == "MR-17":
        view = {}
        for ahead in (1, 2):
            r = world.round + ahead
            ev = SCHEDULED.get(r)
            shock = bool(ev and "lead_time_mult" in ev[1])
            seen = rng.chance(0.70, world.run_id, world.round, tid, "study", code, r)
            view[r] = {"lead_time_mult": ev[1]["lead_time_mult"] if (shock and seen) else 1.0}
        return {"lead_time_forecast": view}

    if code == "MR-05":
        r = world.round + 1
        ev = SCHEDULED.get(r)
        if ev and rng.chance(0.60, world.run_id, world.round, tid, "study", code, r):
            return {"warning": {"round": r, "event": ev[0]}}
        return {"warning": None}

    return None


def _true_value(world, params, ctx, tid: str, code: str):
    """What each study measures. Studies with no scalar answer return None."""
    if code == "MR-01":
        return world.category_size
    if code == "MR-02":
        return world.market_avg_price
    if code == "MR-03":
        total = sum(ctx["net_revenue"].values()) or 1.0
        return ctx["net_revenue"][tid] / total
    if code == "MR-07":
        return ctx["perception_gap"].get(tid, 0.0)
    if code == "MR-10":
        team = world.teams[tid]
        active = sum(c.active for c in team.cohorts) or 1.0
        return sum(c.churn_base * c.active for c in team.cohorts) / active
    if code == "MR-11":
        cacs = [v for v in ctx["cac_blended"].values() if v > 0]
        return sum(cacs) / len(cacs) if cacs else None
    if code == "MR-15":
        return ctx["courier_success"][tid]
    if code == "MR-16":
        return ctx["return_rate"][tid]
    return None
