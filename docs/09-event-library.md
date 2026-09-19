# 09 — Event Library

24 events across three types. The governing rule from `07-engine-chain.md`:

> **Events modify parameters, never a team's P&L.** The chain propagates the
> consequence.

An event that subtracts PKR 2M from a team's profit teaches nothing. An event
that raises supplier lead time from 14 to 28 days forces a team to reason about
safety stock, cash and forecast error — and the PKR 2M loss emerges from their
response, or does not.

---

## Event taxonomy

| Type | Fires | Fairness basis | Count |
|---|---|---|---|
| **A — Scheduled** | Fixed round, all teams | Identical for everyone | 9 |
| **B — Conditional** | When a team's state meets a trigger | **Earned, not luck** | 9 |
| **C — Stochastic** | Random, bounded severity | Symmetric in expectation, forewarnable | 6 |

### The fairness rule

**Type B is the important innovation.** Most simulations deliver bad news to
individual teams at random, which is unfair and teaches nothing — a team
punished by dice learns only that dice exist.

Here, almost every single-team adversity is **endogenous**: it fires because of
what the team did. The debrief line is *"this did not happen to you, you caused
it"*, which is the most valuable sentence available in a management course.

Type C exists because real markets do contain genuine luck. It is constrained:
**low severity, symmetric in expectation, and forewarnable** by a purchasable
study. No Type C event can determine a team's outcome.

---

## Event schema

```yaml
code:        EV-xx
name:        Human-readable
type:        A | B | C
trigger:     round N  |  condition expression  |  probability p
scope:       all_teams | segment:<name> | single_team
duration:    rounds
modifies:    { parameter: multiplier or delta }
warning:     which study forewarns, and with what probability
severity:    scales with EVENT_SEVERITY
```

Severity scaling:
```
effective_mult = 1 + (mult - 1) × EVENT_SEVERITY
```
`EVENT_SEVERITY` default 1.0, green 0.5–1.6.

---

## Type A — Scheduled events

The backbone of the run. Identical for all teams, so outcome differences are
purely differences in response.

### EV-01 · Ramadan demand surge · Round 3

| | |
|---|---|
| Modifies | `category × 1.22` · `CPM_base × 1.18` · `courier_success × 0.94` · `sla_attainment × 0.88` |
| Duration | 1 round |
| Warning | MR-01 reveals the seasonal index, 3 rounds ahead |
| Counter-play | Pre-build inventory in R2; raise safety stock; book courier capacity |

**The trap:** it looks like pure upside. Teams that chase the demand without
pre-building stock hit the R3 surge at 70% in-stock, convert poorly, and take a
rating hit in R4 that costs them more than the surge gave.

**Teaching point:** peak season is an operations problem disguised as a
marketing opportunity.

---

### EV-02 · Competitor price cut · Round 4

| | |
|---|---|
| Modifies | AI Incumbent A net price `× 0.85`, held 4 rounds |
| Scope | All teams, via the share model |
| Duration | 4 rounds |
| Warning | MR-05 (60%); MR-02 shows it the round it lands |
| Counter-play | Match, hold, or reposition — all three are viable |

**No correct answer, by design.** Matching protects share and destroys margin.
Holding protects margin and cedes Value Seekers and Deal Hunters — 49% of the
category. Repositioning toward Quality Loyalists works but takes 3 rounds and
40% of brand equity.

**Teaching point:** a price war is won by choosing which customers to lose.

---

### EV-03 · Supplier lead-time shock · Round 5

| | |
|---|---|
| Modifies | `lead_time × 2.0` for Suppliers A and B; Supplier C unaffected |
| Duration | 3 rounds |
| Warning | **MR-17 (70%), one round ahead** |
| Counter-play | Switch to Supplier C at +9% cost; raise safety stock; cut assortment breadth |

Supplier C being unaffected is deliberate: the expensive, fast, low-MOQ supplier
that looked irrational in Rounds 1–4 is suddenly the only one working.

**Teaching point:** supplier cost premiums are insurance priced in advance. MR-17
at PKR 200,000 pays for itself several times over here, which is the cleanest
demonstration of research value in the run.

---

### EV-04 · Platform CPM inflation · Round 6

| | |
|---|---|
| Modifies | `φ_meta 0.25 → 0.55` · `φ_tiktok 0.25 → 0.45` · `φ_google 0.25 → 0.35` |
| Duration | 2 rounds |
| Warning | MR-05 (60%); MR-11 shows it as it lands |
| Counter-play | Shift to organic, CRM, marketplace; accept lower ROAS; pre-build brand equity |

Every team bidding into 11.11 simultaneously. The more the field spends, the
worse it gets for everyone — a genuine tragedy of the commons.

**Teaching point:** your CAC is set by your competitors' budgets, not your skill.
Teams that built brand equity and a customer base in Rounds 1–5 barely feel it.

---

### EV-05 · COD return-rate spike · Round 7

| | |
|---|---|
| Modifies | `RTO_base 0.18 → 0.27` |
| Duration | 3 rounds |
| Warning | MR-05 (60%); MR-15 quantifies it |
| Counter-play | Raise prepaid incentive; COD threshold; tighten courier mix; improve delivery promise accuracy |

**The Pakistan-specific event.** No imported simulation has it, and it is where
this sim earns its reason to exist. Post-sale-season COD abandonment is a real
and recurring feature of the market.

**Teaching point:** COD is not a payment method, it is a working-capital and
risk-transfer decision.

---

### EV-06 · Quick Commerce market opens · Round 5 (announced Round 3)

| | |
|---|---|
| Type | **Opportunity** |
| Modifies | Unlocks decision 4.3; opens a second market per `03-core-mechanisms.md` |
| Warning | Announced R3; MR-20 available from R4 to size it |
| Counter-play | Enter one city, enter three, or stay out — all defensible |

**Teaching point:** adjacency decisions are cash-allocation decisions. Entering
all three cities is the most common and most expensive error in the run.

---

### EV-07 · Well-funded new entrant · Round 8

| | |
|---|---|
| Modifies | Adds Incumbent C: aggressive price, heavy spend, weak service, poor delivery |
| Duration | Permanent from R8 |
| Warning | MR-05 (60%), one round ahead |
| Counter-play | Compete on service and delivery, not price; accelerate retention; defend Quality Loyalists |

The entrant is deliberately **strong on acquisition and weak on operations**. It
takes share fast in R8–R9, then its rating decays and it bleeds customers back
into the market from R10.

**Teaching point:** funded competitors buy share, not customers. Teams that
panic and match on price lose twice.

---

### EV-08 · Marketplace mega-campaign slots · Round 9

| | |
|---|---|
| Type | **Opportunity — contested** |
| Mechanism | Sealed-bid auction, 3 slots. Winners get `mp_rank_score × 1.9`, 2 rounds |
| Warning | Announced R8 with slot count and reserve price |
| Counter-play | Bid, or spend the cash elsewhere |

The only **direct team-vs-team interaction** in the sim. Bids are cash, paid
whether or not the slot converts.

**Teaching point:** the winner's curse. Expect at least one team to overbid
badly, and build the debrief around it.

---

### EV-09 · FX devaluation · Round 10

| | |
|---|---|
| Modifies | Import-sourced COGS `× 1.16`; local unaffected |
| Duration | Permanent from R10 |
| Warning | MR-05 (60%); MR-17 flags supplier exposure |
| Counter-play | Switch sourcing (costs one lead time); raise prices; absorb into margin |

**Teaching point:** sourcing decisions made in Round 0 carry currency risk that
surfaces nine rounds later. Nobody models this at founding; everyone should.

---

## Type B — Conditional events

These fire from a team's own state. They are consequences, not misfortune.

### EV-10 · Review crisis

| | |
|---|---|
| Trigger | `rating < 3.6` for 2 consecutive rounds |
| Modifies | `sessions_organic × 0.75` · `CR_base × 0.88` · `mp_rank_score × 0.70` |
| Duration | Until `rating ≥ 3.9` for 2 rounds |
| Exit | Recovery takes 3–4 rounds minimum, given rating moves 30%/round |

**Teaching point:** reputation is slow in both directions. The cost of a service
failure is paid long after the failure is fixed.

---

### EV-11 · Stock-out ranking penalty

| | |
|---|---|
| Trigger | `instock_ratio < 0.75` in any round |
| Modifies | `mp_rank_score × 0.65` for 2 rounds |
| Note | Marketplaces demote unreliable sellers. Fixing stock does not restore rank immediately |

---

### EV-12 · Customer service collapse

| | |
|---|---|
| Trigger | `backlog > 1.5 × capacity` |
| Modifies | `CSAT_target − 18` · `return_rate × 1.25` · `churn × 1.30` |
| Duration | Until backlog clears |

Backlog compounds into next round's ticket volume (M13). Two rounds of neglect
is considerably worse than twice one round.

---

### EV-13 · Supplier terms withdrawn

| | |
|---|---|
| Trigger | `credit_line_drawn > 0.80 × ceiling` |
| Modifies | All suppliers → advance payment only; MOQ `× 1.4` |
| Duration | Until drawn < 50% for 2 rounds |

**The death-spiral accelerator, deliberately included.** A team in cash trouble
finds its terms withdrawn exactly when it can least afford it. This is precisely
how it works in reality, and the P5 runway band exists to make teams avoid
getting here.

---

### EV-14 · Supplier deprioritisation

| | |
|---|---|
| Trigger | Order volume falls > 50% vs 2-round average, twice |
| Modifies | `lead_time × 1.5` · `MOQ × 1.3` · unit cost `× 1.06` |
| Duration | 3 rounds after volume recovers |

**Teaching point:** supplier relationships are built on consistency. Teams that
whipsaw procurement to manage cash pay for it in the next cycle.

---

### EV-15 · Marketplace suspension

| | |
|---|---|
| Trigger | Marketplace return rate > 20% OR marketplace rating < 3.4 |
| Modifies | Marketplace channel disabled for 1 round; `mp_rank_score × 0.5` on return |
| Duration | 1 round suspension + 2 rounds recovery |

---

### EV-16 · Capability erosion

| | |
|---|---|
| Trigger | Payroll cut below 70% of the prior 3-round average |
| Modifies | `ux_score × 0.92` · `CQ × 0.85` · forecast error `× 1.3` per round sustained |
| Duration | While sustained, + 2 rounds |

**Teaching point:** cutting people is the fastest way to improve this quarter's
margin and the slowest thing to reverse.

---

### EV-17 · Viral moment

| | |
|---|---|
| Type | **Opportunity — earned** |
| Trigger | `CQ > 0.70` AND TikTok spend > PKR 400k, from R6 |
| Selection | One team, weighted by `CQ² × tiktok_spend`, plus a small random term |
| Modifies | `sessions × 2.4` for 1 round · `BE + 0.08` permanently |
| Frequency | At most twice per run |

Deliberately **earned, not random.** The team that invested in creative quality
for six rounds with nothing visible to show for it finally gets paid — publicly,
in front of the cohort.

**Teaching point:** you cannot buy virality, but you can buy the conditions for
it. This single event justifies decision 3.8 for the whole class.

---

### EV-18 · Loyalty flywheel

| | |
|---|---|
| Type | **Opportunity — earned** |
| Trigger | Repeat order share > 35% AND NPS > 45, 2 consecutive rounds |
| Modifies | `sessions_organic × 1.30` · `churn × 0.85` · `CAC_blended × 0.88` |
| Duration | While sustained |

The retention counterpart to EV-17. Sustained customer quality compounds into
cheaper acquisition — which is the actual mechanism behind every durable
consumer business, and is invisible unless modelled explicitly.

---

## Type C — Stochastic events

Genuine luck, deliberately bounded. **No Type C event can decide an outcome.**

| Code | Event | Probability | Modifies | Duration | Warning |
|---|---|---|---|---|---|
| EV-19 | Regional courier disruption | 0.15/round from R3 | One random courier `success × 0.88` | 1 round | MR-15 (50%) |
| EV-20 | Payment gateway outage | 0.10/round | One random gateway `success × 0.82` | 1 round | None |
| EV-21 | Supplier quality lot variance | 0.12/round | One random supplier `quality × 0.90` | 1 round | MR-16 detects after |
| EV-22 | Ad platform policy change | 0.10/round from R4 | One random channel `k_base × 0.85` | 2 rounds | MR-05 (40%) |
| EV-23 | Category demand noise | Every round | `category × N(1.0, 0.035)` | 1 round | Irreducible |
| EV-24 | Competitor stock-out | 0.12/round | One incumbent `instock × 0.70` | 1 round | MR-19 only |

EV-23 is the honest one: **irreducible noise, every round, unforecastable.** It
exists so teams cannot attribute every variance to a decision. Learning which
variances are signal and which are noise is a core analytical skill, and a sim
without noise teaches false precision.

---

## Dynamic event generation (AI layer)

Your original brief called for AI-driven events so teams cannot follow a fixed
playbook. The safe implementation is narrower than it first appears.

**The LLM must not invent effects.** An LLM inventing arbitrary parameter
changes will break the economic model, defeat the validation harness, and make
runs non-comparable.

**What the LLM should do:**

1. **Select** from the library, given the cohort's current state — for example
   choosing EV-02 over EV-04 in a round where the field is under-spending on
   marketing but over-discounting.
2. **Parameterise within published bands** — set EV-02's price cut anywhere in
   0.80–0.92 rather than fixed at 0.85.
3. **Generate the narrative** — the news headline, the supplier's email, the
   trade-press article. This is where an LLM adds genuine value: twenty
   differently-worded, differently-framed presentations of the same underlying
   parameter change.
4. **Time it** — advance or delay a scheduled event by up to 2 rounds based on
   how the cohort is performing.

**What the LLM must never do:** create new parameter targets, exceed published
severity bands, or apply effects to a single team outside the Type B trigger
conditions.

Under this design, no run is identical, every run is balanced, and the
validation harness stays meaningful.

---

## Instructor controls

| Control | Effect |
|---|---|
| Enable / disable per event | Any event can be removed entirely |
| Reschedule | Move any Type A event to any round |
| Severity | Per-event override of `EVENT_SEVERITY` |
| Manual injection | Fire any event immediately, any scope |
| Type B thresholds | Editable, within bands |
| Type C probabilities | Editable, 0 to 0.30 |

**Recommended first-cohort configuration:** Type A only, severity 0.7, Type C
disabled except EV-23. Add Type B from the second cohort once you have seen how
teams behave without conditional pressure, and how often the triggers would
have fired. The instructor console should log **near-misses** — teams that came
within 10% of a Type B trigger — so you can calibrate the thresholds before
switching them on.

---

## Coverage check

The original brief listed six example events. All are present and specified:

| Brief | Implemented as |
|---|---|
| Month 3: competitor cuts price 15% | EV-02, Round 4, −15% |
| Month 4: TikTok campaign goes viral | EV-17, earned rather than random |
| Month 5: lead time 7 → 21 days | EV-03, doubled from 14 |
| Month 6: COD return rate increases | EV-05, 18% → 27% |
| Month 7: new competitor enters | EV-07, Round 8 |
| Month 8: AI recommendation available | Decision 11.1, available from R3 |

Eighteen further events are added, of which **four are opportunities**
(EV-06, EV-08, EV-17, EV-18) and nine are consequences of the team's own
conduct rather than external misfortune.
