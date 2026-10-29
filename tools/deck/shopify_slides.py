"""Advanced Shopify - a workshop deck beside Session 11's toolkit. About 40 slides.

Run: python shopify_slides.py <deck folder> [logo url]
Built from the instructor's note "Advanced Shopify Website Tricks": four parts of
real-world practice (sell more per visit, build more into the store, what most
stores overlook, for developers), each with sourced cases, then the simulation.
Platform facts were checked in October 2026; Shopify changes its plans and
features every few months, so check them again before teaching. Slide ids carry
a "shp-" prefix.
"""
import html, pathlib, sys, json
HERE = pathlib.Path(__file__).parent
exec((HERE / "s7_slides.py").read_text().split("\nS = {}\n")[0])
FT = "Advanced Shopify &middot; Tricks that pay"
ILL = "Illustrative numbers, PKR &middot; not market data"
def sec(sid, bg, eyebrow, title, body, notes, footer=FT, **kw):
    return section(sid, bg, "#131316", eyebrow, title, body, notes, footer=footer, **kw)
def div(sid, part, title, line, notes):
    return divider(sid, part, title, line, notes).replace("Session 2 &middot; Finding the Right Idea", FT).replace("856d57cb939a323d46943b3b229572d7", "__LOGO__")

RED, ORANGE, BLUE, GREEN, BROWN, GREY = "#ed0000", "#eb6834", "#2a78d6", "#1baf7a", "#8a6414", "#55555f"


def code(n, L, T, W, H, label, lines, size=22):
    """A dark code panel: lines are shown as written, in a monospace face."""
    body = "<br>".join(html.escape(x).replace(" ", "&nbsp;") for x in lines)
    return f'''  <div data-build-in="fade {n}" style="position:absolute; left:{L}px; top:{T}px; width:{W}px; height:{H}px; background:#131316; padding:30px 36px; border-radius:18px; display:flex; flex-direction:column; gap:16px">
    <p style="font-size:20px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:#ff3b3b">{label}</p>
    <p style="font-size:{size}px; line-height:1.55; color:#e4e4e7; font-family:'JetBrains Mono', monospace; font-variant-ligatures:none; font-feature-settings:'liga' 0, 'calt' 0; white-space:nowrap">{body}</p>
  </div>'''


def side(items, start, top=290, h=176, L=1164, W=628):
    """Cards stacked beside a code panel."""
    return "\n".join(card(start + i, L, top + i * (h + 20), W, h, lab, t, x, col=c, pad="24px 30px", tsize=27, bsize=22)
                     for i, (lab, t, x, c) in enumerate(items))


S = {}

# --- Opening ---------------------------------------------------------------------------

S["shp-cover"] = cover("X", "Advanced<br>Shopify",
  "Moves that raise the basket, take out the busywork and show what each order really earns.",
  """A workshop deck that goes deeper than Session 11's Shopify toolkit. About 40 slides in five parts: 1 sell more per visit, 2 build more into the store, 3 what most stores overlook, 4 for developers, 5 the simulation.

It can be taught in one block of about two and a half hours, or as two sessions. Session A, for every founder, about 90 minutes: the opening question 8, Part 1 30, Part 3 30, the exercise 12, Part 5 10. Session B, for whoever builds the store, about 75 minutes: Part 2 35, Part 4 40.

Built from the instructor's note "Advanced Shopify Website Tricks". Every platform claim was checked against Shopify's documentation, the developer docs and named sources in October 2026; Shopify renames plans and features often, so check the dated ones (plan availability above all) before teaching. Vendor-reported results are marked as such.""",
  size=132).replace('id="cover"', 'id="shp-cover"').replace("Session X of 12", "Workshop &middot; Shopify")

S["shp-ex1"] = exercise("shp-ex1", "Opening question", "The store you nearly left",
  "The last Pakistani online store where you nearly gave up before paying &mdash; or did.",
  ["What nearly made you leave?", "What made you stay &mdash; or not?",
   "What did it show you that you had not asked for?", "Would you buy there again? Why?"],
  "Opening question",
  """Eight minutes: two minutes alone, then the room. One question per click.

Collect the answers and sort them into the four parts on the next slide: most will be checkout and delivery surprises (Part 1), slow pages (Part 3) and a store that did not answer the question the shopper had (Part 2, product data). Come back to them at the end.""",
  top=500, h=180, cols=2)

S["shp-map"] = sec("shp-map", "#ffffff", "The workshop", "Four kinds of move",
  grid([
    ("Part 1", "Sell more per visit", "Bundles, quantity breaks, a free-delivery bar and a checkout that does not lose people.", RED),
    ("Part 2", "Build more into the store", "Metafields, metaobjects, Flow, Liquid, Functions, and links to the back office.", ORANGE),
    ("Part 3", "What most stores overlook", "Personalisation, speed, orders recovered, and the profit on each order.", BLUE),
    ("Part 4", "For developers", "Dynamic pages, content systems, business rules, checkout logic and integrations.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "Parts 1 and 3 are for every founder; Parts 2 and 4 for whoever builds the store. <b>Who is that in your team?</b>", size=30),
  """One part per click. Part 5, at the end, maps the moves onto the simulation's decisions.

The moves come from one rule: a store earns more by selling more to the visitors it already has, and by doing less by hand, before it buys more traffic.""")

# --- Part 1 - Sell more per visit -------------------------------------------------------

S["shp-part1"] = div("shp-part1", "Part 1 &middot; Sell more per visit", "Bigger baskets,<br>fewer exits",
  "Bundles, quantity breaks, a free-delivery bar, and a checkout that does not lose people.",
  """Part 1 is about the visitor already in the store: what makes the basket bigger, and what makes them leave before paying. About 30 minutes.""")

S["shp-bundles"] = sec("shp-bundles", "#ffffff", "Sell more &middot; bundles", "Bundles: sell the routine",
  grid([
    ("What", "The routine, not the item", "Cleanser, toner and moisturiser as one product &mdash; or a three-pack of a staple.", RED),
    ("Shopify", "The free Bundles app", "Shopify&rsquo;s own app builds fixed bundles and multipacks; stock follows the parts.", ORANGE),
    ("Limits", "Fixed, not mix-and-match", "Build-your-own boxes and tiered bundle prices need a third-party app.", BLUE),
    ("Where", "Where the shopper decides", "&lsquo;Complete the routine&rsquo; on the product page; one bundle offer in the cart.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "A bundle pays only if it moves shoppers up. <b>Who buys it: people who wanted one item, or people who wanted all three anyway?</b>", size=30),
  """One idea per click.

Shopify Bundles is Shopify's own free app (launched 2023): fixed bundles and multipacks, with inventory tracked through the component products. It does not do mix-and-match, build-your-own boxes or tiered bundle pricing; reviewers name these as its gaps, and apps fill them. Third-party reviews cite limits such as 30 components and 100 variants per bundle; check Shopify's documentation for the current limits. Shopify's developer docs list the Online Store, Shop and Shopify POS as channels that can sell bundles.

The question on the band is the whole economics of a bundle: the saving is given to every buyer, including those who would have bought all three at full price.

Sources: Shopify Bundles app listing; shopify.dev, Bundles; BOGOS and Craftshift reviews (2026).""")

S["shp-quantity"] = sec("shp-quantity", "#f5f5f6", "Sell more &middot; quantity breaks", "Quantity breaks, carefully",
  grid([
    ("Offer", "5% off two, 10% off three", "A reason to take one more of something the shopper already wants.", RED),
    ("Shopify", "Automatic discounts", "One automatic discount per tier, set by minimum quantity &mdash; no code to type.", ORANGE),
    ("Apps", "Tier tables on the page", "Volume-discount apps, built on Shopify Functions, show the tiers beside the price.", BLUE),
    ("Trade", "Price breaks for B2B", "Shopify&rsquo;s own quantity price breaks are for B2B company accounts, not shoppers.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "Every tier is a discount for people who would have bought that many anyway. <b>How many have to move up to pay for them?</b>", size=30),
  """One idea per click; the next slide does the sum.

Shopify's automatic discounts (amount off products, with a minimum quantity of items) set one tier each, so three tiers are three discounts; how automatic discounts combine is set on each discount. Volume-discount apps add tier tables, badges and customer-tag rules.

B2B: third-party guides report that Shopify extended native B2B quantity price breaks to all paid plans in April 2026, for company accounts only, with a limited number of catalogues outside Plus. Check Shopify's Help Center before teaching this line.

Sources: Skailama, BOGOS and Sherocommerce guides (2026).""")

S["shp-basket-math"] = sec("shp-basket-math", "#ffffff", "Sell more &middot; the sum", "What a tier earns",
  band(1, 262, 90, "An item sells at PKR 1,000 and costs PKR 400. The store pays PKR 250 to deliver each parcel.", bg="#f5f5f6", col="#33333b", size=27)
  + "\n" + trows(["Order", "Revenue", "Product cost", "Delivery", "Earns"],
                 [("One item", "1,000", "400", "250", "350"),
                  ("Two items, 5% off", "1,900", "800", "250", "850"),
                  ("Three items, 10% off", "2,700", "1,200", "250", "1,250")],
                 382, [560, 262, 262, 262, 262], rh=84, size=27, start=2)
  + "\n" + band(5, 736, 150, "One shopper moved from one item to two earns PKR 500 more; one who wanted two anyway now earns PKR 100 less. <b>One mover pays for five.</b>", size=30),
  """Assumptions first, then one order per click, then the conclusion. The numbers are illustrative.

Why a tier can pay: delivery is paid per parcel, so the second and third items ride free. Why it can lose: two items at full price would have earned 950, and the discount takes 100 of it from every shopper who wanted two anyway.

A question for the room: at 10% off three, how many shoppers must move up from one item to pay for each one who wanted three anyway? (Three at full price earns 1,550; at 10% off, 1,250, so each costs 300. Moving from one to three earns 900 more: one mover pays for three.)""",
  footer=ILL)

S["shp-threshold"] = sec("shp-threshold", "#f5f5f6", "Sell more &middot; free delivery", "The free-delivery bar",
  grid([
    ("Show", "Progress in the cart", "&ldquo;Add Rs. 500 more for free delivery&rdquo; &mdash; a theme setting or a small app.", RED),
    ("Set", "From your own costs", "The items added to reach it must earn back the delivery you give away.", ORANGE),
    ("Place", "Just above a typical basket", "Close enough to reach with one more item; far enough to need one.", BLUE),
    ("Watch", "Baskets bunch at the bar", "Baskets just above it: it works. Small orders vanish: it is too high.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "Surveys say many shoppers add items to qualify &mdash; <b>but what shoppers say is more than what they do.</b> Your own order data decides.", size=30),
  """One idea per click.

The surveys disagree: figures from 51% to 84% of shoppers saying they have added items to reach a free-shipping threshold are quoted (Dotcom Distribution 67%; an eConsultancy survey of 5,000+ shoppers 58% who would act to qualify), and most are stated intent, not observed behaviour. The store's own basket sizes, before and after a bar, are the evidence that counts.

Sources: secondary summaries of Dotcom Distribution, eConsultancy and NRF surveys (Red Stag Fulfillment, 2026).""")

S["shp-threshold-math"] = sec("shp-threshold-math", "#ffffff", "Sell more &middot; the sum", "Setting the bar",
  row3([("Typical basket", "PKR 2,200", "The middle of your basket sizes over the last 90 days of orders."),
        ("Delivery &divide; margin", "+ PKR 500", "PKR 250 to deliver at a 50% gross margin: PKR 500 of extra product pays for it."),
        ("The bar", "PKR 2,700", "Close enough for one more item; the margin on anything added beyond it is profit.")], 290, 400)
  + "\n" + band(4, 730, 150, "Bar &asymp; typical basket + delivery cost &divide; gross margin. <b>And a month later: did baskets move up, or did small orders disappear?</b>", size=30),
  """One step per click. The numbers are illustrative.

The rule of thumb sets the bar where the extra product a shopper adds to reach it pays for the delivery the store now covers. Then it is tested: move it a few hundred rupees and compare a month of orders.

Use the median basket, not the mean: a few large orders pull the mean up and put the bar out of reach of most shoppers.""",
  footer=ILL)

S["shp-checkout"] = sec("shp-checkout", "#f5f5f6", "Sell more &middot; checkout", "Take the friction out of checkout",
  grid([
    ("Costs", "No surprise at the end", "Delivery and any cash-on-delivery charge on the product page and in the cart.", RED),
    ("Fields", "Only what the courier needs", "Name, phone, address, city; the rest optional or hidden in checkout settings.", ORANGE),
    ("Buttons", "Accelerated checkout", "Shop Pay, Apple Pay and Google Pay buttons depend on Shopify Payments &mdash; not in Pakistan.", BLUE),
    ("Trust", "Policies one tap away", "Returns, exchanges and delivery times linked from the cart and the checkout.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "Baymard Institute&rsquo;s average across 48 studies: <b>about 7 in 10 carts are abandoned</b>, and unexpected extra costs are the reason shoppers give most.", size=30),
  """One idea per click.

Baymard Institute's average of 48+ studies puts cart abandonment at about 70% (70.19% in its 2025 figure, as widely quoted). In its survey of shoppers who abandoned, extra costs (delivery, taxes, fees) are the top reason, ahead of forced account creation, card-security worries, slow delivery and a long checkout; the exact shares differ by edition.

Shopify's checkout settings let a store make fields such as company and address line 2 optional or hidden. Accelerated buttons (Shop Pay and wallet buttons) rely on Shopify Payments or supported providers, which Pakistan-based stores do not have; local gateways bring cards and mobile wallets instead.

Sources: Baymard Institute via Contentsquare and others (2025); Shopify Community and third-party guides on Shop Pay.""")

S["shp-checkout-pk"] = sec("shp-checkout-pk", "#ffffff", "Sell more &middot; checkout in Pakistan", "Checkout, the Pakistani way",
  grid([
    ("COD", "Say how it works", "Pay the rider in cash; the total, with delivery, shown before the order is placed.", RED),
    ("Dates", "A promise by city", "&lsquo;Lahore 1&ndash;2 days, other cities 3&ndash;5&rsquo; on the product page and in the confirmation.", ORANGE),
    ("Exchange", "One line, one link", "What can be exchanged, within how many days, and who pays the courier.", BLUE),
    ("Confirm", "Before the parcel leaves", "A WhatsApp message or a call to confirm the order; unconfirmed orders wait.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "DHL&rsquo;s advice to Pakistani sellers: <b>check the buyer still wants it before dispatch</b> &mdash; confirm, screen risky orders, reward paying online.", size=30),
  """One idea per click. The delivery promise in the second card is an example, not a benchmark.

DHL's e-commerce advice for Pakistan argues that cash-on-delivery returns eat sellers' margins and that the fix is to verify intent before dispatch: confirmation calls, screening high-risk orders and encouraging digital prepayment. It puts the share of Pakistani online shoppers who prefer cash on delivery at nearly 70%. Payment companies' blogs put COD's share of orders higher (85&ndash;94%) and refusals at 25&ndash;30%; these are vendor figures.

Sources: DHL Discover Pakistan, How Pakistani e-commerce sellers can reduce COD returns; Simpaisa blog (June 2026).""")

S["shp-case-sales"] = cases("shp-case-sales", "Cases &middot; sell more per visit", "Fewer exits, bigger baskets",
  ("Pakistan", "Interwood", "Furniture, Pakistan", [
    ("The move", "From Magento (Adobe Commerce) to Shopify Plus, with the agency Devsinc."),
    ("The result", "Orders up 55%, uptime up 90%, a Lighthouse score of 85 and fewer abandoned carts, Devsinc reports.")]),
  ("Regional", "Bombay Shaving Company", "India", [
    ("The move", "From a custom build, then Magento, to Shopify in 2021."),
    ("The result", "Conversion up 150% and average order value four times higher, Shopify reports; 50,000+ orders in two days of a sale.")]),
  "Both sold more to the visitors they already had. <b>Fix the store before you buy more traffic.</b>",
  """Two cases, both vendor-reported: the direction is the lesson, not the size.

Interwood: Devsinc's case study describes moving the furniture retailer's store from Adobe Commerce (Magento 2) to Shopify Plus, with 55% more orders, uptime up 90%, a Lighthouse score of 85, operations twice as fast and reduced cart abandonment (no figure given).

Bombay Shaving Company: Shopify's case study says the brand moved from a custom platform, then Magento, to Shopify in 2021, and credits a 150% uplift in conversion rate, four times the average order value and 20 times the online revenue, with more than 50,000 orders in two days during its monthly sales.

Sources: Devsinc case study, Interwood; Shopify case study, Bombay Shaving Company.""",
  "Sources: Devsinc case study, Interwood; Shopify case study, Bombay Shaving Company")

# --- Part 2 - Build more into the store ---------------------------------------------------

S["shp-part2"] = div("shp-part2", "Part 2 &middot; Build more into the store", "A store that behaves<br>like a platform",
  "Six tools that let a Shopify store do what a custom-built one does &mdash; without building one.",
  """Part 2 is the technical toolkit, explained for founders: what each tool does and what it costs to use. Part 4 shows the code. About 35 minutes.""")

tech = [("Metafields", "Facts stored as fields: specs, ingredients, warranty, size", "Every plan"),
        ("Metaobjects", "Reusable content: FAQs, size guides, brand stories, landing sections", "Every plan"),
        ("Shopify Flow", "Automations: tag orders, flag risky ones, tell staff", "Basic and above"),
        ("Custom Liquid", "Custom sections, conditional content, badges", "Every Online Store 2.0 theme"),
        ("Shopify Functions", "Your own discount, delivery and payment rules in checkout", "Apps on every plan; your own code on Plus"),
        ("Webhooks and APIs", "Links to your ERP, POS, couriers, CRM and analytics", "Every plan")]
S["shp-tech-map"] = sec("shp-tech-map", "#ffffff", "Build more &middot; the tools", "Six tools beyond the theme",
  trows(["Tool", "What it does", "Where it works"], tech, 262, [380, 800, 428], rh=76, size=25, head_size=20)
  + "\n" + band(7, 790, 110, "Together they give a store <b>a custom platform&rsquo;s behaviour without building a platform.</b>", size=29),
  """One tool per click; the next slides take them one at a time.

Availability as checked in October 2026. Metafields, metaobjects and webhooks work on every plan. Shopify Flow is free and runs on Basic and above; some actions (sending an HTTP request) are reported by third-party guides to need a higher plan. Shopify Functions: any store can use App Store apps built on them; only Plus stores can run custom apps containing their own functions. Custom Liquid is a section in Online Store 2.0 themes such as Dawn.

Sources: shopify.dev, About Shopify Functions; shopify.dev, Metaobject limits; third-party guides to Shopify Flow (2026).""")

S["shp-metafields"] = sec("shp-metafields", "#f5f5f6", "Build more &middot; metafields", "Metafields: one fact, many places",
  grid([
    ("Define", "A field with a type", "Settings, then Custom data: text, number, list, file or a link to another product.", RED),
    ("Fill", "Once, in bulk", "Fill in the admin&rsquo;s bulk editor or by CSV import, not product by product.", ORANGE),
    ("Show", "No code needed", "Theme blocks connect to the field as a dynamic source on every product page.", BLUE),
    ("Use", "Filters, feeds, agents", "Search &amp; Discovery filters, Google&rsquo;s feed and AI agents read the same field.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "For a skincare range: skin type, concern, key ingredient, size. <b>Which question do your shoppers ask on WhatsApp before buying?</b>", size=30),
  """One step per click.

A metafield definition sets the field's type and validation; the theme editor connects it to a block through dynamic sources, and the free Search &amp; Discovery app can turn product and variant metafields into storefront filters. The question on the band finds the first metafield: whatever shoppers ask most before buying is a fact the product page should carry as a field.

Sources: Shopify Help Center, Custom data; Shopify Search &amp; Discovery app.""")

S["shp-metaobjects"] = sec("shp-metaobjects", "#ffffff", "Build more &middot; metaobjects", "Metaobjects: write once, show everywhere",
  grid([
    ("FAQs", "One answer, many pages", "Each question an entry; products and pages show the ones that apply.", RED),
    ("Guides", "Size and ingredient guides", "One entry per ingredient: what it does and who it is for, linked from products.", ORANGE),
    ("Stories", "Brand and maker profiles", "The founder, the artisan, the farm &mdash; written once, shown wherever it fits.", BLUE),
    ("Pages", "Landing sections", "Campaign and city pages built from entries, so the team edits content, not code.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "Change the entry once, and <b>every page that shows it changes with it.</b>", size=31),
  """One use per click.

A metaobject is a content type you define (fields such as name, description, image) with as many entries as you need; products link to entries through metafields, and themes show them through dynamic sources. Limits (Shopify developer docs, October 2025 change): up to 1,000,000 entries per definition, up to 40 fields per definition, and 128 merchant-created definitions on Basic, Shopify and Advanced (256 on Plus).

Sources: shopify.dev, Metaobject limits; Shopify developer changelog, Increased limits for metafields and metaobjects (October 2025).""")

flows = [("Order created", "Cash on delivery, first order, over PKR 10,000", "Tag &lsquo;confirm&rsquo; and alert the team"),
         ("Order risk analysed", "Risk is high", "Hold fulfilment and notify the owner"),
         ("Inventory changed", "Fewer than 10 units left", "Tag the product and email the buyer"),
         ("Order fulfilled", "Customer agreed to marketing", "Tag for a review request"),
         ("Scheduled, daily", "Product out of stock for 30 days", "Hide it from the store")]
S["shp-flow"] = sec("shp-flow", "#f5f5f6", "Build more &middot; Shopify Flow", "Flow: when, if, then",
  trows(["When (trigger)", "If (condition)", "Then (action)"], flows, 262, [440, 600, 568], rh=84, size=25, head_size=20)
  + "\n" + band(6, 770, 110, "Every rule a person follows by hand is a Flow waiting to be written. <b>Which one does your team do every day?</b>", size=29),
  """One workflow per click. The thresholds are examples.

Shopify Flow is free on Basic and above. A workflow is one trigger, any number of conditions and one or more actions; triggers can be store events, a schedule, or events from other apps. Shopify publishes a library of templates to start from. Third-party guides report limits such as a 90-day maximum wait and that some actions (sending an HTTP request to another system) need a higher plan; check them in the Flow app.

Sources: Shopify Flow app; third-party guides (Ringly, eSEOspace, 2026).""")

S["shp-liquid"] = sec("shp-liquid", "#ffffff", "Build more &middot; Custom Liquid", "Custom Liquid: small code, big effect",
  grid([
    ("Badges", "Say it on the card", "&lsquo;Bestseller&rsquo; or &lsquo;Ships from Lahore in 24 hours&rsquo;, from a tag or a field.", RED),
    ("Conditions", "Show it only when it applies", "A cash-on-delivery note on eligible products; a free-delivery line above the bar.", ORANGE),
    ("Sections", "Blocks the theme lacks", "&lsquo;Complete the routine&rsquo;, reading a list of products from a metafield.", BLUE),
    ("Tools", "Interactive help", "A shade or size finder that asks two questions and points to one product.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "Liquid is Shopify&rsquo;s template language: <b>a few lines in a Custom Liquid section</b>, no new theme, no app.", size=30),
  """One use per click; Part 4 shows the code.

Online Store 2.0 themes such as Dawn include a Custom Liquid section and block, so small pieces of code can be added in the theme editor without editing theme files. Anything larger belongs in the theme's code, kept under version control.""")

S["shp-functions"] = sec("shp-functions", "#f5f5f6", "Build more &middot; Shopify Functions", "Functions: your rules in checkout",
  grid([
    ("Discounts", "Tiers, gifts, bundles", "Product, order and delivery discounts with logic the built-in ones lack.", RED),
    ("Delivery", "Rename, reorder, hide", "Hide &lsquo;same-day Lahore&rsquo; for addresses outside Lahore.", ORANGE),
    ("Payments", "Choose who sees COD", "Hide cash on delivery above a cart value, or for a flagged customer.", BLUE),
    ("Rules", "Stop a bad checkout", "Limit units per customer in a sale; insist on a valid mobile number.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "Most stores get Functions through an app; <b>only Plus stores can run functions they write themselves.</b>", size=30),
  """One use per click.

Shopify Functions run custom logic inside Shopify's checkout: discount functions (product, order and delivery), delivery customisation, payment customisation, and cart and checkout validation, among others. Stores on any plan can use public App Store apps that contain functions; only Shopify Plus stores can use custom apps that contain them. Shopify Scripts, the older Plus-only way, stopped running on 30 June 2026.

Sources: shopify.dev, About Shopify Functions; shopify.dev, Function APIs.""")

S["shp-apis"] = sec("shp-apis", "#ffffff", "Build more &middot; webhooks and APIs", "Connect the back office",
  grid([
    ("Webhooks", "Shopify calls you", "The moment an order is created, paid or fulfilled, your system hears &mdash; no checking.", RED),
    ("Admin API", "You call Shopify", "Update stock, prices and tracking from your own systems; GraphQL is the current API.", ORANGE),
    ("Couriers", "Book from the admin", "Apps book PostEx, Leopards, Trax and TCS parcels and bring tracking back.", BLUE),
    ("POS and ERP", "One stock count", "Connectors sync shop and store stock with Pakistani POS systems such as Candela.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "Every number copied by hand between two systems is a mistake waiting to happen. <b>Which one does your team still copy?</b>", size=30),
  """One link per click.

Webhooks notify an app about shop events (an order created, a product updated) so it does not have to poll. Shopify made the REST Admin API legacy on 1 October 2024, and new public apps must use the GraphQL Admin API from 1 April 2025.

Examples from Shopify's App Store: Courierify (launched January 2026) books and tracks parcels with PostEx, Leopards, Trax, TCS and BlueEx; Candela Connector syncs orders and stock between Candela and Shopify. Listed as examples of what exists, not as recommendations.

Sources: shopify.dev, REST Admin API (legacy notice); Shopify App Store listings, Courierify and Candela Connector.""")

S["shp-case-tech"] = cases("shp-case-tech", "Cases &middot; build more", "Rules in the system, not in people",
  ("Pakistan", "The local stack", "Shopify App Store, 2026", [
    ("Couriers", "Courierify books PostEx, Leopards, Trax, TCS and BlueEx parcels and syncs tracking; free."),
    ("Stores", "Candela Connector keeps Shopify and Candela POS orders and stock in step."),
    ("What it means", "A Pakistani store can link couriers and shops without writing the integration.")]),
  ("Global", "Shelfies", "Custom apparel, with Flow", [
    ("The rule", "High-risk orders automatically tell the manufacturer to halt production."),
    ("The result", "Fraudulent production avoided, and design turnaround cut from six hours to two, Shopify reports.")]),
  "Write the rule once and the system follows it every time. <b>People forget; workflows do not.</b>",
  """Two cases. The local apps are examples of what exists, not recommendations; check any app's reviews and terms before installing.

Courierify (GrowZar, launched 30 January 2026, free): one-click booking, labels, bulk loadsheets and tracking sync for Pakistani couriers. Candela Connector: syncs orders and inventory between Candela and Shopify, with a free tier and paid plans.

Shelfies: Shopify's case study describes Flow workflows that alert the manufacturer to stop production on high-risk orders, saving thousands in production and chargeback costs, and cut custom-design turnaround from six hours to two. Vendor-reported.

Sources: Shopify App Store, Courierify and Candela Connector; Shopify case study, Shelfies.""",
  "Sources: Shopify App Store listings; Shopify case study, Shelfies")

# --- Part 3 - What most stores overlook -------------------------------------------------------

S["shp-part3"] = div("shp-part3", "Part 3 &middot; What most stores overlook", "The quiet<br>money",
  "A storefront that knows the shopper, speed without a new theme, orders won back, and profit per order.",
  """Part 3 is the money most stores leave on the table: none of it needs more traffic. About 30 minutes.""")

S["shp-personal"] = sec("shp-personal", "#ffffff", "Overlooked &middot; personalisation", "A storefront that knows the shopper",
  grid([
    ("Behaviour", "What they looked at", "Recently viewed and &lsquo;goes well with&rsquo;, from Shopify&rsquo;s recommendations.", RED),
    ("History", "What they bought", "A signed-in customer sees a reorder button for the last purchase.", ORANGE),
    ("Attributes", "What fits them", "Pick a skin type once; the collection filters to it from the metafields.", BLUE),
    ("Segments", "Who they are", "Segments for messages; Flow tags them so the theme can show them more.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "Few Pakistani shoppers sign in to pay cash on delivery, so <b>behaviour and attributes do most of the work</b> &mdash; and WhatsApp the rest.", size=30),
  """One source per click.

Shopify's product recommendations (related and complementary, set by hand or automatically in Search &amp; Discovery) work for every visitor. Purchase history needs a signed-in customer, which is rare when most orders are guest checkouts paid in cash. Customer segments are built in the admin for marketing; the theme cannot read segment membership directly, so stores use Flow to tag customers and Liquid to show tagged customers different content.

McKinsey's explainer reports that 71% of consumers expect personalised interactions and 76% are frustrated when they do not get them.

Sources: Shopify Search &amp; Discovery app; Shopify developer community; McKinsey, What is personalization?""")

S["shp-speed"] = sec("shp-speed", "#f5f5f6", "Overlooked &middot; speed", "Faster without a new theme",
  grid([
    ("Images", "Let the CDN do it", "Shopify&rsquo;s image filters serve WebP or AVIF at the right size, and lazy-load below the fold.", RED),
    ("Apps", "Fewer, and cleaned up", "Remove unused apps, then check the theme for the code they left behind.", ORANGE),
    ("Scripts", "Only where needed", "Reviews on product pages, not the home page; chat after the page has loaded.", BLUE),
    ("Measure", "On a phone, from real visits", "PageSpeed Insights and Search Console: the Core Web Vitals, on mobile.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "Deloitte, for Google: <b>a 0.1-second faster mobile site lifted retail conversions 8.4%</b>, across 37 brands and 30 million sessions.", size=30),
  """One fix per click.

Shopify's theme best practices: the image_url and image_tag filters give responsive srcset, the right dimensions and format negotiation (WebP or AVIF where the browser supports it) through Shopify's CDN, with images below the first screen loaded lazily. Older apps that edited theme files can leave scripts behind after removal; apps built on theme app extensions remove cleanly.

Core Web Vitals, at the 75th percentile of real visits: Largest Contentful Paint 2.5 seconds or less, Interaction to Next Paint 200 milliseconds or less, Cumulative Layout Shift 0.1 or less.

Deloitte's Milliseconds Make Millions (2020, commissioned by Google, 37 European and US brand sites, 30 million sessions): a 0.1-second improvement in mobile speed metrics was associated with 8.4% more retail conversions (Deloitte's own report rounds to 8%) and almost 10% more spending.

Sources: shopify.dev, Theme performance best practices; web.dev, Core Web Vitals thresholds; web.dev, Milliseconds make millions.""")

S["shp-recovery"] = sec("shp-recovery", "#ffffff", "Overlooked &middot; recovery", "Win back the orders you nearly had",
  grid([
    ("Abandoned", "The checkout left half-way", "A reminder within hours, by email or WhatsApp, to the number given at checkout.", RED),
    ("After the order", "Confirm and teach", "Confirmation, delivery date, how to use it &mdash; and the cash-on-delivery check.", ORANGE),
    ("Win-back", "The customer gone quiet", "No order in 60 or 90 days: a reason to come back, not only a discount.", BLUE),
    ("Measure", "Revenue, not opens", "Orders recovered per message sent; email open rates are inflated by privacy features.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "Klaviyo&rsquo;s 2026 benchmark of 110,000+ brands: <b>abandoned-cart messages earn more per person reached</b> than any other automation.", size=30),
  """One message per click.

Shopify's own messaging app includes automations such as abandoned checkout, welcome and win-back; third-party reviews (2026) say Shopify Messaging includes 10,000 emails a month free and that abandoned-checkout emails do not count against it. Check the current terms. WhatsApp reminders need an app and the shopper's consent.

Klaviyo's abandoned-cart benchmark (October 2026, 110,000+ customers): abandoned-cart flows have the highest average revenue per recipient of its automations, USD 6.77 by email and USD 4.48 by text on average, about twice that for the top 10% of brands.

Apple's Mail Privacy Protection (2021) pre-loads emails and inflates open rates, which is why recovered revenue is the measure.

Sources: Klaviyo, Abandoned cart benchmarks (2026); third-party reviews of Shopify Messaging (2026).""")

pnl = [("Order value, after a PKR 150 discount", "3,000"),
       ("Product cost", "&minus; 1,200"),
       ("Delivery", "&minus; 250"),
       ("Payment and cash-handling fees", "&minus; 90"),
       ("Refusals and returns, spread over every order", "&minus; 150"),
       ("Contribution before marketing", "1,310"),
       ("Marketing to win the order", "&minus; 800"),
       ("Contribution after marketing", "510")]
S["shp-profit"] = sec("shp-profit", "#f5f5f6", "Overlooked &middot; profit", "Track profit, not sales",
  trows(["One order", "PKR"], pnl, 262, [1180, 428], rh=62, size=25, head_size=20)
  + "\n" + band(9, 810, 90, "A PKR 3,000 sale can leave PKR 510. <b>Which of your products sells most &mdash; and which earns most?</b>", size=28),
  """One line per click. The numbers are illustrative.

The order's contribution is what is left after the product, delivery, payment fees, the share of refused and returned parcels and, after marketing, the cost of winning the order. A best-seller with deep discounts, heavy refusals or expensive ads can earn less than a quieter product.

Shopify's profit reports show gross profit by product once a cost per item is entered on each product (third-party sources say the reports need the Shopify plan or above, and that costs entered later do not change past sales). They do not subtract delivery, payment fees, refusals or ads: those need a spreadsheet or a profit app.

Sources: Shopify Help Center, Profit reports; Shopify changelog, Product cost and profit reporting.""",
  footer=ILL)

S["shp-case-overlooked"] = cases("shp-case-overlooked", "Cases &middot; the quiet money", "Speed and the second visit",
  ("Pakistan", "Bonanza Satrangi", "Fashion, 2020&ndash;", [
    ("The switch", "Moved to Shopify Plus after slowdowns in sales; conversion up 3&ndash;4 points within a day, its e-commerce head said."),
    ("The second visit", "Web push to 600,000+ subscribers: 7.9% of all orders, the app&rsquo;s case study reports.")]),
  ("Global", "Rakuten 24", "Online store, Japan", [
    ("The test", "Two identical versions of its pages; one tuned for Core Web Vitals."),
    ("The result", "Revenue per visitor up 53%, conversion up 33%, exits down 35%, web.dev reports.")]),
  "Neither bought more traffic. <b>Both earned more from the visitors they already had.</b>",
  """Two cases.

Bonanza Satrangi: Profit (Pakistan Today, November 2020) reported the move from Magento to Shopify Plus with the agency Shopistan, after slow changes and server slowdowns during seasonal sales; the brand's head of e-commerce said onsite conversion rose three to four percentage points within a day. PushOwl's case study (vendor-reported) gives 600,000+ web-push subscribers, 7.9% of all store orders attributed to web push and 46% of those from first-time customers.

Rakuten 24: web.dev's case study reports an A/B test of identical-looking pages, one optimised for Core Web Vitals: revenue per visitor up 53.37%, conversion rate up 33.13%, average order value up 15.20% and exit rate down 35.12%.

Sources: Profit by Pakistan Today (13 Nov 2020); PushOwl case study, Bonanza Satrangi; web.dev, Rakuten 24 case study.""",
  "Sources: Profit by Pakistan Today (Nov 2020); PushOwl; web.dev, Rakuten 24")

# --- Part 4 - For developers ------------------------------------------------------------------

S["shp-part4"] = div("shp-part4", "Part 4 &middot; For developers", "Under<br>the hood",
  "Five moves for whoever writes the code: pages, content, rules, checkout logic and integrations.",
  """Part 4 shows what Part 2 looks like in code. The snippets are short examples to read, not to copy into a live store untested. About 40 minutes.""")

S["shp-dev-pages"] = sec("shp-dev-pages", "#ffffff", "Developers &middot; 1", "Dynamic product pages",
  code(1, 128, 290, 1010, 560, "Liquid, in a product section", [
    "{% assign skin = product.metafields.custom.skin_type %}",
    "{% if skin != blank %}",
    "  <p class=\"fit\">For {{ skin.value | join: ', ' }} skin</p>",
    "{% endif %}",
    "",
    "{% comment %} Prices are in paisa: 270000 = Rs 2,700 {% endcomment %}",
    "{% if product.price >= 270000 %}",
    "  <p class=\"badge\">Free delivery on this one</p>",
    "{% endif %}"], size=23)
  + "\n" + side([("One template", "Not one page per product", "The same section serves the whole range.", RED),
                 ("Fields", "Facts from metafields", "The page shows what each product&rsquo;s fields say.", ORANGE),
                 ("Rules", "Logic in Liquid", "Badges and notes appear only where they apply.", BLUE)], 2),
  """The code first, then one card per click.

Liquid reads metafields as product.metafields.namespace.key, with .value for the typed value (a list of skin types here). Money values in Liquid are in the currency's smallest unit, so PKR 2,700 is 270000; forgetting this is the commonest Liquid price bug.

The point for founders: one template plus good product data replaces dozens of hand-built pages.""")

S["shp-dev-content"] = sec("shp-dev-content", "#f5f5f6", "Developers &middot; 2", "Reusable content systems",
  code(1, 128, 290, 1010, 560, "A metaobject, read in Liquid", [
    "{% comment %} Definition 'ingredient': name, what_it_does,",
    "   best_for, image. Products hold a list of them in",
    "   product.metafields.custom.key_ingredients {% endcomment %}",
    "",
    "{% for ing in product.metafields.custom.key_ingredients.value %}",
    "  <h4>{{ ing.name }}</h4>",
    "  <p>{{ ing.what_it_does }}</p>",
    "{% endfor %}"], size=23)
  + "\n" + side([("Once", "One entry per ingredient", "Written and approved once by the person who knows it.", RED),
                 ("Linked", "Products point to entries", "A product lists its ingredients; the page shows each.", ORANGE),
                 ("Everywhere", "One change, every page", "Edit the entry and every product that uses it updates.", BLUE)], 2),
  """The code first, then one card per click.

A product metafield of type 'list of metaobject references' links a product to entries; the loop reads each entry's fields. The same entries can feed a glossary page, a size guide or a landing section. Limits: up to 40 fields per definition and 1,000,000 entries per definition (Shopify developer docs, October 2025).

The official guide: Shopify Help Center, Metaobjects; shopify.dev, Custom data.""")

S["shp-dev-flow"] = sec("shp-dev-flow", "#ffffff", "Developers &middot; 3", "Automated business rules",
  grid([
    ("1 &middot; When", "Order created", "The trigger: every new order starts the workflow.", RED),
    ("2 &middot; If", "COD, first order, large", "Payment is cash on delivery, the customer&rsquo;s first order, over PKR 10,000.", ORANGE),
    ("3 &middot; Then", "Tag and hold", "Tag &lsquo;confirm&rsquo; and hold fulfilment until it is confirmed.", BLUE),
    ("4 &middot; And", "Tell another system", "Send the order to a WhatsApp confirmation app, or by HTTP request.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "Interline, a furniture retailer, uses Flow for refunds, commissions, staff discounts and out-of-stock tags: <b>about an hour a day saved on refunds alone</b>, Shopify reports.", size=29),
  """One step per click. The threshold is an example.

A Flow workflow has one trigger, then conditions and actions, which can branch and run in sequence; apps add their own triggers and actions (WhatsApp, courier and review apps among them). The HTTP-request action reaches any outside system that accepts one; third-party guides say it needs a plan above Basic.

Interline: Shopify's case study describes Flow automations for refund reporting, commission tracking, employee discounts, tagging out-of-stock products and publishing discontinued ones, saving about an hour a day on refunds (hundreds of hours a year). Vendor-reported.

Sources: Shopify Flow app; Shopify case study, Interline.""")

S["shp-dev-functions"] = sec("shp-dev-functions", "#f5f5f6", "Developers &middot; 4", "Custom commerce logic",
  grid([
    ("Language", "Rust or JavaScript", "Compiled to WebAssembly and run by Shopify inside its checkout.", RED),
    ("Discount", "A tiered discount", "5% off two, 10% off three, in one function instead of three discounts.", ORANGE),
    ("Payment", "COD by rule", "Hide cash on delivery above PKR 25,000 or for a tagged customer.", BLUE),
    ("Validation", "A sale-day limit", "No more than three units of one product per order during a sale.", GREEN),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "Functions must be small and fast, because they run on every checkout. <b>Custom ones need Plus; apps bring them to every plan.</b>", size=30),
  """One card per click. The values are examples.

Shopify Functions are written in Rust (Shopify's recommended language) or JavaScript, compiled to WebAssembly, and run by Shopify with strict limits on size and run time. Each function implements one Function API: discounts, delivery customisation, payment customisation, cart and checkout validation, cart transforms and others; a few are limited to Plus. They replace Shopify Scripts, which stopped running on 30 June 2026.

Sources: shopify.dev, About Shopify Functions; shopify.dev, Function APIs reference.""")

S["shp-dev-integrate"] = sec("shp-dev-integrate", "#ffffff", "Developers &middot; 5", "External system integration",
  code(1, 128, 290, 1010, 560, "Webhook topics a store subscribes to", [
    "orders/create      ->  courier booking, ERP sales order",
    "orders/paid        ->  finance: cash received",
    "fulfillments/create  ->  WhatsApp: your parcel is on its way",
    "inventory_levels/update  ->  POS and marketplace stock",
    "",
    "Back the other way, through the GraphQL Admin API:",
    "  tracking numbers, stock counts, prices"], size=24)
  + "\n" + side([("Verify", "Check the signature", "Every webhook carries an HMAC header: reject any that fail.", RED),
                 ("Repeat-safe", "The same event twice", "Webhooks can arrive twice or out of order: process each once.", ORANGE),
                 ("Patient", "Respect the limits", "The API rations requests: queue them and back off.", BLUE)], 2),
  """The topics first, then one rule per click.

Shopify signs each webhook with an HMAC (the X-Shopify-Hmac-SHA256 header) that the receiving app checks with its secret; Shopify may deliver a webhook more than once and not always in order, so receivers store the event id and ignore repeats. The GraphQL Admin API has rate limits measured in query cost, so integrations queue and retry.

Off-the-shelf connectors (couriers, Candela, marketplaces) do this for you; build your own only when no connector fits.

Sources: shopify.dev, Webhooks; shopify.dev, API rate limits.""")

learn = [("1", "Conversion basics", "Bundles, the delivery bar, checkout, speed", "No code"),
         ("2", "Liquid and metafields", "Dynamic product pages and badges", "Theme code"),
         ("3", "Automation", "Flow workflows from templates, then your own", "No code"),
         ("4", "APIs and webhooks", "Couriers, POS and analytics, linked", "An app"),
         ("5", "Custom checkout logic", "Discount, delivery and payment functions", "An app, or Plus")]
S["shp-learn"] = sec("shp-learn", "#f5f5f6", "Developers &middot; where to start", "What to learn first",
  trows(["Step", "Learn", "First project", "Needs"], learn, 262, [140, 520, 640, 308], rh=88, size=26, head_size=20)
  + "\n" + band(6, 790, 110, "Each step pays for the next. <b>Which step is your store on now?</b>", size=30),
  """One step per click. The order is the instructor's note's recommendation: conversion first, because it pays on the traffic the store already has; custom checkout logic last, because it needs the most skill and, for custom functions, the Plus plan.""")

# --- Exercise and the simulation ------------------------------------------------------------------

S["shp-ex2"] = exercise("shp-ex2", "Exercise", "Fix one store",
  "A Lahore skincare store: typical basket PKR 2,200, delivery PKR 250 a parcel, 50% gross margin, 85% of orders cash on delivery, 22% refused, home page 6 seconds on a phone, nine apps.",
  ["Which three moves first, and why those?", "Where would you set the delivery bar?",
   "Which Flow rule would you write first?", "Which number shows it worked, a month on?"],
  "Exercise &middot; illustrative store, not market data",
  """Twelve minutes in teams, then two teams report. One question per click. The store is invented; the numbers are illustrative.

Strong answers: confirm cash-on-delivery orders before dispatch (22% refusals cost delivery twice), fix the home page (six seconds on mobile), and set the bar near PKR 2,700 (typical basket plus delivery divided by margin). The first Flow: tag first-time cash-on-delivery orders above a value for confirmation. The measure: refusal rate and contribution per order, not sales.""",
  top=540, h=170, cols=2)

S["shp-part5"] = div("shp-part5", "Part 5 &middot; The simulation", "The moves in<br>the simulation",
  "Which of these moves your team can make in months 10 to 12, and how the simulation counts them.",
  """Part 5 maps the workshop onto the simulation's decisions. Every rule on the next slides is the simulation's assumption, not market data. About 10 minutes.""")

simmap = [("Bundles", "1.2 bundles", "Up to three three-packs; about 5% off earns most, past about 12% a pack loses money"),
          ("Quantity breaks", "Not modelled", "Discounts are set product by product in 1.1"),
          ("Free-delivery bar", "2.4 threshold", "Just above a typical basket lifts baskets; free on everything: +4% conversion, &minus;3% basket"),
          ("Checkout and speed", "5.1 website", "Closes part of the gap to your store&rsquo;s best, from the next month"),
          ("COD control", "9.1 COD &middot; 9.2 prepaid discount", "Fewer refusals against fewer orders, paid for in margin"),
          ("Recovery", "6.1 CRM and retention", "Fewer customers lost, more repeat orders"),
          ("Personalisation", "11.1 recommendations", "Average order about 7% higher once live, after a two-month build"),
          ("Flow, Liquid, Functions, APIs", "Not modelled", "Their effect is part of what 5.1 buys")]
S["shp-sim-map"] = sec("shp-sim-map", "#ffffff", "In the simulation", "The workshop in the simulation",
  trows(["Real move", "Decision", "How the simulation treats it"], simmap, 262, [430, 430, 748], rh=74, size=23, head_size=19),
  """One row per click. These are the simulation's rules (docs/01, the decision list), not market data.

1.2: uptake follows the saving against three singles; the saving is given away on every pack unit, so a small saving (about 5%) earns most and past about 12% a pack loses money. 2.4: free delivery on everything lifts conversion 4% and shrinks baskets 3%; a bar up to half a basket above a typical order lifts basket size; beyond that small buyers walk away; items added to reach the bar carry their cost of goods. 5.1: each month's spend closes part of the gap to the tech stack's ceiling (half the gap at PKR 300,000), and the gain lands the following month. 11.1: PKR 3,000,000 to build, two months, 85% chance of working, PKR 250,000 a month to run.""",
  footer="Decision rules from the simulation &middot; not market data")

S["shp-sim-now"] = sec("shp-sim-now", "#fdeceb", "Months 10 to 12", "Four questions before you decide",
  grid([
    ("Bundles", "Is your saving near 5%?", "Deeper savings give margin away on packs people would have bought anyway.", RED),
    ("Delivery bar", "Is it just above your basket?", "Check your average order in the report against your threshold.", ORANGE),
    ("Website", "Will the spend land in time?", "5.1 works from the next month: month 12&rsquo;s spend lands after the game ends.", BLUE),
    ("Cash on delivery", "Is the prepaid discount paying?", "Compare refusals and margin before and after you changed it.", GREEN),
  ], 4, 300, 380, bsize=24)
  + "\n" + band(5, 720, 150, "Say in the board memo <b>which move you made, and which number in next month&rsquo;s report should show it.</b>", size=30),
  """One question per click, while teams look at their latest report.

The website point is the simulation's timing rule: 5.1 improves the store the month after the spend, and the final scorecard does not read the website score, so website spend in month 12 is a cost with no return inside the game.

Logistics for the notes, not the slide: decisions for the open month close at [deadline].""",
  footer="Decision rules from the simulation &middot; not market data")

S["shp-close"] = sec("shp-close", "#131316", "To take away", "One rule behind every move",
  grid([
    ("Sell more", "Per visit", "Bundles, tiers and a delivery bar that pay for themselves; a checkout with no surprises.", "#ff3b3b"),
    ("Do less", "By hand", "Fields, content, workflows and connections that follow the rule every time.", "#ff3b3b"),
    ("Know more", "Per order", "What each order earns after delivery, fees, refusals and ads.", "#ff3b3b"),
  ], 3, 300, 300, bg="#1f1f24", border="border:1px solid #33333b;", tcol="#ffffff", bcol="#c9c9d1")
  + "\n" + band(4, 660, 150, "Change one thing, measure it against the last, and keep what pays. <b>Which one will your store change first?</b>", bg="#ed0000", size=31),
  """Close. One card per click.

Come back to the opening answers: which of the moves would have kept you in the store you nearly left?""", dark=True, eyecol="#ff3b3b")

ORDER = ["shp-cover", "shp-ex1", "shp-map",
         "shp-part1", "shp-bundles", "shp-quantity", "shp-basket-math", "shp-threshold", "shp-threshold-math",
         "shp-checkout", "shp-checkout-pk", "shp-case-sales",
         "shp-part2", "shp-tech-map", "shp-metafields", "shp-metaobjects", "shp-flow", "shp-liquid",
         "shp-functions", "shp-apis", "shp-case-tech",
         "shp-part3", "shp-personal", "shp-speed", "shp-recovery", "shp-profit", "shp-case-overlooked",
         "shp-part4", "shp-dev-pages", "shp-dev-content", "shp-dev-flow", "shp-dev-functions", "shp-dev-integrate",
         "shp-learn",
         "shp-ex2", "shp-part5", "shp-sim-map", "shp-sim-now", "shp-close"]
SECTIONS = {
    "shp-open": {"description": "Advanced Shopify · the store you nearly left, and four kinds of move", "start": "shp-cover"},
    "shp-sales": {"description": "Part 1 · Sell more per visit: bundles, quantity breaks, the delivery bar, checkout", "start": "shp-part1"},
    "shp-tech": {"description": "Part 2 · Build more into the store: metafields, metaobjects, Flow, Liquid, Functions, APIs", "start": "shp-part2"},
    "shp-overlooked": {"description": "Part 3 · What most stores overlook: personalisation, speed, recovery, profit", "start": "shp-part3"},
    "shp-dev": {"description": "Part 4 · For developers: pages, content, rules, checkout logic, integrations", "start": "shp-part4"},
    "shp-apply": {"description": "The exercise, Part 5 · the simulation, and the close", "start": "shp-ex2"}}

if __name__ == "__main__":
    write(S, ORDER, "Advanced Shopify — Tricks that Pay", SECTIONS)
