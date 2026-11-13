#!/usr/bin/env python3
"""Elementos de colagem com SOMBRA SUAVE de verdade (sem corte seco) + verificador de bordas.

Regras que este script garante (lição de 13/11/2026: sombras "acabavam do zero" em cima/embaixo):
- A tela do PNG tem margem >= deslocamento + 3σ do desfoque + folga, então o alfa chega a 0 ANTES da borda.
- A sombra é gerada NO TAMANHO FINAL do elemento (nunca um sombra.png quadrado esticado: esticar
  achata o degradê num lado e corta no outro).
- Deslocamento sem wrap (nunca ImageChops.offset).

Uso:
  colagem.py sombra  saida.png LARGURA ALTURA [--blur 18] [--dx 0] [--dy 14] [--alpha 110] [--raio 0]
      -> PNG da sombra para ficar ATRÁS de uma foto/polaroid LARGURAxALTURA (px do post).
         Imprime o deslocamento (x,y) para posicionar: el.x = foto.x - margem, el.y = foto.y - margem.
  colagem.py cartao  saida.png LARGURA ALTURA --cor '#FBFAE9' [--seed 1] [--blur 14] [--dy 12]
      -> cartão/etiqueta de papel rasgado com sombra suave embutida.
  colagem.py checar  pasta_ou_png [...]
      -> lista PNGs cujo alfa NÃO é zero na borda (sombra/contorno cortado). Ignora full-bleed de
         propósito (nomes com grad_, rasgo_, fita_, logo, papel_, foto). Rode antes do build.
"""
import sys, os, glob, argparse, random
from PIL import Image, ImageDraw, ImageFilter

def margem(blur, dx, dy):
    return int(max(abs(dx), abs(dy)) + 3 * blur + 8)

def sombra(out, w, h, blur=18, dx=0, dy=14, alpha=110, raio=0, cor=(15, 25, 8)):
    m = margem(blur, dx, dy)
    W, H = w + 2 * m, h + 2 * m
    a = Image.new('L', (W, H), 0); d = ImageDraw.Draw(a)
    box = [m + dx, m + dy, m + dx + w, m + dy + h]
    (d.rounded_rectangle(box, raio, fill=alpha) if raio else d.rectangle(box, fill=alpha))
    a = a.filter(ImageFilter.GaussianBlur(blur))
    im = Image.new('RGBA', (W, H), cor + (0,)); im.putalpha(a); im.save(out)
    print(f'ok {out} {W}x{H}  posicione em (foto.x-{m}, foto.y-{m}) com w={W} h={H}, fit=stretch, MESMA rotação da foto')
    return m

def cartao(out, w, h, cor, seed=1, blur=14, dy=12, dx=6, sombra_alpha=110, irregular=5):
    m = margem(blur, dx, dy) + irregular
    W, H = w + 2 * m, h + 2 * m
    r = random.Random(seed); poly = []
    for x in range(0, w, 7): poly.append((m + x, m + r.uniform(-irregular, irregular)))
    for y in range(0, h, 7): poly.append((m + w + r.uniform(-irregular, irregular), m + y))
    for x in range(w, 0, -7): poly.append((m + x, m + h + r.uniform(-irregular, irregular)))
    for y in range(h, 0, -7): poly.append((m + r.uniform(-irregular, irregular), m + y))
    sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).polygon([(x + dx, y + dy) for x, y in poly], fill=sombra_alpha)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    c = cor.lstrip('#'); rgb = tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    shadow = Image.new('RGBA', (W, H), (20, 30, 10, 0)); shadow.putalpha(sh)
    card = Image.new('L', (W, H), 0); ImageDraw.Draw(card).polygon(poly, fill=255)
    fill = Image.new('RGBA', (W, H), rgb + (255,)); fill.putalpha(card.filter(ImageFilter.GaussianBlur(0.5)))
    Image.alpha_composite(shadow, fill).save(out)
    print(f'ok {out} {W}x{H}  área útil do cartão começa em ({m},{m})')

IGNORA = ('grad_', 'rasgo_', 'fita_', 'logo', 'papel_', 'foto', 'faz', 'cestas_')

def checar(paths):
    files = []
    for p in paths:
        files += sorted(glob.glob(os.path.join(p, '*.png'))) if os.path.isdir(p) else [p]
    ruins = 0
    for f in files:
        nome = os.path.basename(f).lower()
        if any(k in nome for k in IGNORA): continue
        if nome.startswith('recorte') and 'sticker' not in nome: continue  # recorte rente, sem sombra: pode encostar
        im = Image.open(f)
        if im.mode != 'RGBA': continue
        a = im.getchannel('A'); w, h = a.size
        bordas = {'topo': a.crop((0, 0, w, 1)).getextrema()[1], 'base': a.crop((0, h - 1, w, h)).getextrema()[1],
                  'esq': a.crop((0, 0, 1, h)).getextrema()[1], 'dir': a.crop((w - 1, 0, w, h)).getextrema()[1]}
        if any(bordas.values()):
            ruins += 1; print('CORTE SECO', f, {k: v for k, v in bordas.items() if v})
    print('ok: nenhuma sombra/contorno cortado' if not ruins else f'{ruins} arquivo(s) com sombra cortada: refaça com mais margem')
    return ruins

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd'); ap.add_argument('args', nargs='*')
    ap.add_argument('--blur', type=float, default=None); ap.add_argument('--dx', type=int, default=None)
    ap.add_argument('--dy', type=int, default=None); ap.add_argument('--alpha', type=int, default=110)
    ap.add_argument('--raio', type=int, default=0); ap.add_argument('--cor', default='#FBFAE9'); ap.add_argument('--seed', type=int, default=1)
    a = ap.parse_args()
    if a.cmd == 'sombra':
        out, w, h = a.args[0], int(a.args[1]), int(a.args[2])
        sombra(out, w, h, blur=a.blur or 18, dx=a.dx or 0, dy=14 if a.dy is None else a.dy, alpha=a.alpha, raio=a.raio)
    elif a.cmd == 'cartao':
        out, w, h = a.args[0], int(a.args[1]), int(a.args[2])
        cartao(out, w, h, a.cor, seed=a.seed, blur=a.blur or 14, dy=12 if a.dy is None else a.dy, dx=6 if a.dx is None else a.dx)
    elif a.cmd == 'checar':
        sys.exit(1 if checar(a.args) else 0)
    else:
        print(__doc__)
