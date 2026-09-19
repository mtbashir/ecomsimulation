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

from ..decisions import REGISTRY
from ..params import BandViolation
from . import db, service

GROUP_NAMES = {
    "G1": "Assortment & product", "G2": "Pricing", "G3": "Marketing",
    "G4": "Channel", "G5": "Site & experience", "G6": "CRM & retention",
    "G7": "Supply & procurement", "G8": "Fulfilment", "G9": "Payments",
    "G10": "Customer service", "G11": "Technology & AI", "G12": "Finance & research",
}


def create_app(database: str | Path | None = None) -> Flask:
    app = Flask(__name__)
    app.config["DATABASE"] = str(
        database or os.environ.get("ECOMSIM_DB", "game.db"))
    # A stable secret keeps sessions alive across restarts; a generated one is
    # fine for a single class but logs everyone out when the laptop sleeps.
    app.secret_key = os.environ.get("ECOMSIM_SECRET") or secrets.token_hex(32)

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


# --- Auth ---------------------------------------------------------------------

def login_required(role: str | None = None):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            if "user" not in session:
                return redirect(url_for("login", next=request.path))
            if role and session.get("role") != role:
                abort(403)
            return fn(*a, **kw)
        return wrapper
    return deco


def register_routes(app: Flask) -> None:

    @app.route("/login", methods=["GET", "POST"])
    def login():
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
                return redirect(request.args.get("next")
                                or url_for("admin" if row["role"] == "admin" else "home"))
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    # --- Team portal ----------------------------------------------------------

    @app.route("/")
    @login_required("team")
    def home():
        game = db.game(g.db)
        tid = session["team_id"]
        open_round = game["open_round"]
        return render_template(
            "team_home.html",
            open_round=open_round,
            submitted=db.submission(g.db, open_round, tid) is not None if open_round else False,
            rounds=list(range(1, game["round"] + 1)),
        )

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

        if request.method == "POST":
            values, errors = {}, []
            for spec in specs:
                raw = (request.form.getlist(spec.code)
                       if spec.code in service.LIST_DECISIONS
                       else request.form.get(spec.code))
                try:
                    value = service.coerce(spec.code, raw)
                except ValueError:
                    errors.append(f"{spec.name}: {raw!r} is not a number")
                    continue
                if value is None or value == []:
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
        return render_template("submit.html", round=rnd, by_group=by_group,
                               current=current, previous=previous)

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
        return render_template(
            "admin.html", next_round=nxt,
            status=db.submission_status(g.db, game["open_round"] or nxt),
            teams=teams, audit=db.audit(g.db, 12),
            overrides=db.overrides(g.db))

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
