# 12 — Solo Delivery Plan

**Resourcing reality:** one person (the course owner) plus Claude, working in
bursts rather than steady weekly hours.

This supersedes the 33.5-week programme in `06-build-sequencing.md`, which
assumed a modeller and one to two developers. That plan is not achievable solo
and is retained only for the day a team exists.

---

## What changes, and what does not

| | Team plan | Solo plan |
|---|---|---|
| Engine depth | Advanced, 56 decisions | **Unchanged** |
| Events, research menu, perception gap, cohort ledger | Full | **Unchanged** |
| Presets (Foundation → Advanced) | Config layer | **Unchanged** |
| Instructor parameter editing | Console UI | CLI + CSV (**already built**) |
| Team interface | Web app | Form → CSV → HTML report |
| Instructor console | Web app | CLI |
| Round processing | One click, self-serve | Manual, ~20 min per round |
| Expert tier (92 decisions) | Week 39 | **Dropped** |
| Concurrent sections | Unlimited | One |
| Elapsed to first cohort | ~23 weeks steady | **6–9 focused days, spread** |

**The simulation is the same. The delivery is simpler.** That trade is heavily
in your favour given the constraint.

---

## Why not the Google Sheets architecture

The multi-workbook Sheets design discussed earlier assumed the **engine lived in
Sheets**. It no longer does — it is Python, in this repo, with a parameter
registry and a test suite.

That changes the calculus. The recommended delivery is now:

```
Google Form  →  decisions.csv  →  python run.py  →  report_<team>.html
```

| vs the Sheets design | |
|---|---|
| No IMPORTRANGE fragility | Nothing breaks at 11pm before a round |
| Students cannot break the engine | They never touch it; they fill a form |
| Engine stays portable | The day a developer arrives, the port is P4, unchanged |
| Version controlled and tested | Sheets is neither |
| Cost | Manual round processing, ~20 min |

---

## The burst plan

Each burst ends at a **stable, usable state**, because the next one may be weeks
away. No burst leaves the repo half-finished.

| # | Burst | Effort | Ends when |
|---|---|---|---|
| **1** | Complete the engine — the 13 remaining modules | ~1 day | A 12-round game runs end to end without crashing |
| **2** | **Calibrate to T2** | ~1 day | Baseline holds within 2% for 12 rounds at N = 2…16 |
| **3** | Validation harness and balance | ~1–2 days | 20 archetypes, 12 invariants, all green |
| **4** | Round 0 founding + decision I/O | ~1 day | Teams can submit a form and receive a result |
| **5** | Delivery surface | ~1–2 days | HTML report per team, instructor round-runner |
| **6** | Course materials | ~1 day | Handbook, decision forms, debrief pack, rubric |
| — | **Run a cohort** | A term | The only test that matters |

**6–9 focused days.** At roughly monthly bursts, a **Spring 2027 cohort** is
realistic. At quarterly bursts, autumn 2027.

### Burst 2 is the gate

Calibration is where your domain judgement is irreplaceable and cannot be
delegated to Claude. *Is 18% RTO right for this category? Is PKR 850 blended CAC
plausible? Does 22% repeat order share match what you see at SnappRetail?*

Claude can build the engine. Claude cannot know whether it is true.

If burst 2 will not converge, **stop and fix the model.** Do not proceed to
burst 3 on a foundation that does not hold.

### Burst 3 is where it becomes a simulation

Until the invariants pass, this is a spreadsheet that produces numbers. After
they pass, it is a simulation that teaches. Invariant I7 in particular — research
must beat both buying nothing and buying everything — is the one that determines
whether the Markstrat mechanism works at all.

Budget two days for burst 3, not one. Something will fail and the failure
diagnosis table in `11-validation-harness.md` exists for that moment.

---

## Working with Claude across sessions

**Claude has no memory between conversations.** Every session starts cold. The
repository is the entire handover, which is why the specification documents came
before any code.

### Opening a session

> Read the repo at `mtbashir/ecomsimulation`, branch
> `claude/beautiful-hypatia-d7shuu`. Check `README.md` for current status. We
> are on burst N.

Claude will read the specs, the parameter registry and the tests, and be
current within one turn.

### Closing a session

Never end mid-module. Before finishing, Claude must:

1. Run `pytest -q` and report the result honestly
2. Commit and push
3. Update the **Current status** block in `README.md` — what landed, what is
   next, anything known-broken
4. Record any calibration judgement you made, and the reasoning, in
   `docs/13-calibration-log.md`

Point 4 matters more than it looks. When you decide RTO should be 22% rather
than 18%, that judgement is yours and unrecoverable — Claude cannot re-derive
it, and in four months neither will you.

---

## What is explicitly out of scope

| Dropped | Why | Reversible? |
|---|---|---|
| Web application | Needs a developer to own deploy, auth, hosting and live-class triage | Yes — engine ports cleanly, it is P4 in `06` |
| Expert tier, 92 decisions | Genuine new engine work | Yes, additively |
| Instructor console UI | CLI and CSV do the same job for one instructor | Yes |
| Concurrent sections | Manual round processing does not scale past one | Only with the platform |
| Empirical benchmarking | Reasoned figures are sufficient to start | Yes — swap `params/*.csv`, re-run burst 3 |

Nothing dropped is load-bearing for teaching the course. Every item becomes
available the day a developer or an RA does.

---

## The honest risk

**The main risk is not technical. It is that bursts stop happening.**

A project needing thirty weeks of steady attention from a COO with a day job
dies quietly around week six. One needing six well-defined days can survive
months of silence, because each burst ends somewhere stable and the repo holds
the context.

That is the reason for the burst structure, and the reason every session must
end with the status block updated. Design for interruption; it is the actual
operating condition.
