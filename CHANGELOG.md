# Changelog

Every change to the simulation since the specification and the web app were
first published, newest first, with the commit that made it. Rules that change
how a month is played are switched **per game**: a new game starts on all of
them, and a game already trading when a rule arrived (the Fall-2026 cohort)
keeps the old behaviour until the instructor switches it on from a month not
yet run. *Applies to* says which. `docs/04-configurability.md` lists the
switches; `docs/01-decision-list.md` is the decision list as built.

---

## Engine 2.3.0 — 2026-10-25

### Documentation brought up to date with the engine

- `README.md` rewritten for the system as it now stands; this changelog added.
- `docs/01-decision-list.md`: the decision list **as built** - all 38 decisions
  with input, opening month, presets, default, what each does and where it is
  offered - generated from the engine's registry by `tools/doc_tables.py`, with
  notes on the levers that need more than a line and a map of what became of
  each field in the original 56-field design.
- `docs/08-scoring.md`: the published scorecard and the runway band generated
  from `scoring.SCORECARD` (several anchors in the old tables had drifted from
  what the engine scores); decision quality as built; administration rules;
  shared ranks.
- `tests/test_docs.py` fails whenever the generated tables and the engine
  disagree, and checks this file names the engine version.
- `docs/03` mechanisms 5-7 (working capital, the cost of stock, channels);
  `docs/07` *As built* notes under every module that changed; `docs/04`
  per-game rules and instructor controls; `docs/10` scored points corrected and
  the new metrics; `docs/11` the thirteenth invariant; `docs/00`, `05`, `14`,
  `15` and `QUICKSTART.md` updated; `docs/17-instructor-guide.md` added.
- Decision help corrected on the form: 1.1 no longer says range changes are
  not modelled; 3.6 says partners bring visitors.

The engine version moves to 2.3.0 for the engine changes since 2.2.0 below.

### 2026-10-25 — questions from the course in the docs

- `docs/00-game-world.md` explains, step by step, how the market's orders are
  created each month (market size, segments, attractiveness, repeat demand,
  traffic and stock), with the Fall-2026 figures; the season index now lists all
  twelve months. `docs/07` M1 and M7 gain the calibration scale and the AI
  competitors.
- Each relevant doc ends with *Questions from the course*: the instructor's
  questions and their answers. `docs/18-questions.md` indexes them.
- `docs/00-game-world.md`: the market is one pool of orders, split only by
  customer segment - not by product or product category - and a worked example,
  from an engine run, of how an order reaches a team and is filled with its
  products (`tools/order_example.py`, checked by `tests/test_docs.py`).

### 2026-10-25 — research and campaigns no longer go stale in a draft

- A draft the cash had refused kept its own copy of the team's market research
  (12.1) and campaigns (3.10), which are saved on the research desk and the
  campaigns page. A study cancelled on the desk therefore still showed as
  *1 study commissioned* on the form and was put back into every later save, so
  a month the study alone had pushed past the cash could never be submitted
  (MUSE, month 8). The form now takes research and campaigns as last saved by
  their own pages; when either page saves, a pending draft is checked again and
  submitted if it now fits. Saving the form also keeps *broad* campaigns, which
  it used to drop. *Applies to:* all games.

### 2026-10-22 — technology builds, dynamic pricing withdrawn, autosave

- **Failed builds are visible.** A build that did not work left no trace, so a
  team could pay for it twice. The team report has a *Technology projects*
  section (started, paid, building / live / failed), each AI decision on the
  form says what the team owns and what Yes would cost, and the console lists
  every team's builds and money lost on failures. `77537e8`, `5c0f15d`.
  *Applies to:* all games.
- **Dynamic pricing (11.3) withdrawn and refunded.** Nothing in the engine ever
  read it, so it cost PKR 3.8M plus PKR 300k a month for no effect. It is in no
  preset, never on the form, never built or charged; what each team paid -
  every build and the running cost of each month it was live - is refunded
  once, in cash, in the month after the withdrawal (Cash sheet line *Refund for
  a withdrawn technology lever*). `77537e8`. *Applies to:* all games.
- **Autosave.** Every change on the decision form is saved as it is made, through
  the same path and cash check as the Submit button; the line beside Submit
  says *Saved*, or why not. A change the month cannot pay for is kept as a
  draft, the form reopens with it and the admin page shows *changes not
  submitted*. `77537e8`. *Applies to:* all games.
- **A blank stock order buys what the month can pay for.** With *Stock to
  purchase* blank the engine orders to the cover target; the loan box and cash
  check now price that order exactly as M3 will place it (units and cost), it
  is elastic - it buys as far as cash and the approved loan go - and it never
  blocks a save. The form says how many units will be bought, or that the order
  falls below the supplier's minimum. `dab7aad`, `bf3a766`. *Applies to:* all
  games.

### 2026-10-20 — market size on the console

- A grid of every store's orders by product and customer segment (orders asked
  for: served plus lost to stock-outs), with the change on last month and each
  segment's share of a product; the same in sales value. Instructor only.
  `b0cf8a1`, `946a0d8`.

### 2026-10-18 — the cash limit, returns to the supplier, PKR 13M

- **Spending never runs past the cash.** Stock is bought on 45-day terms, so an
  order moved no cash when placed and a team could commit more than twice the
  credit limit. The form shows the month's cash balance and refuses a month
  whose stock, budgets, research and AI builds exceed cash plus the loan applied
  for; the engine caps the order and budgets as a backstop. `be21ec7`.
  *Applies to:* all games.
- **Return stock to the supplier (7.6).** Units product by product; the supplier
  keeps 50% of landed cost and refunds the rest in cash that month. Shown on the
  form beside each product's stock and cover, in the console and the handbook
  (beside the holding cost and ageing write-down). `68e9efc`, `bb39c2b`.
  *Applies to:* new games from month 1; a running game from the month the
  instructor picks.
- **Starting capital PKR 13M** for new games, so the default opening month fits
  without borrowing; a game already trading keeps PKR 12M. `199e1a8`.
- **Memo verdicts in the preview**: judge each board memo before the month runs.
  `44c493b`.
- Strategy page: changes on last month, stock rows, pinned team header.
  `585c3b9`.

### 2026-10-17 — full costs, working affiliates

- **Full costs.** Packaging (PKR 25 branded, PKR 70 premium a shipped order), the
  3PL (PKR 30 an order) and quality positioning (claiming a tier other than the
  one sourced costs or saves the difference) now cost what the decisions said.
  `50eda55`. *Applies to:* new games from month 1; a running game from the
  month the instructor picks.
- **Working affiliates (3.6).** Commission used to be charged on all revenue and
  bring nothing. Partners now bring visitors, more the higher the rate with
  diminishing returns; 30% would have come anyway; their customers churn about
  20% a month; commission is paid only on sales they track. `d3683da`.
  *Applies to:* as full costs.

### 2026-10-16 — working capital loans, the handbook by decision

- **Working capital loans as a decision (12.6, 12.7).** The credit line used to
  draw itself and was never repaid. The team now approves a loan each month
  against the need the form shows; short of money, the stock order is cut first,
  then marketing; bills owed are paid regardless (unplanned borrowing); cash
  above a month of fixed costs repays automatically and 12.7 repays more.
  `1fd5e1d`. *Applies to:* new games from month 1; the Fall-2026 game from
  month 5.
- **Handbook by decision.** Each decision card says how it moves the score and
  carries its live table; *How You Are Scored* lists the levers under every
  measure; a scoring playbook for the instructor; console cards show points by
  pillar against the best in the room. `b1c3f91`, `b50df0e`, `79eda12`,
  `8fab0f8`, `dc21330`, `4853074`, `3020e4b`.

### 2026-10-15 — like-for-like pricing, preview, strategy grid

- **Like-for-like pricing.** The price index compared rupees across different
  products, so premium homecare looked cheap beside serum. It now compares each
  shelf with the same products at catalogue price; conversion has no floor under
  its price response; past a segment's willingness to pay it pulls away. Category
  focus is read off the opening range. `e5c559b`, `bed9709`. *Applies to:* new
  games; a running game from the month the instructor picks (Price model card).
- **Preview** the next month on an in-memory copy without saving anything.
  `ad6c52a`.
- **Strategy grid**: every team's founding choices and month decisions side by
  side; Title Case across the app. `f698f5c`, `720570a`.
- The Excel workbook can be opened to teams month by month from the report grid.
  `435683f`.

### 2026-10-14 — report detail, every month's report, rankings

- The instructor ticks, per month, which report sections teams see (sales by
  product, who bought each product, stock by product, paid media by campaign),
  when rankings are published (from month 4 by default) and when the workbook
  is open. `d53d96b`.
- Every report links every earlier month's report.
- Rankings for teams once published: cumulative and each month on its own
  (`scoring.month_score`), with movement. `d53d96b`.
- Console: the cumulative leaderboard from month 1, *Results by round*, every
  round's console a click away; equal scores share a rank. `9e7a718`.

## Engine 2.2.0 — 2026-10-13 — the marketplace

- **Marketplace (4.1) built as designed** (`ecomsim/marketplace.py`): a pool of
  marketplace shoppers shared by rank (half price, half rating) with the other
  listed teams and the marketplace's own sellers; 10% of own-site orders move
  across; commission on marketplace orders only; payout after 15 days; a
  marketplace cohort that churns faster and is out of reach of CRM. It used to
  charge commission and bring nobody. Opens in month 5. `710dc6d`.
- **Decision windows reach the engine**: a lever the instructor closed runs on
  its default even if a team saved it earlier. `710dc6d`.
- Duplicate `mp_payout_days` parameter row removed. `040eee4`.

### 2026-10-11

- **Purchase orders costed like cost of goods** (`cogs_scale`): every unit bought
  had cost about 5.4% more in cash than the P&L charged. `e6ec3e0`.
  *Applies to:* new games.
- New Consulytics.ai logo, light and dark. `d97e169`.

## Engine 2.1.0 — 2026-10-10 — launch order, range changes, returns

- **Founded teams open with their own launch order** - a month of baseline
  demand for their own range at their own landed cost - instead of the
  going-concern pipeline, which delivered other products and debts for sales
  never made. *New game* also resets the rules to v2 from month 1. `9dff43b`.
  *Applies to:* new games.
- **Range changes (1.3)**: add or drop products from month 3; an added product
  is ordered at once; a dropped one's stock goes back less a 20% fee. `85a02fc`.
  *Applies to:* new games.
- **Off-range stock returned**: the admin page lists each team's stock of
  products outside its range and one button sends it back for a full refund the
  next month. `d5ea60c`.
- Stock and cash detail rebuilt for months recorded before the engine kept it;
  the Cash sheet opens with the set-up cash walk. `5d83b78`.

## Engine 2.0.0 — 2026-10-09 — rules v2

- **Rules v2** (the Fall-2026 game from month 3, new games from month 1):
  profitability marked against the best team in the room; decision quality from
  decisions taken (8) and a board memo the instructor has not rejected (2); a
  lever left alone keeps last month's setting. Months played before stay as
  published. The admin footer and console show the engine, build and rules.
  `925ab91`.
- Teams see decision quality described, not its arithmetic. `940b9e7`.
- **Stock by product** in the report; stock to purchase (7.1) as a total or
  product by product. `1502b0e`.

### 2026-10-03 to 2026-10-08

- **Website investment (5.1) improves the store**: it was charged and changed
  nothing; now each month's spend closes part of the gap to the tech stack's UX
  ceiling, landing the month after. `5f18f23`.
- **Bundles**: the pack price decides uptake and margin; the saving is what
  sells a pack, a pack dearer than three singles does nothing. `6313272`,
  `014aedd`, `4485ec1`.
- **Free-delivery threshold** is a trade-off: free on everything lifts
  conversion and shrinks baskets; a bar far above a typical basket loses small
  buyers; added items carry their cost. `df7bf32`.
- **Sales by product**: each team's product mix follows its customers, prices,
  campaigns, packs and stock, with gross margin and contribution per line that
  add up to the P&L; who bought each product. `da4807e`.
- **Funnel and stock** on the report and dashboard; paid media shares orders by
  channel intent; the marketing guide explains spend to sessions to orders.
  `d54f986`, `921992d`, `7ac5200`.
- **Results workbook**: every month as Excel with the KPIs as formulas;
  instructor only until opened to teams. `c992196`, `2b41f84`.
- **Console debrief**: one card per team with results and ranks, a strategy
  summary, what worked and what to raise, and campaigns; one published
  scorecard (`scoring.SCORECARD`) that the engine, briefing and handbook all
  read, and a *How You Are Scored* page. `530ace3`, `cc9236a`, `b34a7a9`,
  `eaf4616`.

## Course materials

Lecture deck generators and their engine test runs, following
`docs/16-lecture-decks.md`: Session 3 `496044f`; Session 4 `742c517`,
`0091d6a`, `cda48b8`, `7be732e`; Session 5 `afdf439`; Session 6 `040eee4`;
Sessions 7 and 8 `600ca02`; Session 9 `b8f191c`. Deck rules `806d2d9`,
`558f597`. Student KPI definitions PDF generator `8a15483`.

## Before 28 September 2026

The web app (team portal and instructor console) and its deployment
(`230fc33`, `45b10a1`, `05c4052`); research charged and delivered, the research
desk and commissioning studies (`88733a6`, `919a518`, `a1b6d8d`); invariants I7
and I11 closed (`7f2b534`); the LUMS course map (`58cb67d`); the campaign screen
(`ff77e27`); past games kept when a new cohort starts (`f749f9b`). The
calibration decisions behind them are in `docs/13-calibration-log.md`.
