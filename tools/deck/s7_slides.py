"""Session 7 - How Will You Get Customers? About 25 slides.

Run: python s7_slides.py <deck folder> [logo url]
Part 2's numbers come from tools/deck/s7_s8_tests.py (one baseline game, six
teams, every default; one team changes one decision).
"""
import pathlib, sys, json
HERE = pathlib.Path(__file__).parent
exec((HERE / "s6_slides.py").read_text().split("\nS = {}\n")[0])
FT = "Session 7 &middot; How Will You Get Customers?"
def sec(sid, bg, eyebrow, title, body, notes, footer=FT, **kw):
    return section(sid, bg, "#131316", eyebrow, title, body, notes, footer=footer, **kw)
def div(sid, part, title, line, notes):
    return divider(sid, part, title, line, notes).replace("Session 2 &middot; Finding the Right Idea", FT).replace("856d57cb939a323d46943b3b229572d7", "__LOGO__")

def two(n, L, T, W, H, label, title, items, col):
    li = "".join(f'<p style="font-size:25px; line-height:1.38; color:#33333b">&middot; {x}</p>' for x in items)
    return f'''  <div data-build-in="fade {n}" style="position:absolute; left:{L}px; top:{T}px; width:{W}px; height:{H}px; background:#ffffff; padding:26px 32px; border-radius:18px; border:1px solid #e4e4e7; display:flex; flex-direction:column; gap:8px">
    <p style="font-size:21px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:{col}">{label}</p>
    <h3 style="font-size:30px; font-weight:600; color:#131316">{title}</h3>
    {li}
  </div>'''

def cover(n, title_html, promise, notes, size=132):
    return f'''<section id="cover" data-transition="fade" style="background:#131316; color:#ffffff; {FONT}; padding:128px 128px 160px; display:flex; flex-direction:column; justify-content:space-between">
  {LOGO}
  <div style="display:flex; flex-direction:column; gap:28px">
    <p style="font-size:28px; font-weight:600; letter-spacing:4px; text-transform:uppercase; color:#ff3b3b">Session {n} of 12</p>
    <h1 style="font-size:{size}px; font-weight:700; line-height:1.02; letter-spacing:-3px">{title_html}</h1>
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
  <p data-build-in="fade 1" style="position:absolute; left:128px; top:647px; width:1400px; height:110px; font-size:38px; line-height:1.45; color:#c9c9d1">{promise}</p>
  <aside>{notes}</aside>
</section>
'''

def write(S, ORDER, title, sections):
    assert set(ORDER) == set(S), set(S) ^ set(ORDER)
    logo = sys.argv[2] if len(sys.argv) > 2 else "__LOGO__"
    root = pathlib.Path(sys.argv[1]) / "project"
    (root / "slides").mkdir(parents=True, exist_ok=True)
    for k, v in S.items():
        (root / "slides" / f"{k}.html").write_text(v.replace("__LOGO__", logo.rsplit("/", 1)[-1]))
    deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-10-17T09:00:00Z"}, "lists": "css",
            "title": title, "order": ORDER, "sections": sections,
            "faces": {"inter": {"family": "Inter", "href": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap"},
                      "jetbrains-mono": {"family": "JetBrains Mono"}},
            "designSystems": []}
    if not (root / "deck.json").exists():
        (root / "deck.json").write_text(json.dumps(deck, indent=2, ensure_ascii=False))
    print("wrote", len(S))

S = {}
S["cover"] = cover(7, "How Will You<br>Get Customers?",
  "Social media, Meta ads, Google, influencers, content and performance marketing &mdash; and a customer acquisition plan.",
  """Two hours, about 25 slides: 3 min recap, 8 min opening exercise, Part 1 theory about 65 min (the funnel and paid, owned and earned 10, paid social and search 15, the numbers of a campaign 10, influencers and content 15, brand against performance 10, what a customer is worth and the plan 10), exercise 10, Part 2 simulation about 30 min, 3 min close.

Month 5 has run. Today's decisions open for month 6: 3.1 Meta, 3.2 Google, 3.4 TikTok, 3.10 campaign setup, 3.6 affiliate and influencer commission, 3.8 creative, 3.9 brand-building.

The idea for the day: every customer costs something to find. The job is not to buy the cheapest click, but the customer who stays.""")

S["recall"] = sec("recall", "#f5f5f6", "Where we got to last week", "Where you sell decides who keeps the customer",
  grid([
    ("Marketplace", "Rent their shoppers", "Instant reach; a commission on every order; the buyer stays theirs.", "#ed0000"),
    ("Own website", "Own the customer", "No commission &mdash; but you bring every visitor yourself.", "#2a78d6"),
    ("Social", "Sell in the conversation", "Cheap to start, slow to scale: every order is a chat.", "#1baf7a"),
  ], 3, 300, 300)
  + "\n" + band(4, 660, 170, "Last week: <b>where</b> the shop stands. Today: <b>how</b> customers find it &mdash; and what each one costs to bring.", size=31),
  """Three quick clicks from Session 6.

The bridge: an own website or Instagram page has no customers until someone brings them. That bringing is customer acquisition, and it has a price per customer. Sessions 6 and 7 are a pair: choose the place, then pay to bring people to it.""")

S["ex1"] = exercise("ex1", "Exercise 1", "How did the last brand find you?",
  "Think of the last thing you bought online from a brand you had not bought from before.",
  ["Where did you first see it?", "Were you looking for it &mdash; or did it find you?",
   "What made you click, and what made you buy?", "Would you buy again without seeing another ad?"],
  "Exercise 1 &middot; every customer arrived through a channel",
  """Eight minutes. One question per click; take a show of hands, then three stories.

Sort the answers on the spot into the channels of today's session: an Instagram or TikTok post or ad (paid social), a Google search (search), a creator or a friend (influencer or word of mouth), a video or article (content), or "I already knew the name" (brand).

Question 2 separates two kinds of demand: people already looking (search catches them) and people who did not know they wanted it (social and creators create the want).

Question 4 is the retention question that Session 8 picks up: the first order is bought; the second should not need to be.""", top=500, h=180, cols=2)

S["part1"] = div("part1", "Part 1 &middot; Theory", "Bringing customers<br>to you",
  "The funnel; paid social and search; influencers and content; brand against performance &mdash; each with a Pakistani and a global case.",
  """Part 1 follows the course outline: social media and Meta ads, Google, influencers, content and performance marketing, ending with a customer acquisition plan. Real-world practice only; the simulation is Part 2.""")

S["funnel"] = sec("funnel", "#ffffff", "The funnel", "From stranger to customer, in four steps",
  grid([
    ("Awareness", "They hear of you", "A video, a post, a creator, a billboard. Measured in reach and impressions.", "#ed0000"),
    ("Consideration", "They look closer", "They visit, read reviews, compare prices. Measured in clicks and visits.", "#eb6834"),
    ("Conversion", "They buy", "Cart, checkout, payment. Measured in orders and conversion rate.", "#2a78d6"),
    ("Repeat", "They come back", "And tell others. Measured in repeat orders &mdash; Session 8.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "Each channel is strongest at one step. <b>Which step is your brand losing people at?</b>", size=30),
  """One step per click.

The funnel is a simplification &mdash; real people jump around &mdash; but it organises the channels. Brand advertising and creators work at the top; search and retargeting work in the middle; the website, price and checkout decide the bottom (Session 4); retention is the loop back (Session 8).

A brand that spends at the top but has a weak store pays for attention it cannot convert. A brand that only buys bottom-of-funnel search runs out of people who already know to search for it.""")

S["poe"] = sec("poe", "#f5f5f6", "Three kinds of media", "Paid, owned and earned",
  grid([
    ("Paid", "You buy the attention", "Meta, TikTok and Google ads; paid creators. Fast, measurable, stops the day you stop paying.", "#ed0000"),
    ("Owned", "You control the channel", "Your website, Instagram page, WhatsApp list, email list. Free to use, slow to build.", "#2a78d6"),
    ("Earned", "Others talk about you", "Reviews, shares, press, word of mouth. The most trusted, the least controllable.", "#1baf7a"),
  ], 3, 300, 330)
  + "\n" + band(4, 690, 170, "Good acquisition plans use <b>paid</b> to start, turn the people it brings into an <b>owned</b> audience, and give them a reason to create <b>earned</b> media.", size=30),
  """One kind per click.

Paid media rents attention. Owned media is attention you have already won and can reach again for almost nothing (this is why the customer's number matters so much: Session 6's own-site argument). Earned media is attention other people give you.

The cost of a customer falls as owned and earned grow: a brand with 50,000 followers and good reviews pays less for each new buyer than one starting cold.""")

S["social"] = sec("social", "#ffffff", "Paid social", "Meta and TikTok: ads that find people",
  two(1, 128, 280, 819, 300, "How it works", "The platform picks who sees it",
      ["You set the budget, the goal and a broad audience", "The algorithm shows the ad to people likely to act", "You pay per thousand views (CPM) or per click"], "#ed0000")
  + "\n" + two(2, 973, 280, 819, 300, "What decides the result", "The creative is the targeting",
      ["The first three seconds decide who stops scrolling", "Many versions tested; the winners get the budget", "Ads tire: the same one loses power in weeks"], "#ed0000")
  + "\n" + two(3, 128, 600, 819, 280, "Meta (Facebook, Instagram)", "The broad workhorse",
      ["Largest audience; reels, stories and the feed", "Good for products people discover"], "#2a78d6")
  + "\n" + two(4, 973, 600, 819, 280, "TikTok", "Cheap reach, short attention",
      ["Younger audience; trends move fast", "Cheap views; buyers may be less certain"], "#2a78d6"),
  """Four clicks.

Paid social creates demand: the people who see the ad were not searching. Modern platforms do most of the targeting themselves; the brand's real lever is the creative. That is why brands make many short versions and let the platform find the winners.

Ad fatigue: an ad shown repeatedly to the same people gets fewer clicks each week, so creative has to be refreshed.

The global case later shows the risk: the platform's targeting and measurement depend on data the brand does not control.""")

S["search"] = sec("search", "#f5f5f6", "Search", "Google: catching people who are already looking",
  grid([
    ("Intent", "They typed what they want", "&ldquo;Anti-dandruff shampoo price&rdquo; is a buyer, not a browser.", "#ed0000"),
    ("Keywords", "You bid on words", "Generic words are expensive; your own brand name is cheap.", "#eb6834"),
    ("Cost", "Pay per click", "Clicks cost more than on social &mdash; and convert better.", "#2a78d6"),
    ("Limit", "Only as big as demand", "Search cannot create people who are not yet searching.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "Social <b>creates</b> demand; search <b>captures</b> it. When people start searching for your name, your brand is working.", size=30),
  """One card per click.

Search ads appear when someone types a query. The price of each click is set in an auction: the more advertisers want a word, the more it costs. Brand search (people typing your name) is the cheapest and best-converting traffic there is, and it grows when other marketing works.

Google Shopping and Performance Max show products with price and picture directly in results; they need a clean product feed.

Organic search (SEO) is the unpaid version: pages that rank because they answer the question well. It is content marketing's long game (later in the session).""")

camp = [("Impressions", "How many times the ad was shown", "100,000"),
        ("CTR &middot; click-through rate", "Clicks &divide; impressions", "1.5% &rarr; 1,500 clicks"),
        ("CPC &middot; cost per click", "Spend &divide; clicks", "Rs 20 &rarr; Rs 30,000 spent"),
        ("CVR &middot; conversion rate", "Orders &divide; clicks", "2% &rarr; 30 orders"),
        ("CAC &middot; acquisition cost", "Spend &divide; new customers", "Rs 1,000 a customer"),
        ("ROAS &middot; return on ad spend", "Revenue &divide; spend", "30 &times; Rs 3,000 &divide; 30,000 = 3.0")]
S["metrics"] = sec("metrics", "#ffffff", "The numbers of a campaign", "Six numbers that explain any campaign",
  trows(["Measure", "What it is", "Example"], camp, 276, [520, 560, 528], rh=72, size=27)
  + "\n" + band(7, 770, 120, "ROAS 3.0 sounds good &mdash; but if the margin before marketing is 30%, <b>every rupee of ads returned 90 paisa</b>.", size=29),
  """Illustrative numbers. One row per click.

Read down the funnel: impressions become clicks (CTR), clicks cost money (CPC), clicks become orders (CVR). CAC divides spend by new customers; ROAS divides revenue by spend.

The trap is ROAS. Revenue is not profit: at a 30% margin before marketing, a ROAS of 3.0 gives back Rs 0.90 of margin per rupee spent &mdash; a loss on the first order, unless the customer buys again. Breakeven ROAS = 1 &divide; margin; at 30% margin it is 3.3.

Platforms also count generously: an ad platform may claim a sale the customer would have made anyway. Session 10 returns to measurement.""",
  footer="Illustrative numbers")

S["case-perf"] = cases("case-perf", "Cases &middot; Performance marketing", "Search and video at a sale; data the platform owns",
  ("Pakistan", "Daraz", "Black Friday 2017", [
    ("The insight", "Working with Google, Daraz saw searches for &lsquo;Black Friday&rsquo; up three times on the year before."),
    ("The result", "YouTube and display for reach, search to capture: a Rs 1bn sales goal tripled; conversions up 3&times;.")]),
  ("Global", "Meta", "Apple's iOS 14.5, 2021", [
    ("The change", "Apple let iPhone users refuse tracking by apps. Most did, so ads were harder to target and measure."),
    ("The cost", "Meta estimated a hit of about US$10bn to its 2022 revenue; advertisers' results got harder to read.")]),
  "Performance marketing works best on <b>demand you can see</b> &mdash; and it runs on data that belongs to the platform.",
  """Two performance-marketing cases.

Daraz, Black Friday 2017 (Think with Google case study): working with Google, Daraz found a three-fold year-on-year rise in searches around "Black Friday". It set a goal of Rs 1 billion in sales for the sale (24&ndash;27 November 2017), used YouTube and the Google Display Network for awareness and search to capture demand, and reported tripling its sales goal, with twice the reach and three times the conversions. Pakistan Today reported Rs 3 billion of sales over the four days.

Meta: Apple's App Tracking Transparency, in iOS 14.5 (April 2021), asks iPhone users whether apps may track them across other apps. Most decline. On its Q4 2021 call, Meta's CFO estimated the hit to 2022 revenue at about US$10 billion, calling it an estimate. For advertisers, ads became harder to target and their results harder to measure.

The lesson: performance marketing is powerful where demand already exists and can be measured, but the brand rents both the audience and the measurement.

Question for the room: what would you search for before a sale, and which ad would you click?

Sources: Think with Google APAC (Daraz case study); Pakistan Today (Dec 2017); CNBC (2 Feb 2022).""",
  "Sources: Think with Google (Daraz); Pakistan Today (2017); CNBC (Feb 2022)")

S["creators"] = sec("creators", "#f5f5f6", "Influencers", "Borrowing someone else's trust",
  grid([
    ("Mega and celebrity", "Millions of followers", "Huge reach, expensive, and the audience knows it is an ad.", "#ed0000"),
    ("Micro", "Ten to a hundred thousand", "A niche that listens: skincare, mums, students. Cheaper and more trusted.", "#eb6834"),
    ("How they are paid", "Fee, free product or commission", "A discount code or link shows which creator brought which sale.", "#2a78d6"),
    ("The rule", "Say it is paid", "Followers forgive an ad; they do not forgive a hidden one.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "An influencer sells <b>trust</b>, not reach. <b>Whose recommendation would make you try a new face wash?</b>", size=30),
  """One card per click.

Creators matter because people trust a person more than a brand. Smaller creators often have more engaged audiences in a niche, which is why brands run many micro-influencers rather than one celebrity.

Payment models: a flat fee per post; free products (gifting); or commission per sale tracked with a code or link (affiliate). Commission costs nothing until something sells, which is why brands like it &mdash; and why creators prefer a fee.

Disclosure: platforms and advertising codes expect paid partnerships to be labelled; hidden ads damage both the creator and the brand when found out.""")

S["case-influence"] = cases("case-influence", "Cases &middot; Influencers", "A following becomes a sales channel",
  ("Pakistan", "Skin Recipe", "Aiman and Minal Khan", [
    ("The launch", "The actress twins launched their own skincare label and announced it together on Instagram."),
    ("The channel", "Their own following is the first audience; celebrity labels are now common in Pakistani beauty.")]),
  ("Global", "Daniel Wellington", "Sweden, 2011", [
    ("The method", "Gave watches to many smaller Instagram creators instead of buying traditional ads, often with a code."),
    ("The scale", "Company-reported revenue of about US$220m by 2015, from a start of about US$15,000.")]),
  "One brand <b>owns</b> the audience; the other <b>borrows</b> thousands of them. Both sell on a person's trust.",
  """Two influencer cases.

Skin Recipe: the actress twins Aiman and Minal Khan launched the skincare label and announced it together on Instagram (Jang). Celebrity- and creator-founded beauty brands are now a pattern in Pakistan: Ayesha Omar's Ayesha O Beauty (2021), Shahid Afridi's personal-care line Ooh Lala (2021), Komal Rizvi's Truly Komal (2019). The founder's own following is the launch channel; the risk is that the brand depends on one person's reputation.

Daniel Wellington: the Swedish watch brand founded in 2011 by Filip Tysander grew largely through Instagram, giving watches to large numbers of smaller creators in exchange for posts, often with a discount code, rather than buying traditional advertising (Bloomberg, via Practical Ecommerce). Company figures put revenue at about US$220 million in 2015 from a start of about US$15,000 (reported figures vary).

Question for the room: would you trust a celebrity's own brand more or less than one they are paid to post about?

Sources: Jang; Express Tribune and Daily Pakistan (Pakistani celebrity labels); Practical Ecommerce citing Bloomberg; YourStory (2016).""",
  "Sources: Jang; Practical Ecommerce citing Bloomberg; YourStory (2016) &middot; DW figures company-reported")

S["content"] = sec("content", "#ffffff", "Content marketing", "Be found without paying every time",
  grid([
    ("Teach", "How-to and routines", "&ldquo;Five-minute skincare routine&rdquo; answers a question people already have.", "#ed0000"),
    ("Show", "Reviews and real customers", "Customers' photos and videos sell better than the brand's own.", "#eb6834"),
    ("Rank", "Pages that search finds", "A good guide keeps bringing visitors for years, for free.", "#2a78d6"),
    ("Gather", "A community", "Followers who comment, ask and share &mdash; an owned audience.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "Ads rent attention for a day; <b>content builds it for years</b> &mdash; slowly. What could your brand teach?", size=30),
  """One card per click.

Content marketing creates something useful or entertaining that brings people to the brand: tutorials, routines, reviews, recipes, guides. It costs time and production, not a price per click, and its reach compounds: a video or article keeps working long after it is published.

User-generated content (customers' own photos and videos) is the cheapest and most trusted content of all; many brands reuse it in ads.

The catch: content is slow to pay back and hard to attribute to sales.""")

S["case-content"] = cases("case-content", "Cases &middot; Content", "An audience first, products next",
  ("Pakistan", "Food Fusion", "Karachi, 2016", [
    ("The content", "Short recipe videos; more than five million YouTube subscribers, and the first Pakistani food channel past a billion views."),
    ("The business", "Brands such as Dalda and Olper's pay to appear in its recipes &mdash; buying a trusted audience.")]),
  ("Global", "Glossier", "New York, 2014", [
    ("The content", "Grew out of Into The Gloss (2010), a blog of people's beauty routines; readers shaped the first products."),
    ("The result", "Launched with four products in 2014; valued at US$1.8bn in 2021.")]),
  "Both built <b>an audience before</b> selling to it &mdash; one rents it to other brands, the other sold it its own products.",
  """Two content cases.

Food Fusion: a Pakistani recipe channel founded by Asad Memon and Saima Asad, launched on YouTube in May 2016. ProPakistani (July 2026) reports more than five million subscribers and that it was the first Pakistani food channel to cross one billion views. Brands including Dalda, Olper's and Dawlance have sponsored its videos (Sponsorradar), buying a place inside content its audience already trusts.

Glossier: Emily Weiss started the beauty blog Into The Gloss in 2010, profiling people's routines. Glossier launched in October 2014 with four products, shaped by readers' comments and requests. In July 2021 it raised a Series E at a valuation of US$1.8 billion (it has since faced harder years).

The lesson: content builds an owned audience. A brand can sell its own products to it, or other brands will pay to reach it.

Question for the room: which creator or channel has made you buy something you saw them use?

Sources: ProPakistani (July 2026); APP (2022); Sponsorradar; Global Venturing and Wikipedia (Glossier).""",
  "Sources: ProPakistani (2026); Sponsorradar; Global Venturing (2021)")

S["brand"] = sec("brand", "#f5f5f6", "Brand against performance", "This month's orders, or next year's?",
  two(1, 128, 280, 819, 380, "Performance marketing", "Buys orders now",
      ["Ads aimed at people ready to act", "Measured click by click, this month", "Stops working the day the budget stops", "Gets dearer as you chase more buyers"], "#ed0000")
  + "\n" + two(2, 973, 280, 819, 380, "Brand-building", "Buys memory",
      ["Advertising that makes the name known and liked", "Pays back slowly; hard to measure", "Fades if you stop, but lasts for months", "Makes every later ad and search cheaper"], "#2a78d6")
  + "\n" + band(3, 690, 180, "Performance harvests the demand that brand creates. <b>Spend only on performance, and the people who already know you run out.</b> Which does your brand need more of now?", size=29),
  """Two clicks, then the band.

Performance marketing targets people close to buying and is measured by immediate results. Brand-building makes the brand known, trusted and preferred, so that more people search for it, click its ads and choose it over a rival &mdash; its effect is spread over months and is hard to attribute.

Marketing research (for example Les Binet and Peter Field's work for the IPA) argues that strong brands balance both. The exact split depends on the category and the stage of the business; do not quote a universal ratio as fact.

A young brand often starts heavy on performance to prove demand and get cash in, then adds brand as it grows. A brand that stops brand-building usually sees nothing for a while &mdash; then a slow fall in organic traffic and search for its name.""")

S["case-brand"] = cases("case-brand", "Cases &middot; Brand-building", "When people already know the name",
  ("Pakistan", "Surf Excel", "Unilever Pakistan, since 1948", [
    ("The brand", "Launched as Surf in 1948; its line &lsquo;Daag tou achay hotay hain&rsquo; (dirt is good) is known across the country."),
    ("The method", "Decades of advertising built on one idea &mdash; stains are good &mdash; from children's play to festive campaigns.")]),
  ("Global", "Airbnb", "2020&ndash;2021", [
    ("The shift", "Cut performance marketing sharply and moved spend to brand advertising."),
    ("The result", "Q1 2021: marketing down 45%; about 90% of traffic direct or unpaid; traffic near 2019 levels.")]),
  "A known brand gets <b>customers it does not pay for click by click</b> &mdash; built over years, not months.",
  """Two brand cases. Surf Excel is home care: the simulation's own category.

Surf Excel: Unilever Pakistan says the brand was launched as Surf in Pakistan in 1948 and is known for the line 'Daag tou achay hotay hain' (dirt is good). Its advertising has long been about children's play, stains as a sign of doing good, and festive campaigns about helping others (such as #MadadEkIbadat, 2016), rather than the product's formula. That builds memory and preference that make every later promotion work harder.

Airbnb: in 2020 the company cut performance marketing and shifted spend to brand marketing (its IPO filing set out the strategy; direct and unpaid channels were 77% of traffic in 2019). In Q1 2021 total marketing spend fell 45%, driven by lower performance marketing; Brian Chesky said about 90% of traffic was direct or unpaid and traffic was near 2019 levels (Marketing Week, Campaign Asia). Airbnb also warned it might not keep driving traffic so cheaply.

The lesson: brand-building is how a company stops paying for every visitor. It takes years, and a famous brand can do what a young one cannot yet.

Question for the room: which home-care brand could you name without seeing an ad this week?

Sources: Unilever Pakistan (brand page); afaqs and Social Samosa; Airbnb Form S-1 (2020); Marketing Week and Campaign Asia (2021).""",
  "Sources: Unilever Pakistan; Airbnb S-1 (2020); Marketing Week, Campaign Asia (2021)")

worth = [("Social ads", "Rs 900", "1 in 3", "Rs 900 &middot; 3 orders", "Rs 2,700"),
         ("Search ads", "Rs 1,400", "1 in 4", "Rs 900 &middot; 2 orders", "Rs 1,800"),
         ("Short-video ads", "Rs 600", "1 in 8", "Rs 900 &middot; 1.3 orders", "Rs 1,170"),
         ("A 30% discount", "Rs 400", "1 in 12", "Rs 300 &middot; 1.1 orders", "Rs 330")]
S["worth"] = sec("worth", "#ffffff", "What a customer is worth", "The cheapest customer is not the best one",
  trows(["Channel (illustrative)", "Cost to win (CAC)", "Still buying in 6 months", "Margin per order", "Margin in a year"], worth, 276,
        [380, 300, 330, 360, 238], rh=78, size=27)
  + "\n" + band(5, 640, 230, "Compare what a customer <b>costs</b> with what they <b>earn you over time</b> (lifetime value, LTV). Here the cheapest click is not the best customer, and the discount loses money on every buyer. <b>Which channel does your report say your customers stay from?</b>", size=28),
  """Illustrative numbers, not market data. One row per click.

Lifetime value (LTV) is the margin a customer brings over their life with the brand: orders &times; margin per order. The rule of thumb many investors quote is LTV at least three times CAC; it is a rule of thumb, not a law.

Read the rows: the cheapest acquisition (a deep discount) brings buyers who came for the price, earn little on their order and rarely return. The dearest click (search) brings intent, but not necessarily loyalty. The lesson is to judge a channel on what its customers are worth over time, not on its cost per click &mdash; which needs cohort data: where did each customer come from, and did they come back?""",
  footer="Illustrative numbers")

S["plan"] = sec("plan", "#f5f5f6", "The customer acquisition plan", "A customer acquisition plan on one page",
  grid([
    ("Who", "One customer, described", "Who they are, what they want, where they spend time.", "#ed0000"),
    ("Where", "Two or three channels", "Chosen for that customer and that step of the funnel.", "#eb6834"),
    ("What", "One message, many creatives", "The promise, shown many ways, tested.", "#2a78d6"),
    ("How much", "A budget and a ceiling", "Split by channel; the most you will pay for a customer.", "#1baf7a"),
    ("How you know", "Measures for each step", "CTR, CVR, CAC, and whether buyers come back.", "#8a6414"),
    ("What next", "Test, keep, cut", "Move money every month to what wins.", "#6b4fbb"),
  ], 3, 290, 250)
  + "\n" + band(7, 830, 80, "A plan is a set of bets with a way to tell which ones paid.", size=28, extra="padding:18px 40px;"),
  """One box per click. This is the deliverable named in the course outline.

Who: a specific customer, not 'everyone'. Where: the channels that reach them, matched to the funnel. What: the promise and the creative. How much: the monthly budget by channel, and a CAC ceiling worked back from the customer's value (the previous slide). How you know: one measure per step. What next: a rule for moving budget &mdash; for example, cut any campaign whose CAC is above the ceiling for two months.""")

S["ex2"] = exercise("ex2", "Exercise 2", "Spend Rs 1 million a month",
  "A new Pakistani skincare brand: a hero face wash at Rs 1,200, an Instagram page and a website.",
  ["Who exactly are you trying to reach first?", "Which two channels get most of the money &mdash; and why?",
   "What is the most you would pay for one customer?", "What would make you move money between channels?"],
  "Exercise 2 &middot; a customer acquisition plan",
  """Ten minutes in teams. One question per click. The brand is hypothetical.

Push question 3: the answer should come from the product's margin and how often customers rebuy, not a guess. At Rs 1,200 and, say, a 50% margin before marketing, one order earns about Rs 600; if a customer buys three times a year, a CAC of Rs 1,000 can pay.

Question 4 is the test-and-learn rule. Take two teams' plans and compare where they put the money.""", top=500, h=180, cols=2)

S["part2"] = div("part2", "Part 2 &middot; The simulation", "The marketing budget<br>becomes yours",
  "Seven decisions open for month 6: Meta, Google, TikTok, campaign setup, affiliates, creative and brand-building.",
  """Part 2 is the simulation. Month 5 has run. For five months every team has been paying a default marketing budget it did not choose; from month 6 it is theirs.

Every number in Part 2 is the simulation's assumption or a test run of it, not market data.""")

S["category"] = sec("category", "#f5f5f6", "The category online", "How personal care finds customers in Pakistan",
  grid([
    ("Video", "YouTube reaches most online Pakistanis", "73% of online Pakistanis used it monthly (Kantar for Google, 2018).", "#ed0000"),
    ("Search", "Searches spike before sales", "Daraz saw Black Friday searches triple in 2017.", "#eb6834"),
    ("Creators", "Brands buy into trusted content", "Dalda and Olper's sponsor Food Fusion's recipes.", "#2a78d6"),
    ("Celebrity labels", "Stars launch beauty brands", "Skin Recipe, Ayesha O Beauty, Ooh Lala.", "#1baf7a"),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "The simulation's teams sell personal care and home care online in Pakistan. <b>Which of these has your team been paying for without choosing?</b>", size=30),
  """The real category first. One card per click.

Video: Think with Google's Pakistan insights cite a 2018 Kantar TNS study that YouTube reached 73% of online Pakistanis each month &mdash; an old figure; treat as indicative.

Search: Daraz's 2017 Black Friday searches tripled year on year (Think with Google).

Creators: Food Fusion's sponsors include Dalda and Olper's (Sponsorradar).

Celebrity labels: Skin Recipe (Aiman and Minal Khan), Ayesha O Beauty (2021), Ooh Lala (Shahid Afridi, 2021).

Sources: Think with Google APAC; Sponsorradar; Jang; Express Tribune; Daily Pakistan.""",
  footer="Sources: Think with Google (Kantar 2018; Daraz 2017); Sponsorradar; Jang")

S["sim-market"] = sec("sim-market", "#ffffff", "In the simulation", "How marketing works in the simulation",
  grid([
    ("Channels", "Three ad budgets, three kinds of buyer", "Google buyers convert best but cost most per visit; TikTok is cheapest and converts least; Meta sits between.", "#ed0000"),
    ("Who stays", "Each channel's customers churn differently", "Lost each month: organic 3.7%, Meta 6.3%, Google 14%, TikTok 26%. A discount over 25% makes buyers deal-driven: 44%.", "#eb6834"),
    ("Creative &amp; brand", "Spend that raises every rupee", "Creative lifts how well ads work and fades 15% a month. Brand builds organic traffic and fades 8% a month.", "#2a78d6"),
    ("Campaigns", "Aim each budget", "3.10 splits each ad budget into up to three campaigns by product, age, city, interests and format. The report shows CTR, CPC, CVR, ROAS and CAC for each.", "#1baf7a"),
  ], 4, 290, 440, bsize=23)
  + "\n" + band(5, 770, 110, "<b>The default you have paid since month 1:</b> Meta 468k, Google 234k, TikTok 168k, creative 200k, brand 267k &mdash; Rs 1.34m a month.", size=28),
  """One rule per click. The rules are the simulation's.

Channels: each paid channel has its own cost per thousand views and its own buyer intent: Google search converts at 1.8 times Meta's rate, TikTok at 0.6 times. Spend has diminishing returns: each extra rupee in a channel buys a little less.

Who stays: the simulation remembers which channel brought each group of customers (cohorts) and gives each its own monthly churn. These rates are the simulation's assumptions.

Creative and brand: creative quality rises with spend and fades about 15% a month; brand equity rises with brand spend and fades about 8% a month, and drives organic and direct visits.

Campaigns (3.10): each budget can be split into up to three campaigns aimed by product, age, gender, city tier, interests, language and format, with results per campaign in the report.

Affiliate and influencer commission (3.6): partners bring their own visitors, more the higher the rate; some would have come anyway; their customers churn about 20% a month; commission is paid only on the sales they track.

Real founders estimate such numbers from their own campaigns and tests; these are the simulation's assumptions.""",
  footer="Decision rules from the simulation &middot; not market data")

tests7 = [("All default", "3,798", "544", "34,571", "5.54m"),
          ("Meta +50% &nbsp;(702k)", "3,986", "592", "35,675", "4.63m &nbsp;(&minus;0.90m)"),
          ("Google budget moved to TikTok", "4,170", "475", "36,293", "6.69m &nbsp;(+1.15m)"),
          ("Brand-building stopped", "3,793", "441", "33,988", "6.98m &nbsp;(+1.44m)"),
          ("Brand-building doubled", "3,804", "647", "35,170", "4.11m &nbsp;(&minus;1.43m)"),
          ("30% off everything", "5,588", "321", "32,881", "&minus;14.84m")]
S["sim-tests"] = sec("sim-tests", "#f5f5f6", "In the simulation", "What one change did, month 6 to month 12",
  trows(["Test, kept from month 6", "Orders, month 6", "CAC, month 6", "Active, month 12", "Contribution, 6&ndash;12"], tests7, 276,
        [520, 270, 250, 290, 278], rh=72, size=26)
  + "\n" + band(7, 786, 100, "Brand stopped: organic visits <b>27,245 &rarr; 20,936</b> by month 12. <b>Which line is your team's plan?</b>", size=29),
  """One test per click. Each line is one team changing one decision from month 6 and keeping it, against an identical team on every default, in the same simulated world (six teams, five default months first). Contribution is after marketing, months 6 to 12.

Meta +50%: more orders and customers, but each extra buyer cost more (diminishing returns) &mdash; contribution down 0.9m.

Google moved to TikTok: the cheapest reach won more customers and more contribution by month 12 in this test, even though TikTok buyers churn fastest; its repeat share was lower (33.3% against 36.0%).

Brand stopped: the saving shows at once, and contribution rose 1.44m within the game; but organic visits fell from 27,245 to 20,936 a month by month 12, and kept falling &mdash; a cost that lands mostly after month 12. Brand doubled cost 1.43m for 6,550 more organic visits a month.

30% off everything: 47% more orders in month 6, then a collapse: deal-driven buyers left, repeat share fell to 16%, NPS to 58, and contribution to minus 14.8m.

Results depend on each team's prices, rating and stock; these are directions, not forecasts.""",
  footer="Simulation test run, six teams, months 6&ndash;12, all else default &middot; not market data")

S["checks"] = sec("checks", "#fdeceb", "Before month 6 runs", "Four questions before you spend",
  grid([
    ("Customer", "Who are you paying to reach?", "Aim campaigns (3.10) at the segments your range was built for.", "#ed0000"),
    ("Ceiling", "What can a customer cost?", "Work it back from your margin and how often buyers return.", "#eb6834"),
    ("Mix", "Which channels, and why?", "Cheap clicks or customers who stay? Check your report's churn by channel.", "#2a78d6"),
    ("Brand", "What happens after month 12?", "Brand and creative work slowly. Cutting them shows profit now, decline later.", "#1baf7a"),
  ], 4, 300, 340)
  + "\n" + band(5, 700, 150, "Name in the board memo the number in month 6's report that will tell you <b>whether your marketing paid</b>.", size=30),
  """One question per click, while teams fill in the decision form.

Logistics for the notes, not the slide: decisions for month 6 close at [deadline]. Open this round: 3.1 Meta, 3.2 Google, 3.4 TikTok, 3.10 campaign setup, 3.6 affiliate and influencer commission, 3.8 creative, 3.9 brand-building, plus everything opened earlier. The month-6 report shows each campaign's CTR, CPC, CVR, ROAS and CAC, and new customers by channel.""")

S["next"] = sec("next", "#131316", "Next session", "How will you get customers to come back?",
  grid([
    ("Session 8", "Retention opens", "CRM, the service team and the returns policy.", "#ff3b3b"),
    ("Your customers", "Who came back?", "Every cohort you bought now has a repeat rate.", "#ff3b3b"),
    ("Your numbers", "Did your marketing pay?", "Month 6's CAC by channel is the test.", "#ff3b3b"),
  ], 3, 300, 300, bg="#1f1f24", border="border:1px solid #33333b;", tcol="#ffffff", bcol="#c9c9d1")
  + "\n" + band(4, 660, 150, "Today: how to bring customers, and what each costs. Next time: <b>how to keep them, so you do not pay for them twice</b>.", bg="#ed0000", size=31),
  """Close. One card per click.

Session 8 opens retention: 6.1 CRM and retention, 10.1 customer service team, 10.4 returns policy. The customers bought in month 6 are the ones Session 8 tries to keep.""", dark=True, eyecol="#ff3b3b")

ORDER = ["cover", "recall", "ex1", "part1", "funnel", "poe", "social", "search", "metrics", "case-perf",
         "creators", "case-influence", "content", "case-content", "brand", "case-brand", "worth", "plan", "ex2",
         "part2", "category", "sim-market", "sim-tests", "checks", "next"]
if __name__ == "__main__":
    write(S, ORDER, "Session 7 — How Will You Get Customers?", {
        "open": {"description": "How will you get customers, and how the last brand found you", "start": "cover"},
        "channels": {"description": "Part 1 · The funnel, paid social, search and the numbers of a campaign", "start": "part1"},
        "creators": {"description": "Influencers and content, with cases", "start": "creators"},
        "brand": {"description": "Brand against performance, customer value and the acquisition plan", "start": "brand"},
        "sim": {"description": "Part 2 · Marketing in the simulation", "start": "part2"}})
