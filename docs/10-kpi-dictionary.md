# 10 — KPI Dictionary

Every metric in the simulation: its formula, its source module, who can see it,
and whether it is scored.

**This document is authoritative.** Where a dashboard label, a research report
and the scorecard appear to disagree about a metric, this file decides.

---

## Conventions

| Field | Meaning |
|---|---|
| **Code** | `snake_case` identifier used in the engine, API and spreadsheet model |
| **Module** | Where it is computed (`07-engine-chain.md`) |
| **Visibility** | `free` team sees it always · `paid` requires a study · `instructor` never shown to teams |
| **Scored** | Pillar and points from `08-scoring.md`, or `—` |
| **Block** | Dashboard block it appears in |

Currency is PKR. Rates are decimals internally, displayed as percentages.
All flow metrics are per round unless stated.

---

## Definitional decisions

**Read this section before anything else.** Every metric below has at least two
defensible definitions. Ambiguity here produces disputes in Round 7 that cannot
be settled, so each is decided once, here.

| Metric | The ambiguity | **Decision** |
|---|---|---|
| **CAC** | All marketing ÷ all new customers, or paid spend ÷ paid-acquired customers? | Both are reported, as `cac_blended` and `cac_paid`. **Scoring uses blended.** Teams that shift budget to organic should see the benefit |
| **AOV** | Before or after discount? Including shipping? Including tax? | **Net of discount, excluding shipping revenue, excluding tax.** `aov_net` |
| **Conversion rate** | Orders ÷ sessions, or orders ÷ unique users? | **Orders ÷ sessions.** One session yields at most one order |
| **Return rate** | Of orders placed, of units delivered, or of revenue? | **Units returned ÷ units delivered.** RTO is a separate metric and is never folded in |
| **RTO rate** | Of all orders or of COD orders? | **Of COD orders only.** Prepaid orders cannot RTO |
| **Repeat rate** | Repeat orders ÷ total orders, or customers with ≥2 orders ÷ total customers? | Both reported. **Scoring uses order-based** `repeat_order_share` |
| **LTV** | Revenue, gross margin, or contribution margin? Over what horizon? | **Contribution margin, from the actual cohort ledger, 24-month horizon.** Never a formula applied to averages |
| **Active customer** | Ever purchased, or purchased recently? | **Ordered within the last 3 rounds** |
| **Gross margin** | Before or after returns? | **After returns and RTO revenue reversal** — computed on net revenue |
| **ROAS** | Platform-reported or true incremental? | **Both exist and deliberately differ.** `roas_reported` is biased +25–40%; `roas_true` requires MR-12 |
| **In-stock rate** | Share of SKUs, or revenue-weighted? | **Revenue-weighted** by each SKU's prior-round revenue share |
| **Contribution margin** | Which costs sit above the line? | Net revenue − COGS − fulfilment − payment costs − marketing − marketplace commission. **Payroll, warehouse fixed, technology and research are below it** |

---

## Block 1 — Growth

| Code | Metric | Formula | Module | Vis | Scored |
|---|---|---|---|---|---|
| `revenue_gross` | Gross revenue | `orders × aov_net` | M9 | free | — |
| `revenue_net` | Net revenue | `revenue_gross − returns_value − rto_value` | M14 | free | — |
| `orders` | Orders | Realised orders | M8 | free | — |
| `order_growth` | Order growth | `orders[t]/orders[t−1] − 1` | M8 | free | **P2 · 5** |
| `revenue_multiple` | Revenue multiple | `revenue_net[T]/revenue_net[1]` | M17 | free | **P2 · 8** |
| `sessions` | Sessions | Σ paid + organic + returning + affiliate (marketplace shoppers are counted separately) | M6 | free | — |
| `sessions_split` | Where visits came from | Paid (the campaign clicks), organic and direct, returning customers, marketplace; a founded team's month 1 has no returning visitors | M6 | free | — |
| `conversion_rate` | Conversion rate | `orders ÷ sessions` | M8 | free | — |
| `aov_net` | AOV | Net of discount | M9 | free | — |
| `market_share` | Market share | `revenue_net ÷ Σ all` | M7 | **paid** MR-03 | **P2 · 7** |
| `share_change_pp` | Share change | `market_share[T] − market_share[1]` | M17 | paid | scored via above |
| `new_vs_repeat` | New vs repeat split | `new_orders`, `repeat_orders` | M12 | free | — |

## Block 2 — Marketing

| Code | Metric | Formula | Module | Vis | Scored |
|---|---|---|---|---|---|
| `spend_total` | Marketing spend | Σ G3 decisions | M0 | free | — |
| `spend_by_channel` | Spend by channel | Per channel | M0 | free | — |
| `cac_blended` | Blended CAC | `spend_total ÷ new_customers` | M12 | free | — |
| `cac_paid` | Paid CAC | `paid_spend ÷ paid_new_customers` | M12 | free | — |
| `roas_reported` | Platform ROAS | **Biased +25–40%** | M16 | free | — |
| `roas_true` | Incremental ROAS | True contribution ÷ spend | M16 | **paid** MR-12 | — |
| `cpm_effective` | Effective CPM | Per channel, post-inflation | M6 | free | — |
| `creative_quality` | Creative quality score | `CQ` ∈ [0,1] | M5 | free | — |
| `brand_equity` | Brand equity stock | `BE` ∈ [0,1] | M5 | **paid** MR-08 | — |
| `channel_saturation` | Saturation index | `adstock^σ` vs linear | M6 | paid MR-11 | — |

## Block 3 — Commercial

| Code | Metric | Formula | Module | Vis | Scored |
|---|---|---|---|---|---|
| `gross_margin_pct` | Gross margin % | `gross_profit ÷ revenue_net` | M14 | free | **P1 · 5** |
| `contribution_pre_marketing_pct` | Contribution before marketing % | Contribution margin with marketing added back | M14 | free | **P1 · 12** |
| `contribution_margin_pct` | Contribution margin % | See definitional decisions | M14 | free | — |
| `ebitda_margin_pct` | EBITDA margin % | `ebitda ÷ revenue_net` | M14 | free | **P1 · 8** |
| `discount_rate` | Effective discount | `1 − net_price ÷ list_price` | M9 | free | — |
| `workbook` | Results workbook | Every month as Excel: P&L with each subtotal a formula, every report KPI rebuilt as a formula where it can be, sales and stock by product, cash flow, campaigns, segments (`ecomsim.workbook`; instructor console, one per team or all as a zip; teams only when `ECOMSIM_TEAM_WORKBOOKS=1`) | M17 records | instructor | — |
| `products` | Sales by product | Per product: units, net sales, gross margin, contribution before and after marketing, buyers by segment - adding up to the P&L (`ecomsim.mix.product_lines`) | M9 / M17 | free | — |
| `price_index` | Price vs market | `net_price ÷ market_avg` | M7 | **paid** MR-02 | — |
| `bundle_penetration` | Bundle share | Bundle orders ÷ orders | M9 | free | — |

## Block 4 — Operations

| Code | Metric | Formula | Module | Vis | Scored |
|---|---|---|---|---|---|
| `instock_rate` | In-stock rate | Revenue-weighted | M3 | free | — |
| `service_level` | Service level | Orders served ÷ orders asked for | M8 | free | **P4 · 2** |
| `weeks_of_cover` | Weeks of cover | Closing stock ÷ (units sold this month ÷ 4.33) | M3 | free | — |
| `stockout_lost_orders` | Lost to stock-out | `potential − stock_capacity` | M8 | free | — |
| `delivery_success` | Delivery success | `delivered ÷ orders` | M10 | free | **P4 · 6** |
| `sla_attainment` | SLA attainment | Orders delivered in promise | M10 | free | — |
| `rto_rate` | RTO rate | **Of COD orders** | M10 | free | — |
| `return_rate` | Return rate | Units returned ÷ delivered | M11 | free | — |
| `return_rto_cost_pct` | Return + RTO cost | `÷ revenue_net` | M14 | free | **P4 · 4** |
| `inventory_turns` | Inventory turns | `COGS × (12/ROUND_MONTHS) ÷ avg inventory` | M14 | free | **P4 · 3** |
| `inventory_value` | Inventory value | Closing stock at cost | M3 | free | — |
| `inventory_ageing` | Ageing | Rounds held, by SKU | M3 | free | — |
| `capacity_utilisation` | Fulfilment utilisation | `orders ÷ capacity` | M10 | free | — |
| `forecast_error` | Forecast error | \|forecast − actual\| ÷ actual | M3 | free | — |

## Block 5 — Customer

| Code | Metric | Formula | Module | Vis | Scored |
|---|---|---|---|---|---|
| `active_customers` | Active base | Ordered in last 3 rounds | M12 | free | **P3 · 6** |
| `new_customers` | New customers | `new_orders ÷ first_order_units` | M12 | free | — |
| `repeat_order_share` | Repeat order share | `repeat_orders ÷ orders` | M12 | free | **P3 · 5** |
| `repeat_customer_rate` | Repeat customer rate | Customers with ≥2 orders ÷ base | M12 | free | — |
| `churn_rate` | Churn | Weighted across cohorts | M12 | free | — |
| `ltv_contribution` | LTV | Cohort ledger, 24-month, contribution basis | M12 | free | — |
| `ltv_cac_ratio` | LTV : CAC | `ltv_contribution ÷` lifetime CAC (all marketing ÷ all new customers) | M17 | free | **P3 · 6** |
| `cohort_retention` | Cohort curves | Per acquisition cohort | M12 | **paid** MR-10 | — |
| `cohort_by_channel` | Retention by channel | The churn table in M12 | M12 | **paid** MR-10 | — |
| `rating` | Average rating | 0–5 | M13 | free | — |
| `nps` | NPS | −100 to +100 | M13 | free | **P3 · 3** |
| `csat` | CSAT | 0–100 | M13 | free | — |
| `cs_backlog` | Service backlog | Unresolved tickets | M13 | free | — |

## Block 6 — Finance

| Code | Metric | Formula | Module | Vis | Scored |
|---|---|---|---|---|---|
| `cash_balance` | Cash | Closing | M15 | free | — |
| `runway_rounds` | Runway | `cash ÷ max(1, −operating_cf)` | M15 | free | **P5 · 5** |
| `free_cash_flow` | FCF | Operating CF − capex | M15 | free | — |
| `free_cash` | Cash the business generated | (cash − starting cash) − (credit drawn − opening credit) | M17 | free | **P5 · 3** |
| `net_margin_pct` | Net profit margin | `net_profit ÷ revenue_net` (stands in for the cash conversion cycle, not tracked) | M14 | free | **P5 · 2** |
| `working_capital` | Working capital | Inventory + receivables − payables | M15 | free | — |
| `credit_drawn` | Credit drawn | Against ceiling | M15 | free | — |
| `net_profit` | Net profit | Bottom line | M14 | free | — |
| `cod_receivable` | COD in transit | Remitting next round | M15 | free | — |

`cod_receivable` deserves its own dashboard tile despite being a minor line.
It is the number that explains why a profitable, growing team has no cash, and
most teams will not look for it unless it is placed in front of them.

## Block 7 — Perception & Brand

| Code | Metric | Formula | Module | Vis | Scored |
|---|---|---|---|---|---|
| `quality_actual` | Actual quality | `AQ` | M5 | free | — |
| `quality_perceived` | Perceived quality | `PQ` | M5 | **paid** MR-07 | — |
| `delivery_actual` | Actual reliability | `ADR` | M5 | free | — |
| `delivery_perceived` | Perceived reliability | `PDR` | M5 | **paid** MR-07 | — |
| `perception_gap` | **The gap** | `max(G_q, G_v, G_d)` | M5 | **paid** MR-07 | — |

The asymmetry is deliberate: actual scores are free, perceived scores cost
PKR 300,000, and **the gap between them is the single most valuable number in
the sim.**

## Block 8 — Decision Quality

| Code | Metric | Module | Vis | Scored |
|---|---|---|---|---|
| `decisions_taken` | Decisions taken ÷ (¾ × decisions open), capped at 1 (rules v2) | M17 | instructor (teams see it described) | **P6 · 8** |
| `memo` | A board memo the instructor has not rejected (rules v2) | M17 | instructor | **P6 · 2** |
| `memo_score`, `prediction_accuracy`, `plan_variance` | As designed; not built | — | — | — |
| `research_spend` | Research purchased | M14 | free | — |

## Added since the specification (October 2026)

| Code | Metric | Formula / source | Module | Vis | Scored |
|---|---|---|---|---|---|
| `stock_by_product` | Stock by product | Opening + received + back from failed deliveries − sold − returned to supplier = closing; weeks of cover; on order and when it lands; stock value at landed cost | M3 / M17 | free | — |
| `campaigns` | Campaign results | Per campaign: spend, impressions, clicks, CTR, CPC, orders, CVR, ROAS, CAC, with the reason it worked or did not (`ecomsim.targeting`) | M6 / M8 | free | — |
| `mp_sessions`, `mp_orders` | Marketplace visits and orders | Share of the marketplace pool by listing rank; orders at 1.5× own-site conversion | M6 / M8 | free | — |
| `listing_rank` | Listing rank | Half price, half rating; 1.00 is the best a listing can score | M6 | free | — |
| `marketplace_commission` | Marketplace commission | 14.5% of marketplace order revenue | M14 | free | — |
| `holding_cost` | Stock holding cost | 2.1% of stock value a month | M14 | free | — |
| `ageing` | Write-down of ageing stock | 10% a month of the value of cover beyond 6 months | M14 | free | — |
| `restocking` | Restocking fee on stock returned | What the supplier keeps on 7.6 (50%) and 1.3 (20%) returns | M14 | free | — |
| `supplier_refund` | Refund for stock returned | Cash back for stock sent to the supplier, its own cash line | M15 | free | — |
| `tech_refund` | Refund for a withdrawn lever | Build and running costs of dynamic pricing (11.3) paid back once | M15 | free | — |
| `loan_needed`, `loan_approved` | The month's loan | What the month needs (bills, stock, spending, fixed costs less cash and receipts) and what the team approved (12.6) | loans | free | — |
| `stock_cut`, `spend_cut` | Spending cut to fit | What M0 cut from the stock order and from other spending when cash plus the loan fell short | M0 | free | — |
| `unplanned_borrowing` | Borrowing not approved | Bills already owed that cash and the approved loan could not cover, paid by the bank up to the limit | M15 | free | — |
| `credit_repaid` | Loan repaid | Spare cash above a month of fixed costs, plus extra repayment (12.7) | M15 | free | — |
| `tech_projects` | Technology projects | Every build: started, paid, building / live / failed / withdrawn (`service.project_timeline`) | app | free | — |
| `month_score` | The month on its own | The published scorecard applied to one month, growth against the month before (`scoring.month_score`) | M17 | free once rankings are published | — |

Every figure on the team report is also in the Excel workbook, rebuilt as a
formula where it can be (`workbook` above), and the KPI definitions PDF
(`tools/kpi_definitions_pdf.py`) gives students the same formulas.

---

## Instructor-only

| Code | Metric | Why hidden |
|---|---|---|
| `true_segment_weights` | The real `w_*[s]` | MR-06 sells a noisy estimate |
| `true_market_share` | Exact share | MR-03 sells a ±5% estimate |
| `competitor_internals` | Incumbent state | Never purchasable |
| `near_miss_log` | Teams within 10% of a Type B trigger | Threshold calibration |
| `research_roi` | Each team's research spend vs score | Post-run debrief evidence |
| `event_warning_hits` | Who was forewarned and acted | Debrief evidence |
| `rng_seed`, `config_hash` | Replay keys | Dispute resolution |
| `market_size` | Orders by product and segment | Every store's orders asked for, served plus lost to stock-outs, with each segment's share (console) |
| `debrief` | What each team decided and what it did | Console cards: results with ranks, strategy summary, what worked / to raise, points by pillar against the best |
| `strategy_grid` | Every team's choices side by side | Admin *Strategy* page: founding choices and each month's decisions, with changes on last month |

---

## Metrics deliberately NOT scored

| Metric | Why |
|---|---|
| `revenue_net` | Movable by discounting without improving the business |
| `aov_net` | Movable by dropping cheap SKUs |
| `sessions` | Movable by buying junk traffic |
| `conversion_rate` | Movable by suppressing traffic |
| `rating` | Already inside NPS and the conversion chain |
| `cash_balance` | Hoarding is not achievement — `runway_rounds` is banded instead |

Governing rule from `08-scoring.md`: **no metric is scored if it can be moved
without moving the business.** All six above fail that test and appear on the
dashboard purely as diagnostics.

---

## Dashboard layout

Six blocks, as in the original brief, plus perception.

```
┌─ GROWTH ─────────┬─ MARKETING ──────┬─ COMMERCIAL ─────┐
│ revenue_net      │ cac_blended      │ contribution_mgn │
│ orders           │ roas_reported *  │ gross_margin     │
│ conversion_rate  │ spend_by_channel │ discount_rate    │
│ aov_net          │ creative_quality │ sku_contribution │
│ new_vs_repeat    │ cpm_effective    │ price_index °    │
├─ OPERATIONS ─────┼─ CUSTOMER ───────┼─ FINANCE ────────┤
│ instock_rate     │ active_customers │ cash_balance     │
│ delivery_success │ repeat_share     │ runway_rounds    │
│ rto_rate         │ ltv_cac_ratio    │ cod_receivable   │
│ return_rate      │ nps              │ cash_conv_cycle  │
│ inventory_turns  │ cs_backlog       │ net_profit       │
└──────────────────┴──────────────────┴──────────────────┘
  PERCEPTION: quality_actual | delivery_actual | gap °

  * biased    ° requires a purchased study
```

**Biased and paid metrics must be visually marked.** A team should be able to
see at a glance that `roas_reported` carries an asterisk — and should have to
decide whether to pay PKR 450,000 to find out what the asterisk means.
