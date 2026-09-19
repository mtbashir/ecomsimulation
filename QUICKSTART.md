# Quickstart

## See it without installing anything

The repository ships a finished twelve-round game. **No Python needed** - just
open the file.

| | |
|---|---|
| **Windows** (PowerShell) | `ii demo\round_12\console_r12.html` |
| **macOS** | `open demo/round_12/console_r12.html` |
| **Linux** | `xdg-open demo/round_12/console_r12.html` |

Or just double-click it in the file browser.

That console is what you read between rounds as the instructor. Beside it,
`report_<team>_r12.html` is what each team receives. Start with
`report_team_02_r12.html` - the discount-led team, which finished last.

## Run it yourself

Needs **Python 3.11 or newer**. Nothing else: no database, no server, no build
step.

### Check what you have

| | |
|---|---|
| **Windows** | `py --version` (and `python --version`) |
| **macOS / Linux** | `python3 --version` |

On Windows the command is **`py`** or **`python`** - `python3` is not a thing,
and typing it opens a Microsoft Store prompt. Install from
[python.org/downloads](https://www.python.org/downloads/) and tick **"Add
python.exe to PATH"** on the first screen. Avoid the Microsoft Store build: it
sandboxes file writes, and this writes files.

Below, **`py`** means `py` on Windows and `python3` on macOS/Linux.

### Play the demo

```
py demo.py --out demo
```

Six teams, twelve rounds, about ten seconds. Then open
`demo/round_12/console_r12.html` as above.

### Run a real cohort

```
py run.py new --teams 8 --out game        # create the game
py run.py template --game game            # blank decisions file
#   send game/decisions_r1.csv to the teams
py run.py round --game game               # process the round
```

Then open `game/round_1/console_r1.html` for your view, and send each team its
own `report_<team>_r1.html`. Repeat `template` / `round` for each round.
`results.csv` accumulates every team's every round for your own analysis.

The decisions file is long-format - `team_id,decision,value` - so a Google Form
export drops straight in. A blank value means "use the default", and a team
that submits nothing keeps its previous round's decisions.

### Check it is behaving

```
py -m pip install -e ".[dev]"     # once, for the test suite
py -m pytest -q                   # 96 tests, about a second
py calibrate.py                   # baseline holds? ~2 minutes
py validate.py --games 160        # balanced? ~4 minutes
```

Run `validate.py` after changing anything in `params/`. It reports which
invariant broke and what to check first.

## Changing the economics

Everything lives in `params/parameters.csv`. Nothing is hardcoded in the
engine. Each row carries a default plus green and hard bands. Set a value
outside its hard band and the run is refused with the reason; inside the amber
range it runs but warns and marks the configuration unvalidated.

## Where to look

| | |
|---|---|
| What it simulates | `docs/00-game-world.md`, `docs/01-decision-list.md` |
| How a round is computed | `docs/07-engine-chain.md` |
| How teams are scored | `docs/08-scoring.md` |
| What the instructor can change | `docs/04-configurability.md` |
| Why each number is what it is | `docs/13-calibration-log.md` |
