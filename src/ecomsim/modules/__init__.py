"""The eighteen round modules, in execution order (docs/07-engine-chain.md).

Order is not arbitrary. M5 precedes M7 because perception drives attractiveness.
M3 precedes M8 because stock constrains what can be sold. M13 follows M11 because
ratings react to delivered experience and feed the NEXT round's conversion.

Each module has the signature:

    def run(world, params, resolved, ctx) -> None

and mutates the state vector in place. Adding a mechanism means adding a module
between two existing ones, not touching the ones already there.
"""
from . import (
    m00_resolve, m01_market, m02_events, m03_supply, m04_capability,
    m05_perception, m06_traffic, m07_share, m08_conversion, m09_basket,
    m10_fulfilment, m11_returns, m12_ledger, m13_experience, m14_pnl,
    m15_cash, m16_research, m17_score,
)

PIPELINE = [
    m00_resolve, m01_market, m02_events, m03_supply, m04_capability,
    m05_perception, m06_traffic, m07_share, m08_conversion, m09_basket,
    m10_fulfilment, m11_returns, m12_ledger, m13_experience, m14_pnl,
    m15_cash, m16_research, m17_score,
]
