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

        reports: dict[str, dict] = {}

        # Studies bought earlier that land now. They carry the numbers as they
        # stood when the study was commissioned, which is the whole point of a
        # lagged study: the answer is real, and it is a month out of date.
        still_waiting = []
        for q in team.queued_reports:
            if q["deliver"] <= world.round:
                reports[q["code"]] = dict(q["report"], status="lagged")
            else:
                still_waiting.append(q)
        team.queued_reports = still_waiting

        for code in purchased:
            if not _exists(params, code):
                continue
            study = params.study(code)
            report = _generate(world, params, ctx, tid, study)
            lag = int(study["lag_rounds"])
            if lag > 0:
                team.queued_reports.append(
                    {"code": code, "deliver": world.round + lag, "report": report})
                continue
            reports[code] = report

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


def _forward_view(world, params, tid: str, code: str):  # noqa: C901
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

    if code == "MR-06":
        # The hidden weights themselves. Nothing else reveals what a segment
        # actually trades off, which is why it is the dearest customer study.
        return {"segments": [
            {"code": seg["code"], "name": seg["name"],
             "share": float(seg["share"]),
             "repeat_propensity": float(seg["repeat_propensity"]),
             "weights": {k[2:]: float(seg[k]) for k in seg
                         if k.startswith("w_")}}
            for seg in params.segments]}

    if code == "MR-19":
        return {"bundles": ["MR-02", "MR-03", "MR-04"]}

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

    team = world.teams[tid]
    if code == "MR-04":
        # What rivals are spending, estimated from the outside. The study's own
        # bias of 0.90 is what makes this deliberately understated.
        rivals = [sum(float(ctx["resolved"][o].get(k, 0) or 0)
                      for k in ("3.1", "3.2", "3.4", "3.9"))
                  for o in ctx["resolved"] if o != tid]
        return sum(rivals) / len(rivals) if rivals else None
    if code == "MR-08":
        return team.brand_equity
    if code == "MR-09":
        return ctx["nps"][tid]
    if code == "MR-12":
        # The flagship lesson: what the marketing actually contributed, against
        # the over-attributed number the platforms hand out for free.
        marketing = ctx["pnl"][tid]["marketing"]
        return ctx["net_revenue"][tid] / marketing if marketing > 0 else None
    if code == "MR-13":
        d = ctx["resolved"][tid]
        if not d.get("4.1") or str(d.get("4.1")) == "off":
            return None          # nothing to rank if you are not listed
        return ctx["net_revenue"][tid] / max(sum(ctx["net_revenue"].values()), 1.0)
    if code == "MR-14":
        return team.creative_quality
    if code == "MR-18":
        return ctx["assortment_fit_mean"][tid]
    if code == "MR-20":
        # Readiness is delivery speed and stock depth, which is what quick
        # commerce actually demands of you.
        return 0.5 * ctx["sla_attainment"][tid] + 0.5 * ctx["instock_ratio"][tid]
    return None
