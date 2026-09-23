"""The decision handbook, as students read it in the portal.

One entry per decision in the registry. The registry already carries each
lever's name, one-line help and typical range; this adds what a student needs
before pulling it: the trade-off, where the result shows up in the monthly
report, the mistake teams usually make, and which levers it works with.

It replaces docs/01-decision-list.md as the students' reference. That file is
a build specification written before the engine existed - several of its 56
fields were merged, reshaped or never built - and it was never meant to be
read by a class. tests/test_web.py fails if a decision ships without an entry
here, so the two cannot drift apart again.

Written to teach reasoning, not answers: nothing here says which choice wins,
and nothing reveals a scheduled event or who buys a product.
"""
from __future__ import annotations

GROUP_INTROS = {
    "G1": "What you sell, at what quality, and at what price. Every other decision "
          "multiplies against the margin set here.",
    "G2": "The price the customer actually pays, after discounts and delivery. "
          "Cheap to change, easy to get wrong, slow to undo in customers' minds.",
    "G3": "How customers find you. Paid media buys this month's visits; creative "
          "and brand decide what every later rupee is worth.",
    "G4": "Where you sell. Your own site keeps the customer; the marketplace lends "
          "you its shoppers for a fee.",
    "G5": "What happens once a visitor arrives. Conversion is where paid traffic "
          "either turns into orders or into cost.",
    "G6": "Customers you already have. The cheapest orders you will ever get come "
          "from people who bought before.",
    "G7": "Stock: what you buy, from whom, and how much you keep in reserve. Cash "
          "sits here more than anywhere else.",
    "G8": "Getting the order to the door. Speed, reliability and cost pull in "
          "different directions, and a failed delivery is a return.",
    "G9": "How customers pay, and when the money reaches you. In Pakistan this "
          "decides your working capital as much as your conversion.",
    "G10": "What happens after the sale: questions, complaints, returns. It shows "
           "up in churn and ratings a month later.",
    "G11": "Technology you build. Expensive, slow, uncertain - and worth more the "
           "earlier you commit.",
    "G12": "Evidence and intent: what you pay to learn, and what you tell the "
           "board you are trying to do.",
}

ENTRIES = {
    "1.1": dict(
        does="Sets the price of every product you sell and where each one is "
             "sourced. Local stock arrives fast and costs more; imported stock is "
             "cheaper and takes longer; buying from both sits in between. The grid "
             "shows the margin on each line as you type.",
        tradeoff="Price against volume, line by line. Sourcing is cost against lead "
                 "time - a cheaper line you cannot restock quickly is a line you "
                 "will run out of.",
        watch="Gross margin and conversion rate in the report; the market price "
              "column in the grid tells you where you sit against the reference.",
        mistake="Cutting price on lines that barely sell. The grid weights the "
                "average by volume for a reason: a deep cut on a slow line moves "
                "nothing but the margin.",
        related=["1.5", "2.2", "1.2", "7.2"]),
    "1.5": dict(
        does="Where your catalogue sits on quality: economy, standard or premium. "
             "Higher tiers cost more to source and lift how customers rate you and "
             "how well visitors convert. On automatic, your product mix decides.",
        tradeoff="Perceived quality and conversion against cost of goods. It also "
                 "sets what price customers find believable.",
        watch="Rating, return rate and gross margin.",
        mistake="Claiming premium and pricing like economy. The market reads the "
                "mismatch as confusion, not a bargain.",
        related=["1.1", "7.4", "8.5"]),
    "1.2": dict(
        does="Offers three-packs of your own products at a pack price. Bundles lift "
             "average order value; the gain flattens after about three bundled "
             "lines.",
        tradeoff="Basket size against margin. A pack priced well below three "
                 "singles trades margin for a bigger order.",
        watch="Average order value (AOV) and gross margin.",
        mistake="Discounting the pack so hard that a bigger basket earns less than "
                "the single order it replaced.",
        related=["1.1", "2.4"]),
    "2.2": dict(
        does="An average discount across the whole site. Every point buys volume "
             "and costs margin on every order - including orders you would have "
             "had anyway.",
        tradeoff="Volume now against margin now and customer quality later. Past "
                 "about 25%, the customers you win are deal-driven and leave as "
                 "soon as the deal does.",
        watch="Discount rate, contribution margin, repeat order share.",
        mistake="Using discount to fix a traffic or conversion problem. It hides "
                "the problem and makes it more expensive.",
        related=["1.1", "2.4", "6.1"]),
    "2.4": dict(
        does="The cart value above which delivery is free. Enter 0 for free "
             "delivery on everything.",
        tradeoff="A low threshold wins small orders and you pay their shipping; a "
                 "high one pushes baskets up and loses customers who only wanted "
                 "one thing.",
        watch="AOV, conversion rate and fulfilment cost per order.",
        mistake="Setting it without looking at your AOV. A threshold far above what "
                "a typical basket costs changes nobody's behaviour; it just loses "
                "orders.",
        related=["1.2", "8.3"]),
    "3.1": dict(
        does="Monthly spend on Facebook and Instagram. The largest audience and "
             "your main source of new customers.",
        tradeoff="Returns diminish as you spend more, and every team spending on "
                 "Meta pushes its cost up for everyone.",
        watch="The paid media table in the report: CPM, CVR, CAC and ROAS for "
              "Meta. New customers and CAC on the dashboard.",
        mistake="Doubling spend to double orders. The curve bends; the second "
                "half-million buys much less than the first.",
        related=["3.10", "3.8", "3.9", "3.2", "3.4"],
        guide="marketing"),
    "3.2": dict(
        does="Monthly spend on Google Search ads. Reaches people already searching "
             "for what you sell.",
        tradeoff="The best intent there is, from a pool that runs out: beyond a "
                 "point, extra spend buys very little.",
        watch="Google Search rows in the paid media table; its CVR is usually the "
              "highest and its volume the lowest.",
        mistake="Treating it as a volume channel. It harvests demand; it does not "
                "create it.",
        related=["3.10", "3.1", "3.9"],
        guide="marketing"),
    "3.4": dict(
        does="Monthly spend on TikTok. The youngest audience and the cheapest "
             "attention.",
        tradeoff="Cheap reach, low intent. It depends on creative more than any "
                 "other channel.",
        watch="TikTok's CTR and CVR against Meta's in the paid media table.",
        mistake="Judging it on CPM. Cheap impressions from people who do not buy "
                "your products are the most expensive traffic there is.",
        related=["3.10", "3.8", "3.1"],
        guide="marketing"),
    "3.8": dict(
        does="Shoots, video and copywriting. Builds a creative quality score that "
             "raises what every rupee of paid media returns, most of all on "
             "TikTok.",
        tradeoff="It buys no traffic by itself, and the quality it builds decays "
                 "each month you stop.",
        watch="Creative quality on your dashboard; CTR across channels.",
        mistake="Cutting it first when cash is tight. The report looks fine for a "
                "month or two, then every channel gets more expensive at once.",
        related=["3.1", "3.4", "11.5"],
        guide="marketing"),
    "3.9": dict(
        does="Awareness advertising with no direct response. Builds brand equity, "
             "which drives organic traffic and makes paid traffic cheaper.",
        tradeoff="Pays back slowly: most of this month's effect lands over the "
                 "next two or three months, and it fades if you stop.",
        watch="Brand equity and organic sessions over several months, not one.",
        mistake="Judging it in the month you spend it. Teams that cut it look best "
                "early and worst by the second half.",
        related=["3.1", "3.8"]),
    "3.10": dict(
        does="Splits each ad budget into up to three campaigns and aims each one: "
             "which products, and to whom - age, gender, cities, interests, "
             "language, format, objective. On Google, keyword type and match. Can "
             "run campaigns 1 and 2 as an A/B test.",
        tradeoff="Sharper aim concentrates spend on likely buyers and shrinks the "
                 "audience; too small an audience for its budget gets tired and "
                 "expensive. Broad targeting is always the safe baseline.",
        watch="The paid media table: every campaign's CPM, CTR, CPC, CVR, ROAS, "
              "CAC, how much harder it worked than broad, and findings on what it "
              "missed.",
        mistake="One campaign for every product. Products bought by different "
                "people need different audiences.",
        related=["3.1", "3.2", "3.4"],
        guide="marketing"),
    "3.6": dict(
        does="Commission paid to affiliates and influencers on the sales they refer.",
        tradeoff="Costs nothing when nothing sells, but it is paid on every "
                 "referred order - including some that would have come to you "
                 "anyway.",
        watch="Contribution margin, and the marketing line of the P&L.",
        mistake="A high rate on a thin-margin range. The referred orders can lose "
                "money one by one.",
        related=["3.1", "1.1"]),
    "4.1": dict(
        does="Lists your range on the marketplace, which brings shoppers who would "
             "never find your own site.",
        tradeoff="Extra orders against a commission on each one, a payout that "
                 "arrives later, and customers who belong to the marketplace, not "
                 "to you.",
        watch="Revenue split, contribution margin and cash timing.",
        mistake="Counting marketplace revenue as if it were own-site revenue. The "
                "commission comes off the top, and you cannot remarket to those "
                "customers.",
        related=["1.1", "6.1"]),
    "5.1": dict(
        does="Site speed, search, product pages and checkout. Builds a UX score "
             "that lifts conversion and organic traffic.",
        tradeoff="The improvement lands the month after you spend, and it lifts "
                 "only the traffic you already have.",
        watch="Conversion rate the following month.",
        mistake="Spending on traffic while visitors bounce. Fix the store before "
                "paying to fill it.",
        related=["3.1", "11.1"]),
    "6.1": dict(
        does="SMS, WhatsApp, email and loyalty for existing customers. Cuts churn "
             "and lifts repeat purchase.",
        tradeoff="Returns flatten as you spend more, and it only works on customers "
                 "you already have.",
        watch="Repeat order share, active customers and LTV.",
        mistake="Starving it while buying new customers. Every customer who leaves "
                "has to be bought again at full CAC.",
        related=["8.5", "10.1", "2.2"]),
    "7.2": dict(
        does="Chooses who makes your stock. Suppliers differ in cost, lead time and "
             "minimum order size.",
        tradeoff="Cheap stock arrives slowly in large batches, tying up cash and "
                 "leaving you exposed if anything disrupts supply. Fast stock costs "
                 "more per unit.",
        watch="Gross margin, in-stock rate and inventory on the dashboard.",
        mistake="Choosing on unit cost alone. The cheapest supplier is only cheapest "
                "if nothing goes wrong.",
        related=["7.5", "7.1", "1.1"]),
    "7.1": dict(
        does="How many units to buy this month. Leave it blank and the system "
             "orders to your safety-stock target.",
        tradeoff="Too little and a good month sells out; too much and cash sits in "
                 "the warehouse.",
        watch="In-stock rate, lost sales to stock-outs, weeks of cover, cash.",
        mistake="Ordering to last month's sales in a month demand is about to move.",
        related=["7.5", "7.2", "11.2"]),
    "7.5": dict(
        does="The weeks of demand you hold on top of forecast.",
        tradeoff="More cover means fewer stock-outs and more cash locked in stock.",
        watch="In-stock rate and weeks of cover; cash balance.",
        mistake="Raising cover after a stock-out that was really a lead-time "
                "problem. Check the supplier first.",
        related=["7.1", "7.2", "11.2"]),
    "7.4": dict(
        does="Inspection and testing before stock ships. Cuts defects, returns and "
             "the reviews that follow them.",
        tradeoff="A steady cost against fewer returns and a better rating.",
        watch="Return rate and rating.",
        mistake="Treating returns as a courier problem when the product is the "
                "cause.",
        related=["1.5", "10.4"]),
    "8.2": dict(
        does="Share of orders handled by an outsourced warehouse (3PL) rather than "
             "your own.",
        tradeoff="Capacity with no capex, at a higher cost per order.",
        watch="Fulfilment cost per order and fill rate.",
        mistake="Keeping everything in-house through a peak month and running out "
                "of capacity.",
        related=["8.3"]),
    "8.3": dict(
        does="How deliveries are split between couriers. Couriers differ in cost, "
             "speed, success rate, rural reach and how quickly they pay you COD "
             "cash. Shares must add up to 100%.",
        tradeoff="Speed and reliability cost more per order; a cheap courier fails "
                 "more deliveries, and every failed delivery is a return you paid "
                 "for twice.",
        watch="Delivery success, RTO rate, delivery perception and cash timing.",
        mistake="Choosing on cost per order alone. Count the failed deliveries "
                "before calling a courier cheap.",
        related=["9.1", "8.2"]),
    "8.5": dict(
        does="What the order looks like when it arrives.",
        tradeoff="Better packaging lifts repeat purchase and cuts damage, at a "
                 "higher cost on every order.",
        watch="Repeat order share and rating.",
        mistake="Premium unboxing on a price-led range whose buyers do not come "
                "back for the box.",
        related=["6.1", "1.5"]),
    "9.1": dict(
        does="Whether customers can pay cash on delivery - how most Pakistani "
             "shoppers expect to pay.",
        tradeoff="COD wins orders. It also means parcels refused at the door, and "
                 "cash that reaches you weeks after you ship.",
        watch="Orders, RTO rate, COD receivable and cash.",
        mistake="Switching it off to fix returns. You fix the returns by losing "
                "most of the orders.",
        related=["9.2", "8.3"]),
    "9.2": dict(
        does="A discount for paying online instead of COD.",
        tradeoff="Shifts customers to prepaid - fewer refusals, faster cash - "
                 "and you pay for it with margin on every prepaid order.",
        watch="Payment mix, RTO rate, cash.",
        mistake="A discount so large it costs more than the refusals it prevents.",
        related=["9.1", "9.3"]),
    "9.3": dict(
        does="Who processes online payments. Gateways differ in success rate and "
             "fee.",
        tradeoff="A failed payment is a lost order, so the success rate matters "
                 "more than the fee.",
        watch="Conversion rate.",
        mistake="Picking the lowest fee and losing more in failed checkouts than "
                "the fee saved.",
        related=["9.1", "9.2"]),
    "10.1": dict(
        does="Agents handling calls, chat and complaints.",
        tradeoff="Each agent is a fixed monthly cost; too few and response times "
                 "slide.",
        watch="Service backlog now; churn and rating a month later.",
        mistake="Cutting the team in a busy month and paying for it in next "
                "month's churn.",
        related=["11.4", "6.1"]),
    "10.4": dict(
        does="Who pays when a customer sends something back.",
        tradeoff="Free returns convert best and invite the most returns; a "
                 "restocking fee cuts returns and weakens conversion.",
        watch="Return rate, conversion rate, rating.",
        mistake="Offering free returns on the products that come back most.",
        related=["7.4", "9.1"]),
    "11.1": dict(
        does="Builds a 'customers also bought' engine. Lifts average order value "
             "once it is live.",
        tradeoff="Capex paid up front, a build period, a monthly running cost, and "
                 "a chance the build fails. Built early it is worth more; the same "
                 "system built late delivers less.",
        watch="AOV after it goes live; capex and technology cost in the P&L.",
        mistake="Committing late, once the case is certain, and getting a fraction "
                "of the benefit.",
        related=["1.2", "5.1"]),
    "11.2": dict(
        does="Builds sharper demand forecasting: fewer stock-outs and less dead "
             "stock for the same cover.",
        tradeoff="Capex, a build period, a running cost and a real chance of "
                 "failure - against inventory that works harder every month after.",
        watch="Forecast error, in-stock rate, weeks of cover.",
        mistake="Buying it and keeping the same heavy safety stock, so the benefit "
                "never reaches your cash.",
        related=["7.5", "7.1"]),
    "11.3": dict(
        does="Prices that move with demand and rivals.",
        tradeoff="The most expensive build with the lowest odds of success; it "
                 "protects margin when it works.",
        watch="Gross margin; capex in the P&L.",
        mistake="Expecting it to fix a price position that is wrong to begin with.",
        related=["1.1", "2.2"]),
    "11.4": dict(
        does="Automated first-line support for routine contacts.",
        tradeoff="Fast to build and likely to work; it handles routine contacts, "
                 "not every complaint.",
        watch="Service backlog and CS cost.",
        mistake="Cutting the whole human team the month it goes live.",
        related=["10.1"]),
    "11.5": dict(
        does="Machine-generated ad creative.",
        tradeoff="Cheaper and faster than a production shoot, and caps how good "
                 "your creative can get.",
        watch="Creative quality and CTR.",
        mistake="Treating it as a replacement for all creative spend.",
        related=["3.8"]),
    "12.1": dict(
        does="Studies you commission on the Research page. Each answers one "
             "question, costs money, carries a margin of error, and some arrive a "
             "month late.",
        tradeoff="Research buys information, never advantage. It is only worth its "
                 "price if it changes a decision you are about to take.",
        watch="The Research page, where every finding sits beside the decision it "
              "bears on.",
        mistake="Buying studies you will not act on - paying twice, once for the "
                "study and once for the mistake it could have prevented.",
        related=[]),
    "12.5": dict(
        does="A short note on what you are trying to achieve this month and why. "
             "Your instructor reads it; the model ignores it.",
        tradeoff="Two minutes of writing against a month of decisions nobody can "
                 "explain afterwards.",
        watch="Next month's report, against what you said you expected.",
        mistake="Describing what you did instead of what you expect to happen. A "
                "memo that makes a prediction can be checked.",
        related=[]),
}

GUIDES = {"marketing": ("Performance marketing guide", "guide_marketing")}
