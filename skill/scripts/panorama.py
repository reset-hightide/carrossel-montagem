#!/usr/bin/env python3
"""Carrossel PANORÂMICO: o post é desenhado como UMA tira contínua (n slides lado a lado) e depois fatiado.
Imagens, painéis, cartas, faixas e objetos podem atravessar a divisa entre slides: metade aparece no fim
de um slide e a outra metade no começo do próximo (a "emenda" entre slides).

Uso:
  panorama.py fatiar  pano.json spec_carrossel.json            -> 1 slide = 1 quadro de 1080x1350 (o post)
  panorama.py unico   pano.json spec_unico.json [--max 7560]   -> design único: tira inteira em páginas largas
  panorama.py checar  pano.json                                -> divisas, texto cortado, emendas

pano.json = {
  "w": 1080, "h": 1350, "n": 10,              # tamanho de UM slide e quantidade
  "fonts": {...}, "bg": "#F4EFE6",            # fundo da tira inteira (opcional)
  "notes": ["notas slide 1", ...],            # opcional, 1 por slide
  "els": [ ... mesmos elementos do build_pptx.py, com x na coordenada da TIRA (0 .. n*w) ... ]
}
Cada elemento pode ter "slide": k (1..n) para escrever x relativo ao slide k (x_tira = (k-1)*w + x).
Elemento que cruza a divisa vai para os DOIS slides, com o x deslocado (a parte de fora fica fora da página
e o Canva corta na exportação/no post). No Canva continua sendo UMA imagem em cada slide (editável).

Regras (checar avisa):
- TEXTO nunca cruza divisa e fica a >= 64px dela (margem segura; o Instagram corta a borda no feed).
- Ponte = elemento que cruza a divisa. Pelo menos uma ponte em ~metade das divisas (ritmo), e o objeto
  cortado tem que fazer sentido nos dois lados (nada de cortar rosto ou o logo do produto no meio).
- A divisa não deve cair sobre detalhe pequeno (preço, rótulo): o corte tem que parecer intencional.

Design único (limite do Canva: 8000 px de lado): os slides são agrupados em páginas de até 7 slides
(7 x 1080 = 7560), divididos por igual (10 slides -> 2 páginas de 5; 14 -> 2 de 7). Pontes que cruzam a
divisa entre páginas aparecem nas duas páginas. O .pptx tem limite de 56 polegadas (5376 px a 96 dpi), então
o `unico` reduz a escala sozinho (ex.: 5400 px -> escala 0.5 = 2700 x 675) e imprime o tamanho cheio. Depois do
import no Canva: se a página não vier no tamanho cheio, redimensionar o design (resize-design / Redimensionar)
para o tamanho impresso — a proporção é a mesma, o conteúdo escala junto. Conferir as fontes depois.
"""
import json, sys, math, copy, argparse

def bbox(e):
    if e['t'] == 'line':
        return min(e['x1'], e['x2']), max(e['x1'], e['x2'])
    return e['x'], e['x'] + e['w']

def shift(e, dx):
    e = copy.deepcopy(e)
    if e['t'] == 'line':
        e['x1'] += dx; e['x2'] += dx
    else:
        e['x'] += dx
    e.pop('slide', None)
    return e

def load(p):
    P = json.load(open(p)); W = P.get('w', 1080)
    for e in P['els']:
        k = e.get('slide')
        if k:
            dx = (k - 1) * W
            if e['t'] == 'line': e['x1'] += dx; e['x2'] += dx
            else: e['x'] += dx
            e.pop('slide')
    return P

def cortar(P, chunk):
    """agrupa 'chunk' slides por página e devolve spec do build_pptx."""
    W, H, n = P.get('w', 1080), P.get('h', 1350), P['n']
    notes = P.get('notes', [])
    pages = math.ceil(n / chunk); out = []
    for i in range(pages):
        a, b = i * chunk, min(n, (i + 1) * chunk)
        x0, x1 = a * W, b * W
        els = [shift(e, -x0) for e in P['els'] if bbox(e)[1] > x0 and bbox(e)[0] < x1]
        nt = '\n\n'.join(f'[slide {k + 1}] {notes[k]}' if chunk > 1 else notes[k]
                        for k in range(a, b) if k < len(notes) and notes[k])
        pg = {'els': els, 'notes': nt}
        if P.get('bg'): pg['bg'] = P['bg']
        out.append(pg)
    spec = {'w': chunk * W, 'h': H, 'fonts': P.get('fonts', {}), 'slides': out}
    if P.get('escala'): spec['escala'] = P['escala']
    return spec

def checar(P):
    W, n = P.get('w', 1080), P['n']; prob = 0; pontes = {}
    for e in P['els']:
        x0, x1 = bbox(e); nm = e.get('name') or (e.get('runs') or [{}])[0].get('txt', e['t'])[:30]
        for d in range(1, n):
            s = d * W
            if x0 < s < x1:
                if e['t'] == 'text':
                    print(f'ERRO texto cruza a divisa {d}|{d + 1}: {nm}'); prob += 1
                else:
                    pontes.setdefault(d, []).append(nm)
        if e['t'] == 'text':
            k = int(x0 // W); l, r = x0 - k * W, x1 - k * W
            if l < 64 or r > W - 64:
                print(f'AVISO texto a menos de 64px da borda do slide {k + 1}: {nm}'); prob += 1
    for d in range(1, n):
        print(f'divisa {d:>2}|{d + 1:<2}', 'ponte: ' + ', '.join(pontes[d]) if d in pontes else '-- sem ponte')
    if len(pontes) < (n - 1) / 2:
        print(f'AVISO só {len(pontes)} de {n - 1} divisas têm ponte; o pedido é imagens emendando entre os slides')
    print('ok' if not prob else f'{prob} problema(s)')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['fatiar', 'unico', 'checar'])
    ap.add_argument('pano'); ap.add_argument('out', nargs='?')
    ap.add_argument('--max', type=int, default=7560, help='largura máx. da página do design único (Canva: 8000)')
    ap.add_argument('--escala', type=float)
    a = ap.parse_args(); P = load(a.pano)
    if a.escala: P['escala'] = a.escala
    if a.cmd == 'checar': checar(P); sys.exit()
    W, n = P.get('w', 1080), P['n']
    if a.cmd == 'fatiar': chunk = 1
    else:
        per = max(1, a.max // W); pages = math.ceil(n / per); chunk = math.ceil(n / pages)
    if a.cmd == 'unico' and not P.get('escala') and chunk * W > 5376:
        P['escala'] = math.floor(5376 / (chunk * W) * 20) / 20  # múltiplo de 0,05
    spec = cortar(P, chunk)
    if spec.get('escala'):
        print(f"escala {spec['escala']}: pptx {int(spec['w'] * spec['escala'])} x {int(spec['h'] * spec['escala'])};"
              f" no Canva redimensionar para {spec['w']} x {spec['h']}")
    json.dump(spec, open(a.out, 'w'), ensure_ascii=False, indent=1)
    print('ok', a.out, len(spec['slides']), 'página(s) de', spec['w'], 'x', spec['h'])
