"""Flask app: team portal and instructor console.

Deliberately small and boring. Server-rendered HTML, no JavaScript build, one
SQLite file to back up. Nobody is on call during a class, so every destructive
action is reversible and the file-based escape hatch stays one click away.
"""
from __future__ import annotations

import os
import secrets
from functools import wraps
from pathlib import Path

from flask import (
    Flask, Response, abort, flash, g, redirect, render_template,
    request, session, url_for,
)

from .. import founding
from .. import charts
from .. import targeting
from ..decisions import REGISTRY
from ..params import BandViolation
from . import briefing, db, service

# Round 0, in the order a founder actually decides things: who you are, who
# you sell to, what you sell, where it comes from, what you build it on, then
# what it costs and what you are promising. The engine does not care about the
# order; a student does.
FOUNDING_STAGES = [
    ("identity", "1. Who you are",
     "Start with the thing everything else has to be consistent with. A brand "
     "that says one thing and prices another converts badly."),
    ("market", "2. Who you sell to",
     "Two categories out of five, and where you sit on quality. These set your "
     "margin profile, your return rate and how expensive your customers are "
     "to acquire. Positioning is the hardest of all of them to change later."),
    ("offer", "3. What you sell, where it comes from, and what you charge",
     "Your opening range and the channel you sell it through. A wide range "
     "spreads your stock thin; a narrow one leaves demand on the table."),
    ("supply", "",
     "Sourcing is a decision per product, not one decision for the business. "
     "Local costs about 6% more and lands in nine days. Imported is about 9% "
     "cheaper, takes twenty-two days, ties up more cash in the pipeline, and "
     "is the line that hurts when the rupee moves. Dual-sourcing a product "
     "splits the difference on all four. Which products you put on which side "
     "is the judgement."),
    ("build", "4. What you build it on",
     "Your storefront, your warehouse and your payments. The capex is paid now "
     "and is not refundable, so what you choose here constrains what you can "
     "spend on customers for months."),
    ("money", "5. Where the money and the people go",
     "Twelve million rupees, split four ways, and a payroll to allocate. The "
     "floors and ceilings exist because an all-in bet on stock puts most teams "
     "out of cash by month three."),
    ("plan", "6. What you are promising",
     "Buy the founding research at half price if you want evidence first. Then "
     "write down the targets you expect to hit - you will be asked to explain "
     "the variance against them at the end."),
]

TIER_CHOICES = [
    ("value", "Value", "Lower price, thinner margin, cheaper customers, "
                       "higher volume"),
    ("mainstream", "Mainstream", "The middle of the market on every dimension"),
    ("premium", "Premium", "Higher price and margin, better ratings, dearer "
                           "customers, slower growth"),
]
MODEL_CHOICES = [
    ("d2c", "Own site only (D2C)",
     "All traffic is yours to earn and yours to keep. No commission, no "
     "shortcut to reach."),
    ("hybrid", "Hybrid",
     "Own site plus the marketplace. Reach now, commission on about a third "
     "of your orders."),
    ("marketplace_first", "Marketplace first",
     "Volume from day one, the thinnest margin, and a customer who belongs to "
     "the marketplace."),
]
SOURCING_CHOICES = [
    ("local", "Local", "Costs about 6% more, arrives in 9 days, no currency risk"),
    ("mixed", "Mixed", "Baseline cost, 14 days, some currency exposure"),
    ("import", "Import", "About 9% cheaper, 22 days, fully exposed to the rupee"),
]
STACK_CHOICES = [
    ("basic", "Basic platform",
     "PKR 400,000 up front. Live immediately. Your site experience cannot get "
     "better than mediocre."),
    ("standard", "Standard platform",
     "PKR 1,200,000 up front. Live immediately. Room to improve the experience "
     "for two years."),
    ("custom", "Custom build",
     "PKR 2,800,000 up front and two months before it is live. The highest "
     "ceiling, paid for with your first two trading months."),
]
FULFILMENT_CHOICES = [
    ("3pl", "Third-party logistics",
     "No capex. Someone else's warehouse, at a price per order."),
    ("own", "Own warehouse",
     "PKR 2,400,000 up front, lower cost per order, and capacity you control."),
]
GATEWAY_CHOICES = [
    ("A", "Gateway A - balanced", "91% of online payments succeed"),
    ("B", "Gateway B - cheapest", "84% of online payments succeed"),
    ("C", "Gateway C - most reliable", "96% succeed, at the highest fee"),
]

SEGMENT_DRIVERS = {
    "w_price": "price", "w_quality": "quality", "w_delivery": "fast delivery",
    "w_availability": "things being in stock", "w_brand": "the brand",
    "w_fit": "range",
}


def _segment_driver(seg) -> str:
    """The one thing this segment weights most, in plain words."""
    key = max(SEGMENT_DRIVERS, key=lambda k: float(seg.get(k, 0)))
    return SEGMENT_DRIVERS[key]


def _segment_loyalty(seg) -> str:
    """Whether they come back, said without a number nobody can calibrate."""
    p = float(seg["repeat_propensity"])
    if p >= 1.3:
        return "comes back far more often than average"
    if p >= 1.0:
        return "comes back about as often as average"
    if p >= 0.6:
        return "comes back less often than average"
    return "rarely comes back"


GROUP_NAMES = {
    "G1": "Assortment & product", "G2": "Pricing", "G3": "Marketing",
    "G4": "Channel", "G5": "Site & experience", "G6": "CRM & retention",
    "G7": "Supply & procurement", "G8": "Fulfilment", "G9": "Payments",
    "G10": "Customer service", "G11": "Technology & AI", "G12": "Finance & research",
}


def create_app(database: str | Path | None = None) -> Flask:
    app = Flask(__name__)
    path = Path(database or os.environ.get("ECOMSIM_DB", "game.db"))
    path.parent.mkdir(parents=True, exist_ok=True)
    app.config["DATABASE"] = str(path)

    # A stable secret keeps sessions alive across restarts. Without one set,
    # every restart silently signs everyone out mid-class, so fall back to a
    # key persisted beside the database rather than a fresh one each boot.
    app.secret_key = os.environ.get("ECOMSIM_SECRET") or _persistent_secret(path)

    if os.environ.get("ECOMSIM_BEHIND_PROXY"):
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
        app.config.update(SESSION_COOKIE_SECURE=True, SESSION_COOKIE_HTTPONLY=True,
                          SESSION_COOKIE_SAMESITE="Lax")

    _autoinit(path)

    @app.before_request
    def _open_db():
        g.db = db.connect(app.config["DATABASE"])

    @app.teardown_request
    def _close_db(exc):
        con = g.pop("db", None)
        if con is not None:
            con.close()

    @app.context_processor
    def _inject():
        return {"game": db.game(g.db), "user": session.get("user"),
                "role": session.get("role"), "group_names": GROUP_NAMES}

    register_routes(app)
    return app


def _persistent_secret(db_path: Path) -> str:
    key_file = db_path.parent / ".secret_key"
    if key_file.exists():
        return key_file.read_text().strip()
    key = secrets.token_hex(32)
    key_file.write_text(key)
    try:
        key_file.chmod(0o600)
    except OSError:
        pass          # Windows and some mounts do not support it; not fatal
    return key


def _autoinit(path: Path) -> None:
    """Create the game on first boot of a hosted deploy.

    There is no shell on a managed host, so the first boot reads its setup from
    the environment and stores the generated team passwords for one-time
    collection in the Teams page.
    """
    if path.exists():
        con = db.connect(path)
        with con:
            db.migrate(con)
        con.close()
        return
    teams = int(os.environ.get("ECOMSIM_TEAMS", 8))
    db.init(
        path,
        name=os.environ.get("ECOMSIM_NAME", "E-Commerce Simulation"),
        teams=teams,
        preset=os.environ.get("ECOMSIM_PRESET", "advanced"),
        rounds=int(os.environ.get("ECOMSIM_ROUNDS", 12)),
        start_mode=os.environ.get("ECOMSIM_START_MODE", "founding"),
        admin_password=os.environ.get("ECOMSIM_ADMIN_PASSWORD")
        or secrets.token_urlsafe(12),
    )


# --- Auth ---------------------------------------------------------------------

def role_home(role: str | None) -> str:
    """Where a signed-in user of this role belongs."""
    return url_for("admin") if role == "admin" else url_for("home")


def login_required(role: str | None = None):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            if "user" not in session:
                return redirect(url_for("login", next=request.path))
            if role and session.get("role") != role:
                abort(403)
            return fn(*a, **kw)
        wrapper._required_role = role
        return wrapper
    return deco


def _endpoint_role(app: Flask, path: str) -> str | None:
    """The role a path demands, or None if it is open to any signed-in user."""
    try:
        endpoint, _ = app.url_map.bind("localhost").match(path, method="GET")
    except Exception:
        return "__unroutable__"
    return getattr(app.view_functions.get(endpoint), "_required_role", None)


def safe_next(app: Flask, target: str | None, role: str | None) -> str | None:
    """Validate a ``next`` parameter: same-site, routable, and open to *role*.

    Anything else is dropped so the caller falls back to the role's home page.
    Without the role check an admin who lands on ``/`` first is bounced to
    ``/login?next=/`` and then straight back to a team-only page.
    """
    if not target:
        return None
    # Same-site only: one leading slash, no scheme, no protocol-relative "//",
    # no backslash (some browsers normalise it to "/").
    if not target.startswith("/") or target.startswith("//") or "\\" in target:
        return None
    path = target.split("?", 1)[0].split("#", 1)[0]
    required = _endpoint_role(app, path)
    if required == "__unroutable__":
        return None
    if required is not None and required != role:
        return None
    return target


def register_routes(app: Flask) -> None:

    @app.context_processor
    def nav_state():
        """What the shell needs, on every page, without each route saying so."""
        theme = session.get("theme") or "consulytics"
        if "user" not in session:
            return {"nav_at": request.endpoint, "open_count": 0, "theme": theme}
        if session.get("role") != "team":
            return {"nav_at": request.endpoint, "open_count": 0, "theme": theme,
                    "themes": db.THEMES}
        game = db.game(g.db)
        count = len(service.open_decisions(g.db, game["open_round"])) \
            if game["open_round"] else 0
        record = db.founding(g.db, session["team_id"])
        brand = (record or {}).get("config", {}).get("brand_name")
        return {"nav_at": request.endpoint, "open_count": count, "theme": theme,
                "themes": db.THEMES,
                "brand": brand if brand and brand != "Unnamed" else None}


    @app.route("/login", methods=["GET", "POST"])
    def login():
        if "user" in session and request.method == "GET":
            return redirect(safe_next(app, request.args.get("next"),
                                      session.get("role"))
                            or role_home(session.get("role")))
        if request.method == "POST":
            row = db.authenticate(g.db, request.form.get("username", ""),
                                  request.form.get("password", ""))
            if row is None:
                flash("Wrong username or password.", "error")
            else:
                session.update(user=row["username"], role=row["role"],
                               team_id=row["team_id"], name=row["display_name"],
                               theme=row["theme"] or "consulytics")
                with g.db:
                    db.log(g.db, row["username"], "auth.login", "")
                dest = safe_next(app, request.args.get("next"), row["role"])
                return redirect(dest or role_home(row["role"]))
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    # --- Team portal ----------------------------------------------------------

    @app.route("/")
    @login_required()
    def home():
        # The front door. An instructor who types the bare URL lands here, so
        # send them on to their own console rather than refusing the page.
        if session.get("role") != "team":
            return redirect(url_for("admin"))

        # Nobody should meet a decision form before they have been told what
        # the game is. First sign-in goes to the brief, once.
        me = db.account(g.db, session["user"])
        if me is not None and me["briefing_seen_at"] is None:
            return redirect(url_for("brief"))

        game = db.game(g.db)
        tid = session["team_id"]
        open_round = game["open_round"]
        founding = db.founding(g.db, tid)
        setting_up = (game["start_mode"] == "founding" and game["round"] == 0)
        heading, note = briefing.round_note(
            0 if setting_up else (open_round or game["round"] or 1),
            game["total_rounds"])

        submitted = (db.submission(g.db, open_round, tid) is not None
                     if open_round else False)
        return render_template(
            "team_home.html",
            open_round=open_round,
            setting_up=setting_up,
            founding_done=bool(founding and founding["submitted_at"]),
            founding_started=founding is not None,
            heading=heading, note=note,
            submitted=submitted,
            rounds=list(range(1, game["round"] + 1)),
            position=service.company_position(g.db, tid),
            research=_research_bought(g.db, tid, game["round"]),
            kpis=service.headline_kpis(g.db, tid),
            meters=service.plan_meters(g.db, tid),
            agenda=service.agenda(g.db, tid),
            standings=service.standings(g.db, tid),
            spark=charts.sparkline,
            steps=_steps(g.db, tid, game, submitted),
        )

    def _steps(con, team_id, game, submitted):
        """Read results, review research, set decisions, submit. Where you are
        in that is read off what you have actually done."""
        read = bool(game["round"])
        research = bool((db.submission(con, game["round"], team_id) or {}).get("12.1"))
        entered = submitted
        done = [read, research or read, entered, entered]
        labels = ["Read results", "Review research", "Set decisions", "Submit"]
        links = [url_for("results", round_=game["round"]) if game["round"] else None,
                 url_for("research"), url_for("submit"), url_for("submit")]
        out, hit_current = [], False
        for i, (label, ok, href) in enumerate(zip(labels, done, links), 1):
            state = "done" if ok else ("now" if not hit_current else "")
            if state == "now":
                hit_current = True
            out.append({"n": i, "label": label, "state": state, "href": href})
        return out

    def _differs(typed: str, standing: float) -> bool:
        """Did the team actually change this price, or just leave it sitting?"""
        try:
            return abs(float(typed.replace(",", "")) - float(standing)) > 0.5
        except ValueError:
            return True

    def _research_bought(con, team_id, upto_round):
        """The distinct studies this team holds, most recent reading first.

        Distinct, not one row per purchase: a team that re-buys MR-09 every
        month holds one study, not six, and the dashboard card counts what it
        can read rather than what it has spent.
        """
        params = service.load_params(con)
        by_code = {s["code"]: s for s in params.studies}
        out, seen = [], set()
        for rnd in range(upto_round, 0, -1):
            for code in (db.submission(con, rnd, team_id) or {}).get("12.1", []):
                row = by_code.get(code)
                if row and code not in seen:
                    seen.add(code)
                    out.append({"round": rnd, "name": row["name"],
                                "price": float(row["price"]), "code": code})
        return out

    @app.get("/research")
    @login_required("team")
    def research():
        """What the studies you paid for actually say.

        Research buys no advantage. It cannot raise a number or win a customer;
        the only thing it does is tell you whether the decision you are about to
        take is the right one. Everything that moves is still the team's call.
        """
        return render_template(
            "research.html",
            desk=service.research_desk(g.db, session["team_id"]),
            game=db.game(g.db))


    @app.get("/handbook")
    @login_required()
    def handbook():
        """Every decision: what it does, the trade-off, where it shows up in
        the report, and the mistake teams usually make."""
        return render_template("handbook.html", hb=service.handbook_page(g.db))

    @app.get("/guide/marketing")
    @login_required()
    def guide_marketing():
        """How to read the campaign numbers, aim a budget, and run a test that
        can actually tell you something. Open to instructors too."""
        return render_template(
            "guide_marketing.html",
            g_=service.marketing_guide(g.db, session.get("team_id")))

    @app.get("/campaigns")
    @login_required("team")
    def campaigns():
        """How the Meta, TikTok and Google budgets are spent, beside what last
        month's campaigns actually did. The budgets themselves stay on the
        decision form: this page never changes how much is spent."""
        return render_template(
            "campaigns.html", desk=service.campaign_desk(g.db, session["team_id"]))

    @app.post("/campaigns")
    @login_required("team")
    def campaigns_save():
        desk = service.campaign_desk(g.db, session["team_id"])
        if not desk["can_edit"]:
            flash("Campaign setup is not open this month.", "error")
            return redirect(url_for("campaigns"))
        rnd, tid = desk["open_round"], session["team_id"]
        current = dict(db.submission(g.db, rnd, tid) or {})
        if request.form.get("action") == "broad":
            # An empty list, not a missing key: broad is a setting that carries
            # forward, where a missing key would inherit last month's campaigns.
            value, errors = [], []
        else:
            value, errors, typed = service.campaign_form(
                request.form, [r["code"] for r in desk["shelf"]])
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("campaigns.html", desk=service.campaign_desk(
                g.db, tid, draft=typed)), 400
        current[targeting.DECISION] = value
        db.submit(g.db, rnd, tid, current, session["user"])
        with g.db:
            db.log(g.db, session["user"], "campaigns",
                   f"r{rnd}: {service.campaign_summary(value)}")
        flash(f"Campaigns saved for month {rnd}: "
              f"{service.campaign_summary(value)}. They run until you change them.",
              "ok")
        return redirect(url_for("campaigns"))

    @app.post("/research/commission")
    @login_required("team")
    def commission():
        """Order this month's studies, from the page that shows what they say.

        The order replaces the month's list rather than adding to it, so
        un-ticking a study is how you cancel it. Nothing is charged until the
        instructor runs the month, which is why a team may change its mind as
        often as it likes while the round is open.
        """
        game = db.game(g.db)
        rnd = game["open_round"]
        if not rnd:
            flash("Submissions are closed, so nothing can be commissioned.",
                  "error")
            return redirect(url_for("research"))

        tid = session["team_id"]
        params = service.load_params(g.db)
        allowed = {s["code"]: int(s["min_round"]) for s in params.studies}
        wanted, refused = [], []
        for code in request.form.getlist("study"):
            if code not in allowed:
                continue
            if allowed[code] > rnd:
                refused.append(code)
                continue
            wanted.append(code)

        current = dict(db.submission(g.db, rnd, tid) or {})
        if wanted:
            current["12.1"] = wanted
        else:
            current.pop("12.1", None)
        db.submit(g.db, rnd, tid, current, session["user"])
        with g.db:
            db.log(g.db, session["user"], "commission",
                   f"r{rnd}: {len(wanted)} studies")

        for code in refused:
            flash(f"{code} does not open until month {allowed[code]}.", "error")
        if wanted:
            cost = sum(float(s["price"]) for s in params.studies
                       if s["code"] in wanted)
            flash(f"{len(wanted)} stud{'y' if len(wanted) == 1 else 'ies'} "
                  f"commissioned for month {rnd}, PKR {cost:,.0f}. It is "
                  f"charged when the month is run, and the findings land here.",
                  "ok")
        elif not refused:
            flash("Nothing commissioned for this month.", "ok")
        return redirect(url_for("research"))


    @app.route("/brief", methods=["GET", "POST"])
    @login_required("team")
    def brief():
        """The rules, the market and the marking scheme, on one page."""
        game = db.game(g.db)
        if request.method == "POST":
            db.mark_briefing_seen(g.db, session["user"])
            return redirect(url_for("home"))
        me = db.account(g.db, session["user"])
        config = (db.founding(g.db, session["team_id"]) or {}).get("config", {})
        brand = config.get("brand_name")
        return render_template(
            "brief.html", rules=briefing.RULES, market=briefing.MARKET,
            pillars=briefing.PILLARS, endowment=service.endowment(g.db),
            setting_up=(game["start_mode"] == "founding" and game["round"] == 0),
            first_time=(me is not None and me["briefing_seen_at"] is None),
            objectives=founding.OBJECTIVES,
            team_name=me["display_name"] if me else "",
            company_name=config.get("company_name", ""),
            brand_name=brand if brand and brand != "Unnamed" else "",
            objective=config.get("objective", ""),
            handbook=service.HANDBOOK)

    @app.route("/company")
    @login_required("team")
    def company():
        """What you have: stock, cash, catalogue, people, capabilities."""
        tid = session["team_id"]
        return render_template(
            "company.html", position=service.company_position(g.db, tid),
            endowment=service.endowment(g.db), game=db.game(g.db))

    @app.route("/found", methods=["GET", "POST"])
    @login_required("team")
    def found():
        """Round 0. Set the business up, in the order you would really do it.

        Save as often as you like and watch the projection move. Submitting is
        the commitment, and it stays open until the instructor closes setup.
        """
        game = db.game(g.db)
        if game["start_mode"] != "founding":
            flash("This game starts from a running business - there is no "
                  "setup round.", "error")
            return redirect(url_for("home"))
        if game["round"] > 0:
            flash("Setup is closed. Trading has started.", "error")
            return redirect(url_for("home"))

        tid = session["team_id"]
        params = service.load_params(g.db)
        record = db.founding(g.db, tid)

        if request.method == "POST":
            f = service.founding_from_form(request.form, params)
            problems = founding.validate(f, params)
            committing = request.form.get("action") == "submit"
            if problems and committing:
                for problem in problems:
                    flash(problem, "error")
            else:
                db.save_founding(g.db, tid, service.founding_to_dict(f),
                                 session["user"], submitted=committing)
                with g.db:
                    db.log(g.db, session["user"],
                           "founding.submit" if committing else "founding.save",
                           f.brand_name)
                if committing:
                    flash("Your business is set up. You can still change it "
                          "until the instructor closes setup.", "ok")
                    return redirect(url_for("home"))
                flash("Draft saved. The projection below is from what you have "
                      "chosen so far.", "ok")
            record = db.founding(g.db, tid) or {"config": service.founding_to_dict(f),
                                                "submitted_at": None}
            current = f
        else:
            current = (service.founding_from_dict(record["config"], params)
                       if record else founding.Founding.default(params))

        return render_template(
            "found.html", f=current, params=params,
            stages=FOUNDING_STAGES,
            categories=founding.CATEGORIES,
            tiers=TIER_CHOICES, models=MODEL_CHOICES,
            sourcing=SOURCING_CHOICES, stacks=STACK_CHOICES,
            fulfilment=FULFILMENT_CHOICES, gateways=GATEWAY_CHOICES,
            segments=params.segments, skus=params.skus,
            catalogue=service.product_catalogue(params, current),
            blended=service.blended_margin(
                service.product_catalogue(params, current)),
            seg_driver=_segment_driver, seg_loyalty=_segment_loyalty,
            studies=[st for st in params.studies
                     if st["code"] in founding.FOUNDING_RESEARCH],
            research_discount=founding.FOUNDING_RESEARCH_DISCOUNT,
            capital=params["starting_cash"],
            payroll=params["payroll_base"],
            preview=service.founding_preview(g.db, current),
            problems=founding.validate(current, params),
            submitted=bool(record and record["submitted_at"]))

    @app.route("/submit", methods=["GET", "POST"])
    @login_required("team")
    def submit():
        game = db.game(g.db)
        rnd = game["open_round"]
        if not rnd:
            flash("Submissions are closed. The instructor will open the next round.",
                  "error")
            return redirect(url_for("home"))

        tid = session["team_id"]
        specs = service.open_decisions(g.db, rnd)
        # Discounting is set per product in the range grid now, so the single
        # site-wide lever no longer gets a tile of its own. The engine still
        # reads it - it is what the file runner and the archetypes use.
        specs = [s for s in specs if s.code != "2.2"]
        # 12.1 keeps its tile - it is a decision, and the red bar has to say
        # whether it was taken - but the tile is a link to the research desk,
        # so the form carries no field for it and must not be able to clear it.
        ELSEWHERE = {"12.1", targeting.DECISION}
        # Positioning comes before pricing: what you claim to be decides what
        # your prices are allowed to say.
        specs.sort(key=lambda s: (int(s.group[1:]), s.code != "1.5",
                                  tuple(int(p) for p in s.code.split("."))))
        current = db.submission(g.db, rnd, tid) or {}
        previous = db.submission(g.db, rnd - 1, tid) or {}
        params = service.load_params(g.db)
        # Readable choices for every lever backed by a reference table, so the
        # form can offer names and prices instead of codes.
        catalogues = {
            s.code: service.catalogue_options(params, s.catalogue)
            for s in specs if s.catalogue
        }

        if request.method == "POST":
            values, errors = {}, []
            for spec in specs:
                if spec.code in ELSEWHERE:
                    continue
                if spec.kind == "bundles":
                    raw = {}
                    for row in service.bundle_rows(g.db, tid, current):
                        code = row["code"]
                        if not request.form.get(f"bundle_{code}"):
                            continue
                        price = (request.form.get(f"bundleprice_{code}") or "").strip()
                        raw[code] = {"price": price} if price else {}
                    raw = raw or None
                elif spec.kind == "grid":
                    raw = {}
                    for row in service.monthly_catalogue(g.db, tid, current):
                        code = row["code"]
                        price = (request.form.get(f"price_{code}") or "").strip()
                        source = (request.form.get(f"sourcing_{code}") or "").strip()
                        disc = (request.form.get(f"discount_{code}") or "").strip()
                        cell = {}
                        if disc and _differs(disc, row["discount"] * 100):
                            cell["discount"] = disc
                        # Only a real change counts. Re-submitting the standing
                        # price should not read as a decision the team took.
                        if price and _differs(price, row["standing"]):
                            cell["price"] = price
                        if source and source != row["sourcing"]:
                            cell["sourcing"] = source
                        if cell:
                            raw[code] = cell
                    raw = raw or None
                elif spec.kind == "shares":
                    raw = {o["value"]: request.form.get(f"{spec.code}__{o['value']}", "")
                           for o in catalogues.get(spec.code, [])}
                    if not any(v.strip() for v in raw.values()):
                        raw = None
                elif spec.code in service.LIST_DECISIONS:
                    raw = request.form.getlist(spec.code)
                else:
                    raw = request.form.get(spec.code)
                try:
                    value = service.coerce(spec.code, raw)
                except (ValueError, TypeError):
                    errors.append(f"{spec.name}: {raw!r} is not a number")
                    continue
                if value is None or value == [] or value == {}:
                    continue           # blank means "use the default"
                problem = service.validate(spec.code, value)
                if problem:
                    errors.append(problem)
                else:
                    values[spec.code] = value
            if errors:
                for e in errors:
                    flash(e, "error")
            else:
                for code in ELSEWHERE:
                    if current.get(code):
                        values[code] = current[code]
                db.submit(g.db, rnd, tid, values, session["user"])
                with g.db:
                    db.log(g.db, session["user"], "submit", f"r{rnd}: {len(values)} decisions")
                flash(f"Submitted for round {rnd}. You may revise until the "
                      f"instructor closes it.", "ok")
                return redirect(url_for("home"))

        by_group: dict[str, list] = {}
        for spec in specs:
            by_group.setdefault(spec.group, []).append(spec)

        shelf = service.monthly_catalogue(g.db, tid, current)
        summaries = {
            s.code: service.decision_summary(s, current.get(s.code),
                                             catalogues.get(s.code))
            for s in specs
        }
        taken = sum(1 for s in specs if s.code in current)
        return render_template(
            "submit.html", round=rnd, by_group=by_group,
            current=current, previous=previous, catalogues=catalogues,
            default_shares={s.code: service.default_shares(params, s.catalogue)
                            for s in specs if s.kind == "shares"},
            standing={s.code: service.standing_choice(
                          s, previous, catalogues.get(s.code, []))
                      for s in specs if s.kind == "select"},
            shelf=shelf, summaries=summaries, taken=taken,
            campaigns_open=any(s.code == targeting.DECISION for s in specs),
            standing_campaigns=(
                "carried forward: " + (service.campaign_summary(
                    service.standing_campaigns(g.db, tid, rnd - 1)) or "")
                if service.standing_campaigns(g.db, tid, rnd - 1) is not None
                else ""),
            totals=service.shelf_totals(shelf),
            bundles=service.bundle_rows(g.db, tid, current),
            handbook={s.code: service.handbook_entry(s) for s in specs},
            handbook_url=url_for("handbook"),
            group_order=sorted(by_group, key=lambda gr: int(gr[1:])))

    @app.route("/results/<int:round_>")
    @login_required("team")
    def results(round_):
        html = service.team_report(g.db, session["team_id"], round_)
        if html is None:
            abort(404)
        return Response(html, mimetype="text/html")

    # --- Instructor -----------------------------------------------------------

    @app.route("/admin")
    @login_required("admin")
    def admin():
        game = db.game(g.db)
        nxt = game["round"] + 1
        teams = db.accounts(g.db, "team")
        foundings = db.foundings(g.db) if game["start_mode"] == "founding" else {}
        return render_template(
            "admin.html", next_round=nxt,
            status=db.submission_status(g.db, game["open_round"] or nxt),
            teams=teams, audit=db.audit(g.db, 12),
            overrides=db.overrides(g.db),
            setting_up=(game["start_mode"] == "founding" and game["round"] == 0),
            foundings=foundings)

    @app.post("/admin/open")
    @login_required("admin")
    def admin_open():
        rnd = int(request.form.get("round", 0)) or None
        db.set_game(g.db, open_round=rnd)
        with g.db:
            db.log(g.db, session["user"], "round.open",
                   f"r{rnd}" if rnd else "closed")
        flash(f"Round {rnd} open for submissions." if rnd
              else "Submissions closed.", "ok")
        return redirect(url_for("admin"))

    @app.post("/admin/run")
    @login_required("admin")
    def admin_run():
        try:
            result = service.process_round(g.db, session["user"])
        except BandViolation as exc:
            flash(f"Refused: {exc}", "error")
            return redirect(url_for("admin_params"))
        flash(f"Round {result['round']} processed "
              f"({result['submitted']} of {result['teams']} teams submitted; "
              f"the rest kept their previous decisions).", "ok")
        return redirect(url_for("admin"))

    @app.post("/admin/rollback")
    @login_required("admin")
    def admin_rollback():
        # Only a round that has actually run can be undone. A blank field used
        # to crash the page, and a round at or past the current one was
        # reported as a successful rollback while nothing changed.
        now = db.game(g.db)["round"]
        try:
            to = int(request.form.get("to_round", ""))
        except ValueError:
            to = -1
        if not 0 <= to < now:
            flash("Nothing to roll back yet - no round has been run."
                  if now == 0 else
                  f"Pick a round to go back to, from 0 to {now - 1}.", "error")
            return redirect(url_for("admin"))

        db.rollback(g.db, to, session["user"])
        undone = (f"Round {now} undone" if to == now - 1
                  else f"Rounds {to + 1} to {now} undone")
        flash(f"{undone}; the game is back at the end of round {to}. "
              f"Submissions are kept and now closed: fix a parameter and run "
              f"round {to + 1} again, or open it if a team needs to change "
              f"its decisions first.", "ok")
        return redirect(url_for("admin"))

    @app.route("/admin/decisions", methods=["GET", "POST"])
    @login_required("admin")
    def admin_decisions():
        game = db.game(g.db)
        rnd = int(request.args.get("round", game["round"] + 1))
        if request.method == "POST":
            rnd = int(request.form["round"])
            chosen = set(request.form.getlist("open"))
            for code in REGISTRY:
                db.set_window(g.db, code, rnd, code in chosen, session["user"])
            flash(f"Round {rnd}: {len(chosen)} decisions open.", "ok")
            return redirect(url_for("admin_decisions", round=rnd))

        open_now = {s.code for s in service.open_decisions(g.db, rnd)}
        by_group: dict[str, list] = {}
        for code, spec in REGISTRY.items():
            by_group.setdefault(spec.group, []).append(spec)
        return render_template("admin_decisions.html", round=rnd,
                               by_group=by_group, open_now=open_now)

    @app.route("/admin/params", methods=["GET", "POST"])
    @login_required("admin")
    def admin_params():
        params = service.load_params(g.db)
        if request.method == "POST":
            new = {}
            for name in params.specs:
                raw = request.form.get(name, "").strip()
                if raw:
                    new[name] = float(raw)
            try:
                service.P.load(new)            # band check before saving
            except BandViolation as exc:
                flash(f"Refused: {exc}", "error")
                return redirect(url_for("admin_params"))
            db.set_overrides(g.db, new, session["user"])
            flash("Saved. Changing economics mid-game affects future rounds only.",
                  "ok")
            return redirect(url_for("admin_params"))

        return render_template("admin_params.html", params=params,
                               overrides=db.overrides(g.db),
                               warnings=params.warnings)

    @app.get("/healthz")
    def healthz():
        """Liveness probe for the host. Confirms the database answers."""
        try:
            db.game(g.db)
        except Exception:
            return Response("unhealthy", status=503, mimetype="text/plain")
        return Response("ok", mimetype="text/plain")

    @app.post("/admin/teams/clear-initial")
    @login_required("admin")
    def admin_clear_initial():
        n = db.clear_initial_passwords(g.db, session["user"])
        flash(f"Cleared {n} initial passwords. They cannot be shown again.", "ok")
        return redirect(url_for("admin_teams"))

    @app.route("/admin/teams", methods=["GET", "POST"])
    @login_required("admin")
    def admin_teams():
        game = db.game(g.db)
        # The world is built once, on the first run, and sized then. Adding a
        # seat afterwards would hand a team a company the market has never
        # heard of, so the roster is fixed the moment trading starts.
        locked = game["round"] > 0

        if request.method == "POST":
            action = request.form.get("action", "password")
            if action != "password" and locked:
                flash("Trading has started. The roster is fixed from month 1.",
                      "error")
            elif action == "add":
                count = max(1, min(12, int(request.form.get("count", 1) or 1)))
                db.add_teams(g.db, count, session["user"])
                flash(f"Added {count} team{'' if count == 1 else 's'}. "
                      f"Their passwords are listed below.", "ok")
            elif action == "remove":
                tid = request.form.get("team_id", "")
                if len(db.accounts(g.db, "team")) <= 2:
                    flash("A market needs at least two teams.", "error")
                else:
                    db.remove_team(g.db, tid, session["user"])
                    flash(f"{tid} removed, with its setup and submissions.", "ok")
            elif action == "field":
                db.set_game(
                    g.db,
                    ai_competitors=max(0, min(8, int(
                        request.form.get("ai_competitors", 2) or 0))),
                    ai_aggression=max(0.0, min(1.0, float(
                        request.form.get("ai_aggression", 0.5) or 0.5))))
                flash("Field updated.", "ok")
            else:
                username = request.form["username"]
                password = request.form["password"].strip()
                if len(password) < 6:
                    flash("Password must be at least 6 characters.", "error")
                else:
                    db.set_password(g.db, username, password, session["user"])
                    flash(f"Password for {username} changed.", "ok")
            return redirect(url_for("admin_teams"))

        rows = db.accounts(g.db)
        foundings = db.foundings(g.db)
        for row in rows:
            row = dict(row)
        return render_template(
            "admin_teams.html", teams=rows, locked=locked,
            team_count=len(db.accounts(g.db, "team")),
            brands={tid: (rec.get("config") or {}).get("brand_name")
                    for tid, rec in foundings.items()})

    @app.post("/theme")
    @login_required()
    def set_theme():
        """Appearance, remembered against the account."""
        choice = (request.form.get("theme") or "").strip()
        if choice in db.THEMES:
            db.set_theme(g.db, session["user"], choice)
            session["theme"] = choice
        home = url_for("home") if session.get("role") == "team" \
            else url_for("admin")
        return redirect(safe_next(app, request.form.get("next"),
                                  session.get("role")) or home)

    @app.post("/setup")
    @login_required("team")
    def setup():
        """A team names itself, its company and its brand, and states its remit.

        Three names because they do three jobs: the team is who is playing, the
        company is the firm, and the brand is what the market sees - which is
        why market share is reported by brand.
        """
        tid = session["team_id"]
        team_name = (request.form.get("team_name") or "").strip()[:60]
        fields = {
            "company_name": (request.form.get("company_name") or "").strip()[:60],
            "brand_name": (request.form.get("brand_name") or "").strip()[:60],
            "objective": (request.form.get("objective") or "").strip(),
        }
        if fields["objective"] not in founding.OBJECTIVE_LABELS:
            fields["objective"] = ""
        choice = (request.form.get("theme") or "").strip()
        if choice in db.THEMES:
            db.set_theme(g.db, session["user"], choice)
            session["theme"] = choice
        if team_name:
            db.rename_team(g.db, tid, team_name, session["user"])
            session["name"] = team_name
        if any(fields.values()):
            db.set_identity(g.db, tid, fields, session["user"])
        flash("Saved." if (team_name or any(fields.values()))
              else "Nothing to change.",
              "ok" if (team_name or any(fields.values())) else "error")
        return redirect(url_for("brief"))

    @app.route("/admin/report/<team>/<int:round_>")
    @login_required("admin")
    def results_admin(team, round_):
        html = service.team_report(g.db, team, round_)
        if html is None:
            abort(404)
        return Response(html, mimetype="text/html")

    @app.route("/admin/console/<int:round_>")
    @login_required("admin")
    def admin_console(round_):
        html = service.instructor_console(g.db, round_)
        if html is None:
            abort(404)
        return Response(html, mimetype="text/html")

    @app.route("/admin/export/<int:round_>.csv")
    @login_required("admin")
    def admin_export(round_):
        """The escape hatch. If this app fails mid-class, download and run
        `py run.py round --decisions <file>` offline."""
        return Response(
            service.export_decisions(g.db, round_), mimetype="text/csv",
            headers={"Content-Disposition":
                     f"attachment; filename=decisions_r{round_}.csv"})
