# 03 — Core Mechanisms

The four mechanisms adapted from Markstrat, specified for implementation, and
three more the live course added: working capital, the cost of stock, and the
channels beyond the team's own site. Mechanism 1 (paid market research) is
specified separately in `02`.

**What is built (October 2026).** Mechanisms 1, 2, 5, 6 and 7 run in the engine.
Mechanism 3 runs for the AI modules (G11) only; private label, the mobile app
and warehouse capacity were never built. Mechanism 4, Quick Commerce, is design
only. Each section says so where it applies; `01-decision-list.md` maps every
designed field to what became of it.

---

## Mechanism 2 — Perception vs Reality

Markstrat's signature: advertising moves *perception*, R&D moves *physical
reality*, and the gap between them is where the teaching happens.

### Three tracked dimensions

Each carries a **perceived** and an **actual** score, both 0–1.

| Dimension | Actual driven by | Perceived driven by |
|---|---|---|
| Quality | SKU quality tier (1.5), QA spend (7.4), supplier (7.2) | Creative quality (3.8), brand spend (3.9), influencer tier (3.5), packaging (8.5), review scores |
| Value | Net price vs segment willingness to pay | Discount depth (2.2), promo participation (2.3), price anchoring history |
| Delivery reliability | Courier success × SLA attainment (8.3, 8.4) | Delivery promise (8.4), UX messaging (5.1), review sentiment |

### The gap rule

Let `G = Perceived − Actual` on each dimension.

**Over-promising (G > +0.15):**

| Effect | Lag |
|---|---|
| Rating falls proportional to G | 1 round |
| Return rate rises (expectation returns) | 1 round |
| Repeat rate falls | 2 rounds |
| Brand equity stock decays faster | 3 rounds |

**Under-marketing (G < −0.15):**

| Effect | Lag |
|---|---|
| Traffic growth capped below what spend should deliver | Immediate |
| CAC rises — you pay for clicks that don't convert on trust | Immediate |
| Operational investment earns no share gain | Immediate |

Both failure modes must be punished. A sim that only punishes over-promising
teaches "under-promise and over-deliver," which is not actually good advice —
it means you have paid for capability nobody knows you have.

### Visibility

Teams see **actual** scores free. They see **perceived** scores only via
**MR-07**. So the gap is invisible unless purchased. Deliberate: the gap is the
most valuable thing in the game and it sits behind a PKR 300,000 paywall.

### Closing the gap

Perception moves at ~25% of the distance to actual per round when marketing
is aligned. Reality moves faster — one supplier change shifts actual quality
within one lead time. So **reputation lags reality in both directions**, which
is the realistic and useful lesson.

---

## Mechanism 3 — Projects: lead time, sunk cost, failure risk

No capability is instant. Every capability investment is a **project**.

### Project properties

| Property | Meaning |
|---|---|
| Capex | Paid **at commitment**, in full, non-refundable |
| Lead time | Rounds until it goes live |
| Ongoing cost | Monthly from go-live |
| P(success) | Rolled **at completion**, not at commitment |
| Benefit band | Range, drawn on success |
| Abort | Allowed any round. Refunds 0%. |

The project register covers G11 AI modules, 5.3 mobile app, 8.1 warehouse
capacity, and 1.3 private-label development.

**As built.** Only the G11 AI modules are projects (`m04_capability.PROJECTS`);
abort is not offered. A build that fails is not refunded, and ticking the
decision again starts - and pays for - a new build. Since 2026-10-22 every build
is visible: the team report has a *Technology projects* section (started, paid,
building / live / failed), each AI decision on the form says what the team owns
and what Yes would cost, and the console lists every team's builds and the money
lost on failures. Dynamic pricing (11.3) was withdrawn the same day: nothing in
the engine ever read its benefit, so it cost PKR 3.8M and PKR 300k a month for
no effect. It is in no preset, never built or charged (`WITHDRAWN`), and what
each team paid - every build and the running cost of each month it was live -
was refunded once, in cash, in the month after the withdrawal.

### Private-label development (the Vodites analogue) - design only, not built

| Property | Value |
|---|---|
| Minimum viable budget | PKR 2,500,000 (below this, P(success) = 0) |
| Lead time | 3 rounds at minimum budget; 2 rounds at PKR 4,000,000+ |
| P(success) | 0.55 at minimum, rising to 0.85 at PKR 5,000,000 |
| Benefit | Gross margin 58% vs 38% on resold SKUs |
| Risk | On failure: capex lost, one round of team attention lost |
| Hidden risk | If launched without **MR-18**, 40% chance the concept misses segment demand and sells at ~30% of forecast |

**Buying up P(success) with budget is the key teaching point.** Most teams fund
at the minimum, because the minimum is visible and the probability curve is not
— the curve is only revealed in debrief. Teams that reason about expected value
rather than sticker price outperform, and that is worth an entire class session.

### Obsolescence

AI modules built in Rounds 2–3 deliver 100% of their benefit band. The same
modules bought in Round 8 deliver ~60%, because rivals have them and the
advantage has competed away. Early commitment under uncertainty beats late
commitment under certainty — the central lesson of capability investment.

---

## Mechanism 4 — The second market (Quick Commerce, opens Round 5) - design only, not built

Announced at Round 3 ("a category signal"), opens at Round 5.

### Why a second market

It forces the portfolio question Markstrat forces with Vodites: *do I defend a
declining-margin core, or fund an unproven, capital-hungry adjacency?* Neither
answer is correct. The correct behaviour is sizing the bet against your cash
position and your core's defensibility.

### Q-Commerce economics (deliberately inverted vs core)

| | Core e-commerce | Quick Commerce |
|---|---|---|
| AOV | PKR 3,000 | PKR 900 |
| Gross margin | 38% | 29% |
| Order frequency | 1.4 / customer / quarter | 3.8 / customer / quarter |
| Fulfilment cost / order | PKR 175 | PKR 260 |
| Delivery SLA | 3 days | 60 minutes |
| Return rate | 9% | 2% |
| COD share | 62% | 38% |
| Capex to enter | — | PKR 8,000,000 per city (dark store) |
| Lead time to enter | — | 2 rounds |
| Breakeven | — | ~1,800 orders/day/city |

Q-Com is **worse on unit economics and better on frequency and retention**. It
only pays if you reach density. A team that enters all three cities at once
runs out of cash around Round 8. A team that never enters watches the two teams
that entered one city each compound a retention advantage through Round 10.

### Competition for internal resource

Q-Com competes with the core for the same cash, the same warehouse capacity,
and the same CS headcount. It must not be modelled as a separate P&L bolted on
— shared-constraint contention is the entire point.

---

## Mechanism 5 — Working capital: the loan, the cash limit and administration

Built 2026-10-16 to 2026-10-22 (`ecomsim/loans.py`, M0 and M15). Before it, the
credit line drew itself whenever cash went below zero and nothing paid it back,
so every team borrowed without being told.

| Step | When | What happens |
|---|---|---|
| 1. Need | On the form | The month's money line by line: supplier bills falling due, the stock being ordered (a blank order priced as the engine will place it), marketing and other budgets, research, AI builds and fixed costs, less cash and money arriving. A suggested loan and a one-click Approve. |
| 2. Limit | On saving | Stock, budgets, research and AI builds must fit cash plus the approved loan (12.6). A month that does not fit cannot be submitted; it is kept as a draft and the admin page shows *changes not submitted*. A blank stock order never blocks: it buys what is left. |
| 3. Fund | Start of the month (M0) | If the money still does not fit, the stock order is cut first, then marketing and other discretionary spend. The report says by how much. |
| 4. Settle | End of the month (M15) | The month draws on the approved loan only as bills need it. Bills already owed are paid regardless: the bank covers the gap up to the PKR 24M limit and the report names it unplanned borrowing. Cash above one month of fixed costs repays the loan automatically; 12.7 repays more. Interest is 22% a year on what is drawn. |
| 5. Insolvency | End of the month | Cash still below zero with the limit used: the team is in administration (see `08-scoring.md`). It stays in until cash is back above zero with the loan under half the limit. |

Games on the automatic line (games already trading when loans arrived, until the
instructor switches them over) keep step 2 and 3 as a backstop - what is left on
the line counts as applied for - but have no 12.6 / 12.7 decisions.

**The teaching point.** Stock bought on 45-day supplier terms moves no cash when
it is ordered, so a team can commit far more than it can pay. The form now makes
the month's cash visible before it is submitted; the cut in step 3 is what a
bank does to a business that did not ask for the money it needed.

---

## Mechanism 6 — Stock and what it costs to hold

| Lever / rule | As built |
|---|---|
| Buying (7.1) | A total split by what sold, or product by product; a split below the supplier's minimum is scaled up. Stock lands the month after it is ordered at the earliest; lead time is drawn, not fixed. |
| Automatic order (7.1 blank) | Orders up to half a month of cycle stock + the believed lead time + safety cover (7.5), from a deterministic demand forecast, as far as cash and the approved loan go. Below the supplier's minimum nothing is ordered. The form shows the units and the cost before the month runs. |
| Holding cost | 2.1% of the value of stock on hand a month (`inventory_holding_rate`). |
| Ageing write-down | Cover beyond six months of sales (`inventory_obsolescence_rounds`) is written down 10% of its value a month. |
| Return to supplier (7.6) | Units product by product; the supplier keeps 50% of landed cost (`supplier_return_fee`) and refunds the rest in cash that month. |
| Range changes (1.3) | From month 3 in new games: an added product is ordered at once and goes on sale when it lands; a dropped product's stock goes back less a 20% restocking fee. |
| Off-range stock | Stock of products outside a team's range (from the going-concern opening order in the Fall-2026 game) can be sent back by the instructor from the admin page for a full refund the next month. |
| Purchase cost | Orders are costed on the same scale as cost of goods (`cogs_scale`) in games set up from 2026-10-11; older games keep the cost they started with. |

**The teaching point.** Too little stock loses orders in a good month; too much
costs every month it sits, and past six months of cover it starts to rot. The
return lever is the exit, at half price.

---

## Mechanism 7 — Channels beyond the own site

| Channel | As built |
|---|---|
| Marketplace (4.1, opens month 5) | A shared pool of marketplace shoppers split by rank (half price, half rating) between listed teams and the marketplace's own sellers, so each slice shrinks as more of the class lists. Marketplace shoppers convert 1.5x the own-site rate from the same stock. 10% of a listed team's own-site orders move to the marketplace and pay commission (14.5%). Payout 15 days after the sale. Marketplace customers buy less often, leave faster, are out of reach of CRM and buy again only while the team stays listed. |
| Affiliates and influencers (3.6) | In working-affiliate games, partners bring visitors in proportion to the rate with the same diminishing returns as paid media; 30% would have come anyway and are taken from organic; their customers churn about 20% a month; commission is paid only on sales they track. |
| Paid media by channel (3.1-3.4, 3.10) | Each channel has a buying intent that shares the paid orders out between channels (Google Search 1.8, Meta 1.0, TikTok 0.6), so CVR and CAC differ by channel; campaigns aim each budget by product and audience. |

---

## Interaction summary

As designed, the four mechanisms reinforce each other (private label and
Q-Commerce were not built, so the links through them are design only):

- **MR-07** (research) is the only way to see the **perception gap** (M2).
- **MR-18** (research) is the only way to de-risk **private label** (M3).
- **MR-20** (research) is the only way to size **Q-Commerce** (M4).
- Q-Com entry (M4) competes for the cash that funds AI projects (M3).
- Over-promising 60-minute delivery (M4) opens a perception gap (M2) that
  destroys core-category ratings.

A team that treats research as an overhead to be cut will make the private-label
bet blind, enter Q-Com in the wrong city, and never see its perception gap until
ratings collapse in Round 7. That chain is the sim's spine, and it should be
drawn on one slide in the final debrief.
