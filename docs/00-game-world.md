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
| Core category size (addressable) | PKR 150,000,000 / month |
| Category growth | +2.5% / month, seasonal index applied |
| Team share at start | ~8% each |
| AI incumbents combined | ~36% (Incumbent A: price leader; Incumbent B: premium/service leader) |

## Team starting position (identical for all teams)

| Metric | Value |
|---|---|
| Cash | PKR 25,000,000 |
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
| Repeat order share | 22% |
| Active customer base | 31,000 |
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

| Round | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Index | 1.00 | 1.05 | 1.18 | 0.92 | 0.95 | 1.30 | 1.45 | 0.88 | 1.10 | 1.22 |

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
