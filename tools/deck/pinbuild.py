"""Give flow content click-by-click builds without moving anything.

Each target is measured in Chromium, replaced in place by an invisible spacer
of the same size, and re-added as a pinned direct child of the section at the
same box, with a fade build. Tables are split so each row fades on its own.
"""
import sys, json, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fit import Page, SHELL

JS = r"""(spec) => {
  const sec = document.querySelector('section');
  const S = sec.getBoundingClientRect();
  const foot = [...sec.children].find(e => e.tagName === 'ASIDE');
  const addPinned = (html) => { const t = document.createElement('template');
      t.innerHTML = html.trim(); const el = t.content.firstChild;
      sec.insertBefore(el, foot || null); return el; };
  const box = (el) => { const r = el.getBoundingClientRect();
      return {l: Math.round(r.left - S.left), t: Math.round(r.top - S.top),
              w: Math.round(r.width), h: Math.round(r.height)}; };
  const spacer = (el) => { const b = box(el); const d = document.createElement('div');
      d.setAttribute('style', `width:${b.w}px; height:${b.h}px; flex:0 0 auto`);
      el.replaceWith(d); };
  let n = 0; const made = [];
  const pin = (el, build=true) => {
      const b = box(el); const c = el.cloneNode(true);
      const st = (c.getAttribute('style') || '').replace(/(^|;)\s*(flex|width|height)\s*:[^;]*/g, '');
      c.setAttribute('style', `position:absolute; left:${b.l}px; top:${b.t}px; width:${b.w}px; height:${b.h}px; ${st.replace(/^;\s*/, '')}`);
      if (build) c.setAttribute('data-build-in', `fade ${++n}`);
      made.push([c, el]); };
  const pinTable = (tbl) => {
      // Rows become pinned flex rows of <p> cells: the viewer normalises real
      // tables (its own hairlines, no per-cell fonts), so a row-per-table
      // would not render as measured. Rows are 2.1 x the font size, as the
      // viewer lays table rows out.
      const T = box(tbl); const tstyle = tbl.getAttribute('style') || '';
      const fs = parseFloat((tstyle.match(/font-size:\s*([\d.]+)/) || [0, 28])[1]);
      const pad = 20, rh = Math.round(fs * 2.1);
      const rows = [...tbl.querySelectorAll('tr')];
      const inner = T.w - 2 * pad;
      const widths = [...rows[0].children].map(c => {
          const m = (c.getAttribute('style') || '').match(/width:\s*([\d.]+)%/);
          return m ? inner * parseFloat(m[1]) / 100 : inner / rows[0].children.length; });
      const H = rows.length * rh + 2 * pad;
      made.push([null, `<div style="position:absolute; left:${T.l}px; top:${T.t}px; width:${T.w}px; height:${H}px; border:1px solid #e4e4e7; border-radius:16px"></div>`]);
      rows.forEach((tr, i) => {
        const cells = [...tr.children].map((td, j) => {
          let st = (td.getAttribute('style') || '').replace(/(^|;)\s*width\s*:[^;]*/g, '').replace(/^;\s*/, '');
          if (!/font-size/.test(st)) st = `font-size:${fs}px; ` + st;
          if (td.tagName === 'TH' && !/font-weight/.test(st)) st = 'font-weight:600; ' + st;
          const al = /text-align:\s*right/.test(st) ? 'justify-content:flex-end; ' : '';
          return `<div style="width:${Math.round(widths[j])}px; padding:0 12px; display:flex; align-items:center; ${al}"><p style="${st}">${td.innerHTML}</p></div>`;
        }).join('');
        const bg = (tr.getAttribute('style') || '').match(/background:[^;]*/);
        const line = i > 0 ? ' border-top:1px solid #e4e4e7;' : '';
        const html = `<div style="position:absolute; left:${T.l + pad}px; top:${T.t + pad + i * rh}px; width:${inner}px; height:${rh}px; display:flex; align-items:stretch; ${bg ? bg[0] + ';' : ''}${line}${/font-family/.test(tstyle) ? ' ' + tstyle.match(/font-family:[^;]*/)[0] + ';' : ''}">${cells}</div>`;
        made.push([null, html, i === 0 ? null : ++n]);
      });
      // keep the space the viewer would have given the table
      const d = document.createElement('div');
      d.setAttribute('style', `width:${T.w}px; height:${H}px; flex:0 0 auto`);
      tbl.replaceWith(d);
      window.__tableEnd = T.t + H;
  };
  // run the plan
  const pinnedBefore = [...sec.children].filter(e => e.hasAttribute('data-build-in'));
  for (const step of spec) {
    const els = [...sec.querySelectorAll(step.sel)];
    if (step.table) { els.forEach(pinTable); continue; }
    els.forEach(el => pin(el, !step.static));
  }
  // measure is done: now swap flow elements for spacers and add the pins
  for (const m of made) if (m[0]) spacer(m[1]);
  for (const m of made) {
    if (m[0]) { addPinned(m[0].outerHTML); continue; }
    const el = addPinned(m[1]); if (m[2]) el.setAttribute('data-build-in', `fade ${m[2]}`);
  }
  // existing builds go after the new ones, in their old order
  pinnedBefore.forEach(el => { const k = parseInt((el.getAttribute('data-build-in') || '').split(' ')[1] || '0');
      el.setAttribute('data-build-in', `fade ${n + k}`); });
  return JSON.stringify({html: sec.outerHTML, tableEnd: window.__tableEnd || null});
}"""

def run(path, spec):
    p = pathlib.Path(path)
    with Page() as pg:
        pg.pg.set_content(SHELL.replace("__S__", p.read_text()), wait_until="load")
        try: pg.pg.wait_for_function("document.fonts.status === 'loaded'", timeout=4000)
        except Exception: pass
        out = json.loads(pg.pg.evaluate(JS, spec))
    p.write_text(out["html"] + "\n")
    if out["tableEnd"]: print(p.stem, "table ends at", out["tableEnd"])

if __name__ == "__main__":
    run(sys.argv[1], json.loads(sys.argv[2]))
