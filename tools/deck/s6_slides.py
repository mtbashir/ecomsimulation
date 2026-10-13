"""Session 6 - Where Will You Sell? About 23 slides, with page snapshots.

Run: python s6_slides.py <deck folder> [logo url] [shots.json]
shots.json maps a snapshot key (see SHOTS) to the published image url of that
page's screenshot; a key without one renders as a labelled empty frame.
"""
import pathlib, sys, json
HERE = pathlib.Path(__file__).parent
exec((HERE / "s5_slides.py").read_text().split("\nS = {}\n")[0])
FT = "Session 6 &middot; Where Will You Sell?"
def sec(sid, bg, eyebrow, title, body, notes, footer=FT, **kw):
    return section(sid, bg, "#131316", eyebrow, title, body, notes, footer=footer, **kw)
def div(sid, part, title, line, notes):
    return divider(sid, part, title, line, notes).replace("Session 2 &middot; Finding the Right Idea", FT).replace("856d57cb939a323d46943b3b229572d7", "__LOGO__")

# --- Page snapshots ------------------------------------------------------------------
# key: (address shown in the browser bar, the page to capture)
SHOTS = {
    "sg-site":   ("saeedghani.pk", "https://saeedghani.pk"),
    "sg-daraz":  ("daraz.pk/saeed-ghani", "https://www.daraz.pk/saeed-ghani/"),
    "sg-insta":  ("instagram.com/saeedghani", "Instagram profile of Saeed Ghani"),
    "daraz":     ("daraz.pk", "https://www.daraz.pk"),
    "amazon":    ("amazon.com", "An Amazon product page showing 'Sold by' a third-party seller"),
    "conatural": ("conaturalintl.com", "https://conaturalintl.com"),
    "nike":      ("nike.com", "https://www.nike.com"),
    "markaz":    ("markaz.app", "https://www.markaz.app (or the app's catalogue)"),
    "meesho":    ("meesho.com", "https://www.meesho.com"),
    "khaadi":    ("pk.khaadi.com", "https://pk.khaadi.com"),
    "target":    ("target.com", "Target's Order Pickup / Drive Up page"),
}
IMG = json.loads(pathlib.Path(sys.argv[3]).read_text()) if len(sys.argv) > 3 else {}

def frame(key, W, H, tag=None):
    """A browser window holding the page snapshot (or an empty labelled frame)."""
    addr = SHOTS[key][0]
    chip = (f'<p style="font-size:16px; font-weight:600; letter-spacing:1.5px; text-transform:uppercase; '
            f'color:#ffffff; background:#131316; padding:3px 10px; border-radius:6px">{tag}</p>') if tag else ""
    if key in IMG:
        body = f'<img src="{IMG[key]}" alt="{addr}" style="width:{W}px; height:{H - 38}px; object-fit:cover; object-position:top; display:block">'
    else:
        body = (f'<div style="width:{W}px; height:{H - 38}px; background:#f5f5f6; display:flex; flex-direction:column; '
                f'align-items:center; justify-content:center; gap:8px">'
                f'<p style="font-size:17px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:#86868f">Page snapshot</p>'
                f'<p style="font-size:22px; color:#55555f; font-family:\'JetBrains Mono\', monospace">{addr}</p></div>')
    return (f'<div style="width:{W}px; height:{H}px; border:1px solid #d4d4d8; border-radius:12px; overflow:hidden; background:#ffffff; flex:0 0 auto">'
            f'<div style="height:38px; background:#ececef; display:flex; align-items:center; gap:7px; padding:0px 14px; border-bottom:1px solid #d4d4d8">'
            f'<div style="width:11px; height:11px; border-radius:6px; background:#ed6a5e"></div>'
            f'<div style="width:11px; height:11px; border-radius:6px; background:#f5bf4f"></div>'
            f'<div style="width:11px; height:11px; border-radius:6px; background:#61c554"></div>'
            f'<p style="margin-left:12px; flex:1; font-size:17px; color:#55555f; background:#ffffff; border-radius:6px; padding:3px 12px; '
            f'font-family:\'JetBrains Mono\', monospace">{addr}</p>{chip}</div>{body}</div>')

def shot_card(n, L, where, name, meta, key, rows, tagcol, T=272, W=819, H=560, fh=276):
    rows_html = "\n".join(
        f'''    <div style="display:flex; flex-direction:column; gap:2px">
      <p style="font-size:18px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:#86868f">{k}</p>
      <p style="font-size:23px; line-height:1.36; color:#33333b">{v}</p>
    </div>''' for k, v in rows)
    return f'''  <div data-build-in="fade {n}" style="position:absolute; left:{L}px; top:{T}px; width:{W}px; height:{H}px; background:#ffffff; padding:22px 26px; border-radius:18px; border:1px solid #e4e4e7; display:flex; flex-direction:column; gap:12px">
    <div style="display:flex; align-items:baseline; gap:16px">
      <p style="font-size:19px; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:{tagcol}">{where}</p>
      <h3 style="font-size:32px; font-weight:700; color:#131316">{name}</h3>
      <p style="font-size:21px; color:#86868f">{meta}</p>
    </div>
    {frame(key, W - 54, fh)}
{rows_html}
  </div>'''

def shot_cases(sid, eyebrow, title, pk, gl, lesson, notes, footer):
    body = (shot_card(1, 128, *pk, "#ed0000") + "\n" + shot_card(2, 973, *gl, "#2a78d6")
            + "\n" + band(3, 850, 68, lesson, size=26, extra="padding:16px 36px;"))
    return section(sid, "#f5f5f6", "#131316", eyebrow, title, body, notes, footer=footer)

S = {}
S["cover"] = f'''<section id="cover" data-transition="fade" style="background:#131316; color:#ffffff; {FONT}; padding:128px 128px 160px; display:flex; flex-direction:column; justify-content:space-between">
  {LOGO}
  <div style="display:flex; flex-direction:column; gap:28px">
    <p style="font-size:28px; font-weight:600; letter-spacing:4px; text-transform:uppercase; color:#ff3b3b">Session 6 of 12</p>
    <h1 style="font-size:132px; font-weight:700; line-height:1.02; letter-spacing:-3px">Where Will<br>You Sell?</h1>
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
  <p data-build-in="fade 1" style="position:absolute; left:128px; top:647px; width:1400px; height:110px; font-size:38px; line-height:1.45; color:#c9c9d1">Daraz, your own website, Instagram and WhatsApp: marketplaces, social commerce and omnichannel &mdash; and how to choose the mix.</p>
  <aside>Two hours, about 23 slides: 3 min recap, 8 min opening exercise on real pages, Part 1 theory about 60 min (four places to sell 10, marketplace against own site 15, social commerce 10, omnichannel 10, channel strategy and conflict 15), exercise 10, Part 2 simulation about 30 min, 3 min close.

Month 4 has run. Today's decision (4.1, sell on the marketplace) opens for month 5.

The idea for the day: a marketplace rents you its shoppers; your own site lets you keep them. Most brands end up using both, on purpose.</aside>
</section>
'''

S["recall"] = sec("recall", "#f5f5f6", "Where we got to last week", "The shelf decides what each order is worth",
  grid([
    ("Range", "Every product has a job", "Stars, traffic builders, basket fillers and margin makers.", "#ed0000"),
    ("Price", "Good, better, best", "Customers judge a price by what is shown next to it.", "#eb6834"),
    ("Offers", "Discount the line, not the shop", "Cost = discount &times; share of sales. Packs at a small saving.", "#2a78d6"),
  ], 3, 300, 300)
  + "\n" + band(4, 660, 170, "Last week: <b>what</b> is on the shelf and at what price. Today: <b>where</b> the shelf stands &mdash; and who keeps the customer who buys from it.", size=31),
  """Three quick clicks from Session 5.

The bridge: the same product at the same price earns a different amount depending on where it is sold. On a marketplace, a commission comes off every order; on your own site, the cost of bringing the visitor does. And only one of them gives you the customer's number.""")

ex1_q = ["Which door would you buy a face wash from &mdash; and why?", "After you pay, who has your name and number?",
         "Which door leaves the brand the most of your money?", "Why would a brand with 100+ shops use all three?"]
S["ex1"] = f'''<section id="ex1" data-transition="push" style="background:#fdeceb; color:#131316; {FONT}; padding:128px 128px 160px; display:flex; flex-direction:column; gap:14px">
  <p style="font-size:26px; font-weight:600; letter-spacing:4px; text-transform:uppercase; color:#ed0000">Exercise 1</p>
  <h2 style="font-size:72px; font-weight:700; letter-spacing:-1.5px">One brand, three doors</h2>
  <p style="position:absolute; left:128px; top:268px; width:1664px; height:50px; font-size:30px; line-height:1.4; color:#55555f">Saeed Ghani has sold beauty products since 1888. Today you can buy the same products in all three places.</p>
''' + "\n".join(
  f'''  <div data-build-in="fade {i + 1}" style="position:absolute; left:{128 + i * 563}px; top:336px; width:538px; height:370px">{frame(k, 538, 370, tag)}</div>'''
  for i, (k, tag) in enumerate([("sg-site", "Own website"), ("sg-daraz", "Marketplace"), ("sg-insta", "Social")])) + "\n" + "\n".join(
  f'''  <div data-build-in="fade {i + 4}" style="position:absolute; left:{128 + i * 422}px; top:728px; width:398px; height:180px; background:#ffffff; padding:22px 26px; border-radius:16px; border:1px solid #f2c9c6; display:flex; flex-direction:column; gap:6px">
    <p style="font-size:22px; font-weight:600; color:#ed0000; font-family:'JetBrains Mono', monospace">{i + 1}</p>
    <p style="font-size:26px; font-weight:600; line-height:1.3">{q}</p>
  </div>''' for i, q in enumerate(ex1_q)) + f'''
  {FOOT.format("Exercise 1 &middot; the same product, three different businesses")}
  <aside>Eight minutes. Three clicks for the pages, then one per question.

The three pages are real: Saeed Ghani's own website, its official store on Daraz, and its Instagram. Founded in 1888, it has more than a hundred outlets of its own (Dawn, 2023) and sells through general trade as well.

Ask for a show of hands on question 1, then take three reasons. Expect: Daraz for trust, delivery and returns, and because "I'm already on the app"; the website for the full range and genuine product; Instagram for seeing it used and asking a question.

Question 2 is the heart of the session. On the website and on Instagram, the brand has the buyer's name, number and address. On Daraz, the order is Daraz's customer; the brand ships to an address but cannot market to that buyer.

Question 3: the website keeps the most per order (no commission), but the brand paid to bring the visitor there. Daraz takes a commission set by category; Instagram costs time per order.

Question 4: each door reaches different people. The rest of the session is how to choose and how to stop the doors competing with each other.

Sources: Dawn (2023) on Saeed Ghani's stores; the brand's own website, Daraz store and Instagram. Page snapshots captured for class.</aside>
</section>
'''

S["part1"] = div("part1", "Part 1 &middot; Theory", "Four places<br>to sell",
  "Marketplaces, your own website, social commerce and omnichannel &mdash; each with a Pakistani and a global case, and real pages.",
  """Part 1 follows the course outline: marketplaces against your own website, then social commerce, then omnichannel, then channel strategy. Real-world practice only; the simulation is Part 2.""")

S["places"] = sec("places", "#ffffff", "The channels", "Four places a brand can sell online",
  grid([
    ("Marketplace", "Rent their shoppers", "Daraz, Amazon. Millions already searching; you pay a commission on every order.", "#ed0000"),
    ("Own website", "Own the customer", "Your site or app. You keep the margin and the data &mdash; and bring every visitor yourself.", "#2a78d6"),
    ("Social commerce", "Sell in the conversation", "Instagram, Facebook, TikTok, WhatsApp. Found in the feed, sold in a chat.", "#1baf7a"),
    ("Omnichannel", "Every door, one customer", "Stores, site and marketplaces sharing one stock, one price and one customer record.", "#8a6414"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "Most brands use more than one. The question is not <b>which</b> channel, but <b>which job each one does</b>. Where do your customers already shop?", size=30),
  """One channel per click.

Marketplace: a platform that brings buyers and many sellers together and runs payment and, often, delivery. You rent access to its shoppers.

Own website (direct-to-consumer, D2C): you sell on your own site or app. You own the relationship and the data, and you pay for every visitor through ads, search and social.

Social commerce: selling where people already spend time. In Pakistan, a large share of small brands start here: a page, a WhatsApp number, cash on delivery.

Omnichannel: the channels joined up, so the customer sees one brand. Multichannel is being in many places; omnichannel is the customer not noticing the joins.

Question for the room: which of the four did Saeed Ghani's three pages show, and which one was missing from the screen? (The shops.)""")

def two(n, L, T, W, H, label, title, items, col):
    li = "".join(f'<p style="font-size:25px; line-height:1.38; color:#33333b">&middot; {x}</p>' for x in items)
    return f'''  <div data-build-in="fade {n}" style="position:absolute; left:{L}px; top:{T}px; width:{W}px; height:{H}px; background:#ffffff; padding:26px 32px; border-radius:18px; border:1px solid #e4e4e7; display:flex; flex-direction:column; gap:8px">
    <p style="font-size:21px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:{col}">{label}</p>
    <h3 style="font-size:30px; font-weight:600; color:#131316">{title}</h3>
    {li}
  </div>'''

S["rent-own"] = sec("rent-own", "#f5f5f6", "Marketplace or own website", "Rented reach against owned customers",
  two(1, 128, 280, 819, 290, "Marketplace &middot; what you get", "Shoppers who are already buying",
      ["Traffic and trust from day one", "Payments and cash on delivery collected for you", "Delivery network and sale events"], "#ed0000")
  + "\n" + two(2, 973, 280, 819, 290, "Marketplace &middot; what it costs", "A share of every order, for ever",
      ["Commission on each sale, set by category", "Your price shown next to your rivals'", "The buyer stays the platform's customer"], "#ed0000")
  + "\n" + two(3, 128, 590, 819, 290, "Own website &middot; what you get", "The margin, the data, the brand",
      ["No commission on any order", "Every buyer's name, number and history", "Your page, your prices, your story"], "#2a78d6")
  + "\n" + two(4, 973, 590, 819, 290, "Own website &middot; what it costs", "You bring every visitor",
      ["Ads, search and social to find each buyer", "Your own gateway, COD and courier", "Trust built from zero"], "#2a78d6"),
  """Four clicks: what a marketplace gives, what it costs, then the same for your own site.

The trade is reach now against customers later. A marketplace is the fastest way to a first thousand orders: the shoppers, the trust and the payment are already there. But you pay on every order, including the fifth order from a loyal buyer, and the platform decides how your product is shown and who sees it.

Your own website costs nothing per order beyond payment fees, but every visitor has to be bought or earned. The prize is the customer record: the name and number you can message for the next order at almost no cost.

Pakistani detail: Daraz publishes commission by category to sellers in its Seller Center; check the current rate for your category before planning a price.

Question for the room: for a product people buy once a year, which side wins? For a shampoo they buy every month?""")

own = [("1st order", "Rs 550", "Rs 300", "Rs 550", "Rs 300"), ("2nd order", "Rs 80", "Rs 300", "Rs 630", "Rs 600"),
       ("3rd order", "Rs 80", "Rs 300", "Rs 710", "Rs 900"), ("4th order", "Rs 80", "Rs 300", "Rs 790", "Rs 1,200"),
       ("5th order", "Rs 80", "Rs 300", "Rs 870", "Rs 1,500")]
S["repeat"] = sec("repeat", "#ffffff", "Marketplace or own website", "The marketplace is cheaper only once",
  trows(["One customer, Rs 2,000 orders", "Own site", "Marketplace", "Own site, total", "Marketplace, total"], own, 276,
        [460, 260, 260, 310, 318], rh=72, size=28)
  + "\n" + band(6, 700, 170, "Own site: Rs 500 in ads to win the buyer, then about Rs 80 a time to bring them back. Marketplace: 15% of every order. <b>From the third order, your own site is cheaper.</b> How often does your customer buy?", size=28),
  """Illustrative numbers. One row per click, then the conclusion.

The same customer buys five times, Rs 2,000 each time. Product cost and delivery are the same in both columns, so they are left out.

Own website: about Rs 500 of advertising to win the first order (the customer acquisition cost) plus about Rs 50 of payment and COD fees, then about Rs 80 per repeat order (fees plus a message or a small offer to bring them back).

Marketplace: an illustrative 15% commission, Rs 300 on every order, first or fifth. No acquisition cost, because the marketplace brought the buyer.

The marketplace wins the first order easily. By the third, the own site is cheaper, and the gap grows with every repeat. So the channel depends on the product: for something bought once (a gift, an appliance), the marketplace is cheaper; for something bought every month (shampoo, detergent, baby care), the customer is worth owning.

The catch: the own-site numbers only hold if the buyer comes back, which needs their number and a reason to return. Session 8 is about exactly that.""",
  footer="Illustrative numbers")

S["social"] = sec("social", "#f5f5f6", "Social commerce", "Found in the feed, sold in a chat",
  grid([
    ("Discovery", "The feed does the finding", "Instagram, TikTok and Facebook show products to people who were not looking.", "#ed0000"),
    ("The sale", "A chat, not a checkout", "Price on DM, photos and voice notes on WhatsApp. A real person builds trust.", "#2a78d6"),
    ("Payment", "Cash, transfer or wallet", "Cash on delivery, a bank transfer or a mobile wallet &mdash; agreed in the chat.", "#1baf7a"),
    ("Resellers", "Other people's networks", "Individuals sell a supplier's products to their own contacts for a margin.", "#8a6414"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "Cheap to start, hard to scale: every order is a conversation. <b>What breaks first at 50 orders a day?</b>", size=30),
  """One idea per click.

Social commerce is where many Pakistani brands begin: an Instagram page, a WhatsApp Business number and a courier account. No website, no commission. Trust comes from seeing a real person, real customers' photos and quick answers.

The limits show with volume: replies slow down, orders are typed by hand, stock is tracked in a notebook, and cash-on-delivery refusals rise. Brands usually add a simple website (often on Shopify) once chats take more time than the products.

Resellers are the other form: people with no stock of their own sell a supplier's catalogue to friends, family and neighbours on WhatsApp and Facebook, adding their own margin. Platforms such as Markaz in Pakistan and Meesho in India built businesses on this (next cases).

Question for the room: name a brand you first found on Instagram. Did you buy it there, or somewhere else?""")

cmp_rows = [("Who brings the shopper", "The platform's traffic", "You: ads, search, social", "Your followers and their contacts"),
            ("What each order costs", "Commission, every time", "Ads to win the first one", "Your time, every time"),
            ("Who owns the customer", "The platform", "You", "You, one chat at a time"),
            ("Price and page", "Beside rivals, on its rules", "Entirely yours", "Yours, by hand"),
            ("When the cash arrives", "On the platform's payout cycle", "COD after the courier pays", "Often in advance"),
            ("How it scales", "Fast", "With money", "Slowly, by hand")]
S["compare"] = sec("compare", "#ffffff", "Side by side", "Three channels, six differences",
  trows(["", "Marketplace", "Own website", "Instagram &amp; WhatsApp"], cmp_rows, 276, [380, 400, 400, 428], rh=76, size=26)
  + "\n" + band(7, 790, 110, "No channel wins every row. <b>Which two rows matter most for your brand?</b>", size=30),
  """One row per click. This is the summary of the theory so far; leave it up while the room argues.

Read across each row. The marketplace wins on reach and speed; the own website wins on ownership and margin per repeat order; social wins on trust and the cost of starting.

Cash timing matters in Pakistan: marketplaces pay out on a cycle after delivery (Daraz cut its cycle from 14 to 7 days in 2021); your own COD orders wait for the courier to remit; social sellers often ask for an advance on bank transfer for custom or high-value orders.

Question for the room: if your product is bought every month, which row matters most? If it is a once-a-year gift?""")

S["case-mp"] = shot_cases("case-mp", "Cases &middot; Marketplaces", "The marketplace's shoppers, on its terms",
  ("Pakistan", "Daraz", "since 2012", "daraz",
   [("The platform", "Owned by Alibaba since 2018. By December 2022: 27 million users and 262,569 verified sellers."),
    ("The terms", "Commission by category; payouts cut from 14 to 7 days in 2021. The shopper stays Daraz's.")]),
  ("Global", "Amazon", "marketplace since 2000", "amazon",
   [("The platform", "Opened its pages to other sellers in 2000. By early 2024 they sold 61% of the units on Amazon."),
    ("The terms", "A referral fee on each sale; sellers of the same item compete for one 'Buy Box'.")]),
  "Both give sellers <b>instant shoppers</b> &mdash; and keep the customer, the comparison and the rules.",
  """Two marketplace cases, with real pages. Point at the snapshots: the search results, the ratings, the rival sellers on the same screen.

Daraz: founded in 2012 by Rocket Internet, initially for fashion; acquired Kaymu's operations in 2016 and was bought by Alibaba Group in May 2018. It runs in Pakistan, Bangladesh, Sri Lanka, Nepal and Myanmar. In a Dawn Aurora interview Daraz said that as of December 2022 its user base stood at 27 million with 262,569 verified sellers. In 2021 it cut the seller payment cycle from 14 to 7 days. Commission is set by category and shown to sellers in Seller Center; DarazMall is its section for official brand stores.

Amazon: opened its marketplace to third-party sellers in 2000. Marketplace Pulse reported that third-party sellers accounted for 61% of units sold in Q1 2024 (62% by Q4 2024). Sellers pay a referral fee per sale, set by category, and often fulfilment fees; when several sell the same product, one wins the 'Buy Box' — usually on price, delivery and rating.

The lesson for a brand: on a marketplace you compete on the platform's page, next to rivals, on price and rating. The customer remembers buying "on Daraz".

Question for the room: on the Daraz page, what tells you which seller to trust?

Sources: Dawn Aurora (Daraz interview, data to December 2022); Daraz seller announcement via ACN Newswire (2021); Marketplace Pulse (2024).""",
  "Sources: Dawn Aurora (data to Dec 2022); Daraz 2021 seller release (ACN Newswire); Marketplace Pulse (2024)")

S["case-own"] = shot_cases("case-own", "Cases &middot; Your own website", "Own the customer, pay to find them",
  ("Pakistan", "Conatural", "Lahore, 2014", "conatural",
   [("The model", "Natural skin and hair care, sold on its own site, in its own Lahore stores and by high-end retailers."),
    ("The bet", "Raised US$825,000 in 2020 to grow 'click-and-mortar': its own website and its own shops.")]),
  ("Global", "Nike", "2017&ndash;2025", "nike",
   [("The push", "Left Amazon in 2019 and cut wholesale partners to sell direct, on its own site and app."),
    ("The pull-back", "Rebuilt wholesale under a new CEO; in 2025 Amazon began buying from Nike directly again.")]),
  "Owning the customer pays &mdash; <b>but only if you can afford to keep finding new ones</b>.",
  """Two own-site cases.

Conatural: a Lahore natural and organic skin and hair care brand, founded in 2014 by Myra Qureshi Jahangir and Rema Taseer. It sells online on its own website, in its own stores at Emporium Mall and Packages Mall, and through high-end retailers, plus exports. In November 2020 it raised US$825,000 in a pre-Series A round (Karavan and angel investors) to scale what it called its click-and-mortar operations: own site plus own stores.

Nike: from 2017 it pushed direct-to-consumer — its own website and apps and its own stores — and cut many wholesale accounts. It had begun selling on Amazon in 2017 and stopped in 2019, after complaints that Amazon did too little about counterfeits and unauthorised sellers. Direct sales grew, but the cost of bringing every buyer to Nike's own channels rose; Elliott Hill became CEO in October 2024 with rebuilding wholesale a priority. In May 2025 Amazon told sellers it would source a number of Nike products directly, and Hill said the renewed partnership would launch that autumn (Modern Retail).

The lesson: owning the customer is valuable, but a brand that leaves the places where shoppers already are must pay to bring every one of them to its own site. Even Nike found the bill too high.

Question for the room: what would make you go to a brand's website instead of searching on Daraz?

Sources: Profit by Pakistan Today and Wamda (Nov 2020); Modern Retail (May and June 2025) on Nike.""",
  "Sources: Profit (Pakistan Today), Wamda (2020); Modern Retail on Nike (2025)")

S["case-social"] = shot_cases("case-social", "Cases &middot; Social commerce", "Selling through people's own networks",
  ("Pakistan", "Markaz", "Islamabad, 2021", "markaz",
   [("The model", "Resellers pick wholesale products in the app and sell them in their own WhatsApp and Facebook stores."),
    ("The scale-up", "Markaz delivers, collects the cash and pays resellers. US$2.4m seed in 2022, aimed at women in smaller cities.")]),
  ("Global", "Meesho", "India, 2015", "meesho",
   [("The start", "Homemakers and small shops reselling to friends and family on WhatsApp."),
    ("The pivot", "Became a marketplace; in 2021 cut seller commission to zero, earning from ads and logistics.")]),
  "Social selling starts with <b>trust between people</b>; to scale, someone has to run the delivery and the cash.",
  """Two social-commerce cases.

Markaz: an Islamabad startup (Y Combinator backed), founded in 2021. Anyone can pick products from wholesale suppliers in the Markaz app, add their own margin and sell through their own WhatsApp and Facebook stores with no investment; Markaz handles delivery, cash collection and customer service, and pays resellers to mobile wallets such as Easypaisa and JazzCash. In May 2022 it raised a US$2.4 million seed round led by Indus Valley Capital, with a focus on women in tier-2 cities.

Meesho: founded in 2015 by Vidit Aatrey and Sanjeev Barnwal in Bengaluru. It began by helping small sellers and homemakers resell products on WhatsApp and Facebook. It grew into a marketplace and, in mid-2021, became the first Indian e-commerce marketplace to charge sellers zero commission — earning instead from advertising and logistics.

The lesson: social selling runs on trust between people who know each other. The platforms that scaled it took over the hard parts — catalogue, delivery, cash — and left the selling to the people.

Question for the room: who in your family buys or sells through WhatsApp groups? What do they buy?

Sources: ProPakistani and Dawn (May 2022); Markaz website; Meesho press release (Aug 2021); TechCrunch.""",
  "Sources: ProPakistani (2022); Markaz; Meesho press release (2021); TechCrunch")

S["omni"] = sec("omni", "#ffffff", "Omnichannel", "Every door, one customer",
  grid([
    ("One stock", "Sell what any store holds", "No &lsquo;sold out online&rsquo; while a shop has it on the shelf.", "#ed0000"),
    ("One customer", "Same account everywhere", "Online, in store and on WhatsApp: one history, one set of points.", "#2a78d6"),
    ("Any door", "Buy here, collect or return there", "Order online, pick up or return in a shop near you.", "#1baf7a"),
    ("One price", "Or a reason when it differs", "Different prices by channel feel like a trick unless the offer is different too.", "#8a6414"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "Multichannel is being in many places. <b>Omnichannel is the customer not noticing the joins.</b> Where would your customer notice them first?", size=30),
  """One idea per click.

Omnichannel needs systems more than slogans: one inventory that every channel can see and sell from, one customer record, and order routing that decides which shop or warehouse fills each online order.

It matters most for brands that already have shops. A shop is also a warehouse close to the customer, a pickup point that saves delivery cost, and a returns desk that makes buying online less risky.

For a young online brand, the same idea applies on a smaller scale: one stock across your site, Daraz and Instagram, so that the product you promised in a chat is not the one that just sold on the marketplace.""")

S["case-omni"] = shot_cases("case-omni", "Cases &middot; Omnichannel", "The shop becomes the warehouse",
  ("Pakistan", "Khaadi", "Karachi, 1998", "khaadi",
   [("The footprint", "Stores across Pakistan, the GCC and the UK, plus its own online shops."),
    ("One stock", "Built 'Omni Plus' and 'Store Plus' so online orders are filled from any store's stock.")]),
  ("Global", "Target", "US", "target",
   [("Stores as hubs", "Stores filled most online orders by 2019; in Q3 2020 they fulfilled 95% of all sales."),
    ("The economics", "Pickup and Drive Up cut fulfilment cost by about 90% against shipping from a warehouse.")]),
  "Both use <b>the shops they already have</b> as the website's warehouse and pickup point.",
  """Two omnichannel cases.

Khaadi: the Pakistani fashion and home brand, founded in Karachi in 1998, with stores in Pakistan, the Gulf and the UK (counts vary by year; Microsoft's case study says 70+). With Microsoft Dynamics 365 and Power Apps it built tools it calls Omni Plus and Store Plus, so an online order can be filled from any store's inventory ('one inventory'). Microsoft reports shorter fulfilment times and lower logistics costs; the team built a first prototype in a weekend.

Target: the US retailer turned its stores into fulfilment hubs. In its Q1 2019 call, CEO Brian Cornell said that moving from a distribution centre to same-day services such as Order Pickup and Drive Up cut fulfilment cost by about 90%. In Q3 2020, stores fulfilled 95% of Target's sales.

The lesson: for a brand with shops, omnichannel turns fixed costs it already pays (rent, staff, stock) into cheaper, faster online fulfilment.

Question for the room: which Pakistani brand lets you return an online order in a shop? Did you use it?

Sources: Microsoft customer story and casestudies.com (Khaadi); Supply Chain Dive, Modern Retail (Target, 2019); Supermarket News (Target Q3 2020).""",
  "Sources: Microsoft customer story (Khaadi); Supply Chain Dive, Supermarket News (Target)")

S["strategy"] = sec("strategy", "#f5f5f6", "Channel strategy", "Four questions to choose the mix",
  grid([
    ("Where", "Where do your buyers already shop?", "Go where the demand is first; persuading people to a new place is the expensive part.", "#ed0000"),
    ("Margin", "Can it carry the cost?", "Commission on a marketplace, or the cost of each new buyer on your own site.", "#eb6834"),
    ("Repeat", "Do they come back?", "Bought monthly: own the customer. Bought once: rent the reach.", "#2a78d6"),
    ("Control", "Can you hold one price?", "If a channel forces deeper discounts, it will pull buyers from the others.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "A common path: <b>prove demand on social, find reach on a marketplace, keep repeat buyers on your own site</b>. Which step is your brand on?", size=30),
  """One question per click.

Where: a channel's value is the demand already in it. Daraz has shoppers searching for "face wash" today; your website has nobody until you bring them.

Margin: a marketplace commission comes off every order; an own-site acquisition cost comes off the first. Products with thin margins struggle on marketplaces; products with low repeat struggle on own sites.

Repeat: the repeat-order table. The more often customers buy, the more owning them is worth.

Control: price and presentation. The more channels you use, the harder it is to keep the same price everywhere.

The common path is a pattern, not a rule: many Pakistani brands start on Instagram, add Daraz for reach, and invest in their own site once they have repeat buyers worth keeping. Brands with shops add omnichannel.""")

S["conflict"] = sec("conflict", "#ffffff", "Channel conflict", "When your channels compete with each other",
  grid([
    ("Price", "Cheaper on Daraz than on your site", "Your own site loses every comparison, and your loyal buyers notice.", "#ed0000"),
    ("Sale events", "11.11 sets the price people wait for", "Marketplace mega-sales expect deep cuts; your full-price weeks get quieter.", "#eb6834"),
    ("Other sellers", "Someone else lists your product", "Resellers and fakes set your price and your reviews for you.", "#2a78d6"),
    ("What brands do", "Make each channel different", "One price list, channel-only packs, an official store, a reason to buy direct.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "Channels do not conflict because they exist; <b>they conflict when the same offer is cheaper in one of them</b>. What reason would a buyer have to come to your own site?", size=29),
  """One click per card.

Price parity: if the same item is cheaper on a marketplace, price-aware customers move there, and you pay commission on orders you used to get for free.

Sale events: Daraz's 11.11 and Big Friday bring huge traffic but set expectations of deep discounts. Session 5's lesson: a promotion borrows from the weeks around it.

Other sellers: anyone can list a branded product on a marketplace; an official brand store (DarazMall for brands) tells shoppers which seller is genuine.

What brands do: keep one price list; sell different packs or bundles in different channels (a marketplace-only pack is not directly comparable); give a reason to buy direct — a loyalty programme, full range, first access, gift sets. Follow each platform's rules on steering its buyers elsewhere.""")

S["ex2"] = exercise("ex2", "Exercise 2", "Plan the channels for a launch",
  "Imagine a new Pakistani skincare brand: one hero serum, a small budget and 5,000 Instagram followers.",
  ["Where does it sell first, and why there?", "When would it list on Daraz &mdash; or never?", "Which channel gets its lowest price, if any?", "How does a Daraz buyer become its own customer?"],
  "Exercise 2 &middot; a channel plan, not a channel list",
  """Ten minutes in teams. One question per click. The brand is hypothetical.

Push on question 2: the trigger to list should be a number — e.g. when the brand can't grow Instagram orders without paying more per buyer than a marketplace commission would cost.

Question 3 is the conflict slide: the honest answer is often "none" — the same price everywhere, with channel-specific packs.

Question 4 has no easy answer on a marketplace: the buyer is the platform's customer. Good answers stay within platform rules: a strong brand name people search for directly, an Instagram presence, a product worth looking up.

Take two teams' answers.""", top=500, h=180, cols=2)

S["part2"] = div("part2", "Part 2 &middot; The simulation", "The marketplace<br>opens",
  "Decision 4.1 opens for month 5: list on the marketplace, or stay on your own site.",
  """Part 2 is the simulation. Month 4 has run. One decision opens this round: 4.1, sell on the marketplace.

Every number in Part 2 is the simulation's assumption or a test run of it, not market data.""")

S["category"] = sec("category", "#f5f5f6", "The category online", "How personal care sells online in Pakistan",
  grid([
    ("Marketplace", "Beauty is a top Daraz category", "Makeup and skincare were among the top categories of Daraz's 11.11 in 2023; brand stores led its 2025 sale.", "#ed0000"),
    ("Brand websites", "Heritage brands sell direct too", "Saeed Ghani (1888) sells through 100+ own outlets, its own site and Daraz.", "#2a78d6"),
    ("Social", "New brands start on Instagram", "Young skincare brands launch with a page, a WhatsApp number and a courier.", "#1baf7a"),
    ("Payment", "Cash on delivery still leads", "About 63% of SME online sales were cash on delivery in a 2021 survey.", "#8a6414"),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "The simulation's teams sell personal care and home care online in Pakistan. <b>Which of these four is your team's business today?</b>", size=30),
  """The real category first, as every Part 2 does. One card per click.

Marketplace: ProPakistani reported makeup and skincare among the top categories of Daraz's 11.11 sale in 2023, and that DarazMall (official brand) stores led the 2025 11.11 sale.

Brand websites: Saeed Ghani, founded in 1888, has more than a hundred outlets of its own (Dawn) and sells on its own website and on Daraz — the opening exercise.

Social: many young beauty brands start on Instagram and WhatsApp before they have a website; the cases earlier (Markaz, Meesho) show the reseller version.

Payment: bSecure's 2021 survey of Pakistani SMEs found about 63% of their online sales were cash on delivery.

Sources: ProPakistani (2023, Dec 2025); Dawn (2023); Profit (2020); bSecure SME survey (2021).""",
  footer="Sources: ProPakistani (2023, 2025); Dawn (2023); bSecure SME survey (2021)")

S["sim-market"] = sec("sim-market", "#ffffff", "In the simulation", "How the marketplace works in the simulation",
  grid([
    ("Shoppers", "A pool shared by rank", "Each month the marketplace's own shoppers are shared between listed sellers: half on price, half on rating. The rest of the marketplace counts as four typical sellers.", "#ed0000"),
    ("Money", "14.5% on marketplace orders", "The marketplace collects the payment (no gateway or COD fee of yours) and pays you 15 days later.", "#eb6834"),
    ("Your own buyers", "One in ten moves over", "A tenth of your own-site orders are placed on the marketplace instead, and pay commission there.", "#2a78d6"),
    ("Whose customer", "The marketplace's", "Its buyers churn 10.3% a month (3.7% for organic buyers). Your CRM cannot reach them; they come back only while you are listed.", "#1baf7a"),
  ], 4, 290, 430, bsize=24)
  + "\n" + band(5, 760, 120, "<b>4.1 opens for month 5.</b> Marketplace orders sell from the same stock as your own site.", size=30),
  """One rule per click. The rules are the simulation's.

Shoppers: a fixed pool of marketplace shoppers is shared between the listed teams by a rank score — half price (cheaper ranks higher), half last month's rating. The rest of the marketplace is counted as four typical sellers, so a team listing alone gets a slice, and a smaller one the more teams list. Marketplace shoppers convert half as well again as the team's own-site visitors: they arrive ready to buy.

Money: commission 14.5% on marketplace orders only. The marketplace collects payment, so the team pays no gateway or COD fee on those orders, and the cash arrives 15 days after the sale.

Your own buyers: 10% of own-site orders move to the marketplace (cannibalisation) — no extra orders, but commission on them.

Whose customer: buyers won on the marketplace churn at 10.3% a month, against 3.7% for organic buyers and 6.3% for Meta-acquired ones, buy less often, are not reached by the team's CRM, and reorder through the marketplace only while the team stays listed.

Real founders estimate such numbers from the marketplace's seller data and their own tests; these are the simulation's assumptions.""",
  footer="Decision rules from the simulation &middot; not market data")

tests6 = [("Not listed", "3,495", "&mdash;", "615k"),
          ("Listed, the only team listed", "4,484 &nbsp;&middot; 30% via it", "462k", "883k &nbsp;(+268k)"),
          ("Listed, three teams listed", "4,201 &nbsp;&middot; 25%", "364k", "784k &nbsp;(+169k)"),
          ("Listed, all six teams listed", "3,989 &nbsp;&middot; 21%", "290k", "708k &nbsp;(+93k)"),
          ("Listed, and 10% off everything", "4,839 &nbsp;&middot; 33%", "493k", "&minus;57k"),
          ("Listed months 5&ndash;6, off in month 7", "Month 7: 3,854 &nbsp;(3,855 never listed)", "&mdash;", "681k &nbsp;(810k)")]
S["sim-tests"] = sec("sim-tests", "#f5f5f6", "In the simulation", "What listing did in a test month",
  trows(["Test, month 5, all else default", "Orders", "Commission", "Contribution"], tests6, 276, [560, 560, 220, 268], rh=72, size=26)
  + "\n" + band(7, 786, 100, "<b>Which line describes your month 5 &mdash; and what would you do in month 7?</b>", size=30),
  """One test per click. Each line is one team changing one decision against an identical team on every default, in the same simulated month (six teams, month 5, after four default months).

Read down: listing alone added about 1,000 orders (30% of the month came through the marketplace) and 268k of contribution after 462k of commission. The more teams list, the smaller each slice: with all six listed, the gain falls to 93k, because the marketplace's shoppers are shared.

Listing with 10% off everything ranked higher and sold the most, but gave away the margin on every order, own-site ones included: contribution fell below zero. (The same 10% off without listing lost 153k: the discount is the problem, not the listing.)

The last line is the customer lesson: a team that listed for two months and then left had, in month 7, the same orders as a team that never listed. The marketplace's buyers stayed with the marketplace. Its contribution was lower that month too: returns from the last marketplace month arrived, and its stock had run down (2,529 units against 4,423), because listing sells from the same stock.

Results depend on each team's prices, rating and stock; these are directions, not forecasts.""",
  footer="Simulation test run, six teams, month 5, all else default &middot; not market data")

S["checks"] = sec("checks", "#fdeceb", "Before month 5 runs", "Four questions before you list",
  grid([
    ("Margin", "Can your margin carry 14.5%?", "On top of delivery, returns and discounts &mdash; check your month-4 gross margin.", "#ed0000"),
    ("Rank", "Will shoppers find you there?", "Price and rating decide your slice. Discounting to rank gives the margin away.", "#eb6834"),
    ("Stock", "Have you bought for it?", "Marketplace orders come from the same stock. Check your weeks of cover in 7.1.", "#2a78d6"),
    ("Customers", "Whose customers are you building?", "Marketplace buyers stay the marketplace's. What brings buyers to your own site?", "#1baf7a"),
  ], 4, 300, 340)
  + "\n" + band(5, 700, 150, "Name in the board memo the number in month 5's report that will tell you <b>whether listing paid</b>.", size=30),
  """One question per click, while teams fill in the decision form.

Logistics for the notes, not the slide: decisions for month 5 close at [deadline]. Open this round: 4.1 sell on the marketplace, plus everything opened earlier. The month-5 report shows marketplace orders, their share, commission and the payout still to come.""")

S["next"] = sec("next", "#131316", "Next session", "How will you get customers?",
  grid([
    ("Session 7", "The ad budget becomes yours", "Meta, Google, TikTok, influencers and brand-building.", "#ff3b3b"),
    ("Your customers", "What does each one cost?", "Every channel has its own cost per buyer and its own churn.", "#ff3b3b"),
    ("Your numbers", "Did listing pay?", "Month 5's marketplace orders and commission are the test.", "#ff3b3b"),
  ], 3, 300, 300, bg="#1f1f24", border="border:1px solid #33333b;", tcol="#ffffff", bcol="#c9c9d1")
  + "\n" + band(4, 660, 150, "Today: where to sell, and who keeps the customer. Next time: <b>how to bring customers to you, and what each one costs</b>.", bg="#ed0000", size=31),
  """Close. One card per click.

Session 7 opens the marketing budget (3.1–3.10): the channels the teams have been paying by default for five months. Sessions 6 and 7 are a pair: choose a channel, then pay to bring people to it.""", dark=True, eyecol="#ff3b3b")

ORDER = ["cover", "recall", "ex1", "part1", "places", "rent-own", "repeat", "case-mp", "case-own", "social",
         "case-social", "compare", "omni", "case-omni", "strategy", "conflict", "ex2", "part2", "category",
         "sim-market", "sim-tests", "checks", "next"]
assert set(ORDER) == set(S), set(S) ^ set(ORDER)
logo = sys.argv[2] if len(sys.argv) > 2 else "__LOGO__"
root = pathlib.Path(sys.argv[1]) / "project"
(root / "slides").mkdir(parents=True, exist_ok=True)
for k, v in S.items():
    (root / "slides" / f"{k}.html").write_text(v.replace("__LOGO__", logo.rsplit("/", 1)[-1]))
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-10-13T09:30:00Z"}, "lists": "css",
        "title": "Session 6 — Where Will You Sell?", "order": ORDER,
        "sections": {
          "open": {"description": "Where will you sell, and one brand's three doors", "start": "cover"},
          "channels": {"description": "Part 1 · Marketplace against own website, with cases", "start": "part1"},
          "social": {"description": "Social commerce, with cases", "start": "social"},
          "omni": {"description": "Omnichannel, channel strategy and conflict", "start": "omni"},
          "sim": {"description": "Part 2 · The marketplace in the simulation", "start": "part2"}},
        "faces": {"inter": {"family": "Inter", "href": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono"}},
        "designSystems": []}
if not (root / "deck.json").exists():
    (root / "deck.json").write_text(json.dumps(deck, indent=2, ensure_ascii=False))
print("wrote", len(S))
