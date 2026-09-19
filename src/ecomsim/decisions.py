"""Decision registry and resolution.

The rule that makes presets work (docs/04-configurability.md):

    The engine never reads a decision directly. It reads a resolved value -
    the team's input if the decision is enabled and unlocked, otherwise the
    configured default.

Disabling a decision removes student agency over it. It never removes it from
the model, which is why Foundation running on a full-depth engine is a better
product than Foundation on a Foundation engine.
"""
from __future__ import annotations

from dataclasses import dataclass

PRESETS = {
    "foundation": 24,
    "standard": 38,
    "advanced": 56,
    "expert": 92,
}


@dataclass(frozen=True)
class DecisionSpec:
    code: str
    group: str
    name: str
    kind: str                # select | multi | num | pct | curr | per_sku | text
    default_when_disabled: object
    presets: frozenset[str]  # presets in which this decision is enabled
    unlock_round: int = 1
    min_granularity: int = 1  # max ROUND_MONTHS at which it stays an action


# Abbreviated registry. Full 56 in docs/01-decision-list.md; the remaining rows
# follow this shape exactly and are added as each module is implemented.
REGISTRY: dict[str, DecisionSpec] = {
    d.code: d for d in [
        DecisionSpec("2.2", "G2", "Site-wide discount depth", "pct", 0.0,
                     frozenset({"foundation", "standard", "advanced", "expert"})),
        DecisionSpec("2.4", "G2", "Free-shipping threshold", "curr", 2500,
                     frozenset({"foundation", "standard", "advanced", "expert"})),
        DecisionSpec("3.1", "G3", "Meta spend", "curr", 468_000,
                     frozenset({"foundation", "standard", "advanced", "expert"})),
        DecisionSpec("3.2", "G3", "Google Search spend", "curr", 234_000,
                     frozenset({"foundation", "standard", "advanced", "expert"})),
        DecisionSpec("3.4", "G3", "TikTok spend", "curr", 168_000,
                     frozenset({"foundation", "standard", "advanced", "expert"})),
        DecisionSpec("3.8", "G3", "Creative production budget", "curr", 200_000,
                     frozenset({"standard", "advanced", "expert"}), unlock_round=2),
        DecisionSpec("3.9", "G3", "Brand spend", "curr", 267_000,
                     frozenset({"standard", "advanced", "expert"}), unlock_round=2),
        DecisionSpec("7.2", "G7", "Supplier selection", "select", "B",
                     frozenset({"foundation", "standard", "advanced", "expert"})),
        DecisionSpec("7.5", "G7", "Safety stock target (weeks)", "num", 2,
                     frozenset({"foundation", "standard", "advanced", "expert"})),
        DecisionSpec("9.1", "G9", "COD policy", "select", "on",
                     frozenset({"foundation", "standard", "advanced", "expert"})),
        DecisionSpec("9.2", "G9", "Prepaid incentive", "pct", 0.03,
                     frozenset({"standard", "advanced", "expert"})),
        DecisionSpec("10.1", "G10", "CS headcount", "num", 4,
                     frozenset({"standard", "advanced", "expert"}), unlock_round=2),
        DecisionSpec("1.2", "G1", "Bundle definition", "multi", [],
                     frozenset({"standard", "advanced", "expert"})),
        DecisionSpec("1.5", "G1", "SKU quality tier", "select", None,
                     frozenset({"foundation", "standard", "advanced", "expert"})),
        DecisionSpec("3.6", "G3", "Affiliate commission rate", "pct", 0.0,
                     frozenset({"standard", "advanced", "expert"}), unlock_round=2),
        DecisionSpec("4.1", "G4", "Marketplace participation", "select", "off",
                     frozenset({"standard", "advanced", "expert"}), unlock_round=3),
        DecisionSpec("5.1", "G5", "UX investment", "curr", 0,
                     frozenset({"standard", "advanced", "expert"}), unlock_round=2),
        DecisionSpec("6.1", "G6", "Retention budget", "curr", 60_000,
                     frozenset({"foundation", "standard", "advanced", "expert"})),
        DecisionSpec("7.4", "G7", "Quality assurance spend", "curr", 80_000,
                     frozenset({"foundation", "standard", "advanced", "expert"})),
        DecisionSpec("8.2", "G8", "3PL share", "pct", 0.4,
                     frozenset({"foundation", "standard", "advanced", "expert"})),
        DecisionSpec("8.3", "G8", "Courier mix", "multi", None,
                     frozenset({"foundation", "standard", "advanced", "expert"})),
        DecisionSpec("8.5", "G8", "Packaging tier", "select", "basic",
                     frozenset({"foundation", "standard", "advanced", "expert"})),
        DecisionSpec("9.3", "G9", "Payment gateway", "select", "A",
                     frozenset({"foundation", "standard", "advanced", "expert"})),
        DecisionSpec("10.4", "G10", "Return policy", "select", "customer_pays",
                     frozenset({"standard", "advanced", "expert"}), unlock_round=2),
        DecisionSpec("11.1", "G11", "Recommendation engine", "select", False,
                     frozenset({"advanced", "expert"}), unlock_round=3),
        DecisionSpec("11.2", "G11", "Demand forecasting AI", "select", False,
                     frozenset({"advanced", "expert"}), unlock_round=3),
        DecisionSpec("11.3", "G11", "Dynamic pricing", "select", False,
                     frozenset({"advanced", "expert"}), unlock_round=3),
        DecisionSpec("11.4", "G11", "AI customer service", "select", False,
                     frozenset({"advanced", "expert"}), unlock_round=3),
        DecisionSpec("11.5", "G11", "AI creative generation", "select", False,
                     frozenset({"advanced", "expert"}), unlock_round=3),
        DecisionSpec("12.1", "G12", "Market research purchases", "multi", [],
                     frozenset({"foundation", "standard", "advanced", "expert"})),
        DecisionSpec("12.5", "G12", "Board memo", "text", "",
                     frozenset({"foundation", "standard", "advanced", "expert"})),
    ]
}


class Resolver:
    """Turns submitted decisions into the resolved values modules read."""

    def __init__(self, preset: str = "advanced", round_: int = 1,
                 overrides: dict[str, dict] | None = None):
        self.preset = preset
        self.round = round_
        self.overrides = overrides or {}

    def enabled(self, code: str) -> bool:
        spec = REGISTRY[code]
        cfg = self.overrides.get(code, {})
        if "enabled" in cfg:
            return bool(cfg["enabled"])
        return self.preset in spec.presets

    def unlocked(self, code: str) -> bool:
        spec = REGISTRY[code]
        unlock = self.overrides.get(code, {}).get("unlock_round", spec.unlock_round)
        lock = self.overrides.get(code, {}).get("lock_round")
        if lock is not None and self.round > lock:
            return False
        return self.round >= unlock

    def resolve(self, submitted: dict[str, object]) -> dict[str, object]:
        out: dict[str, object] = {}
        for code, spec in REGISTRY.items():
            if self.enabled(code) and self.unlocked(code) and code in submitted:
                out[code] = submitted[code]
            else:
                out[code] = self.overrides.get(code, {}).get(
                    "default_when_disabled", spec.default_when_disabled
                )
        return out
