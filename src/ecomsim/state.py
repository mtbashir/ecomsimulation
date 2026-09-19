"""The state vector.

Modules read and write this; nothing else is shared between them. Keeping it
explicit is what makes the Expert tier additive rather than a rewrite
(docs/06-build-sequencing.md).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Cohort:
    """One acquisition cohort, tracked individually (docs/07 M12).

    LTV is computed from these, never from a formula applied to averages.
    """
    acquired_round: int
    channel: str
    active: float
    churn_base: float
    freq: float
    cumulative_contribution: float = 0.0


@dataclass
class TeamState:
    team_id: str

    # Finance
    cash: float = 25_000_000.0
    credit_drawn: float = 0.0
    cod_receivable: float = 0.0
    mp_receivable: float = 0.0
    payables: dict[int, float] = field(default_factory=dict)
    receivables: dict[int, float] = field(default_factory=dict)

    # Demand-side stocks
    brand_equity: float = 0.50
    creative_quality: float = 0.50
    ux_score: float = 0.50
    rating: float = 4.10
    nps: float = 24.0

    # Perception vs reality (docs/03 mechanism 2)
    quality_actual: float = 0.60
    quality_perceived: float = 0.60
    value_actual: float = 0.50
    value_perceived: float = 0.50
    delivery_actual: float = 0.62
    delivery_perceived: float = 0.62

    # Operations
    inventory: dict[str, float] = field(default_factory=dict)
    active_skus: list[str] = field(default_factory=list)
    open_pos: list[dict] = field(default_factory=list)
    warehouse_capacity: float = 6_000.0
    cs_agents: int = 4
    cs_backlog: float = 0.0

    # Customers
    cohorts: list[Cohort] = field(default_factory=list)

    # Capability projects
    projects: list[dict] = field(default_factory=list)
    capabilities: set[str] = field(default_factory=set)

    # Carried history - several effects are explicitly lagged
    adstock: dict[str, float] = field(default_factory=dict)
    brand_spend_history: list[float] = field(default_factory=list)
    delivered_prev: float = 0.0
    pending_gap_penalties: dict[int, dict] = field(default_factory=dict)
    # Written by M13, read by M12 the FOLLOWING round. These lived in ctx,
    # which is rebuilt every round, so M12 - which runs first - always read
    # zero and neither retention spend nor service failure ever touched churn.
    experience_penalty: float = 0.0
    predictions: list[dict] = field(default_factory=list)
    reports: dict[int, dict] = field(default_factory=dict)
    in_administration: bool = False
    founding: object | None = None
    brand_name: str = ""
    price_multiplier: float = 1.0
    traffic_multiplier: float = 1.0
    last_discretionary: dict[str, float] = field(default_factory=dict)

    # Per-round results, appended by M14/M15/M17
    history: list[dict] = field(default_factory=list)


@dataclass
class WorldState:
    run_id: str
    round: int = 0
    category_size: float = 0.0
    incumbents: list[dict] = field(default_factory=list)
    active_events: list[dict] = field(default_factory=list)
    teams: dict[str, TeamState] = field(default_factory=dict)
    market_spend: dict[str, float] = field(default_factory=dict)
    market_avg_price: float = 3_000.0
    market_avg_aov: float = 3_000.0
    category_scale: float = 1.0
