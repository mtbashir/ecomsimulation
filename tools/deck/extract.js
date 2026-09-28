() => {
  const sec = document.querySelector('section');
  const S = sec.getBoundingClientRect();
  const rgb = (c) => { const m = c.match(/rgba?\(([^)]+)\)/); if (!m) return null;
    const p = m[1].split(',').map(x => parseFloat(x)); if (p.length > 3 && p[3] === 0) return null;
    return p.slice(0, 3).map(v => Math.round(v).toString(16).padStart(2, '0')).join('').toUpperCase(); };
  const R = (el) => { const r = el.getBoundingClientRect();
    return {x: r.left - S.left, y: r.top - S.top, w: r.width, h: r.height}; };
  const topOf = (el) => { while (el.parentElement && el.parentElement !== sec) el = el.parentElement; return el; };
  const buildOf = (el) => { const t = topOf(el); const b = t.getAttribute('data-build-in');
    return b ? parseInt(b.split(' ')[1] || '1') : 0; };
  const pinned = (el) => getComputedStyle(topOf(el)).position === 'absolute';
  const items = []; let order = 0;
  const TEXT = new Set(['P', 'H1', 'H2', 'H3']);
  const walk = (el) => {
    if (el.tagName === 'ASIDE') return;
    const cs = getComputedStyle(el); const r = R(el);
    const base = {build: buildOf(el), pinned: pinned(el), order: order++};
    if (el.tagName === 'IMG') { items.push({...base, kind: 'img', src: el.getAttribute('src'), ...r}); return; }
    const bg = rgb(cs.backgroundColor);
    const sides = ['Top', 'Right', 'Bottom', 'Left'].map(s => ({w: parseFloat(cs['border' + s + 'Width']) || 0,
      c: rgb(cs['border' + s + 'Color'])}));
    if (bg || sides.some(s => s.w > 0 && s.c)) {
      items.push({...base, kind: 'box', ...r, fill: bg, sides: sides,
                  radius: parseFloat(cs.borderTopLeftRadius) || 0});
    }
    if (TEXT.has(el.tagName)) {
      const runs = [];
      const push = (node, st) => {
        if (node.nodeType === 3) {
          let t = node.textContent.replace(/\s+/g, ' ');
          if (st.textTransform === 'uppercase') t = t.toUpperCase();
          if (t) runs.push({t, color: rgb(st.color), size: parseFloat(st.fontSize),
            bold: parseInt(st.fontWeight) >= 600, mono: /Courier|Mono/i.test(st.fontFamily),
            ls: parseFloat(st.letterSpacing) || 0});
        } else if (node.nodeType === 1) {
          if (node.tagName === 'BR') { runs.push({br: true}); return; }
          const s2 = getComputedStyle(node); node.childNodes.forEach(c => push(c, s2));
        }
      };
      el.childNodes.forEach(c => push(c, cs));
      // trim the ends
      while (runs.length && !runs[0].br && !runs[0].t.trim()) runs.shift();
      if (runs.length && !runs[0].br) runs[0].t = runs[0].t.replace(/^\s+/, '');
      if (runs.length && !runs[runs.length - 1].br) runs[runs.length - 1].t = runs[runs.length - 1].t.replace(/\s+$/, '');
      const pad = ['Top', 'Right', 'Bottom', 'Left'].map(s => parseFloat(cs['padding' + s]) || 0);
      const bw = ['Top', 'Right', 'Bottom', 'Left'].map(s => parseFloat(cs['border' + s + 'Width']) || 0);
      let lh = parseFloat(cs.lineHeight); if (!lh) lh = parseFloat(cs.fontSize) * 1.15;
      // how many lines the browser drew
      const range = document.createRange(); range.selectNodeContents(el);
      const tops = new Set([...range.getClientRects()].map(q => Math.round(q.top)));
      const parent = el.parentElement ? getComputedStyle(el.parentElement) : null;
      let align = cs.textAlign;
      if (parent && parent.display === 'flex' && parent.flexDirection !== 'column') {
        if (parent.justifyContent === 'flex-end') align = 'right';
        else if (parent.justifyContent === 'center') align = 'center';
      }
      if (align === 'start') align = 'left'; if (align === 'end') align = 'right';
      items.push({...base, kind: 'text', ...r, runs, lh, align, lines: tops.size,
                  pad: pad.map((p, i) => p + bw[i])});
      return;
    }
    [...el.children].forEach(walk);
  };
  [...sec.children].forEach(walk);
  items.sort((a, b) => (a.pinned - b.pinned) || (a.order - b.order));
  const notes = (sec.querySelector('aside') || {}).textContent || '';
  return {bg: rgb(getComputedStyle(sec).backgroundColor), items, notes: notes.trim(),
          transition: sec.getAttribute('data-transition') || ''};
}
