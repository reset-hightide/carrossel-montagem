#!/usr/bin/env python3
"""Renderiza um preview PNG aproximado de cada slide do spec (o mesmo JSON do build_pptx.py),
para revisar layout/overflow sem LibreOffice. Também gera um contact sheet.

Uso: ~/.venvs/post/bin/python preview.py spec.json pasta_saida/
Fontes: procura TTF em ~/.local/share/fonts por nome (ex.: "Poppins Black" -> Poppins-Black.ttf).
"""
import json, sys, os, glob
from PIL import Image, ImageDraw, ImageFont, ImageOps

FONT_DIRS = [os.path.expanduser('~/.local/share/fonts'), '/usr/share/fonts']
_cache = {}

def font_file(name, bold=False, italic=False):
    key = (name, bold, italic)
    if key in _cache: return _cache[key]
    base = name.replace(' ', '')
    cands = []
    if italic:  # ex.: "Playfair Display" italic -> PlayfairDisplay-Italic / -BoldItalic; "Poppins Black" -> Poppins-BlackItalic
        parts = name.split(); fam = parts[0] if len(parts) > 1 and parts[-1] in ('Black', 'ExtraBold', 'Bold', 'SemiBold', 'Medium', 'Light') else base
        w = parts[-1] if fam != base else ('Bold' if bold else '')
        if fam != base: fam = ''.join(parts[:-1])
        cands += [f'{fam}-{w}Italic', f'{base}-Italic']
    cands += [base + ('-Bold' if bold and '-' not in base else ''), base, name.split()[0] + '-' + ''.join(name.split()[1:]), name.split()[0] + '-Regular', name.split()[0]]
    for d in FONT_DIRS:
        for c in cands:
            for ext in ('ttf', 'otf'):
                g = glob.glob(f'{d}/**/{c}.{ext}', recursive=True)
                if g: _cache[key] = g[0]; return g[0]
    # fallback: fontconfig (acha "DM Serif Text" -> DMSerifText-Regular.ttf, fontes variáveis etc.)
    import subprocess
    st = ('Bold ' if bold else '') + ('Italic' if italic else '')
    r = subprocess.run(['fc-match', '-f', '%{family}|%{file}', name + (':style=' + st.strip() if st.strip() else '')], capture_output=True, text=True).stdout
    fam, _, f = r.partition('|')
    if f and name.split()[0].lower() in fam.lower():
        _cache[key] = f; return f
    _cache[key] = None; return None

def load_font(ff, size, bold=False):
    """carrega a fonte e, se for variável (ex.: LibreFranklin[wght]), aplica peso 700/400 como o Canva."""
    fnt = ImageFont.truetype(ff, size)
    try:
        axes = fnt.get_variation_axes()
        if axes: fnt.set_variation_by_axes([700 if bold else 400] + [a['default'] for a in axes[1:]])
    except Exception:
        pass
    return fnt

def hexc(h, a=1.0):
    h = h.lstrip('#'); r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r, g, b, int(255 * (a if a is not None else 1)))

def wrap(draw, words, fnt, maxw):
    lines, cur = [], ''
    for w in words.split(' '):
        t = (cur + ' ' + w).strip()
        if draw.textlength(t, font=fnt) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def expand_destaques(els, fonts):
    """Mesma lógica do build_pptx.add_destaque: texto de 1 linha + traço/bloco medido com a fonte real."""
    import importlib.util
    sp = importlib.util.spec_from_file_location('bp', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_pptx.py'))
    bp = importlib.util.module_from_spec(sp); sp.loader.exec_module(bp)
    out = []
    for e in els:
        if e.get('t') == 'text' and (e.get('sub') or e.get('bloco')):
            tw = bp.text_width(e, fonts)
            x0 = e['x'] + (e['w'] - tw if e.get('align') == 'r' else (e['w'] - tw) / 2 if e.get('align') == 'c' else 0)
            if e.get('bloco'):
                b = e['bloco']; px, py = b.get('padx', 12), b.get('pady', 4)
                out.append({'t': 'rect', 'x': x0 - px, 'y': e['y'] - py, 'w': tw + 2 * px, 'h': e['h'] + 2 * py, 'fill': b['color']})
            out.append(dict(e, x=x0, w=tw * 1.04 + 4, align='l'))
            if e.get('sub'):
                u = e['sub']; out.append({'t': 'rect', 'x': x0, 'y': e['y'] + e['h'] + u.get('dy', 2), 'w': tw, 'h': u.get('h', 8), 'fill': u['color']})
        else:
            out.append(e)
    return out

def render(spec, outdir):
    os.makedirs(outdir, exist_ok=True)
    W, H = spec.get('w', 1080), spec.get('h', 1350); fonts = spec.get('fonts', {})
    thumbs = []; warns = []
    for i, s in enumerate(spec['slides'], 1):
        im = Image.new('RGBA', (W, H), hexc(s.get('bg', '#000000')))
        for e in expand_destaques(s.get('els', []), fonts):
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            if e['t'] == 'img':
                src = Image.open(e['src']).convert('RGBA'); w, h = int(e['w']), int(e['h'])
                if e.get('fit', 'cover') == 'cover':
                    src = ImageOps.fit(src, (w, h), centering=tuple(e.get('focus', [0.5, 0.5])))
                    pos = (int(e['x']), int(e['y']))
                elif e['fit'] == 'contain':
                    src.thumbnail((w, h)); pos = (int(e['x'] + (w - src.width) / 2), int(e['y'] + (h - src.height) / 2))
                else:
                    src = src.resize((w, h)); pos = (int(e['x']), int(e['y']))
                if e.get('rot'): src = src.rotate(-e['rot'], expand=True)
                lay.paste(src, pos, src)
            elif e['t'] == 'rect':
                box = [e['x'], e['y'], e['x'] + e['w'], e['y'] + e['h']]
                fill = hexc(e['fill'], e.get('alpha')) if e.get('fill') else None
                line = hexc(e['line']) if e.get('line') else None
                if e.get('shape') == 'oval': d.ellipse(box, fill=fill, outline=line, width=e.get('lw', 3))
                else: d.rounded_rectangle(box, radius=e.get('radius', 0), fill=fill, outline=line, width=e.get('lw', 3))
                if e.get('rot'):
                    lay = lay.rotate(-e['rot'], center=(e['x'] + e['w'] / 2, e['y'] + e['h'] / 2))
            elif e['t'] == 'line':
                d.line([e['x1'], e['y1'], e['x2'], e['y2']], fill=hexc(e.get('color', '#FFFFFF')), width=e.get('wpx', 3))
            else:
                pad = e.get('pad', 0); x0 = e['x'] + pad; maxw = e['w'] - 2 * pad
                paras = [[]]
                for r in e['runs']:
                    if r.get('br') and paras[-1]: paras.append([])
                    paras[-1].append(r)
                lines = []  # (texto, fonte, cor, altura)
                for para in paras:
                    for r in para:
                        size = r.get('size', 32); fname = fonts.get(r.get('font', 'body'), r.get('font', 'body'))
                        ff = font_file(fname, r.get('bold'), r.get('italic'))
                        fnt = load_font(ff, size, r.get('bold')) if ff else ImageFont.load_default(size)
                        txt = r['txt'].upper() if e.get('caps') else r['txt']
                        for ln in txt.split('\n'):
                            for wl in wrap(d, ln, fnt, maxw):
                                asc, desc = fnt.getmetrics()  # entrelinha natural da fonte (como PowerPoint/Canva) x lh
                                sp = r.get('spacing', e.get('spacing')) or 0
                                lines.append((wl, fnt, r.get('color', '#FFFFFF'), (asc + desc) * e.get('lh', 1.0), sp))
                total = sum(l[3] for l in lines)
                y = e['y'] + pad
                if e.get('valign') == 'm': y = e['y'] + (e['h'] - total) / 2
                if e.get('valign') == 'b': y = e['y'] + e['h'] - pad - total
                if total > e['h'] + 2: warns.append(f'slide {i}: texto "{lines[0][0][:25]}" estoura a caixa ({int(total)}>{e["h"]})')
                for txt, fnt, col, lh, sp in lines:
                    tw = d.textlength(txt, font=fnt) + sp * max(0, len(txt) - 1)
                    x = x0 if e.get('align', 'l') == 'l' else (x0 + (maxw - tw) / 2 if e['align'] == 'c' else x0 + maxw - tw)
                    if tw > maxw + 2: warns.append(f'slide {i}: palavra larga demais "{txt[:25]}"')
                    if sp:
                        cx = x
                        for ch in txt: d.text((cx, y), ch, font=fnt, fill=hexc(col)); cx += d.textlength(ch, font=fnt) + sp
                    else: d.text((x, y), txt, font=fnt, fill=hexc(col))
                    y += lh
                if e.get('rot'): lay = lay.rotate(-e['rot'], center=(e['x'] + e['w'] / 2, e['y'] + e['h'] / 2))
            im = Image.alpha_composite(im, lay)
        p = os.path.join(outdir, f'slide_{i:02d}.png'); im.convert('RGB').save(p); thumbs.append(im.convert('RGB'))
    # contact sheet 5 colunas
    tw, th = 270, int(270 * H / W); cols = 5; rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * tw + (cols + 1) * 10, rows * th + (rows + 1) * 10), 'white')
    for k, t in enumerate(thumbs):
        t = t.resize((tw, th)); sheet.paste(t, (10 + (k % cols) * (tw + 10), 10 + (k // cols) * (th + 10)))
    sheet.save(os.path.join(outdir, 'contact_sheet.jpg'), quality=88)
    print('\n'.join(warns) or 'sem avisos de overflow'); print('ok', outdir)

if __name__ == '__main__':
    render(json.load(open(sys.argv[1])), sys.argv[2])
