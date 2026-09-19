# 04 — Configurability

Everything an instructor can change before or during a run, and the bands
within which the economic model stays well-behaved.

**Architectural rule underpinning all of it:** the engine never reads a decision
directly. It reads a *resolved value* — the team's decision if that decision is
enabled, otherwise the configured default. This is what makes every decision
independently switchable without breaking the model.

---

## 1. Team count

Supported: **2 to 16 teams.** Recommended: 4–10.

### Market scaling

Category size is derived, never fixed:

```
category_size = (N_teams × starting_team_revenue) / TEAM_SHARE_TOTAL
```

With `TEAM_SHARE_TOTAL = 0.64`, AI incumbents always hold ~36% and each team
starts at the same share regardless of N. Per-team economics are identical at
N=2 and N=12, so scorecards remain comparable across sections.

| N teams | Category size (PKR/mo) | Share per team |
|---|---|---|
| 2 | 37,500,000 | 32% |
| 4 | 75,000,000 | 16% |
| 8 | 150,000,000 | 8% |
| 12 | 225,000,000 | 5.3% |
| 16 | 300,000,000 | 4% |

### Adjustments required at the extremes

**N ≤ 3 — duopoly instability.** With two teams the logit share model becomes
a direct tug-of-war: every point one team gains comes visibly from the other,
and a single aggressive discount can swing 15 share points in one round. Fixes,
applied automatically:

- Raise AI incumbents from 2 to **4**, so teams compete against the field rather
  than only each other
- Reduce `SHARE_SENSITIVITY` from 2.0 to **1.4**, damping the swing
- Disable the Round 6 price-war event (it is redundant — a duopoly generates
  its own)

**N ≥ 12 — dilution and event fatigue.** Each team holds ~5% share, so
individual actions barely move the market and the competitive lesson weakens.
Fixes:

- Raise `SHARE_SENSITIVITY` to **2.6**, so actions still register
- Split teams into **two leagues** of 6–8 that share a category but are scored
  separately; this also halves debrief time, which is the real constraint
- Enable segment-targeted events so different teams face different shocks

**Above 16** the limit is not compute — it is that an instructor cannot run a
meaningful debrief across more than ~16 decision sets in a class session.

---

## 2. The decision registry

**56 is a curated preset, not the complete set.** The registry defines **92
decisions**; the instructor activates a subset.

### Presets

| Preset | Fields | Suits |
|---|---|---|
| **Foundation** | 24 | Undergraduate, 6-week module, first exposure |
| **Standard** | 38 | MBA elective, 8–10 week course |
| **Advanced** | 56 | The default. `01-decision-list.md` |
| **Expert** | 92 | Executive education, full-semester, or a second run with a returning cohort |

### Registry beyond the Advanced 56

Extension decisions, by group. Each is fully specified in the params sheet but
disabled in the Advanced preset.

**G1 Assortment (+5):** SKU-level merchandising priority · cross-sell rules ·
gift-wrap / personalisation option · pre-order policy · catalogue expansion via
third-party sellers

**G2 Pricing (+4):** price per marketplace separately · member-only pricing ·
bulk / multi-buy tiers · psychological price-point rounding policy

**G3 Marketing (+6):** YouTube spend · programmatic display · WhatsApp broadcast ·
sponsorship / event spend · agency vs in-house · geo-targeting weights

**G4 Channel (+4):** second marketplace · own-app vs web budget split ·
social commerce storefronts · wholesale / B2B channel

**G5 Experience (+3):** site search investment · localisation (Urdu / English) ·
A-B testing programme budget

**G6 CRM (+4):** referral programme · subscription / replenishment offer ·
review-incentive programme · lapsed-customer segmentation depth

**G7 Supply (+4):** import vs local sourcing · FX hedging · consignment vs
owned inventory · supplier development investment

**G8 Fulfilment (+4):** second warehouse city · returns-processing capacity ·
same-day city selection · reverse-logistics partner

**G9 Payments (+2):** BNPL enablement · wallet partnership

**G10 Service (+2):** CS channel mix (call / chat / WhatsApp) · proactive
order-status communication

**G11 Technology (+3):** customer data platform · fraud-detection engine ·
inventory-optimisation AI

Total: 56 + 41 = **97 defined**, of which 92 are simultaneously activatable
(5 are mutually exclusive with Advanced-preset decisions).

### The rule that makes this work

**Every decision must declare a `default_when_disabled` value.** The engine
always has a value. Disabling a decision removes student agency over it; it
never removes it from the model.

Example: if 9.2 (prepaid incentive) is disabled, the engine uses the configured
default of 3%. COD economics still run; students simply cannot tune them.

---

## 3. Instructor control over introduction timing

Every decision carries a per-run configuration row:

| Field | Meaning |
|---|---|
| `enabled` | In this run at all? |
| `unlock_round` | First round students may set it |
| `lock_round` | Optional — round after which it freezes (for forced-commitment exercises) |
| `default_when_disabled` | Value the engine uses while locked or disabled |
| `visible_when_locked` | Show greyed-out (builds anticipation) or hide entirely |

This supports **mid-run introduction**. An instructor watching teams coast
through Round 4 can unlock the private-label track early, or hold back
Q-Commerce to Round 7 for a cohort that is struggling.

Constraint: unlocking a decision mid-run **cannot** retroactively change prior
rounds. The engine is deterministic and replayable; changing an unlock round
invalidates the replay from that round forward, and the instructor console
must warn before allowing it.

---

## 4. Round length and total horizon

Round length is a parameter: `ROUND_MONTHS ∈ {1, 3, 6, 12}`.

### The honest trade-off

**Round length determines which lessons are teachable at all.** This is not a
cosmetic setting.

| Horizon | Config | What it teaches | What it cannot teach |
|---|---|---|---|
| **1 year** | 12 × 1 month | Stock-outs, promo calendar, cash conversion cycle, CAC volatility, CS backlog, courier SLA | Capability payback, brand compounding, market-cycle strategy |
| **3 years** | 12 × 3 months | Cohort LTV realisation, capability payback, category entry, one full cycle | Weekly operational rhythm, promo-calendar management |
| **5 years** | 10 × 6 months | Portfolio strategy, market cycles, capital allocation, competitive repositioning | Essentially all operational e-commerce management |

Note the arithmetic on the Markstrat comparison: 5 years at annual rounds is
only **5 decision points** — too few for any learning curve. A 5-year horizon
needs 10 six-month rounds or 20 quarterly rounds.

### Recommendation for *E-Commerce in Practice*

**12 monthly rounds.** The course's central lesson is the interconnection chain
— ad spend → traffic → demand → stock-out → conversion → complaints → cash.
That chain is **invisible at annual granularity**. At `ROUND_MONTHS = 12` a
stock-out is not an event, it is an annual average; a promo calendar does not
exist; a 21-day supplier lead time rounds to zero.

Markstrat's annual periods work because Markstrat teaches *marketing strategy*,
where the unit of decision genuinely is the year. E-commerce is an
operationally-paced business, and copying the horizon copies the wrong thing.

### If you want the 5-year strategic view as well

Run the **Epoch configuration**: 12 monthly rounds (Year 1, full decision set)
followed by 4 six-month rounds (Years 2–3, policy-only decision set). Students
first learn to operate, then learn that operating well is not the same as
allocating capital well. 16 rounds total, ~14 contact hours.

This is more work to build than a single fixed granularity, and I would not
attempt it before the monthly version has run with two cohorts.

### What scales with round length, and what does not

| Behaviour | Handling |
|---|---|
| Revenue, orders, spend, fixed costs | Linear × `ROUND_MONTHS` |
| Rates — CR, margin %, return rate, RTO | **Unchanged** |
| Prices, AOV | **Unchanged** |
| Decay rates (brand equity, creative quality) | Compound: `1 − (1 − d)^ROUND_MONTHS` |
| Seasonality | Amplitude shrinks toward zero as round length rises; **disabled at 12** |
| Supplier lead times | Converted to rounds, minimum 1; **below 0.25 rounds, treated as instant** |
| Project lead times | Re-specified per granularity, **not** auto-converted |
| Cash conversion cycle | Re-specified per granularity — this is the one most often got wrong |

Project and cash-cycle values must be authored per granularity, not derived.
Auto-conversion produces a 2-round AI-module build at monthly granularity
becoming a 2-round build at annual granularity, which is nonsense.

### Decision granularity flags

Each decision declares `min_granularity`. At coarser round lengths it either
auto-disables or converts to a policy setting:

| Decision | Monthly | Quarterly | 6-month | Annual |
|---|---|---|---|---|
| 2.3 Promo window participation | Action | Action | Policy | Disabled |
| 7.1 Purchase order quantity | Action | Action | Policy (cover target) | Policy |
| 8.3 Courier mix | Action | Policy | Policy | Policy |
| 10.1 CS headcount | Action | Action | Action | Policy |
| 1.3 Private-label project | Action | Action | Action | Action |
| 3.9 Brand spend | Action | Action | Action | Action |

---

## 5. Parameter levers and safe ranges

Every economic parameter is instructor-editable, in three bands.

- **Green** — model stays well-behaved. Change freely.
- **Amber** — valid, but distorts balance. Console warns; re-validate before use.
- **Red** — blocked. The model breaks or a dominant strategy appears.

### The three parameters that break the sim

These deserve separate mention. Almost every broken build of a simulation like
this traces to one of them.

| Parameter | Default | Green | Amber | Red — and why |
|---|---|---|---|---|
| **Marketing saturation exponent** | 0.60 | 0.45 – 0.75 | 0.35–0.45, 0.75–0.90 | **> 0.90**: returns become near-linear, "spend everything on Meta" dominates and no other decision matters. **< 0.30**: marketing does nothing, G3 becomes decorative |
| **Share sensitivity (logit exponent)** | 2.0 | 1.2 – 3.0 | 3.0 – 4.0 | **> 4.5**: winner-take-all — a small early lead compounds to total share by Round 6 and the rest of the class disengages. **< 0.6**: share barely responds, decisions feel inert |
| **Starting cash** | 25,000,000 | 15M – 50M | 10M–15M | **< 8M**: a team making one ordinary mistake in Round 2 is mathematically unrecoverable. Death spirals destroy more classes than any other single setting |

### Full parameter bands

**Demand & pricing**

| Parameter | Default | Green | Red | Failure mode |
|---|---|---|---|---|
| Own-price elasticity | −1.8 | −2.4 – −1.3 | < −3.5 | Price-war spiral to zero margin |
| | | | > −0.9 | Price cuts never pay; pricing becomes trivial |
| Cross-price elasticity | 0.7 | 0.4 – 1.1 | > 1.8 | One team's discount empties every rival |
| Category growth / round | 2.5% | 0% – 5% | > 10% | Growth covers every mistake; no learning |
| Seasonality amplitude | ±45% | 0% – ±60% | > ±100% | Timing luck dominates decision quality |

**Marketing & acquisition**

| Parameter | Default | Green | Red | Failure mode |
|---|---|---|---|---|
| Adstock carryover | 0.35 | 0.20 – 0.50 | > 0.70 | Past spend dominates; current decisions stop mattering |
| CPM inflation vs total market spend | 0.25 | 0.10 – 0.45 | > 0.70 | Any spend increase is self-defeating; teams stop spending |
| Creative quality weight on CTR | 0.30 | 0.15 – 0.45 | > 0.60 | 3.8 becomes the only marketing decision |
| Brand equity decay / round | 8% | 4% – 15% | > 25% | Brand investment never pays; 3.9 becomes a trap not a trade-off |

**Conversion & experience**

| Parameter | Default | Green | Red | Failure mode |
|---|---|---|---|---|
| Base conversion rate | 2.1% | 1.2% – 3.5% | < 0.5% | Traffic economics collapse; nothing is affordable |
| | | | > 8.0% | Everything is profitable; no trade-offs exist |
| Stock-out CR penalty | 0.45 | 0.25 – 0.65 | > 0.85 | One stock-out ends a team's run |
| Rating weight on CR | 0.20 | 0.10 – 0.35 | > 0.50 | Rating becomes the only thing that matters |

**Unit economics**

| Parameter | Default | Green | Red | Failure mode |
|---|---|---|---|---|
| Gross margin | 38% | 28% – 50% | < 20% | No room for marketing; the game is unplayable |
| | | | > 65% | Everything is affordable; no trade-offs |
| COD share | 62% | 30% – 75% | > 90% | Cash model degenerates; working capital lesson lost |
| RTO on COD | 18% | 8% – 28% | > 40% | Turning COD off becomes unambiguously correct; 9.1 becomes trivial |
| Return rate | 9% | 4% – 18% | > 30% | Returns swamp every other effect |
| Repeat rate | 22% | 12% – 35% | > 55% | LTV so high that CAC never binds; retention lesson inverts |

**Competitive & structural**

| Parameter | Default | Green | Red | Failure mode |
|---|---|---|---|---|
| AI incumbent aggression | 0.5 | 0.2 – 0.8 | > 0.95 | Incumbents beat every team; agency disappears |
| Event severity multiplier | 1.0 | 0.5 – 1.6 | > 2.5 | Outcomes are event luck, not decision quality |
| Credit line ceiling | 15M | 5M – 30M | > 50M | Cash never binds; working capital lesson lost |

---

## 6. Why individual ranges are not sufficient

**Every parameter can sit inside its green band and the model can still be
broken.** The dangerous cases are joint:

- High gross margin + low CPM inflation + high saturation exponent → unlimited
  profitable spend. Each is green; together they are a dominant strategy.
- Low starting cash + long supplier lead time + high MOQ → mathematically
  guaranteed stock-out in Round 2 regardless of decisions.
- High repeat rate + low churn + high brand decay → retention investment is both
  essential and impossible to sustain.

### Mandatory post-configuration validation

Any change to a parameter outside its default must trigger an automated
validation run before the configuration can be used with students: **200
scripted strategies × the configured settings**, checked against seven
invariants.

| # | Invariant | Threshold |
|---|---|---|
| 1 | No dominant strategy | Best scripted strategy scores < 2.5× median |
| 2 | No death spiral | No strategy is unrecoverable before round `N/2` |
| 3 | Discounting is a trap | Max-discount strategy ranks below balanced by round 8 |
| 4 | Margin is viable | Contribution margin at default decisions ∈ [5%, 15%] |
| 5 | Cash is binding but survivable | ≥ 20% of strategies need the credit line; < 10% go insolvent |
| 6 | Share conserves | Team + incumbent share sums to 1.00 ± 0.001 every round |
| 7 | Research pays | Strategies buying 3–6 studies/round outperform both zero-research and buy-everything |

Invariant 7 is the one to watch. If buying everything wins, research prices are
too low. If buying nothing wins, the studies do not carry enough real signal.
Either way the Markstrat mechanism has failed and the prices need rework.

This validation harness should be built **alongside the engine, not after it**.
It is the only thing that lets an instructor safely touch the parameters, and
it is what turns "we think it's balanced" into something demonstrable.
