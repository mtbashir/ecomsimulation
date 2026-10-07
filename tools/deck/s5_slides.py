"""Session 5 - What to Sell & How to Price It. About 21 slides."""
import pathlib, sys, json
HERE = pathlib.Path(__file__).parent
exec((HERE / "s4_slides.py").read_text().split("\nS = {}\n")[0])
FT = "Session 5 &middot; What to Sell &amp; How to Price It"
def sec(sid, bg, eyebrow, title, body, notes, footer=FT, **kw):
    return section(sid, bg, "#131316", eyebrow, title, body, notes, footer=footer, **kw)
def div(sid, part, title, line, notes):
    return divider(sid, part, title, line, notes).replace("Session 2 &middot; Finding the Right Idea", FT).replace("856d57cb939a323d46943b3b229572d7", "__LOGO__")

S = {}
S["cover"] = f'''<section id="cover" data-transition="fade" style="background:#131316; color:#ffffff; {FONT}; padding:128px 128px 160px; display:flex; flex-direction:column; justify-content:space-between">
  {LOGO}
  <div style="display:flex; flex-direction:column; gap:28px">
    <p style="font-size:28px; font-weight:600; letter-spacing:4px; text-transform:uppercase; color:#ff3b3b">Session 5 of 12</p>
    <h1 style="font-size:132px; font-weight:700; line-height:1.02; letter-spacing:-3px">What to Sell &amp;<br>How to Price It</h1>
    <div style="width:1200px; height:110px; flex:0 0 auto"></div>
  </div>
  <div style="display:flex; align-items:flex-end; gap:64px">
    <div style="display:flex; flex-direction:column; gap:6px">
      <p style="font-size:24px; color:#86868f">Course</p>
      <p style="font-size:30px; font-weight:600; color:#ffffff">E-Commerce: Building, Scaling &amp; Managing Digital Businesses</p>
    </div>
    <div style="flex:1"></div>
    <div style="display:flex; flex-direction:column; gap:6px">
      <p style="font-size:24px; color:#86868f">LUMS CES</p>
      <p style="font-size:30px; font-weight:600; color:#ffffff">Tariq Bashir</p>
    </div>
  </div>
  <p data-build-in="fade 1" style="position:absolute; left:128px; top:647px; width:1300px; height:110px; font-size:38px; line-height:1.45; color:#c9c9d1">Product selection, assortment, pricing, discounts, bundles and promotions &mdash; the shelf, and what it costs to buy from it.</p>
  <aside>Two hours, about 21 slides: 3 min recap, 7 min opening exercise, Part 1 theory about 60 min (selection and assortment 15, pricing 15, discounts and bundles 12, promotions 12, exercise 10), Part 2 simulation about 35 min, 3 min close.

Month 3 has run. Session 3 taught the arithmetic of a discount; today goes further: which products deserve shelf space, how prices are architected, and how bundles and promotions move the basket.

The idea for the day: every product on the shelf has a job, and every price tells the customer something.</aside>
</section>
'''

S["recall"] = sec("recall", "#f5f5f6", "Where we got to last week", "The store turns visitors into orders",
  grid([
    ("Shoppers", "Online buyers check more", "With nothing to touch, a beauty buyer weighs 37 things, not 7.", "#ed0000"),
    ("Trust", "Strangers need reasons", "Cash on delivery, reviews, a real person, a clear returns line.", "#eb6834"),
    ("Checkout", "Most carts are abandoned", "Surprise costs and forced accounts lose the most orders.", "#2a78d6"),
  ], 3, 300, 300)
  + "\n" + band(4, 660, 170, "The store decides <b>how many</b> visitors buy. Today: <b>what is on the shelf, and what each thing costs</b> &mdash; which decides how much each order is worth.", size=31),
  """Three quick clicks from Session 4.

The bridge: revenue is visitors × conversion × average order. Sessions 4 and 7 deal with the first two. Today is the third: the range, the prices, and the offers that shape every basket.""")

S["ex1"] = exercise("ex1", "Exercise 1", "The last thing you bought on sale",
  "Think of the last time you bought something because it was <b>on offer</b> &mdash; online or in a shop.",
  ["Had you planned to buy it before you saw the offer?", "Would you have paid the full price?", "Did you buy more than you meant to?"],
  "Exercise 1 &middot; every offer is a bet on how you will react",
  """Seven minutes. One question per click. Three minutes to write, then take five answers.

Sort the answers as they come:
- Planned anyway, would have paid full price: the discount was money given away.
- Not planned, bought because of the offer: the discount created a sale.
- Bought more than intended: the offer grew the basket.

Most rooms find the first group is the biggest. That is the problem with discounts the session will return to: a lot of the money goes to people who would have bought anyway.""", top=500, h=210)

S["part1"] = div("part1", "Part 1 &middot; Theory", "Six decisions<br>on the shelf",
  "Product selection, assortment, pricing, discounts, bundles and promotions &mdash; each with a Pakistani and a global case.",
  """Part 1 follows the course outline in order: product selection and assortment, then pricing, then discounts and bundles, then promotions. Real-world practice only; the simulation is Part 2.""")

# --- Product selection: margin x volume matrix
def quad(n, L, T, label, title, text, col, bg="#ffffff"):
    return f'''  <div data-build-in="fade {n}" style="position:absolute; left:{L}px; top:{T}px; width:760px; height:250px; background:{bg}; padding:28px 32px; border-radius:16px; border:1px solid #e4e4e7; display:flex; flex-direction:column; gap:8px">
    <p style="font-size:22px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:{col}">{label}</p>
    <h3 style="font-size:31px; font-weight:600; color:#131316">{title}</h3>
    <p style="font-size:25px; line-height:1.4; color:#55555f">{text}</p>
  </div>'''
S["selection"] = sec("selection", "#ffffff", "Product selection", "Which products earn their place?",
  '  <p style="position:absolute; left:128px; top:292px; width:130px; font-size:22px; font-weight:600; letter-spacing:2px; color:#86868f">HIGH MARGIN</p>\n'
  '  <p style="position:absolute; left:128px; top:562px; width:130px; font-size:22px; font-weight:600; letter-spacing:2px; color:#86868f">LOW MARGIN</p>\n'
  '  <p style="position:absolute; left:290px; top:832px; width:760px; font-size:22px; font-weight:600; letter-spacing:2px; color:#86868f; text-align:center">SELLS SLOWLY</p>\n'
  '  <p style="position:absolute; left:1072px; top:832px; width:720px; font-size:22px; font-weight:600; letter-spacing:2px; color:#86868f; text-align:center">SELLS FAST</p>\n'
  + quad(2, 290, 282, "Niche earner", "Good money, few buyers", "Keep it if it does not tie up cash in stock. Do not discount it.", "#8a6414")
  + "\n" + quad(1, 1072, 282, "Star", "Good money, many buyers", "Protect it: never out of stock, never on deep discount.", "#1baf7a")
  + "\n" + quad(4, 290, 552, "Question mark", "Little money, few buyers", "Fix the price, the page or the target &mdash; or cut it.", "#ed0000")
  + "\n" + quad(3, 1072, 552, "Traffic builder", "Little money, many buyers", "Keep it sharp on price; earn on what it is bought with.", "#2a78d6"),
  """One box per click, starting with the star. The two questions for every product: how much does it leave per unit (margin after product cost), and how fast does it sell?

Stars carry the business — protect them. Traffic builders bring people in; their job is to be bought with something else. Niche earners are fine in small doses. Question marks either get fixed or get cut: every product on the shelf costs stock, attention and page space.

The 80/20 rule usually holds online too: a small share of the range makes most of the money. A founder who cannot name their stars has not looked at the numbers.

Question for the room: name one product you know that is a traffic builder for the shop that sells it.""")

S["assortment"] = sec("assortment", "#f5f5f6", "Assortment", "A range is a team, not a list",
  grid([
    ("Hero", "Why they come to you", "The product people search for by name. One or two, never out of stock.", "#ed0000"),
    ("Traffic builder", "What gets them in", "A familiar product at a sharp price, easy to compare and easy to say yes to.", "#2a78d6"),
    ("Basket filler", "What gets added", "Cheap, related, bought on impulse: the second and third item in the order.", "#1baf7a"),
    ("Margin maker", "What pays the bills", "Higher price, higher margin, less price-checked: premium sizes, sets, specialist lines.", "#8a6414"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "Wide range or deep range: more categories, or more choice within one? <b>Which would your customer notice first if it were missing?</b>", size=30),
  """One role per click. Every product on a shelf has a job; an assortment works when the roles cover each other.

Breadth (how many categories) wins new customers; depth (how many choices inside a category — sizes, shades, variants) wins the customer who already knows what they want. Online, depth is cheap to show and expensive to stock.

In personal care: a hero (a serum or sunscreen people search for), a traffic builder (shampoo at a sharp price), basket fillers (soap, sanitiser, sheet masks) and margin makers (premium sizes and gift sets).""")

S["case-range"] = cases("case-range", "Cases &middot; Selection and assortment",
  "Start narrow, widen from a strong core",
  ("Pakistan", "Sapphire", "Karachi, 2014",
   [("The start", "One store in Dolmen Mall, built on unstitched lawn from its parent textile group."),
    ("How it widened", "Into ready-to-wear, menswear, kidswear, fragrance and home textiles."),
    ("The lesson", "The core earned the right to widen: around 50 stores and a global online shop.")]),
  ("Global", "Glossier", "US, 2014",
   [("The start", "Launched online with just four products: a moisturiser, lip balm, face mist and skin tint."),
    ("How it widened", "Added lines its blog readers asked for, each one a clear role in the routine."),
    ("The result", "Valued at US$1.8bn by 2019 &mdash; built on a range anyone could explain.")]),
  "Both began with <b>a few products that did one job well</b>, and added lines only when the core had customers.",
  """Two assortment cases.

Sapphire: founded in 2014 by Nabeel Abdullah as part of the Sapphire textile group, opening one store in Dolmen Mall, Karachi, with unstitched lawn — the group's strength. It widened step by step into ready-to-wear, western wear, menswear, kidswear, fragrance and home textiles, and runs around 50 locations plus an online store shipping abroad.

Glossier: Emily Weiss turned her beauty blog Into the Gloss into a brand that launched in October 2014 with four products — Priming Moisturizer, Balm Dotcom, Soothing Face Mist and Perfecting Skin Tint. New lines came from what readers asked for. It was valued at $1.8 billion in 2019 (and has since had harder years — worth saying).

Question for the room: what would be the four products your brand launches with, and what job does each do?

Sources: Wikipedia and Pakistani Journal on Sapphire; Glossier coverage in Business of Fashion and Wikipedia.""",
  "Sources: Sapphire Retail (Wikipedia); Glossier (Wikipedia, Business of Fashion)")

S["architecture"] = sec("architecture", "#ffffff", "Pricing", "Good, better, best",
  grid([
    ("Entry", "Gets them in the door", "The lowest price on the page. Few buy it; it makes the range feel affordable.", "#2a78d6"),
    ("Core", "Where most buy", "Priced for the main segment. Most of the volume and most of the profit.", "#1baf7a"),
    ("Premium", "Makes the core look sensible", "Bought by fewer people, and its price anchors everything below it.", "#8a6414"),
  ], 3, 300, 340)
  + "\n" + band(4, 700, 160, "Three tiers give the customer a choice instead of a yes-or-no. <b>What would your three tiers be for one product?</b>", size=30),
  """One tier per click. Price architecture is how prices relate to each other, not just what each one is.

A single price asks "buy or not?". Three tiers ask "which one?" — and most people pick the middle. The premium tier does two jobs: it earns a high margin from those who want the best, and it makes the core price look reasonable next to it.

Real example: Dollar Shave Club's three razor plans — a two-blade at $1 a month (plus shipping), a four-blade at $6 and a six-blade at $9, delivered monthly. Most customers chose the middle plans.

In personal care: a 100 ml, a 200 ml and a gift set; or economy, standard and premium formulas.""")

S["psychology"] = sec("psychology", "#f5f5f6", "Pricing", "How customers read a price",
  grid([
    ("Price points", "Rs 999 is not Rs 1,000", "The first digit is read first. Pakistani shoppers know every Rs 99 ending.", "#ed0000"),
    ("Anchoring", "The first price sets the scale", "Show the original or the premium price first; everything after is compared to it.", "#eb6834"),
    ("The decoy", "A third option steers the choice", "An option nobody wants makes the one beside it look like a bargain.", "#2a78d6"),
    ("Pack size", "Price per use, not per pack", "A smaller pack keeps a price point people can afford today.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "Customers rarely know what a product should cost. They judge a price against <b>what is shown next to it</b>. What does your product page show next to yours?", size=29),
  """One idea per click. These are well-documented effects, not tricks — but they are easy to overuse.

Price points: prices just below a round number (Rs 999, Rs 1,490) are read as lower. In Pakistan, retail price points like Rs 10, Rs 20 and Rs 50 are fixed in shoppers' minds.

Anchoring: the first number seen becomes the reference. "Was Rs 1,800, now Rs 1,450" works because of the first number — which is why fake "was" prices are both common and illegal in many markets.

The decoy: see the next slide.

Pack size: when costs rise, FMCG companies in Pakistan often shrink the pack rather than break a price point. Online, show price per 100 ml so customers can compare honestly.""")

S["case-price"] = cases("case-price", "Cases &middot; Pricing",
  "The price shown beside yours decides",
  ("Pakistan", "Sooper", "ticky packs, EBM",
   [("The price point", "Small 'ticky' packs at Rs 5 to Rs 10, priced for a child's pocket money."),
    ("Why it works", "The price stays where the buyer expects; the pack size does the adjusting."),
    ("The scale", "Sooper alone now sells more than Rs 30 billion a year.")]),
  ("Global", "The Economist", "subscription test",
   [("Three options", "Web US$59, print US$125, print and web US$125."),
    ("What people chose", "16% web, 0% print, 84% print and web: nobody wanted the decoy."),
    ("Without the decoy", "With print removed, 68% chose web and only 32% the bundle.")]),
  "Neither changed the product. Both changed <b>what the customer compared it with</b>.",
  """Two pricing cases.

Sooper (English Biscuit Manufacturers): Pakistan's best-selling biscuit, sold in small "ticky" packs at Rs 5–10 for schools and corner shops. Holding the price point and adjusting the pack is how many Pakistani FMCG brands handle inflation. Sooper's gross sales are reported at over Rs 30 billion. (The pack-size point is general FMCG practice; check current packs before quoting specifics.)

The Economist: Dan Ariely's well-known experiment with MIT students. With three options — web $59, print $125, print and web $125 — 16 chose web, none print, 84 print-and-web. Removing the print-only "decoy" flipped it: 68 chose web, 32 the bundle. Nobody bought the decoy; it existed to make the bundle look like a bargain. (Note for the room: some later replications found the effect weaker — worth mentioning.)

Question for the room: where have you seen a decoy price this month?

Sources: Profit by Pakistan Today; EBM coverage; Ariely, Predictably Irrational; The Decision Lab.""",
  "Sources: Profit (Pakistan Today); Ariely, <i>Predictably Irrational</i>")

drows2 = [("Facewash", "50%", "10%", "5.0 points"), ("Hair oil", "30%", "0%", "0"), ("Lip balm", "20%", "0%", "0"),
          ("The shop's average discount", "", "", "5.0%")]
S["discounts"] = sec("discounts", "#ffffff", "Discounts", "Discount the line, not the shop",
  trows(["Product", "Share of sales", "Discount", "Adds to the average"], drows2, 282, [560, 340, 340, 368], rh=86, size=29)
  + "\n" + band(5, 720, 170, "A deep cut on a line nobody buys moves nothing; a small cut on your star costs the most. The cost of a discount is <b>discount &times; share of sales</b>. Which of your lines would really sell more if it were cheaper?", size=28),
  """One row per click. Illustrative numbers.

The shop's real discount is the average across what actually sells, weighted by each product's share of sales. Here, 10% off the facewash — half of all sales — costs as much as 5% off everything.

So targeted discounts are cheaper only if they are aimed at lines where the discount wins more customers than it costs: price-sensitive products, traffic builders, new products that need a first trial. Discounting a star that sells anyway gives money to people who would have paid full price — Exercise 1's first group.

Session 3 showed how much extra volume a discount needs to pay for itself; today's point is where to aim it.""",
  footer="Illustrative numbers")

S["bundles"] = sec("bundles", "#f5f5f6", "Bundles", "Three ways to sell products together",
  grid([
    ("Multipack", "Three of the same", "Shampoo &times; 3. Bigger basket, more units, a saving per unit. Works on products that run out.", "#ed0000"),
    ("Mixed bundle", "A set, or each on its own", "Facewash + moisturiser + sunscreen, also sold singly. The set looks like a deal next to the singles.", "#2a78d6"),
    ("Pure bundle", "Only as a set", "A gift box or a routine kit. Easy to price high, hard to compare.", "#1baf7a"),
  ], 3, 300, 330)
  + "\n" + band(4, 690, 180, "The test for every bundle: price it against <b>buying the items separately</b>. Below that, it sells and gives margin away on every pack; above it, nobody buys it. How much would you give away to double your basket?", size=28),
  """One type per click.

Multipacks raise units per order and lock in future use — strong for products that run out (soap, shampoo, detergent). Mixed bundles (sold both ways) make the set look like a bargain beside the singles; most online beauty brands use them as "routines". Pure bundles (only as a set) suit gifts and new-customer kits; they avoid direct comparison.

The economics: a bundle works if the extra items it sells are worth more than the saving it gives away on the items the customer would have bought anyway. Typical saving: 5–15% against singles. Deeper than that, the basket grows and the margin per item shrinks.

Online marketplaces show "frequently bought together" — a mixed bundle built by data.""")

S["promotions"] = sec("promotions", "#ffffff", "Promotions", "Plan promotions around the calendar",
  grid([
    ("Ramadan &amp; Eid", "The biggest season", "Gifting, new clothes, home care before guests. Plan stock two months ahead.", "#1baf7a"),
    ("11.11 and Big Friday", "Marketplace mega-sales", "Huge traffic, deep discounts, fierce comparison. Know your margin floor first.", "#ed0000"),
    ("Seasons", "Summer, winter, monsoon", "Sunscreen in May, moisturiser in December. Promote what people already need.", "#2a78d6"),
    ("Your own moments", "Launches and anniversaries", "A reason to talk to customers that rivals do not share.", "#8a6414"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "Price-off, buy-one-get-one, free gift, free delivery, bundle: <b>which one costs you least for the response you want?</b>", size=30),
  """One moment per click. A promotion works best when customers are already in a buying mood — the calendar decides more than the discount.

Pakistan's retail calendar: Ramadan and Eid (the largest), 11.11 and Big/White Friday on the marketplaces, summer lawn launches, back to school, winter, and wedding season.

Promotion types: price-off is simplest and most comparable; buy-one-get-one doubles units; a free gift protects the price; free delivery fixes the most common checkout objection; a bundle grows the basket. Each costs something different — a free gift costs its unit cost, not its price.""")

# Promo lift chart (illustrative weekly bars)
weeks = [("W1", 100, "b"), ("W2", 100, "b"), ("W3", 230, "p"), ("W4", 210, "p"), ("W5", 70, "d"), ("W6", 85, "d"), ("W7", 100, "b")]
bars = []
for i, (lab, v, kind) in enumerate(weeks):
    L = 300 + i * 200; h = int(v * 1.8); top = 800 - h
    col = {"b": "#86868f", "p": "#ed0000", "d": "#2a78d6"}[kind]
    n = 1 if kind == "b" and i < 2 else 2 if kind == "p" else 3 if kind == "d" else 4
    bars.append(f'''  <div data-build-in="fade {n}" style="position:absolute; left:{L}px; top:{top - 40}px; width:150px; height:{h + 80}px">
    <p style="position:absolute; left:0px; top:0px; width:150px; font-size:26px; font-weight:600; color:#131316; text-align:center; font-family:'JetBrains Mono', monospace">{v}</p>
    <div style="position:absolute; left:25px; top:40px; width:100px; height:{h}px; background:{col}; border-radius:6px"></div>
    <p style="position:absolute; left:0px; top:{h + 46}px; width:150px; font-size:24px; color:#55555f; text-align:center">{lab}</p>
  </div>''')
S["lift"] = sec("lift", "#f5f5f6", "Promotions", "A promotion borrows from next month",
  '  <div style="position:absolute; left:290px; top:799px; width:1400px; height:2px; background:#131316"></div>\n'
  + "\n".join(bars)
  + "\n" + P(1100, 282, 692, 160, txt("<b>Grey</b>: normal weeks &middot; <b>red</b>: the promotion &middot; <b>blue</b>: the weeks after, when customers who stocked up buy less.", 25, "#55555f"))
  + "\n" + P(128, 282, 900, 60, txt("Weekly units of one product, normal week = 100", 28, "#55555f")),
  """Illustrative numbers, built in four clicks: normal weeks, the promotion, the dip after, then back to normal.

The promotion sold 440 units in two weeks against a normal 200 — it looks like +240. But the next two weeks sold 155 instead of 200: 45 of the promotion's sales were customers buying early, not new demand. The true extra is about 195 units, and every promoted unit carried the discount.

How to measure a promotion: compare with a baseline of normal weeks, count the dip afterwards, and only then judge whether the extra units paid for the discount on all the units.

Promotions that bring in new customers who come back are worth more than the units suggest; promotions that only move existing buyers' purchases forward are worth less.""",
  footer="Illustrative numbers")

S["case-promo"] = cases("case-promo", "Cases &middot; Promotions",
  "Make the sale an event",
  ("Pakistan", "Daraz 11.11", "and Big Friday",
   [("The event", "Black Friday in 2015, renamed Big Friday in 2017 after public objections, plus 11.11."),
    ("The scale", "PKR 66 crore in the first hour of 11.11 in 2021; 34 million visitors in 2023."),
    ("The lesson", "A date everyone knows brings shoppers; your margin floor decides if it pays.")]),
  ("Global", "Amazon Prime Day", "2015",
   [("The idea", "A members-only sale on Amazon's 20th birthday, 15 July 2015, in nine countries."),
    ("The result", "34.4 million items ordered: bigger than Black Friday 2014."),
    ("The lesson", "It sold Prime memberships, not just products: the promotion built repeat buying.")]),
  "Both created <b>a reason to buy on a date</b> &mdash; and used it to win customers, not only to clear stock.",
  """Two promotion cases.

Daraz: introduced Black Friday in Pakistan in 2015 and ran the country's first billion-rupee sale in 2016. In 2017, after objections including a Punjab Assembly resolution, it renamed the event Big Friday (other sites used White Friday or Blessed Friday). Its 11.11 sale recorded sales of about PKR 66 crore in the first hour in 2021, and over 34 million visitors in 2023, with makeup and skincare among the top categories.

Amazon Prime Day: first run on 15 July 2015, Amazon's 20th birthday, for Prime members in nine countries. Members ordered 34.4 million items — more than Black Friday 2014. The real prize was Prime sign-ups, which make customers buy more often all year.

For sellers on Daraz: the mega-sale brings traffic, but the platform's discount expectations and commission come off your margin. Know the lowest price at which a sale still pays before you join.

Question for the room: which date in the Pakistani calendar would you build your brand's own sale around?

Sources: Dawn and The Express Tribune (2017); ProPakistani (2021, 2023); Amazon / Business Wire (2015).""",
  "Sources: Dawn, Express Tribune (2017); ProPakistani; Business Wire (2015)")

S["ex2"] = exercise("ex2", "Exercise 2", "Design one promotion",
  "Pick one product your team would sell and design a promotion for one date in the Pakistani calendar.",
  ["Which product, and what is its job in the range?", "Which type of offer, and why that one?", "How many extra units must it sell to pay for itself?", "What happens to sales the month after?"],
  "Exercise 2 &middot; a promotion with a payback, not a hope",
  """Ten minutes in teams. One question per click.

Push on question three: they should use Session 3's rule — extra volume needed = discount ÷ (margin − discount) — for a price-off, or the unit cost of a free gift.

Question four is the dip from the lift slide. Teams that promote a product people stock up on (shampoo, detergent) should expect a bigger dip.

Take two teams' answers: product, offer, the break-even number.""", top=500, h=180, cols=2)

S["part2"] = div("part2", "Part 2 &middot; The simulation", "Your shelf in<br>the simulation",
  "Bundles, the free-delivery bar and product-by-product discounts open this month.",
  """Part 2 is the simulation. Month 3 has run. Three decisions open this round: bundles (1.2), the free-delivery threshold (2.4), and discounts set product by product inside 1.1.

Every number in Part 2 is the simulation's assumption or a test run of it, not market data.""")

S["sim-levers"] = sec("sim-levers", "#ffffff", "In the simulation", "Three decisions open this month",
  grid([
    ("1.2 &middot; Bundles", "Three-packs, priced as a pack", "Below three singles, more customers take the pack and you give the saving away; above, almost nobody buys. Only your three best packs count.", "#ed0000"),
    ("2.4 &middot; Free delivery", "Where to set the bar", "Up to about half a basket above a typical order (about PKR 4,500), customers add items. Higher, small buyers leave. Free on everything: more orders, smaller baskets.", "#2a78d6"),
    ("1.1 &middot; Line discounts", "Discount product by product", "The cost is the discount times each product's share of sales. Your report shows the weighted average.", "#1baf7a"),
  ], 3, 290, 440, bsize=25)
  + "\n" + band(4, 770, 120, "<b>Which of the three does your month-3 report say your basket needs most?</b>", size=30),
  """One decision per click. The rules are the simulation's.

Bundles: each pack is judged against three singles at your own price. A 10% saving is a fair pack. Extra units carry their product cost, so the basket grows and gross margin dips a little.

Free delivery: a typical basket is about PKR 3,000. A bar between there and about PKR 4,500 makes customers add items; beyond that, conversion falls. Free delivery on everything lifts orders about 4% and shrinks baskets about 3%.

Line discounts: discounting a best-seller costs far more than the same discount on a slow line; the "discount rate" in your report is the sales-weighted average.""",
  footer="Decision rules from the simulation &middot; not market data")

tests5 = [("No change", "844k", "PKR 2,959 &middot; 39.3%"),
          ("3 packs at 10% off three singles", "874k &nbsp;(+4%)", "PKR 3,161 &middot; 37.2%"),
          ("3 packs at 30% off", "145k &nbsp;(&minus;83%)", "PKR 2,937 &middot; 31.0%"),
          ("Free delivery above PKR 4,500", "1,028k &nbsp;(+22%)", "PKR 3,137 &middot; 39.3%"),
          ("10% off everything", "94k &nbsp;(&minus;89%)", "PKR 2,663 &middot; 32.5%"),
          ("10% off the 3 best-sellers", "618k &nbsp;(&minus;27%)", "PKR 2,867 &middot; 37.3%"),
          ("10% off the 3 slowest lines", "740k &nbsp;(&minus;12%)", "PKR 2,917 &middot; 38.4%")]
S["sim-tests"] = sec("sim-tests", "#f5f5f6", "In the simulation", "What the levers did in a test month",
  trows(["Test, all else default", "Contribution", "Avg order &middot; gross margin"], tests5, 282, [700, 420, 488], rh=70, size=27)
  + "\n" + band(8, 840, 70, "<b>Which line of this table would you bet your month 4 on?</b>", size=27, extra="padding:16px 40px;"),
  """One test per click. Each line is one team changing one decision against an identical team on every default, in the same simulated month.

Read across: a fair bundle helps a little; a deep one destroys margin. A free-delivery bar just above a typical basket was the best single move here. A blanket 10% discount wiped out nearly all the month's contribution — the Session 3 lesson again. The same 10% aimed at the three slowest lines cost far less than on the three best-sellers, because the weighted average discount was smaller (1.4% against 3.1%).

Results depend on each team's own prices, range and segments; these are directions, not forecasts.""",
  footer="Simulation test run, month 1, all else default &middot; not market data")

S["checks"] = sec("checks", "#fdeceb", "Before month 4 runs", "Four questions before you submit",
  grid([
    ("Range", "Which are your stars?", "Never discount them deeply; never let them run out.", "#ed0000"),
    ("Bundles", "Is every pack below three singles?", "Check the Saving column; three good packs are enough.", "#eb6834"),
    ("Delivery", "Where is your typical basket?", "Set the bar a little above it, not far above.", "#2a78d6"),
    ("Discounts", "Who gets the discount?", "Aim it at lines where it wins customers, not at buyers who would pay anyway.", "#1baf7a"),
  ], 4, 300, 330)
  + "\n" + band(5, 690, 150, "Name in the board memo the number in next month's report that will show <b>whether your shelf changes worked</b>.", size=30),
  """One question per click, while teams fill in the decision form.

Logistics for the notes, not the slide: decisions for month 4 close at [deadline]. Open this round: 1.2 bundles, 2.4 free-delivery threshold, discounts by product in 1.1, plus everything opened earlier.""")

S["next"] = sec("next", "#131316", "Next session", "Where will you sell?",
  grid([
    ("Session 6", "Is Daraz worth its commission?", "Marketplace reach against own-site margin.", "#ff3b3b"),
    ("Your customers", "Who owns them on a marketplace?", "You cannot remarket to buyers the platform keeps.", "#ff3b3b"),
    ("Your numbers", "Did your shelf changes work?", "Month 4's basket and margin are the test.", "#ff3b3b"),
  ], 3, 300, 300, bg="#1f1f24", border="border:1px solid #33333b;", tcol="#ffffff", bcol="#c9c9d1")
  + "\n" + band(4, 660, 150, "Today: what each order is worth. Next time: <b>where to sell it, and who keeps the customer</b>.", bg="#ed0000", size=31),
  """Close. One card per click.

Session 6 opens the marketplace decision (4.1): sell on Daraz or not, at what commission. Own-site margin against marketplace reach.""", dark=True, eyecol="#ff3b3b")

ORDER = ["cover", "recall", "ex1", "part1", "selection", "assortment", "case-range", "architecture", "psychology",
         "case-price", "discounts", "bundles", "promotions", "lift", "case-promo", "ex2", "part2", "sim-levers",
         "sim-tests", "checks", "next"]
assert set(ORDER) == set(S), set(S) ^ set(ORDER)
logo = sys.argv[2] if len(sys.argv) > 2 else "__LOGO__"
root = pathlib.Path(sys.argv[1]) / "project"
(root / "slides").mkdir(parents=True, exist_ok=True)
for k, v in S.items():
    (root / "slides" / f"{k}.html").write_text(v.replace("__LOGO__", logo.rsplit("/", 1)[-1]))
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-10-07T18:40:00Z"}, "lists": "css",
        "title": "Session 5 — What to Sell & How to Price It", "order": ORDER,
        "sections": {
          "open": {"description": "What to sell and how to price it, and what we covered last week", "start": "cover"},
          "range": {"description": "Part 1 · Product selection and assortment, with cases", "start": "part1"},
          "price": {"description": "Pricing architecture and psychology, with cases", "start": "architecture"},
          "offers": {"description": "Discounts, bundles and promotions, with cases", "start": "discounts"},
          "sim": {"description": "Part 2 · Your shelf in the simulation", "start": "part2"}},
        "faces": {"inter": {"family": "Inter", "href": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono"}},
        "designSystems": []}
if not (root / "deck.json").exists():
    (root / "deck.json").write_text(json.dumps(deck, indent=2, ensure_ascii=False))
print("wrote", len(S))
