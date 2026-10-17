"""Session 8 - How Will You Get Customers to Come Back? About 25 slides.

Run: python s8_slides.py <deck folder> [logo url]
Part 2's numbers come from tools/deck/s7_s8_tests.py.
"""
import pathlib, sys, json
HERE = pathlib.Path(__file__).parent
exec((HERE / "s7_slides.py").read_text().split("\nS = {}\n")[0])
FT = "Session 8 &middot; How Will You Get Customers to Come Back?"
def sec(sid, bg, eyebrow, title, body, notes, footer=FT, **kw):
    return section(sid, bg, "#131316", eyebrow, title, body, notes, footer=footer, **kw)
def div(sid, part, title, line, notes):
    return divider(sid, part, title, line, notes).replace("Session 2 &middot; Finding the Right Idea", FT).replace("856d57cb939a323d46943b3b229572d7", "__LOGO__")

S = {}
S["cover"] = cover(8, "How Will You Get Customers<br>to Come Back?",
  "Customer experience, repeat purchases, WhatsApp, SMS, email, loyalty and CRM &mdash; and a customer retention plan.",
  """Two hours, about 25 slides: 3 min recap, 8 min opening exercise, Part 1 theory about 65 min (why the second order matters 10, experience and service 10, WhatsApp, SMS and email 10, loyalty and subscriptions 15, CRM and segments 10, measures and the plan 10), exercise 10, Part 2 simulation about 30 min, 3 min close.

Month 6 has run. Today's decisions open for month 7: 6.1 CRM and retention, 10.1 customer service team size, 10.4 returns policy.

The idea for the day: the first order is bought; the second should be earned. A customer you keep is one you do not pay for twice.""", size=104)

S["recall"] = sec("recall", "#f5f5f6", "Where we got to last week", "Every customer has a price",
  grid([
    ("Channels", "Each one finds a different buyer", "Social creates demand; search captures it; creators lend trust.", "#ed0000"),
    ("Numbers", "CAC, CVR, ROAS", "ROAS is revenue, not profit; breakeven is one over the margin.", "#eb6834"),
    ("Value", "The cheapest click is not the best customer", "Judge a channel by what its customers are worth over time.", "#2a78d6"),
  ], 3, 300, 300)
  + "\n" + band(4, 660, 170, "Last week: <b>what each customer cost to win</b>. Today: <b>how to make them buy again</b> &mdash; so the cost pays back.", size=31),
  """Three quick clicks from Session 7.

The bridge: a customer bought with Rs 1,000 of advertising who orders once and never returns is usually a loss. The same customer ordering four times is a business. Retention is where acquisition spending becomes profit.""")

S["ex1"] = exercise("ex1", "Exercise 1", "The brand you keep going back to",
  "Think of an online brand or shop you have bought from three times or more.",
  ["What brings you back &mdash; the product, the price or a message?", "Which brand lost you, and what happened?",
   "Which messages from brands do you actually open?", "What would make you leave the one you use now?"],
  "Exercise 1 &middot; why customers stay, and why they leave",
  """Eight minutes. One question per click; take a show of hands, then three stories.

Sort the answers into today's session: the product and the experience (it worked, it arrived, the problem was fixed), messages (a reminder on WhatsApp at the right time), loyalty (points, free delivery, a membership), and habit.

Question 2 usually produces the most useful stories: a late delivery, a rude reply, a refused return, a price rise. Most customers do not complain; they simply stop buying.""", top=500, h=180, cols=2)

S["part1"] = div("part1", "Part 1 &middot; Theory", "Keeping the customers<br>you paid for",
  "Experience and service; WhatsApp, SMS and email; loyalty and subscriptions; CRM &mdash; each with a Pakistani and a global case.",
  """Part 1 follows the course outline: customer experience, repeat purchases, WhatsApp, SMS, email, loyalty and CRM, ending with a customer retention plan. Real-world practice only; the simulation is Part 2.""")

second = [("1st order", "Rs 1,000 to win the customer", "+ Rs 600", "&minus; Rs 400"),
          ("2nd order", "Rs 50 message and offer", "+ Rs 600", "+ Rs 150"),
          ("3rd order", "Rs 50", "+ Rs 600", "+ Rs 700"),
          ("4th order", "Rs 50", "+ Rs 600", "+ Rs 1,250")]
S["second"] = sec("second", "#ffffff", "Why retention matters", "The first order is a loss; the second pays",
  trows(["One customer, Rs 2,000 orders", "Cost to get the order", "Margin on the order", "Running total"], second, 276,
        [460, 520, 330, 298], rh=76, size=28)
  + "\n" + band(5, 640, 230, "Winning the customer costs Rs 1,000; bringing them back costs about Rs 50. <b>The profit is in the second, third and fourth orders.</b> What share of your customers ever place a second?", size=29),
  """Illustrative numbers. One row per click.

The customer is won with Rs 1,000 of advertising (a CAC from Session 7) and each Rs 2,000 order earns Rs 600 of margin before marketing. The first order loses Rs 400. A message and a small offer bring them back for about Rs 50, and the running total turns positive on the second order.

This is why retention is usually cheaper than acquisition: the customer already knows the brand, has an account and has the brand's number in their phone. Avoid quoting a universal ratio ("five times cheaper") as fact; the gap depends on the business.""",
  footer="Illustrative numbers")

S["curve"] = sec("curve", "#f5f5f6", "Churn", "Small monthly losses add up over a year",
  row3([
    ("5% lost a month", "54%", "still buying after a year. On average a customer stays 20 months."),
    ("15% lost a month", "14%", "still buying after a year. On average a customer stays 7 months."),
    ("The difference", "4&times;", "as many customers left from the same Rs spent to win them."),
  ], 290, 330)
  + "\n" + band(4, 690, 180, "Churn is the share of customers who stop buying each month. Average life = 1 &divide; churn. <b>Cutting churn from 15% to 5% is worth more than any discount.</b>", size=29),
  """Arithmetic, not market data. One number per click.

If a constant 5% of customers stop buying each month, 0.95 to the power 12 = 54% are still buying after a year; at 15% a month, 0.85 to the power 12 = 14%. The average lifetime is 1 divided by the monthly churn: 20 months against about 7.

Real churn is not constant: it is highest after the first order and falls for customers who stay. That is why the first 90 days matter most (Exercise 2).""")

S["cx"] = sec("cx", "#ffffff", "Customer experience", "Experience is the first retention tool",
  grid([
    ("Product", "It is what was promised", "Photos, size and quality match. Over-promising brings returns and bad reviews.", "#ed0000"),
    ("Delivery", "On time, intact", "A late or damaged parcel undoes the best ad.", "#eb6834"),
    ("Service", "A quick, human answer", "Where is my order? Can I change it? A fast reply keeps the customer.", "#2a78d6"),
    ("Returns", "Easy, but not free for all", "Easy returns build trust to buy; who pays decides what they cost.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "No message brings back a customer whose order went wrong. <b>Where does your experience break first?</b>", size=30),
  """One card per click.

Retention starts before any loyalty programme: the product, the delivery, the service reply and the returns process decide whether there is a second order. A complaint handled well can make a customer more loyal than one who never had a problem; a complaint ignored becomes a one-star review.

Returns policy is a trade-off: free returns make people braver about buying, but invite more returns; a restocking fee cuts returns but makes buying riskier. Session 9 returns to delivery.""")

S["case-cx"] = cases("case-cx", "Cases &middot; Service", "Service that keeps customers",
  ("Pakistan", "PTCL", "with Eocean, on WhatsApp", [
    ("The change", "Moved complaints and service requests onto WhatsApp, with guided forms for common problems."),
    ("The result", "Complaints routed to agents down 31%; 34% resolved at once. Meta featured it as a success story.")]),
  ("Global", "Zappos", "Las Vegas, since 1999", [
    ("The promise", "Free shipping both ways and a 365-day return window on unworn items."),
    ("The bet", "Service as the brand: call-centre staff with no scripts. Amazon bought it in 2009.")]),
  "Both treat service as <b>part of the product</b>, not a cost centre &mdash; one by speed, the other by generosity.",
  """Two service cases.

PTCL with Eocean: Pakistan's telecom company used Eocean's integration of the WhatsApp Business Platform for complaints and service. ProPakistani (March 2025) reported that Meta recognised it as a global success story, citing a 31% reduction in complaints routed directly to customer service, a 10% fall in dispatch service requests through WhatsApp Flows, and 34% of complaints resolved immediately without further team support. A telecom, not a shop &mdash; but the same tool every Pakistani brand can use.

Zappos: the US online shoe retailer built its brand on service: free shipping both ways, a 365-day return window for items in their original condition, and call-centre staff without scripts or time limits under CEO Tony Hsieh. Amazon acquired it in 2009 (valued at about US$1.2 billion at closing; announced at about US$850 million in shares and cash &mdash; figures vary).

The lesson: service can be speed and convenience (meeting customers on WhatsApp) or generosity (returns, time). Both cost money, and both bring customers back.

Question for the room: which brand fixed a problem for you so well that you bought again?

Sources: ProPakistani (Mar 2025); Zappos return policy; press coverage of the 2009 Amazon deal.""",
  "Sources: ProPakistani (Mar 2025); Zappos; Amazon deal coverage (2009)")

chans = [("WhatsApp", "Read almost always; a two-way chat", "Paid per message for businesses", "Order updates, service, reminders"),
         ("SMS", "Reaches every phone, no internet needed", "Cheap per message", "Order codes, short alerts"),
         ("Email", "Often unread in Pakistan", "Almost free at scale", "Receipts, longer content, abroad"),
         ("App or push", "Only if they installed the app", "Free once installed", "Frequent buyers, flash offers")]
S["channels"] = sec("channels", "#ffffff", "WhatsApp, SMS and email", "Four ways to reach a customer again",
  trows(["Channel", "Reach", "Cost", "Best for"], chans, 276, [300, 520, 400, 388], rh=80, size=26)
  + "\n" + band(5, 650, 220, "In Pakistan most customers live on WhatsApp &mdash; and from October 2026 Meta charges a Pakistani business <b>US$0.015 for an order-update message</b>, about 11 times India's rate. <b>Every message has to earn its cost.</b>", size=28),
  """One channel per click.

WhatsApp is where Pakistani customers are, and its messages are read; businesses use the WhatsApp Business app (small sellers) or the Business Platform through a provider (larger ones). Meta prices business messages by category and country: ProPakistani and TechJuice reported (September 2026) that from 1 October 2026 a utility, authentication or service message in Pakistan costs US$0.015, against US$0.0014 in India.

SMS reaches every phone, including those without data, and is used for order confirmations and codes. Email is cheap but under-used by many Pakistani shoppers; it matters more for international customers and receipts.

Consent and frequency: customers who did not agree to messages, or receive too many, block the brand &mdash; and on WhatsApp, blocks and reports can limit a business account.

Reach and cost descriptions in the table are general characteristics, not measured figures.""",
  footer="Sources: ProPakistani, TechJuice (Sep 2026) on WhatsApp business message prices")

S["messages"] = sec("messages", "#f5f5f6", "What to send", "The messages that bring customers back",
  grid([
    ("Updates", "Where is my order?", "Confirmation, dispatch and delivery. Cuts calls and refused parcels.", "#ed0000"),
    ("Replenish", "Timed to run out", "A shampoo lasts about a month: remind them in week four, not week one.", "#eb6834"),
    ("Recommend", "Based on what they bought", "Conditioner for the shampoo buyer, not a random sale.", "#2a78d6"),
    ("Win back", "When they go quiet", "A reason to return after 60 days &mdash; not a discount for everyone.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "The best retention message is <b>useful at the moment it arrives</b>. What would your customer thank you for sending?", size=30),
  """One card per click.

Order updates are the most-read messages a brand sends, and they reduce "where is my order?" calls and cash-on-delivery refusals.

Replenishment is the strongest retention tool for personal care and home care: products run out on a schedule. A reminder timed to that schedule is a service, not spam.

Recommendations use purchase history. Win-back messages go to customers who have stopped buying; a blanket discount to everyone trains customers to wait for one.""")

S["loyalty"] = sec("loyalty", "#ffffff", "Loyalty programmes", "Giving customers a reason to stay",
  grid([
    ("Points", "Earn on every order", "A small share back, spent on the next order. Simple, and easy to copy.", "#ed0000"),
    ("Tiers", "Better perks for the best", "Spend more, unlock more. The top tier makes customers aim higher.", "#eb6834"),
    ("Perks", "Not only discounts", "Early access, samples, free delivery, a birthday gift.", "#2a78d6"),
    ("The trap", "A discount by another name", "If points are just money off, you pay for orders you would have had.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "A loyalty programme works when customers <b>value the membership</b>, not only the discount. What would make yours worth joining?", size=30),
  """One card per click.

Loyalty programmes reward repeat buying and, as importantly, identify the customer: every order is linked to a member, which feeds CRM.

The cost is real: every point is a discount on an order, including orders the customer would have placed anyway. The best programmes give experiences and status that cost the brand less than they are worth to the customer.""")

S["case-loyalty"] = cases("case-loyalty", "Cases &middot; Loyalty", "Members who come back",
  ("Pakistan", "Imtiaz Super Market", "loyalty since 2016", [
    ("The programme", "Points of up to 1.5% on purchases, plus vouchers, hampers and lucky draws; join at any branch."),
    ("The scale", "Close to 350,000 members, and loyalty points worth Rs 250m awarded (ProPakistani).")]),
  ("Global", "Sephora", "Beauty Insider", [
    ("The programme", "Free to join; three tiers by annual spend; points for samples, experiences and rewards."),
    ("The scale", "About 40 million members in the US and Canada in 2024, who make up a majority of its sales.")]),
  "Both reward <b>coming back</b> &mdash; and both learn who their customers are from every order.",
  """Two loyalty cases. Both sell personal care; Imtiaz sells home care too.

Imtiaz Super Market: the Pakistani grocery and household chain started its loyalty programme in September 2016. ProPakistani reported that members earn up to 1.5% in points, with discounted vouchers, gift hampers and lucky draws; that the programme was close to 350,000 members; and that Imtiaz had awarded loyalty points worth Rs 250 million. Registration is at branch kiosks. (Promotional coverage; the member figure is approximate.)

Sephora Beauty Insider: free to join, with tiers by annual spend (Insider, VIB, Rouge) and points redeemed for samples, experiences and rewards. Modern Retail (September 2024) reported about 40 million members in the US and Canada and that Sephora says members account for a majority of its sales.

The lesson: a programme pays when it changes behaviour and tells the brand who its customers are.

Question for the room: which loyalty card or app do you actually use, and why that one?

Sources: ProPakistani (Imtiaz loyalty programme); Modern Retail (Sep 2024).""",
  "Sources: ProPakistani (Imtiaz); Modern Retail (Sep 2024)")

S["subscribe"] = sec("subscribe", "#f5f5f6", "Subscriptions and memberships", "Turning repeat orders into a habit",
  two(1, 128, 280, 819, 330, "Replenishment subscription", "The product arrives on schedule",
      ["Razors, shampoo, nappies, detergent", "Customer saves time; brand knows next month's sales", "Risk: customers pause or cancel when stock piles up"], "#ed0000")
  + "\n" + two(2, 973, 280, 819, 330, "Paid membership", "A fee for better terms",
      ["Free delivery, member prices, early access", "Customer has paid, so they keep using it", "Risk: perks that cost more than the fee"], "#2a78d6")
  + "\n" + band(3, 640, 230, "A subscription changes the question from <b>&lsquo;should I buy again?&rsquo;</b> to <b>&lsquo;should I cancel?&rsquo;</b> &mdash; and most people do not. Which of your products is used up on a schedule?", size=29),
  """Two clicks, then the band.

Subscriptions suit products used up on a schedule &mdash; much of personal care and home care. The brand gets predictable demand and the customer saves effort. The risks are churn when deliveries outpace use, and the cost of discounts offered to subscribers.

Paid memberships charge a fee for better terms. They work because the member wants the fee back, so they buy more often from the same place.""")

S["case-sub"] = cases("case-sub", "Cases &middot; Subscriptions", "Paying to come back",
  ("Pakistan", "foodpanda", "pandapro", [
    ("The offer", "About Rs 167 a month on an annual plan: unlimited free deliveries and member deals on food and groceries."),
    ("The effect", "Foodpanda says a rise in pandapro members brought restaurants more orders (Aurora, 2024).")]),
  ("Global", "Dollar Shave Club", "Los Angeles, 2011", [
    ("The model", "Razors by monthly subscription; a launch video in 2012 brought about 12,000 orders in two days."),
    ("The result", "About 3.2 million members by 2016, when Unilever bought it for a reported US$1bn.")]),
  "Both make the next order <b>the default</b> &mdash; one through free delivery, the other through the post.",
  """Two subscription cases.

foodpanda pandapro: Dawn's Aurora (September 2024) described pandapro in Pakistan at about Rs 167 a month on an annual plan, with unlimited free deliveries, exclusive deals and discounts on food and grocery orders, plus a Spotify trial; it reported that a surge in pandapro memberships had translated into more orders for restaurants. The fee makes members order from foodpanda rather than a rival app. (No member numbers published.)

Dollar Shave Club: founded in 2011, it sold razors by monthly subscription. Its 2012 launch video, made for about US$4,500, brought about 12,000 orders in two days. When Unilever agreed to buy it in July 2016 it had about 3.2 million members; the price was not disclosed but was widely reported at about US$1 billion.

The lesson: subscriptions and memberships turn retention into a default the customer has to choose to break.

Question for the room: which subscription do you keep even though you rarely use it? What does that tell a brand?

Sources: Dawn Aurora (Sep 2024); Fortune, CNN Money and Drugstore News (Jul 2016); Wikipedia (DSC launch video).""",
  "Sources: Dawn Aurora (2024); Fortune, CNN Money, Drugstore News (2016)")

S["crm"] = sec("crm", "#ffffff", "CRM", "Knowing who your customers are",
  grid([
    ("Capture", "Every order is a record", "Name, number, address, what they bought and when.", "#ed0000"),
    ("Group", "Not everyone is the same", "New, regular, lapsed, top spenders &mdash; each needs a different message.", "#eb6834"),
    ("Act", "The right message to each", "Thank the new, reward the regular, remind the lapsed.", "#2a78d6"),
    ("Learn", "Did they come back?", "Repeat rate by month joined and by channel shows what works.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "CRM is not software; it is <b>treating customers differently because you know them</b>. A spreadsheet is enough to start.", size=30),
  """One card per click.

Customer relationship management: capturing who each customer is and what they did, grouping them, acting differently for each group, and measuring the result. Tools range from a spreadsheet and WhatsApp Business labels to Shopify's customer lists and dedicated CRM platforms.

Cohort analysis: group customers by the month (or channel) they joined and track what share are still buying. It is how a brand sees whether retention is improving and which acquisition channels bring customers who stay &mdash; the link back to Session 7.""")

rfm = [("New", "Bought once, recently", "Welcome, how-to, a reason for order two"),
       ("Regular", "Buys often", "Thank them; early access; ask for a review"),
       ("Top spenders", "Most of your revenue", "Look after them personally; never lose one quietly"),
       ("Slipping", "Used to buy, has gone quiet", "A useful reminder; ask what went wrong"),
       ("Lapsed", "Not bought in months", "One win-back offer, then stop messaging")]
S["segments"] = sec("segments", "#f5f5f6", "Who to talk to", "Group customers by when, how often and how much",
  trows(["Group", "Who they are", "What to send"], rfm, 276, [380, 560, 668], rh=78, size=27)
  + "\n" + band(6, 720, 150, "Recency, frequency and value (RFM) sort any customer list. <b>Which group is largest on your list &mdash; and which is most valuable?</b>", size=29),
  """One group per click.

RFM: recency (how long since the last order), frequency (how many orders) and monetary value (how much they spend). Scoring customers on the three sorts them into groups that need different treatment.

The common mistake is sending the same discount to everyone: regulars get money off orders they would have placed anyway, and lapsed customers learn to wait for the offer.""")

S["measures"] = sec("measures", "#ffffff", "Measuring retention", "Four numbers that say whether customers stay",
  row4([
    ("Repeat rate", "35%", "of a month's new customers placed a second order."),
    ("Churn", "6%", "of customers stopped buying this month. Average life = 1 &divide; churn."),
    ("Lifetime value", "Rs 3,600", "orders &times; margin per order over a customer's life."),
    ("NPS", "+45", "promoters minus detractors: would you recommend us?"),
  ], 290, 340)
  + "\n" + band(5, 700, 170, "Watch them <b>by cohort</b> &mdash; customers who joined in the same month or through the same channel. An average hides a leak.", size=30),
  """One measure per click.

Repeat rate and churn say whether customers come back; lifetime value says what they are worth; Net Promoter Score (the share who would recommend minus the share who would not) is an early warning of churn.

The values on the slide are illustrative, not benchmarks.

The averages mislead: a brand winning many new customers can show a rising number of orders while each month's new customers stay for a shorter time. Cohorts expose it.""", footer="Illustrative values")

S["plan"] = sec("plan", "#f5f5f6", "The customer retention plan", "A customer retention plan on one page",
  grid([
    ("Experience", "Fix what breaks first", "Product, delivery, service reply, returns.", "#ed0000"),
    ("Data", "Know each customer", "What you capture, and where it lives.", "#eb6834"),
    ("Groups", "Three to five segments", "New, regular, top, slipping, lapsed.", "#2a78d6"),
    ("Messages", "One journey for each", "What, when and on which channel.", "#1baf7a"),
    ("Reasons", "Loyalty or subscription", "Why staying is better than shopping around.", "#8a6414"),
    ("Measures", "Repeat rate and churn", "By cohort, every month; a budget per kept customer.", "#6b4fbb"),
  ], 3, 290, 250)
  + "\n" + band(7, 830, 80, "Spend on keeping customers until a kept customer costs more than a new one.", size=28, extra="padding:18px 40px;"),
  """One box per click. This is the deliverable named in the course outline.

The plan starts with experience (nothing else works if the order goes wrong), then the data, the segments, the message journey for each, the reason to stay, and the measures. The budget rule: keep spending on retention while it costs less to keep a customer than to win a new one &mdash; Session 7's CAC is the benchmark.""")

S["ex2"] = exercise("ex2", "Exercise 2", "The first 90 days of a customer",
  "A new customer has just bought a Rs 1,200 face wash that lasts about six weeks.",
  ["What do you send the day the parcel arrives?", "When do you remind them, and on which channel?",
   "What reason do you give them to choose you again?", "When do you stop messaging someone who never replies?"],
  "Exercise 2 &middot; a retention journey",
  """Ten minutes in teams. One question per click. The product is hypothetical.

Good answers: a delivery check and how-to on day one (WhatsApp); a reminder timed to the product running out, around week five; a reason that is not just a discount (a bundle, free delivery, loyalty points, a sample of a second product); and a rule to stop after two unanswered messages.

Take two teams' journeys and compare the timing.""", top=500, h=180, cols=2)

S["part2"] = div("part2", "Part 2 &middot; The simulation", "Retention opens",
  "Three decisions open for month 7: CRM and retention, the customer service team and the returns policy.",
  """Part 2 is the simulation. Month 6 has run. Teams now have six months of customers from different channels; from month 7 they control how to keep them.

Every number in Part 2 is the simulation's assumption or a test run of it, not market data.""")

S["category"] = sec("category", "#f5f5f6", "The category online", "How personal care keeps customers in Pakistan",
  grid([
    ("Replenishment", "Used up on a schedule", "Shampoo, soap, detergent and nappies run out, so a reminder is a service.", "#ed0000"),
    ("WhatsApp", "Where customers talk to brands", "Business messages now cost US$0.015 each (Meta, Oct 2026).", "#eb6834"),
    ("Loyalty", "Grocers reward coming back", "Imtiaz: close to 350,000 loyalty members.", "#2a78d6"),
    ("Delivery", "Free delivery as membership", "foodpanda's pandapro: about Rs 167 a month.", "#1baf7a"),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "The simulation's teams sell personal care and home care online. <b>How many of your month-1 customers are still buying?</b>", size=30),
  """The real category first. One card per click.

Replenishment: personal care and home care are bought repeatedly, which makes them good retention categories (a general observation, not a statistic).

WhatsApp: Meta's business-message prices for Pakistan from October 2026 (ProPakistani, TechJuice).

Loyalty: Imtiaz Super Market's programme (ProPakistani).

Delivery: foodpanda's pandapro (Dawn Aurora, 2024) &mdash; a membership built on free delivery.

Sources: ProPakistani; TechJuice; Dawn Aurora.""",
  footer="Sources: ProPakistani, TechJuice (2026); ProPakistani (Imtiaz); Dawn Aurora (2024)")

S["sim-market"] = sec("sim-market", "#ffffff", "In the simulation", "How retention works in the simulation",
  grid([
    ("CRM (6.1)", "Reach grows with spend", "Full effect from about Rs 400k a month: up to 62% less churn and 45% more repeat orders. Marketplace buyers are out of reach.", "#ed0000"),
    ("Service (10.1)", "Agents answer tickets", "An agent answers about 900 tickets a month &mdash; enough for about 1,250 orders &mdash; and costs Rs 48k. A backlog lowers ratings.", "#eb6834"),
    ("Returns (10.4)", "Who pays to send it back", "Against the usual return rate: free returns &times;1.35, customer pays &times;0.85, restocking fee &times;0.70.", "#2a78d6"),
    ("Who stays", "Churn by how they were won", "Organic 3.7% a month, Meta 6.3%, Google 14%, TikTok 26%, deal-driven 44%. A rating below 4 raises it.", "#1baf7a"),
  ], 4, 290, 440, bsize=23)
  + "\n" + band(5, 770, 110, "<b>The default since month 1:</b> CRM Rs 60k a month, 4 service agents, customer pays for returns.", size=28),
  """One rule per click. The rules are the simulation's.

CRM (6.1): retention reach grows with the square root of spend, reaching full effect at about Rs 400,000 a month. At full effect, churn falls by up to 62% and repeat orders rise by up to 45%. Customers won on the marketplace are not reached.

Service (10.1): each order creates about 0.72 contacts (including cash-on-delivery confirmation calls), plus more for each return; an agent handles about 900 a month at Rs 48,000. Unanswered tickets carry over; a slow service level lowers the rating and NPS, which raises churn.

Returns (10.4): the policy multiplies the return rate; free returns also make buying easier.

Who stays: each acquisition channel's cohort has its own churn (Session 7); an experience below a 4-star rating raises next month's churn.

Real founders estimate such numbers from their own customer data; these are the simulation's assumptions.""",
  footer="Decision rules from the simulation &middot; not market data")

tests8 = [("All default", "33.0%", "34,571", "83", "4.77m"),
          ("CRM Rs 400k", "41.9%", "37,150", "83", "3.22m &nbsp;(&minus;1.55m)"),
          ("CRM stopped", "27.6%", "33,070", "83", "4.83m &nbsp;(+0.06m)"),
          ("Service team cut to 2", "33.0%", "33,820", "49", "4.39m &nbsp;(&minus;0.38m)"),
          ("Free returns", "33.0%", "34,571", "83", "3.05m &nbsp;(&minus;1.72m)"),
          ("Restocking fee", "33.0%", "34,571", "83", "5.29m &nbsp;(+0.52m)")]
S["sim-tests"] = sec("sim-tests", "#f5f5f6", "In the simulation", "What one change did, month 7 to month 12",
  trows(["Test, kept from month 7", "Repeat, month 7", "Active, month 12", "NPS, month 12", "Contribution, 7&ndash;12"], tests8, 276,
        [450, 300, 300, 250, 308], rh=72, size=26)
  + "\n" + band(7, 786, 100, "CRM at Rs 400k: <b>2,579 more active customers</b> by month 12, at 1.55m of contribution. <b>Is that customer worth it to you?</b>", size=28),
  """One test per click. Each line is one team changing one decision from month 7 and keeping it, against an identical team on every default, in the same simulated world (six teams, six default months first). Contribution is after marketing, months 7 to 12.

CRM at Rs 400k: in month 7 the same number of orders came more from returning customers (repeat share 33% to 42%); by month 12 the team had 2,579 more active customers and a repeat share of 47%, for 1.55m less contribution &mdash; it bought customer value with margin. Stopping CRM saved almost nothing and lost 1,501 active customers.

Service team cut to 2: tickets piled up, NPS fell from 83 to 49 and 751 customers were lost; the saving on salaries did not cover it. A team of 6 changed nothing against 4: at this size, 4 agents were enough.

Free returns cost 1.72m in returns with no extra orders in this test (these teams were limited by traffic, not by shoppers' doubts); a restocking fee saved 0.52m. Ratings, NPS and active customers were unchanged by the returns policy in this run.

Results depend on each team's customers, prices and traffic; these are directions, not forecasts.""",
  footer="Simulation test run, six teams, months 7&ndash;12, all else default &middot; not market data")

S["checks"] = sec("checks", "#fdeceb", "Before month 7 runs", "Four questions before you decide",
  grid([
    ("Customers", "Who did you win, and from where?", "Your report shows customers by channel. Which cohorts are leaving fastest?", "#ed0000"),
    ("CRM", "How much is a kept customer worth?", "Compare the cost of keeping one with your CAC from month 6.", "#eb6834"),
    ("Service", "Can your team keep up?", "Check the service level and backlog against your orders.", "#2a78d6"),
    ("Returns", "Who should pay?", "Free returns help buyers decide; they also bring more back.", "#1baf7a"),
  ], 4, 300, 340)
  + "\n" + band(5, 700, 150, "Name in the board memo the number in month 7's report that will tell you <b>whether customers are staying</b>.", size=30),
  """One question per click, while teams fill in the decision form.

Logistics for the notes, not the slide: decisions for month 7 close at [deadline]. Open this round: 6.1 CRM and retention, 10.1 customer service team size, 10.4 returns policy, plus everything opened earlier. The month-7 report shows repeat order share, active customers, the service level and backlog, the return rate and NPS.""")

S["next"] = sec("next", "#131316", "Next session", "How will you deliver the order?",
  grid([
    ("Session 9", "Stock, couriers and payment", "Suppliers, safety stock, 3PL, courier mix, cash on delivery.", "#ff3b3b"),
    ("Your customers", "Did they stay?", "Month 7's repeat share and active customers are the test.", "#ff3b3b"),
    ("Your numbers", "Where does the experience break?", "Late deliveries and refusals drive churn next time.", "#ff3b3b"),
  ], 3, 300, 300, bg="#1f1f24", border="border:1px solid #33333b;", tcol="#ffffff", bcol="#c9c9d1")
  + "\n" + band(4, 660, 150, "Today: how to keep customers. Next time: <b>how to deliver what they ordered, on time, without running out of cash</b>.", bg="#ed0000", size=31),
  """Close. One card per click.

Session 9 opens operations: stock (7.1), supplier (7.2), quality assurance (7.4), safety stock (7.5), 3PL share (8.2), courier mix (8.3), cash on delivery (9.1) and the prepaid discount (9.2). Delivery is the part of the experience that loses most customers.""", dark=True, eyecol="#ff3b3b")

ORDER = ["cover", "recall", "ex1", "part1", "second", "curve", "cx", "case-cx", "channels", "messages",
         "loyalty", "case-loyalty", "subscribe", "case-sub", "crm", "segments", "measures", "plan", "ex2",
         "part2", "category", "sim-market", "sim-tests", "checks", "next"]
write(S, ORDER, "Session 8 — How Will You Get Customers to Come Back?", {
    "open": {"description": "Getting customers to come back, and why they stay", "start": "cover"},
    "experience": {"description": "Part 1 · Why retention pays, experience and service, with cases", "start": "part1"},
    "messages": {"description": "WhatsApp, SMS and email, loyalty and subscriptions, with cases", "start": "channels"},
    "crm": {"description": "CRM, segments, measures and the retention plan", "start": "crm"},
    "sim": {"description": "Part 2 · Retention in the simulation", "start": "part2"}})
