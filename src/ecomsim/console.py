"""Instructor console - one HTML file per round.

What an instructor needs between rounds: who is where and why, which teams are
about to trip a conditional event, and the evidence for the debrief. The
leaderboard is withheld until Round 4 (docs/08) so teams settle on a strategy
before anchoring on rivals.
"""
from __future__ import annotations

from html import escape
from pathlib import Path

from . import scoring
from .charts import CSS_TOKENS, rank_bars, small_multiple

LEADERBOARD_FROM_ROUND = 4

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

PANELS = [
    ("Net revenue", "revenue_net", lambda v: f"{v/1e6:,.2f}M", True),
    ("Orders", "orders", lambda v: f"{v:,.0f}", True),
    ("Contribution margin", "contribution_margin_pct", lambda v: f"{v:.1%}", True),
    ("Cash", "cash_balance", lambda v: f"{v/1e6:,.2f}M", True),
    ("Repeat share", "repeat_order_share", lambda v: f"{v:.0%}", True),
    ("Service level", "service_level", lambda v: f"{v:.0%}", True),
    ("CAC", "cac_blended", lambda v: f"{v:,.0f}", False),
    ("Rating", "rating", lambda v: f"{v:.2f}", True),
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


def render(world, params, out_dir: str | Path) -> Path:
    round_ = world.round
    teams = list(world.teams.values())
    cards = {t.team_id: scoring.final_score(t, params, world.teams) for t in teams}
    ranked = sorted(teams, key=lambda t: -cards[t.team_id]["total"])

    def name_of(t):
        return getattr(t.founding, "brand_name", None) or t.team_id

    # Leaderboard
    if round_ >= LEADERBOARD_FROM_ROUND:
        bars = rank_bars([(name_of(t), cards[t.team_id]["total"]) for t in ranked],
                         fmt=lambda v: f"{v:.1f}")
        weight = round_ * (round_ + 1) / 2 / (12 * 13 / 2)
        board = (f'<section class="wide"><h2>Leaderboard</h2>{bars}'
                 f'<p class="note">Rounds so far carry {weight:.0%} of the total '
                 f'weight — later rounds count more, so standings will move.</p>'
                 f'{_table(ranked, cards, name_of)}</section>')
    else:
        board = ('<section class="wide"><h2>Leaderboard</h2>'
                 f'<p class="note">Withheld until Round {LEADERBOARD_FROM_ROUND}, '
                 'so teams settle on a strategy before anchoring on rivals '
                 '(docs/08).</p></section>')

    # Per-team small multiples
    blocks = []
    for t in ranked:
        hist = t.history
        panels = "".join(
            small_multiple(label, [h.get(key) for h in hist],
                           hist[-1].get(key, 0), fmt, good_up)
            for label, key, fmt, good_up in PANELS)
        misses = _near_misses(t, params)
        flags = ""
        if misses:
            flags = ('<p class="flag"><strong>Near a conditional trigger:</strong> '
                     + "; ".join(escape(m) for m in misses) + "</p>")
        h = hist[-1]
        if h["insolvent"]:
            flags += '<p class="flag crit"><strong>In administration.</strong></p>'
        rank = ranked.index(t) + 1
        label = escape(name_of(t))
        ident = "" if name_of(t) == t.team_id else f'<span class="tid">{t.team_id}</span> '
        blocks.append(
            f'<section class="wide"><h2>{rank}. {label} {ident}'
            f'<span class="tid">&middot; {escape(h["binding_constraint"].replace("_", " "))}'
            f'</span></h2>{flags}<div class="sms">{panels}</div></section>')

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
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
table.t{{width:100%;border-collapse:collapse;margin-top:10px;font-size:13px}}
table.t th,table.t td{{text-align:right;padding:5px 7px;
border-bottom:1px solid #e1e0d9;font-variant-numeric:tabular-nums}}
table.t th:first-child,table.t td:first-child{{text-align:left}}
table.t thead th{{color:#52514e;font-weight:600}}
@media(prefers-color-scheme:dark){{
body{{background:#0d0d0d;color:#fff}}
section{{background:#1a1a19;border-color:rgba(255,255,255,.10)}}
h2,.sub,figcaption,.note,summary,.flag{{color:#c3c2b7}}
.sm .v{{color:#fff}} .bars .bl{{fill:#c3c2b7}} .bars .bv{{fill:#fff}}
table.t th,table.t td{{border-color:#2c2c2a}} table.t thead th{{color:#c3c2b7}}
.up{{color:#0ca30c}}}}
{CSS_TOKENS}
</style></head><body class="viz"><div class="wrap">
<h1>Round {round_}</h1>
<p class="sub">Instructor console &middot; {len(teams)} teams &middot;
config {params.config_hash()}</p>
{board}{"".join(blocks)}
</div></body></html>"""

    out = Path(out_dir) / f"console_r{round_}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out


def _table(ranked, cards, name_of) -> str:
    """The table view every chart owes its reader."""
    head = ("<tr><th>Team</th><th>Total</th><th>P1</th><th>P2</th><th>P3</th>"
            "<th>P4</th><th>P5</th><th>Revenue</th><th>Cash</th></tr>")
    rows = []
    for t in ranked:
        c, h = cards[t.team_id], t.history[-1]
        rows.append(
            f'<tr><td>{escape(name_of(t))}</td><td><strong>{c["total"]:.1f}</strong></td>'
            f'<td>{c["p1"]:.1f}</td><td>{c["p2"]:.1f}</td><td>{c["p3"]:.1f}</td>'
            f'<td>{c["p4"]:.1f}</td><td>{c["p5"]:.1f}</td>'
            f'<td>{h["revenue_net"]/1e6:,.2f}M</td>'
            f'<td>{h["cash_balance"]/1e6:,.2f}M</td></tr>')
    return (f'<details><summary>Table view</summary><table class="t">'
            f'<thead>{head}</thead><tbody>{"".join(rows)}</tbody></table></details>')
