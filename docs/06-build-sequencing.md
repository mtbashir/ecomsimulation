# 06 — Build Sequencing: Presets and the Engine

**The question:** build Foundation (24 decisions) first, then grow it to
Standard, Advanced and Expert — or build to full depth from the start?

**The answer splits in two**, and conflating the halves is the expensive mistake:

> **Ship incrementally. Build the engine once, at Advanced depth.**

The preset ladder is the right *delivery* strategy and the wrong *engineering*
strategy. Presets are a configuration layer over one engine — not four engines.

---

## Why the engine cannot be grown incrementally

The engine's value is its **causal chains**, not its decision count. A Foundation
engine does not have fewer chains — it has *simplified* ones, and the
simplifications get hardcoded across dozens of formulas.

Concrete example. Foundation has no separate perceived-vs-actual quality, so
the engine carries a single `quality` scalar, referenced in conversion rate,
rating formation, return rate, repeat propensity, segment attractiveness and
share allocation. Adding the perception layer at Standard means splitting that
scalar in two and revisiting **every one of those call sites**, each of which
was calibrated against the single-scalar version.

Three consequences, in increasing order of cost:

1. **Refactor cost.** Roughly 3–4 weeks per tier transition, touching code
   that already works.
2. **Recalibration cost.** Any change to causal structure invalidates the
   parameter calibration. The 200-strategy validation run and the seven
   balance invariants must be re-established from scratch. ~1.5 weeks per tier,
   and it is unavoidable, not optional.
3. **Loss of cohort comparability.** If you run a cohort on the Foundation
   engine and then change the engine, Cohort 2's results are not comparable to
   Cohort 1's. You lose the accumulated calibration evidence that is the whole
   reason for running early cohorts.

Cost 3 is the one that actually hurts. The entire argument for shipping early
is to gather calibration evidence from real students. Changing the engine
between cohorts discards that evidence.

---

## Why incremental shipping still works

Because of the rule already established in `04-configurability.md`:

> Every decision declares a `default_when_disabled` value. The engine never
> reads a decision directly — it reads a resolved value.

Given a full-depth engine, a preset is **a row of boolean flags**. Foundation
is not a smaller engine; it is the same engine with 32 decisions held at
sensible defaults.

### This makes Foundation strictly better, not just cheaper

A Foundation student who over-promises same-day delivery still suffers the
perception gap — rating falls, returns rise, repeat rate drops — because the
mechanism is **live**, even though they cannot tune it. They experience the
consequence without owning the lever, which is exactly how a junior manager
experiences a real business.

On a Foundation-depth engine, that mechanism does not exist at all. The world
is genuinely simpler, and simpler in a way that teaches less.

**Foundation-on-an-Advanced-engine is a better product than
Foundation-on-a-Foundation-engine**, and it is cheaper over the full programme.

---

## Cost comparison

Assumes 1 modeller, 1–2 developers, plus your domain input. Weeks are elapsed,
not person-weeks.

### Path A — build engine at Advanced depth, ship presets as configuration

| Phase | Weeks | Cumulative |
|---|---|---|
| Complete specification (KPI dictionary, engine chain, events, scoring) | 3 | 3 |
| Economic model at **Advanced depth**, spreadsheet/Python | 7 | 10 |
| Calibration + validation harness (200 strategies, 7 invariants) | 3 | 13 |
| Port to TypeScript, golden-file tests against the model | 4 | 17 |
| Round 0 + pro-forma preview + Foundation UI + instructor console v1 | 6 | 23 → **ship Foundation** |
| Standard increment (14 fields: UI + copy only) | 2 | 25 → **ship Standard** |
| Advanced increment (18 fields: UI + copy only) | 2.5 | 27.5 → **ship Advanced** |
| Instructor console full (parameter editing, unlock config, bands) | 3 | 30.5 |
| Playtest, recalibration, hardening | 3 | 33.5 |
| **Expert tier** — 41 extension decisions, new engine modules | 6 | 39.5 |

### Path B — build Foundation engine, grow it tier by tier

| Phase | Weeks | Cumulative |
|---|---|---|
| Foundation spec + model + calibration + port + UI | 13 | 13 → **ship Foundation** |
| Standard: engine refactor 3 + new chains 2 + recalibrate 1.5 + UI 1.5 | 8 | 21 |
| Advanced: engine refactor 4 + new chains 3 + recalibrate 1.5 + UI 2 | 10.5 | 31.5 |
| Instructor console full (harder — parameters differ per tier) | 4 | 35.5 |
| Playtest, hardening | 3 | 38.5 |
| Expert: refactor 3 + new modules 5 + recalibrate 1.5 + UI 2 | 11.5 | 50 |

### Verdict

| | Path A | Path B | Delta |
|---|---|---|---|
| Foundation shipped | Week 23 | **Week 13** | B is 10 weeks earlier |
| Advanced shipped | **Week 27.5** | Week 31.5 | A is 4 weeks earlier |
| Expert shipped | **Week 39.5** | Week 50 | **A is 10.5 weeks earlier** |
| Full calibration cycles | **1** | 4 | A runs the harness once |
| Cohort comparability | **Preserved throughout** | Broken at each tier | — |

Path B's only genuine advantage is reaching a first shippable product ten weeks
sooner. Everything after that it loses, and it loses the calibration evidence
permanently.

---

## The one place incremental is right

**Expert tier is genuinely different work.** Its 41 extension decisions
introduce mechanisms absent from the Advanced engine — FX hedging, BNPL,
subscription/replenishment, fraud detection, a second warehouse city,
third-party marketplace sellers. These cannot be defaulted into existence;
they must be built.

But they are **additive modules, not refactors**, provided one architectural
rule holds:

> The round calculation is a sequence of independent mechanism modules, each
> reading and writing a shared state vector — not a monolithic function.

Under that architecture, adding FX hedging means adding a module between
procurement and finance. It does not mean touching conversion, share allocation
or retention. Recalibration is then local to the affected chain, not global.

**Get this architecture right in Path A phase 4 (the TypeScript port).** It is
the single decision that determines whether Expert costs 6 weeks or 11.5.

---

## Recommended sequence

1. **Build the engine once, at Advanced (56-decision) depth.** Do not build a
   Foundation engine.
2. **Ship Foundation first** (Week 23) as a configuration. Run your first
   cohort on it. Gather calibration evidence.
3. **Unlock Standard, then Advanced** (Weeks 25, 27.5) as UI work only. The same
   engine, the same calibration, the same cohort comparability.
4. **Defer Expert** until Advanced has run with two cohorts. Build it only if
   demand for it is real — executive education, or a returning cohort wanting a
   second, harder run.

The preset ladder you described is exactly right as a **rollout plan**. It just
needs to sit on top of one engine rather than describe four.

---

## Answering the underlying question

> *Will incremental presets mean better quality, better time management and
> better output — or does each preset need building from scratch?*

- **Better quality:** yes, but from incremental *shipping*, not incremental
  *engine building*. Each cohort on a stable engine improves calibration.
  Each engine change destroys it.
- **Better time management:** yes for the UI, content and rollout. No for the
  engine — growing the engine costs ~10 extra weeks and four calibration cycles
  instead of one.
- **Built from scratch each time:** only true if you build a Foundation engine.
  On a full-depth engine, Standard and Advanced are **UI work only** — two and
  two-and-a-half weeks respectively, not rebuilds. Expert is genuine new
  engine work, but additive rather than a rewrite if the module architecture
  holds.

---

## Scope note

This is a larger programme than the original 22-week plan. The growth is
traceable and was driven by requirements added since:

| Addition | Weeks |
|---|---|
| Round 0 founding round + pro-forma preview | +2 |
| Configurability layer — team count, presets, unlock timing, parameter bands | +3 |
| Validation harness and the seven balance invariants | +2 |
| Market research menu (engine + UI) | +1.5 |
| Advanced-depth engine rather than ~40 decisions | +3 |
| **Total** | **+11.5** |

If the timeline is the binding constraint, the two honest de-scopes are:

- **Drop instructor parameter editing** (keep preset and unlock configuration,
  hardcode the economics): saves ~3 weeks, and removes the need for the
  instructor-facing half of the validation harness.
- **Defer Expert indefinitely:** saves 6 weeks and is easy to reverse later.

Together these bring Advanced delivery back to roughly **Week 27** with no
compromise to what students actually experience.
