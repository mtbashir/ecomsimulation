"""M6 - Traffic generation.

saturation_exponent is the single most dangerous parameter in the model. Above
0.90 returns go near-linear and "spend everything on the cheapest channel"
dominates every other decision in the sim (docs/04).
"""
from __future__ import annotations

from .. import targeting

CHANNEL_DECISIONS = {
    "meta": "3.1",
    "google_search": "3.2",
    "tiktok": "3.4",
}


def _returning_sessions(team, params) -> float:
    """Direct traffic from customers who already bought.

    Sized so that, at the team's conversion rate, it produces the repeat demand
    its cohort ledger implies. Returning customers convert far better than cold
    traffic, so they need proportionally fewer sessions.
    """
    expected_repeat = sum(
        c.active * c.freq * params["cohort_freq_scale"] for c in team.cohorts
    )
    effective_cr = params["cr_base"] * params["repeat_cr_multiplier"]
    return expected_repeat / max(effective_cr, 1e-6)


def run(world, params, resolved, ctx) -> None:
    sigma = params["saturation_exponent"]
    lam = params["adstock_carryover"]
    phi = params["cpm_inflation_phi"]

    # Market-level spend by channel drives CPM inflation for everyone: the more
    # the field spends, the worse it gets for all of them.
    market_spend: dict[str, float] = {}
    for team in world.teams.values():
        for code, dec in CHANNEL_DECISIONS.items():
            market_spend[code] = market_spend.get(code, 0.0) + float(
                ctx["resolved"][team.team_id].get(dec, 0) or 0
            )
    world.market_spend = market_spend

    n_teams = max(1, len(world.teams))
    for team in world.teams.values():
        team_resolved = ctx["resolved"][team.team_id]
        paid = 0.0
        active_channels = 0

        # Campaign settings under each budget (decision 3.10). A channel with
        # none is absent from `scored` and runs at exactly 1.0, which is how a
        # team that never opens the campaign screen plays the engine as it was.
        campaigns = targeting.clean(team_resolved.get(targeting.DECISION) or [],
                                    team.active_skus or None)
        spend = {code: float(team_resolved.get(dec, 0) or 0)
                 for code, dec in CHANNEL_DECISIONS.items()}
        scored = targeting.channel_scores(campaigns, spend, params,
                                          team.active_skus, team.brand_equity)
        by_channel: dict[str, float] = {}
        inflation_by: dict[str, float] = {}

        for code, dec in CHANNEL_DECISIONS.items():
            ch = params.channel(code)
            spend = float(team_resolved.get(dec, 0) or 0)
            team.adstock[code] = spend + lam * team.adstock.get(code, 0.0)
            if spend > 0:
                active_channels += 1

            ref = float(ch["k_base"]) * 2_000 * n_teams
            inflation = 1 + phi * (market_spend.get(code, 0.0) / max(ref, 1) - 1)
            inflation = max(0.6, inflation)

            creative_lift = 1 + float(ch["creative_sensitivity"]) * (
                team.creative_quality - 0.5
            )
            k = (float(ch["k_base"]) * params["channel_k_scale"]
                 / inflation * creative_lift)
            if code in scored:
                k *= scored[code]["traffic"]
            got = k * (team.adstock[code] / 1_000) ** sigma
            by_channel[code] = got
            inflation_by[code] = inflation
            paid += got

        organic = (
            params["organic_base"]
            * (1 - params["organic_brand_coef"] + params["organic_brand_coef"] * team.brand_equity * 2)
            * (1 + params["organic_ux_coef"] * (team.ux_score - 0.5))
        )

        returning = _returning_sessions(team, params)
        sessions = paid + organic + returning
        ctx.setdefault("sessions_returning", {})[team.team_id] = returning
        if active_channels > 1:
            sessions *= 1 - params["channel_overlap"] * (1 - 1 / active_channels)

        sessions *= ctx.get("traffic_mult", {}).get(team.team_id, 1.0)
        sessions *= team.traffic_multiplier   # founding business model
        ctx.setdefault("sessions", {})[team.team_id] = sessions

        # What M8 needs to convert paid visitors at their own rate, and what
        # the report needs to show each campaign's numbers. Scaled so the
        # channel figures add up to the paid sessions actually delivered.
        pre = paid + organic + returning
        scale = sessions / pre if pre > 0 else 0.0
        ctx.setdefault("paid_sessions", {})[team.team_id] = {
            c: v * scale for c, v in by_channel.items()}
        ctx.setdefault("channel_inflation", {})[team.team_id] = inflation_by
        ctx.setdefault("targeting", {})[team.team_id] = scored
        cvr = 1.0
        if scored and paid > 0:
            cvr = sum(by_channel[c] * (scored[c]["cvr"] if c in scored else 1.0)
                      for c in by_channel) / paid
        ctx.setdefault("paid_cvr_mult", {})[team.team_id] = cvr
        ctx.setdefault("paid_share_cold", {})[team.team_id] = (
            paid / (paid + organic) if paid + organic > 0 else 0.0)
