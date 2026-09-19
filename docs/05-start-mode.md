# 05 — Start Mode: Going Concern vs Founding Round

Two supported ways to begin, set by `START_MODE`.

| Mode | Begins with | First operating round | Suits |
|---|---|---|---|
| `going_concern` | Identical running business, no setup | Round 1 | Short modules; a first cohort while the model is still being calibrated |
| `founding` | **Round 0 setup**, then operations | Round 1 | Full semester; *E-Commerce in Practice*; returning cohorts |

`docs/00-game-world.md` specifies `going_concern`. This document specifies
`founding` and the reasoning for preferring it.

---

## Why not build from absolute zero

The intuitive version — teams start with nothing and build a business across
Rounds 1–12 — fails for four reasons, and it is worth naming them because the
failure is not obvious until it has wasted a cohort.

1. **No feedback loop when it matters most.** The first three rounds produce
   almost no operating data. Teams make their most consequential decisions
   (positioning, category, sourcing) at the exact moment they understand the
   model least, and do not learn whether they were right until Round 5.
2. **Variance becomes fate.** A poor founding choice made in ignorance
   compounds. By Round 4 two teams are uncatchable and three are disengaged.
3. **The engine misbehaves at near-zero scale.** Share models, CAC curves and
   cohort retention are all unstable at tiny volumes. Round 1 with 40 orders
   produces noise, not signal.
4. **It teaches the wrong subject.** Building from zero teaches startup
   formation. The course teaches e-commerce management. These are different
   skills and the operational interconnection chain — the spine of this sim —
   only becomes visible at scale.

The answer is not "no founding decisions." It is **founding decisions made with
a projection, at a scale where the engine works.**

---

## Round 0 — the Founding Round

All teams receive **identical capital and identical constraints**, then make
bounded founding choices that produce *different but balanced* starting
positions. Operations begin in Round 1.

### Design principle

> **Year 0 differentiates strategy, not endowment.**

Every valid founding configuration must be viable. Teams should end Round 0
with different *shapes* of business — not different *sizes*. Premium positioning
yields lower volume, higher margin, higher repeat, higher CAC, slower growth.
Value positioning yields the inverse. Neither is correct.

This preserves the comparability that makes `going_concern` attractive while
delivering the ownership and founding lessons it lacks.

### Endowment (identical for all teams)

| Item | Value |
|---|---|
| Founding capital | PKR 25,000,000 |
| Monthly payroll budget | PKR 1,400,000 |
| Available SKU catalogue | 40 (filtered by category choice) |
| Time to launch | Round 0 is setup; no revenue |

### Round 0 decision set (14 decisions)

| # | Decision | Type | Effect |
|---|---|---|---|
| D0.1 | Brand name & positioning statement | TEXT | Ownership. Lightly graded |
| D0.2 | Category focus — pick 2 of 5 | MULTI | Skincare / Haircare / Home care / Personal hygiene / Baby care. Sets available catalogue, margin profile, return rate, repeat profile |
| D0.3 | Target segment priority — rank | RANK | Sets initial brand perception tilt and which segment acquires cheapest |
| D0.4 | Positioning tier | SELECT | Value / Mainstream / Premium. Sets price band, margin, expected rating, CAC |
| D0.5 | Business model | SELECT | Own-site D2C / Marketplace-first / Hybrid. Sets starting traffic mix and commission exposure |
| D0.6 | Opening assortment | MULTI | 12–18 SKUs from the filtered catalogue |
| D0.7 | Sourcing strategy | SELECT | Local / Import / Mixed. Cost, lead time, FX exposure |
| D0.8 | Capital allocation | CURR ×4 | Inventory / marketing / technology / reserve. Must sum to PKR 25M |
| D0.9 | Technology stack | SELECT | Basic (PKR 800k, UX ceiling 0.55) / Standard (2.5M, ceiling 0.75) / Custom (6M, ceiling 0.92, +2 rounds to launch) |
| D0.10 | Fulfilment model | SELECT | 3PL (variable, no capex) / Own warehouse (PKR 5M capex, lower variable) |
| D0.11 | Payment setup | SELECT ×2 | COD on/off; gateway A/B/C |
| D0.12 | Headcount allocation | NUM ×4 | Marketing / Ops / CS / Analytics within payroll budget |
| D0.13 | Founding research | MULTI | Reduced menu — MR-01, MR-06, MR-11, MR-15 at **50% price** |
| D0.14 | Business plan memo | TEXT | 600 words with explicit Round-6 and Round-12 targets |

### The pro-forma preview

**This is the mechanism that makes Round 0 safe.** Before committing, teams see
a live projection of their resulting Round 1 position from their current
choices: projected sessions, conversion rate, orders, AOV, gross margin,
contribution margin, monthly burn and runway.

They can iterate freely until they submit.

The preview is a **projection, not a promise** — it assumes market-average
competitive intensity and ignores rival behaviour entirely. Reality in Round 1
will deviate, sometimes sharply. That gap is the first lesson of the run, and
it lands far better than being blindsided.

### Balance constraints on Round 0

Enforced by the engine; a configuration violating these cannot be submitted.

| Constraint | Threshold |
|---|---|
| Projected Round 1 revenue across all valid configs | Within ±15% of PKR 12,000,000 |
| Projected contribution margin | ≥ 4% |
| Projected runway at Round 1 burn | ≥ 8 rounds |
| Inventory allocation | ≥ 25% and ≤ 60% of capital |
| Reserve allocation | ≥ 10% of capital |

The inventory floor and reserve floor exist because, given a free hand, roughly
a third of teams will allocate ~80% of capital to inventory and be insolvent by
Round 3. That is a real lesson, but it is better taught by a Round 4 cash
squeeze than by elimination in Round 3.

### Reversibility

Most Round 0 choices are changeable later, at a switching cost. A few are
deliberately sticky.

| Decision | Reversible? | Switching cost |
|---|---|---|
| D0.2 Category focus | Yes, from Round 3 | Dead stock write-off, 1 round of assortment disruption |
| D0.4 Positioning tier | **Partially** | One tier per 3 rounds; costs 40% of brand equity stock |
| D0.5 Business model | Yes | Marketplace onboarding takes 1 round |
| D0.7 Sourcing | Yes | One full supplier lead time |
| D0.9 Tech stack | Upgrade only | Full capex again, no credit for prior spend |
| D0.10 Fulfilment | Yes | Warehouse capex is sunk |

**Positioning is the sticky one, by design.** "Repositioning is slow and
expensive" is one of the most valuable things a commercial manager can learn,
and it is best learned by trying to do it in Round 6 and finding it takes until
Round 9.

---

## Scoring treatment

Round 0 is **not scored directly.** Two indirect effects:

1. The business plan memo (D0.14) is worth **3 of the 10 decision-quality
   points** in the final scorecard.
2. **The Round-0 targets become the Round-12 benchmark.** The closing review
   asks each team to explain the variance against the targets they set
   themselves in Round 0.

That second mechanism is the strongest pedagogical closing available. *"You
committed to 30% repeat rate and PKR 620 CAC. You delivered 19% and PKR 940.
Walk us through what you got wrong and when you should have known."*

No externally imposed benchmark carries the same weight as one the team wrote
itself twelve rounds earlier and then forgot about.

---

## Cost of adding Round 0

| | |
|---|---|
| Contact time | +1.5 to 2 hours |
| Build effort | ~2 weeks (the pro-forma preview is most of it) |
| Engine impact | Moderate — Round 0 produces an initial state vector; the round engine itself is unchanged |

The pro-forma preview is the part that must not be cut. Without it, Round 0
becomes a blind lottery and reintroduces the exact failure mode that
building-from-zero was rejected for.

---

## Decision — LOCKED

**`founding` is the build target and the default.** Equal capital, 14 founding
decisions, pro-forma preview, then 12 operating rounds.

`going_concern` remains available as a configuration and costs almost nothing
to retain, since it is simply Round 0 skipped with a fixed initial state vector.
Two uses for it:

- **Engine calibration.** While tuning parameters, an identical start across
  all teams isolates decision effects from founding-configuration effects.
  Balance work should be done in `going_concern` even though students never
  see it.
- **Short modules.** A 6-week guest module has no room for a founding round.

Neither changes what gets built. `founding` is the product.
