#!/usr/bin/env python3
"""T3 - the invariant suite (docs/11-validation-harness.md).

20 archetypes x 10 variations = 200 strategy instances. Each game seats 8
instances drawn deterministically, so every archetype is scored against a
varied field. Twelve invariants; each failure names what to check first.

    python validate.py            # full run
    python validate.py --games 60 # quick
"""
from __future__ import annotations

import argparse
import hashlib
import statistics as st
import sys
import time

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from ecomsim import bootstrap, params as P, scoring  # noqa: E402
from ecomsim.engine import run_game  # noqa: E402
from strategies.archetypes import ARCHETYPES, MUST_FAIL  # noqa: E402

VARIATIONS = 10


def instances():
    return [(name, v / (VARIATIONS - 1)) for name in ARCHETYPES for v in range(VARIATIONS)]


def seat(game: int, pool: list, n: int = 8) -> list:
    """Deterministic draw of n instances for a game, no repeats within a game."""
    order = sorted(pool, key=lambda inst: hashlib.sha256(
        f"{game}|{inst[0]}|{inst[1]:.3f}".encode()).hexdigest())
    return order[:n]


def play(game: int, pool: list, overrides: dict, rounds: int) -> list[dict]:
    p = P.load(overrides)
    world = bootstrap.new_world(p, run_id=f"t3-{game}")
    seated = seat(game, pool)
    amap = {tid: inst for tid, inst in zip(world.teams, seated)}

    def strategy(w, r, tid):
        name, v = amap[tid]
        return ARCHETYPES[name](w, r, tid, v)

    run_game(world, p, strategy=strategy, rounds=rounds)
    out = []
    for tid, (name, v) in amap.items():
        team = world.teams[tid]
        sc = scoring.final_score(team, p, world.teams)
        r8 = team.history[7] if len(team.history) > 7 else team.history[-1]
        out.append({
            "game": game, "archetype": name, "v": v, "score": sc["total"],
            "insolvent": sc["insolvent"], "first_insolvent": sc["first_insolvent_round"],
            "rank": None, "credit_drawn": team.credit_drawn > 0,
            "cm": team.history[-1]["contribution_margin_pct"],
            "r8_score_proxy": r8["contribution_margin_pct"] + 0.5 * r8["repeat_order_share"],
            "research_spend": sum(h["pnl"].get("research", 0) for h in team.history),
        })
    ranked = sorted(out, key=lambda x: -x["score"])
    for i, row in enumerate(ranked):
        row["rank"] = i + 1
    return out


def research_pairs(games: int, overrides: dict | None = None,
                   rounds: int = 12) -> dict[str, float]:
    """I7 measured as a PAIRED comparison, in the same games.

    The main draw seats eight instances out of two hundred by hash, so
    research_zero and research_selective meet different fields, at different
    variations, in different games. Each archetype mean then carries a standard
    error around 0.6 points - three times the effect I7 is looking for, which
    made the invariant a coin toss rather than a measurement. Here the three
    research archetypes sit in the same game at the same variation, against the
    same five opponents, so the only thing that differs between them is what
    they bought and what they did with it.
    """
    pool = instances()
    others = [inst for inst in pool if not inst[0].startswith("research_")]
    scores: dict[str, list[float]] = {a: [] for a in
                                      ("research_zero", "research_selective",
                                       "research_heavy")}
    for game in range(games):
        p = P.load(overrides or {})
        world = bootstrap.new_world(p, run_id=f"t3-paired-{game}")
        v = (game % VARIATIONS) / (VARIATIONS - 1)
        tids = list(world.teams)
        amap = {tid: (name, v) for tid, name in zip(tids, scores)}
        for tid, inst in zip(tids[len(scores):], seat(game, others, len(tids) - len(scores))):
            amap[tid] = inst

        def strategy(w, r, tid):
            name, var = amap[tid]
            return ARCHETYPES[name](w, r, tid, var)

        run_game(world, p, strategy=strategy, rounds=rounds)
        for tid, (name, _) in amap.items():
            if name in scores:
                scores[name].append(
                    scoring.final_score(world.teams[tid], p, world.teams)["total"])
    return {name: st.mean(xs) for name, xs in scores.items()}


def run(games: int, overrides: dict | None = None, rounds: int = 12):
    pool = instances()
    rows = []
    for g in range(games):
        rows.extend(play(g, pool, overrides or {}, rounds))
    return rows


# --- Invariants ----------------------------------------------------------------

def by_arch(rows):
    d = {}
    for r in rows:
        d.setdefault(r["archetype"], []).append(r)
    return d


def invariants(rows, rows_no_events=None, paired=None) -> list[tuple[str, bool, str, str]]:
    A = by_arch(rows)
    mean = {a: st.mean(x["score"] for x in xs) for a, xs in A.items()}
    med = st.median(mean.values())
    best = max(mean, key=mean.get)
    wins = {}
    for r in rows:
        if r["rank"] == 1:
            wins[r["archetype"]] = wins.get(r["archetype"], 0) + 1
    games = max(r["game"] for r in rows) + 1
    top_win_share = max(wins.values()) / games if wins else 0

    out = []

    out.append(("I1  No dominant strategy",
                mean[best] < 2.5 * med and top_win_share <= 0.40,
                f"best={best} {mean[best]:.1f} vs median {med:.1f} ({mean[best]/med:.2f}x); "
                f"top win share {top_win_share:.0%}",
                "saturation_exponent, then share_sensitivity, then cpm_inflation_phi"))

    # Deliberately suicidal archetypes are allowed to die early; a death spiral
    # means a strategy meant to be viable is unrecoverable before mid-game.
    early = [r for r in rows if r["first_insolvent"] and r["first_insolvent"] < 6
             and r["archetype"] not in MUST_FAIL]
    insolvent_scores = [r["score"] for r in rows
                        if r["insolvent"] and r["archetype"] not in MUST_FAIL]
    out.append(("I2  No death spiral",
                not early and (not insolvent_scores or min(insolvent_scores) >= 25),
                f"{len(early)} insolvent before R6; "
                f"min insolvent score {min(insolvent_scores):.1f}" if insolvent_scores else
                f"{len(early)} insolvent before R6; none insolvent",
                "starting_cash, then MOQ x lead time, then credit_ceiling"))

    pair = [(g, ) for g in range(games)]
    disc_below = 0; both = 0
    for g in range(games):
        gr = {r["archetype"]: r for r in rows if r["game"] == g}
        if "discounter" in gr and "balanced" in gr:
            both += 1
            if gr["discounter"]["score"] < gr["balanced"]["score"]:
                disc_below += 1
    frac = disc_below / both if both else 0
    out.append(("I3  Discounting is a trap", frac >= 0.90 and both > 0,
                f"discounter below balanced in {frac:.0%} of {both} shared games; "
                f"means disc={mean.get('discounter',0):.1f} bal={mean.get('balanced',0):.1f}",
                "deal-cohort churn 0.44, then P3 weight, then price_elasticity"))

    base_cm = st.mean(x["cm"] for x in A.get("baseline", [])) if "baseline" in A else 0
    out.append(("I4  Margin viable", 0.05 <= base_cm <= 0.15,
                f"baseline CM {base_cm:.1%}", "gross_margin_base, fulfilment cost, courier defaults"))

    drew = st.mean(1.0 if r["credit_drawn"] else 0.0 for r in rows)
    viable = [r for r in rows if r["archetype"] not in MUST_FAIL]
    insol = st.mean(1.0 if r["insolvent"] else 0.0 for r in viable)
    out.append(("I5  Cash binding but survivable", drew >= 0.20 and insol < 0.10,
                f"{drew:.0%} drew credit, {insol:.0%} of viable strategies insolvent",
                "cash timing (M15), cod_remit_days, supplier terms"))

    out.append(("I6  Share conserves", True, "checked in tests/test_pipeline.py", "M7 redistribution"))

    if paired is not None:
        rs = paired["research_selective"]
        rz, rh = paired["research_zero"], paired["research_heavy"]
        out.append(("I7  Research pays", rs > rz and rs > rh,
                    f"paired: selective {rs:.2f} vs zero {rz:.2f} "
                    f"(+{rs - rz:.2f}) vs heavy {rh:.2f}",
                    "study prices, then error bands, then signal strength of MR-01/17/07"))

    out.append(("I8  Determinism", True, "checked in tests/test_determinism.py", "-"))
    out.append(("I9  Monotonicity", True, "checked in tests/test_monotonicity.py", "-"))
    out.append(("I10 No free lunch", True, "checked in tests/test_monotonicity.py", "-"))

    # Sandbagging and harvesting are tested against playing it straight, not
    # against a rank. Ranks 9 to 15 of this field sit inside 1.7 points while
    # an archetype mean carries a standard error near 0.6, so "bottom 40%" was
    # reading noise: the same engine put harvester at #10 and at #15 depending
    # on how many games were run. What the defences in docs/08 actually claim
    # is that neither trick beats playing straight, and the margin says whether
    # they work. Before the M5 and scoring fixes harvester came in 1.3 points
    # under balanced; a threshold of 5 separates working from not.
    spread = max(mean.values()) - min(mean.values())
    straight = mean.get("balanced", 0)
    sb = straight - mean.get("sandbagger", 0)
    hv = straight - mean.get("harvester", 0)
    out.append(("I11 Scorecard discrimination",
                35 <= spread <= 75 and sb >= 5.0 and hv >= 5.0,
                f"spread {spread:.0f}; sandbagger {sb:+.1f} and harvester "
                f"{hv:+.1f} against balanced (need 5 or more behind)",
                "anchor scales (docs/08), round weights, pillar weights"))

    if rows_no_events is not None:
        B = by_arch(rows_no_events)
        mean_off = {a: st.mean(x["score"] for x in xs) for a, xs in B.items()}
        common = sorted(set(mean) & set(mean_off))
        delta = abs(st.mean(mean[a] for a in common) - st.mean(mean_off[a] for a in common))
        rho = _spearman([mean[a] for a in common], [mean_off[a] for a in common])
        out.append(("I12 Event neutrality", delta < 8 and rho > 0.6,
                    f"mean delta {delta:.1f} pts, rank rho {rho:.2f}",
                    "event_severity, Type C probabilities, Type B thresholds"))
    return out


def _spearman(a, b):
    ra = {v: i for i, v in enumerate(sorted(a))}
    rb = {v: i for i, v in enumerate(sorted(b))}
    n = len(a)
    d2 = sum((ra[x] - rb[y]) ** 2 for x, y in zip(a, b))
    return 1 - 6 * d2 / (n * (n * n - 1)) if n > 2 else 1.0


def report(rows, rows_off, params, elapsed, paired=None):
    A = by_arch(rows)
    mean = {a: st.mean(x["score"] for x in xs) for a, xs in A.items()}
    order = sorted(mean, key=lambda a: -mean[a])
    games = max(r["game"] for r in rows) + 1

    print(f"\nVALIDATION RUN  config_hash={params.config_hash()}  "
          f"{games} games x 8 seats = {games*8} team-runs  {elapsed:.0f}s\n")
    results = invariants(rows, rows_off, paired)
    for name, ok, detail, check in results:
        print(f" {name:<32} {'PASS' if ok else 'FAIL'}  {detail}")
    fails = [r for r in results if not r[1]]
    for name, _, _, check in fails:
        print(f"\n>> {name.strip()} FAILED. Check first: {check}")

    print("\nARCHETYPE MEANS")
    for i, a in enumerate(order):
        flag = " (must fail)" if a in MUST_FAIL else ""
        ins = st.mean(1.0 if x["insolvent"] else 0.0 for x in A[a])
        print(f" {i+1:>2}. {a:<20} {mean[a]:5.1f}   insolvent {ins:3.0%}{flag}")
    return not fails


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=200)
    ap.add_argument("--set", action="append", default=[])
    args = ap.parse_args()
    overrides = {}
    for item in args.set:
        k, _, v = item.partition("="); overrides[k] = float(v)
    t0 = time.perf_counter()
    rows = run(args.games, overrides)
    rows_off = run(max(20, args.games // 4), overrides | {"events_enabled": 0})
    paired = research_pairs(max(150, args.games // 2), overrides)
    ok = report(rows, rows_off, P.load(overrides), time.perf_counter() - t0, paired)
    sys.exit(0 if ok else 1)
