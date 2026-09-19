# E-Commerce Simulation

An advanced, competitive, multi-round e-commerce business simulation calibrated
to the Pakistani market. Teams run a D2C brand for 10 simulated months, making
interconnected decisions across strategy, marketing, pricing, supply chain,
fulfilment, payments, service and finance.

Built for the LUMS *E-Commerce in Practice* course.

## Why this exists

No commercial simulation models Pakistani e-commerce reality: ~60% cash-on-delivery
share, high RTO rates, marketplace commission structures, PKR-denominated CAC.
A sim where COD is a rounding error actively mis-teaches this market.

## Specification

| Doc | Contents |
|---|---|
| [`docs/00-game-world.md`](docs/00-game-world.md) | Premise, market size, starting position, seasonality, customer segments |
| [`docs/01-decision-list.md`](docs/01-decision-list.md) | 56 decision fields across 12 groups, progressive unlock schedule, memo rubric |
| [`docs/02-market-research-menu.md`](docs/02-market-research-menu.md) | 20 purchasable studies with prices, lags, error bands and bias rules |
| [`docs/03-core-mechanisms.md`](docs/03-core-mechanisms.md) | Perception vs reality, projects with lead time and failure risk, the second market |
| [`docs/05-start-mode.md`](docs/05-start-mode.md) | Round 0 founding round vs starting as a going concern, the 14 founding decisions, pro-forma preview and balance constraints |
| [`docs/07-engine-chain.md`](docs/07-engine-chain.md) | **The round calculation.** 18 modules with formulas, ordering and dependencies; the calibration test that gates all other work |
| [`docs/08-scoring.md`](docs/08-scoring.md) | Six pillars, criterion-referenced anchors, round weighting, anti-gaming design, insolvency and instructor reweighting bands |
| [`docs/09-event-library.md`](docs/09-event-library.md) | 24 events in three types - scheduled, conditional (earned) and stochastic - plus bounds on the AI dynamic-event layer |
| [`docs/10-kpi-dictionary.md`](docs/10-kpi-dictionary.md) | Every metric with formula, module, visibility and scoring; the definitional decisions that settle disputes; dashboard layout |
| [`docs/11-validation-harness.md`](docs/11-validation-harness.md) | Five test tiers, 20 strategy archetypes, twelve balance invariants, failure diagnosis and CI gating |
| [`docs/12-solo-delivery-plan.md`](docs/12-solo-delivery-plan.md) | **The active plan.** Burst-based delivery for a single person; what is in and out of scope; how to open and close a Claude session |
| [`docs/13-calibration-log.md`](docs/13-calibration-log.md) | Domain judgements about parameter values. Cannot be reconstructed - record them as they are made |
| [`docs/06-build-sequencing.md`](docs/06-build-sequencing.md) | Why the engine is built once at Advanced depth while presets ship incrementally; Path A vs Path B cost comparison |
| [`docs/04-configurability.md`](docs/04-configurability.md) | Team count 2–16, the 92-decision registry and presets, instructor unlock timing, round length and horizon, parameter safe ranges and validation invariants |

## Design principles

1. **Interconnection with lag.** Consequences arrive 1–3 rounds after the
   decision. Teams that optimise round-by-round must lose to teams that think
   in cohorts.
2. **Shared demand pool.** Teams compete for one market via an attractiveness-share
   model. One team's discount actively takes another's orders.
3. **Information has a price.** Most of what teams need to know must be bought,
   arrives late, and is noisy or biased.
4. **No dominant strategy.** Every lever has a cost that surfaces later.
   Discounting is deliberately the most tempting trap.
5. **Balanced scorecard, published upfront.** Profitability 25 / Growth 20 /
   Customer value 20 / Operational efficiency 15 / Cash 10 / Decision quality 10.
6. **Configurable, within validated bounds.** Team count, decision set, unlock
   timing, round length and every economic parameter are instructor-editable —
   but parameters carry green/amber/red bands and any change outside default
   triggers a 200-strategy validation run against seven balance invariants.

## Current status

**Burst 3 nearly complete.** 11 of 12 invariants pass; 53 tests green, no xfail.

| | |
|---|---|
| **Next** | **Decide the open question below, then burst 4 (Round 0 + decision I/O)** |
| Tests | 53 passing |
| Invariants | 11/12 — I11 open |
| Suites | `pytest -q` · `python calibrate.py` · `python validate.py --games 160` |

### Open question — shrinking currently wins

`cash_preservation` ranks #1 of 20. The business cannot reach EBITDA breakeven,
so cutting spend always improves profitability, and **LTV:CAC rewards not
acquiring customers** — great unit economics, no business. Three options are
laid out in `docs/13-calibration-log.md`; it is a judgement about what the
course should teach, not a parameter to tune.

### Invariant status

| | | |
|---|---|---|
| I1 No dominant strategy | PASS | best/median 1.34x |
| I2 No death spiral | PASS | none before R6 |
| I3 Discounting is a trap | PASS | 100% of shared games |
| I4 Margin viable | PASS | baseline CM 7.2% |
| I5 Cash binding, survivable | PASS | 96% draw credit, 3% of viable insolvent |
| I6 Share conserves | PASS | |
| I7 Research pays | PASS | selective 50.6 > heavy 50.2 > zero 49.6 |
| I8 Determinism | PASS | |
| I9 Monotonicity | PASS | 6/6 levers |
| I10 No free lunch | PASS | 8/8 levers |
| **I11 Discrimination** | **FAIL** | spread 28; sandbagger #10, harvester #11 |
| I12 Event neutrality | PASS | rank rho 0.99 |

### Fixed during burst 3

Seven scoring and engine defects, all surfaced by the must-fail archetypes —
see `docs/13-calibration-log.md` for each.

- **Growth measured against the team's own Round 1**, so sandbagging inflated
  it by suppressing the denominator (#1 → #11 once fixed)
- **LTV:CAC read ~0.25 for everyone** — acquisition charged twice and the first
  order omitted. Now 1.67–2.71, discounter 0.23
- **LTV:CAC used terminal CAC**, paying for the harvest it exists to punish
- **P4 anchors never updated** after burst 2 rebased couriers; 15 dead points
- **Inventory turns hardcoded to 50**
- **Administration capped spend at the prior round** — no constraint at all
- **No strategy could reach EBITDA breakeven**; P1/P5 anchors re-based to the
  reachable frontier

`credit_ceiling` 15M → 25M: coasting stays fatal, but a team with a plan can
fund it. Viable-strategy insolvency fell 22% → 1%.

### Fixed during burst 2

- **AOV now derives from the SKU basket**, so gross margin follows from what is
  in the cart rather than from two parameters that disagreed
- **Courier failure and RTO were double-counted**; courier success now means
  logistics only, RTO carries refusal
- **Reorder policy** targets cycle + pipeline + safety stock and forecasts from
  sellable demand, not raw potential; Round 0 seeds a PO in flight
- **Per-team economics are N-invariant by construction** — the category is
  sized from the actual logit at seeded state
- **Binding-constraint diagnosis** reports the actual minimum, not the first
  branch that matched
- **`events_enabled` switch** — calibration and T2 run without events

### Fixed during burst 1

- **Reorder oscillation** — M3 forecast from realised orders, so a stock-out
  suppressed the next order and perpetuated itself. Now forecasts from potential
  demand. Guarded by `test_no_reorder_oscillation`.
- **Cohort seed inconsistency** — 31,000 active customers generated more repeat
  demand than total orders, silently producing 100% repeat share and zero CAC.
  Base and frequencies corrected; the engine now warns rather than hiding it.

**Opening a session with Claude:** *"Read the repo, check README status, we are
on burst N."* Claude has no memory between conversations — this repo is the
entire handover. Closing procedure is in `docs/12-solo-delivery-plan.md`.

The 33.5-week programme in `docs/06` assumed a team. `docs/12` is the active
plan.

## Build approach

Specification phase. Engine, team console and instructor console not yet started.

**Build rule:** the engine is built once at Advanced (56-decision) depth.
Presets ship incrementally as configuration over that engine — never as
separate engines. See `docs/06-build-sequencing.md`.

Default configuration: **12 monthly rounds**, 8 teams, Advanced (56-decision)
preset, `founding` start mode (Round 0 setup + 12 operating rounds).

Delivery is `Google Form → decisions.csv → python run.py → report_<team>.html`,
not a web application. The simulation is unaffected; only the interface is
simpler (`docs/12`). See `docs/04-configurability.md` for the alternatives and the reasoning
behind the monthly-round default.

Planned sequence: calibrate the economic model in a spreadsheet and run two
cohorts manually before building the platform. The model is the product; the
software is the delivery mechanism.

## Specification status

Complete. Twelve documents covering world, decisions, mechanisms,
configurability, start mode, build sequencing, engine, scoring, events, metrics
and validation.

## Code

```
params/          Every economic constant. Nothing is hardcoded in the engine.
  parameters.csv   ~90 parameters with green and hard bands
  channels.csv     CPM, CTR, creative sensitivity, and cohort churn by channel
  segments.csv     Hidden segment weights (sold, noisily, as MR-06)
  couriers.csv  suppliers.csv  studies.csv
src/ecomsim/
  params.py        Loader, band classification, joint-constraint checks
  rng.py           Deterministic purpose-keyed randomness (invariant I8)
  state.py         The state vector, including the per-cohort customer ledger
  decisions.py     Decision registry and the default_when_disabled resolver
  engine.py        Round orchestrator over the module pipeline
  modules/         The 18 round modules in execution order
tests/           T0 registry integrity, determinism, and the T2 baseline gate
run.py           CLI runner
```

Implemented: M1 market, M5 perception, M6 traffic, M7 share, M8 conversion -
the demand chain, where the architecture has to be right. The remaining
thirteen modules are stubs carrying their contract and spec reference.

```bash
pip install -e ".[dev]"
pytest -q
python run.py --teams 8 --set saturation_exponent=0.55
```

## First engineering task

`docs/07-engine-chain.md` closes with a calibration test: at default decisions
with 8 teams and no events, the engine must reproduce the Round 0 baseline to
within 2% and hold it stable for 12 rounds. Nothing else should be built until
that test passes.
