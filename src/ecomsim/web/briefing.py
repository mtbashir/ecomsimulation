"""What a team is told, and when.

The rules of the game, the scoring criteria and the round-by-round framing
live here rather than in a template, because they are content a course
convenor will want to edit, and because they should be testable. Nothing in
this module computes anything.

The scoring anchors are the ones in docs/08-scoring.md. If those move, they
move here too - a published anchor a team cannot see is not an anchor.
"""
from __future__ import annotations

# --- How the game works ---------------------------------------------------------

RULES = [
    ("You are running a real business, month by month",
     "Each round is one trading month. You set the levers, the market responds, "
     "and you live with the consequences into the next month. Nothing resets."),
    ("You compete for the same customers",
     "Demand is a shared pool. Your share of it depends on how attractive you "
     "are relative to everyone else - price, delivery, rating, assortment, "
     "awareness. A good decision in isolation can still lose to a better one "
     "next door."),
    ("Decisions carry forward",
     "Submit nothing and last month's decisions stand. That is a decision too, "
     "and usually a poor one, because the market moves even when you do not."),
    ("Money is real and finite",
     "You start with fixed capital and a credit facility. Run out of cash and "
     "you go into administration - the run continues, but recovery is slow and "
     "expensive."),
    ("Some things take time",
     "Brand-building, technology projects, supplier changes and repositioning "
     "all land later than you decide them. Plan for the lag; you cannot buy "
     "your way out of it in the last month."),
    ("What you know is not free and not perfect",
     "Your own operating data is exact. Everything about the market and your "
     "rivals comes from research you pay for, with a stated margin of error "
     "and sometimes a month's delay."),
]

# --- The market you are trading in ------------------------------------------------

MARKET = [
    ("Cash on delivery is the norm",
     "Most Pakistani online shoppers pay cash at the door. It wins orders and "
     "it means you are paid weeks later, by a courier, on orders that may come "
     "back."),
    ("Return to origin is the killer",
     "A COD order refused at the door costs you the delivery both ways and "
     "returns stock you have already paid to ship. RTO, not returns, is what "
     "ruins the margin on a growing e-commerce business here."),
    ("The marketplace is a channel, not a partner",
     "Listing on the marketplace buys reach you cannot build yourself, and "
     "charges a commission on every order you win through it."),
    ("Couriers are not interchangeable",
     "Cost per order, success rate, speed and rural reach all differ. The "
     "cheapest courier is rarely the cheapest outcome."),
]

# --- How you are scored -----------------------------------------------------------
#
# Criterion-referenced: the anchors below are fixed and published. You are not
# marked against the cohort, so every team can score well, and a weak cohort
# does not make a weak run look good.

PILLARS = [
    ("Profitability", 25,
     "Contribution margin, EBITDA margin and gross margin, averaged across the "
     "run with later months weighted more heavily.",
     [("Contribution margin", "0% scores nothing, 9% scores half, 18% scores full"),
      ("EBITDA margin", "-10% scores nothing, break-even scores half, +10% scores full"),
      ("Gross margin", "25% scores nothing, 38% scores half, 50% scores full")]),
    ("Growth", 20,
     "How much bigger you finished than you started, and whether you took "
     "share while doing it.",
     [("Revenue multiple, final month against first",
       "0.8x scores nothing, 1.9x scores half, 3.5x scores full"),
      ("Market share change", "-2pp scores nothing, +0.5pp half, +4pp full"),
      ("Order growth per month", "-2% nothing, +3% half, +9% full")]),
    ("Customer value", 20,
     "Whether you built a customer base or rented one. This is where a "
     "discount-led strategy usually comes apart.",
     [("Lifetime value against acquisition cost",
       "1.0x nothing, 2.5x half, 5.0x full"),
      ("Repeat order share", "10% nothing, 22% half, 40% full"),
      ("Active customers at the end", "20,000 nothing, 45,000 half, 90,000 full"),
      ("NPS", "0 nothing, 24 half, 55 full")]),
    ("Operational efficiency", 15,
     "Whether the business actually worked: stock on hand, orders delivered, "
     "cash cycle.",
     [("In-stock rate", "80% nothing, 93% half, 99% full"),
      ("Delivery success rate", "75% nothing, 87% half, 95% full")]),
    ("Cash & capital", 10,
     "Closing cash, runway and how hard you leaned on the credit facility.",
     []),
    ("Decision quality", 10,
     "Judged by your instructor, not the model. Three of these ten points are "
     "your founding business plan, read against what you actually delivered.",
     []),
]

# --- Round framing -----------------------------------------------------------------
#
# A line of context per round, so opening the portal tells a team where they
# are in the arc rather than only which month it is.

ROUND_NOTES = {
    0: ("Set the business up",
        "Nothing trades this month. You are choosing what kind of business you "
        "are going to be, and every team has the same capital to do it with."),
    1: ("Your first trading month",
        "Get a clean read on the business you built. Change little, watch what "
        "the numbers say, and find out where your founding assumptions were "
        "wrong."),
    2: ("Read the first month honestly",
        "You now have one month of real data and one month of variance. Tell "
        "the difference between the two before you act on either."),
    3: ("Fix what the data showed",
        "Early problems are cheap to fix and expensive to ignore. The levers "
        "that take time to land should be pulled around now."),
    6: ("Half time",
        "Your founding plan named targets for this month. Compare them with "
        "what happened, and be specific about why they differ."),
    10: ("Build the finish, do not buy it",
         "Discounting into the last months lifts revenue and costs you on "
         "every pillar that matters. The lags are longer than the rounds you "
         "have left."),
    12: ("The final month",
         "Stock measures - cash, customers, brand, capability - are taken as "
         "they stand at the end of this month. Flow measures are already "
         "mostly written."),
}


def round_note(round_: int, total: int) -> tuple[str, str]:
    """A heading and a line of context for the round a team is looking at."""
    if round_ in ROUND_NOTES:
        return ROUND_NOTES[round_]
    if round_ >= total:
        return ROUND_NOTES[12]
    return ("Trading month %d of %d" % (round_, total),
            "Read last month's report before you change anything. The levers "
            "that pay back slowest are the ones you have least time left to "
            "pull.")
