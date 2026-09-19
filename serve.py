#!/usr/bin/env python3
"""Run the web app.

    py serve.py init --teams 8 --name "E-Commerce in Practice"   # once
    py serve.py                                                   # start it

Prints the team passwords once, at init. They are stored hashed and cannot be
read back afterwards - print that page or write them down.
"""
from __future__ import annotations

import argparse
import secrets
import socket
import sys
from pathlib import Path

sys.path.insert(0, "src")

from ecomsim.web import db  # noqa: E402
from ecomsim.web.app import create_app  # noqa: E402


def local_ip() -> str:
    """Best guess at the address teams on the same wifi should use."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def cmd_init(args) -> int:
    path = Path(args.db)
    if path.exists() and not args.force:
        print(f"{path} already exists. Use --force to start over "
              f"(this deletes the game).")
        return 1
    if path.exists():
        path.unlink()

    admin_pw = args.admin_password or f"{secrets.choice(db.WORDS)}-{secrets.randbelow(9000) + 1000}"
    passwords = db.init(path, args.name, args.teams, preset=args.preset,
                        rounds=args.rounds, admin_password=admin_pw)

    print(f"\nCreated {path} - {args.teams} teams, {args.rounds} rounds, "
          f"preset {args.preset}\n")
    print("  WRITE THESE DOWN. Passwords are hashed and cannot be recovered.\n")
    print(f"  {'account':<12}{'password':<26}who")
    print(f"  {'admin':<12}{admin_pw:<26}you")
    for tid, pw in passwords.items():
        print(f"  {tid:<12}{pw:<26}Team {int(tid.split('_')[1])}")
    print(f"\n  Any password can be changed later under Teams.\n")
    print(f"Next: py serve.py")
    return 0


def cmd_serve(args) -> int:
    path = Path(args.db)
    if not path.exists():
        print(f"No game at {path}. Run: py serve.py init --teams 8")
        return 1
    app = create_app(path)
    ip = local_ip()
    print(f"\n  Instructor and teams both sign in at:\n")
    print(f"      http://{ip}:{args.port}        (teams, same wifi)")
    print(f"      http://127.0.0.1:{args.port}   (you, this machine)\n")
    print(f"  Database: {path.resolve()}")
    print(f"  Back it up by copying that file. Ctrl-C to stop.\n")
    app.run(host=args.host, port=args.port, debug=args.debug)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default="game.db")
    sub = ap.add_subparsers(dest="cmd")

    init = sub.add_parser("init", help="create a game and its accounts")
    init.add_argument("--teams", type=int, default=8)
    init.add_argument("--rounds", type=int, default=12)
    init.add_argument("--name", default="E-Commerce Simulation")
    init.add_argument("--preset", default="advanced",
                      choices=["foundation", "standard", "advanced", "expert"])
    init.add_argument("--admin-password")
    init.add_argument("--force", action="store_true")
    init.set_defaults(fn=cmd_init)

    serve = sub.add_parser("serve", help="start the server (default)")
    serve.add_argument("--host", default="0.0.0.0")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--debug", action="store_true")
    serve.set_defaults(fn=cmd_serve)

    args = ap.parse_args()
    if not getattr(args, "fn", None):
        args = ap.parse_args(["serve"] + (["--db", args.db] if args.db else []))
        args.host, args.port, args.debug = "0.0.0.0", 8000, False
        args.fn = cmd_serve
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
