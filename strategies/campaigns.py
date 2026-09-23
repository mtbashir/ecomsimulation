"""Scripted campaign setups for measuring what decision 3.10 is worth.

`sharp` reads the audience table the way a student who understood the course
would: products grouped by who buys them, each group aimed at its buyers, and
products kept off channels their buyers do not use. `careless` makes the
mistakes a class actually makes - one campaign for everything, aimed at the
young big-city audience the team pictures, with the objective left on traffic
and search spent on the store's own name.

Neither is used by the twenty archetypes: the invariant suite plays with no
campaigns at all, which is what keeps it identical to the engine before 3.10.
validate.targeting_pairs puts them side by side on the same strategy.
"""
from __future__ import annotations


def _weight(params, sku: str) -> float:
    return float(params.sku(sku)["revenue_weight"])


def _aim(params, skus: list[str]) -> dict:
    auds = [params.audience(s) for s in skus]
    w = [_weight(params, s) for s in skus]
    tw = sum(w)
    lead = auds[w.index(max(w))]
    female = sum(x * float(a["female_share"]) for x, a in zip(w, auds)) / tw
    ages = {a["core_age"] for a in auds} | ({lead["second_age"]} if lead.get("second_age") else set())
    geo = {t for a in auds for t in str(a["geo"]).split("|")}
    interests = [lead["interest_1"]] + [a["interest_1"] for a in auds if a["interest_1"] != lead["interest_1"]]
    return {"skus": skus, "ages": sorted(ages), "geo": sorted(geo),
            "gender": "female" if female > 0.65 else "male" if female < 0.35 else "all",
            "interests": interests[:2], "language": lead["language"],
            "format": lead["format"], "objective": "conversions"}


def _uses(params, sku: str, channel: str) -> bool:
    a = params.audience(sku)
    return channel in (a.get("channel_1"), a.get("channel_2"), a.get("channel_3"))


def sharp(params, sold: list[str]) -> list[dict]:
    sold = [s for s in sold if params.audience(s)]
    out = []
    meta = [s for s in sold if _uses(params, s, "meta")]
    groups: dict[tuple, list[str]] = {}
    for s in meta:
        a = params.audience(s)
        key = (a["core_age"], str(a["geo"]).split("|")[0], float(a["female_share"]) > 0.65)
        groups.setdefault(key, []).append(s)
    ranked = sorted(groups.values(), key=lambda g: -sum(_weight(params, s) for s in g))
    if len(ranked) > 3:
        ranked = ranked[:2] + [[s for g in ranked[2:] for s in g]]
    for i, g in enumerate(ranked):
        c = {"channel": "meta", "name": f"Meta {i + 1}",
             "share": sum(_weight(params, s) for s in g)}
        c |= _aim(params, g) if i < 2 or len(ranked) < 3 else {
            "skus": g, "objective": "conversions"}
        out.append(c)
    tiktok = [s for s in sold if _uses(params, s, "tiktok")]
    if tiktok:
        out.append({"channel": "tiktok", "name": "TikTok", "share": 1.0} | _aim(params, tiktok))
    search = [s for s in sold if _uses(params, s, "google_search")]
    if search:
        kinds = [params.audience(s)["purchase"] for s in search]
        exact = sum(k in ("replenishment", "considered") for k in kinds) > len(kinds) / 2
        out.append({"channel": "google_search", "name": "Search", "share": 1.0,
                    "skus": search, "keywords": "generic",
                    "match": "exact" if exact else "broad"})
    return out


def careless(params, sold: list[str]) -> list[dict]:
    young = {"ages": ["18-24"], "geo": ["T1"], "interests": ["fashion"],
             "language": "english", "format": "reels", "objective": "traffic"}
    return [{"channel": "meta", "name": "Everything", "share": 1.0} | young,
            {"channel": "tiktok", "name": "Everything", "share": 1.0} | young,
            {"channel": "google_search", "name": "Our name", "share": 1.0,
             "keywords": "brand", "match": "exact"}]
