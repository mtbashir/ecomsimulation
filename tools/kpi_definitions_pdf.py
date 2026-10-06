from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import sys

F = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("D", F + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DB", F + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DM", F + "DejaVuSansMono.ttf"))
from reportlab.lib.fonts import addMapping
addMapping("D", 0, 0, "D"); addMapping("D", 1, 0, "DB"); addMapping("D", 0, 1, "D"); addMapping("D", 1, 1, "DB")

INK = colors.HexColor("#131316"); RED = colors.HexColor("#ed0000"); GREY = colors.HexColor("#55555f")
LIGHT = colors.HexColor("#f5f5f6"); LINE = colors.HexColor("#e4e4e7"); TINT = colors.HexColor("#fdeceb")

st = {
 "title": ParagraphStyle("t", fontName="DB", fontSize=24, leading=29, textColor=INK, spaceAfter=4),
 "eyebrow": ParagraphStyle("e", fontName="DB", fontSize=8.5, leading=11, textColor=RED, spaceAfter=4),
 "h1": ParagraphStyle("h1", fontName="DB", fontSize=15, leading=19, textColor=INK, spaceBefore=10, spaceAfter=3),
 "lead": ParagraphStyle("l", fontName="D", fontSize=9.3, leading=13.2, textColor=GREY, spaceAfter=7),
 "body": ParagraphStyle("b", fontName="D", fontSize=9.3, leading=13.2, textColor=INK, spaceAfter=5),
 "cell": ParagraphStyle("c", fontName="D", fontSize=8, leading=10.6, textColor=INK),
 "cellg": ParagraphStyle("cg", fontName="D", fontSize=8, leading=10.6, textColor=GREY),
 "cellb": ParagraphStyle("cb", fontName="DB", fontSize=8.3, leading=10.8, textColor=INK),
 "head": ParagraphStyle("h", fontName="DB", fontSize=7.2, leading=9, textColor=GREY),
 "f": ParagraphStyle("f", fontName="DM", fontSize=7.5, leading=10.3, textColor=INK),
 "note": ParagraphStyle("n", fontName="D", fontSize=7.8, leading=10.6, textColor=GREY, spaceBefore=3),
}
P = lambda s, k="cell": Paragraph(s, st[k])

def kpi_table(rows):
    data = [[P("KPI", "head"), P("What it tells you", "head"), P("How it is calculated", "head"), P("Better", "head")]]
    for name, meaning, formula, better in rows:
        data.append([P(name, "cellb"), P(meaning, "cellg"), P(formula, "f"), P(better, "cell")])
    t = Table(data, colWidths=[30*mm, 46*mm, 88*mm, 14*mm], repeatRows=1)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, 0), 1.0, INK),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.5), ("RIGHTPADDING", (0, 0), (-1, -1), 3.5),
    ]))
    return t

def section(story, num, title, lead, rows, note=None):
    part = [Paragraph(f"{num} &middot; {title.upper()}", st["eyebrow"]), Paragraph(title, st["h1"]),
            Paragraph(lead, st["lead"]), kpi_table(rows)]
    if note:
        part.append(Paragraph(note, st["note"]))
    story.append(KeepTogether(part))
    story.append(Spacer(1, 8))

UP, DOWN = "Higher", "Lower"
story = []
story.append(Paragraph("E-COMMERCE SIMULATION &middot; LUMS CES", st["eyebrow"]))
story.append(Paragraph("Monthly results: what every KPI means and how it is calculated", st["title"]))
story.append(Paragraph(
  "Every number in your monthly report is calculated by the simulation engine from the decisions you submitted "
  "and the market's response. This guide gives each KPI in the order the report shows it — Growth, Marketing, "
  "Commercial, Operations, Customer, Finance — followed by the profit and loss lines they are built from and "
  "the paid-campaign table. Formulas are written exactly as the engine computes them. Fixed numbers inside "
  "the formulas (for example 2.424 units per order or a 1.2% COD fee) are the simulation's assumptions, not "
  "measured market data.", st["lead"]))

legend = Table([[P("<b>How to read the formulas.</b> × multiply · ÷ divide · Σ add up over the items named · "
                   "min( ) the smallest of · max( ) the largest of · <i>t</i> this month, <i>t−1</i> last month. "
                   "“Better” says which direction is good news; the report colours the change the same way.", "cell")]],
               colWidths=[178*mm])
legend.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("LEFTPADDING", (0, 0), (-1, -1), 8),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
story += [legend, Spacer(1, 10)]

section(story, 1, "Growth", "How big the business is this month, and where the orders came from.", [
 ("Net revenue", "Money you keep from sales after everything that never turned into a paid order.",
  "Gross revenue − prepaid discount − returned orders × AOV − refused (RTO) orders × AOV − failed deliveries × AOV<br/>"
  "Gross revenue = Orders × AOV", UP),
 ("Orders", "Orders placed this month.",
  "min( Demand potential, Traffic capacity, Stock capacity )<br/>"
  "Traffic capacity = new-visitor sessions × conversion + returning sessions × conversion × 2.6", UP),
 ("Sessions", "Visits to your store and listings.",
  "Paid sessions (each ad channel, with diminishing returns on spend) + organic sessions (brand equity, store "
  "experience, size of customer base) + returning-customer sessions + marketplace sessions", UP),
 ("Conversion rate", "Share of visits that became an order.",
  "Orders ÷ Sessions<br/>Driven by: price against market × store experience × last month's rating × in-stock × "
  "payment success (gateway, +18% with COD) × delivery reliability × range fit", UP),
 ("AOV", "Average order value, net of discount, excluding delivery charges.",
  "Average list price × 2.424 units × (1 − discount rate) × (1 + bundle uplift) × free-delivery-threshold uplift "
  "× (1 + recommendation uplift) × (1 − prepaid-incentive effect)", UP),
 ("Market share", "Your slice of all teams' sales.",
  "Your net revenue ÷ total net revenue of every team in the game", UP),
])

section(story, 2, "Marketing", "What winning customers cost, and the assets that make it cheaper over time.", [
 ("Blended CAC", "Average cost of each new customer, counting all marketing.",
  "Marketing spend ÷ New customers", DOWN),
 ("Reported ROAS", "Return on ad spend as the ad platforms report it.",
  "(Net revenue ÷ Marketing spend) × 1.32<br/>Platforms over-claim by about a third. The true figure "
  "(without the 1.32) is available only through the Attribution research study.", UP),
 ("Creative quality", "How good your ads are, 0 to 1. Raises paid traffic per rupee.",
  "CQ<sub>t</sub> = CQ<sub>t−1</sub> × (1 − 0.15) + 0.12 × √(creative spend ÷ 300,000)<br/>kept between 0 and 1", UP),
 ("New customers", "First-time buyers this month.",
  "(Orders − Repeat orders) ÷ 1.0 orders per new customer", UP),
 ("Marketing spend", "Everything spent to win or keep customers.",
  "Paid channels, creative and brand-building (3.1–3.9) + CRM &amp; retention (6.1) + affiliate commission "
  "(3.6, a share of net revenue)", "—"),
 ("Brand equity", "How well known and liked the brand is, 0 to 1. Raises organic traffic.",
  "BE<sub>t</sub> = BE<sub>t−1</sub> × (1 − 0.08) + 0.05 × (0.2 × brand spend<sub>t</sub> + 0.5 × "
  "spend<sub>t−1</sub> + 0.3 × spend<sub>t−2</sub>) ÷ 400,000<br/>kept between 0 and 1; peaks a month after spending", UP),
], note="Marketing spend has no colour in the report: more is neither good nor bad on its own. Judge it through CAC and contribution.")

section(story, 3, "Commercial", "Whether each order makes money, at three levels of the P&amp;L.", [
 ("Gross margin", "What is left after the product itself.",
  "Gross profit ÷ Net revenue<br/>Gross profit = Net revenue − cost of goods that stayed sold − write-off of returns "
  "that could not be resold (22% of returns)", UP),
 ("Contribution margin", "What is left after fulfilling and winning the order.",
  "Contribution ÷ Net revenue<br/>Contribution = Gross profit − fulfilment − courier on refused, failed and returned "
  "parcels − payment costs − marketing spend − marketplace commission", UP),
 ("EBITDA", "Operating profit after the fixed costs.",
  "Contribution − below-the-line costs<br/>Below the line = payroll + customer-service team + warehouse + technology "
  "+ research + website investment (5.1) + quality assurance (7.4) + stock holding and ageing", UP),
 ("Discount rate", "The average discount actually running.",
  "Σ (discount on each product × its revenue weight) ÷ Σ revenue weights<br/>falls back to the site-wide discount "
  "where no product discount is set; capped at 50%", DOWN),
 ("Fulfilment cost", "Picking, packing and the outbound courier.",
  "Orders × PKR 42 pick-and-pack + Orders × courier cost per order (by courier mix: Speed 210, Wide 175, Value 145)", DOWN),
 ("Payment costs", "Fees for collecting the money.",
  "Net revenue × prepaid share × 2.9% gateway fee + Net revenue × COD share × 1.2% COD fee", DOWN),
])

section(story, 4, "Operations", "Whether the business can deliver what it sells.", [
 ("Service level", "Share of the demand you could have served that you did serve.",
  "Orders ÷ Sellable demand<br/>Sellable demand = min( Demand potential, Traffic capacity ) — what you would have "
  "sold with unlimited stock", UP),
 ("In-stock rate", "Share of your range on the shelf at the start of the month.",
  "Σ revenue weight of active products with stock &gt; 0 ÷ Σ revenue weight of all active products", UP),
 ("Delivery success", "Share of parcels the couriers deliver.",
  "Σ (share of orders given to each courier × its success rate) × event effect<br/>Speed 97.5%, Wide 95.8%, Value 94.0%", UP),
 ("RTO rate", "Share of cash-on-delivery parcels refused at the door.",
  "18% × (1 + 0.5 × (1 − SLA attainment)) × (1 − 0.6 × min(1, prepaid discount ÷ 10%)) × event effect<br/>"
  "capped at 90%; SLA attainment falls when orders exceed warehouse capacity", DOWN),
 ("Return rate", "Share of last month's deliveries sent back.",
  "9% × (1 + 0.8 × (1 − actual quality)) × returns-policy factor × product-mix factor × event effect<br/>"
  "Policy factor: free returns 1.35 · customer pays 0.85 · restocking fee 0.70; capped at 60%", DOWN),
 ("Weeks of cover", "How long the stock on hand would last.",
  "Units in stock × 4.33 ÷ (Orders × 2.424 units per order)", "Balanced"),
], note="Weeks of cover is good up to a point: too little means stock-outs, too much ties up cash and ages in the warehouse.")

section(story, 5, "Customer", "Whether customers come back and like what they get.", [
 ("Active customers", "Customers still buying from you.",
  "Σ over every monthly cohort of the customers who have not yet churned", UP),
 ("Repeat order share", "Share of orders from people who had bought before.",
  "Repeat orders ÷ Orders", UP),
 ("LTV : CAC", "Lifetime value of a customer against what it cost to win one.",
  "LTV ÷ Blended CAC<br/>LTV = Σ cohorts [ cohort's share of active customers × (1 + Σ over 24 months of survival × "
  "purchase frequency × 1.194) ] × AOV × contribution margin before marketing", UP),
 ("Rating", "Average review score, 1 to 5.",
  "Rating<sub>t</sub> = Rating<sub>t−1</sub> + 0.30 × (Target − Rating<sub>t−1</sub>)<br/>Target = 2.289 + 1.2 × "
  "actual quality + 0.6 × delivery reliability + 0.4 × service SLA + 0.2 × packaging score − penalties", UP),
 ("NPS", "Net Promoter Score: would customers recommend you.",
  "100 × (0.42 × (Rating − 3) + 0.30 × service SLA + 0.28 × delivery reliability) − 20", UP),
 ("Service backlog", "Customer contacts still waiting for an answer.",
  "max(0, Tickets − Capacity)<br/>Tickets = Orders × 0.72 + last month's backlog + Returns × 0.6<br/>"
  "Capacity = Service agents × 900 a month", DOWN),
], note="Rating changes slowly — it closes 30% of the gap to its target each month — and it sets next month's conversion, not this month's. "
        "Packaging score: basic 0.25, branded 0.55, premium 0.85.")

section(story, 6, "Finance", "Whether the business can pay its bills.", [
 ("Cash", "Money in the bank at the end of the month.",
  "Last month's cash + cash received − cash paid out<br/>Received: prepaid sales (settle in 3 days), COD remitted by "
  "couriers (after 16 days), marketplace payouts. Paid: suppliers (on their terms), every P&amp;L cost, interest, "
  "investments. If cash falls below zero, credit is drawn automatically", UP),
 ("Runway (months)", "How many months the cash lasts at this month's burn.",
  "Cash ÷ |operating cash flow| when cash flow is negative<br/>shown as 99 when the business is not burning cash", UP),
 ("COD in transit", "Cash collected by couriers but not yet paid to you.",
  "Σ COD receivables not yet remitted (about 16 days of COD sales)", "Context"),
 ("Credit drawn", "How much of the working-capital facility is in use.",
  "Running total of automatic draws, up to PKR 24,000,000", DOWN),
 ("Net profit", "Profit after financing costs.",
  "EBITDA − Interest", UP),
 ("Interest paid", "Cost of the credit you have drawn.",
  "Credit drawn × 22% ÷ 12", DOWN),
], note="COD in transit is real money you will receive, but you cannot spend it yet: a fast-growing COD business can be profitable and short of cash at the same time.")

story.append(PageBreak())
story.append(Paragraph("7 &middot; THE P&amp;L BLOCK", st["eyebrow"]))
story.append(Paragraph("The profit and loss lines behind the margins", st["h1"]))
story.append(Paragraph("The margins above are these lines divided by net revenue. Read top to bottom; each line subtracts from the one above.", st["lead"]))
pl = [
 ("Gross revenue", "Orders × AOV − prepaid discount"),
 ("− Refused, returned, failed", "(RTO orders + returned orders + failed deliveries) × AOV"),
 ("= Net revenue", ""),
 ("− Cost of goods", "Cost of the units that stayed sold + write-off of returns that cannot be resold"),
 ("= Gross profit", "Gross margin % = Gross profit ÷ Net revenue"),
 ("− Fulfilment", "Pick-and-pack PKR 42 per order + outbound courier"),
 ("− RTO courier", "Refused and failed parcels pay the courier twice: out and back"),
 ("− Return courier and write-off", "Return shipping + unsellable returned stock"),
 ("− Payment costs", "2.9% of prepaid revenue + 1.2% of COD revenue"),
 ("= Contribution before marketing", "The economics of fulfilling an order, before winning it"),
 ("− Marketing", "Paid channels, creative, brand, CRM, affiliate commission"),
 ("− Marketplace commission", "14.5% of the marketplace share of revenue (35%) when selling on Daraz"),
 ("= Contribution", "Contribution margin % = Contribution ÷ Net revenue"),
 ("− Below the line", "Payroll, service team, warehouse, technology, research, website, QA, stock holding"),
 ("= EBITDA", ""),
 ("− Interest", "Credit drawn × 22% ÷ 12"),
 ("= Net profit", ""),
]
data = [[P("Line", "head"), P("How it is calculated", "head")]]
for a, b in pl:
    bold = a.startswith("=")
    data.append([P(a, "cellb" if bold else "cell"), P(b, "f")])
t = Table(data, colWidths=[62*mm, 116*mm])
ts = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, 0), 1.0, INK),
      ("LINEBELOW", (0, 1), (-1, -1), 0.4, LINE), ("TOPPADDING", (0, 0), (-1, -1), 4),
      ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5)]
for i, (a, _) in enumerate(pl, start=1):
    if a.startswith("="):
        ts.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
t.setStyle(TableStyle(ts))
story += [t, Spacer(1, 12)]

camp = [
 ("Spend", "Rupees given to this campaign.", "Your split of the channel budget (decision 3.10)", "—"),
 ("Impressions", "Times the ad was shown.", "Spend ÷ CPM × 1,000", UP),
 ("CPM", "Cost per thousand impressions.", "Channel's base CPM × channel inflation ÷ max(creative freshness, 0.3)", DOWN),
 ("Clicks", "Visits the campaign brought.", "Channel's paid sessions × (campaign spend × traffic quality) ÷ Σ same for all campaigns on the channel", UP),
 ("CTR", "Share of impressions that became a visit.", "Clicks ÷ Impressions", UP),
 ("CPC", "Cost of each visit.", "Spend ÷ Clicks", DOWN),
 ("Orders", "Orders from the campaign's visitors.", "Clicks × store conversion rate × campaign's targeting effect on conversion × share of demand realised", UP),
 ("CVR", "Share of the campaign's visits that ordered.", "Orders ÷ Clicks", UP),
 ("Revenue", "Sales from those orders.", "Orders × AOV", UP),
 ("ROAS", "Revenue per rupee of spend.", "Revenue ÷ Spend", UP),
 ("CAC", "Cost of each new customer the campaign won.", "Spend ÷ (Orders × share of this month's orders from new customers)", DOWN),
 ("A/B confidence", "How sure the test is that A and B really differ.",
  "Expected share for A = A's spend ÷ (A + B spend)<br/>z = (A's orders − total orders × expected share) ÷ √(total × share × (1 − share))<br/>"
  "Confidence = erf(|z| ÷ √2). A winner is called at 95% or more", UP),
]
section(story, 8, "Paid campaigns", "The campaign table opens in Session 7, one row per campaign. Targeting (decision 3.10) "
        "changes how much traffic and conversion each rupee buys; the table shows the result.", camp,
        note="Campaign ROAS here is not multiplied by 1.32: it is the simulation's own measurement. The blended "
             "Reported ROAS in the Marketing block is the platforms' over-stated version.")

def footer(c, d):
    c.saveState()
    c.setFont("D", 7.2); c.setFillColor(GREY)
    c.drawString(16*mm, 9*mm, "Monthly results · KPI definitions · numbers inside formulas are the simulation's assumptions, not market data")
    c.drawRightString(194*mm, 9*mm, f"{d.page}")
    c.setFillColor(RED); c.rect(16*mm, 287*mm, 12*mm, 1.2*mm, stroke=0, fill=1)
    c.restoreState()

doc = SimpleDocTemplate(sys.argv[1], pagesize=A4, leftMargin=16*mm, rightMargin=16*mm, topMargin=15*mm,
                        bottomMargin=16*mm, title="Monthly results: KPI definitions", author="Tariq Bashir")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
