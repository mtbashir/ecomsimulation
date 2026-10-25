# 07 — Engine Chain

The round calculation, module by module. This is the document the economic model
is built from.

The formulas below are the specification. Where the engine as built differs, or
a lever was added after the specification, an **As built** note under the module
says what the code does and when it changed (engine 2.3.0, October 2026). The
parameter values quoted are the defaults in `params/parameters.csv`.

## Architecture

The round is **a sequence of independent modules, each reading and writing a
shared state vector.** Not a monolithic function. This is the rule that makes
the Expert tier additive rather than a rewrite (`06-build-sequencing.md`).

```
run_round(state, decisions, config, rng) -> (state', reports)
```

**Determinism is mandatory.** Same `(state, decisions, config, seed)` must
produce identical output, always. All randomness draws from a seeded generator
keyed on `(run_id, round, team_id, purpose)`. This is what makes replay,
golden-file testing and dispute resolution possible.

---

## Module order

Order is not arbitrary — each dependency is noted. Changing the order changes
the economics.

| # | Module | Depends on |
|---|---|---|
| M0 | Resolve decisions | — |
| M1 | Market & seasonality | M0 |
| M2 | Events | M1 |
| M3 | Supply arrival & inventory | M0, M2 |
| M4 | Capability resolution | M0, M2 |
| M5 | Perception & brand | M0, M4, prior-round experience |
| M6 | Traffic generation | M0, M4, M5 |
| M7 | Demand & share allocation | M1, M2, M5 |
| M8 | Conversion & order realisation | M3, M5, M6, M7 |
| M9 | Basket & gross revenue | M0, M8 |
| M10 | Fulfilment & delivery | M0, M4, M8 |
| M11 | Returns | M5, M10, prior round |
| M12 | Customer ledger | M8, M10, M11, M13 (prior) |
| M13 | Experience, service & ratings | M5, M10, M11 |
| M14 | Costs & P&L | all |
| M15 | Cash & working capital | M14 |
| M16 | Research report generation | all |
| M17 | Scoring & persist | M14, M15 |

**M5 before M7** — perception drives attractiveness, so it must resolve first.
**M3 before M8** — stock constrains what can be sold.
**M13 after M11** — ratings react to delivered experience and returns, and feed
*next* round's conversion, never this one.

---

## M0 — Resolve decisions

```
resolved[d] = decisions[d]              if config.enabled[d] and round >= config.unlock_round[d]
              config.default_when_disabled[d]   otherwise
```

Every downstream module reads `resolved`, never `decisions`. This single
indirection is what makes presets work.

Validate before proceeding: capital allocations sum correctly, percentages in
range, courier mix sums to 100%, PO quantities respect MOQ. Invalid submissions
fall back to the prior round's decisions with a flag raised to the instructor.

**As built.**
- *Carry forward (rules v2):* before M0, `engine.carry` merges the month's
  submission over the team's standing decisions, so a lever left alone keeps
  last month's setting and the 1.1 price grid carries line by line. Not carried:
  12.1, 12.5, a typed 7.1, 1.3, 7.6, 11.1-11.5, 12.6, 12.7 (`NOT_CARRIED`).
- *Instructor windows:* the admin's decision windows reach the resolver: a lever
  closed for the month runs its default whatever a team saved.
- *Administration:* a team in administration has marketing (3.1-3.9), website
  (5.1), CRM (6.1) and QA (7.4) capped at half the month before, AI builds off
  and research cleared (`_administration`).
- *Funding (every game):* `loans.fund` fits the month's spending to cash plus the
  approved loan (12.6; on the automatic line, what is left on it). Short, it cuts
  the stock order first, then marketing and other discretionary spend, and
  records the cuts for the report. A blank stock order is elastic: it is priced
  from the order-up-to quantity M3 will place and buys what is left.

---

## M1 — Market & seasonality

```
BASE_CATEGORY   = (N_teams × 12_000_000) / 0.64
category[t]     = BASE_CATEGORY × (1 + g)^t × season[t]
```

`g = 0.025` per month. `season[t]` from the table in `00-game-world.md`.
At `ROUND_MONTHS > 3`, `season[t] → 1.0`.

Category is expressed in **PKR of demand**, converted to order potential in M7.

**As built.** `category = (N × baseline_team_revenue ÷ team_share_total) ×
(1 + g)^(t−1) × season[t] × category_scale`. `category_scale` is fixed at set-up
(`bootstrap._category_scale`) so a default team's share of the contested pool
is `baseline orders × 0.78 × potential_headroom (0.66)` against a fixed
reference field of AI competitors, whatever N: per-team economics do not move
with class size, while competitors added beyond the reference still cost share.
Six teams and two AI competitors give a scale of 0.449. The season index has
twelve values (`00-game-world.md`); `seasonality_amplitude` scales its
deviation from 1.0. A plain-language walk through M1, M7 and M8 is in
`00-game-world.md`, *How the market's orders are created*.

---

## M2 — Events

Events apply multiplicative modifiers to named state variables. Each event
declares `{target, multiplier, duration_rounds, scope}` where scope is
`all_teams | segment | single_team`.

```
category[t]     ×= event.category_mult
CPM_base[c]     ×= event.cpm_mult
lead_time[s]    ×= event.leadtime_mult
RTO_base        ×= event.rto_mult
```

Events never write directly to a team's P&L. They modify **parameters**, and
the chain propagates the consequence. This is what makes events teachable
rather than arbitrary.

Event severity scales by `EVENT_SEVERITY` (default 1.0, green 0.5–1.6).

---

## M3 — Supply arrival & inventory

```
arrivals[sku,t]  = Σ POs where po.round + ceil(lead_time/ROUND_DAYS) == t
opening[sku,t]   = closing[sku,t-1] + arrivals[sku,t]
```

Lead time is drawn, not fixed:

```
lead_time = supplier.lead_base × (1 + N(0, 0.15)) × event.leadtime_mult
```

Seeded on `(run_id, t, team_id, "leadtime", sku)`. A forecasting-AI module
(11.2) does not shorten lead time — it improves the *team's visibility* of it,
which is the honest modelling of what forecasting actually does.

In-stock ratio, used in M7 and M8:

```
instock_ratio = Σ_sku (opening[sku] > 0 ? weight[sku] : 0) / Σ_sku weight[sku]
```

weighted by each SKU's share of prior-round revenue.

**As built.**
- *Arrival:* `arrives = round + max(1, ceil(lead_days × max(0.4, noise) / 30))`,
  `lead_days = supplier.lead_time_days × lead_time_multiplier × event mult`,
  noise drawn with sd `lead_time_noise_sd` (0.15). Stock never lands in the
  month it is ordered.
- *Order of work:* land arrivals → RTO units back on the shelf → stock of
  products dropped from the range (1.3), returns to the supplier (7.6) and the
  instructor's off-range returns go back → this month's purchase order → the
  first order for any product added to the range (1.3).
- *Purchase order:* a typed 7.1 is a total split by last month's demand per
  product (topping up lines that ran short) or a per-product plan; a split below
  the supplier MOQ is scaled up. A blank 7.1 orders up to
  `forecast × (round_weeks/2 + believed lead weeks + safety weeks 7.5)` less
  stock on hand and on order (`automatic_units`), from `demand_forecast`
  (deterministic per month; sd `forecast_error_sd` 0.16, cut 40% by AI
  forecasting), as far as M0's funding allows; below MOQ nothing is ordered.
- *Cost:* `priced_order` charges each line at landed cost × supplier cost index;
  games set up from 2026-10-11 also apply `cogs_scale` (`purchase_scale`), so
  cash and cost of goods agree.
- *Returns:* 7.6 refunds `(1 - supplier_return_fee)` = 50% of landed cost in cash
  this month (M15) and books the fee below the line (M14); a dropped product's
  stock (1.3) goes back less `range_restocking_fee` (20%).

---

## M4 — Capability resolution

For each in-flight project completing this round:

```
roll = rng(run_id, t, team_id, "project", project_id)
success = roll < project.p_success
benefit = success ? uniform(benefit_low, benefit_high) : 0
```

Roll at **completion**, not commitment. Obsolescence applies:

```
benefit ×= max(0.55, 1 - 0.07 × (t - project.first_available_round))
```

An AI module built at first availability delivers 100%; the same module built
six rounds later delivers ~60%.

**As built.** Projects are the G11 modules only (`PROJECTS`). A completed build
that works adds the capability and its running cost; one that fails is dropped
and not refunded. `WITHDRAWN = {"dyn_pricing"}` removes dynamic pricing from
every team's projects and capabilities at the start of M4 and blocks new builds;
the app refunds what was paid (`service.withdrawn_refunds`, paid by M15 as
`tech_refund`). Effects read downstream: forecasting in M3, AI creative in M5,
recommendations in M9, AI customer service in M13.

---

## M5 — Perception & brand

### Brand equity stock

```
BE[t] = BE[t-1] × (1 - δ_BE) + α_BE × (0.2·bs[t] + 0.5·bs[t-1] + 0.3·bs[t-2]) / REF_BRAND
```

`δ_BE = 0.08`, `α_BE = 0.10`, `REF_BRAND = 400_000`. Peak effect at t−1 gives
the 3-round lag from `03-core-mechanisms.md` without a hard delay.

Clamp `BE ∈ [0, 1]`.

### Creative quality

```
CQ[t] = CQ[t-1] × 0.85 + κ × (creative_spend[t] / REF_CREATIVE)^0.5
```

`κ = 0.22`, `REF_CREATIVE = 300_000`. If AI-creative (11.5) is active,
`CQ = min(CQ, 0.75)` unless creative_spend exceeds `REF_CREATIVE` — the module
raises the floor and caps the ceiling.

### Actual scores

```
AQ  = 0.55·tier_score + 0.25·qa_score + 0.20·supplier_quality
AV  = clamp(1 - net_price / segment_wtp, 0, 1)
ADR = courier_success × sla_attainment
```

**As built - website (5.1), applied in M13 after conversion, so the gain lands
next month:** `ux += (ux_ceiling - ux) × spend / (spend + ux_invest_half)`, with
`ux_invest_half` = PKR 300,000 and the ceiling set by the founding tech stack
(2026-10-03).

### Perceived scores — converge at 25% per round

```
PQ_target  = 0.30·CQ + 0.25·BE + 0.15·influencer_tier + 0.10·packaging_tier + 0.20·rating_norm
PQ[t]      = PQ[t-1] + 0.25 × (PQ_target - PQ[t-1])
```

Same form for `PV` (driven by discount depth and price anchoring history) and
`PDR` (driven by delivery promise, UX messaging, review sentiment).

### The gap

```
G_q = PQ - AQ ;  G_v = PV - AV ;  G_d = PDR - ADR
```

Consequences, applied with the stated lag:

| Condition | Effect | Applied at |
|---|---|---|
| `G > +0.15` | `rating_target -= 1.2 × (G - 0.15)` | t+1 |
| `G > +0.15` | `return_rate ×= 1 + 1.8 × (G - 0.15)` | t+1 |
| `G > +0.15` | `repeat_mult ×= 1 - 1.5 × (G - 0.15)` | t+2 |
| `G > +0.15` | `δ_BE ×= 1 + 2.0 × (G - 0.15)` | t+3 |
| `G < -0.15` | `traffic_mult ×= 1 + 0.6 × G` (i.e. reduces) | t |
| `G < -0.15` | `CAC_mult ×= 1 - 0.8 × G` (i.e. raises) | t |

Use `G = max(G_q, G_v, G_d)` for over-promising and `min(...)` for
under-marketing. The worst gap governs.

---

## M6 — Traffic generation

### Paid, per channel c

Adstock:
```
adstock[c,t] = spend[c,t] + λ_ad × adstock[c,t-1]     λ_ad = 0.35
```

Market-level CPM inflation:
```
inflation[c] = 1 + φ_c × (Σ_teams spend[c,t] / REF_SPEND[c] - 1)
```
`φ_c = 0.25` default, green 0.10–0.45.

Effective coefficient:
```
k[c,t] = k_base[c] / inflation[c] × (1 + γ_c × (CQ - 0.5)) × traffic_mult
```
`γ_c` is creative sensitivity: TikTok 0.55, Meta 0.35, Google Search 0.10,
Shopping 0.20, influencer 0.45.

Sessions, with diminishing returns:
```
sessions_paid[c,t] = k[c,t] × adstock[c,t]^σ          σ = 0.60
```

**`σ` is the single most dangerous parameter in the model.** Above 0.90 returns
go near-linear and "spend everything on the cheapest channel" dominates every
other decision in the sim.

**As built - channel intent and campaigns.** Campaign setup (3.10) splits each
budget into up to three targeted campaigns (`ecomsim/targeting.py`). Paid orders
are shared between channels by buying intent (`channels.csv` `intent_cvr`:
Google Search 1.8, Meta 1.0, TikTok 0.6), totals unchanged, so CVR and CAC
differ by channel.

**As built - affiliates (3.6), in working-affiliate games (`world.affiliates`):**
```
affiliate_sessions = k_affiliate × (rate × affiliate_reach_revenue / 1000)^σ
organic           -= affiliate_cannibalisation × affiliate_sessions      (0.30)
```
with `affiliate_reach_revenue` = PKR 3M; M12 stamps the tracked share of new
customers as an affiliate cohort and M14 pays commission only on their sales.

### Organic and direct

```
sessions_organic[t] = ORG_BASE × (0.4 + 0.6·BE) × (1 + 0.25·ln(1 + active_customers/REF_CUST))
                      × (1 + 0.3·(ux_score - 0.5))
```

### Marketplace

```
mp_rank_score  = 0.4·mp_ad_spend_norm + 0.3·price_competitiveness + 0.3·rating_norm
mp_sessions[i] = MP_POOL × mp_rank_score[i] / Σ_j mp_rank_score[j]
```

As built (`ecomsim/marketplace.py`, 2026-10-13): the score is half price, half
rating (teams have no sponsored-listing lever; the scripted `3.7` spend lifts it
by up to half), the denominator adds `mp_rival_weight` average sellers for the
rest of the marketplace, and marketplace sessions turn into orders in M8 rather
than joining own-site traffic. See docs/13 for the parameters and their effect.

### Total

```
sessions[t] = Σ_c sessions_paid[c,t] + sessions_organic[t] + mp_sessions[t]
```

Channel overlap correction — raw sum double-counts reachable audience:
```
sessions[t] ×= 1 - OVERLAP × (1 - 1/n_active_channels)      OVERLAP = 0.12
```

---

## M7 — Demand & share allocation

Category order potential:
```
category_orders[t] = category[t] / AOV_market[t-1]
```

Per-segment utility, per team:
```
U[i,s] = w_price[s]·(1 - price_index[i])
       + w_qual[s]·PQ[i]
       + w_deliv[s]·PDR[i]
       + w_avail[s]·instock_ratio[i]
       + w_brand[s]·BE[i]
       + w_fit[s]·assortment_fit[i,s]
```

`price_index[i] = net_price[i] / market_avg_net_price`, clamped to [0.5, 2.0].
Segment weights `w_*[s]` from `00-game-world.md`, hidden unless MR-06 purchased.

**As built - like-for-like pricing (`world.fair_pricing`, games from
2026-10-15 and any game from the month the instructor picks).** The price index
compares each team's shelf with the same products at catalogue price, then
divides by the market's average of that ratio, so a team selling dearer products
is not mistaken for a dear team. Past a segment's willingness to pay it pulls
away: `U -= wtp_penalty × max(0, price_index - wtp_index[s])`, `wtp_penalty` 0.2
(Value Seekers 0.85 punish a premium price; Premium/Gifting shrugs).

Logit share:
```
share[i,s] = exp(β · U[i,s]) / Σ_j exp(β · U[j,s])       β = SHARE_SENSITIVITY = 2.0
```

AI incumbents participate in the denominator with scripted `U` values.

Potential demand:
```
potential[i] = Σ_s category_orders[t] × segment_share[s] × share[i,s]
```

**As built.** `share[i,s]` also carries the team's founding focus on segment
`s` (`_team_focus`, from D0.3), and the AI competitors enter the denominator
with their own utilities (price leader 0.46, premium/service 0.50, tilted by
`incumbent_aggression`). `β` is damped to 1.4 at three teams or fewer and raised
to 2.6 at twelve or more. Repeat demand from the team's own cohorts (M12) is
added to `potential[i]` after the logit, uncontested; marketplace cohorts are
left out, since they buy through the marketplace (M8).

---

## M8 — Conversion & order realisation

### Conversion rate

```
CR[i] = CR_base × M_price × M_ux × M_rating × M_stock × M_pay × M_deliv × M_assort
```

| Multiplier | Formula | Clamp |
|---|---|---|
| `M_price` | `(price_index)^η`, η = −1.8 | [0.5, 1.8] |
| `M_ux` | `1 + 0.45·(ux_score − 0.5)` | [0.75, 1.25] |
| `M_rating` | `1 + 0.20·(rating[t−1] − 4.0)` | [0.70, 1.20] |
| `M_stock` | `1 − 0.45·(1 − instock_ratio)` | [0.55, 1.00] |
| `M_pay` | `gateway_success × (1 + 0.18·cod_enabled)` | — |
| `M_deliv` | `1 + 0.30·(PDR − 0.5)` | [0.85, 1.20] |
| `M_assort` | `1 + 0.15·(assortment_fit − 0.5)` | [0.90, 1.12] |

`M_rating` uses **prior round's** rating. Ratings never affect the round in
which they are earned.

**As built.**
- In like-for-like games `M_price = price_index^price_elasticity_fair` (-1.8)
  with no 0.5 floor, so pricing high keeps costing buyers.
- `M_ship`, the free-delivery threshold (2.4): free delivery on everything
  ×(1 + 0.04); a bar up to half a basket above a typical order 1.0; beyond that
  `1 - 0.40 × (excess in baskets)`, floor 0.70 (`freeship_*` parameters).
- Marketplace orders (4.1) are converted from the marketplace pool at
  `mp_cr_mult` (1.5) × the own-site rate from the same stock, and
  `mp_cannibalisation` (10%) of own-site orders move across.

### Realisation — the two-sided constraint

```
traffic_capacity[i] = sessions[i] × CR[i]
stock_capacity[i]   = Σ_sku opening[sku] / units_per_order
orders[i]           = min(potential[i], traffic_capacity[i], stock_capacity[i])
```

This is where the sim teaches its central lesson:

- `traffic_capacity < potential` → **under-marketing.** Good proposition, not
  enough people saw it.
- `potential < traffic_capacity` → **wasted spend.** Plenty of traffic, weak
  proposition. Rivals took the demand.
- `stock_capacity` binding → **stock-out.** Both of the above were fine and you
  still lost the order.

### Redistribution of unmet demand

```
unmet = Σ_i (potential[i] - orders[i])
```

Redistribute proportional to each team's remaining share weight, capped by that
team's own spare capacity. **Two iterations**, then any residual is lost to the
category (customers who did not buy at all). Do not iterate to convergence —
real markets leak demand, and unbounded iteration hides stock-out consequences.

---

## M9 — Basket & gross revenue

```
AOV[i] = AOV_base × (1 + 0.08·bundle_penetration)
                  × freeship_effect
                  × (1 - discount_depth)
                  × mix_effect
                  × (1 + recsys_lift)
```

`freeship_effect = 1 + 0.12 × clamp((threshold - AOV_base)/AOV_base, 0, 0.5)` —
a threshold slightly above natural basket lifts AOV; far above kills conversion
(already handled in `M_price`).

**As built (2026-10-07).** Free delivery on everything shrinks the basket 3%
(`freeship_free_aov_drop`); a bar above the typical basket lifts AOV as above,
and the items added to reach it carry their cost of goods, as pack units do.
The conversion side is `M_ship` in M8.

```
gross_revenue[i] = orders[i] × AOV[i]
```

**Product mix (`ecomsim.mix`).** The `mix_effect` term is now explicit: the
basket is the team's own product mix at its own net prices, so revenue and
cost of goods are summed product by product.

```
share[p]  = catalogue[p] × customer_pull[p] × price_pull[p]          (renormalised)
customer_pull[p] = Σ_s orders_by_segment[i,s] × affinity[p,s]
                 ÷ Σ_s stores_mix[s] × affinity[p,s]
price_pull[p]    = (rel_price[p] ÷ range_avg_rel_price)^(-4 × Σ_s buyers[p,s] × w_price[s])
units[p]  = orders × units_per_order × ship × (share[p]·(1−H) + push[p] + uplift × pack[p])
revenue   = Σ_p shipped[p] × net_price[p] − pack saving,   AOV = revenue ÷ orders
```

**Pack uptake.** Each pack's appeal follows its saving against three singles:
`appeal = min(1.6, 0.1 + 11 × saving)` for a pack at or below three singles,
and nothing above (`0.1 − 6 × overprice`, floored at 0). Units sold in packs run
about 3× the extra units packs add - most pack buyers would have bought the
units anyway - so the saving is given away on all of them. A small saving
earns most; past about 12% a pack loses money; a pack with no saving draws
only convenience buyers and a dear one does nothing.

`affinity` comes from each product's main and second buyer segments
(audiences.csv), tilted by tier against each segment's willingness to pay.
`stores_mix` is the size-weighted customer mix of all teams, so identical teams
sell exactly the catalogue mix and the baseline does not move. `push` is one
unit of the promoted product per order a product campaign brings in. Stock is
consumed per product and a line that runs out sells what it had. Purchase
orders are split by last month's demand per product (M3), and M17 records a
per-product P&L that adds up to M14.

---

## M10 — Fulfilment & delivery

```
capacity      = warehouse_orders_cap + 3pl_share × THREE_PL_ELASTIC_CAP
overflow      = max(0, orders - capacity)
sla_attainment = 1 - 0.6 × (overflow / orders) - courier_delay_factor
```

Delivery outcome:
```
courier_success = Σ_c mix[c] × success_rate[c]
delivered_prepaid = orders × prepaid_share × courier_success
rto_rate  = RTO_base × (1 + 0.5·(1 - sla_attainment)) × (1 - 0.6·prepaid_incentive_norm)
delivered_cod = orders × cod_share × courier_success × (1 - rto_rate)
delivered = delivered_prepaid + delivered_cod
```

RTO units return to stock at `RTO_RECOVERY = 0.92` (some damaged in transit).
Forward *and* reverse shipping cost is incurred on every RTO — this is the line
that teaches COD economics.

---

## M11 — Returns (one-round lag)

```
return_rate = RET_BASE × (1 + gap_penalty_q) × (1 + 0.8·(1 - AQ)) × policy_mult
returns[t]  = delivered[t-1] × return_rate
recovered   = returns[t] × RESELL_RATE          RESELL_RATE = 0.78
```

`policy_mult`: free returns 1.35, customer pays 0.85, restocking fee 0.70.
Free returns raise return rate **and** raise conversion and repeat rate. The
net is genuinely ambiguous and depends on margin — which is the point.

---

## M12 — Customer ledger

Cohorts are tracked individually. For cohort `k` acquired in round `k`:

```
churn[k,t]  = churn_base[k] × (1 + 0.9·experience_penalty[t-1]) × (1 - 0.5·retention_effect[t])
active[k,t] = active[k,t-1] × (1 - churn[k,t])
repeat[k,t] = active[k,t] × freq[k] × repeat_mult[t]
```

`churn_base[k]` is set by the **acquisition channel and segment mix of that
cohort**, not by a global constant:

| Acquisition source | churn_base | freq (orders/round) |
|---|---|---|
| Google Search | 0.14 | 0.42 |
| Organic / direct | 0.11 | 0.48 |
| Meta | 0.19 | 0.34 |
| TikTok | 0.26 | 0.24 |
| Influencer | 0.21 | 0.31 |
| Marketplace | 0.31 | 0.19 |
| **Deal-driven (discount > 25%)** | **0.44** | **0.11** |

This table is the engine's most important single artefact. It is what makes
discounting a trap: a Deal Hunter cohort costs the same CAC and returns a
quarter of the lifetime value. Teams see it only via MR-10.

```
repeat_orders[t] = Σ_k repeat[k,t]
new_orders[t]    = max(0, orders[t] - repeat_orders[t])
new_customers[t] = new_orders[t] / FIRST_ORDER_UNITS
```

New cohort `t` is stamped with the channel mix that acquired it.

---

## M13 — Experience, service & ratings

```
tickets[t]  = orders[t] × TICKET_RATE + backlog[t-1] + returns[t] × 0.6
capacity    = agents × 900 × ROUND_MONTHS × (ai_cs ? 2.5 : 1.0)
backlog[t]  = max(0, tickets[t] - capacity)
sla_hit     = clamp(1 - backlog[t]/tickets[t], 0, 1)
```

Backlog carries forward and compounds. A service problem ignored for two rounds
is not twice as bad — it is considerably worse, because the backlog is added to
next round's ticket volume.

```
rating_target = 2.5 + 1.2·AQ + 0.6·ADR + 0.4·sla_hit + 0.2·packaging_tier - gap_penalty
rating[t]     = rating[t-1] + 0.30 × (rating_target - rating[t-1])
NPS[t]        = 100 × (0.42·(rating[t] - 3) + 0.3·sla_hit + 0.28·ADR) - 20
```

Ratings move at 30% per round in both directions. Reputation is slow to build
and slow to lose — which is realistic and is why the perception gap takes
rounds to surface.

---

## M14 — Costs & P&L

```
Gross revenue
  - discounts & promo
  - returns & RTO revenue reversal
= Net revenue
  - COGS (delivered + unrecovered returns)
= Gross profit
  - fulfilment (pick/pack + courier forward + courier reverse + RTO round-trip)
  - payment costs (gateway fees × prepaid + COD handling fee × cod)
  - marketing (all G3 + affiliate commission on attributed orders)
  - marketplace commission
= Contribution margin
  - payroll, warehouse fixed, technology ongoing, research purchases
= EBITDA
  - depreciation on capex
  - interest on credit line
= Net profit
```

**RTO cost is a separate line, not folded into fulfilment.** Teams must see it
to reason about COD, and it is the number most of them have never had to look
at directly.

**As built - lines added since the specification:**

| Line | Where | Rule |
|---|---|---|
| Stock holding cost | Overheads | `inventory_holding_rate` (2.1%) of stock value a month |
| Write-down of ageing stock | Overheads | 10% a month of the value of cover beyond `inventory_obsolescence_rounds` (6) months |
| Restocking fee on stock returned | Overheads | What the supplier keeps on 7.6 (50%) and 1.3 (20%) returns |
| Packaging above a plain box | Cost to serve | Full-cost games: PKR 25 branded, PKR 70 premium a shipped order |
| 3PL handling | Cost to serve | Full-cost games: PKR 30 an order through the 3PL (8.2) |
| Sourcing to your quality positioning | Cost of goods | Full-cost games: claiming a tier (1.5) other than the one sourced costs or saves the sourcing difference |
| Affiliate commission | Marketing | Rate (3.6) on partner-tracked sales only, in working-affiliate games |
| Marketplace commission | Cost to serve | 14.5% on marketplace orders only |
| Interest on credit drawn | Below EBITDA | `credit_drawn × credit_rate_annual (22%) / 12` |

Every subtotal and margin is recorded per product too (M17), and adds up to
the P&L.

---

## M15 — Cash & working capital

Cash is where most teams actually fail, so the timing must be explicit.

| Flow | Timing |
|---|---|
| Prepaid orders | Gateway settles T+3 days → same round |
| COD orders | Courier remits T+12 to T+21 days → **next round** |
| Marketplace | Payout T+15 → next round |
| Supplier — advance | At PO placement |
| Supplier — 30d | Next round |
| Supplier — 60d | Two rounds out |
| Marketing | Same round |
| Payroll, fixed | Same round |
| Capex | At commitment, in full |

```
cash[t] = cash[t-1] + inflows[t] - outflows[t]
runway  = cash[t] / max(1, -net_operating_cf[t])
```

A team growing 30% per round on 62% COD with advance supplier terms **runs out
of cash while profitable.** That is the single most valuable finance lesson in
the sim and it falls directly out of this table.

Credit line draws automatically if `cash < 0` and headroom exists, at a penalty
rate. Below zero with no headroom: insolvency, instructor alerted, team
continues under administration with all discretionary spend capped.

**As built.**
- *Loan rules (`world.loans`, new games from month 1; the Fall-2026 game from
  month 5):* `loans.settle` draws on the approved loan (12.6) only as bills need
  it; bills already owed are paid regardless and the bank covers any gap up to
  `credit_ceiling` (PKR 24M), reported as unplanned borrowing; cash above one
  month of fixed costs repays the loan, plus any extra repayment (12.7).
- *Automatic line (older games until switched):* `cash < 0` draws headroom
  automatically, as specified, at the same 22%.
- *Refunds:* cash from stock returned to the supplier (7.6, 1.3, off-range) and
  from a withdrawn lever (`tech_refund`) are their own cash lines, kept out of
  receipts and operating cash flow.
- *Insolvency:* cash still below zero after settlement sets `in_administration`
  (M0 caps spending next month); it clears when cash is back above zero with
  the loan under half the limit. P5 scores 0 for the rest of the run.

---

## M16 — Research report generation

```
true_value   = state[metric]
biased       = true_value × study.bias            (default 1.0)
ε            = normal(0, study.error_band / 2)    seeded on (run_id, t, team, study_code)
reported     = biased × (1 + ε)
```

**The seed must not include a purchase counter.** Re-buying the same study in
the same round returns the identical number. Without this, teams re-buy to
average out the noise and the uncertainty lesson is lost.

Lag-1 studies are queued and delivered with round `t+1` results, stamped with
"as of Round t".

---

## M17 — Scoring & persist

Scorecard per `08-scoring.md`. Persist the full state vector, the resolved
decisions, the RNG seed and the config hash. That quadruple is what makes the
round replayable, and replay is what settles disputes.

**As built.** Each month's record carries the rules it ran under (`rules`), its
decision tally for decision quality (open, taken, memo), the product P&L, stock
moves, the month's cash flow line by line, and who bought each product, so the
report, the Excel workbook and the console all read the same numbers. The web
app saves the world at every month end (`round_log`), which is what rollback,
preview and the rebuilt early-month detail (`ecomsim/backfill.py`) read.

---

## Calibration test — build this first

Before any other work, the model must satisfy:

> **At default decisions, with 8 teams, no events, the engine must reproduce the
> Round 0 baseline in `00-game-world.md` to within 2% on every headline metric,
> and hold it stable for 12 rounds.**

Revenue PKR 12,000,000 · orders 4,000 · AOV PKR 3,000 · sessions 190,000 ·
CR 2.1% · gross margin 38% · contribution margin 9% · CAC PKR 850 · repeat
share 22% · rating 4.1.

If the engine drifts off baseline with nobody making any decisions, every
parameter downstream is being fitted to a broken foundation. **Do not proceed
past this test.** It typically takes three or four days of tuning and it will
save weeks.
