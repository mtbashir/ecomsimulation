"""New and rewritten Session 2 slides (theory first, simulation after)."""
import pathlib, sys, json
D = pathlib.Path(sys.argv[1]) / "project"
S = D / "slides"
FONT = "font-family:Inter, Arial, sans-serif"
FOOT = '<p style="position:absolute; left:128px; bottom:64px; font-size:24px; color:#86868f">{}</p>'
EYEB = '<p style="font-size:26px; font-weight:600; letter-spacing:4px; text-transform:uppercase; color:{}">{}</p>'
H2 = '<h2 style="font-size:72px; font-weight:700; letter-spacing:-1.5px{}">{}</h2>'

def section(sid, bg, ink, eyebrow, title, body, notes, footer="Session 2 &middot; Finding the Right Idea",
            eyecol="#ed0000", dark=False):
    tcol = "; color:#ffffff" if dark else ""
    return f'''<section id="{sid}" data-transition="fade" style="background:{bg}; color:{ink}; {FONT}; padding:128px 128px 160px; display:flex; flex-direction:column; gap:14px">
  {EYEB.format(eyecol, eyebrow)}
  {H2.format(tcol, title)}
{body}
  {FOOT.format(footer)}
  <aside>{notes}</aside>
</section>
'''

def card(n, L, T, W, H, label, title, text, col="#86868f", bg="#ffffff", border="border:1px solid #e4e4e7;",
         tcol="#131316", bcol="#55555f", pad="30px 34px", tsize=31, bsize=25):
    lab = f'<p style="font-size:22px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:{col}">{label}</p>' if label else ""
    return f'''  <div data-build-in="fade {n}" style="position:absolute; left:{L}px; top:{T}px; width:{W}px; height:{H}px; background:{bg}; padding:{pad}; border-radius:18px; {border} display:flex; flex-direction:column; gap:8px">
    {lab}
    <h3 style="font-size:{tsize}px; font-weight:600; line-height:1.25; color:{tcol}">{title}</h3>
    <p style="font-size:{bsize}px; line-height:1.4; color:{bcol}">{text}</p>
  </div>'''

def band(n, T, H, text, bg="#131316", col="#ffffff", size=30, extra=""):
    return f'''  <div data-build-in="fade {n}" style="position:absolute; left:128px; top:{T}px; width:1664px; height:{H}px; background:{bg}; padding:28px 40px; border-radius:18px; {extra}">
    <p style="font-size:{size}px; line-height:1.4; color:{col}">{text}</p>
  </div>'''

def grid(items, cols, top, h, gap=26, start=1, **kw):
    w = (1664 - gap * (cols - 1)) // cols
    out = []
    for i, it in enumerate(items):
        L = 128 + (i % cols) * (w + gap); T = top + (i // cols) * (h + 20)
        out.append(card(start + i, L, T, w, h, *it, **kw))
    return "\n".join(out)

slides = {}

# --- 1. Finding customer problems ----------------------------------------------------
slides["problems"] = section("problems", "#f5f5f6", "#131316", "Finding customer problems",
  "Where real customer problems show up",
  grid([
    ("Reviews", "One- to three-star reviews", "On marketplaces and rivals' pages: what buyers expected and did not get.", "#2a78d6"),
    ("Search", "What people type", "Google and marketplace searches, and the ones that return nothing worth buying.", "#eb6834"),
    ("Conversations", "Comments and messages", "Instagram comments and WhatsApp questions: “COD hai?”, “which size?”, “original hai?”", "#1baf7a"),
    ("Returns", "Why things come back", "Every return and refused parcel is a customer telling you what went wrong.", "#b3231e"),
    ("Workarounds", "What they do instead", "Asking relatives abroad, buying wholesale, a cousin's shop. A workaround is demand nobody serves.", "#8a6414"),
    ("Your own life", "The thing you could not buy", "A starting point, not proof. One person's irritation is a data point, not a market.", "#55555f"),
  ], 3, 290, 236)
  + "\n" + band(7, 802, 118, "A problem worth building on shows up in <b>more than one</b> of these places.", size=31),
  """One source per click. This is the real-world method: founders do not invent problems, they find them where customers already complain, search or improvise.

Reviews: the most honest free research there is. Read the one- to three-star reviews of the best-selling products in a category; the same complaint five times is a product brief.

Search: what people type, and especially searches where the results are poor or out of stock.

Conversations: in Pakistan, WhatsApp and Instagram comments are where buying questions are asked. "COD hai?" and "original hai?" are trust problems, not product problems — and they are opportunities too.

Returns: every refused parcel is a message. Why did the customer change their mind at the door?

Workarounds: the strongest signal of all. If people ask relatives abroad to bring something back, there is unmet demand.

Your own life: where the opening exercise started. It is a start, not evidence.

Question for the room: which of these could you check tonight for the idea you wrote down?""")

# --- 2. Identifying opportunities ----------------------------------------------------
slides["sizing"] = section("sizing", "#ffffff", "#131316", "Identifying opportunities",
  "Big enough, often enough, profitable enough",
  grid([
    ("How many", "People who have the problem", "And can be reached online, will pay online or on delivery, and live where couriers go.", "#2a78d6"),
    ("How often", "Once, or every month?", "A product bought again and again pays back the cost of finding the customer many times over.", "#1baf7a"),
    ("How much is left", "Margin after everything", "After product cost, delivery, cash handling, returns and the cost of winning the order.", "#ed0000"),
  ], 3, 300, 330)
  + "\n" + band(4, 660, 150, "Would you rather have <b>1,000 customers who buy once</b>, or <b>300 who buy every month</b>?", size=36),
  """Three multipliers, one per click. An opportunity is the product of all three; a zero in any one of them is a zero overall.

How many: not the population, the reachable online buyers with the problem. In Pakistan that means people who buy online at all, can pay (cash on delivery counts), and live where couriers reliably deliver.

How often: the most underrated number in e-commerce. Consumables and refills are bought again; a one-off purchase has to pay back all of its acquisition cost on the first order.

How much is left: the gross margin is not the margin. Delivery, cash-on-delivery handling, returns and the marketing that won the order all come out of it.

The last click is a question to put to the room. Let them argue it: 300 monthly buyers is 3,600 orders a year from customers you only paid to find once.""")

# --- 3. Choosing products ---------------------------------------------------------
slides["products"] = section("products", "#f5f5f6", "#131316", "Choosing products",
  "What makes a product good to sell online",
  grid([
    ("1", "Bought again", "Consumables and refills bring the same customer back without paying for them twice.", "#ed0000"),
    ("2", "Carries its delivery", "A low-price item cannot absorb the courier, cash handling and returns.", "#ed0000"),
    ("3", "Easy to ship", "Light, unbreakable, no cold chain, fits a standard parcel.", "#ed0000"),
    ("4", "Hard to get wrong", "Few sizes or fits to choose between, so fewer returns.", "#ed0000"),
    ("5", "Trusted from a photo", "Sealed, branded or reviewable, so buying unseen feels safe.", "#ed0000"),
    ("6", "Room to stand out", "Not the identical item every marketplace seller already lists.", "#ed0000"),
  ], 3, 290, 236)
  + "\n" + band(7, 802, 118, "How many of the six does your idea pass &mdash; and which one would you fix first?", size=31),
  """Six tests, one per click. These are the traits experienced online sellers look for before choosing a range.

Bought again: repeat purchase is what makes customer acquisition affordable.

Carries its delivery: in Pakistan, courier fees, cash-on-delivery handling and the cost of refused parcels are close to fixed per order. On a cheap item they eat the margin entirely; this is why so many low-ticket online stores lose money on every order.

Easy to ship: weight, fragility and cold chain add cost and damage.

Hard to get wrong: apparel and footwear have high return rates because of fit. Categories with few variants return less.

Trusted from a photo: the customer cannot touch it. Sealed branded goods and products with reviews convert better.

Room to stand out: if twenty sellers list the same item, the only lever left is price.

The last click is a question for each team about their own idea.""")

slides["range"] = section("range", "#ffffff", "#131316", "Choosing products",
  "Start with a range you can explain in one sentence",
  grid([
    ("Hero", "One product people search for", "The reason a customer finds you. It carries the marketing and earns the reviews.", "#ed0000"),
    ("Companions", "A few close companions", "Same buyer, same basket: what they add to the order once they are there.", "#2a78d6"),
    ("Expansion", "New categories only after repeat", "Add a category when the first one brings customers back, not before.", "#1baf7a"),
  ], 3, 300, 300)
  + "\n" + band(4, 630, 180, "A wide range spreads stock, cash and marketing thin. A narrow one leaves demand on the table. <b>Which would you rather fix later?</b>", size=34),
  """Three parts of a first range, one per click.

Hero: most successful online brands start with one product customers search for by name or need. It gets the marketing budget and the reviews.

Companions: products the same customer adds to the same basket. They lift the average order without needing new customers.

Expansion: add categories when the first one shows repeat purchase. Expanding early multiplies the stock you must hold and the cash tied up in it.

The last click is the trade-off, posed as a question. Most first-time founders over-extend the range; it is easier to add a line later than to clear dead stock.""")

# --- 4. Understanding the target customer ---------------------------------------------
slides["persona"] = section("persona", "#f5f5f6", "#131316", "Understanding the target customer",
  "Describe one customer, not a crowd",
  f'''  <div data-build-in="fade 1" style="position:absolute; left:128px; top:290px; width:760px; height:560px; background:#131316; padding:40px 44px; border-radius:18px; display:flex; flex-direction:column; gap:14px">
    <p style="font-size:22px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:#ff6b6b">Illustrative profile</p>
    <h3 style="font-size:40px; font-weight:700; color:#ffffff">Sana, 31, Lahore</h3>
    <p style="font-size:26px; line-height:1.45; color:#c9c9d1">Works full time, two young children. Buys household and baby products online because the nearest good shop is a drive away.</p>
    <p style="font-size:26px; line-height:1.45; color:#c9c9d1"><b style="color:#ffffff">Finds you</b> on Instagram, asks on WhatsApp. <b style="color:#ffffff">Trusts</b> sealed brands, reviews and cash on delivery. <b style="color:#ffffff">Pays</b> a little more for delivery in two days. <b style="color:#ffffff">Comes back</b> every month if nothing goes wrong.</p>
  </div>
''' + "\n".join(card(i + 2, 918, 290 + i * 116, 874, 100, "", q, a, pad="18px 28px", tsize=27, bsize=23)
                 for i, (q, a) in enumerate([
    ("Who pays, and for whom?", "The buyer is often not the user."),
    ("What triggers the purchase?", "Running out, a season, an occasion, a recommendation."),
    ("Where do they discover and ask?", "Search, Instagram, WhatsApp, the marketplace."),
    ("What makes them trust a new seller?", "Reviews, COD, easy returns, a brand they know."),
    ("What would they pay, and how often?", "Price and frequency together decide value."),
  ])),
  """First click: an illustrative customer profile, not real data. Make clear it is a teaching example; teams should build their own from conversations and research.

Then the five questions a useful customer profile answers, one per click. The answers matter more than demographics: two women of 31 in Lahore can be completely different customers.

Who pays: in household and baby products the buyer is usually buying for others.

Trigger: replenishment, season, occasion. Triggers tell you when to advertise.

Discovery: tells you which channel to spend on — this is the bridge to the marketing sessions.

Trust: in Pakistan, cash on delivery and returns are trust signals as much as payment options.

Price and frequency: together they are the customer's value over a year.

Question for the room: who is the one customer for the idea you wrote down at the start?""")

slides["target"] = section("target", "#ffffff", "#131316", "Understanding the target customer",
  "Choose the segment you can win",
  grid([
    ("Worth having", "Size, frequency and margin together", "A small segment that buys every month can be worth more than a big one that buys once.", "#2a78d6"),
    ("Able to serve", "What they value is what you do best", "If they weigh delivery speed most, your courier is your product.", "#1baf7a"),
    ("Room to win", "Who serves them today, and how well", "A large, loyal segment that everyone already serves well is the hardest to win.", "#eb6834"),
  ], 3, 300, 330)
  + "\n" + band(4, 660, 150, "Which segment is <b>worth having, within your reach, and badly served today?</b>", size=36),
  """Three tests for choosing a target segment, one per click. This is standard segment-attractiveness thinking, adapted to e-commerce.

Worth having: size alone misleads. Multiply by how often they buy and what margin they leave.

Able to serve: match what the segment weighs most to what you can actually deliver. A segment that values speed needs your operations to be excellent.

Room to win: the best segment on paper may be the most contested. Look for customers who are poorly served.

The last click is the question every team should answer before the founding workshop.""")

# --- 5. In the simulation --------------------------------------------------------
cats = [
  ("Skincare", "Facewash, moisturiser, serum, sunscreen, face mask"),
  ("Haircare", "Shampoo, conditioner, hair oil, hair serum"),
  ("Hygiene", "Body wash, soap, sanitiser, deodorant, toothpaste"),
  ("Homecare", "Dish liquid, surface cleaner, laundry liquid, air freshener"),
  ("Baby", "Baby lotion, baby wipes"),
]
catcards = "\n".join(card(i + 1, 128 + i * 337, 360, 314, 250, "", c, p, pad="28px 28px", tsize=31, bsize=24)
                     for i, (c, p) in enumerate(cats))
facts = [("20", "products"), ("PKR 390&ndash;2,890", "price range"), ("PKR 12m", "to start"), ("12", "trading months"), ("Rivals", "other teams and computer-run competitors")]
factrow = "".join(f'<div style="display:flex; flex-direction:column; gap:4px; width:{w}px"><p style="font-size:34px; font-weight:700; color:#ffffff; font-family:\'JetBrains Mono\', monospace">{a}</p><p style="font-size:22px; color:#c9c9d1">{b}</p></div>'
                  for (a, b), w in zip(facts, (170, 360, 220, 230, 460)))
slides["simmarket"] = section("simmarket", "#fdeceb", "#131316", "In the simulation",
  "The market you will run",
  f'''  <p style="position:absolute; left:128px; top:282px; width:1664px; font-size:30px; line-height:1.4; color:#55555f">An online personal-care and home-care business in Pakistan, selling to shoppers across the country.</p>
{catcards}
  <div data-build-in="fade 6" style="position:absolute; left:128px; top:640px; width:1664px; height:150px; background:#131316; padding:28px 40px; border-radius:18px; display:flex; gap:40px; align-items:center">{factrow}</div>
  <div data-build-in="fade 7" style="position:absolute; left:128px; top:812px; width:1664px; height:96px">
    <p style="font-size:30px; line-height:1.4">Everyday products people buy again and again &mdash; and every team starts from the same catalogue, the same capital and the same customers.</p>
  </div>''',
  """This is the first time the room sees the simulation's market, so slow down.

The business: an online personal-care and home-care seller in Pakistan. Five categories, one per click, twenty products in total, from a PKR 390 hand sanitiser to a PKR 2,890 serum.

The black band: PKR 12 million of starting capital, twelve trading months, and rivals — the other teams in the room plus computer-run competitors.

Why this category: it passes most of the product tests from earlier. Products are bought again, easy to ship, hard to get wrong and trusted from a photo. The hard part is that ticket sizes are modest, so delivery and returns bite, and every seller can list the same items, so positioning matters.

Each team will choose two of the five categories, a quality position, who to sell to and how to spend the capital. The next slide maps today's theory onto those choices.""",
  eyecol="#ed0000", footer="The simulation's market &middot; products and prices from the simulation catalogue")

rows = [("Customer problems", "Your brand and the objective you promise the board"),
        ("Opportunity", "Which two of the five categories you enter"),
        ("Choosing products", "Your range, its prices, and where each line is sourced"),
        ("Target customer", "The segments you serve and your quality position"),
        ("Where to start", "Own site, hybrid or marketplace first")]
maprows = "\n".join(f'''  <div data-build-in="fade {i + 1}" style="position:absolute; left:128px; top:{290 + i * 112}px; width:1664px; height:96px; background:#ffffff; border:1px solid #e4e4e7; border-radius:16px; display:flex; align-items:center; padding:0 36px; gap:30px">
    <p style="font-size:30px; font-weight:700; width:520px">{a}</p>
    <p style="font-size:30px; color:#ed0000; width:60px">&rarr;</p>
    <p style="font-size:30px; color:#55555f">{b}</p>
  </div>''' for i, (a, b) in enumerate(rows))
slides["simmap"] = section("simmap", "#f5f5f6", "#131316", "In the simulation",
  "Today's theory becomes your founding decisions",
  maprows + "\n" + band(6, 862, 58, "", bg="#f5f5f6").replace('<p style="font-size:30px; line-height:1.4; color:#ffffff"></p>', ''),
  """One mapping per click. Each part of today's theory is a decision on the founding form this afternoon.

Customer problems become the brand and the objective each team promises the board.
Opportunity becomes the two categories they enter.
Choosing products becomes the range, prices and sourcing per product.
Target customer becomes segment priority and quality position.
The channel map from the start of the session becomes own site, hybrid or marketplace first.

Then turn to the simulation's customers: the next slide is its segment table.""")
# the empty band above was only a spacer; drop it
slides["simmap"] = slides["simmap"].replace(band(6, 862, 58, "", bg="#f5f5f6").replace('<p style="font-size:30px; line-height:1.4; color:#ffffff"></p>', ''), "")

for sid, html in slides.items():
    (S / f"{sid}.html").write_text(html)
print("wrote", list(slides))
