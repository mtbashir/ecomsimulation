# 00 — Game World & Baseline Conditions

Every number in the decision list and research menu is scaled to these baselines.
Change these and you must rescale research prices, capex costs and budgets with them.

## Premise

Each team runs a Pakistani direct-to-consumer e-commerce brand in **Personal Care &
Home Essentials**. Teams compete for one shared demand pool. Two AI-controlled
incumbents hold the balance of the market and respond to team behaviour.

At Round 5 a **second market** opens (Quick Commerce). See `03-core-mechanisms.md`.

- **Rounds:** 10 (Round 1 unscored practice, Rounds 2–10 scored)
- **Round = 1 simulated month**
- **Currency:** PKR
- **Teams:** 6–10, plus 2 AI incumbents

## Market

| Item | Value |
|---|---|
| Core category size (addressable) | PKR 150,000,000 / month at 8 teams (teams × PKR 12M ÷ 0.64; PKR 112.5M at 6 teams) - before the engine's calibration scale, see below |
| Category growth | +2.5% / month, seasonal index applied |
| Team share at start | ~8% each |
| AI incumbents combined | ~36% (Incumbent A: price leader; Incumbent B: premium/service leader) |

## How the market's orders are created (as built)

The question *"where do the orders in the total market come from?"* is answered
here in words; the formulas are in `07-engine-chain.md`, modules M1 (market),
M7 (demand and share) and M8 (orders realised). Every month, in this order:

1. **Size the market in rupees (M1).** `teams × PKR 12M ÷ 0.64` - the teams'
   baseline revenue grossed up for the 36% the AI competitors hold - grown 2.5% a
   month from month 1 and multiplied by the month's seasonal index (below). A
   calibration scale (`bootstrap._category_scale`) then sizes it so that a team
   on default decisions faces the same new-customer demand whatever the class
   size: 4,000 baseline orders × 78% net × `potential_headroom` 0.66, about 2,060
   new-customer orders a month at default play. For the Fall-2026 game (six
   teams, two AI competitors) the scale is 0.449, so the contested market is
   about PKR 50.5M in month 1, PKR 85M in month 7 and PKR 52.9M in month 8.
2. **Turn rupees into orders (M7).** Divide by the market's average order value
   last month (PKR 3,000 at the start): about 16,800 contested orders in month 1
   of the Fall-2026 game.
3. **Split the orders by customer segment.** Value Seekers 34%, Urban
   Convenience 26%, Quality Loyalists 18%, Deal Hunters 15%, Premium/Gifting 7%
   (table below).
4. **Share each segment between the stores by attractiveness.** Every team and
   AI competitor gets a score per segment from its price against the market
   (like for like in games on that rule), perceived quality, perceived delivery, in-stock rate, brand and
   range fit, each weighted by what that segment cares about; the segment's
   orders are shared in proportion to `exp(2.0 × score)` (a logit), so a better
   offer wins more but never all of it. A team that focused its founding plan on
   a segment gets a tilt there. The AI competitors take their share of every
   segment.
5. **Add each team's repeat demand on top.** Orders from its own existing
   customers, from the cohort ledger (M12), are not contested: they depend on
   how many customers the team has kept and how often they buy. Marketplace
   customers buy through the marketplace instead (step 7).
6. **Realise the orders (M8).** What a team actually sells is the smallest of
   its demand (steps 4 + 5), its traffic × conversion, and its stock. Short of
   traffic is *under-marketing*; short of demand is *wasted spend*; short of stock
   is a *stock-out*. Demand a team could not serve is offered twice to teams with
   spare capacity; whatever is left is lost to the market.
7. **Marketplace orders come from their own pool.** Listed teams share
   205,000 marketplace sessions a month by listing rank (`docs/03`, mechanism 7).

The console's *Market size* grid shows the result: every store's orders asked
for - served plus lost to stock-outs - by product and segment.

## Team starting position (identical for all teams)

| Metric | Value |
|---|---|
| Cash | PKR 13,000,000 (PKR 12,000,000 in games begun before 2026-10-18), plus a PKR 24M working capital facility at 22% |
| Revenue (Round 0) | PKR 12,000,000 |
| Orders | 4,000 |
| AOV | PKR 3,000 |
| Sessions | 190,000 |
| Conversion rate | 2.1% |
| Gross margin | 38% |
| Contribution margin | 9% |
| Marketing spend | PKR 1,800,000 |
| Blended CAC | PKR 850 |
| New customers | 2,100 |
| Repeat order share | 35% |
| Active customer base | 35,000 |
| COD share of orders | 62% |
| RTO rate on COD | 18% |
| Return rate on delivered | 9% |
| Average rating | 4.1 / 5 |
| NPS | 24 |
| Active SKUs | 14 (of 20 in catalogue) |
| Inventory value | PKR 9,500,000 |
| Warehouse capacity | 6,000 orders / month |
| CS agents | 4 |

## Seasonality index (applied to category demand)

| Month | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Index | 1.00 | 1.05 | 1.18 | 0.92 | 0.95 | 1.30 | 1.45 | 0.88 | 1.10 | 1.22 | 1.00 | 1.15 |

Round 3 = Ramadan build-up. Round 6–7 = 11.11 / Black Friday. Round 10 = year-end.
Teams are told the index shape only if they buy **MR-01**.

## Customer segments

| Segment | Share of category | Price sensitivity | Quality weight | Delivery-speed weight | Repeat propensity |
|---|---|---|---|---|---|
| Value Seekers | 34% | High | Low | Low | Low |
| Urban Convenience | 26% | Medium | Medium | **High** | Medium |
| Quality Loyalists | 18% | Low | **High** | Medium | **High** |
| Deal Hunters | 15% | **Very high** | Low | Low | **Very low** |
| Premium/Gifting | 7% | Very low | **Very high** | High | Medium |

Segment weights are hidden. Teams learn them by buying **MR-06**.

Deal Hunters exist to punish discount-led strategies: they convert well, destroy
margin, and almost never repeat. This is the sim's main trap.

---

## Questions from the course

Asked by the instructor while running the Fall-2026 cohort; the index of every
question is `18-questions.md`.

### Where is the rule for the orders created in the total market? *(October 2026)*

Here, in *How the market's orders are created*: the market is sized in rupees
(teams × PKR 12M ÷ 0.64, grown 2.5% a month, seasonal, calibrated to the class
size), turned into orders at last month's average order value, split by
customer segment, shared between the teams and the AI competitors by
attractiveness, topped up with each team's own repeat demand, and finally
limited by each team's traffic, conversion and stock. The formulas are in
`07-engine-chain.md` (M1, M7, M8).
