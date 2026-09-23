"""Team portal and instructor console.

The things that must not break: a team cannot see another team's anything, a
round can always be rolled back and re-run, and the file-based escape hatch
stays available when the app is the problem.
"""
from __future__ import annotations

import pytest
from html import escape

from ecomsim.web import db, service
from ecomsim.web.app import create_app


@pytest.fixture
def game(tmp_path):
    path = tmp_path / "g.db"
    passwords = db.init(path, "Test", 3, rounds=12, admin_password="admin-pw")
    app = create_app(path)
    app.config["TESTING"] = True
    return app, passwords, path


def _client(app, username, password):
    c = app.test_client()
    r = c.post("/login", data={"username": username, "password": password})
    assert r.status_code in (302, 200)
    return c


# --- Authentication --------------------------------------------------------------

def test_everything_requires_a_login(game):
    app, _pw, _p = game
    anon = app.test_client()
    for path in ("/", "/submit", "/admin", "/admin/params", "/results/1"):
        assert anon.get(path).status_code == 302, path


def test_wrong_password_is_refused(game):
    app, _pw, _p = game
    r = app.test_client().post("/login", data={"username": "admin",
                                               "password": "nope"},
                               follow_redirects=True)
    assert b"Wrong username or password" in r.data


def test_a_team_cannot_reach_the_instructor_pages(game):
    app, pw, _p = game
    team = _client(app, "team_01", pw["team_01"])
    for path in ("/admin", "/admin/params", "/admin/decisions", "/admin/teams",
                 "/admin/console/1", "/admin/report/team_02/1",
                 "/admin/export/1.csv"):
        assert team.get(path).status_code == 403, path
    assert team.post("/admin/run").status_code == 403


def test_an_admin_who_opens_the_site_root_first_reaches_the_console(game):
    """The 403 people hit in class: root -> /login?next=/ -> team-only page."""
    app, _pw, _p = game
    c = app.test_client()
    assert c.get("/").headers["Location"].endswith("/login?next=/")
    r = c.post("/login?next=/", data={"username": "admin", "password": "admin-pw"})
    assert r.status_code == 302
    assert c.get(r.headers["Location"], follow_redirects=True).status_code == 200


def test_the_root_page_sends_an_instructor_to_the_console(game):
    app, _pw, _p = game
    admin = _client(app, "admin", "admin-pw")
    assert admin.get("/").headers["Location"].endswith("/admin")


def test_a_team_is_still_sent_where_it_asked_for(game):
    app, pw, _p = game
    c = app.test_client()
    r = c.post("/login?next=/submit", data={"username": "team_01",
                                            "password": pw["team_01"]})
    assert r.headers["Location"].endswith("/submit")


def test_login_will_not_bounce_to_another_site(game):
    """``next`` is attacker-supplied: only same-site paths are honoured."""
    app, _pw, _p = game
    for bad in ("//evil.example.com/", "https://evil.example.com/",
                "/\\evil.example.com/", "/no/such/route"):
        c = app.test_client()
        r = c.post("/login?next=" + bad, data={"username": "admin",
                                               "password": "admin-pw"})
        assert r.headers["Location"].endswith("/admin"), bad


def test_a_team_only_ever_sees_its_own_results(game):
    """There is no route that takes a team id - identity comes from the session."""
    app, pw, path = game
    con = db.connect(path)
    db.set_game(con, open_round=1)
    service.process_round(con)

    one = _client(app, "team_01", pw["team_01"])
    two = _client(app, "team_02", pw["team_02"])
    first = one.get("/results/1").data
    second = two.get("/results/1").data
    assert b"team_01" in first and b"team_02" not in first
    assert b"team_02" in second and b"team_01" not in second


def test_passwords_are_stored_hashed(game):
    _app, pw, path = game
    con = db.connect(path)
    stored = con.execute(
        "SELECT password_hash FROM account WHERE username = 'team_01'").fetchone()[0]
    assert pw["team_01"] not in stored
    assert stored.startswith(("pbkdf2:", "scrypt:"))


# --- Submission ------------------------------------------------------------------

def test_submission_needs_an_open_round(game):
    app, pw, _p = game
    team = _client(app, "team_01", pw["team_01"])
    r = team.get("/submit", follow_redirects=True)
    assert b"Submissions are closed" in r.data


def test_submit_revise_and_blank_means_default(game):
    app, pw, path = game
    con = db.connect(path)
    db.set_game(con, open_round=1)
    team = _client(app, "team_01", pw["team_01"])

    team.post("/submit", data={"3.1": "900000", "2.2": ""}, follow_redirects=True)
    saved = db.submission(con, 1, "team_01")
    assert saved["3.1"] == 900_000
    assert "2.2" not in saved, "a blank field must fall through to the default"

    team.post("/submit", data={"3.1": "500000"}, follow_redirects=True)
    assert db.submission(con, 1, "team_01")["3.1"] == 500_000, "revision must replace"


def test_implausible_values_are_refused(game):
    app, pw, path = game
    db.set_game(db.connect(path), open_round=1)
    team = _client(app, "team_01", pw["team_01"])
    for field, value, message in [
        ("9.2", "150%", b"between 0"),
        ("3.1", "-50000", b"cannot be negative"),
        ("3.1", "900000000", b"looks like a typo"),
        ("3.1", "lots", b"not a number"),
    ]:
        r = team.post("/submit", data={field: value}, follow_redirects=True)
        assert message in r.data, (field, value)


# --- The form a student actually reads -----------------------------------------------

def test_every_open_decision_explains_itself(game):
    """No lever reaches a student as a bare code with no explanation."""
    app, pw, path = game
    con = db.connect(path)
    db.set_game(con, open_round=1)
    team = _client(app, "team_01", pw["team_01"])
    page = team.get("/submit").data.decode()
    for spec in service.open_decisions(con, 1):
        if spec.code == "2.2":
            continue          # folded into the range grid; no tile of its own
        assert spec.help, f"{spec.code} has no help text"
        assert escape(spec.name) in page, spec.code
        assert escape(spec.help[:40]) in page, f"{spec.code} help not rendered"


def test_choices_are_offered_by_name_not_by_code(game):
    """A team picks "Supplier C - 7-day lead time", never types "C"."""
    app, pw, path = game
    db.set_game(db.connect(path), open_round=1)
    team = _client(app, "team_01", pw["team_01"])
    page = team.get("/submit").data.decode()
    assert "Speed Express" in page, "courier names must appear"
    assert escape("Category Demand & Seasonality") in \
        team.get("/research").data.decode(), "study names must appear"
    assert "Facewash 100ml" in page, "product names must appear"
    assert "Cash on delivery" in page
    assert "MR-01;MR-17" not in page, "no raw-code placeholder anywhere"


def test_a_percentage_field_takes_a_percentage(game):
    """The field says %, so 15 means 15% - not 1500%."""
    app, pw, path = game
    con = db.connect(path)
    db.set_game(con, open_round=1)
    team = _client(app, "team_01", pw["team_01"])
    team.post("/submit", data={"9.2": "15"}, follow_redirects=True)
    assert db.submission(con, 1, "team_01")["9.2"] == pytest.approx(0.15)


def test_a_choice_outside_the_list_is_refused(game):
    app, pw, path = game
    db.set_game(db.connect(path), open_round=1)
    team = _client(app, "team_01", pw["team_01"])
    r = team.post("/submit", data={"9.1": "maybe"}, follow_redirects=True)
    assert b"not one of the choices" in r.data


def test_courier_mix_reaches_the_engine_as_a_mix(game):
    """It is a split across couriers, and the engine reads a split."""
    app, pw, path = game
    con = db.connect(path)
    db.set_game(con, open_round=1)
    team = _client(app, "team_01", pw["team_01"])
    team.post("/submit", data={"8.3__speed": "50", "8.3__value": "20",
                               "8.3__wide": "30"}, follow_redirects=True)
    saved = db.submission(con, 1, "team_01")["8.3"]
    assert saved == {"speed": 0.5, "value": 0.2, "wide": 0.3}


def test_a_courier_mix_that_does_not_add_up_is_refused(game):
    app, pw, path = game
    db.set_game(db.connect(path), open_round=1)
    team = _client(app, "team_01", pw["team_01"])
    r = team.post("/submit", data={"8.3__speed": "50", "8.3__value": "20",
                                   "8.3__wide": "10"}, follow_redirects=True)
    assert b"must add up to 100%" in r.data


def test_research_is_commissioned_where_its_findings_are_read(game):
    """Studies are ordered on the research desk, not on the decision form.

    Picking studies next to the answers last month's studies gave is the only
    place the choice makes sense, so the decision tile is a door to that page.
    """
    app, pw, path = game
    con = db.connect(path)
    db.set_game(con, open_round=1)
    team = _client(app, "team_01", pw["team_01"])

    form = team.get("/submit").data.decode()
    assert "/research" in form, "the tile has to lead somewhere"

    desk = team.get("/research").data.decode()
    assert "110,000" in desk and "200,000" in desk, \
        "each study must show what it costs"
    team.post("/research/commission", data={"study": ["MR-01", "MR-03"]},
              follow_redirects=True)
    assert db.submission(con, 1, "team_01")["12.1"] == ["MR-01", "MR-03"]

    # Un-ticking is how you cancel; the order replaces the month's list.
    team.post("/research/commission", data={"study": ["MR-03"]},
              follow_redirects=True)
    assert db.submission(con, 1, "team_01")["12.1"] == ["MR-03"]


def test_submitting_the_form_cannot_wipe_a_commissioned_study(game):
    """The form carries no field for 12.1, so it must carry the stored value."""
    app, pw, path = game
    con = db.connect(path)
    db.set_game(con, open_round=1)
    team = _client(app, "team_01", pw["team_01"])
    team.post("/research/commission", data={"study": ["MR-07"]},
              follow_redirects=True)
    team.post("/submit", data={"3.1": "900000"}, follow_redirects=True)
    stored = db.submission(con, 1, "team_01")
    assert stored["12.1"] == ["MR-07"], "the decision form ate the order"
    assert stored["3.1"] == 900_000


def test_a_study_cannot_be_commissioned_before_it_opens(game):
    """min_round has sat in studies.csv unread since the catalogue was written."""
    app, pw, path = game
    con = db.connect(path)
    db.set_game(con, open_round=1)
    team = _client(app, "team_01", pw["team_01"])
    # MR-20 Q-Commerce Readiness does not open until month 4.
    team.post("/research/commission", data={"study": ["MR-20", "MR-01"]},
              follow_redirects=True)
    assert db.submission(con, 1, "team_01")["12.1"] == ["MR-01"]


# --- Instructor control ------------------------------------------------------------

def test_instructor_can_open_a_decision_early(game):
    app, _pw, path = game
    con = db.connect(path)
    admin = _client(app, "admin", "admin-pw")
    assert "11.1" not in {s.code for s in service.open_decisions(con, 1)}

    admin.post("/admin/decisions", data={"round": 1, "open": ["11.1", "3.1"]},
               follow_redirects=True)
    codes = {s.code for s in service.open_decisions(con, 1)}
    assert "11.1" in codes, "an override must be able to unlock early"
    assert "2.2" not in codes, "and to hold something back"


def test_parameter_override_outside_its_band_is_refused(game):
    app, _pw, path = game
    admin = _client(app, "admin", "admin-pw")
    r = admin.post("/admin/params", data={"saturation_exponent": "0.99"},
                   follow_redirects=True)
    assert b"Refused" in r.data
    assert db.overrides(db.connect(path)) == {}


def test_ai_competitor_count_is_instructor_controlled(game):
    """The field is set next to the roster it has to balance, not in economics."""
    app, _pw, path = game
    admin = _client(app, "admin", "admin-pw")
    admin.post("/admin/teams",
               data={"action": "field", "ai_competitors": "5",
                     "ai_aggression": "0.7"}, follow_redirects=True)
    row = db.game(db.connect(path))
    assert row["ai_competitors"] == 5 and row["ai_aggression"] == 0.7


def test_rollback_keeps_submissions_so_a_round_can_be_rerun(game):
    app, pw, path = game
    con = db.connect(path)
    admin = _client(app, "admin", "admin-pw")

    for rnd in (1, 2):
        admin.post("/admin/open", data={"round": rnd})
        _client(app, "team_01", pw["team_01"]).post(
            "/submit", data={"3.1": "700000"}, follow_redirects=True)
        admin.post("/admin/run", follow_redirects=True)
    assert db.game(con)["round"] == 2

    admin.post("/admin/rollback", data={"to_round": 1}, follow_redirects=True)
    assert db.game(con)["round"] == 1
    assert db.submission(con, 2, "team_01") is not None, "submissions must survive"
    admin.post("/admin/run", follow_redirects=True)
    assert db.game(con)["round"] == 2


def test_rollback_closes_the_round_that_was_open(game):
    """The next round was usually already open when a mistake came to light.
    Left open, teams kept submitting for a round that no longer came next."""
    app, _pw, path = game
    con = db.connect(path)
    admin = _client(app, "admin", "admin-pw")
    for _ in range(3):
        admin.post("/admin/run", follow_redirects=True)
    admin.post("/admin/open", data={"round": 4})

    page = admin.post("/admin/rollback", data={"to_round": 1},
                      follow_redirects=True).get_data(as_text=True)
    row = db.game(con)
    assert (row["round"], row["open_round"]) == (1, None)
    assert "Rounds 2 to 3 undone" in page
    assert "Submissions for round 2" in page, "the console must follow the rollback"


def test_rollback_refuses_a_round_it_cannot_undo(game):
    """A blank field crashed the page, and naming the current round reported
    success while nothing changed."""
    app, _pw, path = game
    con = db.connect(path)
    admin = _client(app, "admin", "admin-pw")
    for _ in range(2):
        admin.post("/admin/run", follow_redirects=True)

    for bad in ("", "two", "2", "5", "-1"):
        r = admin.post("/admin/rollback", data={"to_round": bad},
                       follow_redirects=True)
        assert r.status_code == 200, bad
        assert "undone" not in r.get_data(as_text=True), bad
        assert db.game(con)["round"] == 2, bad
        assert [x["round"] for x in con.execute(
            "SELECT round FROM round_log ORDER BY round")] == [1, 2], bad


def test_rollback_offers_only_rounds_that_have_run(game):
    app, _pw, _path = game
    admin = _client(app, "admin", "admin-pw")
    assert "Nothing to roll back" in admin.get("/admin").get_data(as_text=True)
    for _ in range(2):
        admin.post("/admin/run", follow_redirects=True)
    page = admin.get("/admin").get_data(as_text=True)
    assert '<option value="1">Undo round 2' in page
    assert '<option value="0">Undo rounds 1 to 2' in page
    assert 'value="2"' not in page.split('id="rb"')[1].split("</select>")[0]


def test_rollback_to_the_start_reopens_setup(game):
    """Rolling back to round 0 is how the roster and the setups are changed
    once trading has begun, so it has to hand setup back to the teams."""
    app, pw, path = game
    admin = _client(app, "admin", "admin-pw")
    admin.post("/admin/run", follow_redirects=True)
    team = _client(app, "team_01", pw["team_01"])
    assert team.get("/found").status_code == 302, "setup is closed while trading"

    admin.post("/admin/rollback", data={"to_round": 0}, follow_redirects=True)
    assert db.game(db.connect(path))["round"] == 0
    assert db.load_world(db.connect(path)) is None
    assert team.get("/found").status_code == 200
    admin.post("/admin/run", follow_redirects=True)
    assert db.game(db.connect(path))["round"] == 1


def test_teams_that_do_not_submit_keep_their_previous_decisions(game):
    app, pw, path = game
    con = db.connect(path)
    admin = _client(app, "admin", "admin-pw")
    admin.post("/admin/open", data={"round": 1})
    _client(app, "team_01", pw["team_01"]).post(
        "/submit", data={"3.1": "700000"}, follow_redirects=True)
    admin.post("/admin/run", follow_redirects=True)

    world = db.load_world(con)
    assert all(len(t.history) == 1 for t in world.teams.values()), \
        "a silent team is still played, not skipped"


# --- The escape hatch ---------------------------------------------------------------

def test_decisions_export_matches_the_file_runner_format(game):
    """If the app fails mid-class, this CSV runs the round offline."""
    app, pw, path = game
    db.set_game(db.connect(path), open_round=1)
    team = _client(app, "team_01", pw["team_01"])
    team.post("/research/commission", data={"study": ["MR-01", "MR-17"]},
              follow_redirects=True)
    team.post("/submit", data={"3.1": "900000"}, follow_redirects=True)

    csv_text = _client(app, "admin", "admin-pw").get("/admin/export/1.csv").data.decode()
    assert csv_text.splitlines()[0] == "team_id,decision,value"

    from ecomsim.io_csv import read_decisions
    out = path.parent / "d.csv"
    out.write_text(csv_text, encoding="utf-8")
    parsed = read_decisions(out)
    assert parsed["team_01"]["3.1"] == 900_000
    assert parsed["team_01"]["12.1"] == ["MR-01", "MR-17"]


# --- Campaign setup (3.10) -------------------------------------------------------

def _to_campaigns(app, pw, path, rounds=2):
    admin = _client(app, "admin", "admin-pw")
    for _ in range(rounds):
        admin.post("/admin/run", follow_redirects=True)
    admin.post("/admin/open", data={"round": rounds + 1})
    return admin, _client(app, "team_01", pw["team_01"])


HAIR_OIL = {"use_meta_0": "1", "name_meta_0": "Hair oil", "share_meta_0": "60",
            "skus_meta_0": "SKU-08", "ages_meta_0": ["25-34", "35-44"],
            "gender_meta_0": "female", "geo_meta_0": ["T2", "Rest"],
            "interests_meta_0": "home", "language_meta_0": "urdu",
            "format_meta_0": "feed", "objective_meta_0": "conversions",
            "use_meta_1": "1", "name_meta_1": "Rest", "share_meta_1": "40",
            "gender_meta_1": "all", "objective_meta_1": "traffic"}


def test_campaigns_are_saved_as_a_decision_and_run(game):
    app, pw, path = game
    con = db.connect(path)
    admin, team = _to_campaigns(app, pw, path)
    page = team.post("/campaigns", data=HAIR_OIL, follow_redirects=True).get_data(as_text=True)
    assert "Campaigns saved for month 3" in page
    saved = db.submission(con, 3, "team_01")["3.10"]
    assert [c["name"] for c in saved] == ["Hair oil", "Rest"]
    assert saved[0]["share"] == pytest.approx(0.6) and saved[0]["gender"] == "female"
    assert "Meta 2" in team.get("/submit").get_data(as_text=True)

    admin.post("/admin/run", follow_redirects=True)
    rows = db.load_world(con).teams["team_01"].history[-1]["campaigns"]
    assert [r["name"] for r in rows if r["channel"] == "meta"] == ["Hair oil", "Rest"]
    page = team.get("/campaigns").get_data(as_text=True)
    assert "How last month&#39;s campaigns did" in page or "How last month's campaigns did" in page


def test_campaigns_carry_forward_until_changed_and_broad_is_a_setting(game):
    app, pw, path = game
    con = db.connect(path)
    admin, team = _to_campaigns(app, pw, path)
    team.post("/campaigns", data=HAIR_OIL, follow_redirects=True)
    admin.post("/admin/run", follow_redirects=True)
    admin.post("/admin/open", data={"round": 4})
    team.post("/submit", data={"3.1": "500000"}, follow_redirects=True)
    assert "3.10" not in db.submission(con, 4, "team_01")
    admin.post("/admin/run", follow_redirects=True)
    rows = db.load_world(con).teams["team_01"].history[-1]["campaigns"]
    assert "Hair oil" in [r["name"] for r in rows], "month 4 kept month 3's campaigns"

    admin.post("/admin/open", data={"round": 5})
    team.post("/campaigns", data={"action": "broad"}, follow_redirects=True)
    assert db.submission(con, 5, "team_01")["3.10"] == []
    admin.post("/admin/run", follow_redirects=True)
    rows = db.load_world(con).teams["team_01"].history[-1]["campaigns"]
    assert all(r["name"].startswith("Broad") for r in rows)


def test_shares_must_add_to_a_hundred_and_the_form_survives_the_refusal(game):
    app, pw, path = game
    con = db.connect(path)
    _admin, team = _to_campaigns(app, pw, path)
    bad = dict(HAIR_OIL, share_meta_1="10")
    r = team.post("/campaigns", data=bad)
    page = r.get_data(as_text=True)
    assert r.status_code == 400
    assert "share 70% of the budget" in page
    assert 'value="Hair oil"' in page, "what the team typed is shown back"
    assert "3.10" not in (db.submission(con, 3, "team_01") or {})


def test_campaigns_cannot_be_set_before_they_open(game):
    app, pw, path = game
    con = db.connect(path)
    admin = _client(app, "admin", "admin-pw")
    admin.post("/admin/open", data={"round": 1})
    team = _client(app, "team_01", pw["team_01"])
    page = team.get("/campaigns").get_data(as_text=True)
    assert "Campaign setup is not open" in page
    team.post("/campaigns", data=HAIR_OIL, follow_redirects=True)
    assert "3.10" not in (db.submission(con, 1, "team_01") or {})


def test_campaigns_survive_the_offline_escape_hatch(game, tmp_path):
    from ecomsim.io_csv import read_decisions
    app, pw, path = game
    con = db.connect(path)
    admin, team = _to_campaigns(app, pw, path)
    team.post("/campaigns", data=HAIR_OIL, follow_redirects=True)
    csv_file = tmp_path / "d.csv"
    csv_file.write_text(service.export_decisions(con, 3), encoding="utf-8")
    back = read_decisions(csv_file)["team_01"]["3.10"]
    assert back == db.submission(con, 3, "team_01")["3.10"]


def test_an_ab_test_is_set_from_the_campaign_page(game):
    app, pw, path = game
    con = db.connect(path)
    admin, team = _to_campaigns(app, pw, path)
    team.post("/campaigns", data=dict(HAIR_OIL, ab_meta="1"), follow_redirects=True)
    saved = db.submission(con, 3, "team_01")["3.10"]
    assert [c.get("test") for c in saved] == ["A", "B"]
    admin.post("/admin/run", follow_redirects=True)
    page = team.get("/campaigns").get_data(as_text=True)
    assert "A/B test on Meta" in page and "Confidence" in page
    report = team.get("/results/3").get_data(as_text=True)
    assert "A/B test on Meta" in report


def test_an_ab_test_needs_both_campaigns(game):
    app, pw, path = game
    _admin, team = _to_campaigns(app, pw, path)
    lone = {k: v for k, v in HAIR_OIL.items() if not k.endswith("meta_1")}
    lone.update(share_meta_0="100", ab_meta="1")
    r = team.post("/campaigns", data=lone)
    assert r.status_code == 400
    assert "needs campaigns 1 and 2 both running" in r.get_data(as_text=True)


def test_the_marketing_guide_teaches_without_giving_the_answers_away(game):
    from ecomsim import params as P, targeting as T
    app, pw, path = game
    team = _client(app, "team_01", pw["team_01"])
    page = team.get("/guide/marketing").get_data(as_text=True)
    for heading in ("The numbers", "Reading them together", "Building an audience",
                    "A/B testing", "How many orders a test needs"):
        assert heading in page, heading
    assert f"{T.orders_needed(0.10):,}" in page, "test sizes come from the verdict's maths"
    for a in P.load().audiences:
        assert a["mistake"] not in page, "who buys each product is for the debrief"
    assert "/guide/marketing" in team.get("/campaigns").get_data(as_text=True)
    admin = _client(app, "admin", "admin-pw")
    assert admin.get("/guide/marketing").status_code == 200


def test_test_sizes_shrink_with_the_edge_and_grow_with_a_lopsided_split():
    from ecomsim import targeting as T
    sizes = [T.orders_needed(e) for e in (0.05, 0.1, 0.2, 0.3)]
    assert sizes == sorted(sizes, reverse=True)
    assert T.orders_needed(0.1, 0.1) > 2 * T.orders_needed(0.1)
