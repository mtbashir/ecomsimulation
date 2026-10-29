"""Session 11, Part 2 - the toolkit: Shopify, Meta ads in the Andromeda era, and
Google Search. About 35 slides, in sections so it can be taught as a session of
its own.

Not run on its own: s11_slides.py executes it with its helpers (sec, div, grid,
band, two, trows, cases, exercise) and splices TOOLKIT_ORDER in after Part 1.
Platform facts were checked in October 2026; Shopify, Meta and Google change
their products every few months, so check them again before teaching.
"""
FT2 = "Session 11 &middot; The toolkit: store, ads and search"


def tsec(sid, bg, eyebrow, title, body, notes, footer=FT2, **kw):
    return sec(sid, bg, eyebrow, title, body, notes, footer=footer, **kw)


def tdiv(sid, part, title, line, notes):
    return div(sid, part, title, line, notes).replace(FT, FT2)


RED, ORANGE, BLUE, GREEN, BROWN, GREY = "#ed0000", "#eb6834", "#2a78d6", "#1baf7a", "#8a6414", "#55555f"

S["s11-tk-part"] = tdiv("s11-tk-part", "Part 2 &middot; The toolkit", "Store, ads<br>and search",
  "Advanced moves on Shopify, on Meta&rsquo;s Andromeda-era ads and on Google Search &mdash; each with a Pakistani and a global case.",
  """Part 2 is real-world practice, not the simulation: three toolkits of about ten slides each, then an exercise and one slide that maps the toolkit onto the simulation's decisions.

It can be taught as a session of its own. Parts 1 and 3 (AI tools, and the simulation's AI builds) make one session; Part 2 makes another, about 90 minutes: Shopify 30, Meta 30, Google 25, exercise 10.

Every platform here changes its products every few months. The facts were checked in October 2026; check the dated ones (feature names, availability in Pakistan) again before teaching.""")

# --- Toolkit 1 - Shopify --------------------------------------------------------------

S["s11-shop"] = tdiv("s11-shop", "Toolkit 1 &middot; Shopify", "The store<br>that sells",
  "Speed, product data, on-site search, bigger baskets, cash on delivery under control, and the AI inside Shopify.",
  """Most Pakistani direct-to-consumer brands that run their own store run it on Shopify. These are the moves that separate a store that sells from a catalogue with a checkout.""")

S["s11-shop-system"] = tsec("s11-shop-system", "#ffffff", "Shopify", "A Shopify store is four systems",
  grid([
    ("Theme", "What shoppers see", "Sections and blocks you rearrange without code, on every page.", RED),
    ("Data", "What the store knows", "Products, variants and metafields: the facts filters, Google and AI agents read.", ORANGE),
    ("Apps", "What you bolt on", "Reviews, bundles, WhatsApp, couriers &mdash; each one can add code to every page.", BLUE),
    ("Checkout", "How you get paid", "No Shopify Payments in Pakistan: local gateways and cash on delivery.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "Slow pages, poor search and refused parcels usually share one cause: <b>nobody owns all four</b>. Who owns them in your team?", size=30),
  """One system per click.

Shopify Payments is not available to Pakistan-based merchants. Stores use gateways on Shopify's Pakistan list (Safepay, UnumPay and XPay are the ones most often named by merchants) and add cash on delivery as a manual payment method. Check the gateway's current terms before launch.

Sources: Shopify Community threads on payments in Pakistan (2024&ndash;2026); Shopify app listings.""")

S["s11-shop-speed"] = tsec("s11-shop-speed", "#f5f5f6", "Shopify &middot; speed", "Every app is a tax on speed",
  grid([
    ("Measure", "Core Web Vitals", "Loads in 2.5s or less, answers a tap in 200ms or less, no layout jumps (CLS 0.1).", RED),
    ("Images", "Right size, modern format", "Upload once at full size; Shopify&rsquo;s CDN resizes it. Lazy-load below the first screen.", ORANGE),
    ("Apps", "Remove what you do not use", "Some apps leave code in the theme after removal: check the theme when one goes.", BLUE),
    ("First screen", "Light above the fold", "Auto-playing video, sliders and pop-ups cost the first screen most.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "Has anyone in your team opened the store <b>on a mid-range phone, on mobile data</b>, this month?", size=30),
  """One rule per click.

The thresholds are Google's: Largest Contentful Paint 2.5 seconds or less, Interaction to Next Paint 200 milliseconds or less, Cumulative Layout Shift 0.1 or less, each judged at the 75th percentile of real visits. Search Console and PageSpeed Insights report them for any store.

Apps built on theme app extensions are removed cleanly; older apps that edited the theme can leave scripts behind.

Source: web.dev, How the Core Web Vitals thresholds were defined.""")

S["s11-shop-data"] = tsec("s11-shop-data", "#ffffff", "Shopify &middot; product data", "Product data does the selling",
  grid([
    ("Metafields", "Facts as fields", "Skin type, concern, key ingredient, size &mdash; stored as fields, not buried in a paragraph.", RED),
    ("Filters", "Shoppers narrow down", "The free Search &amp; Discovery app turns those fields into filters: oily skin, under PKR 1,500.", ORANGE),
    ("Pages", "Blocks that read the fields", "The theme shows ingredients and how to use from the same fields on every product.", BLUE),
    ("Machines", "Google and AI agents", "Structured data and product feeds are built from the same fields.", GREEN),
  ], 4, 290, 400, bsize=24)
  + "\n" + band(5, 740, 130, "Type a fact once, use it everywhere. <b>Which three facts does your shopper ask before buying?</b>", size=30),
  """One idea per click.

Metafields (and metaobjects for richer content such as an ingredient glossary) are Shopify's way to store structured facts about a product. Search &amp; Discovery, Shopify's free app, can build filters from product and variant metafields; Online Store 2.0 themes can show metafields in blocks; feeds to Google and to AI shopping agents read the same data.

The test: could a shopper filter your range by the question they ask most on WhatsApp?""")

S["s11-shop-search"] = tsec("s11-shop-search", "#f5f5f6", "Shopify &middot; on-site search", "Search that finds",
  grid([
    ("Synonyms", "Say it their way", "Group &lsquo;face wash&rsquo;, &lsquo;cleanser&rsquo; and Roman Urdu spellings so each finds the same products.", RED),
    ("Boosts", "Lead with the best", "Pin chosen products to the top for a search term.", ORANGE),
    ("No results", "Read the misses", "The app reports searches that found nothing: a missing product, or a missing word.", BLUE),
    ("Recommendations", "Related and complementary", "Set what goes with what by hand: cleanser, then toner, then moisturiser.", GREEN),
  ], 4, 290, 400, bsize=24)
  + "\n" + band(5, 740, 130, "A search that finds nothing is <b>a lost order you can see</b>. When did your team last read the list?", size=30),
  """One feature per click. All four are in Search &amp; Discovery, Shopify's free app: synonym groups, product boosts, related and complementary product recommendations (which override Shopify's automatic choice), and a search report with top searches and searches with no results.

Roman Urdu is where Pakistani stores lose searches: shoppers type a product the way they say it, and a store that only knows the label's English finds nothing.

Sources: Shopify Search &amp; Discovery app; third-party setup guides (2025&ndash;2026).""")

S["s11-shop-basket"] = tsec("s11-shop-basket", "#ffffff", "Shopify &middot; basket", "Bigger baskets, by design",
  grid([
    ("Bundles", "Routines and multipacks", "Shopify&rsquo;s free Bundles app sells a routine or a three-pack as one product.", RED),
    ("Threshold", "A free-delivery bar", "Show how far the cart is from free delivery; set the bar just above a typical basket.", ORANGE),
    ("Cart", "One add-on, not ten", "Suggest one complementary item in the cart, priced below the main product.", BLUE),
    ("Thank-you page", "The next order", "A code for the next purchase on the order confirmation page and message.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "Delivery is paid per parcel, so an item added to the same parcel <b>costs nothing more to deliver</b>. Which item would you add?", size=30),
  """One lever per click; the theory is Session 5's, these are the Shopify settings.

Shopify Bundles is Shopify's own free app for fixed bundles and multipacks; volume and tiered discounts are set as automatic discounts or through discount apps built on Shopify Functions. A free-delivery progress bar is a theme setting or a small app.

Post-purchase upsell pages work only with some payment gateways; with cash on delivery, the thank-you page and the confirmation message are where the next order is won.""")

S["s11-shop-cod"] = tsec("s11-shop-cod", "#f5f5f6", "Shopify &middot; cash on delivery", "Cash on delivery, under control",
  grid([
    ("Payment rules", "Offer COD where it pays", "Apps built on Shopify Functions hide or rename COD by cart value, city or product.", RED),
    ("Flow", "Tag the risky orders", "Shopify Flow (every plan) tags first-time, high-value COD orders for a confirmation.", ORANGE),
    ("Confirm", "WhatsApp before dispatch", "A message with the order and the delivery window; unconfirmed orders wait.", BLUE),
    ("Prepay", "Make paying online worth it", "A small prepaid discount or free delivery for card and wallet payments.", GREEN),
  ], 4, 290, 400, bsize=24)
  + "\n" + band(5, 740, 130, "Every refused parcel is paid for twice. <b>The cheapest refusal is the order confirmed before it left.</b>", size=30),
  """One control per click.

Shopify Scripts stopped running on 30 June 2026; checkout logic now runs on Shopify Functions, and the payment-customisation apps in Shopify's App Store use them to hide, rename or reorder payment methods by conditions such as cart total, products or address.

Shopify Flow is available on the Basic, Shopify, Advanced and Plus plans (Shopify Help Center); tagging orders and sending them to a confirmation queue is its most common use.

Caution for the room: blocking COD for a whole city turns away good customers too. Rules by order value and by a customer's own refusal history are fairer than rules by place.""")

S["s11-shop-ai"] = tsec("s11-shop-ai", "#ffffff", "Shopify &middot; AI", "The AI inside Shopify",
  grid([
    ("Sidekick", "An assistant in the admin", "Builds reports and Flow automations from a plain request, and suggests next actions.", RED),
    ("Magic", "Copy and images", "Drafts product descriptions, emails and image edits &mdash; a first draft, not the final word.", ORANGE),
    ("Rollouts", "Native A/B tests", "Two versions of the store, shown to real visitors, compared in the admin (where enabled).", BLUE),
    ("Agents", "Selling inside AI chats", "Eligible stores&rsquo; products appear in ChatGPT, Copilot and Google&rsquo;s AI Mode.", GREEN),
  ], 4, 290, 400, bsize=24)
  + "\n" + band(5, 740, 130, "The AI costs little or nothing. <b>Your product data and your judgement are what make it useful.</b>", size=30),
  """One tool per click. Availability differs by plan and by country; check each in your own admin.

Sidekick: builds ShopifyQL reports and Shopify Flow workflows from plain-language requests; some sources say generating custom admin apps needs a higher plan. Shopify Magic: AI writing and image tools. Rollouts: native A/B testing announced in the Winter '26 Edition (December 2025); some stores are still in early access.

Agentic storefronts: Shopify Catalog sends eligible products to ChatGPT, Microsoft Copilot, Google AI Mode and Perplexity; Shopify turned this on by default for eligible US merchants in March 2026. The Universal Commerce Protocol (Shopify and Google, January 2026) is the standard behind it. Whether Pakistan-based stores are eligible was not confirmed in October 2026.

Sources: Shopify blog, How agentic commerce works (2026); Shopify Editions coverage (December 2025, June 2026).""")

S["s11-shop-markets"] = tsec("s11-shop-markets", "#f5f5f6", "Shopify &middot; abroad", "Selling to Pakistanis abroad",
  grid([
    ("Markets", "One store, many countries", "Shopify Markets sets prices, currency and language for each country.", RED),
    ("Payments", "Cards from abroad", "International cards need a gateway that settles to Pakistan &mdash; check before launch.", ORANGE),
    ("Shipping", "Duties and returns", "Show prices with duties included; a return from the UK can cost more than the product.", BLUE),
    ("Ads", "Where Shopping ads run", "Google Shopping and Meta catalogue ads can target the UK, UAE and US.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "The diaspora already knows Pakistani brands. <b>Which one product would you send first &mdash; and to which city?</b>", size=30),
  """One step per click; Session 12 covers new markets as a growth route.

Shopify Markets manages country-specific pricing, currency, language and domains from one store. The hard parts for a Pakistan-based store are payments (a gateway that accepts international cards and settles in Pakistan) and returns, which are often cheaper to refund than to ship back.""")

shop_audit = [("Mobile speed", "Loads in 2.5s or less on a mid-range phone"),
              ("Apps", "Each earns its place; the theme is cleaned after removals"),
              ("Product facts", "Stored in metafields and offered as filters"),
              ("Search", "No-result searches read every week; Roman Urdu synonyms"),
              ("Bundles", "A routine or multipack beside every best-seller"),
              ("Delivery bar", "Set just above the typical basket"),
              ("COD rules", "Risky orders confirmed before dispatch"),
              ("Paying online", "A reason to prepay, shown at checkout"),
              ("Tracking", "Purchases reach Meta and Google from the server, not only the browser"),
              ("Testing", "One change at a time, measured against the last")]
S["s11-shop-audit"] = tsec("s11-shop-audit", "#ffffff", "Shopify &middot; audit", "A Shopify audit in ten checks",
  trows(["Check", "Good looks like"], shop_audit, 262, [420, 1188], rh=58, size=24),
  """One check per click. A handout-style summary of the Shopify toolkit; the question for the room is which three a brand they know fails.

Tracking: Meta's Conversions API and Google's enhanced conversions (next two toolkits) send purchases from the server, so they are not lost to browsers that block tracking.""")

S["s11-shop-case"] = cases("s11-shop-case", "Cases &middot; Shopify", "Same platform, different doorstep",
  ("Pakistan", "Shopify in Pakistan", "2026", [
    ("The stores", "StoreLeads counted 11,788 live Shopify stores in Lahore alone (March 2026)."),
    ("The catch", "No Shopify Payments: local gateways such as Safepay, UnumPay and XPay, and cash on delivery."),
    ("What it means", "The tools are the world&rsquo;s; the payments and the doorstep are Pakistan&rsquo;s.")]),
  ("Global", "Dermalogica", "Skincare, United States", [
    ("The move", "Moved its direct store from Salesforce Commerce Cloud to Shopify."),
    ("One month later", "Sales up 119%, conversion up 45%, average order up 12%, site 44% faster, Shopify reported.")]),
  "A faster, simpler store sells more of the same products. <b>Fix the store before you buy more traffic.</b>",
  """Two Shopify cases.

Shopify in Pakistan: StoreLeads' Punjab report (March 2026) counted 24,068 live Shopify stores in Punjab, 11,788 of them in Lahore; StoreCensus estimated about 25,500 active Shopify stores in Pakistan in September 2026 (different providers count differently). Shopify Payments is not available to Pakistan-based merchants, who use local gateways and cash on delivery.

Dermalogica: Shopify's case study reports that one month after replatforming its direct-to-consumer store from Salesforce Commerce Cloud, Dermalogica saw a 119% uplift in sales, a 45% higher conversion rate, a 12% higher average order value, a 44% faster site and a 14% lower bounce rate. Vendor-reported; the lesson is the direction, not the size.

Sources: StoreLeads (Mar 2026); StoreCensus (Sep 2026); Shopify Community; Shopify case study, Dermalogica.""",
  "Sources: StoreLeads (Mar 2026); Shopify Community; Shopify case study, Dermalogica")

# --- Toolkit 2 - Meta ads in the Andromeda era ---------------------------------------

S["s11-meta"] = tdiv("s11-meta", "Toolkit 2 &middot; Meta ads", "Ads in the<br>Andromeda era",
  "How Meta now chooses which ad each person sees, and what that changes about creative, account structure and the signals you send back.",
  """Andromeda is the name of Meta's ad retrieval system, launched in late 2024; practitioners use it as shorthand for the whole shift to AI-led delivery. The block explains the machine first, then the moves.""")

S["s11-meta-how"] = tsec("s11-meta-how", "#ffffff", "Meta &middot; the machine", "How Meta picks the ad you see",
  grid([
    ("1 &middot; Retrieval", "Andromeda", "From tens of millions of ads, picks a few thousand that could suit this person.", RED),
    ("2 &middot; Ranking", "GEM and Lattice", "Larger models predict how likely each person is to act on each candidate.", ORANGE),
    ("3 &middot; Auction", "Bid &times; predicted action", "The ad with the best value for the person and the advertiser wins the slot.", BLUE),
  ], 3, 290, 340)
  + "\n" + band(4, 680, 190, "Meta&rsquo;s advice since Andromeda: broad audiences and <b>meaningfully different creative</b>. The ads now do much of the targeting.", size=31),
  """One stage per click.

Andromeda (Meta Engineering, 2 December 2024): retrieval is the first stage of Meta's ads system, selecting from tens of millions of ad candidates a few thousand relevant ones; Meta reported a 10,000-fold increase in model capacity, +6% recall and +8% ads quality on selected segments, on NVIDIA Grace Hopper and Meta's own MTIA chips.

GEM, the Generative Ads Recommendation Model (Meta Engineering, November 2025), is a foundation ranking model that teaches smaller models; Meta reported +5% ad conversions on Instagram and +3% on Facebook Feed in Q2 2025. Lattice consolidates many ranking models into fewer, larger ones.

All of these figures are Meta's own.""",
  footer="Sources: Engineering at Meta (Dec 2024, Nov 2025); Meta Q2 2025 results")

S["s11-meta-shift"] = tsec("s11-meta-shift", "#f5f5f6", "Meta &middot; what changed", "From picking people to feeding the machine",
  two(1, 128, 280, 819, 330, "Before", "Find the audience",
      ["Many ad sets, narrow interests and lookalikes", "A few ads, tweaked endlessly", "Targeting did the work; creative filled the slot"], GREY)
  + "\n" + two(2, 973, 280, 819, 330, "Now", "Feed the system",
      ["Fewer campaigns, broad or Advantage+ audience", "Many meaningfully different ads", "Creative and true signals do the work"], RED)
  + "\n" + band(3, 660, 210, "The skill moved from <b>choosing who sees the ad</b> to <b>giving the system good ads and honest results</b>. Which of the two is your team better at?", size=31),
  """Two clicks, then the band.

Advantage+ shopping campaigns were renamed Advantage+ sales campaigns in 2025; sales campaigns now default to Advantage+ settings, with Advantage+ placements, and creating the legacy campaign type through Meta's API stopped in May 2026. Manual interest targeting still exists in some objectives but is treated as a suggestion more often than a fence.

Sources: Meta Ads Manager; third-party trackers of Meta changes (2025&ndash;2026).""")

S["s11-meta-diverse"] = tsec("s11-meta-diverse", "#ffffff", "Meta &middot; creative", "What counts as a different ad",
  two(1, 128, 280, 819, 400, "Different", "A new ad to the machine",
      ["A new reason to buy (concept)", "A different person speaking", "A different format: talking video, demo, carousel, static",
       "A different opening: first seconds, first line", "A different language: Urdu, Roman Urdu, English"], GREEN)
  + "\n" + two(2, 973, 280, 819, 400, "Not different", "The same ad, again",
      ["Same video, new headline", "Same image, new colour or button", "Same script, new music", "Resized copies of one picture"], RED)
  + "\n" + band(3, 710, 160, "Meta: creative must be <b>meaningfully different</b>. Near-copies reach the same people, then show as <b>Creative limited</b> or <b>Creative fatigue</b>.", size=29),
  """Two columns, then the band.

Meta's creative diversification guidance says creative that is too similar may not be recognised as different and can reach the same audiences, which limits reach; Ads Manager then shows Creative limited (cost per result above your past ads, but under double) or Creative fatigue (double or more).

Teach the principle, not the folklore: the "Entity ID" that groups similar ads and similarity thresholds such as "60%" come from agency write-ups, not from Meta, which has not published how it groups creative.

Sources: Meta Business Help Center, creative diversification and delivery statuses; Mockingbird, What creative diversification means (2026).""")

matrix = [("Problem", "A student with oily skin", "Selfie video", "&lsquo;Exams, heat and a shiny face by noon?&rsquo;"),
          ("Proof", "A salon owner", "Talking head", "&lsquo;What I tell clients about vitamin C&rsquo;"),
          ("Value", "A mother buying for the family", "Carousel", "&lsquo;Three products, one parcel, under PKR 3,000&rsquo;"),
          ("Ritual", "A working woman", "Demo reel", "&lsquo;My two-minute morning routine&rsquo;"),
          ("Trust", "A repeat customer", "Review montage", "&lsquo;Order number four &mdash; here is why&rsquo;")]
S["s11-meta-matrix"] = tsec("s11-meta-matrix", "#f5f5f6", "Working it out", "A creative matrix for a skincare brand",
  trows(["Angle", "Who speaks", "Format", "Opening line"], matrix, 276, [240, 460, 300, 608], rh=78, size=25)
  + "\n" + band(6, 740, 140, "Five concepts in two languages are <b>ten ads that are actually different</b>. Which row would you film first?", size=30),
  """Illustrative. One concept per click.

The matrix is the practical answer to Andromeda: plan concepts (a reason to buy, a person, a format, an opening), not variations of one ad. Each row can be made in Urdu, Roman Urdu or English; that is a different ad too.

Practitioners suggest adding new concepts every week or two and letting the system spend on the winners; that cadence is a rule of thumb, not Meta's.""",
  footer="Illustrative")

S["s11-meta-structure"] = tsec("s11-meta-structure", "#ffffff", "Meta &middot; structure", "Fewer, fuller campaigns",
  grid([
    ("Consolidate", "Fewer ad sets", "Each ad set needs enough results to learn; a budget split ten ways learns slowly.", RED),
    ("Learning", "About 50 a week", "Meta&rsquo;s guide: about 50 optimisation events in the 7 days after a big edit to leave learning.", ORANGE),
    ("Broad", "Let Advantage+ find buyers", "Advantage+ audience and placements; exclude existing customers where that matters.", BLUE),
    ("Patience", "Edit less", "Big budget jumps and new audiences or optimisation events restart learning.", GREEN),
  ], 4, 290, 400, bsize=24)
  + "\n" + band(5, 740, 130, "A brand with 30 orders a week cannot feed ten ad sets. <b>How many can your budget feed?</b>", size=30),
  """One rule per click.

Meta's Business Help Center: an ad set generally needs about 50 optimisation events within 7 days of its last significant edit to exit the learning phase; significant edits include large budget changes, targeting changes and a new optimisation event. Practitioners report that adding new ads no longer always restarts learning, but Meta's documentation still lists it.

For a small Pakistani brand the arithmetic is the point: if purchases are too few to reach 50 a week, optimise for an earlier event (add to cart, or a confirmed order you send yourself) or put the budget in fewer ad sets.""")

S["s11-meta-signals"] = tsec("s11-meta-signals", "#f5f5f6", "Meta &middot; signals", "Teach it who really buys",
  grid([
    ("Pixel + CAPI", "Both, not one", "The browser pixel misses visits; the Conversions API sends events from your server.", RED),
    ("Matching", "Who was it?", "Hashed phone and email with each event help Meta match it to a person.", ORANGE),
    ("COD truth", "Send what was delivered", "Send confirmed and delivered orders back, so it learns from buyers who accept the parcel.", BLUE),
    ("Value", "Not every order is equal", "Send the order&rsquo;s value &mdash; better still, what it earned you.", GREEN),
  ], 4, 290, 400, bsize=24)
  + "\n" + band(5, 740, 130, "With cash on delivery, a purchase event is a promise. <b>Optimise for promises and you buy more refusals.</b>", size=30),
  """One signal per click.

The Conversions API sends events from the store's server; Shopify's Facebook &amp; Instagram app sets it up. Event Match Quality in Events Manager shows how well events match people. Offline and CRM events (a confirmed or delivered order) are sent through the same Conversions API.

The cash-on-delivery move is a practitioner recommendation, not a Meta rule: a Purchase event fires when the order is placed, including orders that will be refused. A custom event for confirmed or delivered orders, used as the optimisation event once there are enough of them each week, teaches the system to find people who accept the parcel.""")

S["s11-meta-whatsapp"] = tsec("s11-meta-whatsapp", "#ffffff", "Meta &middot; WhatsApp", "WhatsApp in the funnel",
  grid([
    ("Click to WhatsApp", "Ads that open a chat", "For first orders and considered products: questions answered before the order.", RED),
    ("Marketing messages", "To people who opted in", "Offers and restocks sent from Ads Manager to customers who agreed to hear from you.", ORANGE),
    ("Confirmation", "Before dispatch", "The same chat confirms cash-on-delivery orders and cuts refusals.", BLUE),
  ], 3, 290, 340)
  + "\n" + band(4, 680, 190, "Shoppers already ask &lsquo;COD hai?&rsquo; in a chat. <b>Who in your team answers &mdash; and how fast?</b>", size=31),
  """One use per click.

Ads that click to WhatsApp open a conversation instead of a web page; WhatsApp marketing messages can now be bought inside Ads Manager alongside other placements, to people who have opted in. For Pakistani brands the chat is also where cash-on-delivery orders are confirmed.

The case on the next slide is a Pakistani brand using WhatsApp marketing messages inside its Advantage+ campaigns.""")

S["s11-meta-read"] = tsec("s11-meta-read", "#f5f5f6", "Meta &middot; reading results", "Reading results without fooling yourself",
  grid([
    ("Attribution", "7-day click, 1-day view", "Meta&rsquo;s default counts generously; set it beside delivered orders (Session 10).", RED),
    ("Fatigue", "Cost per result rising", "On the same ads: Creative limited, then Creative fatigue &mdash; time for new concepts.", ORANGE),
    ("Lift", "Test, do not assume", "A conversion lift or hold-out test says what the ads added, not what they touched.", BLUE),
    ("Cadence", "Refresh on a rhythm", "New concepts on a schedule, before fatigue &mdash; not panic edits every day.", GREEN),
  ], 4, 290, 400, bsize=24)
  + "\n" + band(5, 740, 130, "Judge Meta by <b>delivered orders and cash</b>, not by Ads Manager alone.", size=31),
  """One habit per click.

Meta's default attribution counts a purchase within 7 days of a click or 1 day of a view (Session 10). Conversion Lift studies and geographic hold-outs measure incrementality; small brands can run a simple version by pausing ads in one region for two weeks and comparing.""")

S["s11-meta-case"] = cases("s11-meta-case", "Cases &middot; Meta", "The machine, and the brands that feed it",
  ("Pakistan", "Alkaram Studio", "Fashion, November 2025", [
    ("The setup", "Its monthly Advantage+ website-conversion campaigns, with WhatsApp marketing messages added in Ads Manager."),
    ("The audience", "Adults 18&ndash;65 in Pakistan who had interacted with the brand and opted in."),
    ("The result", "Cost per link click improved 6%, Meta reported.")]),
  ("Global", "Meta", "Its own models, 2024&ndash;2025", [
    ("Retrieval", "Andromeda: +6% recall and +8% ads quality on selected segments (December 2024)."),
    ("Ranking", "GEM: +5% ad conversions on Instagram and +3% on Facebook Feed (Q2 2025).")]),
  "The machine gets better every quarter. <b>Your edge is the creative you feed it and the truth you send back.</b>",
  """Two cases: a Pakistani advertiser and the platform itself.

Alkaram Studio: Meta's WhatsApp Business success story describes the fashion brand adding WhatsApp marketing messages, from November 8 to 22, 2025, to the monthly website-conversion campaigns it runs with Advantage+ placements; the messages went to adults 18&ndash;65 in Pakistan who had interacted with the brand and opted in, and linked to product pages. Meta reports a 6% improvement in cost per link click. No baseline or spend is published.

Meta: Engineering at Meta reported Andromeda's gains (December 2024) and GEM's (November 2025; Q2 2025 earnings). These are the platform's own numbers and the reason for the creative-first advice.

Sources: WhatsApp Business, Alkaram Studio success story; Engineering at Meta (Dec 2024, Nov 2025).""",
  "Sources: WhatsApp Business, Alkaram Studio; Engineering at Meta (Dec 2024, Nov 2025)")

# --- Toolkit 3 - Google Search -----------------------------------------------------------

S["s11-google"] = tdiv("s11-google", "Toolkit 3 &middot; Google Search", "Being found<br>on Google",
  "Search engine optimisation, Google Ads and the new AI answers &mdash; what still works and what has changed.",
  """Google is where a shopper who already wants the product looks for it. The block covers the results page as it is now, organic search (SEO), Google Ads and Shopping, then two cases.""")

S["s11-google-page"] = tsec("s11-google-page", "#ffffff", "Google &middot; the results page", "What a results page is now",
  grid([
    ("Ads", "Paid, marked Sponsored", "Search ads at the top and bottom; Shopping ads where Google supports the country.", RED),
    ("AI answers", "AI Overviews and AI Mode", "A generated answer with links. AI Mode reached Pakistan in August 2025.", ORANGE),
    ("Organic", "The blue links", "Earned by relevance, quality and the page experience.", BLUE),
    ("Local", "Maps and Business Profiles", "For &lsquo;near me&rsquo; and city searches, Business Profiles show first.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "With an AI summary on the page, US users clicked a result on <b>8%</b> of visits, against <b>15%</b> without one (Pew, 2025). What does that do to a page that only answers questions?", size=28),
  """One part of the page per click.

AI Mode launched in Pakistan in English in August 2025 (Dawn, ProPakistani), on Google's app and mobile and desktop web; Urdu support was reported later.

Pew Research Center (22 July 2025) analysed 68,879 Google searches by 900 US adults in spring 2025: a traditional result was clicked on 8% of visits with an AI summary and 15% without; links inside the summary were clicked on 1%. A US study; Pakistani behaviour may differ.

Sources: Dawn, ProPakistani (Aug 2025); Pew Research Center (Jul 2025).""",
  footer="Sources: Dawn, ProPakistani (Aug 2025); Pew Research Center (Jul 2025)")

S["s11-google-keywords"] = tsec("s11-google-keywords", "#f5f5f6", "Google &middot; search terms", "Finding what Pakistanis type",
  grid([
    ("Autocomplete", "The box suggests", "Type a product, read the suggestions: price in Pakistan, original, for oily skin.", RED),
    ("Questions", "People also ask", "The questions under the results are content briefs for your pages.", ORANGE),
    ("Spellings", "Roman Urdu and English", "&lsquo;daanon ka ilaj&rsquo;, &lsquo;pimple face wash&rsquo;, misspellings &mdash; rank for how people type.", BLUE),
    ("Search Console", "Your own searches", "Free: the searches that already show your site, with clicks and position.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "Write for the words customers use, <b>not the words on the factory label</b>. Which three searches should your best-seller own?", size=30),
  """One source per click; all free.

Google's autocomplete and People also ask show what is searched; Google Trends compares terms within Pakistan; Search Console's Performance report lists the searches a site already appears for. The examples are illustrative: check them live in class.

Price modifiers ("price in Pakistan") and authenticity modifiers ("original") are common because shoppers compare marketplace sellers; a brand's own site can answer both directly.""")

S["s11-google-pages"] = tsec("s11-google-pages", "#ffffff", "Google &middot; pages", "Pages that deserve to rank",
  grid([
    ("Collections", "Category pages that land", "&lsquo;Face wash for oily skin&rsquo; as a collection with an introduction, filters and FAQs.", RED),
    ("Products", "Your own description", "Not the supplier&rsquo;s text on fifty sites: use, results, ingredients, who it is for.", ORANGE),
    ("Titles", "Say what it is", "Brand, product, key benefit, size &mdash; in the title and the main heading.", BLUE),
    ("Proof", "Reviews and real answers", "Customer reviews, photos and answers to the questions asked on WhatsApp.", GREEN),
  ], 4, 290, 400, bsize=24)
  + "\n" + band(5, 740, 130, "Google&rsquo;s advice has not changed with AI: <b>original, helpful pages written for people</b>.", size=31),
  """One rule per click.

Google Search Central's guidance is to create helpful, reliable, people-first content; its May 2025 guidance on AI features says there are no extra requirements for appearing in AI Overviews or AI Mode beyond normal Search eligibility and good SEO.

On Shopify, collections are the natural category pages; a short introduction and FAQs written from real customer questions give them something to rank for.""")

S["s11-google-tech"] = tsec("s11-google-tech", "#f5f5f6", "Google &middot; technical", "The technical floor",
  grid([
    ("Speed", "Core Web Vitals", "2.5s to load, 200ms to respond, no layout jumps &mdash; on real mobile visits.", RED),
    ("Structured data", "Price, stock, reviews", "Markup lets Google show price, availability, ratings, shipping and returns.", ORANGE),
    ("Index", "Sitemap and Search Console", "Submit the sitemap; fix the pages Google cannot crawl or chose not to index.", BLUE),
    ("Duplicates", "One address per product", "Variants and filtered pages point to the main page (canonical).", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "Shopify does much of this by default. <b>Check it in Search Console</b> rather than assume it.", size=31),
  """One item per click.

Google's merchant listing structured data covers Product and Offer (price, availability), reviews, shipping details and return policies; a store-wide return policy can be marked up once under Organization (MerchantReturnPolicy). Shopify themes output product structured data and a sitemap.xml, and set canonical addresses for variants; apps and theme edits can break them, which is why Search Console is the check.

Sources: Google Search Central, merchant listing and return policy structured data; web.dev.""")

S["s11-google-ai"] = tsec("s11-google-ai", "#ffffff", "Google &middot; AI answers", "Being cited by AI answers",
  grid([
    ("No trick", "Normal SEO", "Google says its AI features need no special setup beyond being indexed and eligible.", RED),
    ("Specific", "Answer exactly", "Ingredients, sizes, prices in PKR, delivery times: specific pages are easier to cite.", ORANGE),
    ("Consistent", "Same facts everywhere", "Price, policies and claims match on the site, Daraz, Instagram and the Business Profile.", BLUE),
    ("Measure", "Watch the clicks", "Clicks falling while rankings hold is the sign AI answers are taking them.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "AI answers send fewer clicks, so <b>the clicks you do get have to convert</b>.", size=31),
  """One idea per click.

Google's guidance (May 2025) is that AI Overviews and AI Mode use the same eligibility as Search, with no separate markup or file required. Consistency across sources is practitioner advice: AI answers draw on many pages, and conflicting prices or claims make a brand harder to cite. Search Console reports AI-feature traffic inside overall web search, without a separate line.""")

S["s11-google-ads"] = tsec("s11-google-ads", "#f5f5f6", "Google Ads", "Google Ads: the advanced moves",
  grid([
    ("Brand", "Protect your name", "A small campaign on your own name, so rivals do not take the click.", RED),
    ("Generic", "Buy the intent", "&lsquo;vitamin c serum price in Pakistan&rsquo;: product and price searches convert.", ORANGE),
    ("Negatives", "Read the search terms", "Every week, add the searches that waste money as negative keywords.", BLUE),
    ("Cities", "Bid by city", "Delivery, refusals and spending power differ by city: adjust bids and copy.", GREEN),
    ("Signals", "Enhanced conversions", "Send hashed customer data and offline sales so bidding learns from real buyers.", BROWN),
    ("AI Max", "Use it with fences", "Wider matching and AI-written copy: add brand and URL controls, compare with a hold-out.", GREY),
  ], 3, 290, 210, tsize=29, bsize=23)
  + "\n" + band(7, 770, 120, "Smart bidding is only as smart as what you count. <b>What counts as a conversion in your account?</b>", size=29),
  """One move per click.

AI Max for Search campaigns (launched May 2025) extends search term matching, writes ad text and chooses landing pages. Google reported 14% more conversions or conversion value at a similar CPA or ROAS for non-retail advertisers (27% for campaigns mostly on exact and phrase match), and later 7% for the full feature set against search-term matching alone. An independent analysis of more than 250 retail campaigns (Smarter Ecommerce) found a median revenue uplift of 13% with a median CPA 16% higher. Dynamic Search Ads are being upgraded to AI Max in 2026.

The lesson is the fence: brand controls, URL controls and a comparison against what the account did before.

Sources: Google Ads Help, About AI Max for Search campaigns; Google Ads blog (2025, 2026); Search Engine Land.""")

S["s11-google-shopping"] = tsec("s11-google-shopping", "#ffffff", "Google &middot; Shopping", "Shopping ads: check the map first",
  grid([
    ("Merchant Center", "The product feed", "Products, prices and stock sent to Google; Shopify&rsquo;s Google app keeps it in sync.", RED),
    ("Countries", "Check the list first", "Shopping ads and free listings run only in the countries Google supports.", ORANGE),
    ("Diaspora", "Sell where it runs", "UK, UAE and US campaigns for Pakistanis abroad, with a feed in that currency.", BLUE),
  ], 3, 290, 320)
  + "\n" + band(4, 660, 190, "At home, two free tools still work: a <b>Business Profile</b>, and product markup on your own pages.", size=31),
  """One step per click.

Merchant Center's supported-countries list decides where Shopping ads and free listings can run. A Pakistani guide that read the list on 7 October 2026 found Pakistan absent while India and the UAE were listed; older guides list Pakistan in a beta. Check the live list before building a feed for Pakistan.

For the diaspora, the feed must be in the target country's currency, with that country's shipping costs.

Sources: Google Merchant Center Help, supported languages and currencies; Pakera (Oct 2026).""")

S["s11-google-case"] = cases("s11-google-case", "Cases &middot; Google", "The fast page and the clear signal",
  ("Pakistan", "Beechtree", "Fashion, with Google", [
    ("The site", "Moved to multi-node hosting: pages loaded up to 30% faster under heavy traffic."),
    ("The tests", "A/B tested which products to promote in each region, with separate city landing pages."),
    ("The audiences", "Tagged the whole site to build remarketing lists such as product viewers and shopping intent.")]),
  ("Global", "IKEA U.S.", "AI Max for Search", [
    ("The setup", "Search term matching, text customisation and final URL expansion together."),
    ("The result", "Store visits up 127%, unbranded clicks up 65%, incremental ROAS up 28%, Google reported.")]),
  "Google rewards the fast page and the clear signal. <b>Neither is bought with budget alone.</b>",
  """Two Google cases.

Beechtree: Think with Google's Pakistan case study describes the HKB-owned fashion retailer shifting from new stores to e-commerce with its agency Shopistan: multi-node hosting that kept pages up to 30% faster under high traffic, A/B tests to choose which products to promote in each region, separate landing pages for Islamabad and Karachi, and site-wide tagging to build remarketing audiences such as product viewers and shopping intent. Google-reported.

IKEA U.S.: Think with Google reports that using all three AI Max features led to a 127% increase in physical store visits, a 65% lift in generic (unbranded) clicks and a 28% higher incremental ROAS. Google-reported; independent retail results are more mixed (previous slide).

Sources: Think with Google, A proven formula in Pakistan; Think with Google, How brands use AI Max for Search campaigns.""",
  "Sources: Think with Google, Beechtree; Think with Google, AI Max for Search")

# --- The toolkit, applied -----------------------------------------------------------------

S["s11-tk-ex"] = exercise("s11-tk-ex", "Exercise 3", "One brand, three audits",
  "A Pakistani skincare or home-care brand you know: its store on a phone, its live ads in Meta&rsquo;s public Ad Library, and its name on Google.",
  ["What slows its store down &mdash; and what would you remove?", "How many of its live ads are meaningfully different?",
   "Which search should it own on Google, and does it?", "One fix for each: which pays back first?"],
  "Exercise 3 &middot; the toolkit on a real brand",
  """Twelve minutes in teams. One question per click.

Meta's Ad Library is public: any page's active ads, with start dates, can be seen without an account. PageSpeed Insights gives a speed check on any address. A Google search on a phone shows what a shopper sees.

Push for one fix per toolkit and an argument about which pays back first: usually speed or cash-on-delivery confirmation, because they lift every order the brand already wins.""", top=500, h=180, cols=2)

toolkit_sim = [("A faster, clearer store", "5.1 website experience", "Closes part of the gap to the best your store can be, from the next month"),
               ("Bundles and a delivery bar", "1.2 bundles &middot; 2.4 free-delivery threshold", "Bigger baskets, with the product cost of the extra items"),
               ("COD control, paying online", "9.1 cash on delivery &middot; 9.2 prepaid discount", "Fewer refusals against fewer orders"),
               ("Creative that differs", "3.8 creative production", "Creative quality rises with spend and fades with time"),
               ("Broad or aimed audiences", "3.10 campaigns on Meta and TikTok", "Broad scores 1.0; aiming at real buyers helps; a pool too small for the budget tires"),
               ("Language and format", "3.10 language &middot; format", "Matching the product&rsquo;s buyers adds; mismatching costs"),
               ("Brand and generic search", "3.10 Google keywords &middot; match", "Your name is cheap but limited by brand equity; exact match narrows reach"),
               ("Testing", "3.10 test A against B", "One A and one B on a channel, compared in the report")]
S["s11-tk-sim"] = tsec("s11-tk-sim", "#ffffff", "In the simulation", "The toolkit in the simulation",
  trows(["Real move", "Where it is", "How the simulation treats it"], toolkit_sim, 262,
        [430, 500, 678], rh=76, size=23, head_size=19),
  """One row per click. The rules are the simulation's.

What the simulation does not model: Andromeda's creative-led delivery (creative quality comes from the production budget, 3.8, and audiences from the campaign settings, 3.10, scored against buyer profiles fixed for the whole game), Google's AI answers, and Shopify's own tools. Targeting effects are capped, and a broad campaign is the neutral baseline, so careful aiming helps without being the whole answer &mdash; much as the real platforms now argue.

These are the simulation's assumptions, not market data.""",
  footer="Decision rules from the simulation &middot; not market data")

TOOLKIT_ORDER = ["s11-tk-part",
                 "s11-shop", "s11-shop-system", "s11-shop-speed", "s11-shop-data", "s11-shop-search",
                 "s11-shop-basket", "s11-shop-cod", "s11-shop-ai", "s11-shop-markets", "s11-shop-audit",
                 "s11-shop-case",
                 "s11-meta", "s11-meta-how", "s11-meta-shift", "s11-meta-diverse", "s11-meta-matrix",
                 "s11-meta-structure", "s11-meta-signals", "s11-meta-whatsapp", "s11-meta-read", "s11-meta-case",
                 "s11-google", "s11-google-page", "s11-google-keywords", "s11-google-pages", "s11-google-tech",
                 "s11-google-ai", "s11-google-ads", "s11-google-shopping", "s11-google-case",
                 "s11-tk-ex", "s11-tk-sim"]
TOOLKIT_SECTIONS = {
    "s11-toolkit": {"description": "Part 2 · The toolkit · Shopify: speed, data, search, basket, COD control and AI", "start": "s11-tk-part"},
    "s11-meta": {"description": "Toolkit · Meta ads in the Andromeda era: creative, structure, signals, WhatsApp", "start": "s11-meta"},
    "s11-google": {"description": "Toolkit · Google Search: the results page, SEO, AI answers, Google Ads and Shopping", "start": "s11-google"},
    "s11-toolkit-applied": {"description": "Toolkit · an audit exercise, and the toolkit in the simulation", "start": "s11-tk-ex"}}
