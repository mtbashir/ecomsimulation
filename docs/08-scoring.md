# 08 — Scoring

Six pillars, 100 points, weights published to students before Round 0.

| Pillar | Weight |
|---|---|
| P1 Profitability | 25 |
| P2 Growth | 20 |
| P3 Customer Value | 20 |
| P4 Operational Efficiency | 15 |
| P5 Cash & Capital | 10 |
| P6 Decision Quality | 10 |

---

## Two structural decisions

### 1. Criterion-referenced, not norm-referenced

Metrics are scored against **published absolute anchors**, not against the
cohort. Contribution margin of 9% scores 50 points whether every rival achieved
12% or 4%.

Three reasons, in order of importance:

1. **Cohort comparability.** Norm-referenced scores cannot be compared across
   sections or across years. Criterion-referenced scores can, which is what
   turns each cohort into calibration evidence (`06-build-sequencing.md`).
2. **Stability at small N.** Z-scores are meaningless with 2–4 teams. Anchors
   work identically at N=2 and N=16.
3. **It is the better lesson.** Students should learn what good looks like in
   absolute terms, not merely that they beat the team next to them.

Competitive ranking still follows — rank the absolute scores. You get both:
*"Team 3 scored 68, which is genuinely good, and placed second."*

The one exception is market share, which is **genuinely zero-sum** and is scored
relatively (P2). Nothing else is.

### 2. Flow metrics weighted by round; stock metrics measured terminally

```
w[t] = t / Σ(1..T)          T = 12  →  Σ = 78
```

Round 1 carries 1.3%, Round 12 carries 15.4%.

| Metric type | Measurement | Examples |
|---|---|---|
| **Flow** — execution during a period | Weighted average across rounds | Service level, delivery success, leakage, order growth, share |
| **Period aggregate** — an accounting fact about the year | Totals, weighted by the thing the ratio is a share of; no round tilt | All three margins, repeat order share |
| **Stock** — accumulated position | Terminal (Round 12) | Cash, runway, customer base, NPS, LTV:CAC |

Later rounds matter more for execution, so improvement is rewarded and late
collapse is punished — but early rounds still count, so sandbagging costs real
points.

The middle row is not the same as the first, and treating it as such was an
error worth naming. A margin is a ratio, and ratios do not average: the
round-weighted mean of twelve monthly percentages paid a team for shrinking,
because the months it shrank in weighed the same as the months it sold in and
happened to be the heaviest three. These are now computed the way a P&L
computes them — over the totals.

---

## P1 — Profitability (25)

| Metric | Pts | Type | 0 pts | 50 pts | 100 pts |
|---|---|---|---|---|---|
| Contribution margin % **before marketing** | 12 | Period aggregate | 14% | 24% | 32% |
| EBITDA margin % | 8 | Period aggregate | −22% | −11% | −2% |
| Gross margin % | 5 | Period aggregate | 30% | 37% | 44% |

Three margins at different levels of the P&L, deliberately. A team can lift
gross margin by dropping low-margin SKUs — and watch contribution margin fall
as fixed costs spread over fewer orders. **No single lever moves all three.**

Two things make that claim true rather than aspirational.

The 12-point margin is read **before marketing**. Marketing sits inside
contribution in the P&L (M14), so while it was scored there, cutting marketing
moved contribution *and* EBITDA — 20 of these 25 points, in the same direction,
off one decision. Above the marketing line, the 12 points measure the economics
of fulfilling an order; marketing's effect lands in EBITDA's 8.

And all three are **period aggregates, weighted by each month's net revenue**,
not round-weighted means of monthly percentages. A margin is a ratio and ratios
do not average: read as a mean, a team that halved its revenue and took a fat
margin on the remainder outscored one that earned a steady margin on twice the
volume. Unlike the operating metrics these carry no round tilt — the year
earned what it earned.

---

## P2 — Growth (20)

| Metric | Pts | Type | 0 pts | 50 pts | 100 pts |
|---|---|---|---|---|---|
| Revenue multiple (R12 ÷ R1) | 8 | Terminal | 0.90× | 1.45× | 2.00× |
| **Market share change (pp)** | 7 | **Relative** | −2.0pp | 0.0pp | +2.5pp |
| Order growth vs baseline | 5 | Flow | −28% | −6% | +22% |

Market share is the only relative metric in the scorecard, because share is the
only thing a team can gain solely by taking it from someone else.

---

## P3 — Customer Value (20)

| Metric | Pts | Type | 0 pts | 50 pts | 100 pts |
|---|---|---|---|---|---|
| LTV : CAC ratio | 6 | Terminal | 1.0 | 2.5 | 5.0 |
| Repeat order share | 5 | Period aggregate | 22% | 30% | 40% |
| Active customer base | 6 | Terminal | 18,000 | 27,000 | 38,000 |
| NPS | 3 | Terminal | 55 | 75 | 88 |

Six points on the base and six on the ratio, not four and eight. The value of a
customer base is how big and how loyal it is, not how efficient the marketing
that built it was; weighted the other way, a team could stop acquiring, watch
the base shrink, and score **better** on customer value for having stopped
spending. Repeat share is taken over total orders for the same reason margins
are: it rises by itself when a team stops acquiring, so a mean of the monthly
figures paid a team for giving up.

LTV is computed from the **actual cohort ledger** (M12), not a formula applied
to averages. A team that bought 30,000 Deal Hunters gets an LTV that reflects
their 0.44 churn, and no amount of blended-average presentation hides it.

---

## P4 — Operational Efficiency (15)

| Metric | Pts | Type | 0 pts | 50 pts | 100 pts |
|---|---|---|---|---|---|
| Service level | 2 | Flow | 93% | 97.5% | 100% |
| Delivery success rate | 6 | Flow | 92.0% | 94.0% | 95.8% |
| Return + RTO cost (% net revenue) | 4 | Flow | 5.5% | 4.2% | 3.2% |
| Inventory turns (annualised) | 3 | Terminal | 8.0 | 13.0 | 20.0 |

Service level carries two points, not four: three weeks of cover absorbs a 16%
forecast miss, so essentially every team serves everything it could sell, and
points nobody can move are points the scorecard is not using. The weight goes
to delivery success, which in a 62%-COD market is the operating number a team
actually lives on.

Inventory turns and in-stock rate pull directly against each other. Maximising
either alone costs the other. That tension **is** the inventory lesson.

---

## P5 — Cash & Capital (10)

| Metric | Pts | Type | Scale |
|---|---|---|---|
| **Runway adequacy** | 5 | Terminal | **Banded — see below** |
| Cumulative free cash flow | 3 | Terminal | −15M → 0 pts · 0 → 50 · +25M → 100 |
| Cash conversion cycle | 2 | Flow | *implemented as net profit margin: −30% → 0 pts · −14% → 50 · −2% → 100* |

Cash conversion cycle in days is not yet tracked, so the two points are carried
by net profit margin, which moves with the same working-capital decisions.
Runway is read **terminally**, as specified: averaging the band across the year
let a team that spent it comfortable and ended on fumes score the same as one
that ended able to keep going.

### Runway is banded, not monotonic

| Terminal runway | Points |
|---|---|
| < 2 rounds | 0 |
| 2–4 rounds | 25 |
| **4–8 rounds** | **100** |
| 8–14 rounds | 60 |
| > 14 rounds | 30 |

**This is the most important anchor in the scorecard.** A team sitting on
14+ rounds of runway in a growing category has failed at capital allocation
just as surely as a team about to run out. Making "most cash wins" the rule
would teach exactly the wrong thing to a room of future operators.

Expect this band to generate the most argument in the first debrief. That
argument is the lesson.

---

## P6 — Decision Quality (10)

| Component | Pts | Basis |
|---|---|---|
| Board memos (rubric, averaged) | 4 | Per-round, rubric in `01-decision-list.md` |
| **Prediction accuracy** | 3 | Retrospective |
| Round 0 plan variance review | 3 | Final review |

### Prediction accuracy — the ungameable component

The memo rubric requires a **falsifiable prediction** each round. The engine
stores it. Three rounds later, the actual value is checked against it.

```
accuracy[t] = 1 - min(1, |predicted - actual| / |actual|)
score       = mean(accuracy) over all rounds with a resolvable prediction
```

Vague predictions score zero because nothing resolves. Precise wrong predictions
score partially. Precise right predictions score fully.

A team cannot write what they think the grader wants, because the grader is the
engine three rounds later. This is the only component of the entire scorecard
that is structurally immune to gaming, and it is the one that most directly
builds commercial judgement.

### Round 0 variance review

The targets each team set in their own founding business plan (D0.14) become
the closing benchmark. Scored on the quality of the variance explanation, not
on the size of the variance.

A team that missed badly and can explain precisely when and why they should
have known scores higher than a team that hit its targets by luck and cannot
account for it.

---

## Anti-gaming design

Students optimise what you publish. Every published scorecard is gamed. The
design goal is not to prevent gaming — it is to ensure **the optimal way to
game the scorecard is to run the business well.**

| Exploit | Counter |
|---|---|
| **Final-round harvest** — cut marketing, brand and capex in R12 to spike profit | Margins are read before marketing and as period aggregates, so cutting spend no longer inflates 20 of the 25 profitability points; the customer base and NPS are terminal and fall; brand equity decays. Measured at 12.1 points below playing it straight |
| **Sandbagging** — coast for six months, sprint for six | Brand equity decays while a team coasts and cannot be bought back inside a quarter, so the sprint starts from a worse position than it would have inherited. Measured at 11.8 points below playing it straight |
| **Sandbagging** — coast early, sprint late | Round weighting still counts early rounds; and cohorts compound, so customers not acquired in R2 cannot be acquired in R10 at the same LTV |
| **Vanity revenue** — deep discount for top-line | P1 (25) and P3 (20) both punish it, and the deal-cohort churn rate of 0.44 collapses LTV:CAC directly |
| **Cash hoarding** | Runway is banded. Hoarding scores 30, the same neighbourhood as near-insolvency |
| **AOV inflation** — drop cheap SKUs to lift AOV | AOV is not scored. Order growth and customer base are |
| **Metric-specific tuning** | Every pillar carries ≥2 metrics that pull in opposing directions. In-stock vs turns; gross vs contribution margin; growth vs LTV:CAC |
| **Memo gaming** | Prediction accuracy is graded by the engine, retrospectively |

### The rule behind the table

> **No metric is scored if it can be moved without moving the business.**

AOV fails this test and is excluded despite being on the dashboard. Revenue
alone fails it. Contribution margin, LTV:CAC and in-stock rate all pass.

---

## Insolvency

A team whose cash goes below zero with no credit headroom is **not eliminated**.
It continues under administration: discretionary spend capped at prior-round
levels, no new capex, no equity raise.

| | |
|---|---|
| P5 score | Set to 0 for the run |
| Other pillars | Scored normally |
| Maximum achievable | 90 |

Elimination teaches nothing to the eliminated. Recovery from administration is
one of the most instructive runs a team can have, and a recovering team should
still be able to place mid-table on the strength of the other five pillars.

---

## Leaderboard visibility

| Rounds | Teams see |
|---|---|
| 0–3 | Own pillar scores only. No cross-team ranking |
| 4–12 | Full leaderboard, all pillars, all teams |

Withholding rank for three rounds lets teams establish a strategy before
anchoring on rivals. Publishing it from Round 4 onward is what makes the
competitive dynamic real for the remaining two thirds of the run.

The leaderboard must display the round-weighting curve alongside it. Teams
leading at Round 5 on 6.4% of the total weight should be able to see that
clearly.

---

## Instructor configuration

Pillar weights are editable within bands, consistent with
`04-configurability.md`.

| Pillar | Default | Green | Red |
|---|---|---|---|
| P1 Profitability | 25 | 15–35 | > 45 — becomes a cost-cutting exercise |
| P2 Growth | 20 | 10–30 | > 40 — rewards unprofitable scale |
| P3 Customer Value | 20 | 10–30 | 0 — removes the retention lesson entirely |
| P4 Operational Efficiency | 15 | 8–25 | > 35 — operations dominate strategy |
| P5 Cash & Capital | 10 | 5–20 | 0 — removes the working-capital lesson |
| P6 Decision Quality | 10 | 5–25 | 0 — outcomes become everything, reasoning nothing |

Weights must sum to 100. **No pillar may be set to zero**, which is why the red
column names 0 for P3, P5 and P6 — removing a pillar removes the behaviour it
protects against, and a scorecard with P3 at zero makes deep discounting
straightforwardly optimal.

Metric anchors are also editable, but any change triggers the 200-strategy
validation run (`04-configurability.md`), because anchors determine which
strategies win.

---

## The debrief question

The scorecard is published in full before Round 0, which means students spend
twelve rounds optimising a known objective function. That is deliberate — it is
what every commercial manager does, and the sim should make the dynamic
visible rather than pretend it away.

So the closing session asks it directly:

> **Did you manage the business, or manage the scorecard? Where did those two
> things come apart, and what did you do when they did?**

Every well-designed incentive system creates that gap somewhere. Finding it is
the most transferable thing in the entire course.
