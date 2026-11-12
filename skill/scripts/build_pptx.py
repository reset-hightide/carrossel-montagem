#!/usr/bin/env python3
"""Gera um .pptx editável (1 slide = 1 página do carrossel) a partir de um spec JSON.

Uso: ~/.venvs/post/bin/python build_pptx.py spec.json saida.pptx

Unidade = pixel do post (1080x1350 por padrão). Cada elemento vira uma camada separada
no Canva depois do upload (Criar > Fazer upload > .pptx).

spec = {
  "w": 1080, "h": 1350,
  "fonts": {"title": "Poppins Black", "body": "Poppins"},   # nomes como o Canva conhece
  "slides": [
    {"bg": "#2E2925", "notes": "texto das notas",
     "els": [
       {"t": "img",  "src": "foto.jpg", "x":0,"y":0,"w":1080,"h":1350, "fit": "cover"|"contain"|"stretch", "name": "foto produto"},
       {"t": "rect", "x":..,"y":..,"w":..,"h":..,"fill":"#E8D2AC","alpha":1.0,"radius":0,"line":null, "rot":0},
       {"t": "text", "x":..,"y":..,"w":..,"h":.., "runs":[{"txt":"ELE PERDEU","size":96,"color":"#FFF","bold":true,"font":"title","hl":"#E8D2AC"}],
        "align":"l|c|r", "valign":"t|m|b", "lh": 0.9, "spacing": 0, "pad": 0, "caps": false, "rot": 0},
       {"t": "line", "x1":..,"y1":..,"x2":..,"y2":..,"color":"#fff","wpx":3}
     ]}
  ]
}
Texto: cada item de "runs" pode ter "br": true para quebrar parágrafo antes dele.
Destaque editorial (bloco colorido atrás da linha): use um "rect" atrás do "text" (mais editável no Canva
que highlight de run, que o Canva ignora).
"""
import json, sys, os
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from PIL import Image

PX = 9525  # EMU por pixel (96 dpi)

def rgb(h):
    h = h.lstrip('#')
    return RGBColor.from_string(h[:6].upper())

def set_alpha(fill_fmt, alpha):
    if alpha is None or alpha >= 1: return
    sf = fill_fmt._xPr.find(qn('a:solidFill'))
    clr = sf[0]
    a = clr.makeelement(qn('a:alpha'), {'val': str(int(alpha * 100000))})
    clr.append(a)

def add_img(sl, e):
    x, y, w, h = e['x'], e['y'], e['w'], e['h']
    fit = e.get('fit', 'cover')
    im = Image.open(e['src']); iw, ih = im.size
    if fit == 'contain':
        s = min(w / iw, h / ih); nw, nh = iw * s, ih * s
        pic = sl.shapes.add_picture(e['src'], Emu(int((x + (w - nw) / 2) * PX)), Emu(int((y + (h - nh) / 2) * PX)), Emu(int(nw * PX)), Emu(int(nh * PX)))
    else:
        pic = sl.shapes.add_picture(e['src'], Emu(int(x * PX)), Emu(int(y * PX)), Emu(int(w * PX)), Emu(int(h * PX)))
        if fit == 'cover':
            r_box, r_img = w / h, iw / ih
            fx, fy = e.get('focus', [0.5, 0.5])
            if r_img > r_box:   # imagem mais larga: corta laterais
                keep = r_box / r_img; c = (1 - keep)
                pic.crop_left = c * fx; pic.crop_right = c * (1 - fx)
            else:
                keep = r_img / r_box; c = (1 - keep)
                pic.crop_top = c * fy; pic.crop_bottom = c * (1 - fy)
    if e.get('rot'): pic.rotation = e['rot']
    pic.name = e.get('name', os.path.basename(e['src']))
    return pic

def add_rect(sl, e):
    shp = MSO_SHAPE.ROUNDED_RECTANGLE if e.get('radius') else MSO_SHAPE.RECTANGLE
    if e.get('shape') == 'oval': shp = MSO_SHAPE.OVAL
    s = sl.shapes.add_shape(shp, Emu(int(e['x'] * PX)), Emu(int(e['y'] * PX)), Emu(int(e['w'] * PX)), Emu(int(e['h'] * PX)))
    if e.get('radius'):
        s.adjustments[0] = min(0.5, e['radius'] / min(e['w'], e['h']))
    if e.get('fill'):
        s.fill.solid(); s.fill.fore_color.rgb = rgb(e['fill']); set_alpha(s.fill, e.get('alpha'))
    else:
        s.fill.background()
    if e.get('line'):
        s.line.color.rgb = rgb(e['line']); s.line.width = Emu(int(e.get('lw', 3) * PX))
    else:
        s.line.fill.background()
    s.shadow.inherit = False
    if e.get('rot'): s.rotation = e['rot']
    s.name = e.get('name', 'forma')
    return s

def add_line(sl, e):
    from pptx.enum.shapes import MSO_CONNECTOR
    c = sl.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Emu(int(e['x1'] * PX)), Emu(int(e['y1'] * PX)), Emu(int(e['x2'] * PX)), Emu(int(e['y2'] * PX)))
    c.line.color.rgb = rgb(e.get('color', '#FFFFFF')); c.line.width = Emu(int(e.get('wpx', 3) * PX))
    if e.get('dash'):
        from pptx.enum.dml import MSO_LINE
        c.line.dash_style = MSO_LINE.DASH
    return c

def add_text(sl, e, fonts):
    tb = sl.shapes.add_textbox(Emu(int(e['x'] * PX)), Emu(int(e['y'] * PX)), Emu(int(e['w'] * PX)), Emu(int(e['h'] * PX)))
    tf = tb.text_frame; tf.word_wrap = True
    pad = Emu(int(e.get('pad', 0) * PX))
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = pad
    tf.vertical_anchor = {'t': MSO_ANCHOR.TOP, 'm': MSO_ANCHOR.MIDDLE, 'b': MSO_ANCHOR.BOTTOM}[e.get('valign', 't')]
    al = {'l': PP_ALIGN.LEFT, 'c': PP_ALIGN.CENTER, 'r': PP_ALIGN.RIGHT}[e.get('align', 'l')]
    p = tf.paragraphs[0]; p.alignment = al
    if e.get('lh'): p.line_spacing = e['lh']
    first = True
    for r in e['runs']:
        if r.get('br') and not first:
            p = tf.add_paragraph(); p.alignment = al
            if e.get('lh'): p.line_spacing = e['lh']
            if r.get('space_before'): p.space_before = Pt(r['space_before'] * 0.75)
        first = False
        run = p.add_run(); run.text = r['txt'].upper() if e.get('caps') else r['txt']
        f = run.font
        f.size = Pt(r.get('size', 32) * 0.75)  # px -> pt
        f.bold = r.get('bold', False); f.italic = r.get('italic', False)
        fname = r.get('font', 'body'); f.name = fonts.get(fname, fname)
        f.color.rgb = rgb(r.get('color', '#FFFFFF'))
        sp = r.get('spacing', e.get('spacing'))
        if sp:
            run._r.get_or_add_rPr().set('spc', str(int(sp * 75)))  # px -> centésimos de pt
    if e.get('rot'): tb.rotation = e['rot']
    tb.name = e.get('name', (e['runs'][0]['txt'][:30] if e['runs'] else 'texto'))
    return tb

def build(spec, out):
    prs = Presentation()
    W, H = spec.get('w', 1080), spec.get('h', 1350)
    prs.slide_width = Emu(W * PX); prs.slide_height = Emu(H * PX)
    fonts = spec.get('fonts', {})
    blank = prs.slide_layouts[6]
    for s in spec['slides']:
        sl = prs.slides.add_slide(blank)
        if s.get('bg'):
            sl.background.fill.solid(); sl.background.fill.fore_color.rgb = rgb(s['bg'])
        for e in s.get('els', []):
            {'img': add_img, 'rect': add_rect, 'line': add_line}.get(e['t'], lambda a, b: add_text(a, b, fonts))(sl, e)
        if s.get('notes'):
            sl.notes_slide.notes_text_frame.text = s['notes']
    prs.save(out)
    print('ok', out, len(spec['slides']), 'slides')

if __name__ == '__main__':
    build(json.load(open(sys.argv[1])), sys.argv[2])
