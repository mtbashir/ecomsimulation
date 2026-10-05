"""Session 4 - Building Your Online Store. About 20 slides."""
import pathlib, sys, json
HERE = pathlib.Path(__file__).parent
_g3 = (HERE / "s3_slides.py").read_text().split("\nS = {}\n")[0]
exec(_g3)
FT = "Session 4 &middot; Building Your Online Store"
LOGO = LOGO.replace("08915064a97a15b612763fb2958cfbac", "__LOGO__")
def sec(sid, bg, eyebrow, title, body, notes, footer=FT, **kw):
    return section(sid, bg, "#131316", eyebrow, title, body, notes, footer=footer, **kw)
def div(sid, part, title, line, notes):
    return divider(sid, part, title, line, notes).replace("Session 2 &middot; Finding the Right Idea", FT).replace("856d57cb939a323d46943b3b229572d7", "__LOGO__")

def qcards(qs, top=480, h=200, cols=None):
    cols = cols or len(qs)
    w = (1664 - 22 * (cols - 1)) // cols
    return "\n".join(f'''  <div data-build-in="fade {i+1}" style="position:absolute; left:{128 + (i%cols)*(w+22)}px; top:{top + (i//cols)*(h+20)}px; width:{w}px; height:{h}px; background:#ffffff; padding:34px 38px; border-radius:16px; border:1px solid #f2c9c6; display:flex; flex-direction:column; gap:10px">
    <p style="font-size:26px; font-weight:600; color:#ed0000; font-family:'JetBrains Mono', monospace">{i+1}</p>
    <p style="font-size:31px; font-weight:600; line-height:1.3">{q}</p>
  </div>''' for i, q in enumerate(qs))

def exercise(sid, label, title, intro, qs, footer, notes, top=480, h=200, cols=None):
    return f'''<section id="{sid}" data-transition="push" style="background:#fdeceb; color:#131316; {FONT}; padding:128px 128px 160px; display:flex; flex-direction:column; gap:40px">
  <p style="font-size:26px; font-weight:600; letter-spacing:4px; text-transform:uppercase; color:#ed0000">{label}</p>
  <h2 style="font-size:88px; font-weight:700; letter-spacing:-2px; line-height:1.05">{title}</h2>
  <p style="font-size:34px; line-height:1.45; color:#55555f; width:1500px">{intro}</p>
{qcards(qs, top, h, cols)}
  {FOOT.format(footer)}
  <aside>{notes}</aside>
</section>
'''

S = {}
S["cover"] = f'''<section id="cover" data-transition="fade" style="background:#131316; color:#ffffff; {FONT}; padding:128px 128px 160px; display:flex; flex-direction:column; justify-content:space-between">
  {LOGO}
  <div style="display:flex; flex-direction:column; gap:28px">
    <p style="font-size:28px; font-weight:600; letter-spacing:4px; text-transform:uppercase; color:#ff3b3b">Session 4 of 12</p>
    <h1 style="font-size:132px; font-weight:700; line-height:1.02; letter-spacing:-3px">Building Your<br>Online Store</h1>
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
  <p data-build-in="fade 1" style="position:absolute; left:128px; top:647px; width:1300px; height:110px; font-size:38px; line-height:1.45; color:#c9c9d1">Website, marketplace or social media &mdash; and what makes a stranger trust you enough to press &ldquo;order&rdquo;.</p>
  <aside>Two hours, 20 slides: 3 min recap, 7 min opening exercise, Part 1 theory about 55 min (channels and case 12, product pages, photos and trust 18, checkout and experience 12, cases 5, the audit 8), store audit exercise 15 min, Part 2 simulation about 30 min, 3 min close.

Month 2 has run with the new prices. Start by asking one team whether their re-pricing worked; then move on, the full debrief is in Part 2.

The idea for the day: last week was what each order leaves behind. This week is how many visitors become orders at all.</aside>
</section>
'''

S["recall"] = sec("recall", "#f5f5f6", "Where we got to last week", "Every order leaves something behind &mdash; or not",
  grid([
    ("Margins", "PKR 1,000 leaves little", "After product, delivery, marketing and fixed costs, a few percent is profit.", "#ed0000"),
    ("Pricing", "Discounts need volume", "10% off at a 40% margin needs a third more sales just to stand still.", "#eb6834"),
    ("Customers", "The first order rarely pays", "Customers who come back pay for the ones you bought.", "#2a78d6"),
  ], 3, 300, 300)
  + "\n" + band(4, 660, 170, "You pay for every visitor. Today: <b>how many of them become orders</b>, and what the store does to that number.", size=31),
  """Three quick clicks from last session; do not re-teach.

The band is the bridge: revenue was visitors × conversion × average order. Session 3 was about the order. Today is conversion, the number the store controls.""")

S["ex1"] = exercise("ex1", "Exercise 1", "The cart you left",
  "Think of the last time you put something in an online cart, or opened a product page, and <b>did not buy</b>.",
  ["Where were you: a website, a marketplace or Instagram?", "What was the exact moment you stopped?", "What one change would have made you buy?"],
  "Exercise 1 &middot; every lost order has a reason",
  """Seven minutes. One question per click. Three minutes to write, then take five answers.

Sort the answers into four piles as they come: cost (delivery charge appeared late, price), trust (fake? will it arrive? what if it is wrong?), effort (account creation, long forms, no COD, slow site) and doubt about the product (photos, size, ingredients).

Most rooms produce trust and surprise costs first. Keep the piles: the theory slides that follow cover each one.""", top=500, h=210)

S["part1"] = div("part1", "Part 1 &middot; Theory", "What makes a stranger<br>press &ldquo;order&rdquo;",
  "Where to sell, product pages, trust, checkout and the experience after it &mdash; with Pakistani and global cases.",
  """Part 1 is real-world practice, no simulation. Five blocks: choosing the channel, the product page (photos and words), trust, checkout, and the experience after the order. Then a ten-minute store audit any of them can use on a real business.""")

shop = [("Touches, smells and tries it", "Sees a photo and reads a label", "Show it the way a hand would check it"),
        ("Knows the shopkeeper", "Buys from a stranger", "Earn trust before asking for money"),
        ("Pays after seeing it", "Pays first, or cash at the door", "Offer the way they want to pay"),
        ("Takes it home now", "Waits two to five days", "Promise a date, and keep it"),
        ("Asks the shopkeeper what to buy", "Reads descriptions and reviews", "Answer the questions before they ask"),
        ("Compares two or three shops", "Compares fifty in a minute", "Give a reason to choose you, not only a price")]
S["shopper"] = sec("shopper", "#ffffff", "Shopper behaviour", "What shoppers give up online",
  trows(["In a shop, the shopper&hellip;", "Online, they&hellip;", "So the store must&hellip;"], shop, 282, [560, 500, 548], rh=80, size=27)
  + "\n" + band(7, 830, 80, "<b>Which of these would stop you buying online?</b>", size=29, extra="padding:20px 40px;"),
  """One row per click. This is the frame for the whole of Part 1: every part of an online store exists to replace something the physical shop gives for free.

Touch: photos, size in the hand, ingredients. Shopkeeper trust: reviews, a real phone number, authenticity proof. Paying after seeing: cash on delivery. Taking it home now: a delivery promise. Advice: descriptions and reviews. Comparison: online makes comparing easy, so a store needs a reason to be chosen beyond price.

Link back to Exercise 1: the answers fall into the same piles — trust, cost, effort and doubt about the product.

Ask the room the band question and take three answers. Then the next slide shows how far Pakistan is from buying online at all.""")

def pill(s, size=24, bg="#f5f5f6", col="#131316", pad="6px 14px"):
    return f'<p style="font-size:{size}px; line-height:1.3; color:{col}; background:{bg}; padding:{pad}; border-radius:8px; white-space:nowrap">{s}</p>'
groups = [("The product", "#2a78d6", ["Brand", "Product name", "Product type", "Shade / colour code", "Shade swatches", "Skin tone suitability",
            "Skin type suitability", "Ingredients", "Benefits / claims", "SPF level", "Finish", "Coverage", "Texture description",
            "Fragrance", "Size / quantity", "How to use"]),
          ("Proof", "#1baf7a", ["Before / after results", "Customer ratings", "Number of reviews", "Customer reviews", "User photos / videos",
            "Influencer reviews", "Expert claims", "Certifications", "Country of origin", "Authenticity", "Expiry / shelf life"]),
          ("Cost and risk", "#ed0000", ["Price", "Discount", "Delivery charges", "Delivery time", "Return / exchange policy", "Seller rating",
            "Seller credibility", "Availability", "Bundle offers", "Competitor comparison"])]
online = "".join(f'''<div style="display:flex; flex-direction:column; gap:8px"><p style="font-size:22px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:{c}">{g}</p><div style="display:flex; flex-wrap:wrap; gap:8px">{"".join(pill(x) for x in items)}</div></div>''' for g, c, items in groups)
offline = "".join(pill(x, 28, "#2b2b31", "#ffffff", "8px 18px") for x in ["Brand", "Shade", "Texture", "Fragrance", "Packaging", "Price", "Promotion"])
S["attributes"] = sec("attributes", "#ffffff", "Shopper behaviour &middot; beauty", "Online shoppers check five times as much",
  f'''  <div data-build-in="fade 1" style="position:absolute; left:128px; top:276px; width:1160px; height:640px; background:#ffffff; padding:28px 32px; border-radius:18px; border:1px solid #e4e4e7; display:flex; flex-direction:column; gap:14px">
    <div style="display:flex; align-items:baseline; gap:20px"><p style="font-size:56px; font-weight:700; color:#ed0000; letter-spacing:-1px">37</p><p style="font-size:28px; font-weight:600; color:#131316">attributes online &middot; &ldquo;I need information to reduce uncertainty&rdquo;</p></div>
    {online}
  </div>
  <div data-build-in="fade 2" style="position:absolute; left:1312px; top:276px; width:480px; height:640px; background:#131316; padding:28px 32px; border-radius:18px; display:flex; flex-direction:column; gap:18px">
    <div style="display:flex; align-items:baseline; gap:20px"><p style="font-size:56px; font-weight:700; color:#ff3b3b; letter-spacing:-1px">7</p><p style="font-size:28px; font-weight:600; color:#ffffff">in a shop</p></div>
    <p style="font-size:26px; line-height:1.35; color:#c9c9d1">&ldquo;I can see, touch and experience it&rdquo;</p>
    <div style="display:flex; flex-wrap:wrap; gap:10px">{offline}</div>
  </div>
  <p data-build-in="fade 3" style="position:absolute; left:1344px; top:740px; width:416px; height:150px; font-size:28px; line-height:1.4; font-weight:600; color:#ffffff">The product page has to do the job of the shop counter, the tester and the shopkeeper.</p>''',
  """Lipstick, foundation or a face serum. Click 1: the online shopper. Click 2: the same shopper in a shop. Click 3: the conclusion.

In a shop the shopper swatches the shade on her hand, smells it, feels the texture, looks at the pack and the price tag. About seven things decide it, because the product answers the rest by itself.

Online she cannot touch anything, so every one of those senses has to be replaced by information: shade swatches on different skin tones, finish and coverage in words, ingredients and SPF, before-and-after photos, reviews with user photos, and then everything about the seller — is it authentic, when will it come, what if the shade is wrong. Thirty-seven attributes in three groups: the product, proof, and cost and risk.

This is an illustrative list for beauty products, not survey data; the exact count matters less than the gap. Ask the room: which of the 37 does your favourite beauty site leave out? Most will say shade on skin like theirs, and authenticity.

Link forward: the product-page, photos and trust slides are the practical answer to this one.""",
  footer="Lipstick, foundation, face serum &middot; illustrative attribute list, not survey data")

S["shopper-data"] = sec("shopper-data", "#f5f5f6", "Shopper behaviour", "How Pakistan shops: mostly offline, still",
  row4([
    ("Did not buy online", "91%", "of adults made no online purchase in the first half of 2025."),
    ("Prefer online", "3%", "for buying clothes, against 90% for local markets. In cities, 5%."),
    ("Paid cash on delivery", "60%", "of online buyers. Easypaisa 15%, cards only 7%."),
    ("Top category bought", "30%", "of online purchases were clothing, followed by watches."),
  ], 290, 360)
  + "\n" + band(5, 700, 180, "Nine in ten Pakistanis are not yet buying online. <b>Is your customer one of the ten percent who already do &mdash; or are you trying to convert the other ninety?</b>", size=30),
  """One number per click. Two nationwide Gallup &amp; Gilani Pakistan surveys, as reported in the press:

1. Online purchases: 91% of respondents said they made no online purchase in the previous six months (first half of 2025). Among those who did, 60% paid cash on delivery, 15% used Easypaisa and 7% a credit or debit card; clothing was the top category at 30%, followed by watches; 52% bought through websites, 16% through local online stores, 5% Amazon, 3% AliExpress. Reported by ProPakistani, December 2025.

2. Where people prefer to shop for clothes: 90% local stores or markets, 3% malls, 3% online. Rural 93% local markets; urban 83% local, 6% malls, 5% online. Fieldwork 7–22 March 2025, 779 adults across all four provinces, telephone interviews, margin of error about ±2–3%. Reported by Business Recorder.

Caveats to say out loud: these are national samples including rural and older adults; urban, young, smartphone-using shoppers — most of the room — buy online far more. The point is the size of the market not yet reached, and why trust and COD dominate.

Question for the room: who is your customer — someone already buying online, or someone you must persuade to try?""",
  footer="Source: Gallup &amp; Gilani Pakistan surveys, 2025, as reported by ProPakistani and Business Recorder")

chan = [("Own website", "You do", "Low per order, but you pay for every visitor", "You must earn it", "Full: brand, data, price"),
        ("Marketplace", "The marketplace", "Commission on every sale", "Borrowed from the platform", "Little: its rules, its rivals"),
        ("Social media", "Shared with the platform", "Low to start; time and ads", "Personal, through the chat", "Some: but checkout is a DM")]
S["channels"] = sec("channels", "#ffffff", "Choosing the channel", "Website, marketplace or social media?",
  trows(["Where you sell", "Who owns the customer", "What it costs", "Trust at the start", "Control"], chan, 282, [280, 300, 370, 380, 278], rh=118, size=27)
  + "\n" + band(4, 780, 120, "Most Pakistani brands start where the customers already are, then build a home. <b>Where do your customers already shop?</b>", size=29),
  """One channel per click.

Own website (Shopify, WooCommerce or custom): you own the customer data, the brand and the price, and you can remarket. But nobody comes unless you pay for traffic, and a new site starts with zero trust.

Marketplace (Daraz and others): traffic and trust come built in, and so does the commission. The customer belongs to the platform; you compete next to rivals on the same page.

Social commerce (Instagram, Facebook, WhatsApp, TikTok): cheap to start, personal, and trust comes through the conversation. Hard to scale: checkout is a chat, and every order needs a person.

The usual path is not one or the other: start where buyers already are, then build a home you own.

Question for the room: which one would you start with for your Exercise 1 product?""")

S["case-channel"] = cases("case-channel", "Cases &middot; Choosing the channel",
  "Start where buyers are, then build a home",
  ("Pakistan", "Bagallery", "Lahore, 2017",
   [("The start", "Began as a fashion and beauty store on Facebook, where the buyers already were."),
    ("What they did", "Built its own website with cash on delivery as the business grew."),
    ("The lesson", "Social media found the first customers; a website made the business its own.")]),
  ("Global", "Nike", "on Amazon",
   [("2019", "Stopped selling to Amazon to control its brand and push its own app and stores."),
    ("2025", "Came back to Amazon in the US as sales fell and it rebuilt its wholesale partners."),
    ("The lesson", "Even the strongest brand needs channels it does not own. The mix keeps moving.")]),
  "The channel is not a one-time choice. <b>Own the customer where you can, rent reach where you must.</b>",
  """Two channel cases.

Bagallery: Pakistani fashion and beauty retailer that began on Facebook in 2017 and moved onto its own website and app. It is one of many Pakistani brands that followed the social-first path. (Check the current detail of its channels before quoting it; online sources are trade blogs.)

Nike: in November 2019 it ended its pilot of selling wholesale to Amazon, wanting more control over counterfeits and its brand, and pushed its own app and stores. In May 2025, with sales down and a new CEO rebuilding wholesale relationships, it started selling directly on Amazon's US site again.

Question for the room: what would make you leave Daraz, and what would bring you back?

Sources: CNBC (Nov 2019); OPB/AP (May 2025); Pakistani Shopify store case studies.""",
  "Sources: CNBC (2019), OPB/AP (2025); Shopify store case studies")

S["pdp"] = sec("pdp", "#f5f5f6", "Product pages", "Six questions a product page must answer",
  grid([
    ("Photos", "Is it what I think it is?", "Size, colour and texture, before they ask.", "#ed0000"),
    ("Description", "Is it for me?", "Who it suits, what it does, how to use it.", "#eb6834"),
    ("Price", "What will it cost me?", "The full price, delivery included, on the page.", "#8a6414"),
    ("Delivery", "When will it arrive?", "A date or a range for their city, not &ldquo;soon&rdquo;.", "#1baf7a"),
    ("Reviews", "Did it work for others?", "Real buyers, with photos, including the 3-star ones.", "#2a78d6"),
    ("Returns", "What if it is wrong?", "One sentence on what happens next.", "#55555f"),
  ], 3, 290, 236)
  + "\n" + band(7, 802, 100, "<b>Which of the six is missing from the page you last left?</b>", size=30),
  """One question per click. A product page is a salesperson who must answer every question without being asked, because the customer will not ask — they will leave.

Tie each to the Exercise 1 piles: photos and description answer doubt about the product; price and delivery answer surprise costs; reviews and returns answer trust.

In personal care specifically: ingredients, skin type, size in ml, and expiry date are part of "Is it for me?".""")

S["photos"] = sec("photos", "#ffffff", "Product pages", "Photos sell, words reassure",
  card(1, 128, 290, 819, 470, "Six photos for every product", "Show it the way a buyer would check it",
       "1 &middot; Front, on a plain background<br>2 &middot; In a hand, so the size is obvious<br>3 &middot; The label and ingredients, readable<br>4 &middot; The texture or the product in use<br>5 &middot; Everything that comes in the box<br>6 &middot; A real customer's photo", col="#ed0000", bsize=27)
  + "\n" + card(2, 973, 290, 819, 470, "A description in five lines", "Benefit first, specification last",
       "1 &middot; What it does for you, in one line<br>2 &middot; Who it is for, and who it is not for<br>3 &middot; How to use it<br>4 &middot; Size, ingredients, origin, expiry<br>5 &middot; Delivery time and what happens if it is wrong", col="#2a78d6", bsize=27)
  + "\n" + band(3, 790, 110, "Online the customer cannot touch, smell or try. <b>What would they check in a shop that your page does not show?</b>", size=29),
  """Two checklists, one per click. Practical rules, not research findings.

Photos: a phone and daylight are enough. The hand-for-scale photo prevents the most common complaint in personal care: "it was smaller than I thought". The label photo answers authenticity and ingredients at once.

Description: lead with the benefit, not the specification. Say who it is not for — it reduces returns and builds trust.

Urdu or Roman Urdu where the audience reads it. Many Pakistani buyers do.""")

S["trust"] = sec("trust", "#f5f5f6", "Trust", "Why should a stranger trust you?",
  grid([
    ("Payment", "Pay when it arrives", "Cash on delivery, or open the parcel before paying.", "#ed0000"),
    ("Proof", "It is the real thing", "Brand authorisation, batch numbers, a video of packing.", "#eb6834"),
    ("People", "Someone answers", "A WhatsApp number and a name, replying within the hour.", "#1baf7a"),
    ("Others", "People like me bought it", "Reviews with photos, from cities they recognise.", "#2a78d6"),
    ("Promise", "It arrives when you said", "A delivery window you keep, and updates when you do not.", "#8a6414"),
    ("Policy", "Mistakes get fixed", "A short, plain returns policy, easy to find.", "#55555f"),
  ], 3, 290, 236)
  + "\n" + band(7, 802, 100, "<b>Which of these could you add to your store this week for free?</b>", size=30),
  """One signal per click. In Pakistan trust is the first conversion problem, before price.

Payment: COD exists because people do not trust paying first. Some sellers go further and let the buyer open the parcel before paying.

Proof: "original hai?" is the most common question in beauty. Answer it on the page.

People: a real person on WhatsApp converts more doubtful buyers than any banner.

Others: reviews from Karachi or Multan count more than five stars from nobody.

Promise and policy: what happens when it goes wrong is what people remember.

Most of these cost nothing but effort.""")

reasons = [("Extra costs too high (delivery, fees)", 48), ("Asked to create an account", 26), ("Delivery too slow", 22),
           ("Did not trust the site with card details", 19), ("Checkout too long or complicated", 18), ("Could not see the total cost up front", 14)]
S["checkout"] = sec("checkout", "#ffffff", "Checkout", "Where buyers give up at checkout",
  P(128, 282, 1664, 50, txt("About <b>7 in 10</b> online carts are abandoned. Reasons given by US shoppers who left at checkout:", 28, "#55555f"))
  + "\n" + "\n".join(f'''  <div data-build-in="fade {i+1}" style="position:absolute; left:128px; top:{350 + i*70}px; width:1664px; height:60px">
    <p style="position:absolute; left:0px; top:12px; width:620px; font-size:27px; color:#131316">{lab}</p>
    <div style="position:absolute; left:640px; top:8px; width:{v*18}px; height:44px; background:{'#ed0000' if i == 0 else '#131316'}; border-radius:6px"></div>
    <p style="position:absolute; left:{656 + v*18}px; top:10px; width:100px; font-size:28px; font-weight:600; font-family:'JetBrains Mono', monospace; color:#131316">{v}%</p>
  </div>''' for i, (lab, v) in enumerate(reasons))
  + "\n" + band(7, 790, 110, "Most are fixed in the store, not with marketing. <b>Which does cash on delivery solve, and which does it create?</b>", size=29),
  """One reason per click. Data: Baymard Institute's checkout research — a 70% average cart abandonment rate across 49 studies, and the reasons US shoppers gave for their most recent abandonment (shoppers could pick several). These are US figures; Pakistan has no comparable published study, so treat the ranking as a guide, not a measurement.

The biggest one by far: costs that appear late. Show delivery charges on the product page.

Forced account creation: let people check out as guests and save the account for after.

Card trust largely disappears with COD — but COD creates its own problem: refused parcels at the door.

Question for the room: which would you fix first on your own store?""",
  footer="Source: Baymard Institute, cart abandonment research (US shoppers, 2025)")

steps = [("1", "Confirmed", "A WhatsApp message with the order and a real name"), ("2", "Dispatched", "A tracking link and a delivery day"),
         ("3", "Delivered", "On the promised day, by a courier who calls"), ("4", "Opened", "Packaging that protects, and feels like a brand"),
         ("5", "Followed up", "A check a week later, and a reason to come back")]
sw = (1664 - 4 * 22) // 5
S["cx"] = sec("cx", "#f5f5f6", "Customer experience", "The store does not end at &ldquo;Order placed&rdquo;",
  "\n".join(f'''  <div data-build-in="fade {i+1}" style="position:absolute; left:{128 + i*(sw+22)}px; top:300px; width:{sw}px; height:330px; background:#ffffff; padding:30px; border-radius:18px; border:1px solid #e4e4e7; display:flex; flex-direction:column; gap:10px">
    <p style="font-size:44px; font-weight:700; color:#ed0000; font-family:'JetBrains Mono', monospace">{n}</p>
    <h3 style="font-size:31px; font-weight:600; color:#131316">{t}</h3>
    <p style="font-size:25px; line-height:1.4; color:#55555f">{d}</p>
  </div>''' for i, (n, t, d) in enumerate(steps))
  + "\n" + band(6, 690, 150, "Every step either lowers the chance the parcel is refused at the door, or raises the chance of a second order. <b>Which step does your favourite store get right?</b>", size=29),
  """One step per click.

In a cash-on-delivery market, the time between "order placed" and the door is where revenue is won or lost. A confirmation message cuts fake and impulsive orders; tracking and a call from the courier cut refusals; packaging and a follow-up make the second order more likely.

This is where Session 8 (getting customers to come back) and Session 9 (delivery) pick up.""")

S["case-trust"] = cases("case-trust", "Cases &middot; Trust and experience",
  "Remove the reason not to buy",
  ("Pakistan", "PriceOye", "Islamabad, 2015",
   [("The fear", "Buying an expensive phone online from a stranger: is it original, will it work?"),
    ("What they did", "Brand warranty, COD and instalments, plus open-the-parcel delivery for a small fee in big cities."),
    ("The lesson", "Each policy answers one specific fear the buyer would otherwise act on.")]),
  ("Global", "Zappos", "US shoes",
   [("The fear", "Shoes bought online might not fit, and sending them back is a hassle."),
    ("What they did", "Free delivery both ways, a 365-day returns window, and service famous for going further."),
    ("The result", "Amazon bought it in 2009 for about US$1.2bn and kept it running separately.")]),
  "Both made the risk of buying <b>theirs, not the customer's</b>.",
  """Two trust cases.

PriceOye (founded 2015 in Islamabad): phones and electronics online, where fakes and grey imports are the main fear. It sells with official brand warranty, offers COD, card and bank instalments, and in Karachi, Lahore, Islamabad and Rawalpindi lets buyers open and inspect the parcel before paying for a small fee (about PKR 300 according to its site at the time of writing). Customers mention confirmation calls and packing videos.

Zappos: selling shoes online in the US when nobody believed people would buy shoes without trying them. Free shipping both ways, a 365-day returns policy, and a culture built on customer service. Amazon bought it in 2009 in a deal worth about $1.2 billion.

The pattern: take the risk off the buyer. It costs money — but it costs less than the orders you would never get.

Question for the room: what is the biggest fear your buyer has, and which policy would answer it?

Sources: PriceOye website and Tracxn; Wikipedia, Fast Company on Zappos.""",
  "Sources: priceoye.pk, Tracxn; Fast Company, Wikipedia")

aud = [("Speed", "Does the page load in three seconds on a phone?"), ("Product page", "Are all six questions answered?"),
       ("Trust", "COD, reviews, a phone number, a returns line?"), ("Cost", "Is the full price, with delivery, visible before checkout?"),
       ("Checkout", "Guest checkout, few fields, the payments people use?"), ("After the order", "Confirmation, tracking, a follow-up?")]
S["audit"] = sec("audit", "#ffffff", "Store audit", "Audit any store in ten minutes",
  trows(["Area", "The question", "Score 0, 1 or 2"], [(a, q, "") for a, q in aud], 282, [340, 1000, 268], rh=82, size=28)
  + "\n" + band(7, 830, 80, "Twelve points. <b>Under eight means fix the store before you pay for more visitors.</b>", size=28, extra="padding:20px 40px;"),
  """One area per click. A practical audit, usable on any store — your own, a rival's, or a business you advise. Score each area 0 (missing), 1 (partly) or 2 (done well). Twelve is the maximum.

The threshold of eight is a teaching rule of thumb, not research: the point is that buying traffic for a weak store wastes money.

Speed: open it on a phone on mobile data, not office wifi.

Next: they use it on a real store in Exercise 2.""",
  footer="A practical checklist &middot; the threshold is a rule of thumb")

S["ex2"] = exercise("ex2", "Exercise 2", "Audit a real Pakistani store",
  "Pick one store your team would buy personal care or home care from. Score it with the twelve-point audit, on a phone.",
  ["Where did it lose points?", "Which fix would cost the least?", "Which fix would win the most orders?", "Would you buy from it now?"],
  "Exercise 2 &middot; the twelve-point audit",
  """Fifteen minutes in teams. One question per click.

Teams choose a real store — an own site, a Daraz store or an Instagram seller — in the simulation's category if possible. Each team audits on a phone, on mobile data.

Take three teams' answers at the end: the store, its score, and the one cheapest fix. Look for the pattern: most stores lose points on cost visibility and on what happens after the order.""", top=500, h=180, cols=2)

S["part2"] = div("part2", "Part 2 &middot; The simulation", "Your store in<br>the simulation",
  "Conversion becomes a number you own: store experience, packaging and payments open this month.",
  """Part 2 is the simulation. Month 2 has run. Three decisions open this round: website experience (5.1), packaging (8.5) and payment gateway (9.3).

Every number in Part 2 is the simulation's assumption or a test run of it, not market data.""")

mult = [("Price", "Your price against the market average", "More than any other single factor"),
        ("Store experience", "Website investment, capped by your tech stack", "Lands the month after you spend"),
        ("Rating", "Last month's rating, from quality, delivery and packaging", "Earned slowly, lost slowly"),
        ("Payments", "Cash on delivery, and the gateway's success rate", "A failed payment is a lost order"),
        ("Delivery and stock", "Reliable couriers, and products in stock", "An empty shelf converts nobody")]
S["sim-cr"] = sec("sim-cr", "#fdeceb", "In the simulation", "What turns a visit into an order",
  trows(["Factor", "What sets it", "Worth knowing"], mult, 282, [360, 760, 488], rh=96, size=27)
  + "\n" + band(6, 820, 90, "Conversion is all of these <b>multiplied together</b>: one weak factor drags the rest.", size=28, extra="padding:22px 40px;"),
  """One factor per click. The simulation's conversion rate multiplies these factors (plus how well your range fits your segments). Because they multiply, a store that is excellent on four and broken on one still converts poorly.

Baseline conversion in the simulation is about 2%.

Ask each team to find their conversion rate and rating in the month-2 report before the next slide.""",
  footer="The simulation's conversion model &middot; not market data")

S["sim-levers"] = sec("sim-levers", "#ffffff", "In the simulation", "Three decisions open this month",
  grid([
    ("5.1 &middot; Website experience", "Spend to improve the store", "Each month's spend closes part of the gap to the best your tech stack allows: PKR 300,000 closes half of it. The gain shows the month after.", "#ed0000"),
    ("8.5 &middot; Packaging", "Basic, branded or premium", "Better packaging lifts your rating and repeat buying, and costs more on every order you ship.", "#eb6834"),
    ("9.3 &middot; Payment gateway", "A, B or C", "Gateway B is cheapest but only 84% of payments succeed; A 91%; C 96% at the highest fee.", "#2a78d6"),
  ], 3, 300, 400, bsize=26)
  + "\n" + band(4, 740, 140, "Each one trades a cost you can see for orders you cannot see yet. <b>Which would your month-2 report tell you to fix first?</b>", size=29),
  """One decision per click. The rules are the simulation's.

Website experience (5.1): each month's spend closes part of the gap between your current store and the ceiling your founding tech stack allows. PKR 300,000 closes half of the gap; the effect has diminishing returns and appears the month after the spend. A basic stack has a low ceiling — investment cannot take it beyond that.

Packaging (8.5): raises the rating (which lifts next month's conversion) and repeat purchase, at a cost on every order.

Gateway (9.3): the success rate multiplies conversion; the fee applies only to prepaid orders. A cheap gateway that fails one payment in six costs far more than its fee saves.""",
  footer="Decision rules from the simulation &middot; not market data")

tests = [("Website: PKR 300,000 in month 2", "+6% orders in month 3", "Conversion 2.03% &rarr; 2.14%, and the better store stays"),
         ("Gateway C instead of A", "+PKR 0.35m", "Contribution over months 2&ndash;6; conversion 2.05% &rarr; 2.17%"),
         ("Gateway B instead of A", "&minus;PKR 0.52m", "Contribution over months 2&ndash;6; the saving on fees is lost on failed payments"),
         ("Premium packaging", "Rating 4.07 &rarr; 4.17", "By month 6; paid for on every order shipped")]
S["sim-tests"] = sec("sim-tests", "#f5f5f6", "In the simulation", "What the levers did in test runs",
  trows(["Test, all else default", "Result", "Detail"], tests, 282, [560, 380, 668], rh=110, size=27)
  + "\n" + band(5, 800, 100, "<b>Which of these pays back fastest for your business, not the default one?</b>", size=29),
  """One test per click. Each line compares one team that changed a single decision with an identical team on every default, in the same simulated market.

Website: PKR 300,000 spent in month 2 raised month-3 orders by about 6%. The UX gain persists, so the spend keeps paying in later months.
Gateway C over A: about PKR 350,000 more contribution over five months. Gateway B: about PKR 520,000 less, despite the lower fee.
Premium packaging: rating up a tenth of a point by month 6 — slow, and paid on every order.

Results depend on each team's own setup: price position, segments and stock all change the outcome.""",
  footer="Simulation test runs, all else default &middot; not market data")

S["checks"] = sec("checks", "#fdeceb", "Before month 3 runs", "Audit your own store",
  grid([
    ("Conversion", "Is your conversion above 2%?", "If not, which factor on the multiplier slide is dragging it?", "#ed0000"),
    ("Rating", "Is your rating rising or falling?", "It sets next month's conversion, so act now.", "#eb6834"),
    ("Payments", "How many payments fail?", "Compare your gateway's success rate with its fee.", "#2a78d6"),
    ("Memo", "What will prove you right?", "Name the number in next month's report, in the board memo.", "#1baf7a"),
  ], 4, 300, 330)
  + "\n" + band(5, 690, 150, "Fix the store before you fill it: <b>marketing opens in Session 7</b>, and every visitor you pay for will meet the store you build now.", size=30),
  """One question per click, while teams fill in the decision form.

Logistics for the notes, not the slide: decisions for month 3 close at [deadline]. Open this round: 5.1 website experience, 8.5 packaging, 9.3 payment gateway, plus last session's prices and the board memo.""")

S["next"] = sec("next", "#131316", "Next session", "What to sell and how to price it",
  grid([
    ("Session 5", "Would three be better than one?", "Bundles open, and the average order can grow.", "#ff3b3b"),
    ("Delivery", "When should delivery be free?", "Set the order value above which you pay the courier.", "#ff3b3b"),
    ("Discounts", "Which line deserves a discount?", "Product by product, not across the shelf.", "#ff3b3b"),
  ], 3, 300, 300, bg="#1f1f24", border="border:1px solid #33333b;", tcol="#ffffff", bcol="#c9c9d1")
  + "\n" + band(4, 660, 150, "Today: how many visitors become orders. Next time: <b>how big each order becomes</b>.", bg="#ed0000", size=31),
  """Close. One card per click.

Session 5 opens bundles (1.2), the free-delivery threshold (2.4) and product-by-product discounting in 1.1. It builds on Session 3's discount lesson and today's checkout lesson: a free-delivery threshold is the answer to "extra costs too high".""", dark=True, eyecol="#ff3b3b")

ORDER = ["cover", "recall", "ex1", "part1", "shopper", "attributes", "shopper-data", "channels", "case-channel", "pdp", "photos", "trust", "checkout", "cx",
         "case-trust", "audit", "ex2", "part2", "sim-cr", "sim-levers", "sim-tests", "checks", "next"]
assert set(ORDER) == set(S), set(S) ^ set(ORDER)
logo = sys.argv[2] if len(sys.argv) > 2 else "__LOGO__"
root = pathlib.Path(sys.argv[1]) / "project"
(root / "slides").mkdir(parents=True, exist_ok=True)
for k, v in S.items():
    (root / "slides" / f"{k}.html").write_text(v.replace("__LOGO__", logo.rsplit("/", 1)[-1]))
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-10-03T09:00:00Z"}, "lists": "css",
        "title": "Session 4 — Building Your Online Store", "order": ORDER,
        "sections": {
          "open": {"description": "Building your online store, and what we covered last week", "start": "cover"},
          "channel": {"description": "Part 1 · Website, marketplace or social media, with cases", "start": "part1"},
          "store": {"description": "Product pages, photos, trust, checkout and customer experience", "start": "pdp"},
          "audit": {"description": "The ten-minute store audit", "start": "audit"},
          "sim": {"description": "Part 2 · Your store in the simulation", "start": "part2"}},
        "faces": {"inter": {"family": "Inter", "href": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono"}},
        "designSystems": []}
if not (root / "deck.json").exists():
    (root / "deck.json").write_text(json.dumps(deck, indent=2, ensure_ascii=False))
print("wrote", len(S))
