"""Market size on the instructor console: orders by product and segment."""
from __future__ import annotations

from ecomsim import bootstrap, console, params as P
from ecomsim.engine import run_round


def test_the_grid_adds_up_to_every_order_asked_for(tmp_path):
    params = P.load({"n_teams": 4, "events_enabled": 0})
    world = bootstrap.new_world(params, run_id="grid")
    world.rules_from = 1
    for _ in range(2):
        run_round(world, params, {})
    asked = sum(t.history[-1]["orders"] + t.history[-1]["lost_to_stockout"]
                for t in world.teams.values())
    cells = sum(sum(console._grid(t.history[-1])[0].values()) for t in world.teams.values())
    assert abs(cells - asked) < 1e-6 * asked

    page = console.render(world, params, tmp_path).read_text()
    assert "Orders by Product and Segment" in page
    assert "Quality Loyalists" in page and "Share of orders" in page
    assert 'aria-label="Orders by segment"' in page and 'class="sh"' in page
