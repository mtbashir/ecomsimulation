"""Where a team's points went, and which of its own decisions to look at.

For the instructor's console only: teams read how each decision moves the
score in the handbook, never a diagnosis of their own play. Each team's card
gets its points pillar by pillar against the best in the room, then its
biggest gaps - the measures where it left the most points - each with what
its own numbers and decisions say about it, and the levers to raise it.

The gaps come from scoring.breakdown, the same arithmetic as the final score.
The levers come from web/handbook.SCORE_IMPACT, the record the handbook reads.
Every line is a rule over the team's figures, so the instructor can check it
against the report before using it.
"""
from __future__ import annotations

from html import escape
from math import sqrt

from . import scoring
from .decisions import REGISTRY
from .modules.m10_fulfilment import DEFAULT_MIX

PILLARS = (("p1", "Profitability", "profitability"), ("p2", "Growth", "growth"),
           ("p3", "Customer value", "customer-value"),
           ("p4", "Operational efficiency", "operations"),
           ("p5", "Cash & capital", "cash-capital"),
           ("p6", "Decision quality", "decision-quality"))
SHOWN = 3              # gaps listed per team
MIN_GAP = 0.25         # points: smaller gaps are not worth a line
CRM_FULL = 400_000     # PKR a month at which CRM reaches every customer it can
QA_BEST = 250_000      # PKR a month at which quality assurance is at its best


def _lever(code: str) -> str:
    name = REGISTRY[code].name if code in REGISTRY else code
    anchor = "d" + code.replace(".", "-")
    return f'<a href="/handbook#{anchor}">{escape(name)} ({code})</a>'


def _pkr(v: float) -> str:
    return f"PKR {v / 1e6:,.1f}m" if abs(v) >= 1e6 else f"PKR {v:,.0f}"


def _num(d: dict, code: str, default: float = 0.0) -> float:
    try:
        return float(d.get(code) if d.get(code) is not None else default)
    except (TypeError, ValueError):
        return default


def _mix(d: dict) -> dict:
    mix = d.get("8.3")
    return mix if isinstance(mix, dict) and mix else DEFAULT_MIX


def _diagnose(key: str, team, params, d: dict, part: dict) -> list[str]:
    """What the team's own figures say about one measure: plain sentences,
    each naming the decision behind it. Empty when no rule applies."""
    h = team.history[-1]
    v = part["value"]
    out = []
    ads = {c: _num(d, c) for c in ("3.1", "3.2", "3.4")}
    crm = _num(d, "6.1")
    disc = _num(d, "2.2")

    if key == "delivery":
        couriers = {c["code"]: c for c in params.couriers}
        best = max(couriers.values(), key=lambda c: float(c["success_rate"]))
        mix = _mix(d)
        share = float(mix.get(best["code"], 0) or 0) / (sum(float(x or 0) for x in mix.values()) or 1)
        out.append(f"Delivers {v:.1%} of parcels. {escape(best['name'])}, the most reliable "
                   f"courier ({float(best['success_rate']):.1%}), carries {share:.0%} of orders "
                   f"in the {_lever('8.3')}.")
    elif key == "leak":
        out.append(f"Refused and returned parcels cost {v:.1%} of revenue "
                   f"(refused {h.get('rto_rate', 0):.1%} of orders, returned "
                   f"{h.get('return_rate', 0):.1%}).")
        if _num(d, "9.2") < 0.05 and str(d.get("9.1", "on")) == "on":
            out.append(f"The {_lever('9.2')} is {_num(d, '9.2'):.0%}: little reason to pay in "
                       f"advance, so most orders stay cash on delivery.")
        if str(d.get("10.4", "")) == "free":
            out.append(f"Free returns ({_lever('10.4')}) invite the most returns.")
        if _num(d, "7.4") < QA_BEST:
            out.append(f"{_lever('7.4')} is {_pkr(_num(d, '7.4'))}, below the "
                       f"{_pkr(QA_BEST)} where it does most against defects.")
    elif key == "turns":
        out.append(f"Stock turns {v:.1f} times a year; it holds about "
                   f"{float(h.get('weeks_cover', 0) or 0):.1f} weeks of stock.")
        if _num(d, "7.5", 3) > 3:
            out.append(f"{_lever('7.5')} is {_num(d, '7.5', 3):g} weeks on top of forecast.")
    elif key == "service":
        lost = float(h.get("lost_to_stockout", 0) or 0)
        out.append(f"Served {v:.1%} of demand" + (f"; about {lost:,.0f} orders were lost to "
                   f"stock-outs last month" if lost >= 1 else "") + ".")
        if _num(d, "7.5", 3) < 2:
            out.append(f"{_lever('7.5')} is only {_num(d, '7.5', 3):g} weeks.")
    elif key in ("ltv_cac", "repeat", "active"):
        if key == "ltv_cac":
            out.append(f"Lifetime value is {v:.1f}x what a customer costs to win.")
        elif key == "repeat":
            out.append(f"{v:.1%} of orders come from returning customers.")
        else:
            out.append(f"{v:,.0f} active customers at the end.")
        if ads["3.4"] > max(ads["3.1"], ads["3.2"]) and ads["3.4"] > 0:
            out.append(f"{_lever('3.4')} is the biggest paid budget ({_pkr(ads['3.4'])}): its "
                       f"customers are the quickest to leave.")
        if disc > 0.25:
            out.append(f"A {_lever('2.2')} of {disc:.0%} makes new customers deal-driven.")
        if crm < CRM_FULL:
            out.append(f"{_lever('6.1')} is {_pkr(crm)}, reaching about "
                       f"{sqrt(max(crm, 0) / CRM_FULL):.0%} of the customers it could.")
        if str(d.get("4.1", "off")) != "off" and key == "repeat":
            out.append(f"Marketplace buyers ({_lever('4.1')}) are out of CRM's reach.")
    elif key == "nps":
        out.append(f"NPS {v:.0f}, rating {float(h.get('rating', 0) or 0):.2f}.")
        if float(h.get("cs_backlog", 0) or 0) > 0:
            out.append(f"Customer service is behind: {float(h['cs_backlog']):,.0f} tickets "
                       f"waiting with {_num(d, '10.1', 4):g} agents ({_lever('10.1')}).")
        if str(d.get("8.5", "basic")) == "basic":
            out.append(f"{_lever('8.5')} is basic.")
        if _num(d, "7.4") < QA_BEST:
            out.append(f"{_lever('7.4')} is {_pkr(_num(d, '7.4'))}.")
    elif key in ("gm", "cm_pre", "ebitda"):
        from .web.handbook import MEASURE_NAMES
        out.append(f"{MEASURE_NAMES[key]} {v:.1%} over the run.")
        if key == "gm" and disc > 0.10:
            out.append(f"A {_lever('2.2')} of {disc:.0%} comes straight off the margin.")
        if key == "cm_pre" and str(d.get("4.1", "off")) != "off":
            out.append(f"Marketplace sales ({_lever('4.1')}) pay a commission.")
        if key == "ebitda":
            rev = float(h.get("revenue_net", 0) or 0)
            mkt = float(h["pnl"].get("marketing", 0) or 0)
            if rev > 0:
                out.append(f"Marketing was {mkt / rev:.0%} of revenue last month.")
    elif key == "rev_multiple":
        out.append(f"Last month's revenue is {v:.2f}x the first month's.")
        if _num(d, "3.9") < 100_000:
            out.append(f"{_lever('3.9')} is {_pkr(_num(d, '3.9'))}: brand fades when it stops.")
    elif key == "share_pp":
        out.append(f"Market share {v:+.1f} points against the first month.")
    elif key == "order_growth":
        out.append(f"Orders {v:+.0%} against a baseline business, over the run.")
    elif key == "runway":
        if v >= 99:
            out.append("Not burning cash: counted as more than 16 months of runway, which "
                       "scores 30%. Cash is sitting idle that could fund growth.")
        elif v > 9:
            out.append(f"{v:.1f} months of runway: more idle cash than the band rewards.")
        else:
            out.append(f"{v:.1f} months of runway: short of the 3 to 9 months that score full "
                       f"marks.")
    elif key == "free_cash":
        out.append(f"The business generated {_pkr(v)} of its own cash.")
        if float(h.get("weeks_cover", 0) or 0) > 8:
            out.append(f"{float(h['weeks_cover']):.1f} weeks of stock tie cash up "
                       f"({_lever('7.1')}, {_lever('7.5')}).")
    elif key == "net_margin":
        out.append(f"Net margin {v:.1%} over the run.")
        if float(h.get("credit_drawn", 0) or 0) > 0:
            out.append(f"It owes the bank {_pkr(float(h['credit_drawn']))} at 22% a year.")
    elif key == "decisions":
        dd = h.get("decisions") or {}
        if dd.get("open"):
            out.append(f"Filled in {int(dd.get('taken', 0))} of {int(dd['open'])} decisions "
                       f"last month; full marks at three-quarters.")
    elif key == "memo":
        missing = sum(1 for x in team.history if not (x.get("decisions") or {}).get("memo"))
        if missing:
            out.append(f"No {_lever('12.5')} in {missing} of {len(team.history)} months.")
    return out


def where_the_points_are(team, params, all_teams: dict, cards: dict, standing: dict,
                         memo_rejected: set | None = None) -> str:
    """The console block for one team: pillars against the best in the room,
    and the biggest gaps with what to look at."""
    from .web import handbook as hb
    parts = scoring.breakdown(team, params, all_teams, memo_rejected)
    card = cards[team.team_id]
    rows = []
    for p, name, anchor in PILLARS:
        best = max(c[p] for c in cards.values())
        mx = sum(v["max"] for k, v in parts.items() if scoring.PILLAR_OF[k] == p)
        rows.append(f'<tr><td><a href="/admin/playbook#{anchor}">{escape(name)}</a></td>'
                    f'<td>{card[p]:.1f} / {mx:g}</td><td>{best:.1f}</td></tr>')
    gaps = sorted(((v["max"] - v["points"], k) for k, v in parts.items()), reverse=True)
    items = []
    for lost, key in gaps:
        if len(items) == SHOWN or lost < MIN_GAP:
            break
        part = parts[key]
        lines = _diagnose(key, team, params, standing, part)
        levers = ", ".join(_lever(c) for c in hb.levers_for(key, "+")) \
            or "every decision open to the team"
        items.append(
            f'<li><b>{escape(hb.MEASURE_NAMES[key])}</b>, {part["points"]:.1f} of '
            f'{part["max"]:g}. {" ".join(lines)}'
            f'<br><span class="lv">Levers: {levers}</span></li>')
    gaps_html = (f'<ol class="gaps">{"".join(items)}</ol>' if items
                 else '<p class="note">No measure is more than a quarter-point short.</p>')
    return ('<div class="coach"><b>Where the points are</b>'
            f' &middot; {card["total"]:.1f} of 100'
            '<table class="t res"><tr class="hd"><th>Pillar</th><th>Points</th>'
            f'<th>Best in room</th></tr>{"".join(rows)}</table>'
            f'<p class="sub-h">Biggest gaps, and what to look at</p>{gaps_html}'
            '<p class="rk-note">From the scorecard and this team\'s own decisions, for you '
            'to check before using. Teams do not see this.</p></div>')


CSS = """
.db .coach{margin:10px 0;padding:10px 12px;border-radius:6px;background:#fbf6ec;font-size:13.5px}
.db .coach table.t.res{max-width:420px}
.db .coach a{color:#2a78d6;text-decoration:none}
.db .coach .sub-h{margin:10px 0 4px;font-weight:600}
.db .coach ol.gaps{margin:0;padding-left:20px;display:grid;gap:6px;line-height:1.5}
.db .coach .lv{color:#52514e;font-size:12.5px}
"""
