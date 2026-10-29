"""Session 11 - How Can AI Help? About 60 slides in three parts.

Run: python s11_slides.py <deck folder> [logo url]
Part 3's numbers come from tools/deck/s11_tests.py; Part 2, the toolkit,
is in s11_toolkit.py. Slide ids carry an "s11-"
prefix so the deck can sit beside Session 12's (tools/deck/s11_s12_slides.py).
"""
import pathlib, sys, json
HERE = pathlib.Path(__file__).parent
exec((HERE / "s7_slides.py").read_text().split("\nS = {}\n")[0])
FT = "Session 11 &middot; How Can AI Help?"
def sec(sid, bg, eyebrow, title, body, notes, footer=FT, **kw):
    return section(sid, bg, "#131316", eyebrow, title, body, notes, footer=footer, **kw)
def div(sid, part, title, line, notes):
    return divider(sid, part, title, line, notes).replace("Session 2 &middot; Finding the Right Idea", FT).replace("856d57cb939a323d46943b3b229572d7", "__LOGO__")
SIM = "Simulation test runs: six teams on every default, events off, twenty games each &middot; not market data"

def num4(n, L, T, W, H, label, num, text):
    """A figure card for four across: the number set smaller, to fit a 396px column."""
    return f'''  <div data-build-in="fade {n}" style="position:absolute; left:{L}px; top:{T}px; width:{W}px; height:{H}px; background:#ffffff; padding:30px 30px; border-radius:18px; border:1px solid #e4e4e7; display:flex; flex-direction:column; gap:10px">
    <p style="font-size:21px; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:#86868f">{label}</p>
    <p style="font-size:42px; font-weight:700; letter-spacing:-1px; line-height:1.1; color:#131316">{num}</p>
    <p style="font-size:23px; line-height:1.4; color:#55555f">{text}</p>
  </div>'''

S = {}
S["s11-cover"] = cover(11, "How Can AI Help?",
  "Recommendations, forecasting, customer service and creative &mdash; what each costs, how long it takes, and whether it pays back.",
  """About 60 slides in three parts, best taught as two sessions. Session A, two hours: 3 min recap, 8 min opening exercise, Part 1 theory about 65 min (the business case 10, recommendations 12, forecasting 12, customer service 12, creative 12, build or buy 7), exercise 10, Part 3 simulation about 30 min, 3 min close. Session B, about 90 minutes: Part 2, the toolkit (Shopify 30, Meta ads 30, Google Search 25, the audit exercise 10).

Month 9 has run; teams decide month 10. The four AI builds (11.1 recommendations, 11.2 forecasting, 11.4 customer service, 11.5 creative) are the session. In the Fall-2026 game they have been open since month 3, so some teams already own one; dynamic pricing (11.3) was withdrawn and refunded.

The idea for the day: an AI tool is an investment like a warehouse. It costs money up front, takes time, may not work, and pays back only through a number you can name.""", size=132).replace('id="cover"', 'id="s11-cover"')

S["s11-recall"] = sec("s11-recall", "#f5f5f6", "Where we got to last time", "Reading the numbers",
  grid([
    ("The equation", "Visits &times; conversion &times; basket", "Sales move because one of the factors moved, and each has its own fix.", "#ed0000"),
    ("Customers", "What one costs, and earns", "Acquisition cost against what a customer earns over time.", "#eb6834"),
    ("The dashboard", "Eight numbers, one page", "With a target, a trend and an owner for each.", "#2a78d6"),
  ], 3, 300, 300)
  + "\n" + band(4, 660, 170, "Last time: <b>knowing whether the business works</b>. Today: which AI tools would move those numbers &mdash; and <b>which would only cost money</b>.", size=31),
  """Three quick clicks from Session 10.

The bridge: every AI tool sold to an online shop promises to move one of last session's numbers. Today's test for each one is the same: which number, by how much, for what cost, and how soon.""")

S["s11-ex1"] = exercise("s11-ex1", "Exercise 1", "Would you buy it?",
  "A vendor offers a Pakistani skincare brand an AI assistant for its WhatsApp orders: PKR 1.8m up front and PKR 120,000 a month.",
  ["What would it have to save or earn each month to pay back in a year?", "Which number would tell you it is working?",
   "What could go wrong with your customers?", "Who answers when it cannot?"],
  "Exercise 1 &middot; an AI tool is an investment",
  """Eight minutes. One question per click. The brand and the offer are hypothetical.

Question 1: 1.8m over twelve months is 150,000 a month, plus the 120,000 running cost: it must save or earn about 270,000 a month. Ask the room what that is in agents' salaries, or in extra orders at the brand's profit per order.

Question 2: contacts answered without a person, response time, refused cash-on-delivery parcels (if it confirms orders), repeat purchase. Not "number of chats".

Questions 3 and 4 set up the customer-service case: wrong answers given confidently, angry customers stuck with a bot, and the hand-off to a person.""", top=500, h=180, cols=2)

S["s11-part1"] = div("s11-part1", "Part 1 &middot; Theory", "Where AI earns<br>its keep",
  "The business case for an AI tool, then four jobs it does in an online shop &mdash; each with a Pakistani and a global case.",
  """Part 1 follows the course outline: how AI helps an e-commerce business. Real-world practice only; the toolkit is Part 2 and the simulation Part 3.""")

S["s11-jobs"] = sec("s11-jobs", "#ffffff", "Four jobs AI does", "What AI does in an online shop",
  grid([
    ("Recommend", "What each shopper sees", "&ldquo;Customers also bought&rdquo;, search results and emails that differ by shopper.", "#ed0000"),
    ("Forecast", "How much stock to buy", "Predicting next month's demand, product by product, from sales and seasons.", "#eb6834"),
    ("Serve", "Answering customers", "Order status, cash-on-delivery confirmation, returns &mdash; on chat and WhatsApp.", "#2a78d6"),
    ("Create", "Ads, photos and copy", "Many versions of an ad, product photos and descriptions, made in minutes.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "Each job moves a different line: <b>basket, stock, service cost, ad cost</b>. Which line is biggest in your business?", size=31),
  """One job per click.

These are the four uses most online sellers meet first, and the four the simulation offers. Others exist (fraud screening of cash-on-delivery orders, pricing, search), but the question for each is the same: which number does it move?

The band is the key move of the session: an AI tool is worth what it does to one line of the P&L, not what it does in a demo.""")

S["s11-case-for"] = sec("s11-case-for", "#f5f5f6", "The business case", "An AI tool is an investment",
  grid([
    ("Cost up front", "Paid before it works", "Licences, set-up, data work, the people who build it.", "#ed0000"),
    ("Running cost", "Every month after", "Software fees, data, the staff who look after it.", "#eb6834"),
    ("Time", "Months to be useful", "Building, connecting your data, training staff.", "#2a78d6"),
    ("Chance", "It may not work", "Poor data, the wrong problem, customers who reject it.", "#1baf7a"),
  ], 4, 290, 340)
  + "\n" + band(5, 680, 190, "It pays back only if <b>(monthly gain &minus; running cost) &times; months live</b> beats the cost up front. Which of the four do vendors talk about least?", size=31),
  """One part per click.

The same arithmetic as any capital investment (a warehouse, a delivery fleet): money now, a gain later, and a risk that the gain never comes. AI tools add two twists. The gain is often uncertain until the tool has been running on your own data, and the advantage fades as rivals buy the same tool.

Vendors talk about the gain; ask about the other three.""")

payrows = [("Cost up front", "PKR 2,000,000", "Paid before it works"),
           ("Gain once live", "PKR 400,000 a month", "Extra profit, not extra revenue"),
           ("Running cost", "PKR 150,000 a month", "Software, data, people"),
           ("Net gain", "PKR 250,000 a month", "400,000 &minus; 150,000"),
           ("Payback", "8 months live", "2,000,000 &divide; 250,000"),
           ("If it works 4 times in 5", "10 months, on average", "2,000,000 &divide; (0.8 &times; 250,000)")]
S["s11-payback"] = sec("s11-payback", "#ffffff", "Working it out", "When does an AI tool pay for itself?",
  trows(["", "Example", "Where it comes from"], payrows, 276, [500, 440, 668], rh=70, size=27)
  + "\n" + band(7, 740, 150, "Add two months to build it: committed today, it pays back in a year &mdash; if it works. <b>How long will it stay ahead before every rival has it?</b>", size=29),
  """Illustrative numbers. One row per click.

Three traps. Counting the gain as revenue rather than profit (a 400,000 rise in sales might be 100,000 of profit). Forgetting the running cost. Ignoring the chance of failure: a tool that works four times in five is worth four-fifths of one that always works.

The last question is the obsolescence point: recommendation engines were once an edge and are now expected. The earlier a tool goes live, the longer it earns before everyone has it.""",
  footer="Illustrative numbers")

S["s11-recs"] = sec("s11-recs", "#f5f5f6", "Recommendations", "Showing each shopper the right next product",
  grid([
    ("Data", "What it learns from", "Orders, product views and carts &mdash; the more shoppers, the better it gets.", "#ed0000"),
    ("Where", "Where shoppers see it", "Product pages, the cart, search results, emails and WhatsApp messages.", "#eb6834"),
    ("Moves", "What it changes", "Basket size first; conversion and repeat orders if it is good.", "#2a78d6"),
    ("Fails", "Where it goes wrong", "A new shop with few orders, or the same best-sellers shown to everyone.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "A recommendation is worth the <b>profit on the extra item</b>, not its price. Which product would you want it to suggest?", size=31),
  """One idea per click.

Recommendation engines are the oldest AI in e-commerce: collaborative filtering ("people who bought this also bought") goes back to the 1990s. They need data, which is the catch for a small shop: with few orders, the suggestions are mostly the best-sellers, which a person could choose by hand.

Each extra item in the basket carries its own product cost but rides on the same delivery, which is why a bigger basket is one of the cheapest gains an online shop can get (Session 10).""")

S["s11-case-recs"] = cases("s11-case-recs", "Cases &middot; Recommendations", "Suggestions that sell &mdash; and numbers to check",
  ("Pakistan", "Daraz", "AskDaraz, July 2023", [
    ("What it is", "An in-app shopping assistant built on Microsoft&rsquo;s Azure OpenAI Service."),
    ("What it does", "Asks what a shopper needs, then suggests products and collections from millions of listings."),
    ("Who it is for", "Shoppers new to buying online; sellers get more visibility, Daraz said.")]),
  ("Global", "Amazon", "Recommendations", [
    ("The famous number", "McKinsey estimated in 2013 that 35% of what consumers buy on Amazon comes from recommendations."),
    ("The check", "A 2018 University of Florida study found a lift nearer 11%, and called such estimates hard to believe.")]),
  "Recommendations sell. <b>A vendor&rsquo;s number is not your number</b> &mdash; test it on your own shop.",
  """Two recommendation cases.

Daraz: in July 2023 Daraz launched AskDaraz, an in-app discovery chatbot built on Microsoft's Azure OpenAI Service (ChatGPT). Shoppers describe what they need; it refines the request and suggests products, styles and collections across categories. Daraz aimed it at South Asians new to online shopping and said sellers would gain visibility and new audiences. Company-reported.

Amazon: the figure that 35% of what consumers purchase on Amazon comes from recommendations is a 2013 McKinsey estimate, quoted ever since. Anuj Kumar of the University of Florida called such estimates hard to believe; his 2018 research put the overall sales lift from recommendations at about 11%. The lesson is not that recommendations fail, but that the size of the gain depends on the shop, and only a test on your own customers says what it is.

Sources: Daraz press release, ProPakistani (Jul 2023); McKinsey (2013) as reported by the University of Florida (2018).""",
  "Sources: Daraz, ProPakistani (Jul 2023); McKinsey (2013) via University of Florida (2018)")

S["s11-forecast"] = sec("s11-forecast", "#ffffff", "Forecasting", "Narrowing the error, not removing it",
  grid([
    ("Inputs", "What it reads", "Past sales, seasons, Eid and 11.11, promotions, searches, even weather.", "#ed0000"),
    ("Gain", "What it improves", "Fewer stock-outs for the same stock &mdash; or less stock for the same service.", "#eb6834"),
    ("Limit", "What it cannot do", "Shorten the supplier&rsquo;s lead time, or see a one-off shock coming.", "#2a78d6"),
    ("Catch", "Where the cash comes from", "Only if you then hold less safety stock. Same stock, same cash.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "Safety stock exists because forecasts are wrong. <b>Halve the error and you can hold less</b> &mdash; if you are brave enough to.", size=31),
  """One idea per click.

Session 9 set safety stock as the buffer against forecast error and supplier delay. A better forecast does not change the supplier's lead time; it narrows how wrong next month's estimate is likely to be, so the same service level needs less buffer.

The catch is behavioural: a team that buys better forecasting and keeps the same heavy safety stock has paid for the tool and kept the cash tied up in stock.""")

fcrows = [("Forecast typically wrong by", "&plusmn;20%", "&plusmn;12%"),
          ("Safety stock for the same service", "4 weeks", "2.4 weeks"),
          ("Stock held, at PKR 1.5m of cost a week", "PKR 6.0m", "PKR 3.6m"),
          ("Cash freed", "", "PKR 2.4m")]
S["s11-forecast-ex"] = sec("s11-forecast-ex", "#f5f5f6", "Working it out", "Same service, less stock",
  trows(["", "Before", "With a better forecast"], fcrows, 276, [700, 400, 508], rh=80, size=28)
  + "\n" + band(5, 680, 190, "The tool is paid for by the cash it frees and the sales it saves. <b>What would you do with PKR 2.4m that is no longer on a shelf?</b>", size=30),
  """Illustrative numbers. One row per click.

Safety stock scales roughly with forecast error: cut the error by 40% and the same service needs about 40% less buffer. The freed cash is a one-off; the saving each month is the cost of holding that stock (the warehouse, the money, the stock that ages).

Pair it with Session 9: lead time is the supplier's, error is the forecast's. Forecasting attacks the second.""",
  footer="Illustrative numbers")

S["s11-case-forecast"] = cases("s11-case-forecast", "Cases &middot; Forecasting", "Better guesses about next month",
  ("Pakistan", "Daraz", "11.11, 2021", [
    ("The plan", "AI, predictive algorithms and big data to give its sellers demand forecasts before the sale."),
    ("Why", "So sellers could pre-stock the right quantity in the right place, it said."),
    ("The peak", "13,000 delivery staff, 4,000 vehicles and seven logistics partners lined up.")]),
  ("Global", "Walmart", "Holiday season, 2023", [
    ("The model", "Machine learning on each store&rsquo;s past sales and the weather, for 4,700+ US stores."),
    ("The upgrade", "In 2023 it added what shoppers search for, after 2021&rsquo;s excess stock."),
    ("The limit", "History cannot prepare you for a one-off shock like Covid-19, its executive said.")]),
  "Forecasting narrows the error; it never removes it. <b>The gain reaches cash only when you hold less stock.</b>",
  """Two forecasting cases.

Daraz: ahead of 11.11 in 2021 Daraz said it would use artificial intelligence, predictive algorithms and big-data analytics to give sellers demand forecasts, so they could pre-stock the right quantity in the right location; it also announced 13,000 delivery staff, 4,000 vehicles and seven logistics partners for the event. Company-reported plans.

Walmart: Reuters reported that Walmart's machine-learning forecasting uses weather patterns and each store's past sales to predict inventory needs across its 4,700+ US stores. For holiday 2023, Retail Brew reported, the system was upgraded to read how people were searching, designed to meet demand without the excess inventory of 2021. Its senior vice president Parvez Musani said historical data does not prepare a retailer for one-off disruptions such as Covid-19.

Sources: ProPakistani (Oct 2021); Reuters; Retail Brew (Oct 2023).""",
  "Sources: ProPakistani (Oct 2021); Reuters; Retail Brew (Oct 2023)")

S["s11-service"] = sec("s11-service", "#ffffff", "Customer service", "Automating the routine, keeping the people",
  grid([
    ("Routine", "What it handles well", "Where is my order, confirming cash on delivery, sizes, the returns policy.", "#ed0000"),
    ("Language", "Where customers are", "WhatsApp and chat, in Urdu, Roman Urdu and English, at any hour.", "#eb6834"),
    ("Hand-off", "When a person takes over", "Complaints, refunds and anything the bot is unsure of.", "#2a78d6"),
    ("Risk", "Where it goes wrong", "Wrong answers given confidently, and customers stuck with no way out.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "The saving is real only at volume: a bot that replaces two agents must cost less than <b>two agents</b>.", size=31),
  """One idea per click.

Most contacts to an online shop in Pakistan are routine: order status, cash-on-delivery confirmation calls, delivery times, exchanges. These are what a bot handles well, on the channel customers already use. A complaint or a refund is where a customer decides whether to come back, and where a person is worth the cost.

The band is the arithmetic that decides it for a small brand: automation pays when it replaces a lot of work. A business with a handful of agents saves a handful of salaries.""")

S["s11-case-service"] = cases("s11-case-service", "Cases &middot; Customer service", "How far to automate",
  ("Pakistan", "J.", "JBot, October 2020", [
    ("What it is", "A 24/7 shopping assistant on WhatsApp &mdash; the first for a Pakistani e-retail brand, J. said."),
    ("Why", "To handle the rush of online orders through its digital channels."),
    ("The safety net", "Shoppers can ask for a person at any point.")]),
  ("Global", "Klarna", "AI assistant, 2024&ndash;2025", [
    ("The claim, 2024", "Two-thirds of chats and 2.3m conversations in its first month: the work of 700 agents."),
    ("The reversal, 2025", "Cost had been too dominant and quality fell, its CEO said; it began hiring people again.")]),
  "Automate the routine contacts. <b>Keep a person for the ones that decide whether a customer comes back.</b>",
  """Two customer-service cases.

J. (Junaid Jamshed): in October 2020 J. launched JBot, a round-the-clock WhatsApp assistant, described as the first WhatsApp chatbot from a Pakistani e-retail brand, to handle the influx of online orders across its digital channels; customers can connect with a representative when needed. Company-reported.

Klarna: in February 2024 Klarna said its OpenAI-powered assistant handled two-thirds of customer-service chats in its first month, 2.3 million conversations, the work of about 700 full-time agents, with satisfaction on a par with humans and an estimated $40m profit improvement for 2024. In May 2025 its chief executive Sebastian Siemiatkowski told Bloomberg that cost had been too predominant a factor and the result was lower quality; Klarna began recruiting human agents again, describing a dual track of AI and human support.

Sources: ProPakistani (Oct 2020), Dawn Images (Nov 2020); CX Today, TechRadar (Feb 2024); Bloomberg as reported by Maginative and Tech.co (May 2025).""",
  "Sources: ProPakistani, Dawn Images (2020); CX Today (Feb 2024); Bloomberg via Tech.co (May 2025)")

S["s11-creative"] = sec("s11-creative", "#f5f5f6", "Creative", "Cheaper and faster &mdash; and rarely the best",
  grid([
    ("Volume", "Many versions to test", "Ten headlines and five images instead of one, so the market picks.", "#ed0000"),
    ("Speed", "Days, not weeks", "Product photos, descriptions and short videos without a shoot.", "#eb6834"),
    ("Ceiling", "Good enough, rarely great", "Generic, sometimes uncanny; the brand&rsquo;s own voice gets lost.", "#2a78d6"),
    ("Trust", "What customers accept", "Fake-looking faces, real people&rsquo;s likeness, and saying it was made by AI.", "#1baf7a"),
  ], 4, 290, 380)
  + "\n" + band(5, 720, 150, "AI <b>raises the floor and lowers the cost</b> of creative. It rarely makes the ad people remember.", size=31),
  """One idea per click.

For a small brand the real gain is volume and speed: testing many versions of an ad (Session 7) used to need a production budget; now it needs an afternoon. The risk is sameness: when every brand uses the same tools, the ads look alike, and the ones that stand out are still made with care.

Trust is the other risk: would your customers trust a face they suspect was generated, and would they mind if they found out?""")

S["s11-case-creative"] = cases("s11-case-creative", "Cases &middot; Creative", "Made by machine &mdash; and judged by people",
  ("Pakistan", "Nescaf&eacute;", "Chilled coffee, 2023", [
    ("The campaign", "Twelve Instagram reels: four AI-generated with influencers, eight shot normally."),
    ("The claim", "Pakistan&rsquo;s first AI-generated campaign, the brand team said."),
    ("The aim", "Reach Gen Z through creators rather than celebrities.")]),
  ("Global", "Coca-Cola", "Holidays Are Coming, 2024", [
    ("The remake", "An AI-made version of its 1995 holiday ad, made in about a month instead of a year."),
    ("The reaction", "It tested well, then was called soulless and creepy once it aired.")]),
  "AI makes creative cheaper and faster. <b>Whether it is good enough is the customer&rsquo;s call</b>, not the tool&rsquo;s.",
  """Two creative cases.

Nescaf&eacute; Pakistan: its chilled ready-to-drink coffee campaign, launched in October 2023 with Red Publicis, ran twelve reels, four of them AI-generated featuring Instagram creators and eight conventional; the brand team called it Pakistan's first AI-generated campaign, aimed at Gen Z through creators rather than celebrities. Company-reported (Aurora, January 2024).

Coca-Cola: its 2024 holiday ad remade the 1995 "Holidays Are Coming" spot with AI; the company said AI cut the timeline from about a year to a month. It tested positively before release (System1), then drew a backlash as "soulless" and "creepy", with critics pointing to distorted wheels and faces.

Sources: Aurora, Dawn (Jan 2024); Adweek, Business Today (Nov 2024).""",
  "Sources: Aurora, Dawn (Jan 2024); Adweek, Business Today (Nov 2024)")

S["s11-buildbuy"] = sec("s11-buildbuy", "#ffffff", "Build, buy or wait", "Which AI should a small brand own?",
  grid([
    ("Buy a tool", "Live in days", "A monthly fee, little risk &mdash; and the same tool your rivals can buy.", "#ed0000"),
    ("Build your own", "An edge, if your data is", "Months of work, costs up front, may fail. Worth it only where you know more.", "#2a78d6"),
    ("Wait", "Let others prove it", "Cheaper and safer later; worth less, because rivals got there first.", "#1baf7a"),
  ], 3, 290, 340)
  + "\n" + band(4, 680, 190, "For most small brands: <b>buy, measure, and build only where your own data is the advantage</b>. Which of your numbers would you trust a tool with?", size=31),
  """One option per click.

The build-or-buy question is old, but AI sharpens it: off-the-shelf tools (shop-platform recommendation apps, the ad platforms' own AI, WhatsApp bot services) are cheap and quick, and give no lasting edge because everyone can buy them. Building only pays where the business has data or a problem nobody else has.

Waiting is a real option, not a failure: the price falls and the risk falls. What is lost is the months of gain, and in a competitive market, the head start.""")

S["s11-ex2"] = exercise("s11-ex2", "Exercise 2", "Which AI first?",
  "A Pakistani skincare brand: about 3,500 orders a month, four service agents, three weeks of stock, most orders cash on delivery.",
  ["Which of the four would you buy first &mdash; and why that one?", "What must change in your numbers for it to pay back within a year?",
   "What would you stop doing the month it goes live?", "Which number in month one tells you it works?"],
  "Exercise 2 &middot; one tool, one number",
  """Ten minutes in teams. One question per click. The brand is hypothetical.

Push for one number per tool: basket size for recommendations, stock held and stock-outs for forecasting, agents and response time for service, ad cost per order for creative. Question 3 is the one teams miss: a tool pays only if something else changes (less safety stock, fewer agents, less spent on shoots).

Take two teams' answers and compare the arithmetic.""", top=500, h=180, cols=2)

S["s11-part2"] = div("s11-part2", "Part 3 &middot; The simulation", "AI in the simulation",
  "Four builds: recommendations, forecasting, customer service and creative. Each costs money up front, takes time, may fail &mdash; and the game ends in month 12.",
  """Part 3 is the simulation. Month 9 has run; teams decide month 10. In the Fall-2026 game the builds have been open since month 3: some teams own one, some saw one fail. Dynamic pricing (11.3) was withdrawn because it did nothing, and teams that paid for it were refunded.

Every number in Part 3 is the simulation's assumption or a test run of it, not market data.""")

S["s11-category"] = sec("s11-category", "#f5f5f6", "The category online", "AI in Pakistani online retail today",
  grid([
    ("Discovery", "Marketplace assistants", "Daraz&rsquo;s AskDaraz suggests products from a shopper&rsquo;s own words (2023).", "#ed0000"),
    ("Service", "WhatsApp assistants", "J. launched a 24/7 WhatsApp shopping assistant in 2020.", "#eb6834"),
    ("Ads", "AI-made campaigns", "Nescaf&eacute; (2023) and Zong (2025) ran partly or wholly AI-generated ads.", "#2a78d6"),
    ("Stock", "Forecasts for sellers", "Daraz promised its sellers demand forecasts before 11.11 (2021).", "#1baf7a"),
  ], 4, 290, 380, bsize=24)
  + "\n" + band(5, 720, 150, "The simulation&rsquo;s teams sell personal care and home care online in Pakistan. <b>Which of these would a brand your size buy, not build?</b>", size=30),
  """The real category first. One card per click.

All four are company announcements, not measured results: AskDaraz (Daraz, July 2023); JBot (J., October 2020); Nescaf&eacute;'s chilled coffee reels (Aurora, January 2024) and Zong 4G's AI-generated television campaign for the ICC Champions Trophy (February 2025); Daraz's 11.11 seller forecasts (October 2021).

Notice what a small brand can buy off the shelf (WhatsApp bots, AI ad tools, a shop platform's recommendation app) and what only a marketplace with millions of shoppers can build.""",
  footer="Sources: ProPakistani (2020, 2021, 2023); Aurora, Dawn (Jan 2024); MEA Tech Watch (Feb 2025)")

buildrows = [("Recommendations (11.1)", "3.0m", "2 months", "250k", "85%", "Basket value about 7% higher"),
             ("AI forecasting (11.2)", "2.2m", "2 months", "180k", "80%", "Forecast error cut by 40%"),
             ("AI customer service (11.4)", "1.8m", "1 month", "120k", "90%", "Each agent answers 2.5&times; as much"),
             ("AI creative (11.5)", "1.2m", "1 month", "90k", "75%", "Creative quality capped at 0.75")]
S["s11-sim-builds"] = sec("s11-sim-builds", "#ffffff", "In the simulation", "Four builds, four price tags",
  trows(["Build", "Up front", "Build time", "A month", "Works", "Once live"], buildrows, 276,
        [480, 170, 210, 160, 140, 448], rh=92, size=25, head_size=20)
  + "\n" + band(5, 720, 150, "All in PKR. <b>Which build touches the line your report says is weakest?</b>", size=31),
  """One build per click. The costs, timings and chances are the simulation's.

Recommendations: lifts the value of every basket by about 7% once live (6&ndash;9% in its first month, and less the later it is built: about half when it goes live in month 12).
AI forecasting: cuts the error of the forecast your stock order is planned on by 40% (the error's spread falls from 16% to 9.6%). It does not shorten the supplier's lead time.
AI customer service: multiplies what each agent can answer by 2.5. It saves money only if the team is cut to match.
AI creative: in this game it caps creative quality at 0.75 while production spend (3.8) is under PKR 300,000 a month. It does not lower the cost of production.
Dynamic pricing (11.3) was withdrawn and refunded.

These are the simulation's assumptions, not market data.""",
  footer="Costs, timings and effects from the simulation &middot; not market data")

S["s11-sim-rules"] = sec("s11-sim-rules", "#f5f5f6", "In the simulation", "How a build works",
  grid([
    ("Paid at once", "Cash leaves now", "The full cost leaves your cash the month you commit. It is never refunded.", "#ed0000"),
    ("Then rolled", "It works or it fails", "Decided when the build completes. A failed build shows on the form; trying again is a new build.", "#eb6834"),
    ("Running cost", "Every month after", "Once live, a fixed cost in the technology line of your P&amp;L.", "#2a78d6"),
    ("Timing", "Months left", "Committed for month 10, a two-month build is live in month 12 only.", "#1baf7a"),
  ], 4, 290, 400, bsize=24)
  + "\n" + band(5, 740, 130, "The cost up front hits your <b>cash</b>; the running cost hits your <b>profit</b>. Both are on the scorecard.", size=30),
  """One rule per click. The rules are the simulation's.

The cost up front is capital spending: it reduces cash (and so runway and the cash the business generated) but does not appear in EBITDA. The running cost is in the P&amp;L every month the build is live. A build that fails costs its full price and nothing after.

Committed for month 10: recommendations and forecasting go live in month 12; customer service and creative in month 11. The form shows each build's status: live, building, or failed, and what Yes would do now.""",
  footer="Decision rules from the simulation &middot; not market data")

early = [("Recommendations", "17 of 20", "+2.51m", "&minus;0.67m", "+4.9"),
         ("AI forecasting", "17 of 20", "&minus;1.19m", "&minus;3.21m", "&minus;1.1"),
         ("&hellip; and safety stock cut to 2 weeks", "17 of 20", "&minus;0.95m", "&minus;1.35m", "&minus;0.3"),
         ("AI customer service", "19 of 20", "&minus;1.03m", "&minus;2.90m", "&minus;0.6"),
         ("&hellip; and the team cut to 2 agents", "19 of 20", "&minus;0.16m", "&minus;1.98m", "&minus;0.6"),
         ("AI creative", "14 of 20", "&minus;0.57m", "&minus;1.80m", "&minus;0.4")]
S["s11-sim-early"] = sec("s11-sim-early", "#ffffff", "In the simulation", "Built in month 3: worth it by month 12?",
  trows(["Build", "Worked", "EBITDA", "Cash", "Score"], early, 276, [640, 230, 250, 250, 238], rh=70, size=25, head_size=20)
  + "\n" + band(7, 770, 130, "Only recommendations came close to paying for itself. The rest needed the business run differently &mdash; and <b>still cost more than they saved</b>.", size=29),
  """One build per click. Each line is one team committing to one build in month 3 against an identical team on every default, both played to month 12, in twenty games each; the figures are the averages, so the failed builds are in them (tools/deck/s11_tests.py). EBITDA is months 3&ndash;12; cash is at month 12, net of the loan; score is the final score before decision quality.

Recommendations: about +0.4m of EBITDA a month once live, after its 250k running cost; cash nearly back by month 12.
Forecasting alone: better forecasts, the same stock, so only the cost shows. Cutting safety stock to two weeks with it held every order (two weeks without it lost 533 orders in one game) and freed stock, but not enough to pay for the build.
Customer service alone saves nothing: four agents were already enough. Cut to two agents, it held service (two agents without it left 9,648 contacts waiting and NPS fell from 83 to 45), but two agents cost 96,000 a month and the build 120,000.
Creative: no change at the default production budget; only its cost shows.

Directions, not forecasts.""",
  footer=SIM)

now = [("Recommendations", "14 of 20", "+0.10m", "&minus;3.05m", "+0.9"),
       ("AI forecasting", "17 of 20", "&minus;0.15m", "&minus;2.39m", "&minus;0.1"),
       ("&hellip; and safety stock cut to 2 weeks", "17 of 20", "&minus;0.13m", "&minus;1.37m", "0.0"),
       ("AI customer service", "19 of 20", "&minus;0.23m", "&minus;2.06m", "&minus;0.1"),
       ("&hellip; and the team cut to 2 agents", "19 of 20", "+0.01m", "&minus;1.91m", "&minus;0.6"),
       ("AI creative", "14 of 20", "&minus;0.13m", "&minus;1.34m", "&minus;0.2")]
S["s11-sim-now"] = sec("s11-sim-now", "#f5f5f6", "In the simulation", "Committed now, for month 10",
  trows(["Build", "Worked", "EBITDA", "Cash", "Score"], now, 276, [640, 230, 250, 250, 238], rh=70, size=25, head_size=20)
  + "\n" + band(7, 770, 130, "Committed now, <b>no build earns back its cost before the game ends</b>. What would a founder whose business carries on decide?", size=29),
  """One build per click. The same test with the build committed for month 10, months 10&ndash;12 (tools/deck/s11_tests.py), twenty games each.

With two or three months left, no build repays its cost up front: every line leaves less cash at month 12. Recommendations still lifts the final score a little, because month 12 carries the most weight and the margin improves; it also gives back less in its one live month, because it is built late. Cutting agents in month 10, before the service build is live in month 11, costs a month of service.

The discussion: the game ends in month 12; a real business does not. A founder judges payback over the tool's life. Ask teams which they are deciding for, and to say so in the memo.""",
  footer=SIM)

S["s11-sim-live"] = sec("s11-sim-live", "#ffffff", "In the simulation", "What each build changed once live",
  "\n".join(num4(i + 1, 128 + i * 422, 290, 396, 380, lab, num, text) for i, (lab, num, text) in enumerate([
    ("Recommendations", "2,959 &rarr; 3,166", "Average basket, PKR, month 12: about 7% more on every order."),
    ("Forecasting", "14.2% &rarr; 11.2%", "Average forecast miss. With two weeks&rsquo; safety stock: 24% less stock, no orders lost."),
    ("Customer service", "0 waiting", "With two agents. Without it, two agents left 9,648 contacts waiting and NPS fell to 45."),
    ("Creative", "0.653 &rarr; 0.653", "Creative quality at the default budget: no change. At PKR 290k it held quality to 0.750."),
  ]))
  + "\n" + band(5, 720, 150, "Each build moved one number. <b>Whether it paid depended on what else the team changed.</b>", size=31),
  """One build per click. Month 12 of one game, each build committed in month 3 against the team on every default (tools/deck/s11_tests.py).

Recommendations: average basket PKR 2,959 against 3,166.
Forecasting: the stock order's forecast missed by 14.2% on average without it, 11.2% with it; with safety stock at two weeks the team held 2,874 units at month 12 against 3,780 and lost no orders.
Customer service: with two agents and the build, no backlog; with two agents and no build, 9,648 contacts waiting by month 12, rating 4.10 down to 3.79, NPS 83 down to 45.
Creative: creative quality 0.653 either way at the default PKR 200,000 of production; at PKR 290,000 it reached 0.760 without the build and 0.750 with it.

These are the simulation's assumptions and results, not market data.""",
  footer="Simulation test run: one game, six teams on every default, events off &middot; not market data")

S["s11-checks"] = sec("s11-checks", "#fdeceb", "Before month 10 runs", "Four questions before you build",
  grid([
    ("Months left", "Will it be live long enough?", "A two-month build committed now is live in month 12 only.", "#ed0000"),
    ("Cash", "Can you pay for it?", "The cost up front comes out of this month&rsquo;s cash.", "#eb6834"),
    ("Change", "What will you stop?", "Less safety stock, fewer agents, smaller shoots.", "#2a78d6"),
    ("Proof", "Which number shows it?", "Name it in the memo, and look for it next month.", "#1baf7a"),
  ], 4, 300, 340)
  + "\n" + band(5, 700, 150, "Say in the board memo <b>what the build must change, and by when</b> &mdash; or why you chose not to build.", size=30),
  """One question per click, while teams review their report and the decision form.

Logistics for the notes, not the slide: decisions for month 10 close at [deadline]. The form shows each build's status and what Yes would do now. Months 11 and 12 are decided before Session 12, which reviews the final results.""")

S["s11-next"] = sec("s11-next", "#131316", "Next session", "How do you grow?",
  grid([
    ("Session 12", "Growth", "New channels, new markets, and paying for growth.", "#ff3b3b"),
    ("The results", "Twelve months", "The final scorecard, against the plan you wrote in month 0.", "#ff3b3b"),
    ("Your story", "What you present", "The decisions that mattered, and what you would do next.", "#ff3b3b"),
  ], 3, 300, 300, bg="#1f1f24", border="border:1px solid #33333b;", tcol="#ffffff", bcol="#c9c9d1")
  + "\n" + band(4, 660, 150, "Two months left to decide. Next time: <b>what your twelve months added up to</b> &mdash; and where you would take the business next.", bg="#ed0000", size=31),
  """Close. One card per click.

Months 11 and 12 are decided before Session 12. Session 12 covers growth in theory, then the final scorecard and the teams' presentations.""", dark=True, eyecol="#ff3b3b")

ORDER = ["s11-cover", "s11-recall", "s11-ex1", "s11-part1", "s11-jobs", "s11-case-for", "s11-payback",
         "s11-recs", "s11-case-recs", "s11-forecast", "s11-forecast-ex", "s11-case-forecast",
         "s11-service", "s11-case-service", "s11-creative", "s11-case-creative", "s11-buildbuy", "s11-ex2",
         "s11-part2", "s11-category", "s11-sim-builds", "s11-sim-rules", "s11-sim-early", "s11-sim-now",
         "s11-sim-live", "s11-checks", "s11-next"]
SECTIONS = {
    "s11-open": {"description": "Session 11 · How can AI help?", "start": "s11-cover"},
    "s11-case": {"description": "Part 1 · The business case for an AI tool, and recommendations, with cases", "start": "s11-part1"},
    "s11-ops": {"description": "Forecasting and customer service, with cases", "start": "s11-forecast"},
    "s11-create": {"description": "Creative, and build or buy", "start": "s11-creative"},
    "s11-sim": {"description": "Part 3 · AI in the simulation", "start": "s11-part2"}}

# Part 2, the toolkit - Shopify, Meta ads and Google Search - between the theory
# and the simulation, in its own sections so it can become a session of its own.
exec((HERE / "s11_toolkit.py").read_text())
_at = ORDER.index("s11-part2")
ORDER = ORDER[:_at] + TOOLKIT_ORDER + ORDER[_at:]
SECTIONS = ({k: v for k, v in SECTIONS.items() if k != "s11-sim"} | TOOLKIT_SECTIONS
            | {"s11-sim": SECTIONS["s11-sim"]})

if __name__ == "__main__":
    write(S, ORDER, "Session 11 — How Can AI Help?", SECTIONS)
