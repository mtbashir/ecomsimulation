"""M6 - Traffic generation.

saturation_exponent is the single most dangerous parameter in the model. Above
0.90 returns go near-linear and "spend everything on the cheapest channel"
dominates every other decision in the sim (docs/04).
"""
from __future__ import annotations

CHANNEL_DECISIONS = {
    "meta": "3.1",
    "google_search": "3.2",
    "tiktok": "3.4",
}


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
            paid += k * (team.adstock[code] / 1_000) ** sigma

        organic = (
            params["organic_base"]
            * (1 - params["organic_brand_coef"] + params["organic_brand_coef"] * team.brand_equity * 2)
            * (1 + params["organic_ux_coef"] * (team.ux_score - 0.5))
        )

        sessions = paid + organic
        if active_channels > 1:
            sessions *= 1 - params["channel_overlap"] * (1 - 1 / active_channels)

        sessions *= ctx.get("traffic_mult", {}).get(team.team_id, 1.0)
        ctx.setdefault("sessions", {})[team.team_id] = sessions
