"""Session 9 - How Will You Deliver the Order? About 27 slides.

Run: python s9_slides.py <deck folder> [logo url]
Part 2's numbers come from tools/deck/s9_tests.py.
"""
import pathlib, sys, json
HERE = pathlib.Path(__file__).parent
exec((HERE / "s7_slides.py").read_text().split("\nS = {}\n")[0])
FT = "Session 9 &middot; How Will You Deliver the Order?"
def sec(sid, bg, eyebrow, title, body, notes, footer=FT, **kw):
    return section(sid, bg, "#131316", eyebrow, title, body, notes, footer=footer, **kw)
def div(sid, part, title, line, notes):
    return divider(sid, part, title, line, notes).replace("Session 2 &middot; Finding the Right Idea", FT).replace("856d57cb939a323d46943b3b229572d7", "__LOGO__")

S = {}
S["cover"] = cover(9, "How Will You<br>Deliver the Order?",
  "Stock, suppliers, warehouses, couriers, cash on delivery and returns &mdash; getting the order to the door without running out of cash.",
  """Two hours, about 27 slides: 3 min recap, 8 min opening exercise, Part 1 theory about 65 min (the order's journey 5, how much stock 15, suppliers 10, stock that will not sell 10, fulfilment 10, couriers and cash on delivery 15), exercise 10, Part 2 simulation about 30 min, 3 min close.

Month 7 has run. Today's decisions open for month 8: 7.1 stock to purchase, 7.2 supplier, 7.4 quality assurance, 7.5 safety stock, 7.6 return stock to supplier (where the game offers it), 8.2 3PL share, 8.3 courier mix, 9.1 cash on delivery, 9.2 discount for paying online.

The idea for the day: in Pakistani e-commerce the order is not won when it is placed; it is won when the cash reaches you. Stock, couriers and cash on delivery decide how much of what you sell you actually keep.""")

S["recall"] = sec("recall", "#f5f5f6", "Where we got to last week", "Customers come back when the experience works",
  grid([
    ("Experience", "The first retention tool", "Product as promised, on time, fast answers, fair returns.", "#ed0000"),
    ("Messages", "Useful at the right moment", "Order updates, replenishment reminders, win-back.", "#eb6834"),
    ("CRM", "Treat customers differently", "Group them by when, how often and how much they buy.", "#2a78d6"),
  ], 3, 300, 300)
  + "\n" + band(4, 660, 170, "Last week: <b>why customers stay</b>. Today: <b>the part of the experience that loses most of them</b> &mdash; the parcel, and whether it arrives.", size=31),
  """Three quick clicks from Session 8.

The bridge: a late, damaged or refused parcel undoes every ad and every WhatsApp message. Operations is where the promise is kept or broken, and in Pakistan it is also where the cash is.""")

S["ex1"] = exercise("ex1", "Exercise 1", "Your last parcel",
  "Think of the last thing you ordered online and had delivered.",
  ["How long did it take, and did you know when it would come?", "Did you pay at the door &mdash; and why?",
   "Have you ever refused a parcel? What happened?", "What would make you pay online in advance?"],
  "Exercise 1 &middot; the order is not done until the cash is in",
  """Eight minutes. One question per click; take a show of hands for questions 2 and 3.

Question 2 is the heart of the session: expect most of the room to pay cash on delivery, for trust ("I see it before I pay"), habit and fear of fraud.

Question 3 brings out refusals: changed mind, ordered from two shops and took the first, not at home, price looked different, or the parcel took too long. Each one cost the seller a courier trip both ways.

Question 4 is the lever: a discount, a trusted brand, a wallet they already use, or a guarantee of easy refunds.""", top=500, h=180, cols=2)

S["part1"] = div("part1", "Part 1 &middot; Theory", "From order<br>to doorstep",
  "Stock, suppliers, stock that will not sell, warehouses, couriers and cash on delivery &mdash; each with a Pakistani and a global case.",
  """Part 1 follows the course outline: how the order reaches the customer, in the order the money moves. Real-world practice only; the simulation is Part 2.""")

S["journey"] = sec("journey", "#ffffff", "The order's journey", "Four steps between the click and the cash",
  grid([
    ("Stock", "Is it on the shelf?", "Bought weeks earlier, from a supplier, with cash paid before it sells.", "#ed0000"),
    ("Warehouse", "Picked, packed, labelled", "Your own store-room or a third-party warehouse (3PL).", "#eb6834"),
    ("Courier", "Out to the door", "Speed, reliability and reach &mdash; and a cost on every parcel.", "#2a78d6"),
    ("Cash", "Collected and paid to you", "Online now; cash on delivery when the courier remits it.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "Every step can fail, and every step <b>holds your cash</b> a little longer. Which step fails most often for the brands you buy from?", size=30),
  """One step per click.

The point of the slide: money leaves at step one (the supplier is paid) and comes back at step four (the customer's cash reaches you). Everything in between is time your cash is tied up, and every failure in between &mdash; a stock-out, a lost parcel, a refusal &mdash; is cost with no revenue.""")

S["stock"] = sec("stock", "#f5f5f6", "How much stock", "Too little loses sales; too much loses cash",
  two(1, 128, 280, 819, 300, "Too little", "You run out",
      ["Lost orders, and customers who go to a rival", "Ads paid for visitors who could not buy", "Ranking falls on marketplaces when out of stock"], "#ed0000")
  + "\n" + two(2, 973, 280, 819, 300, "Too much", "Cash sits on a shelf",
      ["Supplier paid for stock that has not sold", "Storage and handling every month", "Old stock ages, expires or goes out of fashion"], "#2a78d6")
  + "\n" + band(3, 600, 270, "Two numbers run stock: <b>weeks of cover</b> = stock &divide; a week's sales, and the <b>reorder point</b> = sales during the supplier's lead time + a safety buffer. Order when stock falls to it. <b>How many weeks of cover does your best seller have today?</b>", size=29),
  """Two clicks, then the band.

Weeks of cover tells you how long stock will last at the current rate of sale. The reorder point tells you when to order so the new stock lands before the old runs out: the sales you expect while the order is on its way, plus a safety buffer for forecasts that miss and suppliers that run late.

The buffer is a trade-off, not a rule: more buffer, fewer stock-outs and more cash tied up. Fast sellers deserve more attention than slow ones; many brands find most of their sales come from a small share of their products.""")

reorder = [("Sales a week", "500 units", "From last month's sales, adjusted for any campaign coming"),
           ("Supplier lead time", "2 weeks", "Order to arrival on your shelf"),
           ("Sales during the lead time", "1,000 units", "500 &times; 2"),
           ("Safety buffer", "500 units", "One week of sales, for a forecast that misses"),
           ("Reorder point", "1,500 units", "Order when stock falls to this")]
S["reorder"] = sec("reorder", "#ffffff", "When to order", "Working out the reorder point",
  trows(["", "Example", "Where it comes from"], reorder, 276, [480, 340, 788], rh=76, size=27)
  + "\n" + band(6, 700, 170, "A supplier with a <b>4-week</b> lead time needs a reorder point of 2,500 units &mdash; and 1,000 more units of cash on the shelf. <b>Cheaper stock from far away is not cheaper if you must hold more of it.</b>", size=28),
  """Illustrative numbers. One row per click.

The calculation every team can do: weekly sales times lead time, plus a buffer. The band shows why lead time is a cost: doubling it doubles the stock in the pipeline and the cash tied up in it, which can wipe out a lower unit price.""",
  footer="Illustrative numbers")

S["cash"] = sec("cash", "#f5f5f6", "Stock is cash", "How long your cash is tied up",
  row4([
    ("Stock waits", "60 days", "from arriving on your shelf to being sold."),
    ("Cash on delivery", "+16 days", "until the courier pays you the cash it collected."),
    ("Supplier credit", "&minus;45 days", "you pay the supplier this long after stock arrives."),
    ("Cash tied up", "31 days", "of sales, financed by you or by a loan."),
  ], 290, 340)
  + "\n" + band(5, 700, 170, "This is the <b>cash conversion cycle</b>. Growing fast makes it bite harder: every extra rupee of monthly sales needs about a month of cash first. <b>What would shorten yours?</b>", size=29),
  """Illustrative numbers. One box per click.

Days of stock plus days to collect from customers, minus days of credit from suppliers: the number of days of sales a business must finance itself. Shorter stock holding, faster collection (prepaid, faster couriers) and longer supplier terms all shrink it.

This is how a profitable business runs out of cash: sales grow, and each month's extra sales need stock paid for before the cash comes back.""",
  footer="Illustrative numbers")

S["suppliers"] = sec("suppliers", "#ffffff", "Suppliers", "Choosing who makes your stock",
  grid([
    ("Cost", "Price a unit", "The obvious number &mdash; and only one of four.", "#ed0000"),
    ("Lead time", "Order to shelf", "Longer means more stock in the pipeline and more risk.", "#eb6834"),
    ("Minimum order", "The smallest batch", "A big minimum makes a small brand buy more than it sells.", "#2a78d6"),
    ("Reliability", "Quality and on time", "A cheap batch that arrives late or faulty costs the most.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "Local suppliers: dearer, faster, smaller batches. Imports: cheaper, slower, exposed to <b>ports, currency and policy</b>. Which risk can your cash carry?", size=30),
  """One factor per click.

Total cost is what matters: unit price plus the stock you must hold because of the lead time and the minimum order, plus the cost of faults and delays. Many brands split: a cheap, slow supplier for steady sellers and a fast, local one for new or unpredictable lines.""")

S["case-supply"] = cases("case-supply", "Cases &middot; Suppliers", "Lead time is a risk as well as a cost",
  ("Pakistan", "Importers", "2022", [
    ("The squeeze", "From May 2022 the State Bank restricted letters of credit for many imports to save dollars."),
    ("The cost", "By November, 2,800 containers sat at Port Qasim alone; for some goods, port charges passed their value.")]),
  ("Global", "Zara", "Inditex, Spain", [
    ("The model", "Factories near Spain; new designs from studio to store in about three weeks."),
    ("The bet", "Only part of a season is made in advance; the rest follows what is selling.")]),
  "One shows the risk of a long, far supply chain; the other pays more per unit to <b>buy closer to what sells</b>.",
  """Two supply cases.

Pakistani importers, 2022: in May 2022 the State Bank of Pakistan restricted the opening of letters of credit for imports in several tariff chapters to curb dollar outflows, and banks delayed others as dollars ran short. A Senate panel was told in November 2022 that 2,800 containers were stuck at Port Qasim, mostly because letters of credit could not be opened; other estimates for Karachi ran higher. Importers of pulses and vegetables reported shortages and demurrage charges exceeding the value of the goods. Restrictions were eased from late December 2022.

Zara (Inditex): makes much of its range in factories it owns or works closely with in and near Spain, and is reported to take new designs from studio to store in under three weeks (Harvard Business School summary). It commits only part of a season's production in advance and makes the rest in small batches as sales show what customers want. Per unit it pays more than far-off suppliers; it holds less stock that will not sell.

The lesson: a cheap, distant supplier is a bet that nothing goes wrong for weeks. A dearer, closer one buys speed and the right to change your mind.

Sources: ProPakistani (Nov 2022); Dawn; Aaj News; Harvard Business School Digital Initiative (Inditex).""",
  "Sources: ProPakistani (Nov 2022), Dawn, Aaj News; HBS Digital Initiative (Inditex)")

S["deadstock"] = sec("deadstock", "#f5f5f6", "Stock that will not sell", "Four ways out, all of them costly",
  grid([
    ("Stop buying", "Let it sell down", "The cheapest fix if it will sell within a few months.", "#ed0000"),
    ("Clear it", "Discount or bundle", "Cash back now, at a lower margin &mdash; and a lower price customers remember.", "#eb6834"),
    ("Return it", "Back to the supplier", "Some cash back, less a restocking fee &mdash; if the supplier agrees.", "#2a78d6"),
    ("Write it off", "Donate or destroy", "No cash, but no more storage or ageing.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "First <b>stop buying</b>. Return or clear only what will not sell before it ages &mdash; a fee on stock that would have sold is money thrown away.", size=30),
  """One option per click.

Excess stock is a sunk cost; the decision is only about the cash and costs from here. Compare what each route brings back with what holding costs (storage, handling, ageing) until it would sell.

Returning to the supplier usually carries a restocking fee, often a large share of the cost, because the supplier must check, store and resell it. It makes sense for stock that would otherwise sit for many months or expire; it is a poor deal for stock that would have sold next month.""")

S["case-stock"] = cases("case-stock", "Cases &middot; Too much, too fast", "When stock and capacity outrun the cash",
  ("Pakistan", "Airlift", "Lahore, 2019&ndash;2022", [
    ("The growth", "Thirty-minute grocery delivery; raised US$85m in 2021 at a US$275m valuation."),
    ("The end", "Pulled out of cities in May 2022 and shut in July when new funding did not arrive.")]),
  ("Global", "H&amp;M", "Sweden, 2018", [
    ("The pile", "Reported about US$4.3bn of unsold clothes in March 2018 after its first sales fall in years."),
    ("The fix", "Price cuts to clear it, slower store openings and a push online.")]),
  "Stock and warehouses are paid for <b>before</b> they earn &mdash; growth needs the cash to carry them.",
  """Two cases about carrying too much.

Airlift: the Lahore quick-commerce company delivered groceries and essentials in about 30 minutes in eight Pakistani cities. In August 2021 it raised US$85 million, then Pakistan's largest Series B, at a US$275 million valuation. Delivering in 30 minutes means holding stock in many small warehouses close to customers. In May 2022 it pulled out of several cities and South Africa; on 12 July 2022 it shut down, saying investors had delayed funding amid a global downturn. Inflation and fuel prices also squeezed demand and costs.

H&amp;M: in its quarterly report of 27 March 2018 the retailer disclosed about US$4.3 billion of unsold clothing and accessories, after an unexpected fall in quarterly sales. It planned price cuts to clear stock, fewer new stores and more online growth.

The lesson: stock and capacity are bought ahead of sales. When sales or funding fall short, they become cash a business cannot get back.

Sources: TechCrunch, Dawn and ProPakistani (Jul 2022); NPR and Supply &amp; Demand Chain Executive (Mar 2018).""",
  "Sources: TechCrunch, Dawn, ProPakistani (2022); NPR (Mar 2018)")

S["fulfil"] = sec("fulfil", "#ffffff", "Fulfilment", "Your own warehouse, or someone else's",
  two(1, 128, 280, 819, 380, "Own warehouse", "Control, fixed cost",
      ["You pick, pack and check every order", "Fixed rent and staff, busy or not", "Hard to grow fast before a sale"], "#ed0000")
  + "\n" + two(2, 973, 280, 819, 380, "Third-party (3PL)", "Flexible, cost per order",
      ["Pay per order and per shelf", "Capacity for peaks and other cities", "Less control over packing and errors"], "#2a78d6")
  + "\n" + band(3, 690, 180, "Many brands keep their own store-room for steady volume and use a 3PL or a marketplace's warehouse <b>for peaks and far cities</b>. Where would your orders queue first?", size=29),
  """Two clicks, then the band.

A 3PL turns a fixed cost into a variable one and adds capacity quickly, at a higher cost per order and with less control. Marketplaces offer their own version (Fulfilment by Daraz, Fulfillment by Amazon), which also makes products eligible for faster delivery badges.""")

S["case-fulfil"] = cases("case-fulfil", "Cases &middot; Fulfilment", "Let the marketplace hold the stock",
  ("Pakistan", "Daraz", "Fulfilment by Daraz", [
    ("The service", "Daraz stores, picks, packs and ships sellers' stock from its warehouses in Karachi, Lahore and Islamabad."),
    ("The terms", "Stock stays the seller's; storage free for 30 days, then charged.")]),
  ("Global", "Amazon", "Fulfillment by Amazon, 2006", [
    ("The service", "Sellers send stock to Amazon's warehouses; Amazon packs, ships and handles service."),
    ("The pull", "Their products became eligible for Prime and free shipping offers.")]),
  "Both rent out <b>their warehouses and delivery</b> &mdash; and charge more the longer stock sits.",
  """Two fulfilment cases.

Fulfilment by Daraz (FBD): Daraz's seller material describes an end-to-end service in which Daraz stores, picks, packs and ships a seller's products from fulfilment centres in Karachi, Lahore and Islamabad. It is a consignment model: ownership stays with the seller. Storage is free for the first 30 days and charged after that; eligibility depends on seller rating and return rates (terms change; check Seller Center).

Fulfillment by Amazon (FBA): launched on 19 September 2006. Sellers send stock to Amazon's warehouses and Amazon handles packing, shipping and customer service; their products could carry Prime and free-shipping offers. Fees are per unit handled and per unit of space per month, with higher charges for long-stored stock.

The lesson: a marketplace warehouse buys speed and badges for a fee per order and per day &mdash; a strong reason not to send it more stock than will sell.

Sources: Daraz seller materials; Amazon press release (Sep 2006); Marketplace Pulse.""",
  "Sources: Daraz seller materials; Amazon press release (2006); Marketplace Pulse")

S["couriers"] = sec("couriers", "#f5f5f6", "The last mile", "Choosing couriers",
  grid([
    ("Speed", "Days to the door", "Faster delivery means fewer changed minds at the door.", "#ed0000"),
    ("Success", "Delivered first time", "Every failed attempt is a trip back and a lost sale.", "#eb6834"),
    ("Reach", "Small towns too", "Some couriers are strong in cities, others outside them.", "#2a78d6"),
    ("Cash", "When they pay you", "Cash on delivery comes back days or weeks later.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "Most brands use <b>more than one courier</b>: the fast one for big cities, the wide one for small towns. What does a failed delivery cost you?", size=30),
  """One factor per click.

Pakistani brands commonly use TCS, Leopards, M&amp;P, Trax, BlueEx or PostEx, often more than one. The cheapest rate per parcel is rarely the cheapest courier once failed deliveries, refusals and slow cash remittance are counted.""")

S["cod"] = sec("cod", "#ffffff", "Cash on delivery", "Trust for the customer, risk for the seller",
  grid([
    ("Why", "The customer sees it first", "Most Pakistani online shoppers prefer to pay at the door.", "#ed0000"),
    ("Refusals", "The parcel comes back", "Changed minds and fake orders: shipped twice, sold never.", "#eb6834"),
    ("Cash", "Arrives later", "The courier pays you after it collects &mdash; often a week or two.", "#2a78d6"),
    ("Fixes", "Confirm, reward, collect", "Confirm by call or WhatsApp; reward paying online; take an advance.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "Cash on delivery wins orders you would not get otherwise &mdash; <b>and charges for them in refusals and waiting</b>. Which orders would you ask to pay first?", size=30),
  """One card per click.

Why: DHL Pakistan says nearly 70% of online shoppers in Pakistan prefer cash on delivery. Refusals: seller-tool vendors report return-to-origin rates of 25&ndash;30% or more for cash-on-delivery orders in Pakistan; there is no official figure, so treat these as indicative. Cash: traditional couriers remit cash-on-delivery money after a cycle (vendors cite 10&ndash;15 days); some services now advance it.

Fixes: confirm orders before dispatch, block repeat refusers, offer a discount or free delivery for paying online, take a small advance on high-value orders, and deliver faster.

Sources: DHL Pakistan; Simpaisa and other vendor estimates (2026).""",
  footer="Sources: DHL Pakistan; vendor estimates (2026) &middot; indicative")

S["case-cod"] = cases("case-cod", "Cases &middot; Cash on delivery", "Making cash on delivery work",
  ("Pakistan", "PostEx", "Lahore, 2021", [
    ("The problem", "Sellers wait for cash-on-delivery money, and banks will not lend against parcels."),
    ("The answer", "Delivers parcels and advances the cash before collection; raised US$8.6m in seed funding.")]),
  ("Global", "Flipkart", "India, 2010", [
    ("The problem", "Few Indians used cards, and shoppers did not trust paying a website in advance."),
    ("The answer", "Built its own delivery and offered cash on delivery with easy replacements.")]),
  "One made cash on delivery <b>possible</b> for shoppers; the other made it <b>bearable</b> for sellers.",
  """Two cash-on-delivery cases.

PostEx: a Lahore fintech and logistics start-up that delivers e-commerce parcels and advances sellers the cash for cash-on-delivery orders before it is collected, underwriting from their sales data. Its founder Muhammad Omer Khan has argued that banks will not lend to e-commerce sellers because they lack collateral. It announced a US$1.5 million seed round in October 2021 (led by MSA Capital); Bloomberg later reported US$8.6 million raised across seed tranches.

Flipkart: when it began, few Indians used cards. Around 2010 it built its own delivery arm and offered cash on delivery, alongside a 30-day replacement policy, which is widely credited with building trust in Indian online shopping (it popularised cash on delivery at scale; it was not the only one to offer it).

The lesson: cash on delivery is what brings many South Asian shoppers online; the businesses that win are the ones that make its costs &mdash; waiting and refusals &mdash; smaller.

Sources: Profit (Pakistan Today) and ProPakistani (Oct 2021); BNN Bloomberg; Bloomberg (2014); YourStory.""",
  "Sources: Profit, ProPakistani (2021); BNN Bloomberg; Bloomberg (2014); YourStory")

refused = [("Courier out", "Rs 180", "Paid whether it is delivered or not"),
           ("Courier back", "Rs 180", "The parcel returns to you"),
           ("Packing and handling", "Rs 60", "Box, label, staff time, twice"),
           ("Damaged or unsellable", "Rs 120", "Some returned stock cannot be sold again"),
           ("A refused parcel costs", "Rs 540", "And the sale never happened")]
S["refusal"] = sec("refusal", "#f5f5f6", "What a refusal costs", "Every refused parcel is paid for twice",
  trows(["On a Rs 2,000 order", "Cost", "Why"], refused, 276, [520, 300, 788], rh=76, size=27)
  + "\n" + band(6, 700, 170, "At one refusal in four cash-on-delivery orders, a Rs 100 discount for paying online <b>pays for itself</b> if it moves enough buyers. <b>What would your break-even be?</b>", size=28),
  """Illustrative numbers. One row per click.

The cost of a refusal is the courier both ways, packing and handling twice, and stock that comes back damaged &mdash; with no sale to show for it.

Break-even for a prepaid discount: compare the discount paid on every prepaid order with the refusal costs it saves on orders that would otherwise have been cash on delivery and refused. Customers who already prepay get the discount too, which is the hidden cost.""",
  footer="Illustrative numbers")

S["plan"] = sec("plan", "#ffffff", "The operations plan", "An operations plan on one page",
  grid([
    ("Forecast", "Sales a week, by product", "From last month, adjusted for campaigns and seasons.", "#ed0000"),
    ("Stock", "Cover and reorder point", "How many weeks to hold; when to order.", "#eb6834"),
    ("Supplier", "Cost, lead time, minimum", "And a back-up for when the first one fails.", "#2a78d6"),
    ("Fulfilment", "Own, 3PL or marketplace", "Capacity for your busiest month.", "#1baf7a"),
    ("Delivery", "Courier mix", "Speed, success and reach for your customers.", "#8a6414"),
    ("Payment", "COD rules and returns", "Who prepays, when to confirm, what to do with stock that will not sell.", "#6b4fbb"),
  ], 3, 290, 250)
  + "\n" + band(7, 830, 80, "The plan is judged by one number: how much of what you sell becomes cash in your account.", size=28, extra="padding:18px 40px;"),
  """One box per click.

Forecast, stock policy, supplier, fulfilment, couriers, payment and returns. Each part has a measure: forecast error, weeks of cover and stock-outs, supplier on-time rate, orders shipped on time, delivery success, refusal rate and days to collect cash.""")

S["ex2"] = exercise("ex2", "Exercise 2", "Plan the first month of deliveries",
  "A new Pakistani skincare brand expects 1,500 orders next month at Rs 2,000 each, mostly cash on delivery.",
  ["How much stock do you buy, and from whom?", "Which courier, or couriers, and why?",
   "Which orders do you confirm before you ship?", "What do you do with stock left after a slow month?"],
  "Exercise 2 &middot; an operations plan",
  """Ten minutes in teams. One question per click. The brand is hypothetical.

Push question 1 to a number: weekly sales times lead time plus a buffer, rounded up to the supplier's minimum order. Push question 4 to the order of options: stop buying first, then clear or return only what will not sell before it ages.

Take two teams' plans.""", top=500, h=180, cols=2)

S["part2"] = div("part2", "Part 2 &middot; The simulation", "Operations open",
  "For month 8: stock, supplier, quality assurance, safety stock, returns to the supplier, 3PL, couriers, cash on delivery and the online-payment discount.",
  """Part 2 is the simulation. Month 7 has run. For seven months the engine has bought stock, chosen couriers and handled payment on defaults; from month 8 those decisions are the teams'.

Every number in Part 2 is the simulation's assumption or a test run of it, not market data.""")

S["category"] = sec("category", "#f5f5f6", "The category online", "How personal care is delivered in Pakistan",
  grid([
    ("Payment", "Cash at the door", "Nearly 70% of online shoppers prefer cash on delivery (DHL Pakistan).", "#ed0000"),
    ("Refusals", "A large share comes back", "Vendors put cash-on-delivery returns at 25&ndash;30% or more.", "#eb6834"),
    ("Warehouses", "Marketplaces hold stock", "Daraz fulfils from Karachi, Lahore and Islamabad.", "#2a78d6"),
    ("Cash", "Advances on parcels", "PostEx pays sellers before the cash is collected.", "#1baf7a"),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "The simulation's teams sell personal care and home care online in Pakistan. <b>How much of your month-7 revenue became cash?</b>", size=30),
  """The real category first. One card per click.

Payment: DHL Pakistan. Refusals: seller-tool vendors (Simpaisa, 2026) &mdash; indicative, no official figure. Warehouses: Daraz seller materials (Fulfilment by Daraz). Cash: PostEx (Profit, ProPakistani, 2021).""",
  footer="Sources: DHL Pakistan; vendor estimates (2026); Daraz seller materials; Profit (2021)")

S["sim-stock"] = sec("sim-stock", "#ffffff", "In the simulation", "How stock and suppliers work in the simulation",
  grid([
    ("Stock (7.1, 7.5)", "Leave it blank and it orders for you", "It buys to your safety cover (default 3 weeks), as far as cash allows. Holding costs 2.1% of stock value a month; cover past 6 months is written down 10% a month.", "#ed0000"),
    ("Suppliers (7.2)", "A, B or C", "A: 12% cheaper, 21 days, minimum 5,000 units. B: baseline, 14 days, 2,000. C: 9% dearer, 7 days, 500. Paid 45 days after ordering.", "#eb6834"),
    ("Quality (7.4)", "Inspection before it ships", "Quality assurance cuts returns and lifts ratings, best from about Rs 250k a month.", "#2a78d6"),
    ("Returns (7.6)", "Back to the supplier", "Name the units product by product; the supplier keeps half the cost; half comes back in cash.", "#1baf7a"),
  ], 4, 290, 450, bsize=23)
  + "\n" + band(5, 780, 100, "<b>The default since month 1:</b> automatic orders to 3 weeks of cover, supplier B, QA Rs 80k a month.", size=28),
  """One rule per click. The rules are the simulation's.

Stock: with 7.1 blank, the engine orders to cover the forecast plus the safety cover in 7.5, as far as cash and the approved loan go; since 22 October the form shows the units it will buy before the month runs. A number in 7.1 is a total split by what sold; product by product is allowed. Stock bought is paid on 45-day supplier terms.

Suppliers: cost index 0.88 / 1.00 / 1.09; lead time 21 / 14 / 7 days; minimum order 5,000 / 2,000 / 500 units; quality index 0.86 / 0.92 / 0.95. In the full game a supply shock in month 5 hits suppliers A and B (not C).

Returns (7.6): in games that offer it. The supplier keeps 50% of landed cost.

These are the simulation's assumptions; real founders get them from supplier quotes and their own records.""",
  footer="Decision rules from the simulation &middot; not market data")

S["sim-deliver"] = sec("sim-deliver", "#f5f5f6", "In the simulation", "How delivery and payment work in the simulation",
  grid([
    ("Couriers (8.3)", "Three, in any mix", "Speed: 97.5% delivered, Rs 210, cash in 12 days. Value: 94.0%, Rs 145, 21 days. Wide: 95.8%, Rs 175, 16 days, best in small towns.", "#ed0000"),
    ("3PL (8.2)", "Extra capacity", "Each 100% through the 3PL adds 4,000 orders a month of capacity, at Rs 30 more an order.", "#eb6834"),
    ("Cash on delivery (9.1)", "62% of orders", "18% of cash-on-delivery parcels are refused, more when deliveries are late. Off: no refusals, fewer orders.", "#2a78d6"),
    ("Pay online (9.2)", "A discount for prepaying", "Fewer choose cash on delivery and fewer refuse &mdash; but every prepaid order gets the discount.", "#1baf7a"),
  ], 4, 290, 450, bsize=23)
  + "\n" + band(5, 780, 100, "<b>The default since month 1:</b> 30% Speed, 40% Value, 30% Wide; 40% through 3PL; cash on delivery on; 3% off for paying online.", size=28),
  """One rule per click. The rules are the simulation's.

Couriers: delivery success is each courier's success rate weighted by the mix; failed deliveries ship both ways. Cash-on-delivery money arrives after each courier's remittance days.

Cash on delivery: about 62% of orders choose it when it is on; 18% of those are refused at base, rising when orders exceed delivery capacity. The discount for paying online moves buyers to prepaying and lowers refusals on what remains.

These are the simulation's assumptions.""",
  footer="Decision rules from the simulation &middot; not market data")

tests9 = [("All default (its own EBITDA)", "95.6%", "0.83m", "2.30m &middot; 0", "&minus;2.09m"),
          ("Supplier A &nbsp;(cheap, slow)", "95.6%", "0.83m", "3.89m &middot; 0", "+3.28m"),
          ("Supplier C &nbsp;(dear, fast)", "95.6%", "0.83m", "1.68m &middot; 0", "&minus;2.45m"),
          ("Safety stock 8 weeks", "95.6%", "0.83m", "0 &middot; 5.02m", "&minus;0.50m"),
          ("All Speed Express", "97.5%", "0.85m", "2.02m &middot; 0", "&minus;0.53m"),
          ("Cash on delivery off", "95.6%", "0.26m", "2.74m &middot; 0", "&minus;1.84m"),
          ("10% off for paying online", "95.6%", "0.48m", "0.55m &middot; 0", "&minus;3.69m")]
S["sim-tests"] = sec("sim-tests", "#ffffff", "In the simulation", "What one change did, month 8 to month 12",
  trows(["Test, kept from month 8", "Delivered", "Refusal cost", "Cash &middot; owed, m12", "EBITDA vs default"], tests9, 276,
        [520, 230, 260, 330, 268], rh=70, size=26)
  + "\n" + band(8, 790, 100, "Cash on delivery off: refusals almost vanish &mdash; and <b>8% of orders go with them</b>. Which line is your team?", size=28),
  """One test per click. Each line is one team changing one decision from month 8 and keeping it, against an identical team on every default (six teams, seven default months first, events off). EBITDA is months 8 to 12; the first line is the default's own EBITDA, the others the difference from it.

Supplier A: 12% cheaper stock added 3.3m of EBITDA in this test, with events off. In the full game a month-5 supply shock hits A and B; a cheap, slow supplier is a bet that nothing goes wrong.

Safety stock 8 weeks: no extra sales (these teams were not running out), 0.5m more holding cost, and 5m owed to the bank by month 12.

All Speed Express: delivery success up 1.9 points (scored under operations) for 0.5m. Cash on delivery off: refusal costs fell by two-thirds, but 8% fewer orders and 1.8m less EBITDA. 10% off for paying online: refusals halved, but the discount on every prepaid order cost 3.7m.

Results depend on each team's stock, customers and cash; these are directions, not forecasts.""",
  footer="Simulation test run, six teams, months 8&ndash;12, events off &middot; not market data")

over = [("Keep 8 weeks of cover", "12,967", "0 &middot; 5.02m", "&minus;1.98m"),
        ("Back to 3 weeks", "4,537", "2.56m &middot; 1.30m", "&minus;1.66m"),
        ("Back to 3 weeks + return half", "4,397", "2.10m &middot; 1.49m", "&minus;2.04m")]
S["sim-returns"] = sec("sim-returns", "#f5f5f6", "In the simulation", "Too much stock: stop buying before you return it",
  trows(["Overstocked in month 8, then from month 9", "Stock, m12", "Cash &middot; owed, m12", "EBITDA, 9&ndash;12"], over, 276,
        [640, 280, 380, 308], rh=80, size=27)
  + "\n" + band(4, 620, 250, "Cutting cover back let the stock sell down. Returning half as well <b>lost half its cost</b> &mdash; and the automatic order then bought stock again at full price. <b>Return only stock that will not sell before it ages.</b>", size=29),
  """One line per click. A team overstocks in month 8 (8 weeks of safety cover); from month 9 it either keeps that cover, cuts it back to 3 weeks, or cuts it back and also returns half its stock to the supplier (7.6).

Cutting cover back is best: the engine stops buying until stock sells down, cash recovers and borrowing falls. Returning half as well is worse than doing nothing: the supplier keeps half the cost, the shelf falls below the new cover, and the automatic order buys again at full price.

Returns pay for stock that would sit past six months (where the 10% monthly write-down starts) or that no longer sells at all &mdash; not for a few weeks too much.""",
  footer="Simulation test run, six teams, months 8&ndash;12, events off &middot; not market data")

S["checks"] = sec("checks", "#fdeceb", "Before month 8 runs", "Four questions before you decide",
  grid([
    ("Stock", "How many weeks of cover?", "Check each product in your report; fast sellers first.", "#ed0000"),
    ("Cash", "Can you pay for it?", "Stock is paid 45 days after you order it. Check your runway.", "#eb6834"),
    ("Delivery", "Which couriers, and why?", "Delivered rate against cost per parcel and cash timing.", "#2a78d6"),
    ("Payment", "Who should pay first?", "Cash on delivery wins orders; refusals cost you twice.", "#1baf7a"),
  ], 4, 300, 340)
  + "\n" + band(5, 700, 150, "Name in the board memo the number in month 8's report that will tell you <b>whether your operations worked</b>.", size=30),
  """One question per click, while teams fill in the decision form.

Logistics for the notes, not the slide: decisions for month 8 close at [deadline]. Open this round: 7.1, 7.2, 7.4, 7.5, 7.6 (where offered), 8.2, 8.3, 9.1, 9.2, plus everything opened earlier. The month-8 report shows stock by product with weeks of cover, delivery success, refusals, cash flow and money owed.""")

S["next"] = sec("next", "#131316", "Next session", "Is your business working?",
  grid([
    ("Session 10", "No new decisions", "The report and the research desk are the session.", "#ff3b3b"),
    ("Your numbers", "Which ones can you trust?", "Platforms over-count; research has error bars.", "#ff3b3b"),
    ("Your operations", "Did the cash come in?", "Month 8's cash flow and refusals are the test.", "#ff3b3b"),
  ], 3, 300, 300, bg="#1f1f24", border="border:1px solid #33333b;", tcol="#ffffff", bcol="#c9c9d1")
  + "\n" + band(4, 660, 150, "Today: getting the order to the door and the cash back. Next time: <b>reading the numbers to know whether it is all working</b>.", bg="#ed0000", size=31),
  """Close. One card per click.

Session 10 opens no new levers: the whole session is the monthly report, the research desk and its studies &mdash; which numbers can be trusted, which are biased, and what platforms over-report.""", dark=True, eyecol="#ff3b3b")

ORDER = ["cover", "recall", "ex1", "part1", "journey", "stock", "reorder", "cash", "suppliers", "case-supply",
         "deadstock", "case-stock", "fulfil", "case-fulfil", "couriers", "cod", "case-cod", "refusal", "plan", "ex2",
         "part2", "category", "sim-stock", "sim-deliver", "sim-tests", "sim-returns", "checks", "next"]
write(S, ORDER, "Session 9 — How Will You Deliver the Order?", {
    "open": {"description": "How will you deliver the order, and your last parcel", "start": "cover"},
    "stock": {"description": "Part 1 · Stock, cash and suppliers, with cases", "start": "part1"},
    "excess": {"description": "Stock that will not sell, and fulfilment, with cases", "start": "deadstock"},
    "lastmile": {"description": "Couriers, cash on delivery and refusals, and the operations plan", "start": "couriers"},
    "sim": {"description": "Part 2 · Operations in the simulation", "start": "part2"}})
