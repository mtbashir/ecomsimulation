"""Instructor console - one HTML file per round.

What an instructor needs between rounds: who is where and why, which teams are
about to trip a conditional event, and the evidence for the debrief. The
leaderboard is here from Round 1; teams see rankings only once the instructor
publishes them (from Round 4 by default, docs/08), so they settle on a strategy
before anchoring on rivals.
"""
from __future__ import annotations

from html import escape
from pathlib import Path

from . import coach, debrief, scoring
from .charts import CSS_TOKENS, rank_bars


# Conditional (Type B) events fire from a team's own state. Logging near-misses
# lets the thresholds be calibrated before they are switched on (docs/09).
TRIGGERS = [
    ("Review crisis", "rating", 3.6, "below"),
    ("Stock-out ranking penalty", "instock_rate", 0.75, "below"),
    ("Service collapse", "cs_backlog", 1.0, "above_capacity"),
    ("Supplier terms withdrawn", "credit_drawn", 0.80, "above_ceiling"),
    ("Marketplace suspension", "return_rate", 0.20, "above"),
    ("Loyalty flywheel", "repeat_order_share", 0.35, "above"),
]



def _near_misses(team, params) -> list[str]:
    """Teams within 10% of a conditional trigger, so thresholds can be tuned."""
    h = team.history[-1]
    out = []
    for name, key, threshold, direction in TRIGGERS:
        value = h.get(key)
        if value is None:
            continue
        if direction == "above_ceiling":
            value = value / max(params["credit_ceiling"], 1.0)
            direction = "above"
        elif direction == "above_capacity":
            capacity = max(team.cs_agents * params["agent_capacity"], 1.0)
            value, direction = value / capacity, "above"
        if direction == "below" and threshold < value <= threshold * 1.10:
            out.append(f"{name} ({value:.2f} vs {threshold})")
        elif direction == "above" and threshold * 0.90 <= value < threshold:
            out.append(f"{name} ({value:.2f} vs {threshold})")
    return out


def _targeting(ranked, params, name_of) -> str:
    """How well each team aimed its ad budgets this month, and the answer key.

    For the debrief: which teams read their buyers right, channel by channel,
    and - folded away until the instructor wants it - who really buys each
    product and the mistake the room usually makes."""
    from . import targeting as T

    rows = []
    for t in ranked:
        camps = t.history[-1].get("campaigns") or []
        cells = []
        for ch in T.CHANNELS:
            mine = [c for c in camps if c["channel"] == ch]
            spend = sum(c["spend"] for c in mine)
            if not mine or spend <= 0:
                cells.append("<td>&mdash;</td>")
                continue
            if len(mine) == 1 and mine[0]["name"].startswith("Broad"):
                cells.append('<td class="mute">broad</td>')
                continue
            lift = sum(c["lift"] * c["spend"] for c in mine) / spend
            cls = "up" if lift > 0.005 else "down" if lift < -0.005 else ""
            cells.append(f'<td class="{cls}">{lift:+.0%} &middot; {len(mine)}</td>')
        rows.append(f'<tr><td>{escape(name_of(t))}</td>{"".join(cells)}</tr>')
    key = "".join(
        f'<tr><td>{escape(str(d["name"]))}</td><td>{escape(d["age"])}</td>'
        f'<td>{d["women"]:.0%}</td><td>{escape(d["where"])}</td>'
        f'<td>{escape(d["interests"])}</td><td>{escape(d["language"])} &middot; '
        f'{escape(d["format"])}</td><td>{escape(d["channels"])}</td>'
        f'<td class="l">{escape(d["mistake"])}</td></tr>'
        for d in (T.debrief(params, a["code"]) for a in params.audiences))
    return (
        '<section class="wide"><h2>Campaigns &middot; how each budget was aimed</h2>'
        '<table class="t"><thead><tr><th>Team</th>'
        + "".join(f"<th>{T.CHANNEL_NAMES[c]}</th>" for c in T.CHANNELS)
        + '</tr></thead><tbody>' + "".join(rows) + '</tbody></table>'
        '<p class="note">Each rupee against one broad campaign, weighted by spend, '
        'then the number of campaigns. Broad is exactly zero.</p>'
        '<details><summary>Answer key: who buys each product</summary>'
        '<table class="t key"><thead><tr><th>Product</th><th>Age</th><th>Women</th>'
        '<th>Where</th><th>Interests</th><th>Message</th><th>Channels</th>'
        '<th>The usual mistake</th></tr></thead><tbody>' + key +
        '</tbody></table></details></section>')


def _grid(record: dict | None) -> tuple[dict, dict]:
    """One team-month's orders asked for and sales value, by product and segment.

    Orders asked for are the orders served plus those lost to stock-outs,
    shared across products by the units each was asked for, then across
    segments by who buys that product (`buyers`). Sales value is what was
    actually sold, split the same way."""
    orders, value = {}, {}
    if not record:
        return orders, value
    lines = record.get("products") or []
    asked = record.get("orders", 0.0) + record.get("lost_to_stockout", 0.0)
    units = sum(r.get("wanted", 0.0) for r in lines) or 1.0
    for r in lines:
        share = r.get("wanted", 0.0) / units
        for seg, b in (r.get("buyers") or {}).items():
            key = (r["code"], seg)
            orders[key] = orders.get(key, 0.0) + asked * share * b
            value[key] = value.get(key, 0.0) + r.get("net_sales", 0.0) * b
    return orders, value


def _market(teams, params) -> str:
    """Market size: every store's orders by product and customer segment this
    month, against last month. For the instructor - teams never see segments."""
    def total(back: int):
        o, v = {}, {}
        for t in teams:
            rec = t.history[-1 - back] if len(t.history) > back else None
            go, gv = _grid(rec)
            for k, x in go.items():
                o[k] = o.get(k, 0.0) + x
            for k, x in gv.items():
                v[k] = v.get(k, 0.0) + x
        return o, v

    (now_o, now_v), (was_o, was_v) = total(0), total(1)
    if not now_o:
        return ""
    segs = [(s["code"], s["name"]) for s in params.segments]
    codes = {c for c, _ in now_o}
    skus = [s for s in params.skus if s["code"] in codes]

    def change(now, was):
        if not was:
            return ""
        d = now / was - 1
        cls = "up" if d > 0.005 else "down" if d < -0.005 else "mute"
        return f' <small class="{cls}">{d:+.0%}</small>'

    def table(now, was, fmt, label):
        def cell(n, w, row=0.0):
            share = f' <small class="sh">{n / row:.0%}</small>' if row > 0 else ""
            return f"<td>{fmt(n)}{change(n, w)}{share}</td>"
        head = ("<tr><th>Product</th>" + "".join(f"<th>{escape(n)}</th>" for _, n in segs)
                + "<th>Total</th></tr>")
        body, cat = [], None
        for s in skus:
            if s["category"] != cat:
                cat = s["category"]
                body.append(f'<tr class="grp"><td colspan="{len(segs) + 2}">'
                            f'{escape(cat.title())}</td></tr>')
            c = s["code"]
            n_row = sum(now.get((c, k), 0.0) for k, _ in segs)
            w_row = sum(was.get((c, k), 0.0) for k, _ in segs)
            body.append(f"<tr><td>{escape(s['name'])}</td>"
                        + "".join(cell(now.get((c, k), 0.0), was.get((c, k), 0.0), n_row)
                                  for k, _ in segs)
                        + f'<td class="top">{fmt(n_row)}{change(n_row, w_row)}</td></tr>')
        n_col = {k: sum(now.get((c, k), 0.0) for c in codes) for k, _ in segs}
        w_col = {k: sum(was.get((c, k), 0.0) for c in codes) for k, _ in segs}
        n_all, w_all = sum(n_col.values()), sum(w_col.values())
        body.append('<tr class="tot"><td>All products</td>'
                    + "".join(f"<td>{fmt(n_col[k])}{change(n_col[k], w_col[k])}</td>"
                              for k, _ in segs)
                    + f"<td>{fmt(n_all)}{change(n_all, w_all)}</td></tr>")
        body.append('<tr class="mix"><td>Share of orders</td>'
                    + "".join(f"<td>{n_col[k] / (n_all or 1):.0%}</td>" for k, _ in segs)
                    + "<td>100%</td></tr>")
        return (f'<div class="gridwrap"><table class="t grid" aria-label="{label}">'
                f"<thead>{head}</thead><tbody>{''.join(body)}</tbody></table></div>")

    def by_segment():
        n_col = {k: sum(v for (c, s), v in now_o.items() if s == k) for k, _ in segs}
        w_col = {k: sum(v for (c, s), v in was_o.items() if s == k) for k, _ in segs}
        n_all, w_all = sum(n_col.values()) or 1.0, sum(w_col.values())
        rows = []
        for k, name in sorted(segs, key=lambda s: -n_col[s[0]]):
            sh = n_col[k] / n_all
            pts = ""
            if w_all:
                d = round((sh - w_col[k] / w_all) * 100, 1) + 0.0   # no -0.0
                cls = "up" if d > 0.05 else "down" if d < -0.05 else "mute"
                pts = f' <small class="{cls}">{d:+.1f} pts</small>'
            rows.append(f"<tr><td>{escape(name)}</td><td>{n_col[k]:,.0f}</td>"
                        f"<td>{change(n_col[k], w_col[k]).strip() or '&mdash;'}</td>"
                        f"<td>{sh:.0%}{pts}</td></tr>")
        rows.append(f'<tr class="tot"><td>All segments</td><td>{sum(n_col.values()):,.0f}</td>'
                    f"<td>{change(sum(n_col.values()), w_all).strip() or '&mdash;'}</td>"
                    "<td>100%</td></tr>")
        return ('<table class="t grid seg" aria-label="Orders by segment"><thead><tr>'
                "<th>Segment</th><th>Orders</th><th>Change on last month</th>"
                "<th>Share of orders</th></tr></thead><tbody>" + "".join(rows)
                + "</tbody></table>")

    return (
        '<section class="wide"><h2>Market size &middot; orders by product and segment</h2>'
        + by_segment()
        + '<p class="note">Orders asked for by each customer segment this month, its change '
        'on last month, and its share of all orders (the small figure: the move in share, '
        'in points).</p>'
        + table(now_o, was_o, lambda v: f"{v:,.0f}", "Orders asked for")
        + '<p class="note">Orders asked for across every team&rsquo;s store this month '
        '(orders served plus those lost to stock-outs), split across products by the '
        'units each was asked for and across segments by who buys that product. In each '
        'cell: orders, the change on last month, and in grey the segment&rsquo;s share of '
        'that product&rsquo;s orders. A product only counts where a team sells it; '
        'incumbent brands are not included.</p>'
        '<details><summary>The same grid in sales value (PKR, what was sold)</summary>'
        + table(now_v, was_v, lambda v: f"{v / 1e6:,.2f}M" if v >= 1e6 else f"{v / 1e3:,.0f}k",
                "Sales value")
        + '</details></section>')


def render(world, params, out_dir: str | Path, submissions: dict | None = None,
           open_codes: list[str] | None = None, workbook_url=None,
           workbooks_zip: str | None = None, memo_rejected: set | None = None,
           memo_url=None, footer: str = "", seen_by_teams: str = "",
           total_rounds: int = 12, by_round: list[dict] | None = None,
           round_urls: list[tuple[int, str]] | None = None) -> Path:
    round_ = world.round
    teams = list(world.teams.values())
    cards = {t.team_id: scoring.final_score(t, params, world.teams, memo_rejected)
             for t in teams}
    months = {t.team_id: scoring.month_score(t, params, world.teams, round_, memo_rejected)
              for t in teams}
    ranked = sorted(teams, key=lambda t: -cards[t.team_id]["total"])

    def name_of(t):
        return (t.brand_name
                or getattr(t.founding, "brand_name", None) or t.team_id)

    # Leaderboard: the cumulative score, from Round 1. Whether the teams see it
    # is the instructor's call, made on the admin page.
    bars = rank_bars([(name_of(t), cards[t.team_id]["total"]) for t in ranked],
                     fmt=lambda v: f"{v:.1f}")
    weight = round_ * (round_ + 1) / 2 / (total_rounds * (total_rounds + 1) / 2)
    seen = f' <b>{escape(seen_by_teams)}</b>' if seen_by_teams else ""
    board = (f'<section class="wide"><h2>Leaderboard &middot; cumulative</h2>{bars}'
             f'<p class="note">Rounds so far carry {weight:.0%} of the total '
             f'weight — later rounds count more, so standings will move.{seen}</p>'
             f'{_table(ranked, cards, name_of, months)}</section>')

    # Where each team's points went, and which of its decisions to look at:
    # for the instructor only, beside that team's debrief.
    coaching = {}
    if submissions is not None:
        for t in teams:
            standing = {**(getattr(t, "standing", None) or {}),
                        **(submissions.get(t.team_id) or {})}
            coaching[t.team_id] = coach.where_the_points_are(
                t, params, world.teams, cards, standing, memo_rejected)

    # Warnings that used to sit on the per-team KPI panels now go into each
    # team's debrief, where the instructor reads about that team anyway.
    flags = {}
    for t in ranked:
        notes = [f"Near a conditional trigger: {m}." for m in _near_misses(t, params)]
        if t.history[-1]["insolvent"]:
            notes.insert(0, "In administration: cash ran out and the credit line is full.")
        flags[t.team_id] = notes

    # Without submissions there is no debrief to carry the warnings, so list
    # them on their own (the file runner and the demo).
    watch = ""
    if submissions is None and any(flags.values()):
        items = "".join(
            f"<li><b>{escape(name_of(t))}</b>: {' '.join(escape(n) for n in flags[t.team_id])}</li>"
            for t in ranked if flags[t.team_id])
        watch = f'<section class="wide"><h2>Trigger watch</h2><ul class="note">{items}</ul></section>'

    downloads = ""
    if workbook_url:
        links = "".join(
            f'<a class="wbk" href="{escape(workbook_url(t.team_id))}">{escape(name_of(t))}'
            f'{"" if name_of(t) == t.team_id else f" <span class=tid>{t.team_id}</span>"}</a>'
            for t in ranked)
        every = (f'<a class="wbk all" href="{escape(workbooks_zip)}">All teams (.zip)</a>'
                 if workbooks_zip else "")
        downloads = (
            '<section class="wide"><h2>Results workbooks &middot; for review</h2>'
            f'<div class="wbks">{every}{links}</div>'
            f'<p class="note">Every month to round {round_} as Excel, one workbook per team: '
            'P&amp;L, KPIs as formulas, sales and stock by product, cash, campaigns and '
            'customer segments. Teams cannot download these.</p></section>')

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<link rel="icon" href="/static/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/static/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/static/apple-touch-icon.png">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Instructor console &mdash; Round {round_}</title><style>
*{{box-sizing:border-box}}
body{{font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;
padding:24px 16px;background:#f9f9f7;color:#0b0b0b}}
.wrap{{max-width:1080px;margin:0 auto}}
h1{{font-size:24px;margin:0 0 2px}}
.sub{{color:#52514e;margin:0 0 20px;font-size:14px}}
section{{background:#fcfcfb;border:1px solid rgba(11,11,11,.10);border-radius:10px;
padding:16px;margin:0 0 14px}}
h2{{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:#52514e;
margin:0 0 12px;font-weight:600}}
.tid{{text-transform:none;letter-spacing:0;color:#898781;font-weight:400}}
.sms{{display:grid;gap:14px 18px;grid-template-columns:repeat(4,1fr)}}
@media(max-width:820px){{.sms{{grid-template-columns:repeat(2,1fr)}}}}
figure.sm{{margin:0}}
figcaption{{font-size:12px;color:#52514e;margin:0 0 2px}}
.sm .v{{font:600 19px/1.2 inherit;color:#0b0b0b}}
.dl{{font-size:11px;margin-left:6px;font-weight:600}}
.up{{color:#006300}} .down{{color:#d03b3b}}
.spark{{display:block;margin-top:2px;overflow:visible}}
.bars text{{font:12px system-ui,sans-serif}}
.bars .bl{{fill:#52514e}} .bars .bv{{fill:#0b0b0b;font-weight:600;
font-variant-numeric:tabular-nums}}
.note{{color:#52514e;font-size:13px;margin:10px 0 0}}
.flag{{background:rgba(250,178,25,.13);border-left:3px solid #fab219;
padding:8px 10px;border-radius:5px;margin:0 0 12px;font-size:13px;color:#52514e}}
.flag.crit{{background:rgba(208,59,59,.12);border-left-color:#d03b3b}}
details{{margin-top:12px}} summary{{cursor:pointer;font-size:13px;color:#52514e}}
.ver{{margin-top:26px;font-family:ui-monospace,Menlo,monospace;font-size:11.5px}}
.wbks{{display:flex;flex-wrap:wrap;gap:8px}}
.wbk{{display:inline-block;padding:6px 11px;border:1px solid #d6d5ce;border-radius:7px;
background:#fff;color:#2a78d6;font-size:13px;font-weight:600;text-decoration:none}}
.wbk.all{{background:#2a78d6;border-color:#2a78d6;color:#fff}}
.wbk .tid{{font-weight:400}}
.rnav{{display:flex;flex-wrap:wrap;gap:6px;margin:-8px 0 18px}}
.rnav a,.rnav span{{padding:4px 11px;border:1px solid #d6d5ce;border-radius:7px;background:#fff;
color:#2a78d6;font-size:13px;font-weight:600;text-decoration:none}}
.rnav span{{background:#0b0b0b;border-color:#0b0b0b;color:#fff}}
table.t td.top{{font-weight:700}}
table.t td small{{color:#898781;font-weight:400}}
table.t{{width:100%;border-collapse:collapse;margin-top:10px;font-size:13px}}
table.t th,table.t td{{text-align:right;padding:5px 7px;
border-bottom:1px solid #e1e0d9;font-variant-numeric:tabular-nums}}
table.t th:first-child,table.t td:first-child{{text-align:left}}
table.t thead th{{color:#52514e;font-weight:600}}
table.t td.mute{{color:#898781}}
.gridwrap{{overflow-x:auto}}
table.t.grid td small{{font-size:11px;margin-left:3px}}
table.t.grid small.up{{color:#006300}} table.t.grid small.down{{color:#d03b3b}}
table.t.grid small.mute{{color:#898781}}
table.t.grid small.sh{{color:#898781;display:block;font-size:10.5px;line-height:1.1}}
table.t.seg{{max-width:620px}} table.t.seg td small{{display:inline}}
table.t.grid tr.grp td{{text-align:left;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:#52514e;padding-top:10px;font-weight:600}}
table.t.grid tr.tot td{{font-weight:700;border-top:2px solid #c9c8c0}}
table.t.grid tr.mix td{{color:#52514e}}
table.t.key th,table.t.key td{{text-align:left;font-size:12px;vertical-align:top}}
table.t.key td.l{{min-width:240px}}
@media(prefers-color-scheme:dark){{
body{{background:#0d0d0d;color:#fff}}
section{{background:#1a1a19;border-color:rgba(255,255,255,.10)}}
h2,.sub,figcaption,.note,summary,.flag{{color:#c3c2b7}}
.sm .v{{color:#fff}} .bars .bl{{fill:#c3c2b7}} .bars .bv{{fill:#fff}}
table.t th,table.t td{{border-color:#2c2c2a}} table.t thead th{{color:#c3c2b7}}
.rnav a{{background:#1a1a19;border-color:#2c2c2a;color:#3987e5}}
.rnav span{{background:#fff;border-color:#fff;color:#0b0b0b}}
.up{{color:#0ca30c}}}}
{CSS_TOKENS}
{debrief.CSS}
{coach.CSS}
</style></head><body class="viz"><div class="wrap">
<h1>Round {round_}</h1>
{_round_nav(round_urls, round_)}
<p class="sub">Instructor console &middot; {len(teams)} teams &middot;
config {params.config_hash()}</p>
{downloads}{board}{_by_round(ranked, name_of, by_round)}{debrief.section(ranked, params, submissions, open_codes or [], name_of, {k: v['total'] for k, v in cards.items()}, flags, workbook_url, memo_rejected, memo_url, coaching)}{watch}{_targeting(ranked, params, name_of)}{_market(ranked, params)}
{f'<p class="note ver">{escape(footer)}</p>' if footer else ''}
</div></body></html>"""

    out = Path(out_dir) / f"console_r{round_}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    # Headings in Title Case, as on every page of the app (web/titlecase.py).
    from .web.titlecase import html as title_case
    out.write_text(title_case(html), encoding="utf-8")
    return out


def _round_nav(round_urls, round_) -> str:
    """Links to every round's console, this one marked."""
    if not round_urls or len(round_urls) < 2:
        return ""
    links = "".join(f'<span>Round {r}</span>' if r == round_
                    else f'<a href="{escape(url)}">Round {r}</a>' for r, url in round_urls)
    return f'<nav class="rnav" aria-label="Every round\'s console">{links}</nav>'


# Measures shown round by round: (label, read from a month's record, format).
BY_ROUND = [
    ("Net revenue", lambda h: h["revenue_net"], lambda v: f"{v / 1e6:,.2f}M"),
    ("Contribution after marketing", lambda h: h["pnl"]["contribution"],
     lambda v: f"{v / 1e6:,.2f}M"),
    ("Orders", lambda h: h["orders"], lambda v: f"{v:,.0f}"),
    ("Market share", lambda h: h["market_share"], lambda v: f"{v:.1%}"),
    ("Cash at month end", lambda h: h["cash_balance"], lambda v: f"{v / 1e6:,.2f}M"),
]


def _by_round(ranked, name_of, by_round) -> str:
    """Every team, round by round: the cumulative standing as it stood at the
    end of each round, each round on its own, and the month's main results.
    Rows in today's cumulative order; the best in each round is in bold."""
    months = [m["month"] for m in by_round or []]
    if not months:
        return ""
    head = "<tr><th>Team</th>" + "".join(f"<th>R{m}</th>" for m in months) + "</tr>"
    cell = {(r["team_id"], m["month"]): r for m in by_round for r in m["rows"]}

    def standing(score_key, rank_key):
        rows = []
        for t in ranked:
            tds = []
            for m in months:
                r = cell.get((t.team_id, m))
                tds.append("<td>&mdash;</td>" if r is None else
                           f'<td class="{"top" if r[rank_key] == 1 else ""}">{r[rank_key]} '
                           f'<small>&middot; {r[score_key]:.1f}</small></td>')
            rows.append(f"<tr><td>{escape(name_of(t))}</td>{''.join(tds)}</tr>")
        return f'<table class="t"><thead>{head}</thead><tbody>{"".join(rows)}</tbody></table>'

    def measure(read, fmt):
        rows = []
        best = {m: max((read(t.history[m - 1]) for t in ranked if len(t.history) >= m),
                       default=None) for m in months}
        for t in ranked:
            tds = []
            for m in months:
                if len(t.history) < m:
                    tds.append("<td>&mdash;</td>")
                    continue
                v = read(t.history[m - 1])
                tds.append(f'<td class="{"top" if v == best[m] else ""}">{fmt(v)}</td>')
            rows.append(f"<tr><td>{escape(name_of(t))}</td>{''.join(tds)}</tr>")
        return f'<table class="t"><thead>{head}</thead><tbody>{"".join(rows)}</tbody></table>'

    parts = [
        f'<details open><summary>Cumulative rank &middot; score, as it stood at the end of '
        f'each round</summary>{standing("score", "rank")}</details>',
        f'<details><summary>Each round on its own: rank &middot; score</summary>'
        f'{standing("month_score", "month_rank")}</details>']
    parts += [f'<details><summary>{label}</summary>{measure(read, fmt)}</details>'
              for label, read, fmt in BY_ROUND]
    return ('<section class="wide"><h2>Results by round</h2>'
            + "".join(parts)
            + '<p class="note">Teams in today\'s cumulative order; the best in each round in '
              'bold. The round on its own applies the published scorecard to that month '
              'alone (docs/08); it is not added to the final score.</p></section>')


def _table(ranked, cards, name_of, months=None) -> str:
    """The table view every chart owes its reader, with this month on its own."""
    months = months or {}
    month_rank = scoring.ranks({tid: m["total"] for tid, m in months.items()})
    head = ("<tr><th>Team</th><th>Total</th><th>P1</th><th>P2</th><th>P3</th>"
            "<th>P4</th><th>P5</th><th>P6</th>"
            + ("<th>This month</th><th>Month rank</th>" if months else "")
            + "<th>Revenue</th><th>Cash</th></tr>")
    rows = []
    for t in ranked:
        c, h = cards[t.team_id], t.history[-1]
        m = months.get(t.team_id)
        rows.append(
            f'<tr><td>{escape(name_of(t))}</td><td><strong>{c["total"]:.1f}</strong></td>'
            f'<td>{c["p1"]:.1f}</td><td>{c["p2"]:.1f}</td><td>{c["p3"]:.1f}</td>'
            f'<td>{c["p4"]:.1f}</td><td>{c["p5"]:.1f}</td><td>{c["p6"]:.1f}</td>'
            + (f'<td>{m["total"]:.1f}</td><td>{month_rank[t.team_id]}</td>' if m else "")
            + f'<td>{h["revenue_net"]/1e6:,.2f}M</td>'
            f'<td>{h["cash_balance"]/1e6:,.2f}M</td></tr>')
    return (f'<details open><summary>Table view &middot; this month on its own beside the '
            f'cumulative score</summary><table class="t">'
            f'<thead>{head}</thead><tbody>{"".join(rows)}</tbody></table></details>')
