# 13 — Calibration Log

Domain judgements made about parameter values, and why.

**This file cannot be reconstructed.** Claude can re-derive code from the specs;
it cannot re-derive why you decided RTO should be 22%. Neither will you, in four
months. Record every judgement here as it is made.

Format: one entry per decision, newest first.

---

## Template

```
### YYYY-MM-DD · parameter_name: old → new

**Basis:** where the figure came from — experience, a specific source, a
reasoned argument.

**Confidence:** high / medium / low.

**Invalidated by:** what evidence would change this.

**Downstream:** which invariants or metrics this is expected to move.
```

---

## Entries

### 2026-09-21 · Closing I7 and I11 — six defects, then a recalibration

**Basis:** Measurement, not judgement. Every change below is a bug the engine
or the harness had; the parameter moves are the consequence of fixing them.

**Confidence:** High on each defect. Medium on the re-solved parameter levels,
which are only as good as the targets in `calibrate.py`.

**Invalidated by:** Any real benchmark for the targets; a better model of
supply risk (see the open item at the end).

**Downstream:** Everything. The previous calibration is void.

---

#### 1. M5 never read a single decision

`m05_perception.run` receives `resolved` keyed by **team id** and passed the
whole dict down to its helpers, which then asked it for decision codes:

```python
spend = float(resolved.get("3.9", 0) or 0)     # asks a map of team ids for "3.9"
```

Brand-building spend, creative production spend and the discount rate all read
as **zero, for every team, in every round, in every game ever run**. Brand
equity therefore decayed from its seeded 0.50 to 0.184 for everyone
identically, and since M6 draws 60% of organic traffic from brand equity and
M5 feeds perceived quality and delivery, the perception gap — "the most
valuable number in the sim" per docs/03, and the thing MR-07 exists to sell —
was inert too.

This one bug is most of why I7 could not pass: there was no brand to build, so
there was nothing for a long-horizon strategy to compound and nothing for
research to inform.

#### 2. A 44-day shipment could arrive in 30 days

`arrives = world.round + max(1, round(lead_days / round_days))` — `round()`,
not `ceil()`. A 44-day lead time divided by a 30.44-day round is 1.45, which
rounds **down** to 1. Doubling a supplier's lead time changed nothing, so
EV-03's lead-time shock cost nothing, sourcing carried no lead-time
consequence, and MR-17 warned about an event with no effect.

#### 3. The buyer was clairvoyant

The reorder policy sized the pipeline using `events["lead_time_mult"]` — this
month's realised shock. The month a supplier slipped, the order already
covered the slip. A buyer finds out late; `team.lead_time_belief` now moves
half the gap toward reality each month, which is what makes a forewarning
worth anything at all.

#### 4. A going concern opened below its own steady state

Two seeds were inconsistent with the parameters they were seeded from:

| Seed | Was | Now | Why |
|---|---|---|---|
| `brand_equity` | 0.50 flat | 0.417 (solved) | `alpha/decay` at the default spend |
| `creative_quality` | 0.50 flat | 0.653 (solved) | `kappa*sqrt(spend/ref)/decay` |
| `starting_active_customers` | 11,000 | 26,000 | Round 1 orders hit the baseline |

With M5 inert this did not show. With M5 working, every team spent the game
climbing out of the hole: Round 1 came in a third below the baseline it is
supposed to define, and orders ramped 37% across the twelve rounds. A going
concern opens mid-life; it now opens where the default plan would have put it.

`brand_alpha` 0.10 → 0.05 and `creative_kappa` 0.22 → 0.12 because
`alpha/decay` is where the reference spend settles: at 0.10 the **default**
brand budget saturated the index, and at 0.22 the default creative budget
pinned every team at 1.0. A lever that saturates at its own default is not a
lever.

#### 5. Small games were scaled against a field they did not face

Below four teams the AI roster is padded to four incumbents so a duopoly is
not a tug-of-war. `bootstrap._category_scale` scaled against a fixed reference
of **two**. N=2 and N=3 therefore ran 4-6% under the baseline while every
larger game sat on it. The reference now carries the forced floor; anything the
instructor adds on top of it still costs share, which was the point of holding
the reference fixed.

#### 6. `potential_headroom` 1.45 → 0.66

The three-way constraint `orders = min(potential, traffic, stock)` was
one-sided: `under_marketing` bound in 99% of team-rounds, so seasonality could
not reach orders and nothing you learned about demand could pay. The parameter
also did not mean what it said — it is measured against the **acquisition
pool**, and M7 adds repeat demand on top, so the total-to-traffic ratio it
produces runs about a third higher than the figure. Band and description
corrected; the value is now solved against the measured ratio.

Constraint mix at the default, across a full archetype cohort:

| | under_marketing | wasted_spend | stock_out |
|---|---|---|---|
| Before | 99% | 0% | 1% |
| After | 55% | 43% | 2% |

#### Re-solved parameters

| Parameter | Was | Now |
|---|---|---|
| `channel_k_scale` | 0.969 | 0.703 |
| `cr_base` | 0.0135 | 0.0134 |
| `cogs_scale` | 0.9492 | 0.949 |
| `cohort_freq_scale` | 1.5375 | 1.194 |
| `rating_base` | 2.2891 | 2.289 |
| `potential_headroom` | 1.45 | 0.66 |
| `starting_active_customers` | 11,000 | 26,000 |
| `brand_alpha` | 0.10 | 0.05 |
| `creative_kappa` | 0.22 | 0.12 |

Baseline after re-solving: orders 4,004, sessions 190k, CR 2.11%, AOV 2,959,
GM 37.9%, CM 9.5%, repeat share 35.0%, rating 4.10 — every settled target
inside 1% except CM at +6%, and N-invariant from 2 teams to 16.

**Residual, deliberately left:** Round 1 opens about 18% under the settled
figure, because the cohort compounds across the game. Raising
`starting_active_customers` further closes it — a joint solve of the seed and
the flow knobs lands Round 1 at −7% — but at 52,000 the founding pro-forma
inherits a customer base large enough to push two of the six strategic
directions outside `check_balance`'s ±15% guardrail. The founding round models
a launch that inherits the going-concern base, and that inheritance is the
thing to fix before pushing the seed again. It was a third under with a 37%
ramp before this pass; `test_a_going_concern_opens_at_its_own_steady_state`
holds the line at 20% and 1.30x.

#### EV-03 severity 2.0x for 3 rounds → 2.0x for 2 rounds

Set when a lead-time shock could not cross a month boundary and so cost
nothing. Once it could, three rounds of doubled lead time was the single most
punishing thing in the game and pushed I12 past its own bound (delta 8.4 on a
limit of 8). Two rounds still slips an importer a full month of arrivals,
which is the point of it. I12 now reads 6.8.

---

### 2026-09-21 · The scorecard: five corrections

**Basis:** Each is an accounting or measurement error, found by tracing what
the gaming archetypes were being paid for.

**Confidence:** High.

**Downstream:** I11, and every team's report.

**1. Ratios were averaged.** Contribution, EBITDA and gross margin were read as
the round-weighted mean of twelve monthly percentages. A margin is a ratio, and
ratios do not average: a team could stop marketing in Month 10, watch orders
halve, take a fat margin on what was left, and outscore a team that earned a
steady margin on twice the volume — in the three rounds the round weights make
heaviest. Margins are now aggregates over the period, weighted by each month's
net revenue, and carry no round tilt, because a margin is an accounting fact
about the year rather than a series of decisions. Repeat order share is a ratio
too, and is now taken over total orders.

**2. Profitability moved on one lever.** docs/08 says the three margins sit at
different levels of the P&L "so that no single lever moves all three". They did
not: marketing is inside contribution, so cutting it moved contribution **and**
EBITDA — 20 of profitability's 25 points, in the same direction, from one
decision. The 12-point metric is now contribution **before marketing**: the
economics of fulfilling an order, with marketing left to EBITDA's 8 points.

**3. Growth was path-independent.** Revenue multiple read the closing month
against the opening one and nothing in between, so coasting for six months and
sprinting for six scored as though the team had grown all year. It is kept as
docs/08 specifies — sandbagging no longer exploits it, because brand equity now
decays while a team coasts and cannot be bought back inside a quarter. The
defence belongs in the engine, not in the scorecard.

**4. P5 diverged from its own spec.** docs/08 specifies runway read terminally
(5 points), cumulative free cash flow (3) and cash conversion cycle (2). The
implementation was a round-weighted average of the runway **band** at 7 points
plus a net-margin proxy at 3, and free cash flow was absent. Averaging the band
let a team that spent the year comfortable and ended on fumes score the same as
one that ended able to keep going.

**5. Seven of the anchors were set against a business this engine does not
build.** Measured across the archetype cohort, four metrics were decided before
the game began — NPS scored 100 for 99% of teams, service level for 97%,
leakage for 95%, inventory turns for 55% — while active customers floored at 0
for 38% and EBITDA margin for 41%. That is 14 of 90 scorable points handed out
uniformly and another large block pinned at zero, which is most of why the
scorecard's spread sat at 31 against a target of 35.

| Metric | Was (0/50/100) | Now |
|---|---|---|
| Contribution margin | 0% / 9% / 18% | *(replaced by CM before marketing)* 14% / 24% / 32% |
| EBITDA margin | −12% / −2% / +6% | −22% / −11% / −2% |
| Gross margin | 25% / 38% / 50% | 30% / 37% / 44% |
| Revenue multiple | 0.85 / 1.30 / 2.20 | 0.90 / 1.45 / 2.00 |
| Order growth | −5% / +10% / +45% | −28% / −6% / +22% |
| Active customers | 20k / 45k / 90k | 18k / 27k / 38k |
| NPS | 0 / 24 / 55 | 55 / 75 / 88 |
| Repeat share | 10% / 22% / 40% | 22% / 30% / 40% |
| Service level (4 pts → 2) | 80% / 93% / 99% | 93% / 97.5% / 100% |
| Delivery success (4 pts → 6) | 93.6% / 95% / 96.4% | 92% / 94% / 95.8% |
| Leakage | 11.5% / 8.5% / 5.5% | 5.5% / 4.2% / 3.2% |
| Inventory turns | 4.0 / 7.5 / 12.0 | 8.0 / 13.0 / 20.0 |

Service level drops from 4 points to 2 because it is the one operating metric
this business cannot fail at — three weeks of cover absorbs a 16% forecast miss
— and its weight goes to delivery success, which in a 62%-COD market is the
number a team actually lives on. Within P3, LTV:CAC goes 8 → 6 and the active
customer base 4 → 6: the value of a customer base is how big and how loyal it
is, not how efficient the marketing that built it was, and at eight-versus-four
a team could stop acquiring, watch the base shrink, and score **better** on
customer value for having stopped spending.

---

### 2026-09-21 · The harness: three corrections

**1. `research_selective` was not selective.** It bought four studies a month,
three of which drove no decision at all — research_heavy with a smaller
invoice. It now buys what it acts on.

**2. `harvester` measured the wrong thing.** Its strip round returned a bare
dict, so it did not just cut spend: it dropped positioning, discount, COD and
every other lever back to the engine default. It also ignored its variation
parameter, so all ten of its instances were the same run repeated, against a
suite that exists to map a response surface.

**3. `MR-10`'s trigger was dead code.** The archetype fired on
`reported > 0.30`; MR-10 reports a blended **monthly churn rate**, which runs
6-9%. The branch could never execute.

---

### 2026-09-21 · I7 and I11 restated

**I7** was failing as a measurement problem on top of an engine problem. The
main draw seats 8 instances out of 200 by hash, so research_zero and
research_selective met different fields at different variations; each mean
carries a standard error near 0.6 points, which is larger than the effect. I7
is now measured **paired** — the three research archetypes in the same game, at
the same variation, against the same five opponents. It reads +0.30 to +0.46
and is stable from 120 games upward.

**I11's rank clauses are gone, replaced by a margin against playing straight.**
Ranks 9 to 15 of this field sit inside 1.7 points, so "bottom 40%" was reading
noise: the same engine put harvester at #10 and at #15 depending only on how
many games were run. What docs/08's defences actually claim is that neither
trick beats playing it straight. Before these fixes harvester came in **1.3
points** under balanced; it now comes in **12.1** under, and sandbagger 11.8
under. The threshold is 5. The spread clause is unchanged at 35-75 and now
reads 36.

**This is a change to an invariant, and it should be reviewed.** The case for
it is that a rank in a 1.7-point band is not a measurement. The case against is
that the original clause is what docs/11 wrote down. Reverting it is a
four-line change in `validate.py`; the engine and scoring fixes above stand
either way.

---

### Still open: operations research cannot pay

Every response to MR-17's lead-time warning loses money:

| Response | Net score |
|---|---|
| Raise safety stock to 4.5 weeks | −0.21 |
| Source the range locally for a month | −1.03 |
| Switch to the fast supplier | −1.08 |
| Do nothing | 0.00 |

The reason is that **stock binds in 2% of team-rounds**. A 16% forecast error
against three weeks of cover does not produce stock-outs, so nothing a team
learns about supply can pay for itself, and MR-17, MR-09 and MR-15 are priced
for information that has no decision to improve. MR-01 is currently the only
study in the catalogue that earns its price (+0.24 net of 40,000 a month), and
I7 passes on that one study.

Closing this means making supply genuinely risky — a real MOQ bite, supplier
reliability, or forecast error that the order-up-to policy cannot absorb — and
then re-pricing the operations studies against what acting on them is worth.
It is the same shape of problem the demand side had before this pass, and it is
not a parameter nudge.


### 2026-09-19 · Option A — lower capital. Profitability is now reachable.

**DECIDED: starting capital 25M -> 12M, credit facility 24M, fixed costs cut
to ~1.35M** (payroll 1.0M -> 500k, warehouse 340k -> 250k, tech 180k -> 120k,
CS 62k -> 48k per agent).

This resolves the incompatibility recorded in the previous entry. With a
smaller balance, a smaller burn still exhausts capital over twelve rounds, so
fixed costs can sit below the best reachable contribution:

| | Before | After |
|---|---|---|
| Starting capital | 25M | **12M** |
| Fixed costs / round | 1.93M | **~1.35M** |
| Baseline EBITDA | -1.16M | **-390k** |
| Best archetype EBITDA | -678k | **+146k** |
| Archetypes turning a profit | **0 of 20** | **3 of 20** |
| Baseline cash at Round 12 | 0 of 25M | **0 of 12M** |

Coasting is still fatal - a do-nothing team ends at zero - and good play now
clears its cost base. Both goals hold for the first time.

**The credit facility matters more than it looks.** At 12M it produced the
same failure as before: 52% of viable strategies insolvent, retention_led 98%,
because working capital demands did not shrink when the buffer halved. A
business buying ~7M of stock a month on 45-day terms needs roughly two months
of facility available. At 24M, viable-strategy insolvency is 4%.

Scoring anchors moved with the economics: P1 EBITDA from the frontier-of-losses
scale (-22/-14/-5%) back to one where breakeven is the midpoint (-12/-2/+6%),
and the runway bands re-based for a 12M balance.

**The cash-trajectory test was reformulated rather than nudged again.** It had
measured swings as a share of starting capital, which is scale-dependent - the
same cycle looks twice as violent against 12M as against 25M. It now checks
for a spike against the trajectory's own typical step, which is what the
concern always was.


### 2026-09-19 · Repeat share raised to 35% — and why the two goals cannot both hold

**DONE: repeat-share target 22% -> 35%.** Baseline re-solved and holding;
`cohort_freq_scale` 1.02 -> 1.54. A welcome side effect: **CAC now derives to
PKR 543**, much closer to the 850 originally quoted than the 452 it had drifted
to. `sandbagger` also fell from #11 to #13, into the bottom 40% that I11 wants.

**It did not make retention pay, and the reason is arithmetic, not mechanics.**
The mechanics are now correct (see the previous entry). At 400k of retention
spend, repeat share goes 29% -> 46% and net revenue rises 9.16M -> 9.47M. That
is +310k of revenue at ~24% pre-marketing margin = **+75k of contribution for
400k of spend**. Retention loses money at any level.

To break even, 400k of retention must generate ~555 extra orders. It generates
about 105, because repeat demand substitutes for acquisition more than it adds.

### THE STRUCTURAL FINDING — the two goals are mutually exclusive

Writing it out plainly, because it governs everything above:

- Baseline contribution is **897k** a round (that IS the approved 9% CM).
- Best contribution across all twenty archetypes is **1.63M** a round.
- Fixed costs are currently **1.93M**.

"Coasting is almost fatal" means a do-nothing team exhausts 25M in 12 rounds,
so it must burn ~2M a round: `897k - fixed = -2M`, giving **fixed = 2.9M**.

"Good play reaches profit" means `1.63M - fixed > 0`, giving **fixed < 1.63M**.

**There is no value of fixed costs that satisfies both.** The gap between
baseline and best contribution (897k vs 1.63M) is smaller than the burn that
"almost fatal" requires. No amount of payroll cutting resolves this - it is a
statement about how much strategy moves contribution.

Three ways out, and this one genuinely needs a decision:

| | Change | What it costs |
|---|---|---|
| **A** | **Lower starting cash** 25M -> ~12M. A 1M/round burn then exhausts capital in 12 rounds, so fixed can sit near 1.6M and good play turns a profit | Teams have less room to invest; the credit line carries more of the game |
| **B** | **Widen the contribution spread** - make strategy move unit economics harder (stronger premium pricing, bigger ops savings, real scale economies) | Real engine work, and it risks I1 if one lever becomes too strong |
| **C** | **Drop "good play reaches profit"** - teach the path to profitability instead, with P1 anchored to the reachable frontier as it is today | The sim stays one where nobody ever turns a profit |

C is what is currently implemented and it is defensible for a 12-month horizon:
most Pakistani D2C brands at 12M GMV are not profitable, and "who improved
fastest toward breakeven" is a real board question. But it should be a choice,
not a default.


### 2026-09-19 · Burst 3b — working capital smoothed; inventory made a decision

**DECIDED: smooth the working-capital cycle.** The ~40% cash swings were not
"what this business does" - they were two modelling artifacts.

1. Supplier terms and COD remittance were rounded to whole rounds, so a month
   of purchasing landed in a single lump. Both now book across the rounds their
   lag actually spans (`M15._schedule`), and terms moved 30 -> 45 days.
2. The bootstrap seeded two discrete purchase orders whose payables piled up a
   few rounds in. It now seeds the **steady-state ledger** - one round of
   purchases due next round plus the tail of the one before, and COD already
   despatched and not yet remitted.

**Peak cash movement fell from 41% to 24%.** The test is back to a flat 30%
with no exclusions and no xfail. I had moved that threshold five times across
bursts 2 and 3; the cause was findable and none of those moves were justified.

**DECIDED: keep growth_max insolvency.** Aggressive growth that outruns its
working capital should bankrupt a team, so `growth_max` is reclassified as an
archetype that exists to fail rather than a viable strategy the invariants must
protect.

### 2026-09-19 · Option A — payroll cut, and three more dead mechanisms

**DECIDED: `payroll_base` 1.4M -> 1.0M.** Fixed costs fell from 2.83M to
1.94M a round.

Chasing why retention never paid uncovered three defects, each of which had
been silently live for the whole project:

**1. Churn modifiers were never applied at all.** `retention_effect` and
`experience_penalty` were written by M13 and read by M12 - which runs first.
`ctx` is rebuilt every round, so both always read zero. **Churn has been the
flat base rate since the ledger was written**, meaning retention spend did
nothing and service failure had no downstream cost. `experience_penalty` now
persists on the team (a deliberate one-round lag that only exists if the value
survives the round); `retention_effect` resolves in M0, same round.

**2. Returning customers generated no traffic.** Every order required a session
from paid or organic traffic, so a loyal customer still needed a paid click to
come back. Repeat demand was therefore capped by marketing spend. Returning
visitors now arrive direct, sized from the cohort ledger.

**3. Returning traffic converted at the blended rate.** Sessions were sized in
M6 using an elevated repeat conversion rate and then converted in M8 at the
cold rate, so loyal customers delivered a fraction of the orders the ledger
says they place. M8 now converts cold and returning traffic separately.

Also: reported `conversion_rate` was the modelled base rate rather than orders
over sessions (the docs/10 definition). Once returning traffic converts at its
own rate the two diverge, and the solver was fitting the wrong number.

**Option A did NOT solve the open question.** Best EBITDA across all twenty
archetypes is now **-678k a round against 1.94M of fixed costs**, so
profitability is still unreachable, `cash_preservation` still ranks third, and
`retention_led` still ranks eighteenth.

Two consequences to weigh:

- **`growth_max` insolvency fell from 52% to 9%.** The extra headroom from the
  payroll cut undid the "keep growth_max insolvency" decision of the same day.
- **Retention still does not pay.** At the approved 22% repeat share the
  installed base buys about 0.05 times per round, so a retained customer is
  worth very little however well retention works. **This is a consequence of
  the repeat-share target itself, not of the retention mechanics**, which are
  now correct. Raising the repeat-share target (or purchase frequency) is the
  lever that would make loyalty a winning strategy.

### SUPERSEDED — earlier framing of the open question

`cash_preservation` ranks **#1 of 20**, and the cause is structural rather than
a bad anchor:

- The business cannot reach EBITDA breakeven (burst 3, finding 7), so **cutting
  spend always improves P1**, and nothing pushes back hard enough.
- **LTV:CAC rewards not acquiring customers.** A team that acquires almost
  nobody has excellent unit economics and no business. This is the same class
  of defect as the harvester exploit, but it cannot be fixed by changing when
  CAC is measured - the ratio itself is scale-blind.

Three ways out, in order of how much I would trust them:

| | Change | Cost |
|---|---|---|
| A | Make profitability reachable - `payroll_base` 1.4M -> ~1.0M | Softens "coasting is almost fatal", which was an explicit decision |
| B | Pair LTV:CAC with scale - reweight P3 toward absolute customer value | Departs from the published docs/08 weights |
| C | Accept and teach it - "why did shrinking win?" is a real debrief | Leaves a scorecard that rewards shrinking |

This is a judgement about what the course should teach, not a parameter to
tune, so it is left open.


### 2026-09-19 · Burst 3 — balance (11 of 12 invariants)

Seven scoring and engine defects found by the invariant suite. Each was a real
bug, not a tuning gap; the archetypes designed to fail were what surfaced them.

**1. Growth was measured against the team's own Round 1.** Sandbagger coasted
six rounds to suppress its own denominator, then scored 19.8/20 on growth off
the trough it had dug. Growth is now measured against the shared starting
position. *Sandbagger fell from #1 to #11.*

**2. LTV:CAC read ~0.25 for every team** — it charged acquisition cost twice
(contribution margin is already net of marketing, then divided by CAC again)
and excluded the customer's first order. LTV now uses pre-marketing
contribution and counts the acquisition order. **Ratios now run 1.67-2.71,
with discounter at 0.23** - the deal-cohort trap finally visible in the metric
built to show it.

**3. LTV:CAC used terminal CAC**, so a team that stopped marketing in the last
rounds had CAC near zero and scored maximum. The scorecard was paying for the
harvest it exists to punish. Now lifetime marketing over lifetime customers
acquired, which timing cannot game.

**4. P4 anchors were never updated after burst 2 rebased courier success.**
Every team maxed operations, 15 points of dead weight. Re-anchored twice, to
the reachable frontier.

**5. Inventory turns was a hardcoded 50** for every team - three more dead
points. Now computed from average inventory and COGS flow.

**6. Administration capped spend at the prior round**, which constrains nothing
for a team that blew up spending 3x. Now halves discretionary spend and blocks
research as well as capex.

**7. No strategy could reach EBITDA breakeven.** Best achievable is
-1.28M/round against fixed costs of 2.17M; the contribution ceiling is ~0.9M,
which IS the approved 9% CM. The scorecard anchors assumed a profitable
business; what we calibrated is a scaling startup. **Re-anchored P1 EBITDA to
the reachable frontier (-22% / -14% / -5%) and re-banded P5 runway to the burn
(<1 fatal, 2.5-6 ideal, >10 under-invested).** The business is unchanged - the
ruler was wrong, not the thing being measured.

**Judgement: `credit_ceiling` 15M -> 25M.** At 15M, coasting consumed exactly
the starting capital over 12 rounds, leaving no headroom for any strategy at
all: retention_led died 41% of the time, tech_led 61%. Raising the ceiling
keeps the burn and keeps coasting fatal - a coasting team still ends at zero,
now carrying interest - while letting a team with a plan fund it at 22% p.a.
*Viable-strategy insolvency fell from 22% to 1%.* Still in the green band.

**Open: I11 scorecard discrimination.** Spread is 29 points against a 35-75
target; sandbagger #11 and harvester #10 against a bottom-40% (#13+)
requirement. Both are now below balanced, so the defences work directionally.
Two known causes: P6 is constant in a scripted harness (real memos and
prediction accuracy add ~6 points of live spread), and **P4 is compressed
because the engine auto-reorders inventory, so decision 7.1 is not really a
team decision yet.** The second is a genuine finding for a later burst, not a
tuning problem.


### 2026-09-19 · Burst 2 — baseline now holds at all N (T2 green)

Solved numerically (`calibrate.py`), not by hand. Nine metrics within
tolerance at N = 2, 4, 8, 12, 16 over 12 rounds. Four judgements were forced
by the baseline being over-determined; each is reversible with one line.

**1. Baseline revenue of 12M is GROSS, not net.** 4,000 orders x PKR 3,000 =
12M is GMV. Net revenue after returns, RTO and failed delivery lands at
~9.2M. The spec's own definition (`docs/10`) makes revenue_net post-leakage,
so 12M cannot be net at these volumes. **Target is now `revenue_gross`.**
*Invalidated by:* deciding 12M should be net, which needs ~5,200 orders.

**2. CM 9% held; marketing default set to 1.48M (was 2.0M); CAC derives to ~477.**
GM 38%, CM 9% and marketing 1.8M cannot coexist with realistic Pakistani
fulfilment costs (courier ~PKR 173/order, RTO round-trips, gateway fees) - at
1.8M marketing CM is ~4.4%. CM is wired into the scoring anchors, so it was
held. **The earlier CAC 850 is dropped as a target; it was inconsistent.**
*Confidence:* medium. CAC ~477 is on the low side for Pakistani D2C personal
care; PKR 600-900 is more typical. *Invalidated by:* choosing to hold CAC 850 instead,
which means CM ~4% or lower fulfilment costs.

**3. Baseline is EBITDA-negative (~-1.3M/round) and burns ~2.1M cash/round.**
Contribution +9.1% but fixed costs (payroll 1.4M, warehouse 340k, tech 180k,
CS 250k) exceed it, and inventory is bought ahead of sale. **A team that does
nothing ends Round 12 with ~1.6M of 25M - and with events on, at zero.**
Inaction is close to insolvency by design.

**DECIDED 2026-09-19: keep `payroll_base` at 1.4M. Coasting is almost fatal.**
Basis: matches how a 12M-GMV D2C brand with ~15 staff actually feels, and
gives the runway lesson teeth. Softer setting (0.9M, ~1.6M burn, ~7M left at
R12) is retained as the option for an undergraduate or pilot cohort.
*Watch in burst 3:* I2 - a team that fumbles R1-R3 may enter administration by
R8. That is acceptable; elimination is not, and the engine does not eliminate. Defensible - a 12M-GMV D2C brand with ~15 staff does burn,
and it gives the runway lesson teeth. **Left as-is; needs an explicit
decision.** *Alternative:* `payroll_base` 1.4M -> 0.9M gives ~-1.0M/round.
*Watch in burst 3:* invariant I2 (no death spiral) - teams that experiment
early will burn faster than baseline.

**4. Courier success rebased to pure logistics (0.94-0.975).** The earlier
0.84-0.92 figures were overall delivery success including customer refusal;
RTO then charged refusal a second time. Total leakage was 30%; now ~21%.
*Confidence:* high on the structure; medium on the exact rates.

**5. T2 runs with `events_enabled = 0`**, as docs/07 and docs/11 specify. The
first solve was accidentally events-on and drifted 5% on orders once the
switch existed. Calibration is always events-off; balance (burst 3) is
events-on.

**Structural fixes that changed levels (not judgements):** AOV now derives
from the SKU basket rather than a free parameter, so GM follows from what is
in the cart; `units_per_order` 1.52 -> 2.424 to hit AOV 3,000 on the
14-SKU basket. Reorder policy now targets cycle + pipeline + safety stock
(safety alone left every team a round short). Forecast basis is
`min(potential, traffic_capacity)` - forecasting on raw potential over-ordered
by the 45% headroom. Bootstrap seeds one round of demand in the supplier
pipeline, payable Round 1, so a going concern starts mid-cycle rather than
placing nothing in Round 1 and lurching. Category size is scaled from the
actual logit at seeded state (`bootstrap._category_scale`), so per-team cash
and orders are identical at N = 2 and N = 16 by construction. Channel `k_base` x4.0 and
cohort `freq` x0.27 baked into `channels.csv`; the scale handles sit near 1.0.

**Solved values (events off):** `cr_base` 0.0175 · `cogs_scale` 0.975 ·
`channel_k_scale` 1.086 · `cohort_freq_scale` 1.039 · `potential_headroom`
1.45 (per-team potential = 1.45 x baseline orders, so traffic binds first,
which matches how a D2C brand at this size actually feels).


### 2026-09-19 · Initial parameter set — all values

**Basis:** Structurally reasoned by Claude, not researched. Relationships and
relative magnitudes are argued in `docs/07-engine-chain.md`; the specific
figures are calibration starting points.

**Confidence:** Low on absolute values. Medium-high on structure and on the
direction and rough magnitude of each relationship.

**Invalidated by:** Any real Pakistani e-commerce benchmark. Expected to be
replaced wholesale during or after the first cohort.

**Downstream:** Everything. Burst 2 exists to make these hold the baseline;
burst 3 exists to make them balanced.

**Explicitly flagged as most likely wrong:**

| Parameter | Default | Why it is suspect |
|---|---|---|
| `rto_base` | 0.18 | Category- and courier-dependent; the figure you personally know best |
| `cod_share_base` | 0.62 | Shifting fast in the real market |
| `cr_base` | 0.021 | Varies hugely by category and traffic mix |
| `aov_base` | 3000 | Entirely category-dependent |
| channel `churn_base` | see `channels.csv` | The deal-driven 0.44 is the most consequential single number in the engine and the least evidenced |

---

## I7 — why "research pays" could not pass, and what it took (CLOSED 2026-09-21)

**Superseded.** The diagnosis below was right about the symptom and wrong about
the cause. Traffic did bind in 99% of team-rounds, and perfect free foresight
was worth 0.22 points. But the reason a long-horizon strategy had nothing to
compound was not the traffic ceiling alone: M5 could not read a decision, so
brand equity was inert for every team in every game (see the entry at the top
of this file). Raising channel `k_base` would have papered over that.

The prediction below that `k_base` x1.8 lifts I11's spread from 31 to 45 was
also an artefact: it moves the spread by shifting the *level* of every metric
against anchors that were never re-fitted, not by discriminating better. After
re-anchoring, the same change leaves the spread near 31.

Kept for the record, because the constraint-mix measurement is still the right
way to diagnose this class of problem.

---

## I7 — the original diagnosis (2026-09-20)

Chased to the bottom. Research is not the problem.

**The binding constraint is `under_marketing` in 99% of team-rounds.** M8
documents a three-way constraint as the spine of the simulation —
`orders = min(potential, traffic_capacity, stock_capacity)` — and in practice
only one side of it ever binds. Measured over a balanced cohort:

| Constraint | Share of team-rounds |
|---|---|
| under_marketing | 99% |
| stock_out | 1% |
| wasted_spend | 0% |
| balanced | 0% |

Demand potential runs 1.24×–2.11× realised orders. A team never sells what it
could sell, because traffic caps it first, every round.

Three consequences:

1. **Seasonality cannot reach orders.** The index swings 0.88 to 1.45 and
   realised orders move by 15%. A demand peak you cannot serve is not a peak.
2. **Stock never binds.** In-stock is 100.0% in all twelve rounds, including
   the 1.45 peak, with nothing lost to stock-out. Safety stock is therefore
   pure holding cost with no upside, which is why every scripted action that
   raises it scores worse.
3. **The debrief diagnosis is degenerate.** Every team is told
   "under-marketing" in every round.

**The ceiling on research value.** Give a team perfect, exact, free foresight
of the seasonal index and let it time all three paid channels against it:

| | Score |
|---|---|
| Blind | 71.84 |
| Perfect free foresight | 72.06 |

**0.22 points.** No price makes MR-01 pay, because the information is worth
almost nothing while traffic binds. Acting on the perception gap (MR-07) is
worth about 0.4; acting on the lead-time shock (MR-17) is negative, because
switching supplier costs more than the shock does.

### What would fix it

Raising channel `k_base` so traffic capacity is comparable to demand
potential. Measured:

| `k_base` | under_marketing | wasted_spend | stock_out | balanced | I11 spread |
|---|---|---|---|---|---|
| ×1.00 (today) | 99% | 0% | 1% | 0% | 31 |
| ×1.35 | 93% | 6% | 1% | 0% | 40 |
| ×1.80 | 59% | 33% | 6% | 2% | 45 |

At ×1.8 the three-way constraint the design calls for actually appears, and
seasonally-timed marketing becomes worth about 0.65 points instead of 0.22.
I11's spread also moves from 31 toward and past its 35 target, which says the
traffic ceiling was suppressing scorecard discrimination too.

**Not done here.** It moves every calibrated number — baseline contribution
margin goes 7.9% → 13.4% at ×1.8 — and needs a full recalibration pass against
I1–I5 rather than a parameter nudge. It is a decision about the model, not a
bug fix.

Until then I7 is correctly reported as failing. The invariant is right; the
engine does not yet earn it.

*(2026-09-21: it earns it now. The constraint mix reads 55/43/2 rather than
99/0/1, but the change that mattered was fixing M5, not raising `k_base`.)*
