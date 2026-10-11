"""Stock is bought at the cost the P&L charges when it sells (cogs_scale)."""
import pickle
import sys
sys.path.insert(0, "src")

import pytest

from ecomsim import bootstrap, params as P, state
from ecomsim.engine import run_round
from ecomsim.modules.m03_supply import landed_index, purchase_scale
from ecomsim.web import db, service

PARAMS = P.load({"n_teams": 2, "events_enabled": 0})


def _bought(scaled: bool):
    world = bootstrap.new_world(PARAMS, run_id="po")
    world.scaled_purchases = scaled
    tid = next(iter(world.teams))
    run_round(world, PARAMS, {tid: {"7.1": 5000.0}})
    team = world.teams[tid]
    (po,) = [p for p in team.open_pos if p["placed"] == 1]
    return world, team, po


def test_an_order_costs_what_its_units_will_charge_as_cost_of_goods():
    world, team, po = _bought(True)
    b = next(s for s in PARAMS.suppliers if s["code"] == "B")
    landed = sum(u * float(PARAMS.sku(c)["unit_cost"]) * float(b["cost_index"])
                 * landed_index(team, c) * PARAMS["cogs_scale"]
                 for c, u in po["units"].items())
    assert po["cost"] == pytest.approx(landed)
    # ...which is what the stock table values those units at
    lines = {s["code"]: s for s in team.history[-1]["stock"]}
    assert po["cost"] == pytest.approx(
        sum(u * lines[c]["unit_cost"] for c, u in po["units"].items()))


def test_a_game_already_trading_keeps_the_cost_it_started_with():
    _, _, new = _bought(True)
    _, _, old = _bought(False)
    assert new["units"] == pytest.approx(old["units"])
    assert new["cost"] == pytest.approx(old["cost"] * PARAMS["cogs_scale"])


def test_a_world_saved_before_the_switch_reads_off():
    world = bootstrap.new_world(PARAMS, run_id="old")
    assert world.scaled_purchases is True
    del world.__dict__["scaled_purchases"]          # as a world pickled before it
    old = pickle.loads(pickle.dumps(world))
    assert purchase_scale(old, PARAMS) == 1.0
    assert state.WorldState.scaled_purchases is False


def test_the_switch_per_game(tmp_path):
    db.init(tmp_path / "new.db", "New", 2)
    assert db.scaled_purchases(db.connect(tmp_path / "new.db")) is True
    import sqlite3
    path = tmp_path / "old.db"
    con = sqlite3.connect(path)
    con.executescript(db.SCHEMA.split("CREATE TABLE IF NOT EXISTS account")[0])
    con.execute("INSERT INTO game (id, name, round, created_at) VALUES (1, 'old', 2, 'now')")
    con.commit()
    con.close()
    con = db.connect(path)
    with con:
        db.migrate(con)
    assert db.scaled_purchases(con) is False
    db.set_game(con, round=4)
    db.new_game(con, path, "Next", 2, 12, "founding", keep_overrides=False)
    assert db.scaled_purchases(con) is True


@pytest.mark.parametrize("on", [True, False])
def test_process_round_runs_on_the_games_switch(tmp_path, on):
    path = tmp_path / "g.db"
    db.init(path, "G", 2, start_mode="going_concern")
    con = db.connect(path)
    db.set_game(con, scaled_purchases=int(on), open_round=1)
    db.submit(con, 1, "team_01", {"7.1": 5000.0}, "t")
    service.process_round(con)
    world = db.load_world(con)
    assert world.scaled_purchases is on
    (po,) = [p for p in world.teams["team_01"].open_pos if p["placed"] == 1]
    _, _, ref = _bought(on)
    assert po["cost"] / sum(po["units"].values()) == pytest.approx(
        ref["cost"] / sum(ref["units"].values()), rel=0.02)
