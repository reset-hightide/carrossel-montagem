#!/usr/bin/env python3
"""Reduz o .pptx (limite de 10 MB do file_upload do Chrome) sem perda visível:
imagens em ppt/media com lado maior > MAX viram MAX px; JPEG q=90; PNG com alpha fica PNG otimizado,
PNG sem alpha é recomprimido (mesmo nome/extensão, para não quebrar as relações).

Uso: ~/.venvs/post/bin/python optimize_pptx.py entrada.pptx saida.pptx [--max 2000]
"""
import zipfile, io, sys, argparse
from PIL import Image

ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('dst'); ap.add_argument('--max', type=int, default=2000)
a = ap.parse_args()
zin = zipfile.ZipFile(a.src); zout = zipfile.ZipFile(a.dst, 'w', zipfile.ZIP_DEFLATED)
before = after = 0
for it in zin.infolist():
    data = zin.read(it.filename)
    if it.filename.startswith('ppt/media/') and it.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        before += len(data)
        im = Image.open(io.BytesIO(data)); im.load()
        if max(im.size) > a.max:
            im.thumbnail((a.max, a.max), Image.LANCZOS)
        buf = io.BytesIO()
        if it.filename.lower().endswith('.png'):
            if im.mode in ('RGBA', 'LA', 'P'):
                im.save(buf, 'PNG', optimize=True)
            else:
                im.convert('RGB').save(buf, 'PNG', optimize=True)
        else:
            im.convert('RGB').save(buf, 'JPEG', quality=90, optimize=True, progressive=True)
        new = buf.getvalue()
        data = new if len(new) < len(data) else data
        after += len(data)
    zout.writestr(it, data)
zout.close()
import os
print(f'media {before/1e6:.1f} MB -> {after/1e6:.1f} MB; arquivo {os.path.getsize(a.dst)/1e6:.1f} MB')
