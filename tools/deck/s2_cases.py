"""Case-study slides for Part 1 and the Part 2 opener (personal care & home care)."""
import pathlib, sys, json
src = pathlib.Path(__file__).with_name("s2_slides.py").read_text()
exec(src.split("slides = {}")[0])

def case_card(n, L, where, name, meta, rows, tagcol):
    rows_html = "\n".join(
        f'''    <div style="display:flex; flex-direction:column; gap:2px">
      <p style="font-size:19px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:#86868f">{k}</p>
      <p style="font-size:24px; line-height:1.38; color:#33333b">{v}</p>
    </div>''' for k, v in rows)
    return f'''  <div data-build-in="fade {n}" style="position:absolute; left:{L}px; top:272px; width:819px; height:436px; background:#ffffff; padding:30px 34px; border-radius:18px; border:1px solid #e4e4e7; display:flex; flex-direction:column; gap:14px">
    <div style="display:flex; align-items:baseline; gap:18px">
      <p style="font-size:20px; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:{tagcol}">{where}</p>
      <h3 style="font-size:34px; font-weight:700; color:#131316">{name}</h3>
      <p style="font-size:22px; color:#86868f">{meta}</p>
    </div>
{rows_html}
  </div>'''

def case_slide(sid, eyebrow, title, pk, gl, lesson, notes, footer):
    body = (case_card(1, 128, *pk, "#ed0000") + "\n" + case_card(2, 973, *gl, "#2a78d6")
            + "\n" + band(3, 732, 100, lesson, size=29))
    return section(sid, "#f5f5f6", "#131316", eyebrow, title, body, notes, footer=footer)

def divider(sid, part, title, line, notes):
    return f'''<section id="{sid}" data-transition="fade" style="background:#131316; color:#ffffff; {FONT}; padding:128px 128px 160px; display:flex; flex-direction:column; gap:28px">
  <img src="/_blob/856d57cb939a323d46943b3b229572d7" alt="Consulytics.AI" style="width:340px; height:67px; object-fit:contain">
  <div style="height:90px; flex:0 0 auto"></div>
  <p style="font-size:28px; font-weight:600; letter-spacing:4px; text-transform:uppercase; color:#ff3b3b">{part}</p>
  <h1 style="font-size:112px; font-weight:700; line-height:1.04; letter-spacing:-3px">{title}</h1>
  <p data-build-in="fade 1" style="position:absolute; left:128px; top:720px; width:1500px; height:120px; font-size:36px; line-height:1.45; color:#c9c9d1">{line}</p>
  {FOOT.format("Session 2 &middot; Finding the Right Idea")}
  <aside>{notes}</aside>
</section>
'''

slides = {}
slides["part1"] = divider("part1", "Part 1 &middot; Theory",
  "Four questions every<br>founder answers",
  "Finding customer problems, spotting opportunities, choosing products and knowing the customer &mdash; each with a Pakistani and a global case.",
  """Part 1 is theory from real-world e-commerce practice, with no simulation in it. Four blocks: finding customer problems, identifying opportunities, choosing products, understanding the target customer.

Each block ends with two short cases, one Pakistani and one global, so the idea is tied to a company the room knows.

Part 2 then applies the same four questions to the simulation's market: personal care and home care.""")

slides["case-problems"] = case_slide("case-problems", "Cases &middot; Finding customer problems",
  "The problem was already in plain sight",
  ("Pakistan", "Daraz", "marketplace",
   [("The problem", "Shoppers would not pay before seeing the product, and worried about fakes."),
    ("What they did", "Made cash on delivery the default and gave official brands their own Daraz Mall stores."),
    ("The lesson", "The first problem was trust, not the product. Fix the buying experience.")]),
  ("Global", "Dollar Shave Club", "US, 2011",
   [("The problem", "Razor blades cost too much and sat in a locked cabinet at the pharmacy."),
    ("What they did", "A razor subscription from US$1 a month, launched with a US$4,500 video: 12,000 orders in 48 hours."),
    ("The result", "3.2 million subscribers; bought by Unilever for US$1 billion in 2016.")]),
  "Both started from an irritation millions of people shared &mdash; and both fixed <b>how people buy</b> as much as what they buy.",
  """Two cases, one per click, then the lesson.

Daraz: in Pakistan the question "COD hai?" is the problem. Shoppers did not trust paying in advance, and worried about fake goods. Cash on delivery became the default and Daraz Mall gave official brands a storefront. The problem was trust, and it showed up in exactly the places on the previous slide: questions, refused parcels, reviews.

Dollar Shave Club (US, founded 2011): Michael Dubin's irritation was expensive blades locked behind a pharmacy counter — a problem every man shared. A razor subscription from $1 a month, a launch video that cost about $4,500 and brought 12,000 orders in two days. Five years later, 3.2 million subscribers and a $1 billion sale to Unilever (2016).

Question for the room: where would you have found the Dollar Shave Club problem — reviews, search, conversations, returns or workarounds?

Sources: Fortune and Marketplace on the Unilever deal (July 2016); Daraz's own site for COD and Daraz Mall.""",
  "Sources: company sites; Fortune, Marketplace (2016)")

slides["case-opportunity"] = case_slide("case-opportunity", "Cases &middot; Identifying opportunities",
  "Big and frequent is not enough",
  ("Pakistan", "Airlift", "2019&ndash;2022",
   [("The opportunity", "Groceries and essentials in 30 minutes: needed often, by millions, in eight cities."),
    ("What they did", "Raised US$85m in 2021 at a US$275m valuation, then spent fast to grow."),
    ("The result", "Shut down in July 2022 when funding dried up before the business covered its costs.")]),
  ("Global", "Webvan", "US, 1999&ndash;2001",
   [("The opportunity", "Online groceries delivered to the door: the same big, frequent need."),
    ("What they did", "Raised about US$800m and ordered US$1bn of warehouses before demand was proven."),
    ("The result", "In 2000: US$178m of sales against US$525m of costs. Bankrupt in 2001.")]),
  "Both passed <i>big enough</i> and <i>often enough</i>. Neither was <b>profitable enough</b> before the money ran out.",
  """Two cases on the three opportunity tests from the previous slide.

Airlift: Pakistan's best-funded startup of its time. Quick commerce in eight cities including Lahore, Karachi and Islamabad. Raised $85 million in August 2021 at a $275 million valuation. By its own account it had reached order-level profitability and cut burn by two thirds, but was still months away from covering its full costs when its lead investor pulled out. It shut down in July 2022.

Webvan: the classic US dot-com failure. Raised about $800 million, placed a $1 billion order for warehouses, and in 2000 had $178.5 million of sales against $525.4 million of expenses. Bankrupt in 2001.

The point: groceries are a huge, frequent need — they pass the first two tests easily. The third test, margin after delivery and the cost of winning each order, is where both failed. And "profitable enough" has a clock on it: how long your cash lasts.

Question for the room: what would you have needed to believe about each delivery to fund Airlift?

Sources: TechCrunch, Dawn and Rest of World (July 2022); Wikipedia and YourStory on Webvan.""",
  "Sources: TechCrunch, Dawn, Rest of World (2022); Webvan filings as reported")

slides["case-products"] = case_slide("case-products", "Cases &middot; Choosing products",
  "Start narrow, with products that travel well",
  ("Pakistan", "Conatural", "2016",
   [("The gap", "The founders kept buying imported skincare; local shelves were full of whitening creams."),
    ("What they did", "Launched with seven natural skincare products, made with chemists from abroad."),
    ("The result", "Grew to about 150 products across skin, hair and men's care; raised US$825k.")]),
  ("Global", "Amazon", "US, 1995",
   [("The choice", "Books only: millions of titles no shop could stock, identical wherever you buy them."),
    ("Why online", "Easy to post, nothing to try on, and search beats a shop's shelf."),
    ("The result", "Only once the model worked did it widen into music, electronics and everything else.")]),
  "A narrow first range, chosen because it <b>suits selling online</b> &mdash; then widen once it works.",
  """Two cases on choosing products and building the first range.

Conatural: founded in 2016 by sisters Myra Qureshi and Rema Taseer. One of them was allergic to many chemicals, and they kept buying imported skincare. They launched with seven products and grew to about 150 formulations across skincare, haircare, men's and salon, with $825,000 of pre-Series A funding. Directly relevant: it is a Pakistani personal-care brand — the category the simulation uses in Part 2.

Amazon: Jeff Bezos chose books because there were millions of titles, more than any shop could stock, and a book is the same product wherever you buy it — no need to touch or try it. Search online beats walking a shelf. Categories came later.

Tie back to the product tests: bought again, easy to ship, hard to get wrong, trusted from a photo, and margin that survives delivery.

Question for the room: which of the product tests did books pass that clothing would fail?

Sources: Formula Botanica and Business Recorder on Conatural; Amazon's founding story is widely documented.""",
  "Sources: Formula Botanica, Business Recorder; company histories")

slides["case-customer"] = case_slide("case-customer", "Cases &middot; Understanding the target customer",
  "Build for one customer you know well",
  ("Pakistan", "Bazaar", "Karachi, 2020",
   [("The customer", "The kiryana shop owner, not the household shopper: busy, offline, short of cash."),
    ("What they did", "Next-day delivery of stock to the shop, then a free bookkeeping app and credit."),
    ("The result", "Over US$100m raised by 2022; its Easy Khata app used by 2.4m businesses.")]),
  ("Regional", "Mamaearth", "India, 2016",
   [("The customer", "New parents afraid of harsh chemicals on a baby's skin. The founders were those parents."),
    ("What they did", "Six toxin-free baby products, tested with 700 mothers, launched on Amazon India."),
    ("The result", "Widened into skin and hair care for the whole family once parents trusted it.")]),
  "Both began with <b>one customer they understood deeply</b> and widened only after winning them.",
  """Two cases on the target customer.

Bazaar (founded June 2020 by Hamza Jawaid and Saad Jangda): chose the kiryana store owner as the customer, not the consumer. It solved that person's problems one after another: getting stock without visiting the wholesaler, keeping accounts (Easy Khata, used by more than 2.4 million businesses) and working capital (Bazaar Credit). Raised a $70 million Series B in 2022, over $100 million in total.

Mamaearth (India, 2016): Ghazal and Varun Alagh could not find safe products for their newborn son's sensitive skin. They launched six baby-care products in December 2016 after testing with over 700 mothers, first on Amazon India. The brand widened into skincare and haircare once parents trusted it. A regional case, but the closest to the simulation's category.

Tie back to the persona slide: both founders could describe their customer's day in detail.

Question for the room: describe the Mamaearth customer in one sentence, the way we described Sana.

Sources: Dawn, MENAbytes, Forbes (2022) on Bazaar; Mamaearth's own story and The Better India.""",
  "Sources: Dawn, MENAbytes, Forbes (2022); Mamaearth company story")

slides["part2"] = divider("part2", "Part 2 &middot; The simulation",
  "Personal care &amp;<br>home care",
  "The same four questions, now applied to the market you will run for the next twelve months.",
  """Part 2 moves from theory to the simulation. The category is personal care and home care in Pakistan — skin, hair, hygiene, homecare and baby.

First, one slide on what this category looks like online in the real world. Then the simulation's market, how today's theory maps onto the founding decisions, its customer segments, and the founding exercise.""")

slides["catreal"] = section("catreal", "#ffffff", "#131316", "Part 2 &middot; The real category",
  "Personal care and home care online in Pakistan",
  grid([
    ("Problem", "“Original hai?”", "Fakes and near-copies in beauty make trust the first problem to solve. Genuine stock and honest listings sell.", "#ed0000"),
    ("Opportunity", "Bought again and again", "Shampoo, soap and detergent run out every few weeks. Repeat buying is built into the category.", "#1baf7a"),
    ("Products", "Heavy, cheap and liquid", "Homecare is bulky and low-priced, so delivery and leaks eat margin. Bundles and minimum orders matter.", "#8a6414"),
    ("Customer", "Big brands own the shelf", "Unilever, P&amp;G, Reckitt and Colgate lead in shops. Online challengers win a niche: natural, derma, men's, value.", "#2a78d6"),
  ], 2, 280, 230)
  + "\n" + band(5, 780, 120, "Conatural and Mamaearth are this category. The simulation asks you to find <b>your</b> way into it.", size=30),
  """One card per click, one per question from Part 1. These are general observations of the real market, not measured data.

Problem — trust. In beauty especially, buyers worry about fakes and expired stock; "original hai?" is the most common question in the comments. Proof of authenticity is a selling point.

Opportunity — frequency. These products run out, so a customer won once can be sold to every month. That is what makes the cost of winning them worth paying.

Products — shipping economics. Homecare is heavy, cheap and liquid: a PKR 400 bottle of dish liquid can cost almost as much to deliver as it earns. Skincare is light and high-margin. That difference will matter in the simulation.

Customer — the incumbents. The multinationals and large local companies own general trade and supermarket shelves. Online challengers rarely beat them head-on; they win a niche.

Then: the simulation's version of this market.""",
  footer="General market observations, not measured data")

S = pathlib.Path(sys.argv[1]) / "project" / "slides"
for k, v in slides.items():
    (S / f"{k}.html").write_text(v)
print("wrote", list(slides))
