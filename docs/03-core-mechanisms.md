# 03 — Core Mechanisms

The four mechanisms adapted from Markstrat, specified for implementation.
Mechanism 1 (paid market research) is specified separately in `02`.

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

### Private-label development (the Vodites analogue)

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

## Mechanism 4 — The second market (Quick Commerce, opens Round 5)

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

## Interaction summary

The four mechanisms deliberately reinforce each other:

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
