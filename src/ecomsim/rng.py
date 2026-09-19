"""Deterministic, purpose-keyed randomness.

Invariant I8: the same (state, decisions, config, seed) must produce identical
output, always and on every platform. Every draw is keyed on its purpose, so
adding a new random draw somewhere in the engine cannot shift the sequence seen
elsewhere.

The research-report key deliberately excludes any purchase counter: re-buying a
study in the same round must return the identical number, or teams average out
the noise and the uncertainty lesson is lost (docs/02, implementation rule 1).
"""
from __future__ import annotations

import hashlib
import math
import struct


def _uniform(*key: object) -> float:
    """A uniform draw in [0, 1) determined entirely by the key."""
    blob = "|".join(str(k) for k in key).encode("utf-8")
    digest = hashlib.sha256(blob).digest()
    (raw,) = struct.unpack(">Q", digest[:8])
    return raw / 2**64


def uniform(run_id: str, round_: int, team: str, purpose: str, *extra: object) -> float:
    return _uniform(run_id, round_, team, purpose, *extra)


def normal(run_id: str, round_: int, team: str, purpose: str,
           mu: float = 0.0, sigma: float = 1.0, *extra: object) -> float:
    """Box-Muller, using two independently keyed uniforms."""
    u1 = max(_uniform(run_id, round_, team, purpose, "n1", *extra), 1e-12)
    u2 = _uniform(run_id, round_, team, purpose, "n2", *extra)
    z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
    return mu + sigma * z


def chance(p: float, run_id: str, round_: int, team: str,
           purpose: str, *extra: object) -> bool:
    return _uniform(run_id, round_, team, purpose, *extra) < p
