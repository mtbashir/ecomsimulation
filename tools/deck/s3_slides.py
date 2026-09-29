"""Session 3 - How Will You Make Money? Theory with cases, then the simulation."""
import pathlib, sys, json
HERE = pathlib.Path(__file__).parent
exec((HERE / "s2_slides.py").read_text().split("slides = {}")[0])
g2 = (HERE / "s2_cases.py").read_text()
exec("def case_card" + g2.split("def case_card", 1)[1].split("\nslides = {}\n")[0])

FT = "Session 3 &middot; How Will You Make Money?"
LOGO = '<img src="/_blob/08915064a97a15b612763fb2958cfbac" alt="Consulytics.AI" style="width:340px; height:67px; object-fit:contain">'

def sec(sid, bg, eyebrow, title, body, notes, footer=FT, **kw):
    return section(sid, bg, "#131316", eyebrow, title, body, notes, footer=footer, **kw)

def div(sid, part, title, line, notes):
    return divider(sid, part, title, line, notes).replace("Session 2 &middot; Finding the Right Idea", FT)

def cases(sid, eyebrow, title, pk, gl, lesson, notes, footer):
    return case_slide(sid, eyebrow, title, pk, gl, lesson, notes, footer)

def P(L, T, W, H, inner, n=None, extra=""):
    b = f' data-build-in="fade {n}"' if n else ""
    return f'  <div{b} style="position:absolute; left:{L}px; top:{T}px; width:{W}px; height:{H}px; {extra}">{inner}</div>'

def txt(s, size=26, col="#131316", w=400, extra=""):
    return f'<p style="font-size:{size}px; font-weight:{w}; line-height:1.3; color:{col}; {extra}">{s}</p>'

# ---------- waterfall (rows) ----------
def waterfall(rows, top=276, rh=60, gap=8, scale=1.05, zero=560, labw=400):
    """rows: (label, start, end, kind, click). kind: total|cost|loss. Values in PKR of 1,000."""
    out = []
    for i, (lab, a, b, kind, n) in enumerate(rows):
        T = top + i * (rh + gap)
        lo, hi = min(a, b), max(a, b)
        L = zero + int(lo * scale); W = max(6, int((hi - lo) * scale))
        col = {"total": "#131316", "cost": "#ed0000", "loss": "#ed0000", "sub": "#55555f"}[kind]
        bold = 600 if kind in ("total", "sub", "loss") else 400
        val = f"&minus;{abs(b - a):,}" if kind == "cost" else (f"&minus;{abs(b):,}" if b < 0 else f"{b:,}")
        out.append(f'''  <div data-build-in="fade {n}" style="position:absolute; left:128px; top:{T}px; width:1664px; height:{rh}px">
    <p style="position:absolute; left:0px; top:12px; width:{labw}px; font-size:26px; font-weight:{bold}; color:#131316">{lab}</p>
    <div style="position:absolute; left:{L - 128}px; top:8px; width:{W}px; height:{rh - 16}px; background:{col}; border-radius:6px"></div>
    <p style="position:absolute; left:{L - 128 + W + 16}px; top:12px; width:200px; font-size:26px; font-weight:600; color:{col if kind != 'sub' else '#131316'}; font-family:'JetBrains Mono', monospace">{val}</p>
  </div>''')
    return "\n".join(out)

# ---------- table of pinned flex rows ----------
def trows(cols, rows, top, widths, rh=84, size=27, head_size=22, start=1, bold_first=True, left=128):
    out = []
    head = "".join(f'<p style="width:{w}px; font-size:{head_size}px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:#86868f">{c}</p>' for c, w in zip(cols, widths))
    out.append(f'  <div style="position:absolute; left:{left}px; top:{top}px; width:1664px; height:50px; display:flex; align-items:center; gap:0px; padding:0px 28px; border-bottom:2px solid #131316">{head}</div>')
    for i, r in enumerate(rows):
        T = top + 50 + i * rh
        cells = "".join(f'<p style="width:{w}px; font-size:{size}px; line-height:1.3; font-weight:{600 if (j == 0 and bold_first) else 400}; color:#131316">{c}</p>' for j, (c, w) in enumerate(zip(r, widths)))
        out.append(f'  <div data-build-in="fade {start + i}" style="position:absolute; left:{left}px; top:{T}px; width:1664px; height:{rh}px; display:flex; align-items:center; padding:0px 28px; border-bottom:1px solid #e4e4e7">{cells}</div>')
    return "\n".join(out)

def bignum(n, L, T, W, H, label, num, text, numcol="#131316", bg="#ffffff"):
    return f'''  <div data-build-in="fade {n}" style="position:absolute; left:{L}px; top:{T}px; width:{W}px; height:{H}px; background:{bg}; padding:34px 36px; border-radius:18px; border:1px solid #e4e4e7; display:flex; flex-direction:column; gap:10px">
    <p style="font-size:22px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:#86868f">{label}</p>
    <p style="font-size:64px; font-weight:700; letter-spacing:-1.5px; line-height:1.1; color:{numcol}; font-family:Inter, Arial, sans-serif">{num}</p>
    <p style="font-size:25px; line-height:1.4; color:#55555f">{text}</p>
  </div>'''

def row4(items, top, h, start=1, gap=26):
    w = (1664 - gap * 3) // 4
    return "\n".join(bignum(start + i, 128 + i * (w + gap), top, w, h, *it) for i, it in enumerate(items))

def row3(items, top, h, start=1, gap=26):
    w = (1664 - gap * 2) // 3
    return "\n".join(bignum(start + i, 128 + i * (w + gap), top, w, h, *it) for i, it in enumerate(items))

S = {}

# ================================ OPENING ====================================
S["cover"] = f'''<section id="cover" data-transition="fade" style="background:#131316; color:#ffffff; {FONT}; padding:128px 128px 160px; display:flex; flex-direction:column; justify-content:space-between">
  {LOGO}
  <div style="display:flex; flex-direction:column; gap:28px">
    <p style="font-size:28px; font-weight:600; letter-spacing:4px; text-transform:uppercase; color:#ff3b3b">Session 3 of 12</p>
    <h1 style="font-size:132px; font-weight:700; line-height:1.02; letter-spacing:-3px">How Will You<br>Make Money?</h1>
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
  <p data-build-in="fade 1" style="position:absolute; left:128px; top:647px; width:1300px; height:110px; font-size:38px; line-height:1.45; color:#c9c9d1">Revenue, costs, pricing, the cost of a customer and the value of one who comes back &mdash; and what is left at the end of the month.</p>
  <aside>Two hours: 3 min recap, 7 min opening exercise, Part 1 theory with cases about 60 min (revenue and costs 18, pricing 14, customers and repeat 16, unit economics 12), Part 2 simulation about 45 min (reading the P&amp;L 10, the numbers 12, re-pricing workshop 18, board memo 5), 5 min close.

Today is the first debrief: month 1 has been run, so every team has a real P&amp;L. Teach the theory first without it, then open their own report in Part 2.

The line to set expectations: last week was about what to sell. This week is about whether selling it makes money.</aside>
</section>
'''

S["recall"] = sec("recall", "#f5f5f6", "Where we got to last week", "Your company exists",
  grid([
    ("Problem", "A problem worth solving", "Found where customers already complain, search, return or improvise.", "#ed0000"),
    ("Opportunity", "Big, often, profitable", "Enough people, buying often enough, with margin left after everything.", "#1baf7a"),
    ("Customer", "One customer you know", "A segment you can win, described as a person, not a crowd.", "#2a78d6"),
  ], 3, 300, 300)
  + "\n" + band(4, 660, 170, "Last week ended on the third word &mdash; <b>profitable</b>. Today we find out what it takes, and your first month's report tells you how far you are from it.", size=31),
  """Three quick clicks from last week — re-land them, do not re-teach.

The band is the bridge: last week's third opportunity test was "profitable enough". Today is the whole of that test.

Month 1 has run. Tell the room their report is waiting, and that they will open it in the second half, after the theory.""")

S["ex1"] = f'''<section id="ex1" data-transition="push" style="background:#fdeceb; color:#131316; {FONT}; padding:128px 128px 160px; display:flex; flex-direction:column; gap:40px">
  <p style="font-size:26px; font-weight:600; letter-spacing:4px; text-transform:uppercase; color:#ed0000">Exercise 1</p>
  <h2 style="font-size:88px; font-weight:700; letter-spacing:-2px; line-height:1.05">Where does PKR 1,000 go?</h2>
  <p style="font-size:34px; line-height:1.45; color:#55555f; width:1450px">A customer pays <b>PKR 1,000</b> for a shampoo and conditioner delivered to her door in Multan.</p>
''' + "\n".join(f'''  <div data-build-in="fade {i+1}" style="position:absolute; left:{128 + i*562}px; top:500px; width:540px; height:210px; background:#ffffff; padding:38px; border-radius:16px; border:1px solid #f2c9c6; display:flex; flex-direction:column; gap:12px">
    <p style="font-size:26px; font-weight:600; color:#ed0000; font-family:'JetBrains Mono', monospace">{i+1}</p>
    <p style="font-size:31px; font-weight:600; line-height:1.3">{q}</p>
  </div>''' for i, q in enumerate(["Who takes a share of it before you do?", "How much would you guess is left for you?", "What would you change first to keep more?"])) + f'''
  {FOOT.format("Exercise 1 &middot; keep your guess, we come back to it")}
  <aside>Seven minutes. One question per click.

Ask each person to write a number for question two — how many rupees of the 1,000 the seller keeps as profit. Take five guesses out loud and write the range down. Most rooms guess 200 to 400.

Question one should produce: the supplier (product cost), the courier, the payment or COD fee, the marketplace if there is one, the ad platforms, and the salaries and rent. Do not correct anything yet.

The answer arrives on the slide "Where PKR 1,000 of an order goes" in Part 1, and again with the simulation's own numbers in Part 2.</aside>
</section>
'''

S["part1"] = div("part1", "Part 1 &middot; Theory",
  "Five numbers that decide<br>if you make money",
  "Revenue, costs, price, the cost of a customer and the value of one who returns &mdash; each with a Pakistani and a global case.",
  """Part 1 is real-world theory with no simulation in it. Five blocks: revenue, costs and margins, pricing, customer acquisition cost and repeat customers, and finally unit economics, which ties them together.

Cases come after each pair of blocks, always one Pakistani and one global.""")

# ================================ REVENUE ====================================
def fbox(n, L, W, label, val, sub, dark=False):
    bg, fg, sc = ("#131316", "#ffffff", "#c9c9d1") if dark else ("#ffffff", "#131316", "#55555f")
    return f'''  <div data-build-in="fade {n}" style="position:absolute; left:{L}px; top:300px; width:{W}px; height:250px; background:{bg}; padding:34px; border-radius:18px; border:1px solid #e4e4e7; display:flex; flex-direction:column; gap:10px">
    <p style="font-size:22px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:{'#ff3b3b' if dark else '#86868f'}">{label}</p>
    <p style="font-size:52px; font-weight:700; letter-spacing:-1px; color:{fg}">{val}</p>
    <p style="font-size:24px; line-height:1.35; color:{sc}">{sub}</p>
  </div>'''
def op(n, L, s):
    return f'  <p data-build-in="fade {n}" style="position:absolute; left:{L}px; top:385px; width:60px; font-size:60px; font-weight:300; color:#86868f; text-align:center">{s}</p>'
bw = 356; ow = 80
xs = [128 + i * (bw + ow) for i in range(4)]
S["revenue"] = sec("revenue", "#ffffff", "Revenue", "Revenue is three numbers multiplied",
  fbox(1, xs[0], bw, "Visitors", "20,000", "People who reach your store or listing this month")
  + "\n" + op(2, xs[0] + bw + 10, "&times;") + "\n" + fbox(2, xs[1], bw, "Conversion rate", "2%", "Share of visitors who place an order")
  + "\n" + op(3, xs[1] + bw + 10, "&times;") + "\n" + fbox(3, xs[2], bw, "Average order", "PKR 3,000", "Rupees per order, after discounts")
  + "\n" + op(4, xs[2] + bw + 10, "=") + "\n" + fbox(4, xs[3], bw, "Revenue", "PKR 1.2m", "400 orders this month", dark=True)
  + "\n" + band(5, 630, 150, "Every growth plan moves one of the three. <b>Which one is cheapest for you to move &mdash; and which costs the most?</b>", size=31),
  """One term per click, then the question. Illustrative numbers.

Visitors come from marketing, search, social and repeat customers. Conversion depends on the store, price, trust, delivery promise and payment options. Average order value rises with bundles, free-delivery thresholds and range.

The point: a founder who says "we will grow revenue" has not said anything until they say which of the three they will move, and what it costs.

Typical answer from the room: visitors are the most expensive (you pay for each one), conversion is often the cheapest (fix the store, add COD, show reviews), average order sits between.""",
  footer="Illustrative numbers")

fun = [("Orders placed", 100, "#131316"), ("After cancellations", 95, "#55555f"), ("After parcels refused at the door", 82, "#55555f"),
       ("After returns", 77, "#55555f"), ("Paid for and kept", 77, "#ed0000")]
S["netrev"] = sec("netrev", "#f5f5f6", "Revenue", "Orders placed are not revenue",
  "\n".join(f'''  <div data-build-in="fade {i+1}" style="position:absolute; left:128px; top:{290 + i*96}px; width:1664px; height:80px">
    <p style="position:absolute; left:0px; top:20px; width:520px; font-size:28px; font-weight:{600 if i in (0,4) else 400}; color:#131316">{lab}</p>
    <div style="position:absolute; left:540px; top:6px; width:{int(v*10.2)}px; height:68px; background:{c}; border-radius:8px"></div>
    <p style="position:absolute; left:{560 + int(v*10.2)}px; top:18px; width:100px; font-size:30px; font-weight:600; color:#131316; font-family:'JetBrains Mono', monospace">{v}</p>
  </div>''' for i, (lab, v, c) in enumerate(fun[:4]))
  + "\n" + band(5, 690, 150, "Out of every 100 orders in this example, you are paid for <b>77</b>. In Pakistan, where most orders are cash on delivery, the door is where revenue is really made.", size=30),
  """Illustrative numbers — not measured market data — but the shape is typical of cash-on-delivery e-commerce.

Click by click: 100 orders placed; a few cancelled before dispatch; a larger slice refused at the door when the courier arrives (the customer changed their mind, was not home, or never meant it); then returns after delivery.

Two lessons. First, the revenue line in any report should be net: after cancellations, refusals, returns and discounts. Second, a refused COD parcel is worse than a lost sale — you paid the courier both ways.

Question for the room: what would you do to cut refusals at the door? (Confirmation calls, prepaid discounts, faster delivery, honest photos.)""",
  footer="Illustrative numbers, not market data")

# ================================ COSTS ======================================
S["costs"] = sec("costs", "#ffffff", "Costs", "Four kinds of cost",
  grid([
    ("Product cost", "What you paid for it", "The product itself and getting it to your warehouse. Grows with every unit sold.", "#ed0000"),
    ("Cost per order", "Getting it to the door", "Packing, courier, cash-on-delivery or card fees, marketplace commission, returns.", "#eb6834"),
    ("Marketing", "Finding the customer", "Ads, influencers, discounts to win the first order. Spent before you know if it works.", "#2a78d6"),
    ("Fixed costs", "Keeping the lights on", "Salaries, rent, warehouse, software. The same whether you sell 10 orders or 10,000.", "#55555f"),
  ], 4, 300, 330)
  + "\n" + band(5, 690, 150, "The first two grow with every order. The last one does not care how many you sell. <b>Which of your costs could you turn off next month?</b>", size=30),
  """One kind per click.

The distinction that matters is variable versus fixed. Product cost and cost per order grow with every order. Marketing is a choice you make each month. Fixed costs arrive whether or not you sell.

In e-commerce the cost per order is the one founders forget. A courier charges the same to deliver a PKR 400 soap as a PKR 3,000 serum.""")

S["margins"] = sec("margins", "#f5f5f6", "Costs and margins", "Where PKR 1,000 of an order goes",
  waterfall([
    ("Customer pays", 0, 1000, "total", 1),
    ("Product cost", 1000, 450, "cost", 2),
    ("Gross margin", 0, 450, "sub", 2),
    ("Packing, courier, payment fees", 450, 280, "cost", 3),
    ("Contribution", 0, 280, "sub", 3),
    ("Marketing", 280, 100, "cost", 4),
    ("After marketing", 0, 100, "sub", 4),
    ("Salaries, rent, software", 100, 30, "cost", 5),
    ("Profit", 0, 30, "total", 5),
  ], top=280, rh=54, gap=6, scale=1.0, zero=600)
  + "\n" + P(1000, 850, 792, 50, txt("Compare with your guess from Exercise 1.", 26, "#55555f", 600), n=6),
  """Two clicks per cost: the cost, then what is left. Illustrative — a plausible shape for a Pakistani personal-care seller, not measured data.

Out of PKR 1,000: 550 to the supplier leaves a gross margin of 450. Packing, courier and COD or card fees take 170, leaving a contribution of 280. Marketing takes 180, leaving 100. Salaries, rent and software take 70. The seller keeps 30 — three percent.

Now go back to the Exercise 1 guesses. Most rooms guessed ten times this.

Name the four margins as you go: gross margin, contribution margin, contribution after marketing, and operating profit (EBITDA). Every investor conversation uses these words.""",
  footer="Illustrative numbers")

# ================================ CASE: REVENUE MODELS =======================
S["case-revenue"] = cases("case-revenue", "Cases &middot; Revenue and costs",
  "The money can come from somewhere else",
  ("Pakistan", "Daraz", "marketplace",
   [("How it earns", "A commission on each sale, from 0% to about 20% by category, plus a payment fee."),
    ("Who carries the cost", "The seller holds the stock, packs the order and funds the discounts."),
    ("The lesson", "A marketplace sells reach. The seller's margin pays for it, order by order.")]),
  ("Global", "Costco", "US",
   [("How it earns", "Membership fees: US$4.8bn in 2024, under 2% of its US$250bn of sales."),
    ("What that allows", "Prices kept close to cost, because the fee arrives whatever members buy."),
    ("The result", "Fees were more than half of its US$9.3bn operating income in 2024.")]),
  "Know <b>which line pays your bills</b>. For Daraz it is commission; for Costco it is the membership card, not the goods.",
  """Two revenue models.

Daraz: the seller's view. Commission runs from 0% to around 20% depending on category, and sellers also pay a payment fee. The seller holds stock, packs, and funds most discounts. A seller who prices without the commission in mind finds it in the P&amp;L. (Rates are published in Daraz's seller centre and change; check the current table before quoting a number.)

Costco: fiscal 2024 membership fees were about $4.8 billion against about $250 billion of net sales — under 2% of revenue — yet more than half of its roughly $9.3 billion operating income. That is why it can price goods close to cost.

Question for the room: in your business, which single line pays the salaries?

Sources: Costco 2024 annual report; Motley Fool (Dec 2024); Daraz seller fee guides.""",
  "Sources: Costco 2024 annual report; Daraz seller fee guides")

# ================================ PRICING ====================================
S["pricing"] = sec("pricing", "#ffffff", "Pricing", "Three ways to set a price",
  grid([
    ("Cost-plus", "Cost, plus a margin", "Simple and safe on paper. Ignores what the customer would pay and what rivals charge.", "#55555f"),
    ("Competitor-based", "Where the market is", "Price against the shelf you are compared with. Easy to start, and easy to get dragged into a price war.", "#eb6834"),
    ("Value-based", "What it is worth to them", "Starts from the customer's problem and alternatives. Hardest to research, and where margin lives.", "#1baf7a"),
  ], 3, 300, 330)
  + "\n" + band(4, 690, 150, "Cost sets the floor, value sets the ceiling, and competitors tell you where you sit between them. <b>Which one set your founding prices?</b>", size=30),
  """One method per click.

Cost-plus: take the landed cost, add a target margin. Useful as a floor, dangerous as a strategy — it leaves money on the table when value is high and prices you out when rivals are cheaper.

Competitor-based: look at the shelf the customer compares you with — Daraz, Instagram sellers, the supermarket. Good for commodities. The risk is following rivals down.

Value-based: what is the problem worth to the customer, and what is their next best alternative? A sensitive-skin moisturiser that works is worth more than its cost-plus price to someone who has tried five that did not.

In practice, use all three: cost is the floor, value the ceiling, competition tells you where in between.

Question for the room: which of the three did you use last week without realising?""")

drows = [("30%", "+50%", "+200%", "impossible"), ("40%", "+33%", "+100%", "+300%"), ("50%", "+25%", "+67%", "+150%")]
S["discount"] = sec("discount", "#f5f5f6", "Pricing", "A discount needs more sales than you think",
  txt("Extra units you must sell just to keep the same gross profit", 30, "#55555f", 400, "position:absolute; left:128px; top:282px; width:1500px")
  + "\n" + trows(["Your margin before the discount", "10% off", "20% off", "30% off"], drows, 350, [640, 330, 330, 308], rh=96, size=34)
  + "\n" + band(4, 720, 150, "The rule: extra volume needed = discount &divide; (margin &minus; discount). <b>Would 10% off really bring a third more buyers?</b>", size=30),
  """One margin row per click. This is arithmetic, not data: the extra volume needed to keep the same gross profit is d / (m − d).

At a 40% margin a 10% discount needs a third more units just to stand still; 20% off needs double. At 30% margin, 30% off leaves no margin at all — no volume can make it up.

And this is before cost per order: every extra order also pays packing, courier and fees, so the real hurdle is higher.

Discounts can still be right — to win a first order, clear stock or answer a rival — but they are an investment with a payback, not a free lever.

Question for the room: what did your founding prices assume about discounts?""",
  footer="Arithmetic: gross profit held constant, before per-order costs")

S["case-pricing"] = cases("case-pricing", "Cases &middot; Pricing",
  "Price the way customers buy",
  ("Pakistan", "Sachets", "shampoo and detergent",
   [("The problem", "Many households buy daily, with cash, and cannot afford a full bottle at once."),
    ("What sellers did", "Sold shampoo and detergent in single-use sachets at a price a day's budget allows."),
    ("The lesson", "Dearer per millilitre, but it reached millions who would never buy the bottle.")]),
  ("Global", "J.C. Penney", "US, 2012",
   [("The idea", "Scrapped coupons and constant sales for honest &ldquo;fair and square&rdquo; everyday prices."),
    ("What happened", "Comparable store sales fell 18.9% in the first quarter; shoppers missed the deal."),
    ("The result", "The CEO was fired after 17 months, and the promotions came back in 2013.")]),
  "A price is not just a number. It is <b>a pack size, a habit and a feeling of a good deal</b>.",
  """Two pricing cases.

Sachets: the single-use sachet was pioneered by Unilever's Indian arm in the 1980s and is now everywhere in Pakistan — shampoo, detergent, tea. Unilever says its brands reach 99% of Pakistani households and lead in soap and shampoo. The sachet costs more per millilitre than the bottle, but it matches how a daily-wage household buys: small amounts, in cash, when needed. The pack size is the price decision. (Critics point out that per unit it charges the poorest more — worth raising.)

J.C. Penney: in February 2012 the new CEO, Ron Johnson, replaced coupons and promotions with everyday "fair and square" prices. Comparable store sales fell 18.9% in the first quarter alone. He was fired in April 2013, and the company returned to promotions. The customers had been buying the feeling of a deal, not the price.

Question for the room: your customers mostly pay cash on delivery. What does that mean for pack size and price points?

Sources: Unilever "Inside our markets: Pakistan" (2023); J.C. Penney SEC filings (2012–13); Chief Executive.""",
  "Sources: Unilever (2023); J.C. Penney SEC filings 2012&ndash;13")

# ================================ CAC & REPEAT ===============================
S["cac"] = sec("cac", "#ffffff", "Customer acquisition cost", "What it costs to win one customer",
  f'''  <div data-build-in="fade 1" style="position:absolute; left:128px; top:290px; width:1664px; height:170px; background:#131316; padding:36px 46px; border-radius:18px; display:flex; align-items:center; gap:36px">
    <p style="font-size:52px; font-weight:700; color:#ffffff">CAC</p>
    <p style="font-size:52px; font-weight:300; color:#86868f">=</p>
    <p style="font-size:40px; font-weight:600; color:#ffffff">Marketing spend</p>
    <p style="font-size:52px; font-weight:300; color:#86868f">&divide;</p>
    <p style="font-size:40px; font-weight:600; color:#ffffff">New customers won</p>
  </div>'''
  + "\n" + grid([
    ("Example", "PKR 600,000 &divide; 1,000 = PKR 600", "Spent on ads and influencers this month, for 1,000 first-time buyers.", "#ed0000"),
    ("Blended CAC", "All marketing &divide; all new customers", "Includes customers who found you for free. Looks better than it is.", "#55555f"),
    ("Paid CAC", "Ad spend &divide; customers from ads", "Only what the ads bought. Harder to measure, closer to the truth.", "#2a78d6"),
  ], 3, 500, 250, start=2)
  + "\n" + band(5, 790, 110, "<b>Is your CAC lower than what a customer's first order leaves you?</b>", size=30),
  """The formula first, then an example and the two versions.

CAC is what you spend on marketing divided by the new customers it brings. Existing customers do not count — you already paid for them.

Blended versus paid: blended divides all marketing by all new customers, including those who came from word of mouth or search. It flatters you. Paid CAC counts only what the ads bought, but relies on the ad platforms' attribution, which tends to over-claim.

The band question sets up the next slide: if the first order leaves less than the CAC, the customer only pays back if they come back.""")

pb = [("CAC paid", -600), ("After order 1", -320), ("After order 2", -40), ("After order 3", 240), ("After order 4", 520)]
k = 0.3
bars = []
for i, (lab, v) in enumerate(pb):
    L = 200 + i * 320; h = max(4, int(abs(v) * k))
    col = "#ed0000" if v < 0 else "#1baf7a"
    top = 280 - h if v >= 0 else 280
    vt = top - 44 if v >= 0 else 280 + h + 8
    vs = ("+" if v >= 0 else "&minus;") + format(abs(v), ",")
    bars.append(f'''  <div data-build-in="fade {i+1}" style="position:absolute; left:{L}px; top:360px; width:260px; height:520px">
    <p style="position:absolute; left:0px; top:0px; width:260px; font-size:24px; font-weight:600; color:#55555f; text-align:center">{lab}</p>
    <div style="position:absolute; left:50px; top:{top}px; width:160px; height:{h}px; background:{col}; border-radius:6px"></div>
    <p style="position:absolute; left:0px; top:{vt}px; width:260px; font-size:30px; font-weight:600; color:{col}; text-align:center; font-family:'JetBrains Mono', monospace">{vs}</p>
  </div>''')
labels = ""
S["payback"] = sec("payback", "#f5f5f6", "Repeat customers", "The first order rarely pays",
  '  <div style="position:absolute; left:128px; top:639px; width:1664px; height:2px; background:#131316"></div>\n'
  + "\n".join(bars)
  + "\n" + P(128, 282, 1664, 60, txt("Running total for one customer: CAC PKR 600, each order leaves PKR 280 of contribution", 28, "#55555f")),
  """Illustrative numbers, one bar per click.

Winning the customer costs PKR 600 (red, below the line). Each order leaves PKR 280 of contribution — revenue after product cost, packing, courier and fees. After one order the customer is still PKR 320 in the red. After two, PKR 40 in the red. Only the third order puts the seller ahead.

So a business whose customers buy once loses money on every customer it wins, however fast it grows. The customers who come back pay for the ones you bought.

Question for the room: how many times a year does someone buy shampoo? Toothpaste? A serum?""",
  footer="Illustrative numbers")

S["ltv"] = sec("ltv", "#ffffff", "Unit economics", "Three checks before you spend to grow",
  row3([
    ("Every order", "&gt; 0", "Contribution per order is positive: each sale leaves something after product, delivery and fees."),
    ("Every customer", "3 : 1", "Lifetime value is about three times CAC. LTV is the contribution a customer brings over their life, not revenue."),
    ("Every rupee", "&lt; 12 mo", "Marketing spend comes back as contribution within about a year. Longer, and cash runs out first."),
  ], 300, 380)
  + "\n" + band(4, 730, 120, "Rules of thumb that investors use, not laws. <b>Which of the three would your business fail first?</b>", size=30),
  """One check per click.

Contribution per order: if a single order loses money after product, packing, delivery and payment costs, growth makes things worse. Fix this before anything else.

LTV to CAC: lifetime value measured as contribution (not revenue) over the customer's life, divided by what it cost to win them. Around 3:1 is the rule of thumb investors quote; below 1:1 every customer loses money.

Payback: how many months until a customer's contribution repays their CAC. The shorter, the less cash you need.

These are widely used rules of thumb from venture investors, not laws — say so. A business with high repeat purchase can live with a lower first-order margin.""",
  footer="Common investor rules of thumb, not laws")

S["breakeven"] = sec("breakeven", "#f5f5f6", "Unit economics", "How many orders pay the fixed costs?",
  f'''  <div data-build-in="fade 1" style="position:absolute; left:128px; top:290px; width:1664px; height:170px; background:#131316; padding:36px 46px; border-radius:18px; display:flex; align-items:center; gap:30px">
    <p style="font-size:40px; font-weight:600; color:#ffffff">Fixed costs a month</p>
    <p style="font-size:52px; font-weight:300; color:#86868f">&divide;</p>
    <p style="font-size:40px; font-weight:600; color:#ffffff">What each order leaves after marketing</p>
    <p style="font-size:52px; font-weight:300; color:#86868f">=</p>
    <p style="font-size:40px; font-weight:600; color:#ff3b3b">Break-even orders</p>
  </div>'''
  + "\n" + row3([
    ("Fixed costs", "PKR 1.2m", "A small team, a warehouse and software, every month."),
    ("Left per order", "PKR 100", "The contribution after marketing from the PKR 1,000 order earlier."),
    ("Break-even", "12,000", "Orders a month &mdash; about 400 a day &mdash; before the first rupee of profit."),
  ], 500, 260, start=2)
  + "\n" + band(5, 790, 110, "<b>Would you rather double your orders, or double what each order leaves?</b>", size=30),
  """The formula, then an illustrative example.

With fixed costs of PKR 1.2 million a month and PKR 100 left per order after marketing, the business needs 12,000 orders a month — 400 a day — to break even.

Now double what each order leaves (a better price, cheaper delivery, a bigger basket): break-even halves to 6,000. Doubling orders at the same economics is usually far harder and costs more marketing.

That is the core of unit economics: improve the unit before you multiply it.""",
  footer="Illustrative numbers")

S["case-repeat"] = cases("case-repeat", "Cases &middot; Repeat customers",
  "Make coming back the default",
  ("Pakistan", "foodpanda pandapro", "2022",
   [("The problem", "Delivery fees made each order a fresh decision, and customers shopped around."),
    ("What they did", "A subscription from about Rs 167 a month: free deliveries and member discounts."),
    ("The lesson", "A member has already paid, so the next order goes to the app they subscribed to.")]),
  ("Global", "Chewy", "US pet supplies",
   [("The problem", "Pet food runs out on a schedule, and any shop can sell the same bag."),
    ("What they did", "Autoship: set a delivery rhythm once, and the order repeats with a small discount."),
    ("The result", "Autoship was 79% of Chewy's US$11.9bn of net sales in 2024.")]),
  "Both turned a product that <b>runs out</b> into an order that <b>repeats by itself</b>.",
  """Two repeat-purchase cases.

foodpanda pandapro (Pakistan, launched 2022): a delivery subscription — as low as about Rs 167 a month on the annual plan — giving free deliveries above a minimum order and member discounts. Once a customer has paid for the membership, the next order has a reason to go to foodpanda. Price and features change; check the current offer before quoting.

Chewy (US online pet supplies): Autoship lets a customer set the delivery rhythm once. In fiscal 2024, Autoship sales were 79.2% of net sales, about $9.4 billion of roughly $11.9 billion.

The link to the simulation's category: shampoo, soap, detergent and baby wipes run out on a schedule too.

Question for the room: what would "Autoship" look like for a Pakistani personal-care brand selling mostly on cash on delivery?

Sources: Business Recorder and foodpanda.pk (pandapro); Chewy FY2024 results.""",
  "Sources: Business Recorder, foodpanda.pk; Chewy FY2024 results")

S["case-unit"] = cases("case-unit", "Cases &middot; Unit economics",
  "Growth that loses money on every order",
  ("Pakistan", "B2B e-commerce", "2021&ndash;2024",
   [("The bet", "Deliver FMCG stock to kiryana shops through an app, and win on scale."),
    ("What happened", "Jugnu, Retailo and Dastgyr raised about US$161m between them."),
    ("The result", "Jugnu and Retailo shut operations in 2023; Dastgyr cut most of its staff.")]),
  ("Global", "MoviePass", "US, 2017&ndash;2019",
   [("The offer", "Unlimited cinema tickets for US$9.95 a month."),
    ("The catch", "It paid cinemas close to full price for every ticket: one film cost about the fee."),
    ("The result", "Over 3 million subscribers in a year, then it shut down in September 2019.")]),
  "More orders only help if each one <b>leaves something behind</b>. Scale multiplies the unit, good or bad.",
  """Two unit-economics failures.

Pakistan's B2B e-commerce wave: startups delivering FMCG stock to kiryana shops. Jugnu, Retailo and Dastgyr together raised about $161 million. FMCG distribution margins are thin and delivery costs are real; when funding tightened in 2022–23, Jugnu shut its core operations (July 2023), Retailo shut distribution (October 2023) and Dastgyr laid off around 80–85% of staff (January 2024). Reports blame thin margins and high costs as well as the economy.

MoviePass: $9.95 a month for unlimited films, while paying cinemas close to full price — the average US ticket was about $9. The subscription grew past three million within a year, and the company lost money on almost every active subscriber. It shut down in September 2019.

Tie back to the three checks: both failed the first — contribution per order.

Question for the room: which check would you have asked each founder about first?

Sources: Profit by Pakistan Today (2024); ProPakistani (2023); Deadline, Forbes (2019).""",
  "Sources: Profit (2024), ProPakistani (2023); Deadline, Forbes (2019)")

# ================================ PART 2 =====================================
S["part2"] = div("part2", "Part 2 &middot; The simulation",
  "Your first month<br>of trading",
  "Personal care and home care: the same five numbers, now read from your own report.",
  """Part 2 is the simulation. Month 1 has been run with each team's founding decisions. First, how the report's P&amp;L maps onto today's theory. Then a default month, for reference, and what price changes do in the simulation. Then the re-pricing workshop and the board memo.

Every number in Part 2 is from the simulation, not the real market. Say so once, clearly.""")

pnl_rows = [
  ("Net revenue", "Orders &times; average order, less refused parcels, returns and prepaid discounts", "Revenue"),
  ("Gross profit", "Net revenue less the product cost of what stayed sold", "Gross margin"),
  ("Contribution before marketing", "Less pick-and-pack, courier both ways on refusals, COD and card fees, commission", "Contribution"),
  ("Contribution", "Less all marketing, including CRM", "After marketing"),
  ("EBITDA", "Less payroll, warehouse, technology, research, stock holding", "Profit"),
]
S["sim-pnl"] = sec("sim-pnl", "#fdeceb", "In the simulation", "Reading your P&amp;L",
  trows(["Report line", "What is in it", "Today's word"], pnl_rows, 282, [480, 880, 248], rh=96, size=27)
  + "\n" + band(6, 830, 80, "Your report also shows <b>AOV, CAC, repeat share and LTV</b>: the customer half of the story.", size=28, extra="padding:20px 40px;"),
  """One line per click. This is the P&amp;L block in each team's monthly report, top to bottom, and the word from Part 1 that matches it.

Point out three things the simulation does that real businesses often forget:
- Net revenue takes out parcels refused at the door, so COD refusals hit revenue, not just cost.
- Refused parcels pay the courier twice, out and back, on their own line.
- CRM (retention) spend counts as marketing, so it sits above contribution.

Ask each team to open their month-1 report now, at the P&amp;L block.""",
  footer="Definitions from the simulation's KPI dictionary")

S["sim-baseline"] = sec("sim-baseline", "#f5f5f6", "In the simulation", "Where PKR 1,000 went in a default month",
  waterfall([
    ("Net revenue", 0, 1000, "total", 1),
    ("Product cost", 1000, 393, "cost", 2),
    ("Gross profit", 0, 393, "sub", 2),
    ("Packing, courier, refusals, fees", 393, 273, "cost", 3),
    ("Contribution before marketing", 0, 273, "sub", 3),
    ("Marketing", 273, 109, "cost", 4),
    ("Contribution", 0, 109, "sub", 4),
    ("Payroll, warehouse, tech", 109, -46, "cost", 5),
    ("EBITDA", 0, -46, "loss", 5),
  ], top=280, rh=54, gap=6, scale=1.0, zero=600)
  + "\n" + P(1000, 850, 792, 50, txt("Now find the same lines in your own report.", 26, "#55555f", 600), n=6),
  """A reference point: a team that kept every default decision, month 1. Per PKR 1,000 of net revenue: product cost 607, gross profit 393 (39%). Packing, courier (including both legs of refused parcels) and COD or card fees take 120, leaving 273 before marketing. Marketing takes 164, leaving 109. Fixed costs take 155. The default business loses about PKR 46 in every 1,000.

Compare with Exercise 1 and the illustrative slide in Part 1: the shape is the same.

Then ask: which line is your team furthest from the default on, and was that a choice?

These numbers are the simulation's baseline run, not market data.""",
  footer="Simulation baseline: all default decisions, month 1 &middot; not market data")

cat_rows = [("Skincare", "34&ndash;43%", "PKR 690&ndash;2,890", "Light, high-value; the serum carries the most margin"),
            ("Haircare", "36&ndash;39%", "PKR 840&ndash;1,890", "Steady margins, bought on a rhythm"),
            ("Baby", "35&ndash;38%", "PKR 890&ndash;1,340", "Trust-led; parents repeat what works"),
            ("Hygiene", "31&ndash;35%", "PKR 390&ndash;980", "Low prices: one courier trip eats a big share"),
            ("Homecare", "32&ndash;34%", "PKR 440&ndash;1,490", "Heavy and cheap; bundles make it pay")]
S["sim-shelf"] = sec("sim-shelf", "#ffffff", "In the simulation", "Not every product earns the same",
  trows(["Category", "Gross margin", "List prices", "What it means for an order"], cat_rows, 282, [300, 280, 360, 668], rh=90, size=27)
  + "\n" + band(6, 790, 110, "A PKR 440 air freshener pays the same PKR 145&ndash;210 courier as a PKR 2,890 serum. <b>Which of your lines lose money alone?</b>", size=28),
  """One category per click. Gross margins are at list price with standard sourcing, from the simulation's catalogue. Courier costs are the simulation's three couriers, PKR 145 to 210 per order.

The lesson for the teams: margin percentage is not the whole story. A cheap product with a 32% margin leaves about PKR 140 of gross profit — less than the courier. It only makes money inside a bigger basket. A serum leaves over PKR 1,200.

This is why bundles and free-delivery thresholds open in Session 5.""",
  footer="Simulation catalogue, list prices and standard sourcing &middot; not market data")

S["sim-unit"] = sec("sim-unit", "#f5f5f6", "In the simulation", "Customer economics in a default month",
  row4([
    ("CAC", "PKR 630", "Marketing spend divided by the new customers it won."),
    ("Per order", "PKR 700", "Contribution before marketing on each order placed."),
    ("Repeat share", "33%", "Of orders came from customers who had bought before."),
    ("LTV : CAC", "1.9 : 1", "Lifetime contribution about PKR 1,180, against the 3 : 1 rule."),
  ], 290, 360)
  + "\n" + band(5, 700, 180, "The default business wins customers at roughly what one order leaves, and gets back less than twice its spend. <b>What would move your LTV : CAC toward 3?</b>", size=30),
  """One number per click, all from the simulation's default run, month 1, rounded.

CAC about PKR 630. Each order leaves about PKR 700 before marketing, so a new customer's first order roughly repays their acquisition. Repeat share is a third. Lifetime value, on the simulation's contribution basis, is about PKR 1,180, so LTV to CAC is about 1.9 — below the 3:1 rule of thumb.

Now ask each team to read their own four numbers from the report and compare.

The levers: a higher price or bigger basket raises contribution per order; better targeting lowers CAC (Session 7); retention raises repeat share (Session 8). Today's lever is price.""",
  footer="Simulation baseline: all default decisions, month 1 &middot; not market data")

prow = [("No change", "3,264", "PKR 3.28m", "PKR 0.88m"), ("10% off everything", "3,396 &nbsp;(+4%)", "PKR 2.54m &nbsp;(&minus;22%)", "PKR 0.12m &nbsp;(&minus;87%)"),
        ("20% off everything", "3,538 &nbsp;(+8%)", "PKR 1.74m &nbsp;(&minus;47%)", "&minus;PKR 0.71m")]
S["sim-price"] = sec("sim-price", "#fdeceb", "In the simulation", "What a discount did in month 1",
  trows(["Same team, same month", "Orders", "Gross profit", "Contribution"], prow, 282, [520, 340, 400, 348], rh=110, size=30)
  + "\n" + band(4, 720, 170, "Ten percent off won 4% more orders and wiped out almost all of the month's contribution. <b>Which of your lines could take a higher price instead?</b>", size=30),
  """One row per click. We ran the simulation's first month three times: a team on every default, the same team with 10% off everything, and with 20% off. Everything else unchanged.

10% off: 4% more orders, gross profit down 22%, contribution down 87%. 20% off: 8% more orders, contribution negative.

Compare with the discount table in Part 1: at a 39% margin, 10% off needed about a third more volume. It got 4%. The simulation's customers do respond to price — especially Value Seekers and Deal Hunters — but not by enough to pay for a blanket cut.

This does not mean never discount. Line-by-line discounting, on products your segments are price-sensitive about, is Session 5.

Simulation results from a test run; they will differ slightly for each team's own setup.""",
  footer="Simulation test run, month 1, all else default &middot; not market data")

# ================================ WORKSHOP ===================================
qs = ["Which three lines carry most of your gross profit?", "Which line sells well but leaves almost nothing?", "Where would a 5% higher price hurt least?", "Does your quality position match your prices?"]
S["ex2"] = f'''<section id="ex2" data-transition="push" style="background:#fdeceb; color:#131316; {FONT}; padding:128px 128px 160px; display:flex; flex-direction:column; gap:40px">
  <p style="font-size:26px; font-weight:600; letter-spacing:4px; text-transform:uppercase; color:#ed0000">Exercise 2</p>
  <h2 style="font-size:88px; font-weight:700; letter-spacing:-2px; line-height:1.05">Re-price your shelf</h2>
  <p style="font-size:34px; line-height:1.45; color:#55555f; width:1500px">Your month-1 report is open at the P&amp;L. Four questions before you change a single price.</p>
''' + "\n".join(f'''  <div data-build-in="fade {i+1}" style="position:absolute; left:{128 + (i%2)*845}px; top:{480 + (i//2)*200}px; width:819px; height:180px; background:#ffffff; padding:34px 38px; border-radius:16px; border:1px solid #f2c9c6; display:flex; flex-direction:column; gap:10px">
    <p style="font-size:26px; font-weight:600; color:#ed0000; font-family:'JetBrains Mono', monospace">Q{i+1}</p>
    <p style="font-size:31px; font-weight:600; line-height:1.3">{q}</p>
  </div>''' for i, q in enumerate(qs)) + f'''
  {FOOT.format("Exercise 2 &middot; decisions 1.1 range, prices and sourcing &middot; 1.5 quality position")}
  <aside>Eighteen minutes, in teams. One question per click.

Teams work from their own month-1 report and the price grid on decision 1.1, which shows the margin on each line as they type. Decision 1.5 (quality position) is open too.

Q1: most teams find two or three lines carry most of the gross profit. Protect those.
Q2: the popular, low-margin line — often a homecare or hygiene product. Price it up, or accept it as a basket-builder.
Q3: the lines where their segments care least about price (Quality Loyalists, Premium/Gifting) can take an increase.
Q4: premium quality with economy prices reads as confusion, not a bargain — the handbook says so.

Take two teams' answers to Q2 at the end. Then they enter the new prices on the decision form for month 2.</aside>
</section>
'''

S["memo"] = sec("memo", "#ffffff", "In the simulation", "The board memo",
  grid([
    ("1", "What did you decide?", "The prices you changed, the quality position, and anything you chose not to change.", "#ed0000"),
    ("2", "Why?", "The number in your month-1 report that made you do it.", "#ed0000"),
    ("3", "How will you know?", "The line in next month's P&amp;L that proves you right or wrong, and by how much.", "#ed0000"),
  ], 3, 300, 300)
  + "\n" + band(4, 660, 160, "Decision 12.5 &middot; 400 words, 10% of the final score. <b>Could a board member check your memo against next month's report?</b>", size=30),
  """One question per click. The board memo is decision 12.5 — 400 words, and it counts for 10% of the final score.

The rubric rewards a decision tied to evidence and a prediction that can be checked. "We raised prices because margins matter" scores low. "Gross margin was 34%, below our 38% target, driven by homecare; we raised the three homecare lines by 6% and expect gross margin above 36% with orders down no more than 5%" scores high.

Remind them: the memo is written for the board, and the board reads next month's report.""",
  footer="Decision 12.5 &middot; board memo")

S["checks"] = sec("checks", "#f5f5f6", "Before month 2 runs", "Four questions before you submit",
  grid([
    ("Margin", "Does every line cover its courier?", "Or does it only earn inside a bigger basket?", "#ed0000"),
    ("Price", "Does the price match the promise?", "Premium quality with bargain prices confuses the market.", "#eb6834"),
    ("Customer", "Who did you price for?", "Your priority segments care about price by different amounts.", "#2a78d6"),
    ("Proof", "What will prove you right?", "One number in next month's P&amp;L, written in the memo.", "#1baf7a"),
  ], 4, 300, 330)
  + "\n" + band(5, 690, 150, "Next session, the report will tell you whether your prices worked. <b>What will you be looking for first?</b>", size=30),
  """One check per click. Use these while teams finish the decision form.

Logistics for the notes, not the slide: decisions for month 2 close at [deadline]. Prices (1.1), quality position (1.5) and the board memo (12.5) are open this round.""")

S["next"] = sec("next", "#131316", "Next session", "Building your online store",
  grid([
    ("Session 4", "Why do visitors leave without buying?", "Conversion rate becomes a number you own.", "#ff3b3b"),
    ("Your store", "What would make you trust a new brand?", "Website experience, packaging and the payment gateway open next.", "#ff3b3b"),
    ("Your numbers", "Did your new prices work?", "Month 2's P&amp;L is the first test of today's decisions.", "#ff3b3b"),
  ], 3, 300, 300, bg="#1f1f24", border="border:1px solid #33333b;", tcol="#ffffff", bcol="#c9c9d1")
  + "\n" + band(4, 660, 150, "Today you learned what an order leaves behind. Next time: <b>how to turn more visitors into orders</b>.", bg="#ed0000", size=31),
  """Close. One card per click.

Session 4 is the online store: website experience (5.1), packaging (8.5) and the payment gateway (9.3) open. Conversion rate becomes theirs.

Before next session: month 2 runs with their new prices, and the report will be the first test of today's decisions.""", dark=True, eyecol="#ff3b3b")

ORDER = ["cover", "recall", "ex1", "part1", "revenue", "netrev", "costs", "margins", "case-revenue",
         "pricing", "discount", "case-pricing", "cac", "payback", "ltv", "breakeven", "case-repeat", "case-unit",
         "part2", "sim-pnl", "sim-baseline", "sim-shelf", "sim-unit", "sim-price", "ex2", "memo", "checks", "next"]
assert set(ORDER) == set(S), set(S) ^ set(ORDER)
root = pathlib.Path(sys.argv[1]) / "project"
(root / "slides").mkdir(parents=True, exist_ok=True)
for k, v in S.items():
    (root / "slides" / f"{k}.html").write_text(v)
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-09-29T09:00:00Z"},
        "title": "Session 3 — How Will You Make Money?", "order": ORDER,
        "sections": {
          "open": {"description": "How will you make money, and what we covered last week", "start": "cover"},
          "revenue": {"description": "Part 1 · Revenue, costs and margins, with cases", "start": "part1"},
          "pricing": {"description": "Pricing, with cases", "start": "pricing"},
          "customers": {"description": "Customer acquisition cost, repeat customers and unit economics, with cases", "start": "cac"},
          "sim": {"description": "Part 2 · The simulation: your first month's P&L and prices", "start": "part2"},
          "workshop": {"description": "Re-price the shelf and write the board memo", "start": "ex2"}},
        "faces": {"inter": {"family": "Inter", "href": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono"}},
        "designSystems": []}
if not (root / "deck.json").exists():
    (root / "deck.json").write_text(json.dumps(deck, indent=2, ensure_ascii=False))
print("wrote", len(S))
