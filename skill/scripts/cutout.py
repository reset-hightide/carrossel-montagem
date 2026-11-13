#!/usr/bin/env python3
"""Recorta o produto do fundo (rembg) e gera PNG transparente + versão "sticker" (contorno branco + sombra),
o recorte estilo colagem editorial.

Uso: ~/.venvs/post/bin/python cutout.py entrada.jpg saida_base [--outline 14] [--model isnet-general-use]
Gera: saida_base.png (só recorte, cortado rente) e saida_base_sticker.png
Dica: fotos de catálogo com fundo branco recortam quase perfeito; confira bordas de inox/vidro no zoom.
"""
import sys, argparse
from PIL import Image, ImageFilter, ImageChops
from rembg import remove, new_session

ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('out')
ap.add_argument('--outline', type=int, default=14); ap.add_argument('--model', default='isnet-general-use')
ap.add_argument('--white', type=int, default=238); ap.add_argument('--minhole', type=int, default=400)
a = ap.parse_args()
im = Image.open(a.src).convert('RGB')
cut = remove(im, session=new_session(a.model), post_process_mask=True)
# Híbrido p/ foto de catálogo em fundo claro: fundo = região quase-branca ligada à borda (flood fill).
# Pixels cromados/brancos DENTRO do produto voltam a ser opacos; buracos fechados quase-brancos
# grandes que o rembg marcou como fundo continuam transparentes.
import numpy as np
from scipy import ndimage
arr = np.asarray(im).astype(int); near = (arr.min(axis=2) >= a.white)
lab, n = ndimage.label(near)
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(border))
rm = np.asarray(cut.getchannel('A')) > 128
hole = near & ~bg & ~rm
hl, hn = ndimage.label(hole); sizes = ndimage.sum(hole, hl, range(1, hn + 1))
big = np.isin(hl, [i + 1 for i, sz in enumerate(sizes) if sz > a.minhole])
if (bg.mean() > 0.15):  # só usa o híbrido se há fundo claro de verdade
    fg = ~bg & ~big
    fg = ndimage.binary_opening(fg, iterations=1)
    m = Image.fromarray((fg * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.8))
    cut = im.convert('RGBA'); cut.putalpha(m)
bbox = cut.getchannel('A').point(lambda v: 255 if v > 20 else 0).getbbox()
cut = cut.crop(bbox); cut.save(a.out + '.png')
o = a.outline
# margem = contorno + deslocamento da sombra + 3σ do desfoque + folga: a sombra precisa chegar a alfa 0 antes da borda
pad = o * 7
base = Image.new('RGBA', (cut.width + 2 * pad, cut.height + 2 * pad), (0, 0, 0, 0)); base.paste(cut, (pad, pad), cut)
alpha = base.getchannel('A').point(lambda v: 255 if v > 40 else 0)
grown = alpha.filter(ImageFilter.MaxFilter(o * 2 + 1)).filter(ImageFilter.GaussianBlur(1))
shadow = grown.filter(ImageFilter.GaussianBlur(o)).point(lambda v: int(v * 0.35))
st = Image.new('RGBA', base.size, (0, 0, 0, 0))
# deslocamento SEM dar a volta (ImageChops.offset faz wrap: a sombra de baixo reaparecia no topo)
shifted = Image.new('L', base.size, 0); shifted.paste(shadow, (o // 2, o))
sh = Image.new('RGBA', base.size, (0, 0, 0, 255)); sh.putalpha(shifted)
st = Image.alpha_composite(st, sh)
wh = Image.new('RGBA', base.size, (255, 255, 255, 255)); wh.putalpha(grown)
st = Image.alpha_composite(st, wh); st = Image.alpha_composite(st, base)
bb = st.getchannel('A').point(lambda v: 255 if v > 0 else 0).getbbox()
x0, y0, x1, y1 = bb; m2 = 4  # folga transparente: nada encosta na borda
st = st.crop((max(0, x0 - m2), max(0, y0 - m2), min(st.width, x1 + m2), min(st.height, y1 + m2)))
st.save(a.out + '_sticker.png')
print('ok', a.out + '.png', a.out + '_sticker.png', cut.size)
