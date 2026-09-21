"""M2 - Events.

Events modify PARAMETERS, never a team's P&L. An event that subtracts PKR 2M
from profit teaches nothing; one that doubles supplier lead time forces a team
to reason about safety stock, cash and forecast error - and the PKR 2M loss
emerges from their response, or does not (docs/09).
"""
from __future__ import annotations

from .. import rng

# Type A - scheduled, identical for all teams. {round: (code, {target: mult}, duration)}
SCHEDULED = {
    3:  ("EV-01", {"category_mult": 1.22, "cpm_mult": 1.18,
                   "courier_success_mult": 0.94, "sla_mult": 0.88}, 1),
    4:  ("EV-02", {"incumbent_price_mult": 0.85}, 4),
    # 2.0x for three rounds was set when a lead-time shock could not cross a
    # month boundary and so cost nothing. Now that it can, that severity was
    # the single most punishing thing in the game and pushed the suite past
    # its own event-neutrality bound. 1.6x for two rounds still slips an
    # importer a full month of arrivals, which is the point of it.
    5:  ("EV-03", {"lead_time_mult": 2.0}, 2),
    6:  ("EV-04", {"cpm_inflation_mult": 2.2}, 2),
    7:  ("EV-05", {"rto_mult": 1.5}, 3),
    8:  ("EV-07", {"new_entrant": 1.0}, 99),
    10: ("EV-09", {"import_cogs_mult": 1.16}, 99),
}

# Type C - stochastic. Bounded severity, symmetric in expectation, forewarnable.
STOCHASTIC = [
    ("EV-19", 0.15, 3, {"courier_success_mult": 0.88}, 1),
    ("EV-20", 0.10, 1, {"gateway_success_mult": 0.82}, 1),
    ("EV-22", 0.10, 4, {"channel_k_mult": 0.85}, 2),
]


def run(world, params, resolved, ctx) -> None:
    if not params["events_enabled"]:
        # Calibration and the T2 gate run without events - including EV-23
        # noise - so that levels can be held to tight tolerances.
        world.active_events = []
        ctx["events"] = {}
        ctx["event_codes"] = []
        return

    severity = params["event_severity"]
    active: list[dict] = [e for e in world.active_events if e["expires"] > world.round]

    if world.round in SCHEDULED:
        code, mods, duration = SCHEDULED[world.round]
        active.append(_make(code, mods, world.round, duration, severity))

    for code, prob, from_round, mods, duration in STOCHASTIC:
        if world.round < from_round:
            continue
        if rng.chance(prob, world.run_id, world.round, "market", f"event:{code}"):
            active.append(_make(code, mods, world.round, duration, severity))

    # EV-23 - irreducible demand noise, every round, unforecastable. It exists so
    # teams cannot attribute every variance to a decision.
    noise = 1 + rng.normal(world.run_id, world.round, "market", "demand_noise",
                           0.0, 0.035)
    world.category_size *= noise

    world.active_events = active
    effects = _combine(active)
    ctx["events"] = effects
    ctx["event_codes"] = [e["code"] for e in active]

    world.category_size *= effects.get("category_mult", 1.0)

    if effects.get("new_entrant") and not any(
        i["id"] == "inc_c_entrant" for i in world.incumbents
    ):
        # Strong on acquisition, weak on operations: takes share fast, then its
        # rating decays and it bleeds customers back into the market.
        world.incumbents.append(
            {"id": "inc_c_entrant", "name": "Funded entrant", "utility": 0.58}
        )


def _make(code, mods, round_, duration, severity) -> dict:
    scaled = {
        k: (1 + (v - 1) * severity) if k.endswith("_mult") else v
        for k, v in mods.items()
    }
    return {"code": code, "mods": scaled, "started": round_,
            "expires": round_ + duration}


def _combine(active: list[dict]) -> dict:
    out: dict[str, float] = {}
    for event in active:
        for key, value in event["mods"].items():
            out[key] = out.get(key, 1.0) * value if key.endswith("_mult") else value
    return out
