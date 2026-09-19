# 14 — Deployment

Target: **`sim.consulyticsai.com`**, on Render, SQLite on a persistent disk.

## Why not Supabase

Supabase is Postgres, auth and storage for apps where the browser talks to the
database directly. **It cannot run the simulation engine** — that is Python, and
Supabase's functions are Deno. It would replace only the database, leaving a
separate Python host to find anyway: two services and two dashboards for ten
concurrent users a few times a term.

The one good reason to add it later is wanting cohort data in Postgres to query
with SQL or a BI tool. `results.csv` and the SQLite file already answer most of
that, and the migration stays open — see **Moving to Postgres** below.

## Deploy

The production stack — gunicorn, the health probe, first-boot creation, proxy
headers and secure cookies — is verified against the exact `startCommand` in
`render.yaml`. What follows is about five minutes of clicking.

1. **Click Deploy to Render** (the button in `README.md`), or go to
   **Render → New → Blueprint** and point it at this repo. Either way it reads
   `render.yaml`.
2. **Sign in or create a Render account.** A card is needed: a persistent disk
   requires the Starter plan, about **$7 a month**. The free plan has no disk,
   and without one the game is wiped on every restart.
3. **Set `ECOMSIM_ADMIN_PASSWORD`** when it prompts — it is the only value not
   in the blueprint, deliberately. Adjust `ECOMSIM_TEAMS` and `ECOMSIM_NAME`
   here too if the defaults (8 teams, "E-Commerce in Practice") are wrong;
   they are read **once**, on first boot.
4. **Apply.** The first build takes two or three minutes. Watch for the health
   check to go green.
5. **Open the URL** Render gives you (`<name>.onrender.com`) and sign in as
   `admin`.
6. **Go to Teams.** The generated team passwords are listed there **once**.
   Write them down, then click to clear them.

### If something goes wrong

| Symptom | Cause |
|---|---|
| Build fails on `pip install` | `PYTHON_VERSION` in the blueprint is pinned to 3.12.7; Render occasionally lags. Set it to a version Render lists |
| Health check never goes green | The disk is not mounted at `/var/data`, so `ECOMSIM_DB` points nowhere writable |
| Signed out after every deploy | `ECOMSIM_SECRET` is not set or not marked `generateValue` |
| Teams page shows no passwords | They were already collected and cleared. Set new ones on that same page |

The `plan: starter` line is not optional — a persistent disk requires a paid
instance, and without the disk the game database is wiped on every deploy.

### Your domain

In Render: **Settings → Custom Domains → Add `sim.consulyticsai.com`**. It shows
a CNAME target. Add that record at your DNS provider:

```
CNAME   sim   <name>.onrender.com
```

HTTPS is issued automatically within a few minutes. `ECOMSIM_BEHIND_PROXY=1` is
already set, so Flask trusts the proxy's headers and marks session cookies
secure.

A path such as `consulyticsai.com/sim` would need your main site to reverse-proxy
to this app; the subdomain avoids touching it at all.

## Anywhere else

`Dockerfile` runs the same image on Fly, Railway, a VPS or your laptop. The only
requirements are a **persistent volume mounted where `ECOMSIM_DB` points** and
the environment variables in `.env.example`.

```bash
docker build -t ecomsim .
docker run -p 8000:8000 -v ecomsim-data:/var/data \
  -e ECOMSIM_ADMIN_PASSWORD=... -e ECOMSIM_SECRET=... ecomsim
```

## What the settings do

| Variable | Why it matters |
|---|---|
| `ECOMSIM_DB` | Must be on the persistent disk. Anywhere else and the game vanishes on restart |
| `ECOMSIM_SECRET` | Stable across restarts. Without it every restart silently signs everyone out mid-class — a key is persisted beside the database as a fallback |
| `ECOMSIM_BEHIND_PROXY` | Trusts the host's forwarded headers and marks cookies secure |
| `ECOMSIM_ADMIN_PASSWORD` | First boot only. Change it in the app afterwards |
| `ECOMSIM_TEAMS` / `ROUNDS` / `PRESET` / `NAME` | Read once, at first boot |

## Running a class on it

| | |
|---|---|
| Concurrency | One gunicorn worker, eight threads. A class of ten is nowhere near it |
| Backup | Copy `game.db` from the disk, or roll back a round in the app |
| Health | `/healthz` returns 200 only if the database answers |
| **If it fails mid-class** | Download the decisions CSV from the console and run `py run.py round --decisions <file>` offline. That path is tested and kept working |

Roll back and re-run is safer than it sounds: rounds are replayed from stored
submissions, so fixing a parameter and re-running a round costs nothing.

## Moving to Postgres

Only worth it for direct SQL access to cohort data, or more than one instance.
The work is bounded: `src/ecomsim/web/db.py` is raw SQLite, so it needs a
placeholder change (`?` to `%s`), `BLOB` to `BYTEA`, and a connection pool.
Roughly half a day. Nothing above it changes — the service layer and the engine
never touch SQL.
