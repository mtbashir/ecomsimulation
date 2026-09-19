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

## Build status

Specification phase. Engine, team console and instructor console not yet started.

Default configuration: **12 monthly rounds**, 8 teams, Advanced (56-decision)
preset, `founding` start mode (Round 0 setup + 12 operating rounds). See `docs/04-configurability.md` for the alternatives and the reasoning
behind the monthly-round default.

Planned sequence: calibrate the economic model in a spreadsheet and run two
cohorts manually before building the platform. The model is the product; the
software is the delivery mechanism.

## Next specification documents

- `04-kpi-dictionary.md` — every metric, its formula, and where it surfaces
- `05-engine-chain.md` — the round calculation, layer by layer
- `06-event-library.md` — the ~18 scripted and dynamic market events
- `07-scoring.md` — scorecard formulas and normalisation
- `08-validation-harness.md` — the 200-strategy balance test suite
