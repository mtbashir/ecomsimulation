# E-Commerce Simulation

A competitive, multi-round e-commerce business simulation calibrated to the
Pakistani market. Teams found a D2C brand in a setup round, then run it for
twelve simulated months, making interconnected decisions across range and
pricing, marketing, channels, stock and suppliers, fulfilment, payments,
service, technology and finance.

Built for the LUMS *E-Commerce in Practice* course, and in use with the
Fall-2026 cohort.

## Why this exists

No commercial simulation models Pakistani e-commerce reality: ~60% cash-on-delivery
share, high RTO rates, marketplace commission structures, PKR-denominated CAC.
A sim where COD is a rounding error actively mis-teaches this market.

## What it is today

**Engine 2.3.0** · rules v2 · 38 decisions · 18 modules · deterministic and
replayable. What changed, and when: [`CHANGELOG.md`](CHANGELOG.md).

**Team portal.** The founding form with a pro-forma preview; a decisions form
that saves every change as it is made, shows the month's cash and the working
capital loan it needs, and refuses a month that spends past it; a monthly report
for every month played (funnel and stock, P&L, sales and stock by product,
campaigns, technology projects, scorecard); rankings once the instructor
publishes them; the research desk, campaign screen, handbook by decision,
marketing guide and *How You Are Scored*.

**Instructor console.** Open, preview, run and roll back months; a debrief card
per team; the leaderboard from month 1 and results by round; market size by
product and segment; every team's choices side by side; which report sections
teams see each month; memo verdicts; per-game rule switches; results as Excel
workbooks; a scoring playbook for coaching. See
[`docs/17-instructor-guide.md`](docs/17-instructor-guide.md).

**Quality gates.** `pytest` (502 tests, including checks that the generated
documentation matches the engine), `validate.py` (thirteen balance invariants,
all passing) and `calibrate.py` (the baseline holds).

| Invariant (engine 2.3.0, 200 games) | | |
|---|---|---|
| I1 No dominant strategy | PASS | best/median 1.24x |
| I2 No death spiral | PASS | none insolvent before month 6 |
| I3 Discounting is a trap | PASS | below balanced in 100% of shared games |
| I4 Margin viable | PASS | baseline contribution 8.6% |
| I5 Cash binding, survivable | PASS | 90% draw credit, 0% of viable strategies insolvent |
| I6 Share conserves | PASS | |
| I7 Research pays | PASS | selective +0.4 over none, heavy far behind |
| I8 Determinism · I9 Monotonicity · I10 No free lunch | PASS | |
| I11 Scorecard discrimination | PASS | spread 48; sandbagger and harvester 16-17 behind balanced |
| I12 Event neutrality | PASS | mean delta 6.7, rank rho 0.95 |
| I13 Targeting pays, not alone | PASS | sharp +4.2, careless -2.3; sharp targeting does not rescue discounting |

## Documentation

| Doc | Contents |
|---|---|
| [`CHANGELOG.md`](CHANGELOG.md) | Every change since the specification and web app were published, with commits and which games each applies to |
| [`docs/00-game-world.md`](docs/00-game-world.md) | Premise, market size, starting position, seasonality, customer segments |
| [`docs/01-decision-list.md`](docs/01-decision-list.md) | **The decision list as built** - 38 decisions, generated from the engine - and the original 56-field design |
| [`docs/02-market-research-menu.md`](docs/02-market-research-menu.md) | 20 purchasable studies with prices, lags, error bands and bias rules |
| [`docs/03-core-mechanisms.md`](docs/03-core-mechanisms.md) | Perception vs reality, projects, working capital and the loan, the cost of stock, channels beyond the own site |
| [`docs/04-configurability.md`](docs/04-configurability.md) | Team count, the registry and presets, decision windows, **per-game rules**, instructor controls, round length, parameter bands |
| [`docs/05-start-mode.md`](docs/05-start-mode.md) | The founding round vs starting as a going concern, the founding decisions, the launch order |
| [`docs/06-build-sequencing.md`](docs/06-build-sequencing.md) | Why the engine is built once at full depth while presets ship as configuration |
| [`docs/07-engine-chain.md`](docs/07-engine-chain.md) | **The round calculation.** 18 modules with formulas and ordering, with *As built* notes where the engine has moved on |
| [`docs/08-scoring.md`](docs/08-scoring.md) | Six pillars, the published scorecard (generated from the engine), rules v2, insolvency, rankings |
| [`docs/09-event-library.md`](docs/09-event-library.md) | Scheduled, conditional and stochastic events |
| [`docs/10-kpi-dictionary.md`](docs/10-kpi-dictionary.md) | Every metric with formula, module, visibility and scoring |
| [`docs/11-validation-harness.md`](docs/11-validation-harness.md) | Test tiers, 20 strategy archetypes, the thirteen invariants, failure diagnosis |
| [`docs/12-solo-delivery-plan.md`](docs/12-solo-delivery-plan.md) | The burst-based plan the build followed |
| [`docs/13-calibration-log.md`](docs/13-calibration-log.md) | Domain judgements behind parameter values - record them as they are made |
| [`docs/14-deployment.md`](docs/14-deployment.md) | Render, the persistent disk, settings, running a class |
| [`docs/15-course-map.md`](docs/15-course-map.md) | The LUMS course outline mapped onto the simulation, session by session |
| [`docs/16-lecture-decks.md`](docs/16-lecture-decks.md) | Rules for the lecture decks and where each deck's generator lives |
| [`docs/17-instructor-guide.md`](docs/17-instructor-guide.md) | Running a live cohort: a month step by step, report detail, rollback, rule cards |
| [`docs/18-questions.md`](docs/18-questions.md) | Every question asked while running the course, and the doc that answers it |

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
   timing, round length and every economic parameter are instructor-editable,
   but parameters carry green/amber/red bands and a change outside default
   needs a validation run against the balance invariants.
7. **A rule never re-marks a month already played.** Rules that change how a
   month is played are switched per game and follow the month; a class is
   never scored on a rule it was not told about.

## Running it

### Hosting it

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/mtbashir/ecomsimulation)

One click, then set `ECOMSIM_ADMIN_PASSWORD` when it asks. The blueprint does
the rest: Python runtime, gunicorn, a 1 GB persistent disk, a generated session
secret, and a health check. Collect the team passwords from the Teams page -
they are shown once. See `docs/14-deployment.md`. The live service redeploys on
every push to the default branch.

### Running it locally

```
py -m pip install -e ".[web]"
py serve.py init --teams 8 --name "E-Commerce in Practice"   # prints passwords once
py serve.py                                                   # start it
```

Everything is one SQLite file, `game.db`.

### Running a cohort from files

```
py run.py new --teams 8 --out game     # start a game
py run.py template --game game         # blank decisions file
#   ... teams fill it in (a Google Form export works too) ...
py run.py round --game game            # reports + console + results.csv
py run.py preview --game game          # Round 0 pro-forma
```

`py` on Windows, `python3` on macOS/Linux. Files in, HTML out - no server, and
students never touch the engine. See `QUICKSTART.md`, including how to open the
shipped demo with no Python at all.

### Checking it

```
py -m pip install -e ".[dev]"
py -m pytest -q                  # the test suite
py validate.py                   # the thirteen balance invariants
py calibrate.py                  # the baseline holds at default decisions
py tools/doc_tables.py --check   # the generated docs match the engine
```

## Changing the rules

1. Change the engine or `params/`, with a test.
2. A change to how a month is played that would re-mark a game already under
   way goes behind a per-game switch (`docs/04-configurability.md`, *Per-game
   rules*), on from month 1 for new games.
3. Run the test suite and `validate.py`.
4. Update the docs: `py tools/doc_tables.py` rewrites the decision list and the
   scorecard tables; the mechanism, engine-chain, KPI and course-map docs by
   hand; add the change to `CHANGELOG.md`.
5. Move `ENGINE_VERSION` in `src/ecomsim/version.py` for any change to how a
   month is simulated or scored.
6. Push between months, not while one is being run: the push is the deploy.

## Code

```
params/            Every economic constant; nothing is hardcoded in the engine
  parameters.csv     ~160 parameters with green and hard bands
  channels.csv segments.csv audiences.csv skus.csv suppliers.csv
  couriers.csv platforms.csv studies.csv
src/ecomsim/
  decisions.py       The decision registry and resolver
  engine.py          Round orchestrator over the module pipeline; carry-forward
  modules/           The 18 round modules, M0 resolve to M17 score
  loans.py           Working capital: the month's need, the cash check, funding, settlement
  marketplace.py     The marketplace channel (4.1)
  mix.py             Product mix and the product P&L
  targeting.py       Campaign setup (3.10) and channel intent
  assortment.py      Range changes (1.3)
  founding.py        The founding round
  scoring.py         The published scorecard, final and monthly scores, ranks
  naming.py          How every page names a team: "Team 1 · Tarz"
  report.py console.py debrief.py coach.py workbook.py charts.py funnel.py
                     What teams and the instructor read
  backfill.py        Rebuilds stock and cash detail for early months
  version.py         Engine version and rule sets
  web/               Flask app: db.py (schema, per-game switches), service.py,
                     app.py, handbook.py, briefing.py, templates/
tools/             doc_tables.py (generated docs), order_example.py, kpi_definitions_pdf.py, deck/
tests/             Registry, determinism, baseline, mechanisms, web, docs
run.py serve.py demo.py calibrate.py validate.py wsgi.py
```

## Working on it with Claude

Claude has no memory between conversations - this repository is the entire
handover. Open a session with: *"Read the README, the CHANGELOG and
docs/17-instructor-guide.md."* Lecture decks follow `docs/16-lecture-decks.md`
(see `CLAUDE.md`).
