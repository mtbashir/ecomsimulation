"""The founder's cost sheet - what selling online costs in Pakistan. About 35 slides.

Run: python costs_slides.py <deck folder> [logo url]
For Pakistani founders starting an online business: the store, payment
gateways, couriers, ads, marketplaces (Daraz, abroad, Airbnb), every fee also
shown in rupees on one PKR 3,000 order, then the simulation's versions of the
same costs. Rates were published or reported between August and November 2026
and change often; most come from comparison guides rather than the providers'
own rate cards, so each slide says whose figure it is. Slide ids carry an
"fc-" prefix.
"""
import pathlib, sys, json
HERE = pathlib.Path(__file__).parent
exec((HERE / "s7_slides.py").read_text().split("\nS = {}\n")[0])
FT = "Founder&rsquo;s cost sheet &middot; Pakistan, November 2026"
ILL = "Illustrative arithmetic on the rates shown &middot; PKR, about 280 to the US$"
def sec(sid, bg, eyebrow, title, body, notes, footer=FT, **kw):
    return section(sid, bg, "#131316", eyebrow, title, body, notes, footer=footer, **kw)
def div(sid, part, title, line, notes):
    return divider(sid, part, title, line, notes).replace("Session 2 &middot; Finding the Right Idea", FT).replace("856d57cb939a323d46943b3b229572d7", "__LOGO__")

RED, ORANGE, BLUE, GREEN, BROWN, GREY = "#ed0000", "#eb6834", "#2a78d6", "#1baf7a", "#8a6414", "#55555f"


def gtrows(*a, **kw):
    """trows with a gutter: each cell keeps 22px clear on its right, so a
    full line in one column never runs into the next."""
    return trows(*a, **kw).replace('; color:#131316">', '; color:#131316; padding-right:22px">')


def num4(n, L, T, W, H, label, num, text):
    """A figure card for four across: the number set smaller, to fit a 396px column."""
    return f'''  <div data-build-in="fade {n}" style="position:absolute; left:{L}px; top:{T}px; width:{W}px; height:{H}px; background:#ffffff; padding:30px 30px; border-radius:18px; border:1px solid #e4e4e7; display:flex; flex-direction:column; gap:10px">
    <p style="font-size:21px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:#86868f">{label}</p>
    <p style="font-size:42px; font-weight:700; letter-spacing:-1px; line-height:1.1; color:#131316">{num}</p>
    <p style="font-size:23px; line-height:1.4; color:#55555f">{text}</p>
  </div>'''


def nums4(items, top, h, start=1, gap=26):
    w = (1664 - gap * 3) // 4
    return "\n".join(num4(start + i, 128 + i * (w + gap), top, w, h, *it) for i, it in enumerate(items))

S = {}

# --- Opening ---------------------------------------------------------------------------

S["fc-cover"] = cover("X", "The Founder&rsquo;s<br>Cost Sheet",
  "What a store, payments, delivery, ads and marketplaces cost a Pakistani founder &mdash; per order, in rupees.",
  """A reference deck for students who plan to start selling online in Pakistan. About 35 slides in six parts: 1 the store, 2 getting paid, 3 delivery, 4 ads, 5 marketplaces (Daraz, abroad, Airbnb), 6 putting it together; then the simulation's versions of the same costs.

Every rate was published or reported between August and November 2026. Most come from Pakistani comparison guides and agencies rather than the providers' own rate cards, which are often behind a login or negotiated; each slide names whose figure it is, and where sources disagree it shows the range. Rates change every few months and are negotiable with volume: they are for planning, and a founder should get each provider's rate card in writing before signing.

About two hours with the exercise; Parts 2 and 3 (payments and delivery) are the core if time is short.

Exchange rate used for US$ prices: about PKR 280 to the dollar (2026 guides quote 278-281).""",
  size=124).replace('id="cover"', 'id="fc-cover"').replace("Session X of 12", "Founder&rsquo;s toolkit &middot; Pakistan")

S["fc-ex1"] = exercise("fc-ex1", "Opening question", "Your first hundred orders",
  "A PKR 3,000 product, sold online from Lahore to customers across Pakistan.",
  ["Which costs come out of each order before the money reaches you?",
   "Which would you still pay if the parcel came back?",
   "Where would you sell first: your own site, Daraz or Instagram?",
   "How much would you spend before the first order arrives?"],
  "Opening question",
  """Eight minutes: two alone, then the room. One question per click.

Write the room's guesses for the per-order costs on one side; Part 6 puts real rates against them. Most rooms forget the tax withheld on every order (Finance Act 2025, section 6A) and the cost of a refused cash-on-delivery parcel.""",
  top=500, h=180, cols=2)

S["fc-map"] = sec("fc-map", "#ffffff", "The cost sheet", "Five bills on every order",
  grid([
    ("Store", "Where you sell", "A platform fee, a domain, apps &mdash; or a marketplace that charges per order instead.", RED),
    ("Payment", "How you are paid", "A gateway&rsquo;s % per transaction, or the courier&rsquo;s fee for collecting cash.", ORANGE),
    ("Delivery", "How it arrives", "A rate per parcel by weight and city, plus the cash-on-delivery fee and returns.", BLUE),
    ("Ads", "How they find you", "A price per click or per 1,000 views on Meta, Google and TikTok.", GREEN),
    ("Tax", "What is withheld", "1% of digital payments and 2% of cash-on-delivery orders, taken before you are paid.", BROWN),
  ], 5, 290, 400, bsize=23, tsize=28)
  + "\n" + band(6, 740, 130, "Every rate here was published or reported in Aug&ndash;Nov 2026, and most are negotiable. <b>Plan with them; sign on a written quote.</b>", size=29),
  """One bill per click.

The tax line: section 6A of the Income Tax Ordinance, added by the Finance Act 2025, withholds tax on payments for goods ordered online: 1% when the buyer pays digitally (collected by the payment intermediary) and 2% on cash on delivery (collected by the courier), in force from August 2025 (SRO 1429(I)/2025). The Finance Act 2026 made it adjustable for sellers with turnover above Rs 200 million and lets smaller sellers opt out of the final-tax regime from tax year 2027, according to Crowe's 2026 tax handbook. A founder should confirm the current treatment with a tax adviser.

Sources: FBR Circular 01 of 2025-26; KPMG, A Brief on Finance Act 2025; Crowe, Finance Act Tax Handbook 2026.""")

# --- Part 1 - The store -----------------------------------------------------------------

S["fc-part1"] = div("fc-part1", "Part 1 &middot; Your store", "What a store<br>costs to build",
  "From a free Instagram shop to a custom build: what each costs up front and every month.",
  """Part 1 is the shop window. About 20 minutes.""")

stores = [("Instagram + WhatsApp Business", "PKR 0", "PKR 0, ads aside", "Testing a product"),
          ("Daraz shop", "Free to open", "Commission on each order (Part 5)", "Shoppers who search Daraz"),
          ("Shopify Basic", "Free themes; set it up yourself", "US$29 billed yearly or US$39 monthly, and 2% of gateway orders", "Most first stores"),
          ("WordPress + WooCommerce", "PKR 50k&ndash;150k (freelancer)", "Hosting and plugins PKR 2k&ndash;15k", "Full control, own upkeep"),
          ("Custom build", "PKR 300k&ndash;1.2M", "Maintenance contract", "Unusual needs")]
S["fc-store-options"] = sec("fc-store-options", "#f5f5f6", "The store", "Five ways to open a store",
  gtrows(["Option", "Up front", "Every month", "Best for"], stores, 262, [400, 360, 520, 328], rh=88, size=23, head_size=19)
  + "\n" + band(6, 770, 120, "Start where the cost of being wrong is lowest. <b>Which of your assumptions does a PKR 0 test check first?</b>", size=29),
  """One option per click.

Shopify: US$29 a month billed yearly or US$39 billed monthly for Basic, as Pakera read Shopify's Pakistan pricing page on 9 October 2026; other Pakistani guides quote US$19-25 for earlier dates, so check shopify.com/pk/pricing on the day. The 2% applies to card and wallet orders paid through an outside gateway (next slides).

WooCommerce: freelancers PKR 50,000-150,000 and agencies PKR 100,000-400,000+ (WebBazaar, 2026); a store on a ready theme PKR 80,000-350,000 in 3-6 weeks (Ezitech); hosting and plugins PKR 2,000-15,000 a month (Progriso).

Custom: PKR 300,000-1,000,000 (Ezitech) to 1,200,000 (Syed Faraz Corp), agency figures.

Sources: Pakera (Oct 2026); WebBazaar; Ezitech; Progriso; Syed Faraz Corp (2026).""",
  footer="Sources: Shopify Pakistan pricing via Pakera (9 Oct 2026); WebBazaar, Ezitech, Progriso (2026)")

S["fc-shopify"] = sec("fc-shopify", "#ffffff", "The store &middot; Shopify", "Shopify, in rupees",
  grid([
    ("Plan", "PKR 8,100&ndash;10,900 a month", "Basic: US$29 billed yearly or US$39 monthly, paid in dollars by card.", RED),
    ("The 2%", "On every gateway order", "No Shopify Payments in Pakistan: 2% on Basic, 1% Grow, 0.6% Advanced. Cash on delivery: none.", ORANGE),
    ("Themes and apps", "Free to start", "Free themes are enough; paid themes and apps are extra, mostly monthly in US$.", BLUE),
    ("Card tax", "0.5% for filers", "Paying Shopify by card abroad: advance tax 0.5% (filers) or 1% (non-filers) from July 2026.", GREEN),
  ], 4, 290, 400, bsize=23)
  + "\n" + band(5, 740, 130, "On a PKR 3,000 card order, Basic&rsquo;s 2% is <b>PKR 60</b> &mdash; more than a Raast payment costs at the gateway.", size=30),
  """One line per click.

Plan: US$29 x 280 = PKR 8,120; US$39 x 280 = PKR 10,920. Third-party transaction fees: Shopify charges them when an order is paid through a provider other than Shopify Payments, which Pakistan-based businesses cannot use; Pakistani guides report that manual payment methods such as cash on delivery carry no Shopify fee (confirm in Shopify's help centre).

Card tax: section 236Y advance tax on payments abroad by Pakistani cards, cut by the Finance Act 2026 to 0.5% for filers and 1% for non-filers from 5% and 10%, according to tax guides (TaxBuddy, ezInvoice); confirm with your bank.

Sources: Pakera, BSS Commerce, Avada (Shopify pricing in Pakistan, 2026); TaxBuddy Umair, Section 236Y (2026).""",
  footer="Sources: Shopify Pakistan pricing via Pakera; Pakistani Shopify guides; s.236Y guides (2026)")

S["fc-woo"] = sec("fc-woo", "#f5f5f6", "The store &middot; WordPress", "WooCommerce, in rupees",
  grid([
    ("Software", "Free", "WordPress and the WooCommerce plugin cost nothing; no 2% on payments.", RED),
    ("Hosting", "PKR 340&ndash;2,000 a month", "Local shared plans listed from about PKR 340; Hostinger from about PKR 550 on a 48-month plan.", ORANGE),
    ("Build", "PKR 50k&ndash;350k", "Freelancer PKR 50k&ndash;150k; an agency store on a ready theme PKR 80k&ndash;350k, 3&ndash;6 weeks.", BLUE),
    ("Upkeep", "Your job", "Updates, security, backups and a fast server: someone must own them.", GREEN),
  ], 4, 290, 400, bsize=23)
  + "\n" + band(5, 740, 130, "No platform fee and no 2% &mdash; <b>but you are the IT department.</b> Who in your team is?", size=30),
  """One line per click.

Hosting: MiddleHost from PKR 338 a month; Pakish Basic PKR 375 a month and a Business Store plan PKR 1,999; Superhost PKR 850; Hostinger about PKR 550 a month on its 48-month plan (DEV Community guide). Introductory prices often rise at renewal.

Build: WebBazaar (freelancer PKR 50,000-150,000; agency PKR 100,000-400,000+); Ezitech (ready theme PKR 80,000-350,000, 3-6 weeks). Over two to three years, Ezitech notes, Shopify and WooCommerce often cost about the same once hosting and upkeep are counted.

Sources: web hosting listings (MiddleHost, Pakish, Superhost, 2026); WebBazaar; Ezitech.""",
  footer="Sources: Pakistani hosting listings; WebBazaar; Ezitech (2026)")

S["fc-domain"] = sec("fc-domain", "#ffffff", "The store &middot; name and trust", "A name, and the pages that win trust",
  grid([
    (".pk domain", "Rs 2,100 a year", "PKNIC&rsquo;s price from 1 August 2026, billed two years at a time: Rs 4,200. Resellers add a margin.", RED),
    (".com domain", "About PKR 3,500 a year", "One Pakistani registrar lists PKR 3,470, renewing at PKR 3,940.", ORANGE),
    ("Trust pages", "Free, and required", "Refund, privacy and delivery policies, contact details and SSL: gateways check them before approving you.", BLUE),
  ], 3, 290, 380, bsize=24)
  + "\n" + band(4, 720, 150, "A gateway will not approve a store without a refund policy. <b>What does yours promise on a damaged parcel?</b>", size=30),
  """One item per click.

.pk: PKNIC raised its price by Rs 300 to Rs 2,100 per domain per year on 1 August 2026 (Pakera); registrations are billed for two years (Digiteazy). .com: HosterPK lists PKR 3,470 a year, renewal PKR 3,940.

Trust pages: gateways commonly require a live website with visible refund and privacy policies and an SSL certificate (Rapid Gateway's merchant-account guide); names on the NTN, CNIC and bank account should match, the commonest cause of delay.

Sources: Pakera (.pk, Aug 2026); Digiteazy; HosterPK; Rapid Gateway (2026).""",
  footer="Sources: Pakera, Digiteazy (.pk 2026); HosterPK; Rapid Gateway")

S["fc-first-year"] = sec("fc-first-year", "#f5f5f6", "The store &middot; the sum", "A first year&rsquo;s store bill",
  row3([("Instagram + WhatsApp", "PKR 0", "A phone, good photos and a WhatsApp Business catalogue; ads are separate."),
        ("Shopify Basic", "&asymp; PKR 100,000", "US$348 for a year&rsquo;s plan, plus a domain; and 2% of card and wallet sales."),
        ("WooCommerce", "PKR 58k&ndash;178k", "A freelancer&rsquo;s build, a year of hosting and a .com domain; no 2%.")], 290, 400)
  + "\n" + band(4, 730, 150, "Shopify&rsquo;s 2% grows with your sales; WooCommerce&rsquo;s upkeep does not. <b>At what sales does the 2% cost more than a developer?</b>", size=29),
  """One option per click. Illustrative arithmetic on the rates of the last three slides.

Shopify Basic billed yearly: US$29 x 12 = US$348 x 280 = PKR 97,440, plus a .com at about PKR 3,470: about PKR 100,000, before paid themes or apps.

WooCommerce: build PKR 50,000-150,000 + hosting PKR 340-2,000 x 12 (PKR 4,080-24,000) + .com PKR 3,470 = PKR 57,550-177,470.

The question: the 2% applies only to gateway orders. On PKR 500,000 a month of card and wallet sales it is PKR 10,000 a month, about what a part-time developer or a managed host costs.""",
  footer=ILL)

# --- Part 2 - Getting paid ------------------------------------------------------------------

S["fc-part2"] = div("fc-part2", "Part 2 &middot; Getting paid", "Gateways,<br>wallets and Raast",
  "How Pakistanis pay online, what each gateway charges per transaction, and the terms to read.",
  """Part 2 is the money in. About 25 minutes.""")

S["fc-pay-how"] = sec("fc-pay-how", "#ffffff", "Getting paid", "How Pakistanis pay online",
  grid([
    ("Cash on delivery", "Most orders", "The courier collects cash, keeps a fee of about 1&ndash;2.5% and pays you days later.", RED),
    ("Cards", "About 2.9&ndash;3.5%", "Debit and credit cards through a gateway: the dearest way to be paid.", ORANGE),
    ("Wallets", "About 1.5&ndash;2.2%", "JazzCash and Easypaisa, in the app or by a payment link.", BLUE),
    ("Raast", "0&ndash;1%", "Instant bank-to-bank by QR or request: free at the bank; gateways charge for the checkout.", GREEN),
  ], 4, 290, 400, bsize=23)
  + "\n" + band(5, 740, 130, "Tax withheld: <b>1% of a digital payment, 2% of a cash-on-delivery order</b> &mdash; one more reason to make paying online worth it.", size=29),
  """One method per click.

Cash on delivery: nearly 70% of Pakistani online shoppers prefer it (DHL Pakistan); payment companies' blogs put COD's share of orders higher. Courier COD fees: Part 3.

Raast: Bank Alfalah's merchant guide states 0% MDR on the Raast scheme with T+1 settlement; SBP's P2M instructions say customers are not charged. Gateways and platforms may charge for what they add (dynamic QR, links, reconciliation): PayFast lists 0.60% for Raast QR and 0.95% for Raast request-to-pay.

Tax: section 6A (Finance Act 2025).

Sources: DHL Discover Pakistan; Bank Alfalah, Raast P2M merchant guide; PayFast pricing; FBR Circular 01 of 2025-26.""",
  footer="Sources: DHL Pakistan; Bank Alfalah Raast P2M; PayFast pricing; FBR (s.6A)")

gws = [("PayFast", "2.95% local; 3.50% international", "2.20%", "0.60% QR; 0.95% request", "2&ndash;3 working days"),
       ("Safepay", "2.9% + Rs 30", "1.5% (one review)", "1.5% (one review)", "Instant payout for 1.5%"),
       ("JazzCash (direct)", "&mdash;", "About 1.5&ndash;2%, negotiated", "&mdash;", "Next working day, reported"),
       ("Easypaisa (direct)", "&mdash;", "About 1.5&ndash;2%, negotiated", "&mdash;", "Set in the agreement"),
       ("XPay (PostEx)", "&ldquo;From 0.3%&rdquo; on Shopify &mdash; ask what is included", "", "", ""),
       ("Your bank&rsquo;s gateway", "Negotiated", "&mdash;", "0% at Bank Alfalah", "Next working day (Raast)")]
S["fc-gateways"] = sec("fc-gateways", "#f5f5f6", "Getting paid &middot; gateways", "What each gateway charges",
  gtrows(["Gateway", "Cards", "Wallets / bank", "Raast", "Pays you"], gws, 262,
        [330, 440, 330, 268, 240], rh=86, size=22, head_size=18),
  """One gateway per click. Rates are per successful transaction and exclude the tax on the fee.

PayFast: its pricing page lists 0.60% Raast QR, 0.95% Raast request-to-pay, 2.20% bank accounts and wallets, 2.95% local cards, 3.50% international cards; its FAQ says no set-up or maintenance fee and settlement 2-3 working days (a partner guide on Scribd lists a PKR 20,000 set-up charge: ask).

Safepay: 2.9% + Rs 30 on domestic cards in several guides (one lists international at 3.2% + Rs 30); 1.5% for wallets and Raast, a Rs 3,000 fee per card dispute and 1.5% for instant payouts in one review (PaymentPop). No set-up or monthly fee on the standard plan, per guides.

JazzCash and Easypaisa direct: no official merchant rate card found; guides report about 1.5-2%, negotiated; aggregators such as Rapid Gateway charge 2% for wallets. JazzCash's circular: no MDR on a refund made the same day.

XPay by PostEx: its pricing page says "starting at 0.3% per transaction for Shopify"; other XStak material says pricing is quoted. Ask whether card-scheme costs are on top.

Banks: negotiated; usually need a registered business and a current account; Bank Alfalah states 0% MDR on Raast with T+1 settlement.

Sources: PayFast pricing and FAQ; Safepay via Extruct, AssanPay, PaymentPop (2026); Rapid Gateway; JazzCash circular (2026); XPay pricing page; Bank Alfalah.""",
  footer="Sources: PayFast pricing; Safepay via guides (2026); XPay pricing; Bank Alfalah; wallet rates reported, not published")

pay3k = [("Raast (PayFast 0.60%)", "18", "60", "30", "108"),
         ("Wallet (PayFast 2.20%)", "66", "60", "30", "156"),
         ("Local card (PayFast 2.95%)", "89", "60", "30", "179"),
         ("Card (Safepay 2.9% + Rs 30)", "117", "60", "30", "207"),
         ("Cash on delivery (courier 1&ndash;2.5%)", "30&ndash;75", "0", "60", "90&ndash;135")]
S["fc-pay-order"] = sec("fc-pay-order", "#ffffff", "Getting paid &middot; per order", "One PKR 3,000 order: what paying costs",
  gtrows(["How the customer pays", "Gateway or courier fee", "Shopify Basic 2%", "Tax withheld", "You give up"], pay3k, 262,
        [560, 300, 260, 230, 258], rh=80, size=24, head_size=18)
  + "\n" + band(6, 742, 140, "At the gateway, Raast costs a fifth of a card. <b>What would make your customers pay that way?</b>", size=30),
  """One way per click. Illustrative arithmetic on the rates of the last slide, in PKR; the delivery charge is extra in every row (Part 3).

The Shopify column applies only on Shopify Basic and only to gateway orders; on WooCommerce it is 0. Tax: 1% on digital payments, 2% on cash on delivery (section 6A). Sales tax on the gateway's fee is not included.

The question: a small discount for paying online (the simulation's decision 9.2), a faster dispatch for prepaid orders, or a Raast QR on the confirmation message are the usual answers.""",
  footer=ILL)

S["fc-pay-terms"] = sec("fc-pay-terms", "#f5f5f6", "Getting paid &middot; terms", "Read before you sign: gateway terms",
  grid([
    ("Documents", "What they ask for", "Sole owner: CNIC, NTN (free on FBR&rsquo;s IRIS) and an IBAN. Banks: a registered business.", RED),
    ("Website", "What they check", "A live store, refund and privacy policies, contact details and SSL.", ORANGE),
    ("Settlement", "When you are paid", "Days after the sale, weekends excluded; a faster payout often costs extra.", BLUE),
    ("Disputes", "Who pays a chargeback", "The merchant, usually, plus a fee: one review reports Rs 3,000 a dispute.", GREEN),
    ("Refunds", "Is the fee returned?", "Often not; JazzCash waives it on a refund made the same day.", BROWN),
    ("The small print", "Lines besides the %", "Tax on the fee, set-up or annual fees, minimum volumes, money held back.", GREY),
  ], 3, 290, 210, tsize=28, bsize=23)
  + "\n" + band(7, 770, 120, "Ask for the rate card in writing, <b>one line per payment method, with tax shown.</b>", size=30),
  """One term per click.

Documents: Rapid Gateway's merchant-account guide and terms: sole proprietors and freelancers need a CNIC, an FBR NTN certificate (free on IRIS) and Pakistani bank details; bank gateways generally expect a registered business with an NTN and a current account; a mismatch between the names on the NTN, CNIC and bank account is the commonest delay. PayPro also asks for a bank account maintenance certificate.

Disputes: Safepay, Rs 3,000 per card dispute (PaymentPop review). Refunds: JazzCash circular, no MDR if the merchant refunds the same day.

Sources: Rapid Gateway (2026); PayPro; PaymentPop; JazzCash circular (2026).""")

S["fc-pay-pick"] = sec("fc-pay-pick", "#ffffff", "Getting paid &middot; choosing", "Which way to be paid, when",
  grid([
    ("Starting out", "COD and one wallet", "Cash on delivery for strangers; a wallet or Raast link for people who already trust you.", RED),
    ("On Shopify", "A gateway with an app", "PayFast, Safepay and XPay have Shopify apps; remember the 2% on Basic.", ORANGE),
    ("Growing", "Add cards, then negotiate", "Compare settlement days and dispute terms, not only the %; rates fall with volume.", BLUE),
    ("Abroad", "Payoneer", "Marketplaces abroad pay Pakistani sellers through Payoneer, then to a rupee account.", GREEN),
  ], 4, 290, 400, bsize=23)
  + "\n" + band(5, 740, 130, "The cheapest payment is the one that does not come back. <b>Which method has the fewest refusals for you?</b>", size=30),
  """One stage per click.

Shopify apps: PayFast, Safepay and XPay by PostEx are among the gateways Pakistani Shopify stores use (Shopify App Store; XStak and Loop2Tech guides, 2026). Abroad: Amazon, Etsy and eBay pay Pakistan-based sellers through Payoneer (Part 5).

The band: a card or wallet payment is not refused at the door; a cash-on-delivery parcel can be, and costs delivery both ways.""")

# --- Part 3 - Delivery -----------------------------------------------------------------------

S["fc-part3"] = div("fc-part3", "Part 3 &middot; Delivery", "Couriers and<br>cash on delivery",
  "What a parcel costs to send, what collecting the cash costs, and when the money reaches you.",
  """Part 3 is the doorstep. About 25 minutes.""")

cours = [("TCS", "PKR 200&ndash;330 in the city", "1.5&ndash;2.5% (min PKR 75&ndash;100); 1&ndash;1.75% on contract", "7&ndash;14 working days"),
         ("Leopards", "PKR 170&ndash;220 in the city; 230&ndash;260 for 1 kg between cities", "About 1&ndash;2% (min about PKR 50)", "About 7 days (5 at volume) to 15"),
         ("PostEx", "From about PKR 190&ndash;230", "About 1.5&ndash;2.5%", "Upfront or next day; a fee for instant"),
         ("Trax", "About PKR 180&ndash;220", "About 2&ndash;3%", "Weekly or fortnightly"),
         ("M&amp;P, BlueEX, Call Courier", "On a tariff sheet", "On a tariff sheet", "7&ndash;14 days, reported"),
         ("Pakistan Post (UMS-COD)", "Rs 75 local, Rs 110 city to city, up to 250 g", "Published tariff", "&mdash;")]
S["fc-couriers"] = sec("fc-couriers", "#f5f5f6", "Delivery &middot; couriers", "What couriers charge for a small parcel",
  gtrows(["Courier", "0.5 kg parcel", "Cash-on-delivery fee", "Pays you in"], cours, 262,
        [400, 500, 450, 258], rh=86, size=22, head_size=18),
  """One courier per click. Approximate 2026 ranges for a 0.5 kg e-commerce parcel; most couriers do not publish fixed e-commerce rates, discount contracted accounts heavily and add fuel surcharge and GST.

TCS: no printed rate card; its online calculator puts 0.5 kg within Lahore or Karachi at about Rs 330 including fuel surcharge and GST (TrackMyOrder); other guides give PKR 200-250. COD: 1.5% in one guide; 2-2.5% retail with a PKR 75-100 minimum and 1-1.75% on corporate contracts in another. Payment: 7-14 working days.

Leopards: PKR 170-220 within a city for 0.5-1 kg and PKR 230-260 for 1 kg between major cities, often 5-15% cheaper than TCS on common slabs (ANOC, mid-2026); COD about 1-2% or a minimum of about PKR 50; payment about 7 days (5 at volume) to 10-15.

PostEx: rates by account (its calculator); guides report from PKR 190-230 per 0.5 kg and a COD fee of about 1.5-2.5%; known for paying COD upfront or within a day, with a financing fee for instant payment.

Trax: no public rate card; guides report PKR 180-220 per 0.5 kg and a 2-3% COD fee; remittance weekly or fortnightly (5 days in metro cities in one guide).

M&P, BlueEX and Call Courier: rates on request; payment 7-14 days reported.

Pakistan Post UMS-COD: walk-in Rs 75 local and Rs 110 city to city up to 250 g from 1 October 2026 (Pakera).

Sources: TrackMyOrder, ANOC, Hypeup, Clicks blog (2026); PostEx calculator; Pakera (Pakistan Post, Oct 2026).""",
  footer="Sources: TrackMyOrder, ANOC, Hypeup (2026); PostEx; Pakera (Pakistan Post) &middot; ranges reported, not rate cards")

S["fc-ship-order"] = sec("fc-ship-order", "#ffffff", "Delivery &middot; per order", "One PKR 3,000 cash order: what delivery costs",
  nums4([("The parcel", "PKR 170&ndash;330", "0.5 kg within a city, Leopards to TCS."),
        ("Collecting cash", "PKR 30&ndash;75", "The COD fee: 1&ndash;2.5% of PKR 3,000."),
        ("Tax withheld", "PKR 60", "2% of a cash-on-delivery order, by the courier."),
        ("In all", "PKR 260&ndash;465", "9&ndash;16% of the order, before the product.")], 290, 400)
  + "\n" + band(5, 730, 150, "A refused parcel costs the trip out <b>and the trip back</b>, and earns nothing. What does one refusal in ten do to these numbers?", size=30),
  """One cost per click. Illustrative arithmetic on the last slide's ranges.

The question: if one parcel in ten is refused, each delivered order also carries a tenth of a wasted delivery both ways - about PKR 35-65 more at these rates, if the return trip costs the same as the trip out (ask your courier what it charges).""",
  footer=ILL)

S["fc-ship-terms"] = sec("fc-ship-terms", "#f5f5f6", "Delivery &middot; terms", "Read before you sign: courier terms",
  grid([
    ("Weight", "Slabs and size", "Charged by weight slab &mdash; or by size if the box is big and light.", RED),
    ("Surcharges", "On top of the rate", "Fuel surcharge and GST are usually added to the quoted price.", ORANGE),
    ("COD fee", "How it is worked out", "A % of the cash collected, with a minimum per parcel.", BLUE),
    ("Returns", "A refused parcel", "What the trip back costs, and how many days it takes.", GREEN),
    ("Payment cycle", "Days to your bank", "Weekly, twice a week or next day &mdash; and the fee for faster.", BROWN),
    ("Claims", "Lost or damaged", "The limit of what they pay, the proof they need, the deadline.", GREY),
  ], 3, 290, 210, tsize=28, bsize=23)
  + "\n" + band(7, 770, 120, "Send ten test parcels with two or three couriers: <b>record days, refusals and payment dates.</b>", size=30),
  """One term per click.

The test is the one the ANOC comparison recommends: controlled test shipments through two or three shortlisted couriers, recording delivery days, remittance delay and returns, because published comparisons disagree and contracted rates differ from retail ones.

Source: ANOC, COD courier comparison (2026).""")

S["fc-ship-pick"] = sec("fc-ship-pick", "#ffffff", "Delivery &middot; choosing", "Choosing couriers",
  grid([
    ("One city first", "The cheapest slab", "Within-city rates are the lowest; start where you can also deliver yourself.", RED),
    ("Cash is tight", "Paid upfront", "Couriers that pay COD upfront or next day free cash for stock &mdash; at a fee.", ORANGE),
    ("Many cities", "Two couriers", "Each is stronger in some cities: split by where parcels arrive.", BLUE),
    ("Less typing", "Book from the store", "Shopify apps book TCS, Leopards, PostEx and Trax and bring tracking back.", GREEN),
  ], 4, 290, 400, bsize=23)
  + "\n" + band(5, 740, 130, "The cheapest courier is the one that delivers. <b>A failed delivery costs more than any rate saves.</b>", size=30),
  """One choice per click.

Many cities: national couriers can perform well in Lahore and Islamabad and worse in smaller cities, so track delivery success by courier and zone (Easysell guide, 2026). Shopify apps: Courierify (free, launched January 2026) books PostEx, Leopards, Trax, TCS and BlueEx parcels from the Shopify admin; couriers also offer their own apps.

Sources: Easysell (2026); Shopify App Store, Courierify.""")

# --- Part 4 - Ads ----------------------------------------------------------------------------

S["fc-part4"] = div("fc-part4", "Part 4 &middot; Ads", "What attention<br>costs",
  "What Meta, Google and TikTok charge in Pakistan, what PKR 10,000 buys, and how to pay for it.",
  """Part 4 is the traffic. About 20 minutes.""")

adrows = [("Meta (Facebook, Instagram)", "1,000 views, or a click", "1,000 views: PKR 150&ndash;1,100; a click: mostly PKR 5&ndash;50", "A small daily budget", "Shoppers not yet searching"),
          ("Google Search", "A click", "E-commerce: PKR 20&ndash;150 a click; up to PKR 800 in crowded categories", "None", "Shoppers already searching"),
          ("TikTok", "1,000 views", "PKR 150&ndash;500 (one guide) to US$4&ndash;8 (an agency)", "US$50 a day per campaign, US$20 per ad group", "Young audiences, video")]
S["fc-ads-rates"] = sec("fc-ads-rates", "#ffffff", "Ads &middot; rates", "What ads cost in Pakistan",
  gtrows(["Platform", "You pay for", "Reported price in Pakistan", "Minimum", "Good for"], adrows, 262,
        [310, 230, 500, 330, 238], rh=118, size=22, head_size=18)
  + "\n" + band(4, 700, 180, "Published rates for Pakistan disagree by three times or more. <b>Your own first PKR 10,000 is the only rate card that counts.</b>", size=30),
  """One platform per click. None of these platforms publishes a Pakistan rate card; these are agency and guide figures from 2026.

Meta: CPM PKR 150-600 (one guide), 200-800 (another), 280-1,100 (Siffar); in US$, Facebook US$0.80-1.50 and Instagram US$1.20-2.20 (Adligator). CPC: most guides PKR 5-50 for Facebook and Instagram traffic; Siffar reports PKR 140-422 for traffic campaigns.

Google: e-commerce CPC about PKR 20-150 (Marketist), apparel PKR 40-150 (Inclivo), PKR 20-800 across categories; small businesses PKR 20-80 (Searchformals, citing local agencies). No minimum budget.

TikTok: Ads Manager minimums of more than US$50 a day per campaign and US$20 a day per ad group (TikTok help centre, as cited by Kixmon) - about PKR 14,000 and 5,600. Pakistan CPM: PKR 150-500 (one guide) or US$4-8 (an agency, AT&R).

Sources: Siffar, Adligator, Adamigo (Meta, 2026); Marketist, Inclivo, Searchformals (Google, 2026); Kixmon, AT&R, WeProms (TikTok, 2026).""",
  footer="Sources: Siffar, Adligator (Meta); Marketist, Inclivo (Google); Kixmon, AT&amp;R (TikTok) &middot; 2026 guides, not platform rate cards")

S["fc-ads-10k"] = sec("fc-ads-10k", "#f5f5f6", "Ads &middot; per rupee", "What PKR 10,000 buys",
  row3([("Google Search", "67&ndash;500 clicks", "At PKR 20&ndash;150 a click: people already looking."),
        ("Meta", "9,000&ndash;67,000 views", "At PKR 150&ndash;1,100 per 1,000 views: people who may want it."),
        ("TikTok", "Under a day", "A campaign&rsquo;s minimum is US$50 a day &mdash; about PKR 14,000.")], 290, 400)
  + "\n" + band(4, 730, 150, "At 2&ndash;3% of visitors buying, <b>200 clicks are 4&ndash;6 orders.</b> What may one order cost you in ads and still leave a profit?", size=30),
  """One platform per click. Illustrative arithmetic on the last slide's ranges.

Conversion: a Pakistani agency reports e-commerce conversion rates of about 2-3.5% (WeProms, 2026), an agency figure. The question is the break-even cost per order: what is left of the order after product, delivery, payment and tax (Part 6) is the most an order can cost in ads.""",
  footer=ILL)

S["fc-ads-pay"] = sec("fc-ads-pay", "#ffffff", "Ads &middot; paying", "Paying for ads from Pakistan",
  grid([
    ("Card", "In dollars or rupees", "A debit or credit card enabled for international use, in the ad account.", RED),
    ("Card tax", "0.5% for filers", "Advance tax on card payments abroad from July 2026: 0.5% filers, 1% non-filers.", ORANGE),
    ("A local route", "Rupees to an agent", "Since May 2026 SBP lets Pakistani aggregators collect rupees and pay Google and Meta.", BLUE),
    ("Other lines", "Read the statement", "The bank&rsquo;s exchange rate, provincial sales tax on card fees, and the platform&rsquo;s invoice.", GREEN),
  ], 4, 290, 400, bsize=23)
  + "\n" + band(5, 740, 130, "Being a tax filer halves the card tax. <b>Is your NTN registered, and on the active taxpayer list?</b>", size=30),
  """One line per click.

Card tax: section 236Y advance tax on international card payments, reduced by the Finance Act 2026 to 0.5% for filers and 1% for non-filers from 5% and 10% (TaxBuddy Umair, ezInvoice, 2026). Some sources also report a provincial sales tax on card fees (16% in Punjab) and withholding on Google invoices; one Pakistani blog estimates the total overhead at 1-17%, an illustrative figure.

Local route: a State Bank rule of 22 May 2026 lets Pakistani aggregators collect rupees and pay Google, Meta, Microsoft or Oracle abroad (Pakera); check that a reseller is authorised before paying it.

Sources: TaxBuddy Umair, ezInvoice (s.236Y, 2026); Pakera (paying for ads from Pakistan, 2026); Orah Jewels blog.""",
  footer="Sources: s.236Y guides (Finance Act 2026); Pakera (SBP aggregator rule, May 2026)")

# --- Part 5 - Marketplaces ------------------------------------------------------------------

S["fc-part5"] = div("fc-part5", "Part 5 &middot; Marketplaces", "Selling where<br>shoppers already are",
  "Daraz step by step and what it keeps, other places to sell, selling abroad &mdash; and hosting on Airbnb.",
  """Part 5 is selling without a store of your own. About 25 minutes.""")

daraz = [("1 &middot; Sign up", "Seller Center, with your phone number; then an email, and pickup and return addresses"),
         ("2 &middot; Documents", "Individual: CNIC front and back, and a cheque or statement showing your IBAN. Company: business registration and a bank document"),
         ("3 &middot; Approval", "Daraz approves the store; then you add products"),
         ("4 &middot; List", "Title, category, attributes, price, stock; 3&ndash;8 square photos, white background, no text or watermarks"),
         ("5 &middot; Ship", "Pack it; a Daraz rider collects or you drop it at a Daraz point &mdash; or Daraz stores and ships it for a fee"),
         ("6 &middot; Get paid", "Weekly, for orders marked delivered; a later return is taken off the next payment")]
S["fc-daraz-steps"] = sec("fc-daraz-steps", "#ffffff", "Marketplaces &middot; Daraz", "Selling on Daraz in six steps",
  gtrows(["Step", "What you do"], daraz, 262, [330, 1278], rh=86, size=23, head_size=18)
  + "\n" + band(7, 846, 64, "New sellers pay <b>0% commission for their first 30 days</b>, Daraz&rsquo;s sign-up page says.", size=26, extra="padding:12px 40px;"),
  """One step per click.

Sign-up and documents: Daraz's Sell on Daraz page and Seller Center (individual sellers: identity card and bank document; corporate sellers: business registration and bank document); the CNIC as a clear photo of both sides and a cheque book or statement showing the name and IBAN (Pakera). Opening a shop is free.

Images: a square 1:1 main image on pure white, JPEG or PNG, 3-8 images, no stickers, text or watermarks (guides citing Daraz's image guidelines, 2026). Listings go through quality control before they go live.

Shipping: fulfilled by the merchant (a Daraz rider picks up, or drop at a Daraz point) or Fulfilled by Daraz (stock in Daraz's warehouse; a pick-and-pack fee and storage on aged stock) (Seedha Hisab guide).

Payment: weekly for delivered orders, transferred about five days after the cycle closes; returns deducted from the next cycle (Pakera, 2026; Daraz Seller Help Center).

Sources: Daraz, Sell on Daraz and Seller Center; Pakera (2026); Daraz Seller Help Center; image and fulfilment guides (2026).""",
  footer="Sources: Daraz Sell on Daraz &amp; Seller Help Center; Pakera (2026)")

S["fc-daraz-fees"] = sec("fc-daraz-fees", "#f5f5f6", "Marketplaces &middot; Daraz fees", "What Daraz keeps from one order",
  grid([
    ("Commission", "2% to 20%, by category", "Mobiles 3%, laptops 2%, TVs 4%, makeup 14.44%, women&rsquo;s fashion 18.5%, jewellery 20%.", RED),
    ("Payment fee", "2.25% of the order", "Some guides report 1.25&ndash;1.75%; Seller Center shows yours.", ORANGE),
    ("Handling", "Rs 10&ndash;60 an item", "A per-item fee; and tax on Daraz&rsquo;s fees, 13&ndash;16% by province.", BLUE),
  ], 3, 290, 300, bsize=24)
  + "\n" + band(4, 630, 250, "A PKR 3,000 makeup set: commission PKR 433 + payment PKR 68 + handling up to PKR 60 = <b>about PKR 560, or 19%</b> &mdash; before tax on the fees and any shipping charge.<br><br>Against your own store: PKR 108&ndash;207 to be paid (Part 2) &mdash; but Daraz brings the shoppers.", size=28),
  """One fee per click, then the example.

Commission: rates effective 1 June 2026 from Daraz University, as listed by Pakhisaab (set by category down to level 6, excluding VAT). Payment fee: 2.25% (Pakera, SellerHub); ProfitTool cites 1.25-1.75%, probably older. Handling: Rs 10-60 per item (Pakera). Tax on fees: 13% in Sindh, 16% in Punjab and KP (ProfitTool); Daraz also withholds income tax.

Example: 14.44% x 3,000 = 433; 2.25% x 3,000 = 67.5; handling up to 60: about 560, 18.7%. Illustrative arithmetic.

Sources: Pakhisaab (Daraz rates from 1 June 2026); Pakera; SellerHub; ProfitTool (2026).""",
  footer="Sources: Pakhisaab (Daraz rates from 1 June 2026); Pakera; SellerHub &middot; example illustrative")

S["fc-other-pk"] = sec("fc-other-pk", "#ffffff", "Marketplaces &middot; at home", "Other places to sell in Pakistan",
  grid([
    ("Instagram and Facebook", "Shop by message", "No in-app checkout in Pakistan: orders by DM, paid by COD or a wallet link.", RED),
    ("WhatsApp Business", "A catalogue in the chat", "Free: a product catalogue, quick replies and payment links.", ORANGE),
    ("Buyon.pk", "Free to list", "Commission only on a sale: 8&ndash;25% by category.", BLUE),
    ("TikTok Shop", "Not yet in Pakistan", "Pakistani sellers cannot register (October 2026); TikTok ads send buyers to your site or Daraz.", GREEN),
  ], 4, 290, 400, bsize=23)
  + "\n" + band(5, 740, 130, "Each place has its own shoppers and its own fee. <b>Where do your customers already shop?</b>", size=30),
  """One place per click.

Buyon.pk: free registration and listing, commission on each sale from 8% to 25% by category (its Sell on Buyon page). TikTok Shop: no seller registration from Pakistan and Pakistan absent from the 24 markets listed in August 2026; TikTok self-serve ads are open to Pakistani businesses but cannot send buyers to an in-app checkout (Revebe, Slashcart, 2026). Category sites (electronics, fashion) run their own seller programmes; ask each.

Sources: Buyon.pk; Revebe, Slashcart (TikTok Shop, 2026).""")

abroad = [("Amazon", "Yes: Pakistan is on Amazon&rsquo;s accepted list", "US$0.99 an item or US$39.99 a month; referral about 15% in most categories", "Payoneer, then a rupee account"),
          ("Etsy", "Yes, through Payoneer", "US$0.20 a listing; 6.5% a sale plus payment processing", "Payoneer, weekly"),
          ("eBay", "Reported yes &mdash; confirm with eBay", "Category fees on each sale", "Payoneer"),
          ("TikTok Shop", "No: register in the country you sell in", "&mdash;", "&mdash;")]
S["fc-abroad"] = sec("fc-abroad", "#f5f5f6", "Marketplaces &middot; abroad", "Selling abroad from Pakistan",
  gtrows(["Marketplace", "Can a Pakistani seller join?", "Fees", "Paid through"], abroad, 262,
        [240, 440, 590, 338], rh=110, size=23, head_size=18)
  + "\n" + band(5, 760, 120, "Selling abroad adds a currency, a courier and returns from far away. <b>Which product travels well?</b>", size=30),
  """One marketplace per click.

Amazon: Pakistan is listed on Amazon's Countries accepted for seller registration (Pakistan was added in 2021, TDAP guide); Individual plan US$0.99 per item sold or Professional US$39.99 a month; referral fees 5-45% by category, 15% in most; Fulfilment by Amazon fees on top; payouts through Payoneer to a Pakistani bank (SideHustlePK, Pakera, 2026).

Etsy: Pakistan is on the list of Payoneer-supported countries; earnings reach Payoneer each Monday; fees reported at 6.5% per sale plus payment processing, about 15% in all for a Pakistani seller in one guide (Pakera; Empowerers, 2026). The US$0.20 listing fee is Etsy's standard fee. One guide reports some Pakistani sellers' Payoneer accounts being disabled after the first payout.

eBay: a guide says Pakistan-based sellers can sell, with Payoneer; not confirmed from eBay.

Sources: Pakera, SideHustlePK, TDAP (Amazon); Pakera, Empowerers, TechList (Etsy, 2026).""",
  footer="Sources: Pakera, SideHustlePK, TDAP (Amazon); Pakera, Empowerers (Etsy, 2026)")

air = [("1 &middot; Check you may", "Your building&rsquo;s and family&rsquo;s rules, and your city&rsquo;s rules and taxes for short stays"),
       ("2 &middot; Become a host", "Sign up with email, Google, Apple or Facebook; start the listing"),
       ("3 &middot; Describe it", "Type of place, guests, rooms, beds, bathrooms, amenities, location"),
       ("4 &middot; Photos", "Clean and bright, every room; the first photo decides the click"),
       ("5 &middot; Price and calendar", "Nightly price, cleaning fee, minimum nights, discounts"),
       ("6 &middot; Rules", "House rules and a cancellation policy"),
       ("7 &middot; Verify and publish", "ID scan and selfie, a payout method; then answer fast and earn reviews")]
S["fc-airbnb-steps"] = sec("fc-airbnb-steps", "#ffffff", "Marketplaces &middot; Airbnb", "Hosting on Airbnb, step by step",
  gtrows(["Step", "What you do"], air, 262, [400, 1208], rh=84, size=23, head_size=18),
  """One step per click.

Steps as Airbnb's host set-up runs them (sign-up, the Become a host wizard, describing the place, photos, price and availability, rules, identity verification by ID scan and selfie) per host guides (Bed-Booking, Steadily, Lodgify, 2026). Airbnb charges no listing or subscription fee.

Step 1: Airbnb does not decide whether your building or city allows short stays; the provincial tourism department, the housing society and the tax office do. Ask before listing.

Sources: host guides (2026); Airbnb help centre.""")

S["fc-airbnb-money"] = sec("fc-airbnb-money", "#f5f5f6", "Marketplaces &middot; Airbnb money", "Airbnb: fees and getting paid",
  grid([
    ("Service fee", "15.5% for most hosts", "One host-paid fee on the booking (nightly price and cleaning fee); the old 3% split fee is being phased out.", RED),
    ("No fee to list", "Only when booked", "Airbnb takes its fee when a booking is confirmed.", ORANGE),
    ("Payouts", "Through Payoneer", "Pakistani hosts report Payoneer as the payout route, then a transfer to a rupee account.", BLUE),
  ], 3, 290, 300, bsize=24)
  + "\n" + band(4, 630, 250, "Two nights at PKR 20,000 with cleaning: the 15.5% fee is <b>PKR 3,100</b>, leaving <b>PKR 16,900</b> before Payoneer&rsquo;s charges, cleaning and tax.<br><br>Price the night so the fee, the cleaning and a quiet week still leave you a margin.", size=28),
  """One item per click, then the example.

Fee: Airbnb moved most hosts to a single host-paid service fee of 15.5% of the booking subtotal, which includes the nightly rate and the host's fees such as cleaning; the split fee (about 3% for hosts) ends once every host has migrated; which applies in Pakistan should be checked in the host dashboard (Airbnb help centre article 1857; Houst, Hostfully, AirDNA, 2026).

Payouts: an Airbnb Community thread says Airbnb offers Pakistani hosts payout through Payoneer, from which funds move to a Pakistani bank account such as HBL or UBL; another host reports trouble selecting Payoneer at set-up. Payoneer's own fees apply (Wise's guide reports 1% on some incoming transfers).

Example: 20,000 x 15.5% = 3,100; 20,000 - 3,100 = 16,900. Illustrative arithmetic.

Sources: Airbnb help centre; Houst, Hostfully, AirDNA (2026); Airbnb Community; Wise (Payoneer in Pakistan).""",
  footer="Sources: Airbnb help centre; host-fee guides (2026); Airbnb Community (payouts) &middot; example illustrative")

# --- Part 6 - Putting it together --------------------------------------------------------------

S["fc-part6"] = div("fc-part6", "Part 6 &middot; Putting it together", "One order,<br>every bill",
  "The same PKR 3,000 order sold four ways, and a first month&rsquo;s checklist.",
  """Part 6 adds up Parts 1-5. About 15 minutes, with the exercise.""")

ways = [("Shopify, cash on delivery", "0", "30&ndash;75", "170&ndash;330", "60", "260&ndash;465"),
        ("Shopify, wallet (PayFast)", "60", "66", "170&ndash;330", "30", "326&ndash;486"),
        ("WooCommerce, Raast (PayFast)", "0", "18", "170&ndash;330", "30", "218&ndash;378"),
        ("Daraz, makeup", "&mdash;", "&asymp; 560 in all", "Daraz&rsquo;s rules", "Withheld", "&asymp; 560 +")]
S["fc-sum-order"] = sec("fc-sum-order", "#ffffff", "Putting it together", "One PKR 3,000 order, four ways",
  gtrows(["How it is sold", "Store 2%", "Payment or marketplace", "Delivery", "Tax", "Costs, PKR"], ways, 262,
        [520, 190, 330, 230, 150, 188], rh=92, size=23, head_size=18)
  + "\n" + band(5, 690, 190, "Before the product and the ads, the same sale costs <b>PKR 220 to 560</b>. The cheapest way is not always the one that sells: <b>which would you start with, and why?</b>", size=30),
  """One way per click. Illustrative arithmetic on the rates in Parts 1-5, in PKR.

Shopify COD: no Shopify fee, COD fee 1-2.5%, a 0.5 kg parcel within a city, 2% tax withheld. Shopify wallet: 2% to Shopify, 2.20% to PayFast, the parcel, 1% tax. WooCommerce Raast: 0.60% to PayFast, the parcel, 1% tax. Daraz: commission, payment and handling fees as on the Daraz fees slide; delivery as Daraz's shipping rules set it; tax withheld by Daraz.

What the table leaves out: refused cash-on-delivery parcels (Part 3), the platform's own monthly fee (Part 1), and ads (Part 4) - the cost of finding the customer, which a marketplace partly replaces.""",
  footer=ILL)

first = [("NTN on FBR&rsquo;s IRIS", "Free", "Lower card and withholding tax as a filer; gateways ask for it"),
         ("A bank account in the business&rsquo;s name", "Free to open", "The same name on the NTN, the CNIC and the account"),
         ("A store", "PKR 0&ndash;100,000 a year", "Instagram, Shopify or WooCommerce (Part 1)"),
         ("One gateway or wallet, and Raast", "No set-up fee at most", "The rate card in writing (Part 2)"),
         ("Two couriers, ten test parcels each", "About PKR 2,000&ndash;3,300 a courier", "Days, refusals, payment dates (Part 3)"),
         ("An ad test", "PKR 10,000 a platform", "Your own cost per order (Part 4)"),
         ("A Daraz shop", "Free; 0% commission for 30 days", "A second shop window (Part 5)")]
S["fc-checklist"] = sec("fc-checklist", "#f5f5f6", "Putting it together", "A first month&rsquo;s checklist",
  gtrows(["Step", "Cost", "Why"], first, 262, [560, 470, 578], rh=84, size=23, head_size=18),
  """One step per click.

Test parcels: ten 0.5 kg parcels at PKR 200-330 each (TCS range) or PKR 170-220 (Leopards) - about PKR 2,000-3,300 a courier, illustrative. NTN: free registration on FBR's IRIS portal (Rapid Gateway guide). The rest repeats Parts 1-5.

A strong close for the room: the first month costs little if the founder tests before committing - the expensive mistakes are a year's platform plan, a custom build or a stock order made before the first ten customers.""",
  footer=ILL)

S["fc-ex2"] = exercise("fc-ex2", "Exercise", "Price one order",
  "Your own product, sold at your own price to a customer in another city.",
  ["What does the parcel cost, and the COD fee?", "What does each way of paying cost you?",
   "What is left after the product, delivery and payment?", "So what is the most one order may cost in ads?"],
  "Exercise &middot; use the rates in Parts 1&ndash;5",
  """Fifteen minutes in teams, then two teams report. One question per click.

Push for the last answer: the most an order can cost in ads is what is left after product, delivery, payment and tax; a team whose ad cost per order is above it loses money on every sale, however fast it grows.""",
  top=540, h=170, cols=2)

# --- The simulation ------------------------------------------------------------------------------

S["fc-sim-part"] = div("fc-sim-part", "In the simulation", "The same bills<br>in the simulation",
  "How the simulation prices payment, delivery, marketplaces and ads &mdash; set beside the market&rsquo;s.",
  """Every simulation number on the next slide is the simulation's assumption, not market data. About 5 minutes.""")

sim = [("Payment gateway (9.3)", "All three charge 2.9%; they differ in payments that succeed (84%, 91% or 96%)", "PayFast 2.20&ndash;3.50%; Safepay 2.9% + Rs 30"),
       ("Cash on delivery (9.1, 9.2)", "Courier fee 1.2% of the order; the cash arrives after the courier&rsquo;s days", "1&ndash;2.5%; 7&ndash;14 days, or upfront"),
       ("Couriers (8.3)", "PKR 145, 175 or 210 a parcel; 94&ndash;97.5% delivered; paid in 12&ndash;21 days", "PKR 170&ndash;330 for 0.5 kg in a city"),
       ("Marketplace (4.1)", "14.5% commission on marketplace orders", "Daraz: commission + 2.25% + handling, &asymp;19% on makeup"),
       ("Ads (3.1&ndash;3.4)", "Budgets by channel; costs rise as every team spends more", "Pakistan CPC and CPM ranges, Part 4")]
S["fc-sim"] = sec("fc-sim", "#ffffff", "In the simulation", "The simulation&rsquo;s prices beside the market&rsquo;s",
  gtrows(["Cost", "In the simulation", "In the market (Parts 2&ndash;5)"], sim, 262, [380, 740, 488], rh=100, size=22, head_size=18),
  """One cost per click. The simulation's numbers are its own assumptions (params/couriers.csv and params/parameters.csv), set to sit inside the market's ranges; they are not market data.

Simulation: gateway_fee 2.9% on prepaid orders, gateway success 84% (B, cheapest), 91% (A) or 96% (C); cod_handling_fee 1.2%; couriers Speed Express PKR 210, 97.5% delivered, paid in 12 days; Value Logistics PKR 145, 94%, 21 days; Wide Network PKR 175, 95.8%, 16 days; marketplace_commission 14.5%.

The point for teams: the simulation's gateway choice is about payments that fail, not the fee, which is the same at all three - just as a real gateway's success rate can matter more than its rate.""",
  footer="Decision rules from the simulation &middot; not market data; market ranges from Parts 2&ndash;5")

S["fc-close"] = sec("fc-close", "#131316", "To take away", "Three rules for the first year",
  grid([
    ("Read the rate card", "In writing", "Every gateway and courier, one line per method, tax and minimums shown.", "#ff3b3b"),
    ("Count per order", "In rupees", "Every fee turned into rupees on one order &mdash; then into profit.", "#ff3b3b"),
    ("Test small", "Before you commit", "Ten parcels, PKR 10,000 of ads, one marketplace &mdash; then scale what pays.", "#ff3b3b"),
  ], 3, 300, 300, bg="#1f1f24", border="border:1px solid #33333b;", tcol="#ffffff", bcol="#c9c9d1")
  + "\n" + band(4, 660, 150, "Rates change every few months. <b>The habit of checking them is worth more than any number in this deck.</b>", bg="#ed0000", size=31),
  """Close. One rule per click.

The rates in this deck were checked in November 2026; update the deck from the providers' own pages before teaching it again (docs/16-lecture-decks.md).""", dark=True, eyecol="#ff3b3b")

ORDER = ["fc-cover", "fc-ex1", "fc-map",
         "fc-part1", "fc-store-options", "fc-shopify", "fc-woo", "fc-domain", "fc-first-year",
         "fc-part2", "fc-pay-how", "fc-gateways", "fc-pay-order", "fc-pay-terms", "fc-pay-pick",
         "fc-part3", "fc-couriers", "fc-ship-order", "fc-ship-terms", "fc-ship-pick",
         "fc-part4", "fc-ads-rates", "fc-ads-10k", "fc-ads-pay",
         "fc-part5", "fc-daraz-steps", "fc-daraz-fees", "fc-other-pk", "fc-abroad",
         "fc-airbnb-steps", "fc-airbnb-money",
         "fc-part6", "fc-sum-order", "fc-checklist", "fc-ex2",
         "fc-sim-part", "fc-sim", "fc-close"]
SECTIONS = {
    "fc-open": {"description": "The founder's cost sheet · five bills on every order", "start": "fc-cover"},
    "fc-store": {"description": "Part 1 · The store: Shopify, WooCommerce, domains, a first year's bill", "start": "fc-part1"},
    "fc-pay": {"description": "Part 2 · Getting paid: gateways, wallets, Raast, rates per order, terms", "start": "fc-part2"},
    "fc-ship": {"description": "Part 3 · Delivery: couriers, COD fees, payment cycles, terms", "start": "fc-part3"},
    "fc-ads": {"description": "Part 4 · Ads: Meta, Google, TikTok rates, what PKR 10,000 buys, paying", "start": "fc-part4"},
    "fc-market": {"description": "Part 5 · Marketplaces: Daraz, other places, abroad, Airbnb", "start": "fc-part5"},
    "fc-sum": {"description": "Part 6 · One order, every bill; a first month's checklist; the exercise", "start": "fc-part6"},
    "fc-sim": {"description": "The same bills in the simulation, and the close", "start": "fc-sim-part"}}

if __name__ == "__main__":
    write(S, ORDER, "The Founder’s Cost Sheet — Selling Online in Pakistan", SECTIONS)
