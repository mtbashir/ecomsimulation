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
