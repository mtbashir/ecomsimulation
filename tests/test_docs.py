"""The documentation says what the engine does."""
from __future__ import annotations

import importlib.util
from pathlib import Path

from ecomsim import version

ROOT = Path(__file__).resolve().parents[1]


def _tool():
    spec = importlib.util.spec_from_file_location(
        "doc_tables", ROOT / "tools" / "doc_tables.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generated_tables_match_the_engine():
    """docs/01's decision list and docs/08's scorecard and runway band."""
    tool = _tool()
    for doc in sorted({doc for doc, _, _ in tool.BLOCKS}):
        text = (ROOT / "docs" / doc).read_text(encoding="utf-8")
        assert tool.render(doc, text) == text, (
            f"docs/{doc} is out of date: run python tools/doc_tables.py")


def test_runway_bands_are_the_scoring_bands():
    """The band table probes each band once; every point inside it must agree."""
    from ecomsim import scoring
    tool = _tool()
    for lo, hi in tool.RUNWAY_BANDS:
        # Which band an exact edge falls in is the code's business; inside, one mark.
        bottom, top = lo + 0.001, (hi if hi is not None else lo + 30) - 0.001
        marks = {scoring._runway_band(bottom + f * (top - bottom))
                 for f in (0.0, 0.25, 0.5, 0.75, 1.0)}
        assert len(marks) == 1, (lo, hi, marks)


def test_changelog_records_the_engine_version():
    log = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"Engine {version.ENGINE_VERSION}" in log


def test_the_order_example_in_docs_00_is_what_the_engine_gives():
    """The worked example of how an order reaches a team and what goes in it."""
    spec = importlib.util.spec_from_file_location(
        "order_example", ROOT / "tools" / "order_example.py")
    ex = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ex)
    doc = (ROOT / "docs" / "00-game-world.md").read_text(encoding="utf-8")

    world, ctx, aov = ex.month({})
    t = "team_01"
    contested = ctx["potential"][t] - ctx["repeat_demand"][t]
    serum = ctx["sku_sales"][t]["SKU-03"]["want"]
    _, ctx2, _ = ex.month({t: {"1.1": {"SKU-03": {"discount": 0.15}}}})
    figures = [world.category_size / aov, contested, ctx["repeat_demand"][t],
               ctx["orders"][t], ctx["traffic_capacity"][t], serum,
               ctx2["potential"][t] - ctx2["repeat_demand"][t], ctx2["orders"][t],
               ctx2["sku_sales"][t]["SKU-03"]["want"]]
    for value in figures:
        assert f"{value:,.0f}" in doc, f"{value:,.0f} is no longer in docs/00's example"
