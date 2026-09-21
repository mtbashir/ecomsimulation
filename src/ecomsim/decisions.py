"""Decision registry and resolution.

The rule that makes presets work (docs/04-configurability.md):

    The engine never reads a decision directly. It reads a resolved value -
    the team's input if the decision is enabled and unlocked, otherwise the
    configured default.

Disabling a decision removes student agency over it. It never removes it from
the model, which is why Foundation running on a full-depth engine is a better
product than Foundation on a Foundation engine.
"""
from __future__ import annotations

from dataclasses import dataclass

PRESETS = {
    "foundation": 24,
    "standard": 38,
    "advanced": 56,
    "expert": 92,
}


@dataclass(frozen=True)
class DecisionSpec:
    """One lever, described well enough that a student needs no glossary.

    ``name``, ``help`` and ``options`` are the entire user interface. A team
    reading the form should understand what the lever does and what moves when
    they pull it, without cross-referencing the handbook or memorising a code.
    """
    code: str
    group: str
    name: str
    kind: str          # select | multi | shares | num | pct | curr | per_sku | text
    default_when_disabled: object
    presets: frozenset[str]  # presets in which this decision is enabled
    unlock_round: int = 1
    min_granularity: int = 1  # max ROUND_MONTHS at which it stays an action
    help: str = ""            # what it does and what it trades off, in one line
    unit: str = ""            # shown next to the input: PKR, %, units, weeks
    guide: str = ""           # a typical range, so a blank field is not a guess
    options: tuple = ()       # ((value, label, note), ...) for a select
    catalogue: str = ""       # skus | studies | couriers | suppliers - option source


# Every preset. Most levers are on from Foundation upward; the ones that are
# not name their presets explicitly.
ALL = frozenset({"foundation", "standard", "advanced", "expert"})


# Abbreviated registry. Full 56 in docs/01-decision-list.md; the remaining rows
# follow this shape exactly and are added as each module is implemented.
#
# Every row carries its own help text. The form is generated from this table,
# so a lever that reads badly on screen is fixed here, once, and not in a
# template.
REGISTRY: dict[str, DecisionSpec] = {
    d.code: d for d in [

        # --- Assortment & product -------------------------------------------
        DecisionSpec(
            "1.1", "G1", "Range, prices and sourcing", "grid", None, ALL,
            help="What you charge for each product, and where each one is "
                 "sourced from. Cost follows the sourcing choice, so the margin "
                 "on every line moves with it. Which products you sell was "
                 "settled at founding - changing the range mid-run is not "
                 "modelled, so this is price and sourcing only.",
            catalogue="skus"),
        DecisionSpec(
            "1.5", "G1", "Product quality positioning", "select", None, ALL,
            help="Where your catalogue sits on quality. A higher tier lifts "
                 "how customers rate you and converts better, but costs more "
                 "to source. Leave on automatic and your actual product mix "
                 "decides it for you.",
            options=(
                ("", "Automatic - follow my product mix",
                 "Quality comes from what you actually sell"),
                ("economy", "Economy", "Cheapest to source, weakest perception"),
                ("standard", "Standard", "The middle of the market"),
                ("premium", "Premium", "Best perceived quality, highest cost"),
            )),
        DecisionSpec(
            "1.2", "G1", "Bundles", "bundles", [],
            frozenset({"standard", "advanced", "expert"}),
            help="Three-packs of your own products, priced as a pack. Offering "
                 "bundles lifts average order value; the gain flattens once you "
                 "are bundling three or more lines. Price the pack below three "
                 "singles and you are trading margin for basket size.",
            catalogue="skus"),

        # --- Pricing ---------------------------------------------------------
        DecisionSpec(
            "2.2", "G2", "Site-wide discount", "pct", 0.0, ALL,
            unit="%",
            help="Average discount off list price across the whole site. "
                 "Every point you give away buys volume and costs margin.",
            guide="Typical 0-25%. Above 30% and you are buying revenue you "
                  "cannot afford."),
        DecisionSpec(
            "2.4", "G2", "Free-delivery order threshold", "curr", 2500, ALL,
            unit="PKR",
            help="Cart value above which the customer pays no delivery fee. "
                 "A low threshold wins orders and raises your shipping bill; "
                 "a high one pushes baskets up but loses small orders.",
            guide="Typical PKR 1,500-3,500. Enter 0 for free delivery on "
                  "everything."),

        # --- Marketing -------------------------------------------------------
        DecisionSpec(
            "3.1", "G3", "Meta ads (Facebook & Instagram)", "curr", 468_000, ALL,
            unit="PKR this month",
            help="Your volume channel: mid intent, mid cost, the largest "
                 "audience. Most of your new customers come from here.",
            guide="Typical PKR 300,000-700,000"),
        DecisionSpec(
            "3.2", "G3", "Google Search ads", "curr", 234_000, ALL,
            unit="PKR this month",
            help="The highest-intent traffic you can buy - people already "
                 "looking for what you sell - but the audience runs out, so "
                 "returns fall away fast above a point.",
            guide="Typical PKR 150,000-350,000"),
        DecisionSpec(
            "3.4", "G3", "TikTok ads", "curr", 168_000, ALL,
            unit="PKR this month",
            help="Cheap reach on a younger audience. Volume is there but "
                 "intent is low, so it leans hard on good creative.",
            guide="Typical PKR 80,000-300,000"),
        DecisionSpec(
            "3.8", "G3", "Creative production budget", "curr", 200_000,
            frozenset({"standard", "advanced", "expert"}), unlock_round=2,
            unit="PKR this month",
            help="Shoots, video and copywriting. Does not buy traffic itself - "
                 "it raises the return on every rupee of paid media you do "
                 "spend, and decays if you stop.",
            guide="Typical PKR 100,000-350,000"),
        DecisionSpec(
            "3.9", "G3", "Brand-building spend", "curr", 267_000,
            frozenset({"standard", "advanced", "expert"}), unlock_round=2,
            unit="PKR this month",
            help="Awareness advertising with no direct-response tracking. Slow "
                 "to pay back, but it builds the awareness that makes every "
                 "later performance rupee cheaper.",
            guide="Typical PKR 150,000-400,000"),
        DecisionSpec(
            "3.6", "G3", "Affiliate & influencer commission", "pct", 0.0,
            frozenset({"standard", "advanced", "expert"}), unlock_round=2,
            unit="% of revenue they refer",
            help="What you pay partners on sales they bring you. Costs nothing "
                 "when nothing sells, but a high rate eats the margin on every "
                 "referred order.",
            guide="Typical 5-12%"),

        # --- Channel ---------------------------------------------------------
        DecisionSpec(
            "4.1", "G4", "Sell on the marketplace (Daraz)", "select", "off",
            frozenset({"standard", "advanced", "expert"}), unlock_round=3,
            help="Listing on the marketplace puts you in front of shoppers who "
                 "would never find your site - but the marketplace takes a "
                 "commission on those orders and owns the customer.",
            options=(("off", "No - own site only", ""),
                     ("on", "Yes - list on the marketplace",
                      "Commission charged on marketplace orders"))),

        # --- Site & experience -----------------------------------------------
        DecisionSpec(
            "5.1", "G5", "Website experience investment", "curr", 0,
            frozenset({"standard", "advanced", "expert"}), unlock_round=2,
            unit="PKR this month",
            help="Site speed, search, product pages and checkout. Raises "
                 "conversion on the traffic you already pay for, but the "
                 "improvement lands a month after you spend.",
            guide="Typical PKR 0-400,000"),

        # --- CRM & retention ---------------------------------------------------
        DecisionSpec(
            "6.1", "G6", "CRM & retention budget", "curr", 60_000, ALL,
            unit="PKR this month",
            help="SMS, WhatsApp, email and loyalty aimed at customers you "
                 "already have. Cuts churn and lifts repeat rate - the "
                 "cheapest growth available to you.",
            guide="Typical PKR 50,000-250,000"),

        # --- Supply & procurement ----------------------------------------------
        DecisionSpec(
            "7.2", "G7", "Supplier", "select", "B", ALL,
            help="Who makes your stock. The trade-off is cost against lead "
                 "time and minimum order size - cheap stock ties up cash and "
                 "arrives late.",
            catalogue="suppliers"),
        DecisionSpec(
            "7.1", "G7", "Stock to purchase this month", "num", None,
            frozenset({"standard", "advanced", "expert"}),
            unit="units",
            help="How many units to buy in. Too little and you stock out in a "
                 "good month; too much and your cash sits in a warehouse. "
                 "Leave blank and the system orders to your cover target.",
            guide="Leave blank to order automatically"),
        DecisionSpec(
            "7.5", "G7", "Safety stock cover", "num", 3, ALL,
            unit="weeks of demand",
            help="The buffer you hold on top of forecast demand. More cover "
                 "means fewer stock-outs and more cash tied up in inventory.",
            guide="Typical 2-6 weeks"),
        DecisionSpec(
            "7.4", "G7", "Quality assurance spend", "curr", 80_000, ALL,
            unit="PKR this month",
            help="Inspection and testing before stock ships. Cuts defects, "
                 "returns and the bad reviews that follow them.",
            guide="Typical PKR 50,000-250,000"),

        # --- Fulfilment ---------------------------------------------------------
        DecisionSpec(
            "8.2", "G8", "Orders shipped through 3PL", "pct", 0.4, ALL,
            unit="% of orders",
            help="Share handled by an outsourced warehouse instead of your "
                 "own. Adds capacity with no capex, at a higher cost per order.",
            guide="Typical 20-60%"),
        DecisionSpec(
            "8.3", "G8", "Courier mix", "shares", None, ALL,
            unit="% of deliveries",
            help="How you split deliveries between couriers. Faster and more "
                 "reliable costs more per order; cheap couriers fail more "
                 "deliveries, and a failed delivery is a returned order. "
                 "Shares must add up to 100%.",
            catalogue="couriers"),
        DecisionSpec(
            "8.5", "G8", "Packaging", "select", "basic", ALL,
            help="What the order looks like when it arrives. Better packaging "
                 "lifts repeat purchase and cuts damage, at a higher cost on "
                 "every single order you ship.",
            options=(("basic", "Basic", "Plain box, lowest cost per order"),
                     ("branded", "Branded", "Printed box, moderate cost"),
                     ("premium", "Premium unboxing",
                      "Best repeat-purchase effect, highest cost"))),

        # --- Payments -------------------------------------------------------------
        DecisionSpec(
            "9.1", "G9", "Cash on delivery", "select", "on", ALL,
            help="COD is what most Pakistani shoppers expect. Switching it off "
                 "collapses return-to-origin and your working capital cycle - "
                 "and costs you a large share of your orders.",
            options=(("on", "Yes - accept cash on delivery",
                      "Most orders will be COD"),
                     ("off", "No - prepaid only",
                      "Far less RTO, far fewer orders"))),
        DecisionSpec(
            "9.2", "G9", "Discount for paying online", "pct", 0.03,
            frozenset({"standard", "advanced", "expert"}),
            unit="%",
            help="A discount offered to customers who pay online instead of "
                 "cash on delivery. Shifts the payment mix, gets you paid "
                 "sooner and cuts return-to-origin - you buy all of that with "
                 "margin.",
            guide="Typical 2-8%"),
        DecisionSpec(
            "9.3", "G9", "Payment gateway", "select", "A", ALL,
            help="Who processes your online payments. A failed payment is a "
                 "lost order, so the success rate matters more than the fee.",
            options=(("A", "Gateway A - balanced", "91% of payments succeed"),
                     ("B", "Gateway B - cheapest", "84% of payments succeed"),
                     ("C", "Gateway C - most reliable",
                      "96% of payments succeed, highest fee"))),

        # --- Customer service ---------------------------------------------------
        DecisionSpec(
            "10.1", "G10", "Customer service team size", "num", 4,
            frozenset({"standard", "advanced", "expert"}), unlock_round=2,
            unit="people",
            help="Agents handling calls, chat and complaints. Too few and "
                 "response times slide, which shows up in churn and reviews "
                 "a month later.",
            guide="Typical 3-12 people"),
        DecisionSpec(
            "10.4", "G10", "Returns policy", "select", "customer_pays",
            frozenset({"standard", "advanced", "expert"}), unlock_round=2,
            help="Who pays when a customer sends something back. A generous "
                 "policy converts better and invites more returns.",
            options=(
                ("free", "Free returns", "Best for conversion, most returns"),
                ("customer_pays", "Customer pays return shipping",
                 "The market norm"),
                ("restocking", "Restocking fee charged",
                 "Fewest returns, weakest conversion"))),

        # --- Technology & AI ------------------------------------------------------
        DecisionSpec(
            "11.1", "G11", "Product recommendation engine", "select", False,
            frozenset({"advanced", "expert"}), unlock_round=3,
            help="Personalised 'customers also bought'. Lifts average order "
                 "value once it is live, after a build period."),
        DecisionSpec(
            "11.2", "G11", "AI demand forecasting", "select", False,
            frozenset({"advanced", "expert"}), unlock_round=3,
            help="Sharper forecasts mean fewer stock-outs and less dead stock "
                 "for the same cover."),
        DecisionSpec(
            "11.3", "G11", "Dynamic pricing", "select", False,
            frozenset({"advanced", "expert"}), unlock_round=3,
            help="Prices that move with demand and competitor moves. Protects "
                 "margin, and customers notice when it is heavy-handed."),
        DecisionSpec(
            "11.4", "G11", "AI customer service", "select", False,
            frozenset({"advanced", "expert"}), unlock_round=3,
            help="Automated first-line support. Handles routine contacts at a "
                 "fraction of the cost of an agent."),
        DecisionSpec(
            "11.5", "G11", "AI creative generation", "select", False,
            frozenset({"advanced", "expert"}), unlock_round=3,
            help="Machine-generated ad creative. Cheaper and faster to test "
                 "than a production shoot, and weaker at its best."),

        # --- Finance & research ---------------------------------------------------
        DecisionSpec(
            "12.1", "G12", "Market research to buy", "multi", [], ALL,
            help="Research is not free and not perfect. Each study costs "
                 "money, carries a margin of error, and some arrive a month "
                 "late. Buy what will change a decision you are about to make.",
            catalogue="studies"),
        DecisionSpec(
            "12.5", "G12", "Board memo", "text", "", ALL,
            help="A short note on what you are trying to achieve this month "
                 "and why. Your instructor reads it; the model ignores it.",
            guide="Optional"),
    ]
}


class Resolver:
    """Turns submitted decisions into the resolved values modules read."""

    def __init__(self, preset: str = "advanced", round_: int = 1,
                 overrides: dict[str, dict] | None = None):
        self.preset = preset
        self.round = round_
        self.overrides = overrides or {}

    def enabled(self, code: str) -> bool:
        spec = REGISTRY[code]
        cfg = self.overrides.get(code, {})
        if "enabled" in cfg:
            return bool(cfg["enabled"])
        return self.preset in spec.presets

    def unlocked(self, code: str) -> bool:
        spec = REGISTRY[code]
        unlock = self.overrides.get(code, {}).get("unlock_round", spec.unlock_round)
        lock = self.overrides.get(code, {}).get("lock_round")
        if lock is not None and self.round > lock:
            return False
        return self.round >= unlock

    def resolve(self, submitted: dict[str, object]) -> dict[str, object]:
        out: dict[str, object] = {}
        for code, spec in REGISTRY.items():
            if self.enabled(code) and self.unlocked(code) and code in submitted:
                out[code] = submitted[code]
            else:
                out[code] = self.overrides.get(code, {}).get(
                    "default_when_disabled", spec.default_when_disabled
                )
        return out
