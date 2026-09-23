# 15 — Course Map: LUMS CES sessions against simulation rounds

**Course:** E-Commerce: Building, Scaling & Managing Digital Businesses
**Shape:** 12 sessions × 2 hours, delivered across 11 days (one day carries two
sessions). Simulation runs from session 2.

This file is the contract between the outline and the engine. It says which
decisions open in which round, which is what the instructor sets on
`/admin/decisions` before each session.

---

## The constraint that sets the schedule

**The simulation needs at least eleven trading months.** Measured over 200
games per length:

| Trading months | Scorecard spread | Harvest penalty | I11 |
|---|---|---|---|
| 10 | 31 | +7.1 | **FAIL** |
| 11 | 35 | +11.8 | PASS |
| 12 | 38 | +16.3 | PASS |

Below eleven, strategies have not had time to separate: the spread falls under
its floor and end-game harvesting stops being properly punished, because there
are too few months left for the damage to land inside the scored window. Ten
in-class rounds is therefore not an option, and the schedule has to find at
least one month beyond "one round per session".

### Where the extra months come from

Sessions 2–12 is eleven teaching slots. Session 2 is the founding round, which
leaves ten. Two slots have to do double duty:

1. **The double-session day carries two months.** Teams submit in class after
   the first session, the instructor runs the month over the break, and the
   second session opens with that debrief. This is the strongest teaching day
   in the course — the same group sees a decision and its consequence inside
   two hours.
2. **One month runs between sessions** where the calendar gives a longer gap.
   Teams submit online; the instructor runs it; the debrief opens the next
   session.

That is twelve trading months. If the calendar slips, dropping the
between-sessions month leaves eleven, which still validates. Dropping two does
not.

**Month 12 must be processed before session 12**, so the final scorecard is in
the room for the presentations. Decisions therefore close after session 11.

---

## The principle the mapping depends on

A team does not own every lever from month one — but every mechanism is live
from month one.

Decisions that have not yet opened run at their `default_when_disabled` value.
The business still markets, ships, takes payment and holds stock; the team just
does not control it yet. So a team in month 3 is already paying the price of a
marketing mix it did not choose, and when marketing opens in session 7 they
arrive with a grievance and a reason to care.

**Feel the consequence, then get the lever.** That is the sequencing rule, and
it is why the course order can differ from the engine order without breaking
anything.

---

## Session-by-session map

| # | Session topic | Sim round | Opens this session | What the team actually does |
|---|---|---|---|---|
| **1** | What is E-Commerce? | — | — | Teams formed, sim demonstrated, handbook issued. No decisions. |
| **2** | Finding the Right Business Idea | **Round 0 — founding** | The whole founding form | Choose brand, two categories of five, segment priority, quality tier, D2C or marketplace, opening range and prices, sourcing per product, tech stack, fulfilment, payments, and the split of PKR 12m four ways. Write the board objective and targets. |
| **3** | How Will You Make Money? | R1 debrief → submit R2 | `1.1` range, prices and sourcing · `1.5` positioning · `12.5` board memo | Re-price the shelf against the first month's actual gross margin. Read the P&L block of the report for the first time. |
| **4** | Building Your Online Store | R2 → R3 | `5.1` website experience · `8.5` packaging · `9.3` payment gateway | Invest in the storefront and the unboxing, and pick the gateway. Conversion rate becomes a number they own. |
| **5** | What to Sell & How to Price It | R3 → R4 | `1.2` bundles · `2.4` free-delivery threshold · per-product discounting in `1.1` | Build three-packs, set the free-delivery bar, discount line by line. The volume-weighted average discount is the lesson. |
| **6** | Where Will You Sell? | R4 → R5 | `4.1` sell on Daraz | Marketplace on or off, and at what commission. Own-site margin against marketplace reach. |
| **7** | How Will You Get Customers? | R5 → R6 | `3.1` Meta · `3.2` Google · `3.4` TikTok · `3.10` campaign setup · `3.6` affiliate & influencer · `3.8` creative · `3.9` brand-building | The budget they have been paying by default for five months is finally theirs. Channel CAC and channel churn differ; the cohort ledger remembers where each customer came from. Brand-building is the contrast: it buys no orders this month, decays if you stop, and carries most of the organic traffic that makes every later performance rupee cheaper. Campaign setup splits each ad budget into up to three campaigns aimed by product, age, gender, city tier, interests, language and format; the monthly report shows CTR, CPC, CVR, ROAS and CAC per campaign and says why each worked or did not. Open `3.10` in the same window as the budgets. |
| **8** | Getting Customers to Come Back | R6 → R7 | `6.1` CRM & retention · `10.1` CS team size · `10.4` returns policy | Retention spend against acquisition spend. A deal-driven cohort churns at more than twice an organic one, and by now they have one. |
| **9** | How Will You Deliver the Order? | R7 → R8 | `7.1` stock · `7.2` supplier · `7.4` QA · `7.5` safety stock · `8.2` 3PL share · `8.3` courier mix · `9.1` COD · `9.2` prepaid discount | The Pakistan session. COD share, RTO, courier success against stated SLA, lead time and the cash tied up in it. |
| **10** | Is Your Business Working? | R8 → R9 | Nothing new — `12.1` research is the session | No new levers. The whole session is the report, the research desk and the twenty studies. Which numbers can be trusted, which are biased, and what the platforms over-report. |
| **11** | How Can AI Help? | R9 → R10 | `11.1` recommendations · `11.2` AI forecasting · `11.3` dynamic pricing · `11.4` AI customer service · `11.5` AI creative | Five AI levers with real costs and real ceilings. AI creative raises the floor and caps the ceiling; AI forecasting narrows the error band rather than shortening lead time. |
| **12** | How Do You Grow? | **R11 and R12 processed** | Decisions closed | Final scorecard, variance against the month-0 targets, presentations. |

**The double-session day** is best placed at sessions 6+7 or 8+9 — the two
pairs where the second topic is the direct consequence of the first. Sessions
6+7 is the stronger pair: choose a channel, then pay to bring people to it.

**The between-sessions month** fits best before session 12, so the final two
months run back to back and the presentations are made against a settled
twelve-month result.

---

## Where the sim differs from the outline, and what to do about it

**Session 3 asks for unit economics before the team has a P&L.** The founding
round's pro-forma preview runs the real engine, so a team leaves session 2 with
a projected month 1 — CAC, contribution margin, AOV, runway. Teach session 3
against their own pro-forma, then contrast it with the actual, which lands
before session 4. The gap between the two *is* the session.

**Session 4 comes before the marketing that fills the store.** Intentional: the
store is empty because traffic is on default. That is the right order — a team
that improves conversion before buying traffic gets more out of every rupee it
later spends, and the ones that do it the other way round find out in month 7.

**Session 10 has no new decisions.** It is the measurement session, and it
carries the sim's hardest idea: the platforms report ROAS over-attributed by
about a third, and the Attribution Study is what shows it. Budget the full two
hours for the research desk.

**The course has five categories and the sim has five categories** — skincare,
haircare, hygiene, homecare, baby — and five customer segments: Value Seekers,
Urban Convenience, Quality Loyalists, Deal Hunters, Premium/Gifting. The
segment weights are the hidden structure of the whole market and are bought
with MR-06.

---

## Assessment

The outline's four components are each 25% and are written against a business
of the student's own choosing. The simulation can carry them, mirror them, or
stay separate from them. Three workable shapes:

| Shape | Assessment 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| **A — sim carries all four** | Round 0 founding + board memo | Rival analysis from the research desk | Monthly report analysis | Final scorecard + presentation |
| **B — sim carries two** | Own business idea (external) | Own business audit (external) | Sim: know your numbers | Sim: final scorecard + plan |
| **C — sim is separate** | All four external | | | Sim graded as participation |

**Shape B is the recommendation.** The outline's first two components ask
students to look at a real business, which the simulation cannot replace and
should not try to. The last two are exactly what the sim measures better than
an essay can: it has the numbers, and it has a scorecard that has been
validated against twenty strategies to make sure no single trick wins.

The sim's own scorecard is Profitability 25 / Growth 20 / Customer value 20 /
Operations 15 / Cash 10 / Decision quality 10. Decision quality is the board
memo, marked by the instructor against the objective the team set in month 0 —
the only pillar the model does not compute.

---

## Setting it up in the portal

Before each session the instructor opens that session's decisions on
`/admin/decisions` for the coming round. Everything not opened runs at its
default, and everything opened stays open for the rest of the game.

The engine's own unlock schedule already approximates this map, but it does not
match it — `3.1` Meta ads is unlocked from round 1 by default, and this course
holds it to session 7. The per-round window overrides are what make the
mapping stick, and they are the instructor's to set.
