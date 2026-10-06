"""Instructor debrief - what each team decided this month, and what it did.

The console already shows scores and KPI trends. This answers the question an
instructor asks before walking into the room: why is this team at the top and
that one at the bottom? Each team gets its results, the decisions it actually
took (and the ones it left at default), and plain-language observations drawn
from both - what worked, and what to raise.

Only what a team SUBMITTED counts as a decision. Anything else ran on the
default, and saying so is often the most useful line in the debrief.
"""
from __future__ import annotations

from html import escape

from .decisions import REGISTRY
from .modules.m09_basket import BUNDLE_UNITS, _unit_net_price
from .targeting import CHANNELS, CHANNEL_NAMES

AD_CODES = list(CHANNELS.values())                     # Meta, TikTok, Google
SOURCING = {"local": "local", "import": "imported", "mixed": "mixed"}


def _money(v: float) -> str:
    v = float(v or 0)
    if abs(v) >= 1e6:
        return f"PKR {v / 1e6:,.2f}m"
    return f"PKR {v:,.0f}"


def _default(code: str):
    return REGISTRY[code].default_when_disabled


def _label(code: str) -> str:
    return REGISTRY[code].name if code in REGISTRY else code


def _packs(team, params, sub: dict) -> list[tuple[str, float]]:
    """(product name, pack price / three singles) for each pack offered."""
    raw = sub.get("1.2") or {}
    cells = {c: {} for c in raw} if isinstance(raw, list) else dict(raw)
    out = []
    for code, cell in cells.items():
        try:
            ref = _unit_net_price(team, params, sub, code) * BUNDLE_UNITS
            price = float((cell or {}).get("price") or 0) or ref * 0.9
        except (KeyError, TypeError, ValueError):
            continue
        if ref > 0:
            out.append((str(params.sku(code)["name"]), price / ref))
    return out


def _decisions(team, params, sub: dict) -> list[tuple[str, str]]:
    """The decisions a team actually took, as (label, plain description)."""
    rows = []
    ads = {c: float(sub[c]) for c in AD_CODES if c in sub}
    if ads:
        names = {v: CHANNEL_NAMES[k] for k, v in CHANNELS.items()}
        rows.append(("Ad budgets", " · ".join(
            f"{names[c]} {_money(v)}" for c, v in ads.items())
            + f" &middot; total {_money(sum(ads.values()))}"))
    for code in ("3.8", "3.9", "6.1"):
        if code in sub:
            rows.append((_label(code), _money(sub[code])))
    grid = sub.get("1.1")
    if isinstance(grid, dict) and grid:
        prices = sum(1 for c in grid.values() if isinstance(c, dict) and c.get("price"))
        discs = sum(1 for c in grid.values() if isinstance(c, dict) and c.get("discount"))
        srcs = [c.get("sourcing") for c in grid.values()
                if isinstance(c, dict) and c.get("sourcing")]
        bits = []
        if prices:
            bits.append(f"{prices} price{'s' if prices != 1 else ''} changed")
        if discs:
            bits.append(f"{discs} line discount{'s' if discs != 1 else ''}")
        if srcs:
            kinds = sorted(set(srcs))
            bits.append(f"{len(srcs)} line{'s' if len(srcs) != 1 else ''} sourced "
                        + "/".join(SOURCING.get(k, k) for k in kinds))
        if bits:
            rows.append(("Prices and sourcing", ", ".join(bits)))
    packs = _packs(team, params, sub)
    if packs:
        avg = sum(1 - r for _, r in packs) / len(packs)
        where = (f"on average {avg:.0%} below three singles" if avg >= 0.005 else
                 f"on average {-avg:.0%} above three singles" if avg <= -0.005 else
                 "priced the same as three singles")
        rows.append(("Bundles", f"{len(packs)} pack{'s' if len(packs) != 1 else ''}, {where}"))
    if "2.4" in sub:
        v = float(sub["2.4"] or 0)
        rows.append(("Free delivery above", "every order" if v <= 0 else _money(v)))
    if "2.2" in sub and float(sub["2.2"] or 0):
        rows.append(("Site-wide discount", f"{float(sub['2.2']):.0%}"))
    for code in ("1.5", "8.5", "9.3", "9.1", "7.2"):
        if code in sub and sub[code] not in (None, ""):
            rows.append((_label(code), escape(str(sub[code]))))
    if "9.2" in sub:
        rows.append((_label("9.2"), f"{float(sub['9.2'] or 0):.0%}"))
    if "7.1" in sub and sub["7.1"] not in (None, ""):
        rows.append((_label("7.1"), f"{float(sub['7.1']):,.0f} units"))
    if "7.5" in sub:
        rows.append((_label("7.5"), f"{float(sub['7.5']):g} weeks"))
    if "7.4" in sub:
        rows.append((_label("7.4"), _money(sub["7.4"])))
    if "5.1" in sub:
        rows.append((_label("5.1"), _money(sub["5.1"])))
    if sub.get("12.1"):
        studies = sub["12.1"] if isinstance(sub["12.1"], list) else str(sub["12.1"]).split(";")
        rows.append(("Research", ", ".join(escape(str(s)) for s in studies)))
    memo = str(sub.get("12.5") or "").strip()
    if memo:
        words = len(memo.split())
        cut = memo if len(memo) <= 220 else memo[:217].rsplit(" ", 1)[0] + "..."
        rows.append(("Board memo", f"&ldquo;{escape(cut)}&rdquo; "
                     f'<span class="mute">({words} words)</span>'))
    return rows


def _observations(team, params, sub, h, room, open_codes) -> tuple[list[str], list[str]]:
    """(what worked, what to raise) for one team."""
    good, watch = [], []
    tid = team.team_id

    def best(key, label, fmt, low=False):
        vals = [r[key] for r in room.values()]
        if len(vals) < 2:
            return
        target = min(vals) if low else max(vals)
        if h[key] == target and len(set(vals)) > 1:
            good.append(f"{label} in the room ({fmt(h[key])}).")

    best("ebitda", "Highest EBITDA", _money)
    best("gross_margin_pct", "Best gross margin", lambda v: f"{v:.1%}")
    best("aov_net", "Biggest average order", _money)
    best("conversion_rate", "Best conversion", lambda v: f"{v:.2%}")
    if h["cac_blended"] > 0:
        best("cac_blended", "Lowest cost per new customer", _money, low=True)

    ebitdas = sorted(r["ebitda"] for r in room.values())
    if len(ebitdas) > 1 and h["ebitda"] == ebitdas[0] and h["ebitda"] < 0:
        watch.append(f"Biggest loss in the room: EBITDA {_money(h['ebitda'])}.")

    taken = [c for c in sub if c in open_codes] if open_codes else list(sub)
    if open_codes and not sub:
        watch.append("Submitted nothing: the whole month ran on default decisions.")
    elif open_codes and len(taken) <= max(2, len(open_codes) // 4):
        left = [c for c in open_codes if c not in sub]
        watch.append(f"Set only {len(taken)} of {len(open_codes)} open decisions; the "
                     f"rest ran on defaults ({', '.join(_label(c) for c in left[:4])}"
                     f"{'&hellip;' if len(left) > 4 else ''}).")

    default_ads = sum(float(_default(c) or 0) for c in AD_CODES)
    if any(c in sub for c in AD_CODES):
        ads = sum(float(sub.get(c, _default(c)) or 0) for c in AD_CODES)
        cacs = sorted(r["cac_blended"] for r in room.values() if r["cac_blended"] > 0)
        median = cacs[len(cacs) // 2] if cacs else 0
        if ads < 0.4 * default_ads:
            watch.append(f"Cut ad budgets to {_money(ads)} (default {_money(default_ads)}): "
                         f"{h['new_customers']:,.0f} new customers while fixed costs stayed "
                         f"the same.")
        elif ads > 1.6 * default_ads and h["cac_blended"] > median:
            watch.append(f"Spent {_money(ads)} on ads with a cost per new customer of "
                         f"{_money(h['cac_blended'])}, above the room's median.")

    packs = _packs(team, params, sub)
    if len(packs) > 3:
        watch.append(f"Offered {len(packs)} bundles; only the three most attractive "
                     f"count, so the rest add nothing.")
    dear = [(n, r) for n, r in packs if r > 1.0]
    if dear:
        n, r = max(dear, key=lambda x: x[1])
        watch.append(f"{len(dear)} pack{'s' if len(dear) != 1 else ''} priced above three "
                     f"singles (worst: {escape(n)} at {r - 1:.0%} over) - few will buy.")
    deep = [(n, r) for n, r in packs if r < 0.75]
    if deep:
        watch.append(f"{len(deep)} pack{'s' if len(deep) != 1 else ''} discounted more "
                     f"than 25% - basket grows, margin per unit shrinks.")

    if "2.4" in sub and float(sub["2.4"] or 0) <= 0:
        watch.append("Free delivery on every order: no reason for customers to add "
                     "to the basket, and the courier bill is all yours.")
    if sub.get("9.3") == "B":
        watch.append("Cheapest payment gateway: 1 in 6 card payments fails, and "
                     "each failure is a lost order.")
    if sub.get("9.1") == "off":
        watch.append("Cash on delivery switched off: far fewer orders in a COD market.")

    demand_units = h["orders"] * params["units_per_order"]
    if "7.1" in sub and sub["7.1"] not in (None, "") and \
            float(sub["7.1"]) < 0.6 * demand_units:
        watch.append(f"Bought only {float(sub['7.1']):,.0f} units against about "
                     f"{demand_units:,.0f} a month of demand: stock-out risk next month.")
    elif h.get("weeks_cover", 99) < 3:
        watch.append(f"Stock covers only {h['weeks_cover']:.1f} weeks of sales.")
    if "7.5" in sub and float(sub["7.5"] or 0) <= 2:
        watch.append(f"Safety stock of {float(sub['7.5']):g} weeks: little buffer "
                     f"if demand rises or a shipment is late.")

    grid = sub.get("1.1") if isinstance(sub.get("1.1"), dict) else {}
    srcs = [c.get("sourcing") for c in grid.values() if isinstance(c, dict)]
    if srcs and all(s == "local" for s in srcs if s) and any(srcs):
        watch.append("Sourced every changed line locally: fastest to restock, "
                     "and the most expensive per unit.")

    if "12.5" in open_codes or not open_codes:
        memo = str(sub.get("12.5") or "").strip()
        words = len(memo.split())
        if not memo:
            watch.append("No board memo (10% of the final score).")
        elif words < 30:
            watch.append(f"Board memo is {words} words: it should say what was decided, "
                         f"why, and the number that will prove it right.")
    return good, watch


def section(ranked, params, submissions: dict, open_codes: list[str], name_of) -> str:
    """The debrief block for the console. Empty when no submissions are known."""
    if submissions is None:
        return ""
    room = {t.team_id: t.history[-1] for t in ranked}
    n = len(ranked)
    cards = []
    for i, t in enumerate(ranked, 1):
        h = t.history[-1]
        sub = submissions.get(t.team_id, {}) or {}
        good, watch = _observations(t, params, sub, h, room, open_codes)
        tag = ("top" if i <= min(3, n // 2) else
               "bottom" if i > n - min(3, n // 2) else "")
        kpis = (f'{_money(h["revenue_net"])} revenue &middot; {h["orders"]:,.0f} orders '
                f'&middot; AOV {_money(h["aov_net"])} &middot; gross margin '
                f'{h["gross_margin_pct"]:.1%} &middot; contribution '
                f'{h["contribution_margin_pct"]:.1%} &middot; CAC {_money(h["cac_blended"])} '
                f'&middot; EBITDA {_money(h["ebitda"])}')
        took = _decisions(t, params, sub)
        took_html = ("".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in took)
                     if took else "<dt>Decisions</dt><dd>None submitted</dd>")
        defaulted = [c for c in open_codes if c not in sub] if open_codes else []
        left = (f'<p class="note">Left at default: '
                f'{escape(", ".join(_label(c) for c in defaulted))}.</p>'
                if defaulted and sub else "")
        lists = ""
        if good:
            lists += ('<div class="obs good"><b>What worked</b><ul>'
                      + "".join(f"<li>{g}</li>" for g in good) + "</ul></div>")
        if watch:
            lists += ('<div class="obs watch"><b>To raise</b><ul>'
                      + "".join(f"<li>{w}</li>" for w in watch) + "</ul></div>")
        cards.append(
            f'<div class="db {tag}"><h3>{i}. {escape(name_of(t))}'
            f'{"" if name_of(t) == t.team_id else f" <span class=tid>{t.team_id}</span>"}'
            f'{" <span class=pill>top</span>" if tag == "top" else ""}'
            f'{" <span class=pill>bottom</span>" if tag == "bottom" else ""}</h3>'
            f'<p class="kpis">{kpis}</p><div class="cols"><dl>{took_html}</dl>'
            f'<div>{lists}</div></div>{left}</div>')
    return ('<section class="wide"><h2>Debrief &middot; what each team decided '
            'and what it did</h2><p class="note">Ranked by score. Decisions are what '
            'each team submitted for this month; anything not listed ran on its '
            'default. Observations are generated from the decisions and the '
            'results, for the instructor to check before using.</p>'
            + "".join(cards) + "</section>")


CSS = """
.db{border-top:1px solid #e1e0d9;padding:14px 0 6px}
.db:first-of-type{border-top:none}
.db h3{font-size:16px;margin:0 0 4px}
.db .pill{font-size:11px;font-weight:600;padding:1px 7px;border-radius:9px;
background:#e7f3e7;color:#006300;vertical-align:2px}
.db.bottom .pill{background:#fbe9e9;color:#d03b3b}
.db .kpis{font-size:13px;color:#52514e;margin:0 0 8px}
.db .cols{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:820px){.db .cols{grid-template-columns:1fr}}
.db dl{margin:0;display:grid;grid-template-columns:150px 1fr;gap:3px 10px;font-size:13px}
.db dt{color:#52514e} .db dd{margin:0}
.db .mute{color:#898781}
.obs{font-size:13px;margin:0 0 8px} .obs ul{margin:4px 0 0;padding-left:18px}
.obs.good b{color:#006300} .obs.watch b{color:#d03b3b}
@media(prefers-color-scheme:dark){.db{border-color:#2c2c2a}.db dt,.db .kpis{color:#c3c2b7}}
"""
