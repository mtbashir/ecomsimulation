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
    ("offer", "3. What you sell and where",
     "Your opening range and the channel you sell it through. A wide range "
     "spreads your stock thin; a narrow one leaves demand on the table."),
    ("supply", "4. Where the stock comes from",
     "Cheap, slow and far, or expensive, quick and near. This decides how much "
     "cash sits in a container and how fast you can react to a good month."),
    ("build", "5. What you build it on",
     "Your storefront, your warehouse and your payments. The capex is paid now "
     "and is not refundable, so what you choose here constrains what you can "
     "spend on customers for months."),
    ("money", "6. Where the money and the people go",
     "Twelve million rupees, split four ways, and a payroll to allocate. The "
     "floors and ceilings exist because an all-in bet on stock puts most teams "
     "out of cash by month three."),
    ("plan", "7. What you are promising",
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
                               team_id=row["team_id"], name=row["display_name"])
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

        return render_template(
            "team_home.html",
            open_round=open_round,
            setting_up=setting_up,
            founding_done=bool(founding and founding["submitted_at"]),
            founding_started=founding is not None,
            heading=heading, note=note,
            submitted=db.submission(g.db, open_round, tid) is not None
                      if open_round else False,
            rounds=list(range(1, game["round"] + 1)),
            position=service.company_position(g.db, tid),
            research=_research_bought(g.db, tid, game["round"]),
        )

    def _research_bought(con, team_id, upto_round):
        """Every study this team has paid for, newest first."""
        params = service.load_params(con)
        by_code = {s["code"]: s for s in params.studies}
        out = []
        for rnd in range(upto_round, 0, -1):
            for code in (db.submission(con, rnd, team_id) or {}).get("12.1", []):
                row = by_code.get(code)
                if row:
                    out.append({"round": rnd, "name": row["name"],
                                "price": float(row["price"]), "code": code})
        return out

    @app.route("/brief", methods=["GET", "POST"])
    @login_required("team")
    def brief():
        """The rules, the market and the marking scheme, on one page."""
        game = db.game(g.db)
        if request.method == "POST":
            db.mark_briefing_seen(g.db, session["user"])
            return redirect(url_for("home"))
        me = db.account(g.db, session["user"])
        return render_template(
            "brief.html", rules=briefing.RULES, market=briefing.MARKET,
            pillars=briefing.PILLARS, endowment=service.endowment(g.db),
            setting_up=(game["start_mode"] == "founding" and game["round"] == 0),
            first_time=(me is not None and me["briefing_seen_at"] is None))

    @app.route("/company")
    @login_required("team")
    def company():
        """What you have: stock, cash, catalogue, people, capabilities."""
        return render_template(
            "company.html", position=service.company_position(g.db, session["team_id"]),
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
                if spec.kind == "shares":
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
                db.submit(g.db, rnd, tid, values, session["user"])
                with g.db:
                    db.log(g.db, session["user"], "submit", f"r{rnd}: {len(values)} decisions")
                flash(f"Submitted for round {rnd}. You may revise until the "
                      f"instructor closes it.", "ok")
                return redirect(url_for("home"))

        by_group: dict[str, list] = {}
        for spec in specs:
            by_group.setdefault(spec.group, []).append(spec)
        return render_template(
            "submit.html", round=rnd, by_group=by_group,
            current=current, previous=previous, catalogues=catalogues,
            default_shares={s.code: service.default_shares(params, s.catalogue)
                            for s in specs if s.kind == "shares"},
            standing={s.code: service.standing_choice(
                          s, previous, catalogues.get(s.code, []))
                      for s in specs if s.kind == "select"})

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
        to = int(request.form["to_round"])
        db.rollback(g.db, to, session["user"])
        flash(f"Rolled back to round {to}. Submissions are kept, so you can "
              f"fix a parameter and re-run.", "ok")
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
            db.set_game(g.db,
                        ai_competitors=int(request.form.get("ai_competitors", 2)),
                        ai_aggression=float(request.form.get("ai_aggression", 0.5)))
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
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"].strip()
            if len(password) < 6:
                flash("Password must be at least 6 characters.", "error")
            else:
                db.set_password(g.db, username, password, session["user"])
                flash(f"Password for {username} changed.", "ok")
            return redirect(url_for("admin_teams"))
        return render_template("admin_teams.html", teams=db.accounts(g.db))

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
