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
   about PKR 50.5M in month 1, PKR 85M in month 7 and PKR 52.9M in month 8,
   before any event that month moves it.
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

### The market is one pool of orders, not of products

The pool built in steps 1-3 is **one number of orders for the whole beauty and
personal-care market**. It is not split by product, nor by product category
(skincare, haircare, homecare, hygiene, baby): there is no separate demand for
serum, or for homecare. The only split is by **customer segment**. An order is a
customer choosing a store; what goes in the basket is decided afterwards, by
the store it chose.

Products and categories still matter, in two places only:

- **How many orders a store wins** (step 4). The range enters the store's
  attractiveness through its *range fit* - how many products it carries (a
  third of the fit) and how well its quality tier matches what each segment will
  pay (two thirds) - and through its prices and in-stock rate. Which categories
  the products belong to does not enter at all: the founding *category focus* is
  only a label read off the range, while the founding *segment* focus does tilt
  the draw from the segments chosen.
- **What each order contains** (below). The basket is the store's own product
  mix, so the range decides the average order value, the margin and the stock
  each line needs - not the number of orders.

Two consequences worth teaching:

1. **No team can own a category's demand.** A store that sells only homecare
   wins orders the same way as one that sells skincare: by being the store the
   segments prefer. Its range changes what those customers buy from it, and so
   its revenue and margin per order.
2. **Discounting one product mostly moves the basket.** It lowers the store's
   price index a little, so it wins slightly more orders, but its main effect is
   to pull units toward that line and away from the others (example below).

This is a simplification of a real market, where categories have shoppers of
their own and a store can be strong in one and absent from another. It keeps
the competition on the store as a whole - proposition, price, service, stock -
which is what the scorecard measures.

### How an order reaches a team, and what goes in it - a worked example

An engine run: month 1, six identical going-concern teams on default decisions,
two AI competitors; `python tools/order_example.py` reproduces it, and
`tests/test_docs.py` fails if the engine stops giving these numbers. They are
the simulation's, not market data.

**Stage 1 - the order goes to a store (M7, M8).**

| Step | What happens | team_01 |
|---|---|---|
| Market | PKR 50.1M after this month's events ÷ PKR 3,000 average order | 16,698 contested orders in the whole market |
| Segments | Split by segment share | Value Seekers 5,677 · Urban Convenience 4,342 · Quality Loyalists 3,006 · Deal Hunters 2,505 · Premium/Gifting 1,169 |
| Share | Each segment shared by attractiveness between six teams and two AI competitors | Wins 667 · 555 · 395 · 273 · 153 = **2,043** (12.2% of the market; the AI competitors take 26.6%) |
| Repeat | Its own returning customers, uncontested | + **1,197** = demand of **3,240** orders |
| Realised | Smallest of demand 3,240, traffic × conversion 3,564, stock 8,157 orders' worth | **3,240 orders** (demand is what binds) |

**Stage 2 - the order is filled with products (M9).** Each order carries 2.424
units on average, so 3,240 orders are 7,853 units. Each product's share of
those units is:

```
share[p] = catalogue weight × customer pull × price pull     (renormalised over the range)
           + units pushed by product campaigns (3.10)        (at most 60% of the basket)
           + extra units from packs on it (1.2)
```

then each line sells what its stock allows; a line that runs out sells what it
had and the order ships without the rest, so the order still counts but its
basket is smaller (the report's *demand missed*).

| Product | Catalogue weight | Customer pull | Price pull | Share of units | Units |
|---|---|---|---|---|---|
| Facewash 100ml | 10.7% | 1.00 | 1.00 | 10.7% | 841 |
| Moisturiser 200ml | 9.5% | 1.00 | 1.00 | 9.5% | 748 |
| Serum 30ml | 7.1% | 1.00 | 1.00 | 7.1% | 561 |
| Hair Oil 200ml | 6.0% | 1.00 | 1.00 | 6.0% | 467 |
| ... 10 more lines | | | | | |

With six identical stores every pull is 1.00 and each sells exactly the
catalogue mix - the neutral case the calibration rests on.

**The same month, team_01 discounting Serum 15%.** Serum's price falls against
the rest of the range, so its *price pull* rises to 1.10 and every other line's
falls to 0.98-0.99: Serum goes from 7.1% to 7.8% of units, **561 to 619 units
(+10%)**, while each other line loses 0.1-0.5%. The store's price index dips, so
it wins 14 more contested orders (2,043 to 2,057) and its orders rise from 3,240
to 3,254 (+0.4%). Most of the discount moved units between lines; little of it
created orders.

**Customer pull, when stores differ.** Each product has a main and a second buyer
segment (`params/audiences.csv`), tilted by tier: Serum's are Quality Loyalists
and Premium/Gifting, Hair Oil's Value Seekers and Deal Hunters. A store whose
orders lean premium - Quality Loyalists 35% and Premium/Gifting 13%, against
24% and 8% for the stores on average - gets a customer pull of **1.33 on Serum
and 0.77 on Hair Oil**: a third more serum and a quarter less hair oil than the
catalogue mix, before price or campaigns. Who a store wins decides what it sells.

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

### Is the total market's demand linked to any product or category? *(2026-10-25)*

No. It is one pool of orders for the whole market, split only by customer
segment; no product or product category has demand of its own. Products enter
twice: the range shapes how attractive a store is (range fit, prices, stock),
and after a store wins an order its own product mix decides what is in it. See
*The market is one pool of orders, not of products*.

### How is an order assigned to a team, and to a product in a category? *(2026-10-25)*

In two stages: the order goes to a store (segment by segment, by
attractiveness, plus the store's repeat customers, limited by its traffic and
stock), then it is filled with that store's products in proportion to catalogue
weight, customer pull and price pull, plus campaigns and packs, as far as each
line's stock goes. The product's category plays no part beyond the product
itself. See the worked example above.
