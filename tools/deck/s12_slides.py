"""Session 12 - How Do You Grow? About 25 slides.

Run: python s12_slides.py <deck folder> [logo url]
Part 2's numbers come from tools/deck/s12_tests.py. Slide ids carry an "s12-"
prefix so the deck can sit beside Session 11's (tools/deck/s11_s12_slides.py).
"""
import pathlib, sys, json
HERE = pathlib.Path(__file__).parent
exec((HERE / "s7_slides.py").read_text().split("\nS = {}\n")[0])
FT = "Session 12 &middot; How Do You Grow?"
def sec(sid, bg, eyebrow, title, body, notes, footer=FT, **kw):
    return section(sid, bg, "#131316", eyebrow, title, body, notes, footer=footer, **kw)
def div(sid, part, title, line, notes):
    return divider(sid, part, title, line, notes).replace("Session 2 &middot; Finding the Right Idea", FT).replace("856d57cb939a323d46943b3b229572d7", "__LOGO__")
SIM = "Simulation test run: six teams on every default, events off &middot; not market data"

def num5(n, L, T, W, H, label, num, text):
    """bignum for five across: the same card, sized to fit a 312px column."""
    return f'''  <div data-build-in="fade {n}" style="position:absolute; left:{L}px; top:{T}px; width:{W}px; height:{H}px; background:#ffffff; padding:30px 26px; border-radius:18px; border:1px solid #e4e4e7; display:flex; flex-direction:column; gap:10px">
    <p style="font-size:21px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:#86868f">{label}</p>
    <p style="font-size:46px; font-weight:700; letter-spacing:-1px; line-height:1.1; color:#131316">{num}</p>
    <p style="font-size:23px; line-height:1.4; color:#55555f">{text}</p>
  </div>'''

def bars(weights, base=700, maxh=330, W=110, gap=31):
    """One bar a month; months 1-6, 7-9 and 10-12 build on three clicks."""
    top = max(weights)
    out = []
    for i, x in enumerate(weights):
        h = int(maxh * x / top)
        L, T = 128 + i * (W + gap), base - h - 44
        n = 1 if i < 6 else 2 if i < 9 else 3
        col = "#ed0000" if i >= 9 else "#c9c9d1"
        out.append(f'''  <div data-build-in="fade {n}" style="position:absolute; left:{L}px; top:{T}px; width:{W}px; height:{h + 92}px">
    <p style="position:absolute; left:0px; top:0px; width:{W}px; text-align:center; font-size:23px; font-weight:600; color:{'#ed0000' if i >= 9 else '#131316'}; font-family:'JetBrains Mono', monospace">{x * 100:.1f}%</p>
    <div style="position:absolute; left:0px; top:44px; width:{W}px; height:{h}px; background:{col}; border-radius:6px 6px 0px 0px"></div>
    <p style="position:absolute; left:0px; top:{h + 56}px; width:{W}px; text-align:center; font-size:22px; color:#55555f">Month {i + 1}</p>
  </div>''')
    return "\n".join(out)

S = {}
S["s12-cover"] = cover(12, "How Do You Grow?",
  "Ways to grow, new channels and markets, paying for growth &mdash; and what your twelve months added up to.",
  """Two hours, about 25 slides: 3 min recap, 8 min opening exercise, Part 1 theory about 50 min (growth options 10, channels 10, new markets 10, paying for growth 15, growth that lasts 5), exercise 10, Part 2 about 45 min (the final scorecard 15, team presentations), 3 min close.

Months 11 and 12 have run and decisions are closed. Before the session: publish the final rankings in the console, and have each team's founding plan (objective and business plan, D0.1 and D0.14) to hand.

The idea for the day: growth is a choice about where the next customer comes from and what it costs to reach them. The game's twelve months are the evidence for each team's answer.""", size=132).replace('id="cover"', 'id="s12-cover"')

S["s12-recall"] = sec("s12-recall", "#f5f5f6", "Where we got to last time", "AI is an investment",
  grid([
    ("Cost and time", "Paid before it works", "Money up front, months to build, a running cost after.", "#ed0000"),
    ("Chance", "It may not work", "And a tool that works four times in five is worth four-fifths.", "#eb6834"),
    ("Proof", "One number", "Basket, stock, service cost or ad cost &mdash; named before you buy.", "#2a78d6"),
  ], 3, 300, 300)
  + "\n" + band(4, 660, 170, "Last time: <b>tools that make the business better</b>. Today: <b>making it bigger</b> &mdash; and what your twelve months added up to.", size=31),
  """Three quick clicks from Session 11.

The bridge: AI, like every lever in the course, is judged by what it does to the numbers. Growth is judged the same way: by what the next rupee of sales costs to win and keep.""")

S["s12-ex1"] = exercise("s12-ex1", "Exercise 1", "Take the money?",
  "A Pakistani skincare brand sells PKR 10m a month online, makes a profit on each order and has customers who come back. An investor offers money to triple it in a year.",
  ["Where would the next PKR 20m a month come from?", "What has to be true before you take the money?",
   "What would you refuse to change?", "What would make you say no?"],
  "Exercise 1 &middot; growth is a choice",
  """Eight minutes. One question per click. The brand and the offer are hypothetical.

Question 1: more customers in the same cities, new products for the same customers, new cities, the diaspora abroad, marketplaces, shops. Each answer is a different growth route (next slide).

Question 2 is the readiness test: profit per order stays positive at the bigger size, customers keep coming back, stock, couriers and service can handle three times the orders, and the working capital is funded.

Question 4: an investor's timetable that forces growth faster than the business can deliver it (Airlift and Getir in Session 10).""", top=520, h=170, cols=2)

S["s12-part1"] = div("s12-part1", "Part 1 &middot; Theory", "Four ways<br>to grow",
  "The growth routes, new channels, new markets and how growth is paid for &mdash; each with a Pakistani and a global case.",
  """Part 1 follows the course outline: how an online business grows. Real-world practice only; the simulation is Part 2.""")

S["s12-routes"] = sec("s12-routes", "#ffffff", "Growth routes", "Where the next customer comes from",
  grid([
    ("Same products, same market", "Sell more of what works", "More reach, better conversion, more repeat orders. The least risk.", "#ed0000"),
    ("New products, same market", "More for the same customers", "A new range for the customers you already have and know.", "#eb6834"),
    ("Same products, new market", "New customers elsewhere", "New cities, the diaspora abroad, a marketplace&rsquo;s shoppers.", "#2a78d6"),
    ("New products, new market", "Start something new", "Everything unknown at once: the most risk, the most money.", "#1baf7a"),
  ], 2, 290, 190, tsize=29, bsize=24)
  + "\n" + band(5, 720, 150, "Risk rises as you move from what you know &mdash; and <b>so does the cash it takes</b>. Which route has your business not finished yet?", size=30),
  """One route per click. This is Igor Ansoff's product&ndash;market matrix (1957), the oldest growth framework still in use.

The usual advice for a young business: exhaust the first box before leaving it. Growing in the same market with the same products uses everything the business already knows: its customers, suppliers, couriers and data. Each move away adds something unknown, and each unknown costs money to learn.""")

S["s12-ready"] = sec("s12-ready", "#f5f5f6", "Before you grow", "Is the business ready to be bigger?",
  grid([
    ("Unit", "Profit on every order", "After product, delivery, refusals and marketing &mdash; or growth multiplies losses.", "#ed0000"),
    ("Customers", "They come back", "A repeat base means each new customer is worth more than one order.", "#eb6834"),
    ("Operations", "It holds at twice the size", "Stock, couriers, the warehouse and service, before the orders arrive.", "#2a78d6"),
    ("Cash", "Growth is paid for", "More stock and more parcels in transit, months before the profit.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "Growing a business that loses money on each order <b>loses money faster</b>. Which of the four would fail first in yours?", size=31),
  """One test per click.

These four come straight from earlier sessions: profit per order (Session 10), retention (Session 8), operations (Session 9), cash (Sessions 3 and 9). Growth puts each under strain at once, which is why a weakness that was manageable at one size becomes fatal at the next.""")

chrows = [("Own website", "What you earn", "Highest", "Full", "All of it"),
          ("Marketplace", "Its shoppers", "Less its commission", "Its rules", "Little"),
          ("Social and WhatsApp", "Your followers", "High, more work", "Shared", "Some"),
          ("Shops and stockists", "Their footfall", "Their margin off", "Theirs", "Little")]
S["s12-channels"] = sec("s12-channels", "#ffffff", "New channels", "Reach, margin and control",
  trows(["Channel", "Reach", "Margin", "Control", "Customer data"], chrows, 276, [400, 320, 340, 248, 300], rh=96, size=26)
  + "\n" + band(5, 720, 150, "A new channel buys reach with margin and control. <b>What do you give up for each new customer it brings?</b>", size=30),
  """One channel per click.

The trade is the same in each: someone else's audience costs a share of the sale (a marketplace's commission, a stockist's margin) and gives up some control over price, presentation and the customer relationship. Your own site keeps all three but every visitor has to be earned.

Most Pakistani brands use several at once. The question is the mix, and whether each channel earns its place after its costs.""")

S["s12-case-channels"] = cases("s12-case-channels", "Cases &middot; Channels", "Renting someone else&rsquo;s shoppers",
  ("Pakistan", "Amazon", "Open to Pakistani sellers, 2021", [
    ("The change", "On 21 May 2021 Amazon added Pakistan to the countries whose sellers can register."),
    ("Before", "Pakistani sellers used accounts and addresses abroad to sell on it."),
    ("After", "Pakistan was third among new sellers&rsquo; home countries on Amazon US in 2022.")]),
  ("Global", "Nike", "Amazon, 2019&ndash;2025", [
    ("The exit", "Stopped selling to Amazon directly in 2019, to grow its own direct business."),
    ("The return", "Back on Amazon in 2025: its products were there anyway, through other sellers.")]),
  "A marketplace brings shoppers you could not reach alone. <b>Decide what you give up for them.</b>",
  """Two channel cases.

Amazon and Pakistan: after an announcement by the commerce adviser on 6 May 2021, Amazon confirmed on 21 May 2021 that Pakistan had been added to its list of countries approved for seller registration; until then Pakistani sellers had worked around the restriction with accounts and proxy addresses abroad. Marketplace Pulse reported that Pakistan was the third-largest home country of new sellers joining Amazon's US marketplace in 2022.

Nike: stopped selling directly on Amazon in 2019, about two years after it started, amid complaints about counterfeits and unauthorised sellers and a push to grow its own direct-to-consumer business. Nike goods stayed on Amazon through third-party sellers. In May 2025 Nike confirmed it was returning to sell directly on Amazon.

Sources: Profit, The Express Tribune (May 2021); Marketplace Pulse; CNBC, Retail Dive (May 2025).""",
  "Sources: Profit, Express Tribune (May 2021); Marketplace Pulse; CNBC, Retail Dive (May 2025)")

S["s12-markets"] = sec("s12-markets", "#f5f5f6", "New markets", "Beyond the first city",
  grid([
    ("Cities", "Beyond the big three", "Delivery times, refusal rates and couriers change city by city.", "#ed0000"),
    ("Diaspora", "Pakistanis abroad", "The UK, the Gulf and North America already know the brands.", "#eb6834"),
    ("Cross-border", "Shipping abroad", "Duties, returns that cost more than the product, payment in dollars.", "#2a78d6"),
    ("Local rivals", "Someone is already there", "Each market has its own leader, prices and habits.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "A new market is a new business with a familiar brand. <b>What would you need to learn there before you spend?</b>", size=31),
  """One idea per click.

Within Pakistan, the first new market is usually the next city: the same products, different couriers, delivery times and cash-on-delivery refusal rates. Abroad, Pakistani brands have a ready first market in the diaspora, which already knows the names; beyond it, the brand is unknown.

The common failure is to treat a new market as more of the same: same range, same prices, same operations, all at once.""")

S["s12-case-markets"] = cases("s12-case-markets", "Cases &middot; New markets", "Too much, too fast &mdash; or one step at a time",
  ("Pakistan", "Khaadi", "Abroad since 2010", [
    ("The steps", "Dubai in 2010, the UK in 2013, then the Gulf, Canada and the US."),
    ("The setback", "In 2019 its UK business went into a pre-pack deal; four of ten stores closed."),
    ("The next step", "In 2024 it made its first moves in the US, one of its main markets ahead.")]),
  ("Global", "Target", "Canada, 2013&ndash;2015", [
    ("The launch", "133 stores opened in Canada in about two years."),
    ("The exit", "Closed them all in January 2015: empty shelves, high prices, &ldquo;too much too fast&rdquo;.")]),
  "Grow into a new market one step at a time, and <b>fix what breaks before the next step</b>.",
  """Two new-market cases.

Khaadi: the Pakistani fashion brand opened its first store abroad in Dubai in 2010 and entered the UK in 2013. In October 2019 its UK business went through a pre-pack administration (administrators RSM, buyer Weaves UK Trading): four underperforming stores of ten closed and six kept trading, with the founding management in place. In 2022 IFC took a $25m minority stake to help expand stores and online global sales, and in July 2024 Modern Retail reported its first moves into the US, which its leadership called one of its primary markets.

Target Canada: Target opened 133 stores in Canada from 2013 and announced in January 2015 that it would close them all, with more than 17,000 jobs lost. Shoppers complained of empty shelves, high prices and missing brands; chief executive Brian Cornell said the company had taken on too much too fast.

Sources: Retail Gazette, FashionUnited (Oct 2019); Modern Retail (Jul 2024); CBC, The Globe and Mail (Jan 2015).""",
  "Sources: Retail Gazette, FashionUnited (Oct 2019); Modern Retail (Jul 2024); CBC (Jan 2015)")

S["s12-funding"] = sec("s12-funding", "#ffffff", "Paying for growth", "Where the money comes from",
  grid([
    ("Profits", "Growth you can afford", "Slow, and the business stays yours.", "#ed0000"),
    ("Terms", "Suppliers and couriers", "Paying suppliers later, getting cash from couriers sooner.", "#eb6834"),
    ("Debt", "Loans", "Repaid from cash flow, with interest, whatever happens.", "#2a78d6"),
    ("Equity", "Investors", "A share of the business &mdash; and their timetable for growth.", "#1baf7a"),
  ], 4, 290, 340)
  + "\n" + band(5, 680, 190, "Each source sets a pace. <b>Investors who want ten times their money will not wait for a business that grows 30% a year.</b>", size=30),
  """One source per click.

In a cash-on-delivery business working capital is the first source to work on: every week shaved off supplier payment or courier remittance is cash that does not have to be raised.

Debt suits a business with predictable cash flow (a working capital loan against stock and receivables). Equity suits a business that can grow fast enough to return many times the money; it brings pressure to grow at that pace, and a business that cannot will be pushed to try.""")

fundrows = [("Sales a month", "PKR 10m", "PKR 20m"),
            ("Stock held: six weeks of product cost", "PKR 8.3m", "PKR 16.6m"),
            ("Cash with couriers: two weeks of sales", "PKR 4.6m", "PKR 9.2m"),
            ("Cash tied up", "PKR 12.9m", "PKR 25.9m")]
S["s12-funding-ex"] = sec("s12-funding-ex", "#f5f5f6", "Working it out", "Growth eats cash before it makes any",
  trows(["", "Today", "Twice the size"], fundrows, 276, [760, 400, 448], rh=86, size=28)
  + "\n" + band(5, 680, 190, "Doubling sales ties up <b>another PKR 12.9m</b> before the first extra rupee of profit. Where would yours come from?", size=31),
  """Illustrative numbers. One row per click.

Assumes product cost is 60% of sales, six weeks of stock (6 &divide; 4.33 months &times; 6m) and courier remittance two weeks behind delivery (2 &divide; 4.33 months &times; 10m). Twice the sales needs twice both, paid before the extra sales arrive.

This is why profitable businesses run out of cash while growing, and why the working capital loan in the simulation exists.""",
  footer="Illustrative numbers")

S["s12-case-funding"] = cases("s12-case-funding", "Cases &middot; Paying for growth", "When the money sets the pace",
  ("Pakistan", "Bazaar", "B2B e-commerce, Karachi", [
    ("The raise", "A $70m Series B in 2022, led by Dragoneer and Tiger Global: over $100m raised in all."),
    ("The plan", "More cities, new categories, lending to the shops it supplied."),
    ("Later", "It shut two new lines and let about 600 people go, as rivals shut down or shrank.")]),
  ("Global", "Allbirds", "Shoes, United States", [
    ("The peak", "Listed in November 2021 at about $4bn; 27 stores in 2021, 58 by the end of 2022."),
    ("The end", "Sales peaked in 2022; in 2026 it agreed to sell its brand and assets for about $39m.")]),
  "Funding can buy growth for a while. <b>Only customers who come back, at a profit, keep paying for it.</b>",
  """Two cases on paying for growth.

Bazaar: founded in Karachi in 2020 as a B2B marketplace supplying neighbourhood shops, it raised a $70m Series B in March 2022, co-led by Dragoneer and Tiger Global, taking its total raised past $100m, to expand into more cities, add categories and scale lending. Profit later reported that it had shut two newly launched verticals and laid off about 600 people, including its whole Lahore field force, while rivals Jugnu (July 2023) and Retailo closed operations and Dastgyr cut most of its staff.

Allbirds: listed on Nasdaq in November 2021 at about $4bn on its first day; it grew from 27 stores in mid-2021 to 58 by the end of 2022 as revenue peaked at about $298m. Revenue then fell; it closed stores from 2024 and in March 2026 agreed to sell its brand and assets for about $39m.

Sources: ProPakistani, Fintech Futures (Mar 2022); Profit; ProPakistani (Jul 2023); Digital Commerce 360, The Next Web (Mar 2026).""",
  "Sources: ProPakistani (Mar 2022, Jul 2023); Profit; Digital Commerce 360 (Mar 2026)")

S["s12-lasting"] = sec("s12-lasting", "#ffffff", "Growth that lasts", "Growth you do not have to buy again",
  grid([
    ("Repeat", "Customers compound", "Each month&rsquo;s customers add to the next month&rsquo;s orders.", "#ed0000"),
    ("Word of mouth", "Customers bring customers", "The cheapest acquisition there is, and the slowest to build.", "#eb6834"),
    ("Brand", "They come without an ad", "Searches for your name, not your category.", "#2a78d6"),
    ("Margin", "Profit holds at scale", "Delivery, refusals and service cost no more per order as you grow.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "Growth bought with ads stops when the ads stop. <b>Growth built on customers keeps going.</b> Which kind is yours?", size=31),
  """One idea per click.

The difference between rented and owned growth was the thread of Sessions 7 and 8: a customer won by a discount or an ad has to be won again; a customer who comes back, or brings a friend, keeps paying for the cost of winning them.

The best evidence of owned growth is in the numbers: a rising repeat share, organic and returning visits growing faster than paid, and profit per order that holds as the business gets bigger.""")

S["s12-ex2"] = exercise("s12-ex2", "Exercise 2", "A growth plan on one page",
  "The skincare brand from Exercise 1 takes the money.",
  ["Which route first &mdash; and why that one?", "What will it cost before it earns anything back?",
   "Which number would tell you to stop?", "What will you say no to?"],
  "Exercise 2 &middot; one route, one number, one stop sign",
  """Ten minutes in teams. One question per click. The brand is hypothetical.

A good answer to question 2 uses the working-capital slide: stock and cash in transit before any profit. A good answer to question 3 is a threshold with a date: "if repeat share in the new city is below 20% after six months, we stop".

Take two teams' plans.""", top=500, h=180, cols=2)

S["s12-part2"] = div("s12-part2", "Part 2 &middot; The simulation", "Your twelve months",
  "Months 11 and 12 have run and the decisions are closed: the final scorecard, what moved it, and the story you present.",
  """Part 2 is the simulation. Every decision is closed; the final rankings are published in the console.

Every number in Part 2 is the simulation's assumption or a test run of it, not market data.""")

S["s12-category"] = sec("s12-category", "#f5f5f6", "The category online", "Routes to growth for a Pakistani brand online",
  grid([
    ("Same market", "Beauty is growing", "Daraz says health &amp; beauty grew 47% in 2022.", "#ed0000"),
    ("Marketplaces", "Selling to the world", "Pakistan was third among new sellers&rsquo; countries on Amazon US in 2022.", "#eb6834"),
    ("Abroad", "The diaspora first", "IFC put $25m into Khaadi in 2022, for stores and online sales abroad.", "#2a78d6"),
    ("Payment", "Mostly cash at home", "63% of online sales were cash on delivery across 200 merchants (2021).", "#1baf7a"),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "The simulation&rsquo;s teams sold personal care and home care online in Pakistan. <b>Which route would your brand take next?</b>", size=30),
  """The real category first. One card per click.

Health &amp; beauty growth: Daraz's chief commercial officer, July 2023 (company-reported, no stated baseline). Amazon: Marketplace Pulse on new sellers joining Amazon's US marketplace in 2022. Khaadi: IFC's $25m minority investment, 2022. Payment: a bSecure study of 200 small and medium merchants, January&ndash;October 2021 (Aurora, Dawn).

The simulation's market is one country and one category; real brands choose between these routes.""",
  footer="Sources: ProPakistani (Jul 2023); Marketplace Pulse; IFC (2022); Aurora, Dawn (2021)")

S["s12-sim-scorecard"] = sec("s12-sim-scorecard", "#ffffff", "In the simulation", "How the final score is built",
  grid([
    ("25 points", "Profitability", "Margins over the twelve months, weighted by revenue, against the best team.", "#ed0000"),
    ("20 points", "Growth", "Month 12 sales against month 1, market share gained, orders.", "#eb6834"),
    ("20 points", "Customer value", "Lifetime value against its cost, repeat orders, the base and NPS at the end.", "#2a78d6"),
    ("15 points", "Operations", "Service, delivery success, refused and returned parcels, stock turns.", "#1baf7a"),
    ("10 points", "Cash", "Runway at the end, cash generated, net margin &mdash; nothing if ever insolvent.", "#8a6414"),
    ("10 points", "Decision quality", "Decisions taken each month, and board memos that match them.", "#55555f"),
  ], 3, 290, 220, tsize=30, bsize=24)
  + "\n" + band(7, 780, 120, "Six pillars, published in month 0. <b>Which one did your team give away?</b>", size=30),
  """One pillar per click. The scorecard is the simulation's, the one published in How You Are Scored.

Profitability: contribution before marketing (12), EBITDA (8) and gross margin (5), each a margin over the run weighted by each month's revenue; from rules v2 (month 3 in the Fall-2026 game), marked against the best team in the room. Growth: month 12's net revenue against month 1's (8), share gained (7), orders against a baseline business (5). Customer value: lifetime value against lifetime acquisition cost (6), repeat share of all orders (5), active customers at the end (6), NPS at the end (3). Operations: service level (2), delivery success (6), refusal and return costs (4), stock turns (3). Cash: runway at the end (5), cash the business generated (3), net margin (2); a team that ever went insolvent scores nothing here. Decision quality: decisions taken (8) and the board memo (2), month by month.""",
  footer="The simulation&rsquo;s published scorecard")

S["s12-sim-weights"] = sec("s12-sim-weights", "#f5f5f6", "In the simulation", "Later months count more",
  bars([(t + 1) / 78 for t in range(12)])
  + "\n" + band(4, 770, 130, "Months 10 to 12 carry <b>42%</b> of every month-by-month measure; months 1 to 6, 27%. And some measures read only month 12.", size=29),
  """Three clicks: months 1&ndash;6, 7&ndash;9, then 10&ndash;12. The weights are the simulation's: month t counts t &divide; 78.

Every measure that is averaged over the year (market share, orders, service, delivery, refusal costs, net margin, decision quality) weighs month 12 about twelve times as heavily as month 1. Margins are weighted by each month's revenue instead. Some measures are read at the end only: month 12's revenue against month 1's, active customers, NPS, runway and lifetime value.

The design intent: a team is judged on where it took the business, not where it started.""",
  footer="Round weights from the simulation &middot; not market data")

endrows = [("All default", "9.56m", "&minus;0.67m", "63.0", ""),
           ("Stop all marketing", "5.93m", "+0.50m", "52.6", "Growth &minus;8.3"),
           ("20% off everything", "7.12m", "&minus;4.23m", "51.3", "Profitability &minus;3.6"),
           ("Buy no more stock", "6.01m", "&minus;1.56m", "52.5", "Growth &minus;6.9"),
           ("Prices 10% higher", "9.11m", "+0.24m", "62.9", "Growth &minus;1.5"),
           ("Double the ad budgets", "11.60m", "&minus;1.34m", "67.0", "Growth +4.0")]
S["s12-sim-endgame"] = sec("s12-sim-endgame", "#ffffff", "In the simulation", "What the last two months could buy",
  trows(["Months 11 and 12", "Month 12 sales", "EBITDA, 11&ndash;12", "Score", "Moved most"], endrows, 276,
        [520, 270, 290, 170, 358], rh=70, size=25, head_size=20)
  + "\n" + band(7, 770, 130, "Cutting to look profitable cost about ten points. The one move that gained <b>spent more to grow &mdash; and lost money doing it</b>.", size=29),
  """One test per click. One team changes course for months 11 and 12 against an identical team on every default; six teams, ten default months first, events off (tools/deck/s12_tests.py). Score is the final score before decision quality, out of 90.

Stop all marketing: EBITDA improved by 1.17m over the two months, but month 12 sales fell 38%, the base shrank, and stock bought for last month's demand was left on the shelf (9,336 units against 3,780), so cash ended lower. Growth fell 8.3 points.
20% off: sales down 25% and 3.56m more lost; every pillar fell.
No more stock: sales down 37% as products ran out; cash 0.83m higher; growth and operations fell.
Prices 10% higher: a little more profit and customer value, a little less growth: nearly level.
Double the ad budgets: sales up 21% and 0.67m more lost; growth up 4.0 points.

The discussion: harvesting, fire sales and running the stock down were built to lose. Pushing for growth at a loss gained, because the scorecard puts twenty points on growth and eight on EBITDA. Would a real board make that trade in a business's last quarter? In its first?""",
  footer=SIM)

S["s12-sim-default"] = sec("s12-sim-default", "#f5f5f6", "In the simulation", "A team on every default: where the points went",
  "\n".join(num5(i + 1, 128 + i * 338, 290, 312, 330, lab, num, text) for i, (lab, num, text) in enumerate([
    ("Profitability", "23.2 / 25", "Close to the best, because in this test every team was the same."),
    ("Growth", "12.0 / 20", "Month 12 sales 15% above month 1; share barely moved."),
    ("Customer value", "10.8 / 20", "Lifetime value 1.8 times its cost; 34% of orders repeat."),
    ("Operations", "13.2 / 15", "95.6% of parcels delivered; stock turned 16 times a year."),
    ("Cash", "3.8 / 10", "PKR 9.7m of the starting cash gone by month 12."),
  ]))
  + "\n" + band(6, 680, 190, "Doing nothing scored <b>63 of 90</b> before decision quality. <b>Where did your team beat the default &mdash; and where did it fall below?</b>", size=30),
  """One pillar per click. The team on every default in the test world, months 1&ndash;12 (tools/deck/s12_tests.py).

The default is the benchmark the console's debrief cards compare against: a team that never changed a setting. In the test world all six teams were on the default, so the default team's margins were close to the best team's and profitability nearly full; in the Fall-2026 game the best team sets that bar.

Measure by measure: contribution before marketing 24.2% (12 of 12), EBITDA margin &minus;6.1% (6.2 of 8), gross margin 38.1% (5 of 5); month 12 net revenue 1.15&times; month 1 (5.7 of 8), share +0.13 points (3.7 of 7), orders 4% below the baseline business (2.7 of 5); lifetime value 1.76&times; its cost (2.6 of 6), repeat share 34.3% (2.2 of 5), 34,600 active customers (4.4 of 6), NPS 83 (1.6 of 3); service 100% (2 of 2), delivery success 95.6% (5.7 of 6), refusal and return costs 3.5% of revenue (3.3 of 4), stock turns 16.5 (2.3 of 3); runway (1.5 of 5), cash generated &minus;PKR 9.7m (0.5 of 3), net margin &minus;5.3% (1.7 of 2).

Runway is read in month 12 alone. The default team's operating cash flow was positive that month, which the engine reads as more than 16 months of runway, the band marked down for idle cash (30% of the runway points).

Use the console's results by round and each team's breakdown to show where each team's points came from.""",
  footer=SIM)

varrows = [("Board objective", "Your mandate", "Did you keep to it?", "When you left it, and why"),
           ("Net revenue, month 12", "Your target", "Every Measure", "Visits, conversion, basket or kept?"),
           ("Market share", "Your target", "MR-03, if bought", "Your moves, or your rivals&rsquo;?"),
           ("Repeat share", "Your target", "Every Measure", "Retention, service or deals?"),
           ("Cash at the end", "Your target", "The cash sheet", "Stock, loans or builds?"),
           ("Final rank", "Where you aimed", "The rankings", "The pillar that decided it")]
S["s12-sim-variance"] = sec("s12-sim-variance", "#ffffff", "In the simulation", "Plan against result",
  trows(["", "Your plan said", "Month 12", "Why the gap"], varrows, 276, [420, 320, 340, 528], rh=70, size=25, head_size=20)
  + "\n" + band(7, 770, 130, "Explain the gap, not just the number: <b>which decision, in which month, and what you would do differently</b>.", size=29),
  """One row per click. A frame for each team's variance analysis; the plan column comes from the founding round: the board objective (D0.1) and the business plan and targets (D0.14).

The variance is the most honest part of a presentation: a team that hit its targets should be able to say which decisions did it; a team that missed should be able to name the month it went wrong and what the report showed at the time.""")

S["s12-sim-present"] = sec("s12-sim-present", "#f5f5f6", "Your presentation", "Five slides, ten minutes",
  grid([
    ("1", "The plan", "Your objective and targets from month 0.", "#ed0000"),
    ("2", "What happened", "Results against the plan, in three numbers.", "#eb6834"),
    ("3", "What mattered", "Two decisions that worked, one that did not.", "#2a78d6"),
    ("4", "What you learned", "One number that surprised you, and why.", "#1baf7a"),
    ("5", "What next", "If the business had twelve more months.", "#8a6414"),
  ], 5, 290, 340, tsize=30, bsize=24)
  + "\n" + band(6, 680, 190, "Every claim on a slide needs a number from your reports. <b>What is the one sentence you want the room to remember?</b>", size=30),
  """One slide per click. A suggested structure for the team presentations; timings and order of teams for the notes, not the slide: [ten minutes a team, five for questions].

Slide 2 is the variance from the previous slide. Slide 3 should name the month and the report figure. Slide 5 is Part 1 applied: which growth route, what it would cost, what they would stop.""")

S["s12-sim-debrief"] = sec("s12-sim-debrief", "#131316", "The question", "Did you manage the business, or the scorecard?",
  grid([
    ("Where", "Where did the two come apart?", "A month when the right move for the business cost you points.", "#ff3b3b"),
    ("What", "What did you do?", "And what did it cost, in the report and the score?", "#ff3b3b"),
    ("Next time", "What would you do now?", "Knowing what the twelve months taught you.", "#ff3b3b"),
  ], 3, 300, 320, bg="#1f1f24", border="border:1px solid #33333b;", tcol="#ffffff", bcol="#c9c9d1")
  + "\n" + band(4, 680, 170, "A real business has no month 12. <b>The decisions that build it are the ones that would still look right a year later.</b>", bg="#ed0000", size=31),
  """The debrief question, for each team after its presentation and for the room at the end. One card per click.

Good answers name a specific month and decision: cutting brand spend to protect a margin, keeping stock cover through a cash squeeze, taking a loan to fund stock, a build committed late. The point is not that the scorecard was wrong but that every scorecard can be managed, and a founder has to decide which numbers to serve.""", dark=True, eyecol="#ff3b3b")

S["s12-close"] = sec("s12-close", "#131316", "The course", "What you take with you",
  grid([
    ("Sessions 1&ndash;3", "The idea and the money", "A real problem, a customer, and a margin that works.", "#ff3b3b"),
    ("Sessions 4&ndash;6", "The store and the offer", "The shop, the range, the price and the trust.", "#ff3b3b"),
    ("Sessions 7&ndash;8", "Customers", "Winning them at a cost, and keeping them.", "#ff3b3b"),
    ("Sessions 9&ndash;12", "Running it", "Delivery, cash, the numbers, AI and growth.", "#ff3b3b"),
  ], 4, 300, 320, bg="#1f1f24", border="border:1px solid #33333b;", tcol="#ffffff", bcol="#c9c9d1")
  + "\n" + band(5, 680, 170, "An online business is a chain: <b>product, price, traffic, conversion, delivery, cash</b>. Find the weakest link, and strengthen it first.", bg="#ed0000", size=31),
  """Close of the course. One block per click.

The chain is the course in one sentence: each session strengthened one link, and the simulation showed that the weakest one sets the result. Thank the teams; point them to their final reports and workbook for the record of their twelve months.""", dark=True, eyecol="#ff3b3b")

ORDER = ["s12-cover", "s12-recall", "s12-ex1", "s12-part1", "s12-routes", "s12-ready", "s12-channels",
         "s12-case-channels", "s12-markets", "s12-case-markets", "s12-funding", "s12-funding-ex",
         "s12-case-funding", "s12-lasting", "s12-ex2", "s12-part2", "s12-category", "s12-sim-scorecard",
         "s12-sim-weights", "s12-sim-endgame", "s12-sim-default", "s12-sim-variance", "s12-sim-present",
         "s12-sim-debrief", "s12-close"]
SECTIONS = {
    "s12-open": {"description": "Session 12 · How do you grow?", "start": "s12-cover"},
    "s12-routes": {"description": "Part 1 · Growth routes, readiness and channels, with cases", "start": "s12-part1"},
    "s12-markets": {"description": "New markets and paying for growth, with cases", "start": "s12-markets"},
    "s12-sim": {"description": "Part 2 · The final scorecard and your presentation", "start": "s12-part2"},
    "s12-end": {"description": "The debrief question and the course", "start": "s12-sim-debrief"}}

if __name__ == "__main__":
    write(S, ORDER, "Session 12 — How Do You Grow?", SECTIONS)
