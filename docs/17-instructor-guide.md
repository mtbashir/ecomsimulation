# 17 — Instructor Guide

How to run a live cohort on the web app, month by month, and what each admin
control does. The rules themselves are in `01` (decisions), `03` and `07`
(mechanics) and `08` (scoring); `04` lists every per-game switch.

The app is deployed on Render from this repository's default branch
(`docs/14-deployment.md`). **Every push redeploys it within a few minutes.**
Months already run are stored as saved worlds and are never re-simulated by a
deploy, but reports, consoles and scores are drawn from them by the code that
is deployed - so a change to scoring or to a report changes how past months
read. The admin footer shows the engine version, the build and the rules in
force.

---

## A month, step by step

1. **Open the month** (Overview → *Open a round for submissions*). Teams can
   now submit; a team that submits nothing keeps its previous decisions.
2. **Teams decide.** Every change on the form is saved as it is made
   (autosave), and Submit saves the whole form. They can revise until the month
   is run. A change the month cannot pay for - spending beyond cash plus the
   approved loan - is kept as a draft and refused with the reason; the
   *Submissions* table shows **changes not submitted** for that team, and the
   last version that fitted stands.
3. **Preview** (beside Run). Runs the month on an in-memory copy and shows its
   console under a banner: nothing is saved. Use it to:
   - read each team's debrief, revenue, stock and cash before anyone else sees
     them - a team with sales collapsing for want of stock is the one to check
     for an unapproved loan (its report names the cut once the month runs);
   - judge each board memo (*memo verdict*): the verdict is saved on the live
     game and counts when the month runs.
4. **Run** the month. Nothing is processed until you do.
5. **Read the console** (*Read the round*): the leaderboard (cumulative from
   month 1, each month on its own beside it), results by round, one debrief card
   per team, technology builds, campaigns, market size by product and segment,
   and the results workbooks.
6. **Decide what teams see** for the month (*What teams see in their monthly
   report*), then open the next month.

---

## What teams see in their monthly report

A grid of months against six rows. A month's column decides that month's
report, the decision form after it and the campaigns page; changing a month
already run changes its report.

| Row | Default | Notes |
|---|---|---|
| Sales by product this month | ticked | Units, net sales, gross margin and contribution per product |
| Who bought each product | ticked | Buyers by customer segment |
| Stock by product, end of month | ticked | Also hides stock and sales beside each product on the next form |
| Paid media, campaign by campaign | ticked | The campaigns page too |
| Rankings, cumulative and by month | ticked from month 4 | Publishing a month publishes every month up to it |
| Excel workbook to download | unticked | Ticking a month gives teams that month's workbook, hidden sections left out |

Your own copy of any report shows the hidden sections, labelled.

---

## Rolling back

*Roll back* returns the game to the end of any month already run. Results after
it are discarded; **every submission and draft is kept**, so nobody re-enters
anything, and submissions are left **closed**.

- *Run* straight away to re-run the month on the decisions as saved, or *open*
  it first so teams can change them (for example, approve a loan they missed).
- Decisions already entered for later months stay in place for when those
  months open.
- A re-run uses the code deployed now, not the code the month first ran on, so
  it will not reproduce the original exactly if the engine has changed since.
  Per-game rules follow the month (a rule switched on from month 7 does not
  apply to a re-run month 6).
- The same decisions repeat the same problems: a month whose stock order was
  cut for want of a loan is cut again unless the team changes it.

---

## Rule cards on the Overview

A game already trading when a rule arrived shows a card for it until the rule
is in force: **Working capital loans**, **Full costs**, **Working affiliates**,
**Returns to the supplier** and **Price model** (like-for-like pricing). Pick a
month not yet run; the months before it stay exactly as played. Tell the teams
before they submit that month - for loans especially, because an unapproved
month has its stock order cut. A new game starts on all of them from month 1
and shows none.

The Overview also lists **stock outside each team's range** (products a team
does not sell, from a going-concern opening order) with one button to send it
all back for a full refund the next month; it can be cancelled until then.

---

## Other pages

| Page | Use it for |
|---|---|
| Teams | Team names and passwords. Generated passwords are shown once; set new ones here |
| Strategy | Every team's founding choices and each month's decisions side by side, with changes on last month - the quickest way to see who is doing what |
| Scoring playbook | The pillars, the levers that move each measure and the trade-offs, for coaching |
| Configure → Decisions | Decision windows: open a lever early or hold it back, month by month (`15-course-map.md` has the recommended sequence) |
| Configure → Economics | Parameter overrides within their bands; anything outside default marks the configuration unvalidated |
| What students read | The handbook, marketing guide and *How You Are Scored*, as teams see them |
| Games | Start a new game (the running one is archived, complete, under Past games) |

---

## The Fall-2026 game

| | |
|---|---|
| Start | Founded teams on the going-concern opening (`launch_order = 0`), PKR 12M capital |
| Preset | Advanced, six teams, two AI competitors |
| Rules v2 | From month 3; months 1-2 as published on v1 |
| Marketplace (4.1) | Opens month 5 |
| Working capital loans | From month 5 |
| Range changes (1.3) | Not offered (the game began before them) |
| Dynamic pricing (11.3) | Withdrawn 2026-10-22; the five teams that bought it refunded |

---

## If something goes wrong

| Problem | What to do |
|---|---|
| A month ran on a mistake | Roll back to the month before, fix it (a parameter, or open the month for teams), run again |
| A team says its change did not save | The Submissions table shows *changes not submitted* when a draft was refused; the form tells the team why (usually spending beyond cash plus the loan) |
| The app is down mid-class | `/healthz` says whether the database answers. Download the decisions CSV from the console and run `py run.py round --decisions <file>` offline |
| Signed out after a deploy | `ECOMSIM_SECRET` is not set (`14-deployment.md`) |

---

## Questions from the course

Asked by the instructor while running the Fall-2026 cohort; the index of every
question is `18-questions.md`.

### Can teams change their decisions after submitting? *(2026-10-22)*

Yes, as often as they like until the month is closed or run. Every change saves
as it is made, and the last save that fitted the month's cash is what runs.

### A team says it changed a decision but the change is not showing. *(2026-10-22)*

The change did not fit the month's cash, so it was kept as a draft: the form
reopens with it and says why, and the Submissions table shows *changes not
submitted*. The last version that fitted stands until the team approves a
bigger loan or cuts spending. Before 2026-10-22 such saves were refused without
being kept, which is how a team's change could vanish.

### If I roll back a month, do teams have to enter their decisions again? *(2026-10-22)*

No. A rollback keeps every submission and draft and closes submissions; see
*Rolling back* above.

### Can I give teams cash before a month so their stock is better for that month? *(2026-10-22)*

Not with cash. Stock lands the month after it is ordered at the earliest, so a
month sells only what was on the shelf at its start plus what was ordered the
month before. The only way to change a month's stock is to re-run the month
before it: roll back, open it, let the teams fix their orders and loans, run it.
The dynamic-pricing refund, for example, was paid at the end of the re-run month
6, so it was in teams' cash going into month 7.

### Why does the form show a study commissioned that the team cancelled? *(2026-10-25)*

A draft kept its own copy of the study after the team cancelled it on the
research desk, and put it back into every later save. Fixed on 2026-10-25
(`CHANGELOG.md`): the form now takes research and campaigns as their own pages
saved them. A team still showing the old warning presses Submit once.

### Why does a team come out at the bottom of the preview again? *(2026-10-22)*

Start from its debrief card and its last report:

1. **Stock.** A collapse in sales with *stock-out* as the constraint usually
   means last month's order was cut for want of an approved loan (the report
   names the cut), or the team is returning the stock it would have sold (7.6).
2. **Cash.** A month that did not fit was cut at the start of the month: stock
   first, then marketing.
3. **Technology.** Builds paid for and failed show in *Technology projects*.
4. **Draft.** *Changes not submitted* means the month will run on an older save.
