"""Per-team round report.

One self-contained HTML file per team per round - no server, no build step, and
it opens on a phone. Mirrors the six dashboard blocks from
docs/10-kpi-dictionary.md, with biased and purchased metrics marked.
"""
from __future__ import annotations

from pathlib import Path

from .charts import CSS_TOKENS, sparkline

# (label, key, format, up_is_good). The last field is not decoration: a rising
# CAC and a rising debt balance are both bad news, and colouring them green
# tells a team the opposite of the truth.
BLOCKS = [
    ("Growth", [
        ("Net revenue", "revenue_net", "pkr", True), ("Orders", "orders", "int", True),
        ("Sessions", "sessions", "int", True),
        ("Conversion rate", "conversion_rate", "pct2", True),
        ("AOV", "aov_net", "pkr", True), ("Market share", "market_share", "pct1*", True),
    ]),
    ("Marketing", [
        ("Blended CAC", "cac_blended", "pkr", False),
        ("Reported ROAS", "roas_reported", "x!", True),
        ("Creative quality", "creative_quality", "score", True),
        ("New customers", "new_customers", "int", True),
    ]),
    ("Commercial", [
        ("Gross margin", "gross_margin_pct", "pct1", True),
        ("Contribution margin", "contribution_margin_pct", "pct1", True),
        ("EBITDA", "ebitda", "pkr", True),
        ("Discount rate", "discount_rate", "pct1", False),
    ]),
    ("Operations", [
        ("Service level", "service_level", "pct1", True),
        ("In-stock rate", "instock_rate", "pct1", True),
        ("Delivery success", "delivery_success", "pct1", True),
        ("RTO rate", "rto_rate", "pct1", False),
        ("Return rate", "return_rate", "pct1", False),
        ("Weeks of cover", "weeks_cover", "num1", True),
    ]),
    ("Customer", [
        ("Active customers", "active_customers", "int", True),
        ("Repeat order share", "repeat_order_share", "pct1", True),
        ("LTV : CAC", "ltv_cac_ratio", "num2", True), ("Rating", "rating", "num2", True),
        ("NPS", "nps", "int", True), ("Service backlog", "cs_backlog", "int", False),
    ]),
    ("Finance", [
        ("Cash", "cash_balance", "pkr", True),
        ("Runway (rounds)", "runway_rounds", "num1", True),
        ("COD in transit", "cod_receivable", "pkr", True),
        ("Credit drawn", "credit_drawn", "pkr", False),
        ("Net profit", "net_profit", "pkr", True),
    ]),
]

BINDING = {
    "under_marketing": ("Under-marketing",
                        "Your proposition was strong enough for more demand than you "
                        "reached. Not enough people saw it."),
    "wasted_spend": ("Wasted spend",
                     "You had plenty of traffic and a weaker proposition than rivals. "
                     "They took the demand."),
    "stock_out": ("Stock-out",
                  "Demand and traffic were both sufficient. You ran out of stock."),
    "balanced": ("Balanced", "Demand, traffic and stock were broadly in step."),
}


def _fmt(value, kind: str) -> str:
    if value is None:
        return "&mdash;"
    k = kind.rstrip("*!")
    try:
        if k == "pkr":
            return f"PKR {value:,.0f}"
        if k == "int":
            return f"{value:,.0f}"
        if k == "pct1":
            return f"{value * 100:.1f}%"
        if k == "pct2":
            return f"{value * 100:.2f}%"
        if k == "num1":
            return f"{value:.1f}"
        if k == "num2":
            return f"{value:.2f}"
        if k == "score":
            return f"{value:.2f}"
        if k == "x":
            return f"{value:.2f}x"
    except (TypeError, ValueError):
        return str(value)
    return str(value)


def _value(record: dict, key: str):
    if key in record:
        return record[key]
    return record.get("pnl", {}).get(key)


TREND_KEYS = {"revenue_net", "orders", "conversion_rate", "cac_blended",
              "contribution_margin_pct", "service_level", "rating",
              "repeat_order_share", "cash_balance", "active_customers"}


def render(team, round_: int, out_dir: str | Path, scorecard: dict | None = None) -> Path:
    record = team.history[round_ - 1]
    prior = team.history[round_ - 2] if round_ > 1 else None
    series = team.history[:round_]
    name = (team.brand_name
            or getattr(team.founding, "brand_name", None) or team.team_id)

    cards = []
    for title, metrics in BLOCKS:
        rows = []
        for label, key, kind, up_is_good in metrics:
            now = _value(record, key)
            was = _value(prior, key) if prior else None
            delta = ""
            if isinstance(now, (int, float)) and isinstance(was, (int, float)) and was:
                change = (now - was) / abs(was)
                if abs(change) >= 0.005:
                    cls = "up" if (change > 0) == up_is_good else "down"
                    delta = f'<span class="d {cls}">{change:+.0%}</span>'
            mark = ""
            if kind.endswith("!"):
                mark = '<abbr title="Platform-reported and over-attributed">*</abbr>'
            elif kind.endswith("*"):
                mark = '<abbr title="Requires a purchased study">&deg;</abbr>'
            trend = ""
            if key in TREND_KEYS and round_ >= 3:
                points = [_value(h, key) for h in series]
                trend = ('<tr class="tr"><td colspan="2">'
                         + sparkline(points, label=label,
                                     fmt=lambda v, k=kind: _fmt(v, k))
                         + "</td></tr>")
            rows.append(
                f"<tr><th>{label}{mark}</th><td>{_fmt(now, kind)}{delta}</td></tr>"
                + trend)
        cards.append(f'<section><h2>{title}</h2><table>{"".join(rows)}</table></section>')

    verdict, explanation = BINDING.get(
        record.get("binding_constraint", "balanced"), BINDING["balanced"])
    events = record.get("events") or []
    events_html = (f'<p class="ev"><strong>Events this round:</strong> '
                   f'{", ".join(events)}</p>') if events else ""
    score_html = ""
    if scorecard:
        score_html = (
            '<p class="ev"><strong>Scorecard to date:</strong> '
            + " &middot; ".join(
                f"{k.upper()} {v:.1f}" for k, v in scorecard.items()
                if k.startswith("p")) + f' &middot; <strong>Total '
            f'{scorecard["total"]:.1f}</strong></p>')

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name} &mdash; Round {round_}</title><style>
*{{box-sizing:border-box}}
body{{font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
margin:0;padding:24px 16px;background:#f6f7f9;color:#1a1d21}}
.wrap{{max-width:1040px;margin:0 auto}}
h1{{font-size:24px;margin:0 0 2px}}
.sub{{color:#666;margin:0 0 20px;font-size:14px}}
.grid{{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(270px,1fr))}}
section{{background:#fff;border:1px solid #e3e6ea;border-radius:10px;padding:14px 16px}}
h2{{font-size:12px;letter-spacing:.09em;text-transform:uppercase;color:#6b7280;
margin:0 0 10px;font-weight:600}}
table{{width:100%;border-collapse:collapse}}
th{{text-align:left;font-weight:400;color:#4b5563;padding:5px 0;font-size:14px}}
td{{text-align:right;font-variant-numeric:tabular-nums;padding:5px 0;font-weight:600}}
.d{{font-size:11px;margin-left:7px;font-weight:600}}
.up{{color:#047857}} .down{{color:#b91c1c}}
abbr{{color:#9ca3af;text-decoration:none;cursor:help}}
.tr td{{padding:0 0 6px}} .spark{{display:block;overflow:visible}}
.verdict{{background:#fff;border:1px solid #e3e6ea;border-left:3px solid #1a1d21;
border-radius:10px;padding:14px 16px;margin:0 0 14px}}
.verdict h3{{margin:0 0 4px;font-size:15px}} .verdict p{{margin:0;color:#4b5563}}
.ev{{margin:12px 0 0;color:#4b5563;font-size:14px}}
{CSS_TOKENS}
footer{{color:#9ca3af;font-size:12px;margin-top:20px}}
@media(prefers-color-scheme:dark){{
body{{background:#101215;color:#e8eaed}}
section,.verdict{{background:#191c20;border-color:#2b3036}}
.verdict{{border-left-color:#e8eaed}}
th,.verdict p,.ev{{color:#9aa3ad}} h2{{color:#7d8794}}}}
</style></head><body class="viz"><div class="wrap">
<h1>{name}</h1>
<p class="sub">Round {round_} results &middot; {team.team_id}</p>
<div class="verdict"><h3>{verdict}</h3><p>{explanation}</p>{events_html}{score_html}</div>
<div class="grid">{"".join(cards)}</div>
<footer>* platform-reported, over-attributed &nbsp;&middot;&nbsp;
&deg; requires a purchased study</footer>
</div></body></html>"""

    out = Path(out_dir) / f"report_{team.team_id}_r{round_}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return out
