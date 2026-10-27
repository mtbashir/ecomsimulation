"""Session 10 - How Do You Know If Your Business Is Working? About 30 slides.

Run: python s10_slides.py <deck folder> [logo url]
Part 2's numbers come from tools/deck/s10_tests.py. Slide ids carry an "s10-"
prefix so the deck can sit beside Session 9's (tools/deck/s9_s10_slides.py).
"""
import pathlib, sys, json
HERE = pathlib.Path(__file__).parent
exec((HERE / "s7_slides.py").read_text().split("\nS = {}\n")[0])
FT = "Session 10 &middot; How Do You Know If Your Business Is Working?"
def sec(sid, bg, eyebrow, title, body, notes, footer=FT, **kw):
    return section(sid, bg, "#131316", eyebrow, title, body, notes, footer=footer, **kw)
def div(sid, part, title, line, notes):
    return divider(sid, part, title, line, notes).replace("Session 2 &middot; Finding the Right Idea", FT).replace("856d57cb939a323d46943b3b229572d7", "__LOGO__")
SIM = "Simulation test run: six teams on every default, month 8, events off &middot; not market data"

def num5(n, L, T, W, H, label, num, text):
    """bignum for five across: the same card, sized to fit a 312px column."""
    return f'''  <div data-build-in="fade {n}" style="position:absolute; left:{L}px; top:{T}px; width:{W}px; height:{H}px; background:#ffffff; padding:30px 26px; border-radius:18px; border:1px solid #e4e4e7; display:flex; flex-direction:column; gap:10px">
    <p style="font-size:21px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:#86868f">{label}</p>
    <p style="font-size:46px; font-weight:700; letter-spacing:-1px; line-height:1.1; color:#131316">{num}</p>
    <p style="font-size:23px; line-height:1.4; color:#55555f">{text}</p>
  </div>'''

S = {}
S["s10-cover"] = cover(10, "How Do You Know If<br>Your Business Is Working?",
  "Sales, conversion, basket size, what a customer costs, profit per order &mdash; and a one-page dashboard that says what to fix.",
  """Two hours, about 30 slides: 3 min recap, 8 min opening exercise, Part 1 theory about 65 min (the revenue equation 15, conversion and basket 15, what a customer costs and earns 15, profit per order 10, dashboards and trusting numbers 10), exercise 10, Part 2 simulation about 30 min, 3 min close.

Month 8 has run. No new decisions open for month 9: everything opened so far stays the teams' to set, and market research (12.1) is the session. If Sessions 9 and 10 are taught on the same day, read month 7's report instead of month 8's.

The idea for the day: a number on its own says nothing. Sales move because visitors, conversion, basket size or the share of orders kept moved, and each has a different fix.""", size=112)

S["s10-recall"] = sec("s10-recall", "#f5f5f6", "Where we got to last time", "Getting the order to the door, and the cash back",
  grid([
    ("Stock", "Weeks of cover", "Too little loses sales; too much holds cash on a shelf.", "#ed0000"),
    ("Cash", "The cash conversion cycle", "Stock is paid for weeks before the customer's cash arrives.", "#eb6834"),
    ("Delivery", "Cash on delivery", "Wins orders; every refused parcel is paid for twice.", "#2a78d6"),
  ], 3, 300, 300)
  + "\n" + band(4, 660, 170, "Last time: <b>running the operation</b>. Today: <b>reading the numbers</b> to know whether the whole business is working &mdash; and which part to fix.", size=31),
  """Three quick clicks from Session 9.

The bridge: every decision so far shows up in a handful of numbers. Today is about reading them: which moved, why, and which ones can be trusted.""")

S["s10-ex1"] = exercise("s10-ex1", "Exercise 1", "Is this shop working?",
  "An online shop's revenue grew 20% last month.",
  ["Is that good news?", "Which three numbers would you ask for before you answer?",
   "Which number would you look at first every morning?", "Which numbers would you trust least &mdash; and why?"],
  "Exercise 1 &middot; a number on its own says nothing",
  """Eight minutes. One question per click.

Question 1: the room should get to "it depends" &mdash; on whether it was profitable, whether the cash came in, whether it was bought with discounts or ads, and whether last month was a low base (seasonality).

Question 2: expect orders, visitors, conversion, average order, profit or margin, marketing spend, returns. Push for the ones that explain the 20%.

Question 4 sets up the trust slide: ad platforms' numbers, orders placed but not delivered (cash on delivery), surveys, one-off months.""", top=500, h=180, cols=2)

S["s10-part1"] = div("s10-part1", "Part 1 &middot; Theory", "The numbers that<br>run an online shop",
  "Sales, conversion, basket size, what a customer costs and earns, profit per order, and a dashboard on one page &mdash; each with a Pakistani and a global case.",
  """Part 1 follows the course outline: sales, conversion, average order value, customer acquisition cost, profit and simple dashboards. Real-world practice only; the simulation is Part 2.""")

S["s10-equation"] = sec("s10-equation", "#ffffff", "The revenue equation", "Sales = visitors &times; conversion &times; basket",
  grid([
    ("Visitors", "How many came", "Paid ads, search, social, marketplace listings and customers coming back.", "#ed0000"),
    ("Conversion", "How many bought", "Orders &divide; visits. Product, price, trust, checkout and payment options.", "#eb6834"),
    ("Basket", "How much each spent", "Average order value: revenue &divide; orders. Bundles, delivery thresholds, add-ons.", "#2a78d6"),
    ("Kept", "How much stayed sold", "In Pakistan, after refused cash-on-delivery parcels and returns.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "When sales move, ask <b>which of the four moved</b>. Each has different causes &mdash; and a different fix.", size=31),
  """One factor per click.

The equation is an identity, not a theory: revenue is always visitors times the share who order times what each order is worth. Its use is diagnosis. A month with flat sales can hide fewer visitors and better conversion; a month with rising sales can hide a shrinking basket bought with discounts.

The fourth factor matters in cash-on-delivery markets: an order placed is not revenue until it is delivered, accepted and not returned.""")

eqrows = [("Visits", "100,000", "90,000", "&minus;10%"),
          ("Conversion", "2.0%", "2.4%", "+20%"),
          ("Orders", "2,000", "2,160", "+8%"),
          ("Average order", "PKR 3,000", "PKR 2,800", "&minus;7%"),
          ("Revenue", "PKR 6.00m", "PKR 6.05m", "+1%")]
S["s10-equation-ex"] = sec("s10-equation-ex", "#f5f5f6", "Reading a month", "Which number moved?",
  trows(["", "Last month", "This month", "Change"], eqrows, 276, [520, 380, 380, 328], rh=74, size=28)
  + "\n" + band(6, 700, 170, "Revenue looks flat. Underneath, <b>fewer visitors bought more often and spent less</b>. What would you check first &mdash; the ads, or the discount?", size=30),
  """Illustrative numbers. One row per click.

Revenue barely moved, but three things changed: visits fell (an ad budget cut, a season ending, a ranking drop), conversion rose and the basket shrank (both typical of a discount or a cheaper product mix). Each needs a different decision, and none would be visible from revenue alone.

Ask the room which they would check first; there is no single right answer, which is the point: the decomposition tells you where to look.""",
  footer="Illustrative numbers")

convrows = [("Visit &rarr; product", "Wrong audience, slow site, weak first screen", "Aim the ads; speed; show the best sellers"),
            ("Product &rarr; cart", "Price, photos, reviews, out of stock", "Better product pages, reviews, stock"),
            ("Cart &rarr; order", "Surprise delivery fee, forced sign-up, no payment option", "Costs shown early, guest checkout, COD and wallets"),
            ("Order &rarr; delivered", "Refused at the door, fake orders, late delivery", "Confirm orders, reliable couriers, pay-online offers")]
S["s10-conversion"] = sec("s10-conversion", "#ffffff", "Conversion", "Where shoppers drop out",
  trows(["Step", "What loses them", "What wins them back"], convrows, 276, [380, 640, 588], rh=96, size=26)
  + "\n" + band(5, 720, 150, "Conversion is not one number: it is a chain of steps. <b>Which step loses the most shoppers in your shop?</b>", size=30),
  """One step per click.

Most shop platforms show the steps: sessions, product views, add to cart, checkout started, orders. The biggest drop is usually between cart and order, which is why checkout gets so much attention (next case).

The last step is the Pakistani one: in a cash-on-delivery market an order can still fail at the door. A shop that counts orders placed will think its conversion is better than the cash says.""")

S["s10-basket"] = sec("s10-basket", "#f5f5f6", "Average order value", "Making each order bigger",
  grid([
    ("Bundles", "Packs that save a little", "Three-packs or kits: more units in one parcel, one delivery cost.", "#ed0000"),
    ("Thresholds", "Free delivery above a bar", "Set just above a typical basket, shoppers add an item to reach it.", "#eb6834"),
    ("Add-ons", "&ldquo;Customers also bought&rdquo;", "Suggestions on the product page and in the cart.", "#2a78d6"),
    ("Discounts", "The bigger basket trap", "Spend-more vouchers lift the basket and cut the margin on every rupee.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "A bigger basket is worth it only if <b>profit per order</b> rises too. Delivery is paid per parcel, not per item &mdash; so which item would you add?", size=30),
  """One lever per click.

The first three raise what each order is worth without lowering prices; the fourth often lifts the basket by giving margin away. The reason a bigger basket matters so much in e-commerce is that delivery, packing and payment costs are per order: two items in one parcel cost almost the same to deliver as one.

Session 5 covered bundles and thresholds in detail; today the point is reading the average order value as one of the four factors.""")

S["s10-case-conv"] = cases("s10-case-conv", "Cases &middot; Checkout", "Where the order is won or lost",
  ("Pakistan", "bSecure", "Z2C, 2020&ndash;2024", [
    ("The idea", "A one-click &ldquo;universal checkout&rdquo; for Pakistani online stores, launched in beta in 2020."),
    ("The problem it named", "Between 8% and 15% of cash-on-delivery orders rejected at the door, it said."),
    ("What happened", "Its parent, Z2C, scaled it back in January 2024.")]),
  ("Global", "Baymard Institute", "E-commerce research", [
    ("The number", "About 70% of online carts are abandoned: the average of 50 studies (2025)."),
    ("The caveat", "Many are shoppers browsing or comparing prices, not a broken checkout.")]),
  "Most shoppers who put something in the cart do not buy. <b>Measure each step before you blame the traffic.</b>",
  """Two checkout cases.

bSecure: a universal checkout built by Z2C (the venture builder behind several Pakistani start-ups) that entered beta in 2020, pitching faster checkout and risk scoring for cash-on-delivery orders; at launch it said 8&ndash;15% of COD orders were rejected at the doorstep. In January 2024 Z2C announced it was scaling bSecure back. The lesson is two-sided: checkout friction and refusals are real costs, and fixing them is hard to turn into a business of its own.

Baymard Institute: its running average of documented cart-abandonment studies stood at 70.22% across 50 studies when updated in 2025. Baymard itself cautions that much abandonment is normal browsing; its checkout research estimates how much better design can win back.

Sources: Profit (Sep 2020); ProPakistani (Jan 2024); Baymard Institute, cart abandonment rate (2025).""",
  "Sources: Profit (Sep 2020); ProPakistani (Jan 2024); Baymard Institute (2025)")

S["s10-cac"] = sec("s10-cac", "#ffffff", "What a customer costs, and earns", "Acquisition cost against lifetime value",
  grid([
    ("Acquisition cost (CAC)", "Marketing &divide; new customers", "Blended: all marketing. By channel: each channel's spend &divide; the customers it brought.", "#ed0000"),
    ("Lifetime value (LTV)", "Profit, not revenue", "Contribution per order (after product, delivery and payment) &times; orders over the customer's life.", "#2a78d6"),
    ("LTV : CAC", "Earn back the cost, and more", "A common rule of thumb aims for about 3 to 1 &mdash; a guide, not a law.", "#1baf7a"),
  ], 3, 290, 380)
  + "\n" + band(4, 720, 150, "<b>Payback:</b> how many orders before a customer has paid back what it cost to win them? That is where repeat buyers come in.", size=31),
  """One idea per click.

CAC is easy to compute and easy to flatter: count only paid channels, or only last month, and it looks low. Blended CAC divides all marketing by all new customers.

LTV is the hard one. Use contribution (what an order earns after product, delivery, packing, payment and refusals), not revenue, and use the orders customers actually place, from your own records of who came back.

The 3:1 ratio is a widely quoted heuristic, not a statistic; a business with fast payback can live with less, one with slow payback needs more.""")

cacrows = [("Cost to win a customer", "PKR 900", "Marketing &divide; new customers"),
           ("Earned on each order", "PKR 450", "After product, delivery, payment and refusals"),
           ("Orders to pay it back", "2", "900 &divide; 450"),
           ("Orders in a year", "3", "From your repeat records"),
           ("Earned in a year", "PKR 1,350", "LTV : CAC 1.5 in year one")]
S["s10-cac-ex"] = sec("s10-cac-ex", "#f5f5f6", "Working it out", "When does a customer pay for themselves?",
  trows(["", "Example", "Where it comes from"], cacrows, 276, [500, 340, 768], rh=76, size=27)
  + "\n" + band(6, 712, 170, "Halve the cost of winning customers, or get each one to order twice more: <b>which is easier for your brand?</b>", size=30),
  """Illustrative numbers. One row per click.

The first order rarely pays for the customer; the second or third does. That is why retention (Session 8) and acquisition (Session 7) are the same calculation seen from two ends: a cheaper customer who never returns can be worth less than a dear one who orders every month.""",
  footer="Illustrative numbers")

S["s10-case-cac"] = cases("s10-case-cac", "Cases &middot; What a customer costs", "Customers you keep, and customers you rent",
  ("Pakistan", "Saeed Ghani", "Skincare, Karachi", [
    ("How it grew", "Word of mouth was its most effective marketing tool, its team told Profit (2020)."),
    ("What it did not do", "No large-scale marketing campaigns: events, exhibitions and free samples."),
    ("Since then", "A shift toward digital marketing, for more contact with customers.")]),
  ("Global", "Blue Apron", "Meal kits, United States", [
    ("The promise", "Its 2017 listing papers put the average cost of a new customer at $94."),
    ("The test", "In late 2017 it cut marketing from $37.1m to $25.2m a quarter; customers fell from 879,000 to 746,000.")]),
  "A customer who comes back costs nothing to find again. A base that leaves <b>has to be bought again every month</b>.",
  """Two cases on acquisition cost and retention.

Saeed Ghani: a long-established Pakistani skincare brand. In Profit's 2020 piece on six local skincare brands, its marketing team said word of mouth had been its most effective tool and that it had never run large-scale marketing campaigns, relying on public events, exhibitions and small-scale free sampling; it had recently begun shifting toward digital marketing. Low acquisition cost comes from customers who recommend and return.

Blue Apron: its 2017 S-1 reported an average cost per customer of $94 and said six-month revenue per customer was more than four times that. In the fourth quarter of 2017 it cut marketing to $25.2m (13.4% of revenue) from $37.1m a year earlier; customers fell from 879,000 to 746,000 and revenue fell 13%, to $187.7m. When acquisition slowed, the base shrank: many customers had to be won again and again.

Sources: Profit (Nov 2020); Blue Apron S-1 (2017); Blue Apron Q4 2017 results (CNBC; Supermarket Perimeter, Feb 2018).""",
  "Sources: Profit (Nov 2020); Blue Apron S-1 (2017), Q4 2017 results (CNBC, Feb 2018)")

S["s10-profit"] = sec("s10-profit", "#ffffff", "Profit per order", "Where PKR 3,000 of order goes",
  waterfall([
    ("Customer pays", 0, 3000, "total", 1),
    ("Product cost", 3000, 1500, "cost", 2),
    ("Gross profit", 0, 1500, "sub", 2),
    ("Delivery, packing, payment", 1500, 1050, "cost", 3),
    ("Refusals and returns", 1050, 800, "cost", 4),
    ("Before marketing", 0, 800, "sub", 4),
    ("Marketing", 800, 350, "cost", 5),
    ("After marketing", 0, 350, "sub", 5),
    ("Salaries, rent, software", 350, 50, "cost", 6),
    ("Profit", 0, 50, "total", 6),
  ], top=280, rh=52, gap=6, scale=0.33, zero=600)
  + "\n" + P(1100, 860, 692, 50, txt("Which line would you attack first?", 26, "#55555f", 600), n=7),
  """Illustrative numbers. Two clicks per cost: the cost, then what is left.

A plausible shape for a Pakistani personal-care seller, not measured data. Half the order goes on product; delivery, packing and payment take 450; refused and returned parcels another 250 (they pay the courier both ways and often lose the sale); marketing per order 450; fixed costs per order 300. What is left is 50 rupees on a 3,000-rupee order.

The point: selling more of an order that loses money loses money faster. Profit per order is also not cash: the cash arrives when the courier remits it, and the stock was paid for weeks earlier (Session 9).""",
  footer="Illustrative numbers")

S["s10-case-profit"] = cases("s10-case-profit", "Cases &middot; Growth before profit", "When the funding stops, the unit economics remain",
  ("Pakistan", "Airlift", "Quick commerce", [
    ("The growth", "Raised $85m in August 2021 at a $275m valuation; Pakistan's largest quick-commerce start-up."),
    ("The turn", "Cut costs and said it reached profit per order, cutting its burn by 66%."),
    ("The end", "Shut down in July 2022 when new funding did not arrive.")]),
  ("Global", "Getir", "Quick commerce, Turkey", [
    ("The growth", "Valued at up to $11.8bn in March 2022 after expanding across Europe and the US."),
    ("The retreat", "In April 2024 it left the US, UK, Germany and the Netherlands to focus on Turkey.")]),
  "Investors' money can pay for growth for a while. <b>Know your profit per order before you scale.</b>",
  """Two quick-commerce cases.

Airlift: raised an $85m Series B in August 2021 at a $275m valuation and expanded fast-delivery grocery across Pakistan (and briefly South Africa). By mid-2022 it had cut headcount, closed markets and raised prices and delivery fees; it said it had reached order-level profitability and cut financial burn by 66%. It shut down in July 2022 when a funding round failed to close as venture markets tightened.

Getir: the Istanbul quick-delivery company was valued at up to $11.8bn when it raised money in March 2022; by September 2023 its valuation had fallen to as low as $2.5bn. In April 2024 it announced it would leave Britain, Germany, the Netherlands and the US (about 7% of revenue, it said) to concentrate on Turkey, after leaving France, Italy, Spain and Portugal in 2023.

The lesson: growth bought with funding hides unit economics until the funding stops. A business that loses money on each order is not fixed by more orders.

Sources: ProPakistani (Jul 2022); The Business Standard / Bloomberg (Jul 2022); Reuters (Apr 2024).""",
  "Sources: ProPakistani (Jul 2022); Reuters (Apr 2024)")

S["s10-dashboard"] = sec("s10-dashboard", "#f5f5f6", "A simple dashboard", "Eight numbers on one page",
  grid([
    ("Sales", "Net revenue", "After returns and refusals.", "#ed0000"),
    ("Orders", "And visitors", "Where the traffic came from.", "#ed0000"),
    ("Conversion", "Orders &divide; visits", "By step if you can.", "#eb6834"),
    ("Basket", "Average order value", "Against last month.", "#eb6834"),
    ("Customers", "New, and their cost", "Acquisition cost by channel.", "#2a78d6"),
    ("Coming back", "Repeat share", "Orders from returning customers.", "#2a78d6"),
    ("Profit", "Per order", "Contribution after marketing.", "#1baf7a"),
    ("Cash", "And runway", "Cash collected; months it lasts.", "#1baf7a"),
  ], 4, 280, 200, bsize=24, tsize=29)
  + "\n" + band(9, 720, 150, "Each number gets a <b>target</b>, a <b>trend</b> and an <b>owner</b> &mdash; the same numbers, in the same order, every week.", size=31),
  """One number per click.

A dashboard is not every number available; it is the few that say whether the plan is working, laid out so a change jumps out. Tools do not matter: a spreadsheet, the shop platform's analytics, Google Looker Studio. What matters is the same page every week, with last week, the target and who acts.

For a Pakistani shop add the cash-on-delivery numbers: delivered rate and refusals, and cash collected from couriers.""")

S["s10-inputs"] = sec("s10-inputs", "#ffffff", "Inputs and outputs", "Numbers you can move, and numbers that follow",
  two(1, 128, 280, 819, 330, "Outputs", "They tell you what happened",
      ["Sales, profit, market share", "Arrive late; you cannot change them directly", "Good for the board; poor for Monday morning"], "#ed0000")
  + "\n" + two(2, 973, 280, 819, 330, "Inputs", "You can change them this week",
      ["Visitors by channel, conversion by step", "Stock cover, delivery success, response time", "Prices against rivals, repeat-order rate"], "#2a78d6")
  + "\n" + band(3, 660, 210, "Outputs follow inputs, with a lag. <b>Which input, if it moved 10%, would move your profit most?</b>", size=32),
  """Two clicks, then the band.

Output numbers (also called lagging indicators) are what the business is judged on. Input numbers (leading indicators) are the ones a team can act on now and that move the outputs later. A good dashboard has both, and the meeting spends its time on the inputs.""")

S["s10-trust"] = sec("s10-trust", "#f5f5f6", "Trusting the numbers", "Can you believe this number?",
  grid([
    ("Ad platforms", "They count generously", "Meta's default counts a purchase up to 7 days after a click or 1 day after a view; two platforms can claim the same sale.", "#ed0000"),
    ("Orders", "Placed is not paid", "With cash on delivery, an order is not cash until delivered, accepted and remitted.", "#eb6834"),
    ("One month", "Noise and seasons", "Eid, 11.11 and pay-day move every number; compare like with like.", "#2a78d6"),
    ("Research", "Estimates with error bars", "Surveys and studies are samples: check the margin of error and the date.", "#1baf7a"),
  ], 4, 290, 400, bsize=23)
  + "\n" + band(5, 740, 130, "Before you celebrate a number, check it against <b>delivered orders and cash in the bank</b>.", size=30),
  """One source of error per click.

Ad platforms: Meta Ads Manager's default attribution setting counts a conversion within 7 days of a click or 1 day of viewing an ad (third-party guides to Meta's settings, 2025); Google and other platforms use their own windows, so the same sale can be claimed more than once. The shop's own order records are the referee.

Orders: in a cash-on-delivery market a placed order is a promise. Delivered, accepted and remitted orders are the sale.

One month: seasonality and campaigns move everything; compare with the same month last year or with the trend, not just last month.

Research: every survey has a sample and a margin of error, and some data is out of date by the time it arrives.""",
  footer="Meta attribution default: Jon Loomer Digital, guides to Meta's attribution setting (2025)")

S["s10-case-dash"] = cases("s10-case-dash", "Cases &middot; What gets measured", "A dashboard says what a business is trying to do",
  ("Pakistan", "Daraz", "11.11, November 2021", [
    ("What it reported", "PKR 66 crore of sales in the first hour; users up 3.4&times; and orders up 4.7&times; on the year before."),
    ("What it chose to track", "Almost half of customer spend paid online, and sellers from over 100 cities beyond the big three.")]),
  ("Global", "Amazon", "Weekly business review", [
    ("The meeting", "The same metrics, in the same order, every week, reviewed by the business's leaders."),
    ("The idea", "Watch the inputs you control &mdash; selection, price, convenience &mdash; and the outputs follow.")]),
  "Pick the few numbers that <b>track your strategy</b> &mdash; and look at them every week.",
  """Two cases on choosing what to measure.

Daraz, 11.11 in November 2021 (company-reported): PKR 66 crore of sales in the first hour; 43% of Pakistan's digital population visited over the previous 30 days; users and orders up to 3.4 and 4.7 times the previous 11.11; almost 50% of customer spend on prepaid payment; 32,000 sellers from 100+ cities outside Karachi, Lahore and Islamabad. The choice of numbers is the strategy: moving shoppers to prepaid and bringing sellers beyond the big three cities.

Amazon: as described by former executives Colin Bryar and Bill Carr in Working Backwards (2021), the weekly business review walks the same metrics in the same order every week, and separates controllable input metrics (selection, price, convenience) from output metrics (orders, revenue, profit), which the inputs drive.

Sources: ProPakistani (13 Nov 2021); The Nation (14 Nov 2021); Bryar &amp; Carr, Working Backwards (2021).""",
  "Sources: ProPakistani, The Nation (Nov 2021); Bryar &amp; Carr, Working Backwards (2021)")

S["s10-ex2"] = exercise("s10-ex2", "Exercise 2", "A dashboard on one page",
  "A Pakistani skincare brand sells on its own site and on Daraz; most of its orders are cash on delivery.",
  ["Which eight numbers go on its page?", "Which two are inputs it can move this week?",
   "What target would you set for each?", "Which number would make you stop and act?"],
  "Exercise 2 &middot; the numbers that track the strategy",
  """Ten minutes in teams. One question per click. The brand is hypothetical.

Push for the cash-on-delivery numbers (delivered rate, refusals, cash collected) and for one number per stage of the revenue equation. A good answer to question 4 is a threshold that triggers a named action: "refusals above 20% in a week: call every refusing customer and switch courier in that city".

Take two teams' pages.""", top=500, h=180, cols=2)

S["s10-part2"] = div("s10-part2", "Part 2 &middot; The simulation", "Reading your month",
  "No new decisions open. The monthly report, the research desk and its twenty studies are the session.",
  """Part 2 is the simulation. Month 8 has run (month 7, if Sessions 9 and 10 share a day). Nothing new opens for month 9: everything opened so far stays the teams' to set, and the research desk (12.1) is where they can buy what their report does not show.

Every number in Part 2 is the simulation's assumption or a test run of it, not market data.""")

S["s10-category"] = sec("s10-category", "#f5f5f6", "The category online", "How personal care is measured online in Pakistan",
  grid([
    ("Marketplace", "Beauty is growing", "Daraz says health &amp; beauty grew 47% in 2022, top local brands up to 6&times;.", "#ed0000"),
    ("Local brands", "Who leads", "Conatural, Saeed Ghani, Jenpharm, Chiltan Pure, Olim Naturals, MEC on Daraz.", "#eb6834"),
    ("Payment", "Mostly cash", "63% of online sales were cash on delivery across 200 merchants (2021).", "#2a78d6"),
    ("Ad platforms", "Generous counting", "Meta counts a purchase up to 7 days after a click by default.", "#1baf7a"),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "The simulation's teams sell personal care and home care online in Pakistan. <b>Which of these numbers does your own report show?</b>", size=30),
  """The real category first. One card per click.

Marketplace and local brands: Daraz's chief commercial officer, July 2023 (company-reported, no stated baseline). Payment: a bSecure study of 200 small and medium merchants, January&ndash;October 2021 (Aurora, Dawn). Ad platforms: Meta's default attribution setting, 7-day click and 1-day view.

Real brands get these numbers from their shop platform, their marketplace seller centre, their courier's portal and their ad accounts &mdash; each with its own definitions.""",
  footer="Sources: ProPakistani (Jul 2023); Aurora, Dawn (2021); Jon Loomer Digital (2025)")

S["s10-sim-equation"] = sec("s10-sim-equation", "#ffffff", "In the simulation", "One team's month 8, through the revenue equation",
  "\n".join(num5(i + 1, 128 + i * 338, 290, 312, 330, lab, num, text) for i, (lab, num, text) in enumerate([
    ("Visits", "187,834", "Paid 133,913, organic 27,096, returning 26,825."),
    ("Conversion", "1.91%", "Orders &divide; visits: 3,585 orders."),
    ("Basket", "PKR 2,919", "Average order, before returns and refusals."),
    ("Kept", "79.6%", "After returns, refusals, failed deliveries and the pay-online discount."),
    ("Net revenue", "PKR 8.33m", "What the month actually earned."),
  ]))
  + "\n" + band(6, 680, 190, "In this game an order is not a sale until it is delivered and kept: <b>a fifth of gross sales never becomes revenue</b>. Where is each of these in your report?", size=30),
  """One factor per click. A team on every default decision, month 8, in a test world of six identical teams with events off (tools/deck/s10_tests.py).

187,834 visits &times; 1.91% = 3,585 orders &times; PKR 2,919 = PKR 10.47m of gross sales; 79.6% of that is kept as net revenue, PKR 8.33m. The report's Funnel and Stock block shows visits by source, orders and conversion; Every Measure shows the average order and net revenue; the P&amp;L shows what was lost to returns, refusals and failed deliveries.

These are the simulation's assumptions and results, not market data.""",
  footer=SIM)

S["s10-sim-order"] = sec("s10-sim-order", "#f5f5f6", "In the simulation", "What one order earned, month 8",
  waterfall([
    ("Customer pays", 0, 2919, "total", 1),
    ("Returns, refusals, discount", 2919, 2323, "cost", 2),
    ("Net revenue", 0, 2323, "sub", 2),
    ("Product cost", 2323, 879, "cost", 3),
    ("Gross profit", 0, 879, "sub", 3),
    ("Delivery, packing, payment", 879, 550, "cost", 4),
    ("Before marketing", 0, 550, "sub", 4),
    ("Marketing", 550, 160, "cost", 5),
    ("After marketing", 0, 160, "sub", 5),
    ("Payroll, warehouse, tech", 160, -168, "cost", 6),
    ("EBITDA", 0, -168, "loss", 6),
  ], top=276, rh=50, gap=5, scale=0.33, zero=600)
  + "\n" + P(1000, 882, 792, 36, txt("On every default the business loses PKR 168 an order.", 25, "#55555f", 600), n=7),
  """Two clicks per cost: the cost, then what is left. The same default team, month 8, per order (tools/deck/s10_tests.py).

Of PKR 2,919 a customer orders: returns 237, refused parcels 229, failed deliveries 90 and the pay-online discount 40 come off, leaving net revenue of 2,323. Product cost takes 1,444; delivery, packing, payment and marketplace fees 329; marketing 390; payroll, warehouse and technology 328. EBITDA is minus 168 an order.

Compare the per-PKR-1,000 version from Session 3. The question for teams: which line can your decisions move most?""",
  footer=SIM)

S["s10-sim-diagnose"] = sec("s10-sim-diagnose", "#ffffff", "In the simulation", "What held the month back",
  grid([
    ("Wasted spend", "Demand ran out first", "Plenty of visitors; the offer did not win enough of them. Look at price, quality and range.", "#ed0000"),
    ("Under-marketing", "Traffic ran out first", "More people wanted it than saw it. More reach, or better-aimed campaigns.", "#2a78d6"),
    ("Stock-out", "The shelf ran out first", "Demand and traffic were there; the stock was not. Check weeks of cover by product.", "#1baf7a"),
  ], 3, 290, 380)
  + "\n" + band(4, 720, 150, "Orders are the smallest of the three, and the report names the one that bound. <b>Which was yours last month?</b>", size=31),
  """One limit per click. The rule is the simulation's.

Each month the engine works out three limits for every team: the demand its offer wins in the market, the orders its traffic and conversion can produce, and the orders its stock can fill. Orders are the smallest of the three. The report's opening line and the console name the one that bound (or "balanced" when they are within 5% of each other).

A default team in month 8 is on wasted spend: it buys more traffic than its offer converts.""")

tests10 = [("All default", "187,834", "1.91%", "2,919", "8.33m", "&minus;0.60m", "Wasted spend"),
           ("Ad budgets halved", "159,984", "2.16%", "2,923", "8.01m", "&minus;0.26m", "Under-marketing"),
           ("10% off everything", "187,834", "1.99%", "2,604", "7.78m", "&minus;1.37m", "Wasted spend"),
           ("Prices 15% higher", "187,834", "1.67%", "3,410", "8.41m", "+0.20m", "Under-marketing"),
           ("No stock bought in month 7", "187,834", "0.26%", "2,940", "0.38m", "&minus;2.70m", "Stock-out")]
S["s10-sim-tests"] = sec("s10-sim-tests", "#f5f5f6", "In the simulation", "One change, month 8: where did revenue move?",
  trows(["Test", "Visits", "Conversion", "Basket", "Net revenue", "EBITDA", "What bound"], tests10, 276,
        [420, 190, 200, 170, 220, 190, 218], rh=72, size=25, head_size=20)
  + "\n" + band(6, 700, 170, "With no stock, <b>conversion collapses to 0.26%</b> though nothing about the shop changed. Which number would have warned you a month earlier?", size=29),
  """One test per click. Each line is one team changing one thing in month 8 (the stock test: buying nothing in month 7) against an identical team on every default; six teams, seven default months first, events off (tools/deck/s10_tests.py).

Ad budgets halved: visits fell 15% but conversion rose, because the offer still won most of the same demand; revenue fell 0.32m (visits &minus;1.23m, conversion +0.94m) and EBITDA improved 0.34m this month on 0.43m less marketing &mdash; with fewer new customers to come back in later months.

10% off: conversion added 0.36m, the smaller basket took 0.94m away: revenue &minus;0.55m, EBITDA &minus;0.77m.

Prices 15% higher: conversion took 1.03m away, the bigger basket added 1.23m; EBITDA +0.80m this month, on 12% fewer orders and so fewer customers to come back.

No stock bought in month 7: 3,104 orders lost to the stock-out; in the funnel it shows as conversion, which is why weeks of cover belongs on the dashboard.

One month only; these are directions, not forecasts.""",
  footer=SIM)

S["s10-sim-trust"] = sec("s10-sim-trust", "#ffffff", "In the simulation", "Which numbers to trust",
  grid([
    ("Ad returns", "Reported runs 32% high", "Platform-reported return on ad spend 7.87 against 5.96 true for the default team. The true figure: Attribution Study, MR-12.", "#ed0000"),
    ("Market share", "Only from research", "Your own report shows your shop; your share of the market comes from MR-03, &plusmn;5%.", "#eb6834"),
    ("Perception", "Only from research", "What customers think of your quality and delivery: Brand Perception Tracker, MR-07.", "#2a78d6"),
    ("Timing", "Some arrive late", "A lagged study lands with next month's report. The same study twice returns the same number.", "#1baf7a"),
  ], 4, 290, 420, bsize=23)
  + "\n" + band(5, 760, 110, "Your report is the truth about <b>your</b> shop. The market, rivals and customers' minds cost money to see.", size=29),
  """One rule per click. The rules are the simulation's.

Ad returns: the report's reported ROAS is the platform's figure, 32% above the true return in this game (7.87 against 5.96 for the default team in month 8); MR-12 measures the true incremental return and arrives a month later.

Market share, perception, segment sizes and rivals' prices are not in a team's own report; they are sold on the research desk, each with a margin of error. Buying a study twice in a month returns the same number, so noise cannot be averaged away.

These are the simulation's assumptions; real founders face the same gaps and buy the same kinds of research.""",
  footer="Decision rules from the simulation &middot; not market data")

study_rows = [("MR-03 Market Share Report", "60,000", "This month", "&plusmn;5%", "Are we gaining on rivals?"),
              ("MR-12 Attribution Study", "110,000", "Next month", "&plusmn;12%", "What do the ads really return?"),
              ("MR-10 Cohort &amp; Churn Analysis", "40,000", "This month", "&plusmn;4%", "Do customers come back?"),
              ("MR-09 NPS &amp; CSAT Deep-dive", "30,000", "This month", "&plusmn;5%", "Are they happy?"),
              ("MR-02 Competitor Price Tracker", "50,000", "This month", "&plusmn;3%", "Are we priced right?"),
              ("MR-07 Brand Perception Tracker", "75,000", "This month", "&plusmn;7%", "Do they see what we are?")]
S["s10-sim-research"] = sec("s10-sim-research", "#f5f5f6", "In the simulation", "Six studies that answer &ldquo;is it working?&rdquo;",
  trows(["Study", "PKR", "Arrives", "Error", "Answers"], study_rows, 276, [560, 170, 230, 160, 488], rh=70, size=25, head_size=20)
  + "\n" + band(7, 760, 110, "Research buys information, not results. <b>Which study would change a decision you are about to take?</b>", size=29),
  """One study per click; six of the twenty on the research desk (12.1). Prices, timing and error bands are the simulation's.

A study is charged when the month runs and its findings land on the research desk beside the decision they bear on. The error column is the study's margin of error. MR-12 is the only way to see the true return on ad spend; MR-03 the only way to see market share; MR-07 the only way to see the perception gap.

Ask which study would change a decision; a study that would not is money spent twice.""",
  footer="Study prices and error bands from the simulation &middot; not market data")

S["s10-sim-dashboard"] = sec("s10-sim-dashboard", "#ffffff", "In the simulation", "Your team's dashboard, from the report",
  grid([
    ("Growth", "Net revenue, orders", "Every Measure &middot; Growth", "#ed0000"),
    ("Funnel", "Visits, conversion", "Funnel and Stock", "#ed0000"),
    ("Basket", "Average order", "Every Measure &middot; Growth", "#eb6834"),
    ("Customers", "New customers, CAC", "Every Measure &middot; Marketing", "#eb6834"),
    ("Coming back", "Repeat share, active base", "Every Measure &middot; Customer", "#2a78d6"),
    ("Profit", "Contribution margin", "Every Measure &middot; Commercial", "#2a78d6"),
    ("Delivery", "Delivered, refused", "Every Measure &middot; Operations", "#1baf7a"),
    ("Cash", "Cash, runway, loan", "Every Measure &middot; Finance", "#1baf7a"),
  ], 4, 280, 200, bsize=23, tsize=28)
  + "\n" + band(9, 720, 150, "Which eight would you put on your team's page &mdash; and <b>what target for month 12?</b>", size=31),
  """One number per click, with where it sits in the monthly report.

The Excel workbook (when the instructor opens it) has every month side by side with the KPIs as formulas, which makes the trend line easy. The board memo is the place to name the target and say whether it was hit.""")

S["s10-checks"] = sec("s10-checks", "#fdeceb", "Before month 9 runs", "Four questions before you decide",
  grid([
    ("Constraint", "What bound last month?", "Wasted spend, under-marketing or stock-out: the report says.", "#ed0000"),
    ("Equation", "Which factor moved?", "Visits, conversion, basket or the share kept.", "#eb6834"),
    ("Customers", "Is each worth its cost?", "Acquisition cost against what they earn over time.", "#2a78d6"),
    ("Research", "What would you buy?", "Only a study that would change a decision.", "#1baf7a"),
  ], 4, 300, 340)
  + "\n" + band(5, 700, 150, "Name in the board memo the number in month 9's report that will tell you <b>whether your plan worked</b>.", size=30),
  """One question per click, while teams review their report and the decision form.

Logistics for the notes, not the slide: decisions for month 9 close at [deadline]. No new levers open this round; market research (12.1) is on the research desk. The month-9 report will show whether the change each team names worked.""")

S["s10-next"] = sec("s10-next", "#131316", "Next session", "How can AI help?",
  grid([
    ("Session 11", "AI in e-commerce", "Recommendations, demand forecasting, customer service, creative.", "#ff3b3b"),
    ("Real costs", "Builds that can fail", "Each has a price, a build time and a chance of not working.", "#ff3b3b"),
    ("Your numbers", "Which would pay back?", "Today's dashboard says where AI could help most.", "#ff3b3b"),
  ], 3, 300, 300, bg="#1f1f24", border="border:1px solid #33333b;", tcol="#ffffff", bcol="#c9c9d1")
  + "\n" + band(4, 660, 150, "Today: knowing whether the business works. Next time: <b>which AI tools would make it work better</b>.", bg="#ed0000", size=31),
  """Close. One card per click.

Session 11 looks at AI across e-commerce and at the simulation's AI builds: each costs money up front, takes time to build and may not work; the dashboard from today is how to judge which one would pay back.""", dark=True, eyecol="#ff3b3b")

ORDER = ["s10-cover", "s10-recall", "s10-ex1", "s10-part1", "s10-equation", "s10-equation-ex", "s10-conversion",
         "s10-basket", "s10-case-conv", "s10-cac", "s10-cac-ex", "s10-case-cac", "s10-profit", "s10-case-profit",
         "s10-dashboard", "s10-inputs", "s10-trust", "s10-case-dash", "s10-ex2", "s10-part2", "s10-category",
         "s10-sim-equation", "s10-sim-order", "s10-sim-diagnose", "s10-sim-tests", "s10-sim-trust",
         "s10-sim-research", "s10-sim-dashboard", "s10-checks", "s10-next"]
SECTIONS = {
    "s10-open": {"description": "Session 10 · How do you know if your business is working?", "start": "s10-cover"},
    "s10-numbers": {"description": "Part 1 · The revenue equation, conversion and basket, with cases", "start": "s10-part1"},
    "s10-customers": {"description": "What a customer costs and earns, and profit per order, with cases", "start": "s10-cac"},
    "s10-dashboards": {"description": "Dashboards, inputs and outputs, trusting the numbers, with cases", "start": "s10-dashboard"},
    "s10-sim": {"description": "Part 2 · Reading your month in the simulation", "start": "s10-part2"}}

if __name__ == "__main__":
    write(S, ORDER, "Session 10 — How Do You Know If Your Business Is Working?", SECTIONS)
