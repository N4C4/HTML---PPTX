(function () {
  function firstFamily(ff) {
    if (!ff) return 'Arial';
    var m = ff.match(/^"[^"]+"|^[^,]+/);
    var f = (m ? m[0] : ff).trim().replace(/^"|"$/g, '');
    return f || 'Arial';
  }
  function parseColor(s) {
    if (!s) return null;
    var m = s.match(/rgba?\(([^)]+)\)/);
    if (!m) {
      if (/^#[0-9a-f]{3,8}$/i.test(s)) {
        var h = s.slice(1);
        if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
        return { r: parseInt(h.slice(0, 2), 16), g: parseInt(h.slice(2, 4), 16), b: parseInt(h.slice(4, 6), 16), a: 1 };
      }
      return null;
    }
    var p = m[1].split(',');
    var a = p.length > 3 ? parseFloat(p[3]) : 1;
    if (isNaN(a)) a = 1;
    return { r: parseFloat(p[0]), g: parseFloat(p[1]), b: parseFloat(p[2]), a: a };
  }
  function comp(c) {
    if (!c) return null;
    var a = c.a === undefined ? 1 : c.a;
    return [Math.round(c.r * a + 255 * (1 - a)), Math.round(c.g * a + 255 * (1 - a)), Math.round(c.b * a + 255 * (1 - a))];
  }
  function hex(c) {
    var v = comp(c);
    if (!v) return '#000000';
    return '#' + v.map(function (x) { return ('0' + x.toString(16)).slice(-2); }).join('');
  }
  function px(v) { var f = parseFloat(v); return isFinite(f) ? f : 0; }
  function ownText(el) {
    var t = '';
    for (var n = el.firstChild; n; n = n.nextSibling) {
      if (n.nodeType === 3) t += n.data;
      else if (n.nodeType === 1 && n.tagName.toUpperCase() === 'BR') t += '\n';
    }
    return t.replace(/\u00a0/g, ' ').replace(/[ \t]+/g, ' ').replace(/\n[ ]+/g, '\n').trim();
  }
  function fullText(el) {
    var t = (el.innerText || '').replace(/\u00a0/g, ' ');
    return t.split('\n').map(function (s) { return s.trim(); }).filter(function (s) { return s.length > 0; }).join('\n');
  }
  function isFilled(el) {
    var c = parseColor(getComputedStyle(el).backgroundColor);
    return !!c && c.a > 0.004;
  }
  function flowText(el) {
    var t = '';
    for (var n = el.firstChild; n; n = n.nextSibling) {
      if (n.nodeType === 3) t += n.data;
      else if (n.nodeType === 1) {
        var tg = n.tagName.toUpperCase();
        if (tg === 'BR') t += '\n';
        else if (tg === 'SCRIPT' || tg === 'STYLE' || tg === 'SVG') continue;
        else if (isFilled(n)) continue;
        else t += flowText(n);
      }
    }
    return t.replace(/\u00a0/g, ' ').replace(/[ \t]+/g, ' ').replace(/\n[ ]+/g, '\n').trim();
  }
  function isSkippable(tag) {
    return tag === 'HEAD' || tag === 'TITLE' || tag === 'META' || tag === 'LINK' || tag === 'STYLE' ||
      tag === 'SCRIPT' || tag === 'NOSCRIPT' || tag === 'BR';
  }
  var out = [];
  function visit(el, suppress) {
    var tag = el.tagName.toUpperCase();
    if (isSkippable(tag)) return;
    var cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden') return;
    var r = el.getBoundingClientRect();
    if (r.width < 0.5 || r.height < 0.5) return;
    var rec = {
      tag: tag, x: r.left, y: r.top, w: r.width, h: r.height,
      fill: null, sides: null, radius: 0, radiusMax: 0,
      text: null, align: 'left', font: 'Arial', size: 11, bold: false, italic: false,
      color: '#000000', lh: 0, svg: null, donut: null, ws: 'normal', ls: 0
    };
    var bg = parseColor(cs.backgroundColor);
    if (bg && bg.a > 0.004) rec.fill = comp(bg);
    var sides = { t: px(cs.borderTopWidth), r: px(cs.borderRightWidth), b: px(cs.borderBottomWidth), l: px(cs.borderLeftWidth) };
    var scol = { t: parseColor(cs.borderTopColor), r: parseColor(cs.borderRightColor), b: parseColor(cs.borderBottomColor), l: parseColor(cs.borderLeftColor) };
    var sst = { t: cs.borderTopStyle, r: cs.borderRightStyle, b: cs.borderBottomStyle, l: cs.borderLeftStyle };
    function sideData(k) {
      if (sides[k] < 0.5 || sst[k] === 'none' || !scol[k]) return null;
      return { w: sides[k], c: comp(scol[k]), d: (sst[k] === 'dashed' || sst[k] === 'dotted') ? sst[k] : null };
    }
    rec.sides = { t: sideData('t'), r: sideData('r'), b: sideData('b'), l: sideData('l') };
    rec.radius = Math.max(0, Math.min(px(cs.borderTopLeftRadius), px(cs.borderTopRightRadius), px(cs.borderBottomLeftRadius), px(cs.borderBottomRightRadius)));
    rec.radiusMax = Math.max(px(cs.borderTopLeftRadius), px(cs.borderTopRightRadius), px(cs.borderBottomLeftRadius), px(cs.borderBottomRightRadius));
    var own = ownText(el);
    var suppressKids = suppress;
    if (tag !== 'SVG' && tag !== 'PATH' && own && (!suppress || rec.fill)) {
      var kidBlock = false;
      for (var i = 0; i < el.children.length; i++) {
        var kd = getComputedStyle(el.children[i]).display;
        if (kd !== 'inline' && kd !== 'inline-block' && kd !== 'inline-flex' && kd !== 'inline-grid' && kd !== 'contents' && kd !== 'none') { kidBlock = true; break; }
      }
      if (!kidBlock) { rec.text = flowText(el); suppressKids = true; }
      else { rec.text = own; suppressKids = false; }
    }
    if (rec.text && cs.textTransform === 'uppercase') rec.text = rec.text.toUpperCase();
    rec.ws = cs.whiteSpace || 'normal';
    rec.ls = (cs.letterSpacing && cs.letterSpacing !== 'normal') ? px(cs.letterSpacing) : 0;
    rec.align = (cs.textAlign === 'center') ? 'center' : (cs.textAlign === 'right' || cs.textAlign === 'end') ? 'right' : (cs.textAlign === 'justify') ? 'justify' : 'left';
    rec.font = firstFamily(cs.fontFamily);
    rec.size = Math.max(4, Math.round(px(cs.fontSize) * 0.75 * 100) / 100);
    rec.bold = parseInt(cs.fontWeight, 10) >= 600 || cs.fontWeight === 'bold';
    rec.italic = cs.fontStyle === 'italic';
    rec.color = hex(parseColor(cs.color));
    var lh = cs.lineHeight;
    rec.lh = (lh && lh !== 'normal') ? px(lh) : 0;
    var bgi = cs.backgroundImage || '';
    if (bgi.indexOf('conic-gradient') >= 0) {
      var slices = [];
      var re = /(rgba?\([^)]+\)|#[0-9a-fA-F]{3,8})\s+([\d.]+)(?:%|deg)/g;
      var m2, toks = [];
      while ((m2 = re.exec(bgi))) toks.push({ c: comp(parseColor(m2[1])), v: parseFloat(m2[2]) });
      for (var ti = 0; ti + 1 < toks.length; ti += 2) {
        slices.push({ c: toks[ti].c, a: toks[ti].v, b: toks[ti + 1].v });
      }
      var af = getComputedStyle(el, '::after');
      var ac = (af.content || '').replace(/^["']|["']$/g, '');
      rec.donut = {
        slices: slices, content: ac,
        it: px(af.top), il: px(af.left), ir: px(af.right), ib: px(af.bottom),
        bw: px(af.borderTopWidth), bc: comp(parseColor(af.borderTopColor)),
        bg: comp(parseColor(af.backgroundColor)),
        fs: Math.max(4, px(af.fontSize) * 0.75), fw: parseInt(af.fontWeight, 10) >= 600,
        fc: hex(parseColor(af.color))
      };
      rec.fill = null;
      rec.sides = null;
    }
    if (tag === 'SVG') {
      var lines = [];
      for (var j = 0; j < el.children.length; j++) {
        var ch = el.children[j];
        if (ch.tagName.toUpperCase() !== 'LINE') continue;
        var stk = getComputedStyle(ch).stroke;
        if (!stk || stk === 'none') continue;
        lines.push({
          x1: parseFloat(ch.getAttribute('x1')), y1: parseFloat(ch.getAttribute('y1')),
          x2: parseFloat(ch.getAttribute('x2')), y2: parseFloat(ch.getAttribute('y2')),
          c: hex(parseColor(stk)), w: px(getComputedStyle(ch).strokeWidth) || 1
        });
      }
      rec.svg = { vb: el.getAttribute('viewBox') || '', lines: lines };
      rec.fill = null; rec.sides = null; rec.text = null;
      out.push(rec);
      return;
    }
    out.push(rec);
    for (var k = 0; k < el.children.length; k++) visit(el.children[k], suppressKids);
  }
  visit(document.documentElement, false);
  var bodyBg = parseColor(getComputedStyle(document.body).backgroundColor);
  var htmlBg = parseColor(getComputedStyle(document.documentElement).backgroundColor);
  var bg = (bodyBg && bodyBg.a > 0.004) ? comp(bodyBg) : (htmlBg && htmlBg.a > 0.004) ? comp(htmlBg) : [255, 255, 255];
  var json = JSON.stringify({ vw: window.innerWidth, vh: window.innerHeight, bg: bg, els: out });
  var b64 = btoa(unescape(encodeURIComponent(json)));
  document.documentElement.innerHTML = '<head><title>DUMP</title></head><body><pre id="d">' + b64 + '</pre></body>';
})();
