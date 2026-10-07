"""The month's funnel and stock position, in the same words everywhere.

Report, dashboard, decision form and instructor console all show these, so a
team can check the arithmetic itself: conversion is orders divided by
sessions, and weeks of cover is the stock on hand divided by a week of sales.
"""
from __future__ import annotations

WEEKS_PER_MONTH = 4.33


def from_scratch_launch(team, h: dict) -> bool:
    """A business the team founded itself, in its first trading month.

    It has no past buyers to come back, so nothing in that month is shown as
    returning. A going-concern game starts with customers, and keeps them.
    """
    return getattr(team, "founding", None) is not None and int(h.get("round", 0) or 0) == 1


def facts(h: dict, units_per_order: float = 2.424, launch: bool = False) -> dict:
    """Plain numbers for one month's record (older records lack some keys).

    `launch` (see from_scratch_launch) counts every non-paid visit as organic:
    the engine opens every game at a working scale, but in the month a founded
    business launches, those visitors are new to it, not returning."""
    sessions = float(h.get("sessions", 0) or 0)
    orders = float(h.get("orders", 0) or 0)
    sold = float(h.get("units_sold") or orders * units_per_order)
    stock = float(h.get("inventory_units", 0) or 0)
    weekly = sold / WEEKS_PER_MONTH if sold > 0 else 0.0
    repeat = float(h.get("repeat_orders") or orders * float(h.get("repeat_order_share", 0) or 0))
    paid = float(h.get("sessions_paid", 0) or 0)
    organic = float(h.get("sessions_organic", 0) or 0)
    returning = float(h.get("sessions_returning", 0) or 0)
    if launch:
        organic, returning = organic + returning, 0.0
        if not paid and sessions:
            # Recorded before the split existed: paid is what the campaigns clicked.
            paid = sum(float(r.get("clicks", 0) or 0) for r in h.get("campaigns") or [])
            organic = max(0.0, sessions - paid)
    return {
        "launch": launch,
        "sessions": sessions,
        "paid": paid,
        "organic": organic,
        "returning": returning,
        "orders": orders,
        "conversion": orders / sessions if sessions > 0 else 0.0,
        "new_customers": float(h.get("new_customers", 0) or 0),
        "repeat_orders": repeat,
        "units_in_stock": stock,
        "units_sold": sold,
        "weekly_units": weekly,
        "weeks_cover": stock / weekly if weekly > 0 else float(h.get("weeks_cover", 0) or 0),
        "lost_to_stockout": float(h.get("lost_to_stockout", 0) or 0),
    }


def sentence(f: dict) -> tuple[str, str]:
    """(funnel line, stock line) as plain text with the arithmetic shown."""
    split = ""
    if f.get("launch") and (f["paid"] or f["organic"]):
        split = f" (paid {f['paid']:,.0f} · organic {f['organic']:,.0f}; no returning customers in the launch month)"
    elif f["paid"] or f["organic"] or f["returning"]:
        split = (f" (paid {f['paid']:,.0f} · organic {f['organic']:,.0f} · "
                 f"returning customers {f['returning']:,.0f})")
    funnel = (f"{f['sessions']:,.0f} sessions{split} → {f['orders']:,.0f} orders → "
              f"conversion {f['conversion']:.2%} (orders ÷ sessions). "
              f"New customers {f['new_customers']:,.0f}; repeat orders {f['repeat_orders']:,.0f}.")
    stock = (f"{f['units_in_stock']:,.0f} units in stock ÷ {f['weekly_units']:,.0f} units "
             f"sold a week = {f['weeks_cover']:.1f} weeks of cover. "
             f"Units sold this month {f['units_sold']:,.0f}"
             + (f"; about {f['lost_to_stockout']:,.0f} orders lost to stock-outs."
                if f["lost_to_stockout"] >= 1 else "; no orders lost to stock-outs."))
    return funnel, stock
