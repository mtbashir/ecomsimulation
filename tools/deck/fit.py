"""Standardise the card rows on a slide and keep every box inside the canvas.

Heights come from Chromium, not from a guess: each card is measured with any
forced height removed, every card in a row is then pinned to the tallest of
them, and the rows are re-stacked under the flowing heading so that nothing
overlaps and nothing runs past the footer band.
"""
import re, sys, math, json, pathlib
from playwright.sync_api import sync_playwright

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
FLOOR, HEAD_GAP, GAP, GAP_MIN = 920, 40, 40, 20
SHELL = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap">
<style>html,body{margin:0;padding:0}
section{position:relative;width:1920px;height:1080px;box-sizing:border-box}
section *{box-sizing:border-box}
aside{display:none}h1,h2,h3,p,table{margin:0}
table{border-collapse:collapse;width:100%}</style></head><body>__S__</body></html>"""

JS = """() => {
  const sec = document.querySelector('section');
  const flow = [], pins = [];
  for (const el of sec.children) {
    if (el.tagName === 'ASIDE') continue;
    const r = el.getBoundingClientRect();
    const s = el.getAttribute('style') || '';
    const abs = /position:\\s*absolute/.test(s);
    if (abs && /(^|;)\\s*top:/.test(s) && /(^|;)\\s*width:/.test(s))
      pins.push({top: r.top, h: r.height, left: r.left});
    else if (!abs) flow.push({bottom: r.bottom, right: r.right});
  }
  return {flow, pins};
}"""

STYLE = re.compile(r'style="([^"]*)"')
BOX = re.compile(r'<(div|p|img|table|ul|ol)\b([^>]*?)>')

def decl(s):
    return dict((k.strip(), v.strip()) for k, v in
                (p.split(":", 1) for p in s.split(";") if ":" in p))

VOID = ("img", "br", "hr", "input", "meta", "link")

def boxes(src):
    """Top-level absolutely-placed cards, in document order.

    Each entry carries where its opening tag sits and where its whole block
    ends, so a card can be restyled or rescaled as a unit.
    """
    body = src[src.index(">", src.index("<section")) + 1:]
    off = len(src) - len(body)
    out, depth, open_at = [], 0, None
    for m in re.finditer(r'<(/?)([a-z][a-z0-9-]*)\b([^>]*?)(/?)>', body):
        closing, tag, attrs, self_close = m.groups()
        if closing:
            depth -= 1
            if depth == 0 and open_at is not None:
                out[-1] = out[-1] + (off + m.end(),)
                open_at = None
            continue
        if depth == 0:
            st = STYLE.search(attrs)
            if st:
                d = decl(st.group(1))
                if d.get("position") == "absolute" and "top" in d and "width" in d:
                    out.append((off + m.start(), off + m.end(), tag, attrs, d))
                    open_at = m.start()
                    if self_close or tag in VOID:
                        out[-1] = out[-1] + (off + m.end(),)
                        open_at = None
        if not self_close and tag not in VOID:
            depth += 1
    return [b for b in out if len(b) == 6]

def put(src, spots, newstyles):
    """Rewrite the style attribute of each card, back to front."""
    for (a, b, tag, attrs, _, _), d in reversed(list(zip(spots, newstyles))):
        keys = ["position", "left", "top", "width", "height"]
        order = [k for k in keys if k in d] + [k for k in d if k not in keys]
        s = "; ".join(f"{k}:{d[k]}" for k in order)
        src = src[:a] + "<" + tag + STYLE.sub('style="' + s.replace("\\", "\\\\") + '"', attrs) + ">" + src[b:]
    return src

def strip_heights(src, spots):
    out = []
    for _, _, _, _, d, _ in spots:
        e = dict(d); e.pop("height", None); out.append(e)
    return put(src, spots, out)

PAD_FLOOR, FONT_FLOOR = 26, 24

def rescale(src, spots, k):
    """Scale the presentation of every card — padding, type size, leading —
    without touching a word of the copy."""
    def one(m):
        prop, val = m.group(1), m.group(2)
        if prop == "padding":
            return "padding:" + " ".join(
                f"{max(PAD_FLOOR, round(float(re.match(chr(94)+chr(45)+'?[0-9.]+', v).group()) * k))}px"
                for v in val.split())
        if prop == "font-size":
            v = float(re.match(r'-?[\d.]+', val).group())
            floor = 34 if v >= 56 else FONT_FLOOR
            return f"font-size:{max(floor, round(v * k))}px"
        if prop == "gap":
            v = float(re.match(r'-?[\d.]+', val).group())
            return f"gap:{max(8, round(v * k))}px"
        return m.group(0)
    for b in reversed(spots):
        a, e = b[0], b[5]
        block = src[a:e]
        inner = block[block.index(">") + 1:]
        head = block[:block.index(">") + 1]
        head = re.sub(r'(padding|font-size|gap):\s*([^;"]+)', one, head)
        inner = re.sub(r'(padding|font-size|gap):\s*([^;"]+)', one, inner)
        src = src[:a] + head + inner + src[e:]
    return src

class Page:
    def __enter__(self):
        self.pw = sync_playwright().start()
        self.b = self.pw.chromium.launch(executable_path=CHROME)
        self.pg = self.b.new_page(viewport={"width": 1920, "height": 1080})
        return self
    def __exit__(self, *a):
        self.b.close(); self.pw.stop()
    def read(self, src):
        self.pg.set_content(SHELL.replace("__S__", src), wait_until="load")
        try: self.pg.wait_for_function("document.fonts.status === 'loaded'", timeout=4000)
        except Exception: pass
        return self.pg.evaluate(JS)

def plan(m, spots):
    """Row heights and tops for one measured slide."""
    flow_bottom = max([f["bottom"] for f in m["flow"]] or [128])
    rows, order = {}, []
    for (spot, meas) in zip(spots, m["pins"]):
        t = round(float(re.match(r'-?[\d.]+', spot[4]["top"]).group()))
        if t not in rows: rows[t] = []; order.append(t)
        rows[t].append(meas["h"])
    order.sort()
    heights = {t: int(math.ceil(max(rows[t]) / 2) * 2) for t in order}
    # A slide whose cards sit beside the flowing column, not under it, must not
    # have its cards shoved below the text they sit next to.
    beside = (bool(m["pins"]) and min(p["left"] for p in m["pins"]) >= 960
              and order[0] < flow_bottom - 40)
    for gap in range(GAP, GAP_MIN - 2, -4):
        y = order[0] if beside else max(order[0], flow_bottom + HEAD_GAP)
        tops, ok = {}, True
        for t in order:
            tops[t] = y; y += heights[t] + gap
        bottom = max(y - gap, flow_bottom if beside else 0)
        if bottom <= FLOOR: return heights, tops, bottom, gap
    # last resort: sit the first row straight under the heading
    gap = GAP_MIN
    y = order[0] if beside else flow_bottom + 24
    tops = {}
    for t in order:
        tops[t] = y; y += heights[t] + gap
    return heights, tops, y - gap, gap

def fit(page, path):
    base = path.read_text()
    spots = boxes(base)
    if not spots: return None
    for k in (1.0, 0.96, 0.92, 0.88, 0.84):
        src = base if k == 1.0 else rescale(base, boxes(base), k)
        spots = boxes(src)
        m = page.read(strip_heights(src, spots))
        if len(m["pins"]) != len(spots):
            return ("mismatch", len(spots), len(m["pins"]))
        heights, tops, bottom, gap = plan(m, spots)
        if bottom <= FLOOR or k == 0.84: break
    new = []
    for (_, _, tag, _, d, _) in spots:
        t = round(float(re.match(r'-?[\d.]+', d["top"]).group()))
        e = dict(d)
        e["top"] = f"{tops[t]:.0f}px"
        e["height"] = f"{heights[t]}px"
        if tag == "img": e.pop("height")
        new.append(e)
    path.write_text(put(src, spots, new))
    return bottom, gap, k

if __name__ == "__main__":
    with Page() as pg:
        for d in sys.argv[1:]:
            print(f"--- {pathlib.Path(d).parent.parent.name} ---")
            for f in sorted(pathlib.Path(d).glob("*.html")):
                r = fit(pg, f)
                if r is None: print(f"  {f.stem:<13} no cards"); continue
                if r[0] == "mismatch": print(f"  {f.stem:<13} MISMATCH {r[1]} vs {r[2]}"); continue
                bottom, gap, k = r
                flag = "   STILL OVER" if bottom > FLOOR else ""
                print(f"  {f.stem:<13} ends {bottom:>4.0f}  gap {gap}  scale {k:.2f}{flag}")
