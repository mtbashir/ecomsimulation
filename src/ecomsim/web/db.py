"""SQLite store for a running game.

One file you can copy, inspect with any SQLite browser, and restore from. The
engine stays a pure function over a state vector; this module only persists
what goes in and what came out.

Two properties matter more than anything else here, because nobody is on call
during a class:

1. Every round is replayable. Decisions are stored as submitted, so a corrupted
   world can be rebuilt by replaying them through the engine.
2. There is always a way out. Decisions export to the same CSV the file-based
   runner reads, so a failure mid-session does not stop the session.
"""
from __future__ import annotations

import json
import pickle
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from werkzeug.security import check_password_hash, generate_password_hash

SCHEMA = """
CREATE TABLE IF NOT EXISTS game (
  id             INTEGER PRIMARY KEY CHECK (id = 1),
  name           TEXT    NOT NULL,
  preset         TEXT    NOT NULL DEFAULT 'advanced',
  round          INTEGER NOT NULL DEFAULT 0,
  total_rounds   INTEGER NOT NULL DEFAULT 12,
  open_round     INTEGER,            -- round teams may submit for; NULL = closed
  ai_competitors INTEGER NOT NULL DEFAULT 2,
  ai_aggression  REAL    NOT NULL DEFAULT 0.5,
  -- 'founding': teams set up their business in Round 0 before trading.
  -- 'going_concern': everyone starts from the same running business (docs/05).
  start_mode     TEXT    NOT NULL DEFAULT 'founding',
  overrides      TEXT    NOT NULL DEFAULT '{}',   -- parameter overrides, JSON
  created_at     TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS account (
  id            INTEGER PRIMARY KEY,
  username      TEXT    NOT NULL UNIQUE,
  password_hash TEXT    NOT NULL,
  role          TEXT    NOT NULL CHECK (role IN ('admin', 'team')),
  team_id       TEXT,               -- NULL for admins
  display_name  TEXT    NOT NULL,
  initial_password TEXT,             -- one-time handover; cleared once seen
  briefing_seen_at TEXT,             -- NULL until the team has read the brief
  created_at    TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS submission (
  id           INTEGER PRIMARY KEY,
  round        INTEGER NOT NULL,
  team_id      TEXT    NOT NULL,
  decisions    TEXT    NOT NULL,    -- JSON {code: value}
  submitted_at TEXT    NOT NULL,
  submitted_by TEXT    NOT NULL,
  UNIQUE (round, team_id)
);

-- Which decisions are open in which round. Absent means "follow the preset".
CREATE TABLE IF NOT EXISTS decision_window (
  code       TEXT    NOT NULL,
  round      INTEGER NOT NULL,
  is_open    INTEGER NOT NULL,
  PRIMARY KEY (code, round)
);

-- Round 0. One row per team, holding the fourteen founding choices.
CREATE TABLE IF NOT EXISTS founding (
  team_id      TEXT PRIMARY KEY,
  config       TEXT NOT NULL,        -- JSON, the Founding dataclass fields
  submitted_at TEXT,                 -- NULL while still a draft
  submitted_by TEXT
);

CREATE TABLE IF NOT EXISTS round_log (
  round       INTEGER PRIMARY KEY,
  world_blob  BLOB    NOT NULL,     -- state AFTER the round, for rollback
  config_hash TEXT    NOT NULL,
  processed_at TEXT   NOT NULL,
  note        TEXT
);

CREATE TABLE IF NOT EXISTS audit (
  id      INTEGER PRIMARY KEY,
  at      TEXT NOT NULL,
  actor   TEXT NOT NULL,
  action  TEXT NOT NULL,
  detail  TEXT
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def connect(path: str | Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(path), detect_types=sqlite3.PARSE_DECLTYPES)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    # WAL survives an abrupt shutdown far better, which matters when the person
    # running this is mid-class and closes the laptop.
    con.execute("PRAGMA journal_mode = WAL")
    return con


def migrate(con) -> None:
    """Bring an older database up to the current schema, in place.

    A game may be mid-semester when the app is updated, so a new column has to
    arrive without anybody exporting and re-importing a cohort.
    """
    con.executescript(SCHEMA)
    for table, column, ddl in [
        ("game", "start_mode", "TEXT NOT NULL DEFAULT 'founding'"),
        ("account", "briefing_seen_at", "TEXT"),
    ]:
        have = {r["name"] for r in con.execute(f"PRAGMA table_info({table})")}
        if column not in have:
            con.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def init(path: str | Path, name: str, teams: int, preset: str = "advanced",
         rounds: int = 12, admin_password: str = "changeme",
         start_mode: str = "founding") -> dict:
    """Create a game and its accounts. Returns the generated team passwords."""
    import secrets

    con = connect(path)
    with con:
        migrate(con)
        con.execute(
            "INSERT OR REPLACE INTO game "
            "(id, name, preset, round, total_rounds, open_round, start_mode, "
            "created_at) VALUES (1, ?, ?, 0, ?, NULL, ?, ?)",
            (name, preset, rounds, start_mode, _now()))
        con.execute(
            "INSERT OR REPLACE INTO account "
            "(username, password_hash, role, team_id, display_name, created_at) "
            "VALUES ('admin', ?, 'admin', NULL, 'Instructor', ?)",
            (generate_password_hash(admin_password), _now()))

        passwords = {}
        for i in range(1, teams + 1):
            tid = f"team_{i:02d}"
            # Readable but not guessable: teams type these once, on paper.
            pw = f"{secrets.choice(WORDS)}-{secrets.choice(WORDS)}-{secrets.randbelow(90) + 10}"
            passwords[tid] = pw
            con.execute(
                "INSERT OR REPLACE INTO account "
                "(username, password_hash, role, team_id, display_name, "
                "initial_password, created_at) VALUES (?, ?, 'team', ?, ?, ?, ?)",
                (tid, generate_password_hash(pw), tid, f"Team {i}", pw, _now()))
        log(con, "system", "game.init",
            f"{name}: {teams} teams, {rounds} rounds, preset {preset}, "
            f"{start_mode.replace('_', ' ')} start")
    return passwords


# --- The founding round ----------------------------------------------------------

def save_founding(con, team_id: str, config: dict, by: str,
                  submitted: bool = False) -> None:
    """Store a team's Round 0 setup. A draft keeps submitted_at NULL."""
    with con:
        con.execute(
            "INSERT INTO founding (team_id, config, submitted_at, submitted_by) "
            "VALUES (?, ?, ?, ?) ON CONFLICT (team_id) DO UPDATE SET "
            "config = excluded.config, submitted_at = excluded.submitted_at, "
            "submitted_by = excluded.submitted_by",
            (team_id, json.dumps(config, sort_keys=True),
             _now() if submitted else None, by))


def founding(con, team_id: str) -> dict | None:
    row = con.execute("SELECT config, submitted_at FROM founding WHERE team_id = ?",
                      (team_id,)).fetchone()
    if row is None:
        return None
    return {"config": json.loads(row["config"]),
            "submitted_at": row["submitted_at"]}


def foundings(con) -> dict[str, dict]:
    """Every team's setup, submitted or draft, keyed by team."""
    return {r["team_id"]: {"config": json.loads(r["config"]),
                           "submitted_at": r["submitted_at"]}
            for r in con.execute("SELECT * FROM founding").fetchall()}


def add_teams(con, count: int, actor: str = "admin") -> dict:
    """Add teams to a game that has not started trading. Returns new passwords.

    Numbering continues from the highest existing team, so a team that was
    removed does not have its identity handed to somebody else.
    """
    import secrets

    existing = {r["team_id"] for r in accounts(con, "team")}
    highest = max((int(t.split("_")[1]) for t in existing), default=0)
    passwords = {}
    with con:
        for offset in range(1, count + 1):
            n = highest + offset
            tid = f"team_{n:02d}"
            pw = (f"{secrets.choice(WORDS)}-{secrets.choice(WORDS)}-"
                  f"{secrets.randbelow(90) + 10}")
            passwords[tid] = pw
            con.execute(
                "INSERT OR REPLACE INTO account "
                "(username, password_hash, role, team_id, display_name, "
                "initial_password, created_at) VALUES (?, ?, 'team', ?, ?, ?, ?)",
                (tid, generate_password_hash(pw), tid, f"Team {n}", pw, _now()))
        log(con, actor, "teams.add", f"{count} added")
    return passwords


def remove_team(con, team_id: str, actor: str = "admin") -> None:
    """Remove a team and everything it owns. Only before trading starts."""
    with con:
        con.execute("DELETE FROM account WHERE team_id = ?", (team_id,))
        con.execute("DELETE FROM founding WHERE team_id = ?", (team_id,))
        con.execute("DELETE FROM submission WHERE team_id = ?", (team_id,))
        log(con, actor, "teams.remove", team_id)


def rename_team(con, team_id: str, display_name: str, actor: str = "admin") -> None:
    with con:
        con.execute("UPDATE account SET display_name = ? WHERE team_id = ?",
                    (display_name, team_id))
        log(con, actor, "teams.rename", f"{team_id}: {display_name}")


def set_identity(con, team_id: str, fields: dict, actor: str = "admin") -> None:
    """Change the names and the objective on the founding record.

    The world blob keeps whatever it was built with, so everything that shows a
    name reads it from here instead - a rename lands everywhere at once and no
    stored result is rewritten.
    """
    record = founding(con, team_id)
    config = record["config"] if record else {}
    config.update({k: v for k, v in fields.items() if v})
    with con:
        con.execute(
            "INSERT INTO founding (team_id, config, submitted_at, submitted_by) "
            "VALUES (?, ?, ?, ?) ON CONFLICT (team_id) DO UPDATE SET "
            "config = excluded.config",
            (team_id, json.dumps(config, sort_keys=True),
             (record or {}).get("submitted_at"), actor))
        log(con, actor, "teams.identity",
            f"{team_id}: {', '.join(f'{k}={v}' for k, v in fields.items() if v)}")


def mark_briefing_seen(con, username: str) -> None:
    with con:
        con.execute("UPDATE account SET briefing_seen_at = ? "
                    "WHERE username = ? AND briefing_seen_at IS NULL",
                    (_now(), username))


def account(con, username: str) -> sqlite3.Row | None:
    return con.execute("SELECT * FROM account WHERE username = ?",
                       (username,)).fetchone()


WORDS = ["indus", "ravi", "chenab", "jhelum", "sutlej", "hunza", "swat", "bolan",
         "khyber", "thar", "makran", "salt", "kirthar", "margalla", "chaukhandi"]


# --- Game state ----------------------------------------------------------------

def game(con) -> sqlite3.Row:
    return con.execute("SELECT * FROM game WHERE id = 1").fetchone()


def set_game(con, **fields) -> None:
    if not fields:
        return
    sets = ", ".join(f"{k} = ?" for k in fields)
    with con:
        con.execute(f"UPDATE game SET {sets} WHERE id = 1", tuple(fields.values()))


def overrides(con) -> dict:
    return json.loads(game(con)["overrides"])


def set_overrides(con, values: dict, actor: str = "admin") -> None:
    with con:
        con.execute("UPDATE game SET overrides = ? WHERE id = 1",
                    (json.dumps(values, sort_keys=True),))
        log(con, actor, "params.override", json.dumps(values, sort_keys=True))


# --- Accounts -------------------------------------------------------------------

def authenticate(con, username: str, password: str) -> sqlite3.Row | None:
    row = con.execute("SELECT * FROM account WHERE username = ?",
                      (username.strip().lower(),)).fetchone()
    if row and check_password_hash(row["password_hash"], password):
        return row
    return None


def set_password(con, username: str, password: str, actor: str = "admin") -> None:
    with con:
        con.execute("UPDATE account SET password_hash = ?, initial_password = NULL "
                    "WHERE username = ?",
                    (generate_password_hash(password), username))
        log(con, actor, "account.password", username)


def clear_initial_passwords(con, actor: str = "admin") -> int:
    """Wipe the one-time handover column once the instructor has the passwords.

    On a hosted box there is no shell to read generated passwords from, so they
    sit here until confirmed. The hashes are what authenticate; this is only a
    handover, and it should not outlive the handover.
    """
    with con:
        n = con.execute(
            "UPDATE account SET initial_password = NULL "
            "WHERE initial_password IS NOT NULL").rowcount
        log(con, actor, "account.clear_initial", f"{n} cleared")
    return n


def accounts(con, role: str | None = None) -> list[sqlite3.Row]:
    if role:
        return con.execute("SELECT * FROM account WHERE role = ? ORDER BY username",
                           (role,)).fetchall()
    return con.execute("SELECT * FROM account ORDER BY role, username").fetchall()


# --- Submissions ----------------------------------------------------------------

def submit(con, round_: int, team_id: str, decisions: dict, by: str) -> None:
    """Store a team's decisions. Re-submitting replaces, so teams may revise."""
    with con:
        con.execute(
            "INSERT INTO submission (round, team_id, decisions, submitted_at, submitted_by) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT (round, team_id) DO UPDATE SET "
            "decisions = excluded.decisions, submitted_at = excluded.submitted_at, "
            "submitted_by = excluded.submitted_by",
            (round_, team_id, json.dumps(decisions, sort_keys=True), _now(), by))


def submission(con, round_: int, team_id: str) -> dict | None:
    row = con.execute("SELECT decisions FROM submission WHERE round = ? AND team_id = ?",
                      (round_, team_id)).fetchone()
    return json.loads(row["decisions"]) if row else None


def submissions(con, round_: int) -> dict[str, dict]:
    rows = con.execute("SELECT team_id, decisions FROM submission WHERE round = ?",
                       (round_,)).fetchall()
    return {r["team_id"]: json.loads(r["decisions"]) for r in rows}


def submission_status(con, round_: int) -> dict[str, str]:
    rows = con.execute(
        "SELECT team_id, submitted_at FROM submission WHERE round = ?",
        (round_,)).fetchall()
    return {r["team_id"]: r["submitted_at"] for r in rows}


# --- Decision windows ------------------------------------------------------------

def windows(con, round_: int) -> dict[str, bool]:
    rows = con.execute("SELECT code, is_open FROM decision_window WHERE round = ?",
                       (round_,)).fetchall()
    return {r["code"]: bool(r["is_open"]) for r in rows}


def set_window(con, code: str, round_: int, is_open: bool, actor: str = "admin") -> None:
    with con:
        con.execute(
            "INSERT INTO decision_window (code, round, is_open) VALUES (?, ?, ?) "
            "ON CONFLICT (code, round) DO UPDATE SET is_open = excluded.is_open",
            (code, round_, int(is_open)))
        log(con, actor, "decision.window", f"{code} r{round_} -> {'open' if is_open else 'closed'}")


# --- Round log (and rollback) -----------------------------------------------------

def save_round(con, round_: int, world, config_hash: str, note: str = "") -> None:
    with con:
        con.execute(
            "INSERT INTO round_log (round, world_blob, config_hash, processed_at, note) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT (round) DO UPDATE SET world_blob = excluded.world_blob, "
            "config_hash = excluded.config_hash, processed_at = excluded.processed_at",
            (round_, pickle.dumps(world), config_hash, _now(), note))


def load_world(con, round_: int | None = None):
    """The world after `round_`, or after the latest processed round."""
    if round_ is None:
        row = con.execute(
            "SELECT world_blob FROM round_log ORDER BY round DESC LIMIT 1").fetchone()
    else:
        row = con.execute("SELECT world_blob FROM round_log WHERE round = ?",
                          (round_,)).fetchone()
    return pickle.loads(row["world_blob"]) if row else None


def rollback(con, to_round: int, actor: str = "admin") -> None:
    """Discard rounds after `to_round`. Submissions are kept, so a round can be
    re-run with the same decisions after fixing a parameter."""
    with con:
        con.execute("DELETE FROM round_log WHERE round > ?", (to_round,))
        con.execute("UPDATE game SET round = ? WHERE id = 1", (to_round,))
        log(con, actor, "round.rollback", f"to r{to_round}")


# --- Audit -------------------------------------------------------------------------

def log(con, actor: str, action: str, detail: str = "") -> None:
    con.execute("INSERT INTO audit (at, actor, action, detail) VALUES (?, ?, ?, ?)",
                (_now(), actor, action, detail))


def audit(con, limit: int = 50) -> list[sqlite3.Row]:
    return con.execute("SELECT * FROM audit ORDER BY id DESC LIMIT ?",
                       (limit,)).fetchall()
