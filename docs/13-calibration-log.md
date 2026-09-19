# 13 — Calibration Log

Domain judgements made about parameter values, and why.

**This file cannot be reconstructed.** Claude can re-derive code from the specs;
it cannot re-derive why you decided RTO should be 22%. Neither will you, in four
months. Record every judgement here as it is made.

Format: one entry per decision, newest first.

---

## Template

```
### YYYY-MM-DD · parameter_name: old → new

**Basis:** where the figure came from — experience, a specific source, a
reasoned argument.

**Confidence:** high / medium / low.

**Invalidated by:** what evidence would change this.

**Downstream:** which invariants or metrics this is expected to move.
```

---

## Entries

### 2026-09-19 · Burst 3b — working capital smoothed; inventory made a decision

**DECIDED: smooth the working-capital cycle.** The ~40% cash swings were not
"what this business does" - they were two modelling artifacts.

1. Supplier terms and COD remittance were rounded to whole rounds, so a month
   of purchasing landed in a single lump. Both now book across the rounds their
   lag actually spans (`M15._schedule`), and terms moved 30 -> 45 days.
2. The bootstrap seeded two discrete purchase orders whose payables piled up a
   few rounds in. It now seeds the **steady-state ledger** - one round of
   purchases due next round plus the tail of the one before, and COD already
   despatched and not yet remitted.

**Peak cash movement fell from 41% to 24%.** The test is back to a flat 30%
with no exclusions and no xfail. I had moved that threshold five times across
bursts 2 and 3; the cause was findable and none of those moves were justified.

**DECIDED: keep growth_max insolvency.** Aggressive growth that outruns its
working capital should bankrupt a team, so `growth_max` is reclassified as an
archetype that exists to fail rather than a viable strategy the invariants must
protect.

### OPEN QUESTION — shrinking currently wins

`cash_preservation` ranks **#1 of 20**, and the cause is structural rather than
a bad anchor:

- The business cannot reach EBITDA breakeven (burst 3, finding 7), so **cutting
  spend always improves P1**, and nothing pushes back hard enough.
- **LTV:CAC rewards not acquiring customers.** A team that acquires almost
  nobody has excellent unit economics and no business. This is the same class
  of defect as the harvester exploit, but it cannot be fixed by changing when
  CAC is measured - the ratio itself is scale-blind.

Three ways out, in order of how much I would trust them:

| | Change | Cost |
|---|---|---|
| A | Make profitability reachable - `payroll_base` 1.4M -> ~1.0M | Softens "coasting is almost fatal", which was an explicit decision |
| B | Pair LTV:CAC with scale - reweight P3 toward absolute customer value | Departs from the published docs/08 weights |
| C | Accept and teach it - "why did shrinking win?" is a real debrief | Leaves a scorecard that rewards shrinking |

This is a judgement about what the course should teach, not a parameter to
tune, so it is left open.


### 2026-09-19 · Burst 3 — balance (11 of 12 invariants)

Seven scoring and engine defects found by the invariant suite. Each was a real
bug, not a tuning gap; the archetypes designed to fail were what surfaced them.

**1. Growth was measured against the team's own Round 1.** Sandbagger coasted
six rounds to suppress its own denominator, then scored 19.8/20 on growth off
the trough it had dug. Growth is now measured against the shared starting
position. *Sandbagger fell from #1 to #11.*

**2. LTV:CAC read ~0.25 for every team** — it charged acquisition cost twice
(contribution margin is already net of marketing, then divided by CAC again)
and excluded the customer's first order. LTV now uses pre-marketing
contribution and counts the acquisition order. **Ratios now run 1.67-2.71,
with discounter at 0.23** - the deal-cohort trap finally visible in the metric
built to show it.

**3. LTV:CAC used terminal CAC**, so a team that stopped marketing in the last
rounds had CAC near zero and scored maximum. The scorecard was paying for the
harvest it exists to punish. Now lifetime marketing over lifetime customers
acquired, which timing cannot game.

**4. P4 anchors were never updated after burst 2 rebased courier success.**
Every team maxed operations, 15 points of dead weight. Re-anchored twice, to
the reachable frontier.

**5. Inventory turns was a hardcoded 50** for every team - three more dead
points. Now computed from average inventory and COGS flow.

**6. Administration capped spend at the prior round**, which constrains nothing
for a team that blew up spending 3x. Now halves discretionary spend and blocks
research as well as capex.

**7. No strategy could reach EBITDA breakeven.** Best achievable is
-1.28M/round against fixed costs of 2.17M; the contribution ceiling is ~0.9M,
which IS the approved 9% CM. The scorecard anchors assumed a profitable
business; what we calibrated is a scaling startup. **Re-anchored P1 EBITDA to
the reachable frontier (-22% / -14% / -5%) and re-banded P5 runway to the burn
(<1 fatal, 2.5-6 ideal, >10 under-invested).** The business is unchanged - the
ruler was wrong, not the thing being measured.

**Judgement: `credit_ceiling` 15M -> 25M.** At 15M, coasting consumed exactly
the starting capital over 12 rounds, leaving no headroom for any strategy at
all: retention_led died 41% of the time, tech_led 61%. Raising the ceiling
keeps the burn and keeps coasting fatal - a coasting team still ends at zero,
now carrying interest - while letting a team with a plan fund it at 22% p.a.
*Viable-strategy insolvency fell from 22% to 1%.* Still in the green band.

**Open: I11 scorecard discrimination.** Spread is 29 points against a 35-75
target; sandbagger #11 and harvester #10 against a bottom-40% (#13+)
requirement. Both are now below balanced, so the defences work directionally.
Two known causes: P6 is constant in a scripted harness (real memos and
prediction accuracy add ~6 points of live spread), and **P4 is compressed
because the engine auto-reorders inventory, so decision 7.1 is not really a
team decision yet.** The second is a genuine finding for a later burst, not a
tuning problem.


### 2026-09-19 · Burst 2 — baseline now holds at all N (T2 green)

Solved numerically (`calibrate.py`), not by hand. Nine metrics within
tolerance at N = 2, 4, 8, 12, 16 over 12 rounds. Four judgements were forced
by the baseline being over-determined; each is reversible with one line.

**1. Baseline revenue of 12M is GROSS, not net.** 4,000 orders x PKR 3,000 =
12M is GMV. Net revenue after returns, RTO and failed delivery lands at
~9.2M. The spec's own definition (`docs/10`) makes revenue_net post-leakage,
so 12M cannot be net at these volumes. **Target is now `revenue_gross`.**
*Invalidated by:* deciding 12M should be net, which needs ~5,200 orders.

**2. CM 9% held; marketing default set to 1.48M (was 2.0M); CAC derives to ~477.**
GM 38%, CM 9% and marketing 1.8M cannot coexist with realistic Pakistani
fulfilment costs (courier ~PKR 173/order, RTO round-trips, gateway fees) - at
1.8M marketing CM is ~4.4%. CM is wired into the scoring anchors, so it was
held. **The earlier CAC 850 is dropped as a target; it was inconsistent.**
*Confidence:* medium. CAC ~477 is on the low side for Pakistani D2C personal
care; PKR 600-900 is more typical. *Invalidated by:* choosing to hold CAC 850 instead,
which means CM ~4% or lower fulfilment costs.

**3. Baseline is EBITDA-negative (~-1.3M/round) and burns ~2.1M cash/round.**
Contribution +9.1% but fixed costs (payroll 1.4M, warehouse 340k, tech 180k,
CS 250k) exceed it, and inventory is bought ahead of sale. **A team that does
nothing ends Round 12 with ~1.6M of 25M - and with events on, at zero.**
Inaction is close to insolvency by design.

**DECIDED 2026-09-19: keep `payroll_base` at 1.4M. Coasting is almost fatal.**
Basis: matches how a 12M-GMV D2C brand with ~15 staff actually feels, and
gives the runway lesson teeth. Softer setting (0.9M, ~1.6M burn, ~7M left at
R12) is retained as the option for an undergraduate or pilot cohort.
*Watch in burst 3:* I2 - a team that fumbles R1-R3 may enter administration by
R8. That is acceptable; elimination is not, and the engine does not eliminate. Defensible - a 12M-GMV D2C brand with ~15 staff does burn,
and it gives the runway lesson teeth. **Left as-is; needs an explicit
decision.** *Alternative:* `payroll_base` 1.4M -> 0.9M gives ~-1.0M/round.
*Watch in burst 3:* invariant I2 (no death spiral) - teams that experiment
early will burn faster than baseline.

**4. Courier success rebased to pure logistics (0.94-0.975).** The earlier
0.84-0.92 figures were overall delivery success including customer refusal;
RTO then charged refusal a second time. Total leakage was 30%; now ~21%.
*Confidence:* high on the structure; medium on the exact rates.

**5. T2 runs with `events_enabled = 0`**, as docs/07 and docs/11 specify. The
first solve was accidentally events-on and drifted 5% on orders once the
switch existed. Calibration is always events-off; balance (burst 3) is
events-on.

**Structural fixes that changed levels (not judgements):** AOV now derives
from the SKU basket rather than a free parameter, so GM follows from what is
in the cart; `units_per_order` 1.52 -> 2.424 to hit AOV 3,000 on the
14-SKU basket. Reorder policy now targets cycle + pipeline + safety stock
(safety alone left every team a round short). Forecast basis is
`min(potential, traffic_capacity)` - forecasting on raw potential over-ordered
by the 45% headroom. Bootstrap seeds one round of demand in the supplier
pipeline, payable Round 1, so a going concern starts mid-cycle rather than
placing nothing in Round 1 and lurching. Category size is scaled from the
actual logit at seeded state (`bootstrap._category_scale`), so per-team cash
and orders are identical at N = 2 and N = 16 by construction. Channel `k_base` x4.0 and
cohort `freq` x0.27 baked into `channels.csv`; the scale handles sit near 1.0.

**Solved values (events off):** `cr_base` 0.0175 · `cogs_scale` 0.975 ·
`channel_k_scale` 1.086 · `cohort_freq_scale` 1.039 · `potential_headroom`
1.45 (per-team potential = 1.45 x baseline orders, so traffic binds first,
which matches how a D2C brand at this size actually feels).


### 2026-09-19 · Initial parameter set — all values

**Basis:** Structurally reasoned by Claude, not researched. Relationships and
relative magnitudes are argued in `docs/07-engine-chain.md`; the specific
figures are calibration starting points.

**Confidence:** Low on absolute values. Medium-high on structure and on the
direction and rough magnitude of each relationship.

**Invalidated by:** Any real Pakistani e-commerce benchmark. Expected to be
replaced wholesale during or after the first cohort.

**Downstream:** Everything. Burst 2 exists to make these hold the baseline;
burst 3 exists to make them balanced.

**Explicitly flagged as most likely wrong:**

| Parameter | Default | Why it is suspect |
|---|---|---|
| `rto_base` | 0.18 | Category- and courier-dependent; the figure you personally know best |
| `cod_share_base` | 0.62 | Shifting fast in the real market |
| `cr_base` | 0.021 | Varies hugely by category and traffic mix |
| `aov_base` | 3000 | Entirely category-dependent |
| channel `churn_base` | see `channels.csv` | The deal-driven 0.44 is the most consequential single number in the engine and the least evidenced |
