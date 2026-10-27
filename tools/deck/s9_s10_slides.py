"""Sessions 9 and 10 in one deck: How Will You Deliver the Order? and How Do
You Know If Your Business Is Working? About 58 slides.

Run: python s9_s10_slides.py <deck folder> [logo url]
Session 9's slides come from s9_slides.py and Session 10's from s10_slides.py,
unchanged; their numbers from s9_tests.py and s10_tests.py.
"""
import pathlib, sys
HERE = pathlib.Path(__file__).parent

# Each generator builds its slides with its own footer and helpers; run them
# one after the other and keep what each built.
ns9 = {"__file__": str(HERE / "s9_slides.py"), "__name__": "s9"}
exec((HERE / "s9_slides.py").read_text().split("\nwrite(S, ORDER,")[0], ns9)
ns10 = {"__file__": str(HERE / "s10_slides.py"), "__name__": "s10"}
exec((HERE / "s10_slides.py").read_text(), ns10)

S = {**ns9["S"], **ns10["S"]}
ORDER = ns9["ORDER"] + ns10["ORDER"]
SECTIONS = {
    "open": {"description": "Session 9 · How will you deliver the order, and your last parcel", "start": "cover"},
    "stock": {"description": "Session 9 · Part 1 · Stock, cash and suppliers, with cases", "start": "part1"},
    "excess": {"description": "Session 9 · Stock that will not sell, and fulfilment, with cases", "start": "deadstock"},
    "lastmile": {"description": "Session 9 · Couriers, cash on delivery and refusals, and the operations plan", "start": "couriers"},
    "sim": {"description": "Session 9 · Part 2 · Operations in the simulation", "start": "part2"},
    **ns10["SECTIONS"]}
ns10["write"](S, ORDER, "Sessions 9 & 10 — Delivering the Order, and Knowing It Works", SECTIONS)
