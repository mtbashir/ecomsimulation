"""Sessions 11 and 12 in one deck: How Can AI Help? and How Do You Grow?
About 52 slides.

Run: python s11_s12_slides.py <deck folder> [logo url]
Session 11's slides come from s11_slides.py and Session 12's from
s12_slides.py, unchanged; their numbers from s11_tests.py and s12_tests.py.
"""
import pathlib, sys
HERE = pathlib.Path(__file__).parent

# Each generator builds its slides with its own footer and helpers; run them
# one after the other and keep what each built.
ns11 = {"__file__": str(HERE / "s11_slides.py"), "__name__": "s11"}
exec((HERE / "s11_slides.py").read_text(), ns11)
ns12 = {"__file__": str(HERE / "s12_slides.py"), "__name__": "s12"}
exec((HERE / "s12_slides.py").read_text(), ns12)

S = {**ns11["S"], **ns12["S"]}
ORDER = ns11["ORDER"] + ns12["ORDER"]
ns12["write"](S, ORDER, "Sessions 11 & 12 — How AI Helps, and How You Grow",
              {**ns11["SECTIONS"], **ns12["SECTIONS"]})
