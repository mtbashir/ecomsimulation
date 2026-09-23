"""Campaign settings under each paid-social and search budget.

The budget a team puts on Meta, TikTok or Google is still the decision the
engine reads. This module only answers one question about how that money was
set up: how many of the people it reached were the people who buy the products
it promoted? The answer is a quality score per channel, and M6 and M8 turn it
into a multiplier on the sessions a rupee buys and on how well those visitors
convert.

Two rules keep it honest:

1. A team that never opens the campaign screen is scored exactly 1.0 - the
   engine runs as it always has. A broad campaign (everyone, everywhere, all
   products) also scores 1.0: targeting is judged against doing nothing clever,
   not against an ideal nobody could guess.
2. The truth it scores against is fixed for the whole run (params/audiences.csv
   and params/platforms.csv), and every point it gives or takes can be named in
   a sentence, which is what the report's findings are built from.
"""
from __future__ import annotations

import math

DECISION = "3.10"
CHANNELS = {"meta": "3.1", "tiktok": "3.4", "google_search": "3.2"}
CHANNEL_NAMES = {"meta": "Meta", "tiktok": "TikTok", "google_search": "Google Search"}
SOCIAL = ("meta", "tiktok")
MAX_PER_CHANNEL = 3
MAX_INTERESTS = 3

AGES = {"18-24": "age_18_24", "25-34": "age_25_34", "35-44": "age_35_44",
        "45+": "age_45p"}
TIERS = {"T1": "geo_t1", "T2": "geo_t2", "Rest": "geo_rest"}
TIER_NAMES = {"T1": "Karachi, Lahore and Islamabad",
              "T2": "Tier 2 cities", "Rest": "the rest of Pakistan"}
GENDERS = {"all": "Everyone", "female": "Women", "male": "Men"}
INTERESTS = {
    "beauty": "Beauty & skincare", "fashion": "Fashion",
    "grooming": "Grooming", "parenting": "Parenting",
    "home": "Home & cooking", "fitness": "Health & fitness",
    "deals": "Deals & shopping", "sports": "Cricket & sports",
    "entertainment": "Entertainment & gaming",
}
OBJECTIVES = {
    "traffic": "Traffic",
    "conversions": "Conversions",
    "awareness": "Awareness",
    "retargeting": "Retargeting recent visitors",
}
LANGUAGES = {"": "Mixed", "urdu": "Urdu", "english": "English",
             "roman_urdu": "Roman Urdu"}
FORMATS = {"": "Mixed", "feed": "Feed posts", "reels": "Reels & stories",
           "carousel": "Carousel"}
KEYWORDS = {
    "generic": "Generic - product terms",
    "brand": "Your store's name",
    "competitor": "Rival stores' names",
}
MATCHES = {"broad": "Broad match", "exact": "Exact match"}

# How well a product sells on a channel, by its rank in the audience table.
CHANNEL_FIT = (1.10, 1.00, 0.90)
CHANNEL_UNFIT = 0.75
# What the objective does to the value of a visit, by the way the product is
# bought. Conversion-optimised delivery finds buyers of impulse products best;
# awareness buys reach, not visits, whatever the product.
OBJECTIVE_FIT = {
    "conversions": {"impulse": 1.10, "considered": 1.06, "replenishment": 1.04,
                    "addon": 1.00},
    "traffic": {},
    "awareness": {"impulse": 0.82, "considered": 0.80, "replenishment": 0.78,
                  "addon": 0.78},
}
MESSAGE_HIT, MESSAGE_MISS = 1.06, 0.95
KEYWORD_FIT = {"generic": 1.0, "competitor": 0.85}
EXACT_FIT = {"replenishment": 1.06, "considered": 1.04, "impulse": 0.94,
             "addon": 0.94}


# --- The submitted value -----------------------------------------------------------

def blank(channel: str) -> dict:
    """The broad campaign every channel starts from, scored exactly 1.0."""
    base = {"channel": channel, "name": "", "share": 1.0, "skus": []}
    if channel == "google_search":
        return base | {"keywords": "generic", "match": "broad"}
    return base | {"objective": "traffic", "ages": [], "gender": "all",
                   "geo": [], "interests": [], "language": "", "format": ""}


def clean(value, sold: list[str] | None = None, normalise: bool = True) -> list[dict]:
    """Normalise a submitted campaign list. Anything unknown is dropped rather
    than trusted, and each channel's shares are scaled to add to one - unless
    `normalise` is off, which is how a refused form is shown back as typed."""
    if not isinstance(value, list):
        return []
    out, per = [], {}
    for raw in value:
        if not isinstance(raw, dict) or raw.get("channel") not in CHANNELS:
            continue
        ch = raw["channel"]
        if per.get(ch, 0) >= MAX_PER_CHANNEL:
            continue
        c = blank(ch)
        c["name"] = str(raw.get("name") or "")[:40]
        try:
            c["share"] = max(0.0, float(raw.get("share", 1.0)))
        except (TypeError, ValueError):
            c["share"] = 0.0
        skus = [s for s in raw.get("skus") or [] if isinstance(s, str)]
        c["skus"] = [s for s in skus if sold is None or s in sold]
        if ch == "google_search":
            c["keywords"] = raw.get("keywords") if raw.get("keywords") in KEYWORDS else "generic"
            c["match"] = raw.get("match") if raw.get("match") in MATCHES else "broad"
        else:
            c["objective"] = raw.get("objective") if raw.get("objective") in OBJECTIVES else "traffic"
            c["ages"] = [a for a in AGES if a in (raw.get("ages") or [])]
            c["gender"] = raw.get("gender") if raw.get("gender") in GENDERS else "all"
            c["geo"] = [t for t in TIERS if t in (raw.get("geo") or [])]
            c["interests"] = [i for i in INTERESTS
                              if i in (raw.get("interests") or [])][:MAX_INTERESTS]
            c["language"] = raw.get("language") if raw.get("language") in LANGUAGES else ""
            c["format"] = raw.get("format") if raw.get("format") in FORMATS else ""
        if raw.get("test") in ("A", "B"):
            c["test"] = raw["test"]
        if c["share"] > 0 or not normalise:
            out.append(c)
            per[ch] = per.get(ch, 0) + 1
    # A test is exactly one A against one B on the same channel. Anything else
    # is not a test, whatever the flags say.
    for ch in per:
        flags = sorted(c.get("test", "") for c in out if c["channel"] == ch)
        if [f for f in flags if f] != ["A", "B"]:
            for c in out:
                if c["channel"] == ch:
                    c.pop("test", None)
    if not normalise:
        return out
    for ch in per:
        total = sum(c["share"] for c in out if c["channel"] == ch)
        for c in out:
            if c["channel"] == ch:
                c["share"] = c["share"] / total
    return out


# --- Who the buyers are --------------------------------------------------------------

def _age_buyers(aud: dict, pool: dict) -> dict[str, float]:
    """Share of a product's buyers in each age band."""
    core, second = aud["core_age"], aud.get("second_age") or ""
    buyers = {core: 0.55 if second else 0.70}
    if second:
        buyers[second] = 0.25
    rest = [a for a in AGES if a not in buyers]
    left = 1.0 - sum(buyers.values())
    weight = sum(float(pool[AGES[a]]) for a in rest) or 1.0
    for a in rest:
        buyers[a] = left * float(pool[AGES[a]]) / weight
    return buyers


def _geo_buyers(aud: dict, pool: dict) -> dict[str, float]:
    listed = [t for t in str(aud["geo"]).split("|") if t in TIERS]
    others = [t for t in TIERS if t not in listed]
    buyers = {}
    for group, share in ((listed, 0.85 if others else 1.0), (others, 0.15)):
        weight = sum(float(pool[TIERS[t]]) for t in group) or 1.0
        for t in group:
            buyers[t] = share * float(pool[TIERS[t]]) / weight
    return buyers


def _interest_weights(aud: dict) -> dict[str, float]:
    top = [i for i in (aud.get("interest_1"), aud.get("interest_2")) if i]
    weights = dict(zip(top, (0.45, 0.30)))
    rest = [i for i in INTERESTS if i not in weights]
    left = 1.0 - sum(weights.values())
    for i in rest:
        weights[i] = left / len(rest)
    return weights


def _pick(chosen: list, universe) -> list:
    return list(chosen) if chosen else list(universe)


def _fit(aud: dict, channel: str) -> float:
    ranked = [aud.get(f"channel_{n}") for n in (1, 2, 3)]
    if channel in ranked:
        return CHANNEL_FIT[ranked.index(channel)]
    return CHANNEL_UNFIT


# --- Scoring ----------------------------------------------------------------------

def _pool_share(c: dict, pool: dict, params, brand_equity: float) -> float:
    """Share of the platform's audience a campaign can reach at all."""
    if c["channel"] == "google_search":
        if c["keywords"] == "brand":
            return params["retarget_pool"] * max(brand_equity, 0.05) / 0.5
        return 0.5 if c["match"] == "exact" else 1.0
    if c["objective"] == "retargeting":
        return params["retarget_pool"]
    share = sum(float(pool[AGES[a]]) for a in _pick(c["ages"], AGES))
    female = float(pool["female"])
    share *= {"all": 1.0, "female": female, "male": 1 - female}[c["gender"]]
    share *= sum(float(pool[TIERS[t]]) for t in _pick(c["geo"], TIERS))
    if c["interests"]:
        share *= min(1.0, params["interest_pool_share"] * len(c["interests"]))
    return share


def _sku_factors(c: dict, aud: dict, pool: dict, params, avg_fit: float) -> dict:
    """Each dimension's effect on one product, as a multiplier (1.0 = broad)."""
    f = {"fit": _fit(aud, c["channel"]) / avg_fit}
    purchase = aud["purchase"]
    if c["channel"] == "google_search":
        if c["keywords"] == "brand":
            f["audience"] = params["brand_search_boost"] ** params["targeting_beta"]
        else:
            f["audience"] = KEYWORD_FIT[c["keywords"]]
        f["message"] = EXACT_FIT[purchase] if c["match"] == "exact" else 1.0
        return f

    if c["objective"] == "retargeting":
        f["audience"] = params["retarget_boost"] ** params["targeting_beta"]
    else:
        conc = {}
        ages = _age_buyers(aud, pool)
        chosen = _pick(c["ages"], AGES)
        conc["age"] = (sum(ages[a] for a in chosen)
                       / sum(float(pool[AGES[a]]) for a in chosen))
        female_buy, female_pool = float(aud["female_share"]), float(pool["female"])
        conc["gender"] = {"all": 1.0,
                          "female": female_buy / female_pool,
                          "male": (1 - female_buy) / (1 - female_pool)}[c["gender"]]
        geo = _geo_buyers(aud, pool)
        chosen = _pick(c["geo"], TIERS)
        conc["geo"] = (sum(geo[t] for t in chosen)
                       / sum(float(pool[TIERS[t]]) for t in chosen))
        if c["interests"]:
            weights = _interest_weights(aud)
            reach = min(1.0, sum(weights[i] for i in c["interests"]))
            conc["interest"] = reach / min(
                1.0, params["interest_pool_share"] * len(c["interests"]))
        else:
            conc["interest"] = 1.0
        beta = params["targeting_beta"]
        for k, v in conc.items():
            f[k] = max(v, 1e-3) ** beta
    f["objective"] = OBJECTIVE_FIT.get(c["objective"], {}).get(purchase, 1.0)
    msg = 1.0
    if c["language"]:
        msg *= MESSAGE_HIT if c["language"] == aud["language"] else MESSAGE_MISS
    if c["format"]:
        msg *= MESSAGE_HIT if c["format"] == aud["format"] else MESSAGE_MISS
    f["message"] = msg
    return f


def score_campaign(c: dict, params, sold: list[str], spend: float,
                   brand_equity: float = 0.5) -> dict:
    """Quality of one campaign, with the reasons it came out that way."""
    pool = params.platform(c["channel"])
    range_ = [s for s in sold if params.audience(s)] or [
        a["code"] for a in params.audiences]
    promoted = [s for s in c["skus"] if s in range_] or range_
    weight = {s: float(params.sku(s)["revenue_weight"]) for s in range_}
    avg_fit = (sum(weight[s] * _fit(params.audience(s), c["channel"]) for s in range_)
               / sum(weight[s] for s in range_))

    per_sku, dims = {}, {}
    total_w = sum(weight[s] for s in promoted)
    for s in promoted:
        f = _sku_factors(c, params.audience(s), pool, params, avg_fit)
        per_sku[s] = f
        for k, v in f.items():
            dims[k] = dims.get(k, 0.0) + weight[s] / total_w * math.log(v)
    quality = sum(weight[s] / total_w * math.prod(per_sku[s].values())
                  for s in promoted)

    share = _pool_share(c, pool, params, brand_equity)
    ref = float(_default_spend(c["channel"]))
    need = params["targeting_pool_min"] * max(spend, 1.0) / ref
    exp = params["targeting_fatigue_exp"]
    if c.get("objective") == "retargeting" or c.get("keywords") == "brand":
        # People who already know you are a pool that does not grow with
        # spend, so over-feeding it is punished twice as hard.
        exp *= 2
    fatigue = min(1.0, share / need) ** exp if need > 0 else 1.0
    return {"quality": quality * fatigue, "fatigue": fatigue, "pool": share,
            "dims": {k: math.exp(v) for k, v in dims.items()},
            "per_sku": per_sku, "promoted": promoted}


def _default_spend(channel: str) -> float:
    from ecomsim.decisions import REGISTRY
    return float(REGISTRY[CHANNELS[channel]].default_when_disabled)


def channel_scores(campaigns: list[dict], spend: dict[str, float], params,
                   sold: list[str], brand_equity: float = 0.5) -> dict:
    """{channel: {"quality", "traffic", "cvr", "campaigns": [...]}} for every
    channel the team set campaigns on. Channels it did not are absent, and the
    engine reads an absent channel as exactly 1.0."""
    out = {}
    for ch in CHANNELS:
        mine = [c for c in campaigns if c["channel"] == ch]
        if not mine:
            continue
        rows = []
        for c in mine:
            s = score_campaign(c, params, sold, spend.get(ch, 0.0) * c["share"],
                               brand_equity)
            rows.append(c | s | {"spend": spend.get(ch, 0.0) * c["share"]})
        # Retargeting draws on one small pool, however it is split up.
        rt = sum(c["share"] for c in mine
                 if c.get("objective") == "retargeting" or c.get("keywords") == "brand")
        quality = sum(r["share"] * r["quality"] for r in rows)
        traffic, cvr = multipliers(quality, params)
        for r in rows:
            r["traffic"], r["cvr"] = multipliers(r["quality"], params)
        out[ch] = {"quality": quality, "traffic": traffic, "cvr": cvr,
                   "retarget_share": rt, "campaigns": rows}
    return out


def multipliers(quality: float, params) -> tuple[float, float]:
    """Sessions per rupee and paid conversion, from campaign quality."""
    lq = math.log(max(quality, 1e-6))
    cap = params["targeting_traffic_cap"]
    traffic = max(1 - cap, min(1 + cap, 1 + params["targeting_traffic_slope"] * lq))
    cap = params["targeting_cvr_cap"]
    cvr = max(1 - cap, min(1 + cap, 1 + params["targeting_cvr_slope"] * lq))
    return traffic, cvr


# --- Explaining it -------------------------------------------------------------------

def _names(params, skus: list[str], limit: int = 2) -> str:
    # "Hair Oil 200ml" -> "hair oil": the pack size says nothing about who buys it.
    names = [" ".join(w for w in str(params.sku(s)["name"]).split()
                      if not any(ch.isdigit() for ch in w)).lower()
             for s in skus]
    names = list(dict.fromkeys(names))
    if len(names) > limit:
        return ", ".join(names[:limit]) + f" and {len(names) - limit} more"
    return " and ".join(names)


def findings(row: dict, params, channel_row: dict | None = None) -> list[str]:
    """Plain sentences on why a campaign worked or did not. They name the
    symptom and the buyer it missed; they do not hand over the settings."""
    c, out = row, []
    label = f"“{c['name']}”" if c.get("name") else "This campaign"
    promoted = c["promoted"]
    auds = [params.audience(s) for s in promoted]
    weights = [float(params.sku(s)["revenue_weight"]) for s in promoted]
    tw = sum(weights) or 1.0
    what = _names(params, promoted)
    ch = CHANNEL_NAMES[c["channel"]]
    dims = c["dims"]

    unfit = [s for s, a in zip(promoted, auds)
             if c["channel"] not in (a.get("channel_1"), a.get("channel_2"),
                                     a.get("channel_3"))]
    # A broad campaign carries poor fits by definition and is scored neutral
    # for them, so this is only said about products the team chose to push.
    if unfit and c["skus"]:
        why = ("people rarely search for it" if c["channel"] == "google_search"
               else f"{ch}'s audience rarely buys it here")
        out.append(f"{label} promotes {_names(params, unfit)} on {ch}, where "
                   f"{why}. Its spend buys visits that do not turn into orders.")

    if c["channel"] != "google_search" and c.get("objective") != "retargeting":
        female = sum(w * float(a["female_share"]) for w, a in zip(weights, auds)) / tw
        if c["gender"] == "male" and female > 0.6:
            out.append(f"{label} targets men, but about {female:.0%} of {what} "
                       f"buyers are women.")
        elif c["gender"] == "female" and female < 0.45:
            out.append(f"{label} targets women only, but {1 - female:.0%} of "
                       f"{what} buyers are men - and they are most of the "
                       f"{ch} audience.")
        cores = {a["core_age"] for a in auds}
        if c["ages"] and not cores & set(c["ages"]):
            out.append(f"{label} leaves out {', '.join(sorted(cores))}, the age "
                       f"most {what} buyers are.")
        home = {str(a["geo"]).split("|")[0] for a in auds}
        if c["geo"] and not home & set(c["geo"]):
            out.append(f"{label} runs in {', '.join(TIER_NAMES[t] for t in c['geo'])}; "
                       f"most {what} buyers are in "
                       f"{', '.join(TIER_NAMES[t] for t in sorted(home))}.")
        if c["interests"]:
            tops = {a.get("interest_1") for a in auds} | {a.get("interest_2") for a in auds}
            if not tops & set(c["interests"]):
                out.append(f"{label} targets {', '.join(INTERESTS[i] for i in c['interests'])}, "
                       f"which is not what {what} buyers follow.")
        if len(promoted) > 1 and dims.get("age", 1) * dims.get("geo", 1) < 0.95 and (
                len(cores) > 1 or len(home) > 1):
            out.append(f"{label} promotes products bought by different people in "
                       f"one audience; no single setting suits all of them. "
                       f"Split it.")
        langs = {a["language"] for a in auds}
        if c["language"] and c["language"] not in langs:
            out.append(f"{label} speaks {LANGUAGES[c['language']]}; "
                       f"{what} buyers respond better to "
                       f"{' or '.join(LANGUAGES[x] for x in sorted(langs))}.")
        if c.get("objective") == "awareness":
            out.append(f"{label} is set to awareness. That buys reach, not visits, "
                       f"so few sessions come back for the rupees spent.")

    if c["fatigue"] < 0.85:
        out.append(f"{label}: the audience is small for PKR {c['spend']:,.0f}, "
                   f"so the same people see the ad again and again and each "
                   f"impression costs more. A wider audience or a smaller "
                   f"budget would use it better.")
    if channel_row and channel_row["retarget_share"] > 0.35 and (
            c.get("objective") == "retargeting" or c.get("keywords") == "brand"):
        out.append(f"{channel_row['retarget_share']:.0%} of {ch} goes to people "
                   f"who already know you. That pool is small; the extra spend "
                   f"mostly shows them the same ads.")
    if c["quality"] >= 1.15 and not any("buyers" in f for f in out):
        out.append(f"{label} reaches the people who buy {what}. Each rupee is "
                   f"working about {c['traffic'] - 1:.0%} harder than a broad "
                   f"campaign.")
    return out


def debrief(params, sku: str) -> dict:
    """The answer, for the end of the run: who buys it and the usual mistake."""
    a = params.audience(sku)
    return {"sku": sku, "name": params.sku(sku)["name"],
            "age": a["core_age"] + (f" (then {a['second_age']})" if a.get("second_age") else ""),
            "women": float(a["female_share"]),
            "where": ", ".join(TIER_NAMES[t] for t in str(a["geo"]).split("|")),
            "interests": ", ".join(INTERESTS[i] for i in (a["interest_1"], a.get("interest_2")) if i),
            "language": LANGUAGES[a["language"]], "format": FORMATS[a["format"]],
            "channels": ", ".join(CHANNEL_NAMES[a[f"channel_{n}"]]
                                  for n in (1, 2, 3) if a.get(f"channel_{n}")),
            "mistake": a["mistake"]}


# --- The month's numbers, per campaign ------------------------------------------------

SETTINGS = {
    "social": ("skus", "objective", "ages", "gender", "geo", "interests",
               "language", "format"),
    "search": ("skus", "keywords", "match"),
}
SETTING_NAMES = {"skus": "products", "objective": "objective", "ages": "age",
                 "gender": "gender", "geo": "cities", "interests": "interests",
                 "language": "language", "format": "format",
                 "keywords": "keywords", "match": "match type"}


def settings_of(c: dict) -> dict:
    keys = SETTINGS["search" if c["channel"] == "google_search" else "social"]
    return {k: c.get(k) for k in keys}


def performance(team, params, ctx, resolved: dict, run_id: str = "",
                round_: int = 0) -> list[dict]:
    """The standard performance-marketing table for one team's month.

    Every paid channel with spend gets rows - a channel with no campaigns set
    is one broad row - so the metrics are there to learn from before anyone
    touches a setting. Sessions are the channel's real sessions split by
    spend and campaign quality; orders use the month's real conversion and
    are scaled by how much of the traffic's demand actually became orders.
    """
    tid = team.team_id
    scored = ctx.get("targeting", {}).get(tid, {})
    sessions = ctx.get("paid_sessions", {}).get(tid, {})
    inflation = ctx.get("channel_inflation", {}).get(tid, {})
    cr = ctx.get("conversion_rate", {}).get(tid, 0.0)
    capacity = ctx.get("traffic_capacity", {}).get(tid, 0.0)
    orders_all = ctx.get("orders", {}).get(tid, 0.0)
    realised = min(1.0, orders_all / capacity) if capacity > 0 else 0.0
    aov = ctx.get("aov", {}).get(tid, 0.0)
    repeat = ctx.get("repeat_order_share", {}).get(tid, 0.0)
    new = ctx.get("new_customers", {}).get(tid, 0.0)
    new_share = min(1.0, new / max(orders_all * (1 - repeat), 1.0))

    rows = []
    for ch, dec in CHANNELS.items():
        spend = float(resolved.get(dec, 0) or 0)
        if spend <= 0:
            continue
        block = scored.get(ch)
        camps = block["campaigns"] if block else [
            blank(ch) | {"quality": 1.0, "traffic": 1.0, "cvr": 1.0,
                         "fatigue": 1.0, "spend": spend, "promoted": [],
                         "dims": {}, "name": "Broad - no campaign set"}]
        weight = [c["spend"] * c["traffic"] for c in camps]
        total = sum(weight) or 1.0
        cpm_base = float(params.channel(ch)["cpm_base"])
        for c, w in zip(camps, weight):
            s = sessions.get(ch, 0.0) * w / total
            cpm = cpm_base * inflation.get(ch, 1.0) / max(c["fatigue"], 0.3)
            impressions = c["spend"] / cpm * 1000 if cpm > 0 else 0.0
            orders = s * cr * c["cvr"] * realised
            revenue = orders * aov
            acquired = orders * new_share
            rows.append({
                "channel": ch, "channel_name": CHANNEL_NAMES[ch],
                "name": c.get("name") or "Campaign",
                "spend": c["spend"], "impressions": impressions, "cpm": cpm,
                "clicks": s, "ctr": s / impressions if impressions else 0.0,
                "cpc": c["spend"] / s if s else 0.0,
                "orders": orders, "cvr": orders / s if s else 0.0,
                "revenue": revenue,
                "roas": revenue / c["spend"] if c["spend"] else 0.0,
                "cac": c["spend"] / acquired if acquired else 0.0,
                "quality": c["quality"], "lift": c["traffic"] - 1,
                "findings": findings(c, params, block) if block else [],
                "test": c.get("test", ""), "settings": settings_of(c),
                "new_share": new_share, "aov": aov,
            })
    _split_tests(rows, run_id, round_, team.team_id)
    return rows


def _split_tests(rows: list[dict], run_id: str, round_: int, team_id: str) -> None:
    """Orders in a test pair are a draw, not an average.

    Each order goes to A or B the way real conversions fall: around each
    campaign's true rate, with the scatter a sample of that size carries. The
    pair's total is untouched, so the month's paid orders still add up and
    nothing outside the report moves. What changes is that a small test can
    now come out the wrong way round - which is the lesson.
    """
    from . import rng
    for ch in CHANNELS:
        pair = {r["test"]: r for r in rows if r["channel"] == ch and r["test"]}
        if set(pair) != {"A", "B"}:
            continue
        a, b = pair["A"], pair["B"]
        n = a["orders"] + b["orders"]
        if n <= 0:
            continue
        p = a["orders"] / n
        draw = rng.normal(run_id, round_, team_id, "abtest", 0.0, 1.0, ch)
        got_a = min(n, max(0.0, n * p + draw * math.sqrt(n * p * (1 - p))))
        for r, o in ((a, got_a), (b, n - got_a)):
            r["orders"] = o
            r["cvr"] = o / r["clicks"] if r["clicks"] else 0.0
            r["revenue"] = o * r["aov"]
            r["roas"] = r["revenue"] / r["spend"] if r["spend"] else 0.0
            acquired = o * r["new_share"]
            r["cac"] = r["spend"] / acquired if acquired else 0.0


def ab_tests(history: list[dict]) -> list[dict]:
    """The verdict on each channel's running test, pooling every consecutive
    month in which A and B ran unchanged. Changing either side restarts it."""
    out = []
    if not history:
        return out
    for ch in CHANNELS:
        now = {r["test"]: r for r in history[-1].get("campaigns") or []
               if r["channel"] == ch and r.get("test")}
        if set(now) != {"A", "B"}:
            continue
        sig = (now["A"]["settings"], now["B"]["settings"])
        pooled = {"A": [0.0, 0.0, 0.0], "B": [0.0, 0.0, 0.0]}   # spend, clicks, orders
        months = 0
        for rec in reversed(history):
            then = {r["test"]: r for r in rec.get("campaigns") or []
                    if r["channel"] == ch and r.get("test")}
            if set(then) != {"A", "B"} or (then["A"]["settings"], then["B"]["settings"]) != sig:
                break
            months += 1
            for k in ("A", "B"):
                pooled[k][0] += then[k]["spend"]
                pooled[k][1] += then[k]["clicks"]
                pooled[k][2] += then[k]["orders"]
        out.append(_verdict(ch, now, pooled, months))
    return out


def _verdict(ch: str, now: dict, pooled: dict, months: int) -> dict:
    (sa, ca, oa), (sb, cb, ob) = pooled["A"], pooled["B"]
    n = oa + ob
    # Conditional on the orders the pair won, A's share should equal its
    # share of the spend if the two work equally hard. How far it sits from
    # that, in standard errors, is the whole test.
    p0 = sa / (sa + sb) if sa + sb else 0.5
    z = (oa - n * p0) / math.sqrt(n * p0 * (1 - p0)) if n and 0 < p0 < 1 else 0.0
    confidence = math.erf(abs(z) / math.sqrt(2))
    # A sample never proves anything to 100%; saying so would teach the wrong
    # thing about what a test can know.
    sure = "over 99%" if confidence > 0.99 else f"{confidence:.0%}"
    rate_a, rate_b = (oa / sa if sa else 0.0), (ob / sb if sb else 0.0)
    lead, trail = ("A", "B") if rate_a >= rate_b else ("B", "A")
    hi, lo = max(rate_a, rate_b), min(rate_a, rate_b)
    edge = hi / lo - 1 if lo else 0.0
    names = {k: now[k]["name"] for k in ("A", "B")}
    diffs = [SETTING_NAMES[k] for k in now["A"]["settings"]
             if now["A"]["settings"][k] != now["B"]["settings"][k]]
    span = f"{months} month{'s' if months != 1 else ''}"

    if not diffs:
        verdict = (f"A and B are set up identically, so this tests nothing but "
                   f"chance. Any gap below is luck - which is worth seeing once.")
        call = "none"
    elif confidence >= 0.95:
        verdict = (f"{lead} wins: {edge:.0%} more orders per rupee than {trail}, "
                   f"{sure} confident after {span} and {n:,.0f} orders. "
                   f"Move the budget to “{names[lead]}”, then test your "
                   f"next idea against it.")
        call = lead
    elif confidence >= 0.80:
        verdict = (f"{lead} is ahead by {edge:.0%}, but only {sure} "
                   f"confident - not enough to call it. Leave both unchanged "
                   f"another month and the extra orders will settle it.")
        call = "leaning"
    else:
        verdict = (f"No difference you can trust yet: {edge:.0%} is inside the "
                   f"noise of {n:,.0f} orders. Either the two really are about "
                   f"as good, or the test needs more orders - a larger share of "
                   f"the budget, or another month unchanged.")
        call = "open"
    if len(diffs) > 1:
        verdict += (f" A and B differ in {len(diffs)} settings ({', '.join(diffs)}), "
                    f"so whichever wins, you will not know which change did it. "
                    f"Test one thing at a time.")
    return {"channel": ch, "channel_name": CHANNEL_NAMES[ch], "names": names,
            "months": months, "orders": {"A": oa, "B": ob},
            "spend": {"A": sa, "B": sb}, "clicks": {"A": ca, "B": cb},
            "per_1000": {"A": rate_a * 1000, "B": rate_b * 1000},
            "cvr": {"A": oa / ca if ca else 0.0, "B": ob / cb if cb else 0.0},
            "confidence": confidence, "sure": sure, "edge": edge, "lead": lead,
            "call": call, "diffs": diffs, "verdict": verdict}
