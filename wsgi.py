"""WSGI entry point for a production server.

    gunicorn wsgi:app --workers 1 --threads 8 --timeout 120

One worker, several threads: the game state is a SQLite file, and a single
writer avoids lock contention entirely. Eight threads is far more concurrency
than a class of ten needs.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ecomsim.web.app import create_app  # noqa: E402

app = create_app()
