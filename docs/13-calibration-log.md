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
