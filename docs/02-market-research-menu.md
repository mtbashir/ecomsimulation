# 02 — Market Research Menu

The Markstrat mechanism, ported. Teams buy information from a priced menu each
round. Every study has a **cost**, a **lag**, and an **error band**. Some have
**systematic bias**, not just noise.

**Design intent:** the lesson is not "research is good." It is *"what is this
answer worth to me, and how wrong might it be?"* A team that buys everything
runs out of cash. A team that buys nothing flies blind into the Round 6 price war.

---

## What teams get free

Free data is real but **partial and partly biased** — which is the point.

| Free | Accurate? |
|---|---|
| Own P&L, cash flow, balance sheet | Exact |
| Own sessions, CR, AOV, orders, revenue | Exact |
| Own inventory position and stock-outs | Exact |
| Own rating, review count, CSAT | Exact |
| Own return rate and delivery success | Exact |
| **Platform-reported ROAS by channel** | **Biased +25–40% (over-attributed)** |
| Total category size | ±15%, rounded |
| Published competitor list-prices (scraped) | Exact, but list price only — not net of promo |

The platform-ROAS bias is the single most instructive line in the sim. Teams
optimise against it for four rounds, then buy **MR-12** and discover their
best-performing channel was mostly claiming credit for organic demand.

---

## The menu

Lag 0 = delivered with this round's results. Lag 1 = delivered one round later.
Error band ≈ 95% interval on the reported figure.

### Tier 1 — Market & Competition

| Code | Study | Tells you | Price (PKR) | Lag | Error | Notes |
|---|---|---|---|---|---|---|
| MR-01 | Category Demand & Seasonality | Category size, growth, **next 3 rounds' seasonal index** | 40,000 | 0 | ±8% | The cheapest high-value study. Most teams find it in Round 5, too late |
| MR-02 | Competitor Price Tracker | Every team's avg net selling price and discount depth | 50,000 | 0 | ±3% | Net of promo — the free scrape is not |
| MR-03 | Market Share Report | Revenue and order share by team | 60,000 | 0 | ±5% | |
| MR-04 | Competitor Ad Spend Estimate | Est. spend by channel by competitor | 75,000 | 0 | ±20% **and biased −10%** | Deliberately unreliable. Teaches that competitive intel is an estimate |
| MR-05 | Category Signal Report | Forward-looking: entrants, regulation, supply signals | 45,000 | 0 | Qualitative | Gives a 1-round warning on ~60% of events |

### Tier 2 — Customer & Brand

| Code | Study | Tells you | Price | Lag | Error | Notes |
|---|---|---|---|---|---|---|
| MR-06 | Segment Size & Needs | Segment sizes, price sensitivity, attribute importance weights | 90,000 | 1 | ±6% | Valid ~3 rounds. Without it, segment targeting in 6.2 is guesswork |
| MR-07 | **Brand Perception Tracker** | Your and competitors' *perceived* quality / value / delivery reliability | 75,000 | 0 | ±7% | **Core study.** The only way to see the perception-reality gap before it bites |
| MR-08 | Brand Funnel Study | Awareness → consideration → preference, by segment | 60,000 | 1 | ±8% | Justifies 3.9 brand spend; without it brand spend looks like waste |
| MR-09 | NPS & CSAT Deep-dive | NPS drivers, complaint themes | 30,000 | 0 | ±5% | Cheap. Usually the first sign of an ops problem |
| MR-10 | Cohort & Churn Analysis | Your retention curves by acquisition cohort and channel | 40,000 | 0 | ±4% | Reveals that Deal Hunter cohorts never repeat |

### Tier 3 — Channel & Marketing

| Code | Study | Tells you | Price | Lag | Error | Notes |
|---|---|---|---|---|---|---|
| MR-11 | Channel CAC & ROAS Benchmark | Market-level CAC, CPM, CTR by channel | 50,000 | 0 | ±10% | Tells you if your CAC is bad or the market's is |
| MR-12 | **Attribution Study (MMM-lite)** | *True incremental* contribution by channel vs platform-reported | 110,000 | 1 | ±12% | **The most expensive and most valuable study in the sim** |
| MR-13 | Marketplace Ranking Report | Your category ranking, marketplace share | 25,000 | 0 | ±5% | Only useful if 4.1 is on |
| MR-14 | Creative Effectiveness Pre-test | Creative Quality Score *before* you spend behind it | 20,000 | 0 | ±10% | Cheap insurance on a large spend |

### Tier 4 — Operations & Product

| Code | Study | Tells you | Price | Lag | Error | Notes |
|---|---|---|---|---|---|---|
| MR-15 | Delivery & Logistics Benchmark | Courier SLA, success, RTO by courier vs market | 30,000 | 0 | ±4% | Courier stated rates drift from actual — this shows actual |
| MR-16 | Return Reason Analysis | Return drivers by SKU and reason code | 22,000 | 0 | ±3% | Distinguishes quality returns from expectation returns |
| MR-17 | Supplier & Lead Time Intelligence | Supplier reliability, **lead-time forecast next 2 rounds** | 50,000 | 0 | ±15% | Forewarns the Round 5 supply disruption ~70% of the time |
| MR-18 | Product Concept Test | Demand estimate for a private-label concept pre-launch | 70,000 | 1 | ±15% | Should gate decision 1.3. Most teams skip it and regret it |

### Tier 5 — Premium & Conditional

| Code | Study | Tells you | Price | Lag | Error | Notes |
|---|---|---|---|---|---|---|
| MR-19 | Full Competitive Dossier | MR-02 + MR-03 + MR-04 **plus competitor stock position** | 200,000 | 0 | ±5% | Costs 1.08× buying the three separately, but tightens MR-04's band from ±20% to ±5% and adds stock data. Genuinely good value — and a big cash hit |
| MR-20 | Q-Commerce Readiness | City-level demand, dark-store unit economics | 90,000 | 0 | ±10% | Available from Round 4 only. Effectively required before 4.3 |

---

## Economics of the menu

| | PKR |
|---|---|
| Buy everything, one round | 4,920,000 |
| Typical sensible spend per round | 300,000 – 600,000 |
| Round-0 monthly marketing budget | 1,800,000 |
| Starting cash | 25,000,000 |

Buying the full menu every round would consume roughly **twice the entire
starting cash balance** across ten rounds. The budget constraint is real and
binding, which is the whole design.

## Subscriptions

Any study may be bought as a **3-round subscription at 2.5× single price**
(≈17% saving), delivered automatically each round.

Teaches commitment vs flexibility: cheaper per unit, but you are locked in when
Round 6 turns out to need completely different information.

---

## Implementation rules

These matter more than the prices. Get them wrong and the mechanism breaks.

1. **Seeded noise.** Reported value = true value × (1 + ε), with
   ε ~ Normal(0, σ) and σ = (error band) / 2. The seed must be
   `hash(team_id, round, study_code)` — **fixed**, so re-buying the same study in
   the same round returns the identical number. Without this, teams re-buy to
   average out the noise and the uncertainty lesson evaporates.

2. **Bias is separate from noise.** MR-04 reports at 0.90 × true before noise is
   applied. Platform-reported ROAS reports at 1.25–1.40 × true. Neither is ever
   corrected by re-purchase. Bias is a *property of the source*, and teams should
   learn to distinguish "noisy" from "wrong in a consistent direction."

3. **Lag is enforced at delivery, not at purchase.** A Lag-1 study bought in
   Round 4 shows Round 4 data, delivered with Round 5 results. It is history by
   the time you read it. This is exactly why MR-12 is hard to use well.

4. **Purchases are visible in the P&L, invisible to rivals.** Research spend hits
   your opex. No team sees another's research purchases — including via MR-19.

5. **Decay on validity.** MR-06 segment weights drift ~4% per round. A Round-2
   purchase is materially stale by Round 6. The report should carry its own
   "as of Round N" stamp and nothing should warn teams that it has aged.

6. **No refunds, no previews.** Study descriptions state what the study covers,
   never what it will say.

---

## Why this is the best-value mechanism to build

Roughly two days of engine work. In exchange it delivers:

- A hard budget trade-off every single round
- The distinction between data and information
- The distinction between noise and bias
- A reason to plan two rounds ahead (lags)
- A debrief slide that ends the argument: *"Team 4 spent PKR 2.1M on research
  across ten rounds and finished first. Team 7 spent PKR 180k and finished
  seventh, and spent Rounds 6 through 9 reacting to things Team 4 saw coming."*

No other single mechanism in the specification returns as much teaching value
per hour of build.
