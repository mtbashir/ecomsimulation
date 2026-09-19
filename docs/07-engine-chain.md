# 07 — Engine Chain

The round calculation, module by module. This is the document the economic model
is built from.

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

---

## M1 — Market & seasonality

```
BASE_CATEGORY   = (N_teams × 12_000_000) / 0.64
category[t]     = BASE_CATEGORY × (1 + g)^t × season[t]
```

`g = 0.025` per month. `season[t]` from the table in `00-game-world.md`.
At `ROUND_MONTHS > 3`, `season[t] → 1.0`.

Category is expressed in **PKR of demand**, converted to order potential in M7.

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

Logit share:
```
share[i,s] = exp(β · U[i,s]) / Σ_j exp(β · U[j,s])       β = SHARE_SENSITIVITY = 2.0
```

AI incumbents participate in the denominator with scripted `U` values.

Potential demand:
```
potential[i] = Σ_s category_orders[t] × segment_share[s] × share[i,s]
```

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

```
gross_revenue[i] = orders[i] × AOV[i]
```

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

Scorecard per `08-scoring.md` (to be written). Persist the full state vector,
the resolved decisions, the RNG seed and the config hash. That quadruple is
what makes the round replayable, and replay is what settles disputes.

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
