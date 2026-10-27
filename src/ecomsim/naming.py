"""How a team is named wherever results are shown: its number and its brand.

"Team 3 · MUSE" on the console, the reports, the rankings, the workbooks and
both portals alike. The number comes from the seat (team_03) and never
changes; the brand is the one the team chose at founding, or renamed since. A
team that has not named a brand is "Team 3". The free-text team name a team
could once type is not shown: three names for one team was one too many.
"""
from __future__ import annotations

SEP = " · "


def number(team_id: str) -> str:
    """"team_03" -> "Team 3"; anything not numbered that way is left as it is."""
    tail = str(team_id).rsplit("_", 1)[-1]
    return f"Team {int(tail)}" if tail.isdigit() else str(team_id)


def clean_brand(brand) -> str:
    """A brand worth showing, or "": blank and the founding default are none."""
    b = str(brand or "").strip()
    return "" if b in ("", "Unnamed") else b


def label(team_id: str, brand=None) -> str:
    """"Team 3 · MUSE", or "Team 3" when the team has no brand."""
    n, b = number(team_id), clean_brand(brand)
    return f"{n}{SEP}{b}" if b and b not in (n, team_id) else n


def of(team) -> str:
    """The label of a simulated team, from the brand it carries."""
    founding = getattr(team, "founding", None)
    return label(team.team_id, team.brand_name or getattr(founding, "brand_name", None))
