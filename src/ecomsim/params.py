"""Parameter registry with green/hard band validation.

Nothing in the engine may hardcode an economic constant. Every value comes from
params/*.csv through this module, which is what makes instructor parameter
editing possible at all (docs/04-configurability.md).
"""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

PARAMS_DIR = Path(__file__).resolve().parents[2] / "params"


class BandViolation(ValueError):
    """Raised when a parameter is set outside its hard band."""


@dataclass(frozen=True)
class ParamSpec:
    name: str
    module: str
    default: float
    green_min: float
    green_max: float
    hard_min: float
    hard_max: float
    unit: str
    danger: str
    note: str

    def classify(self, value: float) -> str:
        """Return 'green', 'amber' or 'red' for a proposed value."""
        if value < self.hard_min or value > self.hard_max:
            return "red"
        if self.green_min <= value <= self.green_max:
            return "green"
        return "amber"


@dataclass
class Params:
    """Resolved parameter set for one run, plus the reference tables."""

    specs: dict[str, ParamSpec]
    values: dict[str, float]
    channels: list[dict]
    segments: list[dict]
    couriers: list[dict]
    suppliers: list[dict]
    studies: list[dict]
    skus: list[dict]
    # Who buys each product, and who is on each ad platform. Fixed for the run:
    # campaign settings are scored against them (targeting.py).
    audiences: list[dict] = field(default_factory=list)
    platforms: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    # Every parameter read during a run, for the coverage test (T0).
    _accessed: set[str] = field(default_factory=set)

    def __getitem__(self, name: str) -> float:
        if name not in self.values:
            raise KeyError(
                f"parameter {name!r} is not in params/parameters.csv - "
                "add it there rather than hardcoding a constant"
            )
        self._accessed.add(name)
        return self.values[name]

    @property
    def accessed(self) -> set[str]:
        return set(self._accessed)

    def channel(self, code: str) -> dict:
        return next(c for c in self.channels if c["code"] == code)

    def sku(self, code: str) -> dict:
        return next(s for s in self.skus if s["code"] == code)

    def study(self, code: str) -> dict:
        return next(s for s in self.studies if s["code"] == code)

    def audience(self, sku: str) -> dict | None:
        return next((a for a in self.audiences if a["code"] == sku), None)

    def platform(self, channel: str) -> dict | None:
        return next((p for p in self.platforms if p["channel"] == channel), None)

    def config_hash(self) -> str:
        """Stable hash of the configuration, stamped on every validation run."""
        blob = json.dumps(self.values, sort_keys=True).encode()
        return hashlib.sha256(blob).hexdigest()[:8]


def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for row in rows:
        for key, raw in list(row.items()):
            if raw is None or raw == "":
                continue
            try:
                row[key] = float(raw) if ("." in raw or "e" in raw.lower()) else int(raw)
            except ValueError:
                pass  # genuine string column
    return rows


def load(overrides: dict[str, float] | None = None,
         params_dir: Path = PARAMS_DIR) -> Params:
    """Load the registry, apply overrides, and classify each against its bands.

    A value outside the hard band raises. A value in the amber band is recorded
    as a warning - the run proceeds, but the instructor console must surface it
    and mark the configuration unvalidated (docs/11-validation-harness.md).
    """
    specs: dict[str, ParamSpec] = {}
    for row in _read_csv(params_dir / "parameters.csv"):
        spec = ParamSpec(
            name=str(row["name"]),
            module=str(row["module"]),
            default=float(row["default"]),
            green_min=float(row["green_min"]),
            green_max=float(row["green_max"]),
            hard_min=float(row["hard_min"]),
            hard_max=float(row["hard_max"]),
            unit=str(row["unit"]),
            danger=str(row.get("danger") or ""),
            note=str(row.get("note") or ""),
        )
        specs[spec.name] = spec

    values = {name: spec.default for name, spec in specs.items()}
    warnings: list[str] = []

    for name, value in (overrides or {}).items():
        if name not in specs:
            raise KeyError(f"unknown parameter {name!r}")
        spec = specs[name]
        band = spec.classify(value)
        if band == "red":
            raise BandViolation(
                f"{name}={value} is outside its hard band "
                f"[{spec.hard_min}, {spec.hard_max}]. {spec.note}"
            )
        if band == "amber":
            warnings.append(
                f"{name}={value} is amber (green is "
                f"[{spec.green_min}, {spec.green_max}]). {spec.note}"
            )
        if spec.danger == "HIGH":
            warnings.append(
                f"{name} is one of the three parameters that most often break "
                f"the model. Re-run the invariant suite before using this "
                f"configuration with students."
            )
        values[name] = value

    params = Params(
        specs=specs,
        values=values,
        channels=_read_csv(params_dir / "channels.csv"),
        segments=_read_csv(params_dir / "segments.csv"),
        couriers=_read_csv(params_dir / "couriers.csv"),
        suppliers=_read_csv(params_dir / "suppliers.csv"),
        studies=_read_csv(params_dir / "studies.csv"),
        skus=_read_csv(params_dir / "skus.csv"),
        audiences=_read_csv(params_dir / "audiences.csv"),
        platforms=_read_csv(params_dir / "platforms.csv"),
        warnings=warnings,
    )
    _check_joint_constraints(params)
    return params


def _check_joint_constraints(params: Params) -> None:
    """Constraints no single band can express (docs/04 section 6).

    Every parameter can sit inside its green band and the model still be broken.
    The dangerous failures are joint.
    """
    pillars = [
        "weight_profitability", "weight_growth", "weight_customer_value",
        "weight_operations", "weight_cash", "weight_decision_quality",
    ]
    total = sum(params.values[p] for p in pillars)
    if abs(total - 100) > 1e-6:
        raise BandViolation(f"scorecard pillar weights sum to {total}, not 100")

    for pillar in ("weight_customer_value", "weight_cash", "weight_decision_quality"):
        if params.values[pillar] <= 0:
            raise BandViolation(
                f"{pillar} may not be zero - removing the pillar removes the "
                "behaviour it protects against (docs/08-scoring.md)"
            )

    segment_share = sum(float(s["share"]) for s in params.segments)
    if abs(segment_share - 1.0) > 1e-6:
        raise BandViolation(f"segment shares sum to {segment_share}, not 1.0")

    # Unlimited-profitable-spend check: high margin + low CPM inflation +
    # high saturation together produce a dominant strategy even when each is green.
    risk = (
        (params.values["gross_margin_base"] - 0.38) / 0.12
        - (params.values["cpm_inflation_phi"] - 0.25) / 0.20
        + (params.values["saturation_exponent"] - 0.60) / 0.15
    )
    if risk > 2.0:
        params.warnings.append(
            "gross_margin_base, cpm_inflation_phi and saturation_exponent "
            "combine into a likely spend-to-win dominant strategy. Each is "
            "individually in band; the combination is not. Run the invariant "
            "suite before use."
        )
