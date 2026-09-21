"""Inline SVG chart primitives - no libraries, no build step.

Colours come from a validated palette (dataviz reference instance). The ordinal
blue ramp below cleared the six checks in both modes at these exact steps; if
you re-step it, re-run the validator rather than eyeballing it.

Every form here carries ONE series per frame, so identity is never encoded in
colour and no legend is needed - the label names the series. That is also why
small multiples are safe: the all-pairs series cap never binds.
"""
from __future__ import annotations

from html import escape

# Ordinal ramp, light->dark. Validated --ordinal in both modes.
RAMP_LIGHT = ["#86b6ef", "#3987e5", "#256abf", "#104281"]
RAMP_DARK = ["#184f95", "#256abf", "#3987e5", "#86b6ef"]

CSS_TOKENS = """
.viz{--surface:#fcfcfb;--ink:#0b0b0b;--ink-2:#52514e;--muted:#898781;
--grid:#e1e0d9;--axis:#c3c2b7;--accent:#2a78d6;--trend:#898781;
--good:#006300;--bad:#d03b3b;--r1:#86b6ef;--r2:#3987e5;--r3:#256abf;--r4:#104281}
@media(prefers-color-scheme:dark){:root:where(:not([data-theme="light"])) .viz{
--surface:#1a1a19;--ink:#fff;--ink-2:#c3c2b7;--muted:#898781;
--grid:#2c2c2a;--axis:#383835;--accent:#3987e5;--trend:#898781;
--good:#0ca30c;--bad:#d03b3b;--r1:#184f95;--r2:#256abf;--r3:#3987e5;--r4:#86b6ef}}
:root[data-theme="dark"] .viz{--surface:#1a1a19;--ink:#fff;--ink-2:#c3c2b7;
--muted:#898781;--grid:#2c2c2a;--axis:#383835;--accent:#3987e5;--trend:#898781;
--good:#0ca30c;--bad:#d03b3b;--r1:#184f95;--r2:#256abf;--r3:#3987e5;--r4:#86b6ef}
"""


def sparkline(values: list[float], width: int = 104, height: int = 28,
              label: str = "", fmt=lambda v: f"{v:,.0f}") -> str:
    """A 12-point trend in the de-emphasis hue, current point in the accent.

    Marker on the last point only - a number on every point is noise, and the
    reader's question is "where is it now, and which way has it been going".
    """
    pts = [v for v in values if v is not None][-12:]
    if len(pts) < 2:
        return f'<svg class="spark" width="{width}" height="{height}" role="img"></svg>'

    lo, hi = min(pts), max(pts)
    span = (hi - lo) or abs(hi) or 1.0
    pad = 4
    x_step = (width - pad * 2) / (len(pts) - 1)

    def xy(i: int, v: float) -> tuple[float, float]:
        return (pad + i * x_step,
                height - pad - (v - lo) / span * (height - pad * 2))

    path = " ".join(
        f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}"
        for i, (x, y) in enumerate(xy(i, v) for i, v in enumerate(pts)))
    cx, cy = xy(len(pts) - 1, pts[-1])
    caption = escape(f"{label}: {fmt(pts[0])} to {fmt(pts[-1])} "
                     f"over {len(pts)} rounds")

    return (
        f'<svg class="spark" width="{width}" height="{height}" role="img" '
        f'aria-label="{caption}" viewBox="0 0 {width} {height}">'
        f'<title>{caption}</title>'
        f'<path d="{path}" fill="none" stroke="var(--trend)" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
        # 2px surface ring keeps the current-point marker off the line it sits on.
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.5" fill="var(--mark)" '
        f'stroke="var(--surface)" stroke-width="2"/></svg>')


def rank_bars(rows: list[tuple[str, float]], fmt=lambda v: f"{v:,.1f}",
              width: int = 520, row_h: int = 26) -> str:
    """Ranked horizontal bars. Magnitude is the job, so one hue, light->dark.

    Direct-labelled at the end of each bar: with a value on every row there is
    nothing for an axis to add, so the axis goes away.
    """
    if not rows:
        return ""
    height = row_h * len(rows) + 8
    label_w, value_w = 132, 62
    track = width - label_w - value_w
    top = max(v for _, v in rows) or 1.0
    floor_ = min(0.0, min(v for _, v in rows))
    span = (top - floor_) or 1.0

    bars = []
    for i, (name, value) in enumerate(rows):
        y = i * row_h + 4
        w = max(2.0, (value - floor_) / span * track)
        # Rank quartile picks the step: leaders darkest, and the ramp is
        # monotone so the ordering reads without reference to the legend.
        step = f"var(--r{min(4, 4 - int(i / max(1, len(rows)) * 4))})"
        caption = escape(f"{name}: {fmt(value)}")
        bars.append(
            f'<g><title>{caption}</title>'
            f'<text x="0" y="{y + row_h * 0.62:.0f}" class="bl">{escape(name)}</text>'
            f'<rect x="{label_w}" y="{y + 4}" width="{w:.1f}" height="{row_h - 12}" '
            f'rx="4" fill="{step}"/>'
            f'<text x="{label_w + w + 8:.1f}" y="{y + row_h * 0.62:.0f}" '
            f'class="bv">{escape(fmt(value))}</text></g>')

    return (f'<svg class="bars" width="{width}" height="{height}" role="img" '
            f'viewBox="0 0 {width} {height}">{"".join(bars)}</svg>')


def small_multiple(label: str, values: list[float], current: float,
                   fmt=lambda v: f"{v:,.0f}", good_up: bool = True) -> str:
    """One metric, one panel: label, current value, delta, trend.

    Small multiples over a shared layout rather than eight series in one frame -
    which is also what keeps the palette inside its all-pairs cap.
    """
    delta = ""
    if len(values) >= 2 and values[-2]:
        change = (values[-1] - values[-2]) / abs(values[-2])
        if abs(change) >= 0.005:
            good = (change > 0) == good_up
            delta = (f'<span class="dl {"up" if good else "down"}">'
                     f'{change:+.0%}</span>')
    return (f'<figure class="sm"><figcaption>{escape(label)}</figcaption>'
            f'<div class="v">{escape(fmt(current))}{delta}</div>'
            f'{sparkline(values, label=label, fmt=fmt)}</figure>')
