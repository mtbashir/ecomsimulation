# 11 — Validation Harness

The test suite that lets anyone — you, a colleague, a future maintainer —
change a parameter and know within fifteen minutes whether the sim is still
balanced.

**Build this alongside the engine, not after it.** It is what turns "we think
it's balanced" into something demonstrable, and it is the only thing that makes
instructor parameter editing safe.

---

## Five test tiers

| Tier | What it proves | Runtime | When |
|---|---|---|---|
| **T0** Unit | Each module computes correctly in isolation | < 5s | Every commit |
| **T1** Golden file | The engine matches the spreadsheet model | < 30s | Every commit |
| **T2** Baseline calibration | The engine holds equilibrium at default decisions | < 10s | Every commit — **gates everything** |
| **T3** Invariant suite | The sim is balanced and has no dominant strategy | ~15 min | Nightly, and before any parameter change |
| **T4** Regression | Past cohort runs still replay identically | ~2 min | Every release |

### Performance requirement

The engine must complete **one 12-round, 8-team game in under 200ms.**

T3 runs 200 strategies × 20 seeds = 4,000 games. At 200ms that is ~13 minutes,
which is tolerable nightly and just tolerable on demand. At 2s per game it is
2.2 hours, and the harness stops being run — which means it stops working.

Treat engine performance as a correctness requirement, not an optimisation.

---

## T2 — The baseline calibration gate

From `07-engine-chain.md`, restated as an executable test:

> At default decisions, 8 teams, no events, seed fixed: the engine reproduces
> the Round 0 baseline to within **2% on every headline metric**, and holds it
> for **12 rounds**.

| Metric | Target | Tolerance |
|---|---|---|
| `revenue_net` | 12,000,000 | ±2% |
| `orders` | 4,000 | ±2% |
| `aov_net` | 3,000 | ±2% |
| `sessions` | 190,000 | ±2% |
| `conversion_rate` | 2.1% | ±2% rel |
| `gross_margin_pct` | 38% | ±2% rel |
| `contribution_margin_pct` | 9% | ±2% rel |
| `cac_blended` | 850 | ±2% |
| `repeat_order_share` | 22% | ±2% rel |
| `rating` | 4.1 | ±2% rel |
| `cash_balance` drift | ≤ ±3% per round | — |

**Nothing else is built until T2 passes.** If the engine drifts off baseline
with nobody making decisions, every parameter downstream is being fitted to a
broken foundation. Expect three or four days of tuning; it saves weeks.

Run T2 at N = 2, 4, 8, 12, 16 — per-team economics must be identical at every
team count (`04-configurability.md`).

---

## The strategy library

200 strategies = **20 archetypes × 10 parameter variations**, run across 20
seeds.

### Scripted strategy DSL

A strategy is a pure function from state to decisions. No AI, no randomness —
these must be reproducible.

```python
@strategy("discounter", variation="depth")
def discounter(state, round, params):
    return {
        "discount_depth": params.depth,          # varied 0.15 … 0.45
        "meta_spend": 0.55 * state.revenue_prev * 0.15,
        "brand_spend": 0,
        "research": [],
        ...
    }
```

### The 20 archetypes

| # | Archetype | Tests |
|---|---|---|
| 1 | **Baseline** — all defaults | T2 equilibrium |
| 2 | **Balanced** — the reference "good" strategy | The benchmark others are measured against |
| 3 | Growth-at-all-costs | Saturation exponent `σ` |
| 4 | **Discounter** | The central trap (I3) |
| 5 | Premium | Quality Loyalist segment viability |
| 6 | Retention-led | Cohort ledger and CRM returns |
| 7 | Operational excellence | Whether ops investment pays |
| 8 | Cash preservation | Whether under-investment is punished |
| 9 | Marketplace-first | Commission vs traffic trade-off |
| 10 | Own-site purist | Whether avoiding marketplace is viable |
| 11 | Technology-led | AI module payback and obsolescence |
| 12 | Private-label bet | Project risk and P(success) curve |
| 13 | Q-Com aggressive (3 cities) | Should fail on cash ~R8 |
| 14 | Q-Com measured (1 city) | Should be viable |
| 15 | **Research-heavy** (buy everything) | I7 upper bound |
| 16 | **Research-zero** | I7 lower bound |
| 17 | **Research-selective** (3–6/round) | I7 — should beat both |
| 18 | **Sandbagger** — coast R1–6, sprint R7–12 | Round weighting (I11) |
| 19 | **Harvester** — build R1–9, strip R10–12 | Terminal stock metrics (I11) |
| 20 | COD-off / prepaid-push | RTO parameter sanity |

Archetypes 4, 15, 16, 17, 18 and 19 exist **solely to fail**. If any of them
wins, a specific design intent has broken, and the invariant names which.

### Variations

Each archetype runs 10 variations across its defining parameter — discount
depth 0.15–0.45, marketing intensity 8%–30% of revenue, and so on. This maps
the response surface rather than testing a single point.

---

## The twelve invariants

I1–I7 are the seven named in `04-configurability.md`. I8–I12 are additions the
suite needs to be trustworthy.

### I1 · No dominant strategy
```
max(final_score) < 2.5 × median(final_score)
AND no archetype wins in more than 40% of seeds
```
**Most common cause:** `σ` (marketing saturation) too high. Check it first.

### I2 · No death spiral
```
no strategy insolvent before round T/2
AND every insolvent team's score ≥ 25 (recoverable, not eliminated)
```
**Most common cause:** starting cash too low, or MOQ × lead time forcing a
guaranteed R2 stock-out.

### I3 · Discounting is a trap
```
rank(discounter) > rank(balanced) by round 8, in ≥ 90% of seeds
```
**Most common cause:** deal-cohort churn (0.44) too low, or P3 weight too low.

### I4 · Margin is viable
```
baseline contribution_margin_pct ∈ [5%, 15%]
```

### I5 · Cash is binding but survivable
```
≥ 20% of strategies draw the credit line
AND < 10% become insolvent
```

### I6 · Share conserves
```
|Σ(team_share) + Σ(incumbent_share) − 1.0| < 0.001, every round, every seed
```
A pure correctness check. Failure means a bug in M7 redistribution, not a
balance problem.

### I7 · Research pays
```
score(research_selective) > score(research_zero)
AND score(research_selective) > score(research_heavy)
```
**The invariant to watch.** If `research_heavy` wins, study prices are too low.
If `research_zero` wins, the studies carry insufficient real signal. Either way
the Markstrat mechanism has failed and the menu needs rework, not the parameters.

### I8 · Determinism
```
hash(run(state, decisions, config, seed)) is identical across 3 executions
AND identical across platforms
```
Without this, replay, golden files and dispute resolution all fail. Test it
first; it is cheap and it catches map-iteration-order bugs early.

### I9 · Monotonicity
Ceteris paribus, with everything else held at default:

| Increase | Must increase | Must decrease |
|---|---|---|
| Marketing spend | `sessions` | — |
| Discount depth | `conversion_rate` | `gross_margin_pct` |
| Safety stock | `instock_rate` | `inventory_turns` |
| Prepaid incentive | `prepaid_share` | `rto_rate` |
| CS headcount | `sla_hit` | `cs_backlog` |
| Supplier C share | `instock_rate` | `gross_margin_pct` |

Catches sign errors, which are the most common and most embarrassing engine
bug, and the hardest to spot in aggregate output.

### I10 · No free lunch
```
for every decision d: ∃ a metric that worsens when d increases
```
Every lever must cost something. A decision with no downside is a dominant
strategy waiting to be discovered by a student in Round 3.

### I11 · Scorecard discrimination
```
35 ≤ (max_score − min_score) ≤ 75
AND rank(sandbagger) in bottom 40%
AND rank(harvester) in bottom 40%
```
Too narrow a spread and the scorecard cannot discriminate. Too wide and one
early mistake decides the run. The sandbagger and harvester checks verify the
round-weighting and terminal-stock defences from `08-scoring.md` actually work.

### I12 · Event neutrality
```
|mean_score(events_on) − mean_score(events_off)| < 8 points
AND rank correlation (events_on, events_off) > 0.6
```
Events should reshuffle the middle of the table, not determine it. If rank
correlation falls below 0.6, outcomes are event luck rather than decision
quality, and `EVENT_SEVERITY` is too high.

---

## Failure diagnosis

When an invariant fails, check in this order.

| Failed | Check first | Then | Then |
|---|---|---|---|
| I1 | `σ` saturation exponent | `SHARE_SENSITIVITY` | CPM inflation `φ` |
| I2 | Starting cash | MOQ × lead time | Credit ceiling |
| I3 | Deal-cohort churn 0.44 | P3 pillar weight | Price elasticity η |
| I4 | Gross margin default | Fulfilment cost | Courier mix defaults |
| I5 | Cash timing table (M15) | COD remittance lag | Supplier terms defaults |
| I6 | M7 redistribution loop | Incumbent share calc | — |
| I7 | Study prices | Study error bands | Signal strength of MR-07/12/18 |
| I8 | Map iteration order | Float accumulation order | Unseeded RNG call |
| I9 | The named formula's sign | Clamp bounds | Module ordering |
| I10 | The named decision's cost path | — | — |
| I11 | Anchor scales in `08` | Round weights | Pillar weights |
| I12 | `EVENT_SEVERITY` | Type C probabilities | Type B thresholds |

This table is the harness's most useful output. An invariant that fails without
naming a likely cause gets ignored; one that says "check `σ` first" gets fixed.

---

## Report format

```
VALIDATION RUN  config_hash=a3f91c  2027-03-14 09:22
200 strategies × 20 seeds = 4,000 games · 11m 42s

T2 BASELINE ......................... PASS  (max drift 0.8%)

INVARIANTS
 I1  No dominant strategy ........... PASS  max/median = 1.84
 I2  No death spiral ................ PASS  earliest insolvency R9
 I3  Discounting is a trap .......... PASS  94% of seeds
 I4  Margin viable .................. PASS  8.7%
 I5  Cash binding .................... PASS  31% draw / 4% insolvent
 I6  Share conserves ................ PASS  max error 2.1e-7
 I7  Research pays .................. FAIL  heavy 71.2 > selective 68.9
 I8  Determinism .................... PASS
 I9  Monotonicity ................... PASS  6/6
 I10 No free lunch .................. PASS  56/56 decisions
 I11 Discrimination ................. PASS  spread 51, sandbagger #16
 I12 Event neutrality ............... PASS  Δ4.1, ρ=0.71

>> I7 FAILED. Check first: study prices. Research-heavy spent
>> PKR 4.1M/round and still won — prices are too low relative to
>> the information's value. See docs/11 failure diagnosis.

TOP STRATEGIES   1. balanced 74.1   2. retention_led 72.8
                 3. research_heavy 71.2   4. operational_excellence 70.4
BOTTOM           18. sandbagger 41.2  19. discounter 38.7  20. harvester 34.1
```

Every run writes `config_hash`, so a validation result can always be tied to
the exact configuration it validated.

---

## CI integration

| Trigger | Tiers |
|---|---|
| Every commit | T0, T1, T2 |
| Nightly | T0–T4 |
| Any parameter change outside default | T3, blocking |
| Before a cohort run | T2, T3, blocking |
| Release | T0–T4 |

**A configuration that has not passed T3 cannot be assigned to a live cohort.**
The instructor console enforces this: changing a parameter marks the
configuration unvalidated, and an unvalidated configuration cannot start a run.

This is the mechanism that makes instructor parameter editing safe, and it is
why the harness is a product feature rather than developer tooling.

---

## T4 — Regression on real cohorts

After each cohort, archive: every team's decisions, the config hash, the seed,
and the final state.

T4 replays each archived cohort and asserts identical output. Any engine change
that alters a past cohort's results is flagged — which is either a bug, or a
deliberate change that must be recorded as a new engine version.

This is what preserves the cohort comparability that
`06-build-sequencing.md` identified as the reason to ship early in the first
place. Without T4, that argument quietly stops being true after the second
engine change.
