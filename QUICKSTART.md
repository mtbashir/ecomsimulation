# Quickstart

## See it without installing anything

Open `demo/round_12/console_r12.html` in a browser. That is a finished
twelve-round game between six scripted teams, and it is what you would read
between rounds as the instructor. Each team's own report is beside it as
`report_<team>_r12.html`.

## Run it yourself

Needs **Python 3.11 or newer**. Nothing else - no database, no server, no
build step.

```bash
git clone https://github.com/mtbashir/ecomsimulation
cd ecomsimulation
git checkout claude/beautiful-hypatia-d7shuu

python3 --version          # 3.11+
pip install -e ".[dev]"    # only needed to run the test suite
```

### Play the demo

```bash
python3 demo.py --out demo
open demo/round_12/console_r12.html      # macOS; use `start` on Windows
```

Six teams, twelve rounds, roughly ten seconds.

### Run a real cohort

```bash
python3 run.py new --teams 8 --out game        # create the game
python3 run.py template --game game            # blank decisions file
#   send game/decisions_r1.csv to the teams (or export a Google Form to it)
python3 run.py round --game game               # process the round
open game/round_1/console_r1.html              # your view
#   send each team its own report_<team>_r1.html
```

Repeat `template` / `round` for each round. `results.csv` accumulates every
team's every round for your own analysis.

The decisions file is long-format - `team_id,decision,value` - so a Google Form
export drops straight in. A blank value means "use the default", and a team
that submits nothing keeps its previous round's decisions.

### Check it is behaving

```bash
pytest -q                          # 96 tests, about a second
python3 calibrate.py               # baseline holds? ~2 minutes
python3 validate.py --games 160    # balanced? ~4 minutes, 11 of 12 invariants
```

`validate.py` is the one to run after changing any parameter in `params/`.
It reports which invariant broke and what to check first.

## Changing the economics

Everything lives in `params/parameters.csv`. Nothing is hardcoded in the
engine. Each row carries a default plus green and hard bands:

```bash
python3 run.py new --teams 8 --out game     # uses defaults
```

Set a parameter outside its hard band and the run is refused with the reason.
Inside the amber range it runs but warns, and marks the configuration
unvalidated - rerun `validate.py` before putting it in front of students.

## Where to look

| | |
|---|---|
| What it simulates | `docs/00-game-world.md`, `docs/01-decision-list.md` |
| How a round is computed | `docs/07-engine-chain.md` |
| How teams are scored | `docs/08-scoring.md` |
| Every decision the instructor can change | `docs/04-configurability.md` |
| Why each number is what it is | `docs/13-calibration-log.md` |
