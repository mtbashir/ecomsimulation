# 01 — Decision List

**56 decision fields across 12 groups.** Not all are open from Round 1 — see
*Progressive unlock* at the end. Round 1 exposes 24 fields; the full set is open
by Round 5.

Field types: `SELECT` (pick one), `MULTI` (pick many), `NUM` (number),
`PCT` (percentage), `CURR` (PKR), `PER-SKU` (one value per active SKU), `TEXT`.

---

## G1 — Assortment & Product (5)

| # | Decision | Type | Range / options | Notes |
|---|---|---|---|---|
| 1.1 | SKU activate / deactivate | MULTI | 20-SKU catalogue | Deactivating leaves dead stock on the books |
| 1.2 | Bundle definition | MULTI | Up to 3 bundles: SKU set + bundle price | Lifts AOV, compresses margin |
| 1.3 | Private-label project | SELECT + CURR | Start / continue / abort; target category; quality tier; R&D budget | **Project mechanic — lead time + failure risk.** See `03` |
| 1.4 | Private-label launch | SELECT | Launch / hold / cancel | Only when project completes |
| 1.5 | SKU quality tier | PER-SKU | Economy / Standard / Premium | Sets true quality; drives cost, rating, return rate |

## G2 — Pricing (4)

| # | Decision | Type | Range | Notes |
|---|---|---|---|---|
| 2.1 | List price | PER-SKU | CURR | Free, but anchoring penalties apply across rounds |
| 2.2 | Site-wide discount depth | PCT | 0–50% | Above 25% triggers Deal Hunter inflow |
| 2.3 | Promo window participation | MULTI | Payday / Ramadan / 11.11 / Black Friday / Year-end | Each has entry cost and traffic multiplier |
| 2.4 | Free-shipping threshold | CURR | 0 (always free) – 5,000 | 0 kills margin; too high kills conversion |

## G3 — Marketing Budget & Channels (9)

| # | Decision | Type | Notes |
|---|---|---|---|
| 3.1 | Meta (FB/IG) spend | CURR | Saturation curve; CPM inflates with total market spend |
| 3.2 | Google Search spend | CURR | Highest intent, lowest volume ceiling |
| 3.3 | Google Shopping / PMax spend | CURR | Requires feed quality (from 5.4) |
| 3.4 | TikTok spend | CURR | Cheapest CPM, worst intent, highest creative dependency |
| 3.5 | Influencer spend + tier | CURR + SELECT | Micro / Macro / Celebrity. Celebrity has variance — can flop |
| 3.6 | Affiliate commission rate | PCT | 0–20%. Pay-on-performance, but cannibalises organic |
| 3.7 | Marketplace ads spend | CURR | Only if 4.1 is on |
| 3.8 | Creative production budget | CURR | Builds **Creative Quality Score** (decays 15%/round) |
| 3.9 | Brand / awareness spend | CURR | Builds **Brand Equity stock** — 3-round lag, 8%/round decay |

**3.8 and 3.9 are the two that separate good teams.** Neither returns anything
in-round. Teams that cut them first look best in Rounds 2–4 and worst by Round 8.

## G4 — Channel Strategy (3)

| # | Decision | Type | Notes |
|---|---|---|---|
| 4.1 | Marketplace participation | SELECT | Off / Basic / Mall tier. Commission 12–18%, ranking is share-based |
| 4.2 | Marketplace price delta | PCT | −15% to +15% vs own site. Cross-channel leakage if negative |
| 4.3 | Q-Commerce participation | SELECT + MULTI | From R5. On/off + city selection (Karachi/Lahore/Islamabad) |

## G5 — Site & Customer Experience (4)

| # | Decision | Type | Notes |
|---|---|---|---|
| 5.1 | UX investment | CURR | Page speed, search, PDP quality → **UX Score** |
| 5.2 | Checkout optimisation | CURR | Directly lifts checkout completion; fastest-payback lever, usually ignored |
| 5.3 | Mobile app | SELECT | None / Build / Maintain. **Project: 2 rounds, PKR 4.5M, ongoing 400k** |
| 5.4 | Content & merchandising | CURR | Photography, copy, review solicitation. Feeds 3.3 and rating velocity |

## G6 — CRM & Retention (4)

| # | Decision | Type | Notes |
|---|---|---|---|
| 6.1 | Retention budget | CURR | Email / SMS / WhatsApp |
| 6.2 | Target segments | MULTI | 5 segments. Mistargeting wastes the budget entirely |
| 6.3 | Loyalty programme | SELECT | Off / Points (1.5% cost) / Tiered (3% cost) |
| 6.4 | Win-back spend | CURR | Targets churned cohorts; efficacy decays with months-since-churn |

## G7 — Supply & Procurement (5)

| # | Decision | Type | Notes |
|---|---|---|---|
| 7.1 | Purchase order quantity | PER-SKU | NUM. The core working-capital decision |
| 7.2 | Supplier selection | SELECT | A: −12% cost, 21d lead, MOQ 5,000 · B: base, 14d, MOQ 2,000 · C: +9% cost, 7d, MOQ 500 |
| 7.3 | Payment terms | SELECT | Advance (−4% cost) / 30d (base) / 60d (+3% cost) |
| 7.4 | Quality assurance spend | CURR | Reduces defect rate → return rate and rating |
| 7.5 | Safety stock target | NUM | Weeks of cover, 0–8 |

## G8 — Fulfilment & Logistics (5)

| # | Decision | Type | Notes |
|---|---|---|---|
| 8.1 | Warehouse capacity | SELECT | **Project: +3,000 orders/mo, 2 rounds, PKR 6M capex, 350k/mo** |
| 8.2 | In-house vs 3PL split | PCT | 3PL: higher variable, zero capex, capacity-elastic |
| 8.3 | Courier mix | PCT×3 | Speed (PKR 210, 92% success, 2.1d) · Value (PKR 145, 84%, 4.3d) · Wide (PKR 175, 88%, 3.2d, best rural) |
| 8.4 | Delivery promise | SELECT | Standard / Express / Same-day. **Sets expectation — missing it costs more than not promising** |
| 8.5 | Packaging tier | SELECT | Basic (PKR 35) / Branded (75) / Premium (140). Affects rating and damage returns |

## G9 — Payments (3)

| # | Decision | Type | Notes |
|---|---|---|---|
| 9.1 | COD policy | SELECT + CURR | Off / On / On below threshold. Turning COD off cuts orders ~35% and RTO to ~0 |
| 9.2 | Prepaid incentive | PCT | 0–10% discount for prepaid. The key COD-economics lever |
| 9.3 | Payment gateway | SELECT | A: 2.9% fee, 91% success · B: 2.2%, 84% · C: 3.4%, 96% + wallets |

## G10 — Customer Service & Policy (4)

| # | Decision | Type | Notes |
|---|---|---|---|
| 10.1 | CS headcount | NUM | Capacity = 900 tickets/agent/month. Backlog compounds across rounds |
| 10.2 | Response SLA target | SELECT | 2h / 8h / 24h / 48h |
| 10.3 | Return window | SELECT | 7 / 15 / 30 days |
| 10.4 | Return policy | SELECT | Free returns / Customer pays / Restocking fee |

## G11 — Technology & AI Modules (5)

All are **projects**: capex, lead time, ongoing cost, success probability. See `03`.

| # | Module | Capex | Lead | Ongoing/mo | P(success) | Benefit if successful |
|---|---|---|---|---|---|---|
| 11.1 | Recommendation engine | PKR 3,000,000 | 2 rds | 250,000 | 0.85 | AOV +6–9%, CR +0.15pp |
| 11.2 | Demand forecasting AI | PKR 2,200,000 | 2 rds | 180,000 | 0.80 | Forecast error −40%, stock-outs down |
| 11.3 | Dynamic pricing | PKR 3,800,000 | 3 rds | 300,000 | 0.70 | Margin +1.5–3pp; **rating risk if aggressive** |
| 11.4 | AI customer service | PKR 1,800,000 | 1 rd | 120,000 | 0.90 | CS capacity ×2.5; CSAT −3 unless 5.4 funded |
| 11.5 | AI creative generation | PKR 1,200,000 | 1 rd | 90,000 | 0.75 | Creative cost −50%; quality ceiling capped at 0.75 |

11.5's capped ceiling is deliberate: AI creative is cheap and good-enough, never excellent.

## G12 — Finance & Intelligence (5)

| # | Decision | Type | Notes |
|---|---|---|---|
| 12.1 | Market research purchases | MULTI | See `02-market-research-menu.md` |
| 12.2 | Equity raise | SELECT + CURR | Rounds 4, 7 only. Dilution priced off trailing performance |
| 12.3 | Credit line draw | CURR | Up to PKR 15M, 22% p.a., covenant on cash ratio |
| 12.4 | Capex approval | MULTI | Confirms which G11/8.1/5.3 projects are funded this round |
| 12.5 | Board memo | TEXT | 400 words: what you decided and why. **10% of final score** |

---

## Progressive unlock

| Opens | Groups available |
|---|---|
| Round 1 | G1 (1.1, 1.2, 1.5), G2, G3 (3.1–3.4, 3.8), G6 (6.1, 6.2), G7, G8 (8.2–8.5), G9, G12 (12.1, 12.5) |
| Round 2 | G3 full, G5, G10 |
| Round 3 | G4 (4.1, 4.2), G11, G12 full, 8.1 |
| Round 4 | 1.3 private-label project, 12.2 equity raise |
| Round 5 | 4.3 Q-Commerce |

Round 1 at 24 fields is deliberately manageable. By Round 5 teams face the full 56
and must delegate internally — which is itself part of the exercise.

---

## Decision-quality rubric (for 12.5)

Graded 0–10 per round on four criteria, not on outcome:

1. **Evidence** — does the memo cite the team's own data or purchased research?
2. **Causal reasoning** — does it name the mechanism, not just the metric?
3. **Trade-off acknowledgement** — does it state what was sacrificed?
4. **Falsifiability** — does it state what result would prove the decision wrong?

Criterion 4 is the one that matters. Teams that write "we expect revenue up"
score low; teams that write "if repeat rate does not exceed 26% by Round 7, this
retention investment was wrong" score high.
