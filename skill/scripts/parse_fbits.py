import re,sys,json
def parse(s):
    out=[]
    for blk in re.split(r'<div id="produto-spot-item-',s)[1:]:
        pid=blk.split('"')[0]
        t=re.search(r'<h3 class="spotTitle">\s*(.*?)\s*</h3>',blk,re.S)
        de=re.search(r'precoDe">.*?fbits-valor">([\d\.,]+)',blk,re.S)
        por=re.search(r'precoPor[^>]*>.*?fbits-valor">([\d\.,]+)',blk,re.S)
        off=re.search(r'fbits-etiqueta-off">\s*([^<]+?)\s*<',blk)
        url=re.search(r'href="(/produto/[^"]+)"',blk)
        img=re.search(r'data-original="(https://[^"]+/img/p/[^"?]+)',blk)
        n=lambda x: float(x.replace('.','').replace(',','.')) if x else None
        out.append(dict(id=pid,nome=t.group(1).strip() if t else None,de=n(de.group(1)) if de else None,por=n(por.group(1)) if por else None,off=off.group(1) if off else None,url=url.group(1) if url else None,img=img.group(1) if img else None))
    return out
allp=[]
for f in sys.argv[1:]:
    allp+=parse(open(f,errors='ignore').read())
json.dump(allp,open('produtos.json','w'),ensure_ascii=False,indent=1)
for p in allp:
    eco=(p['de']-p['por']) if p['de'] and p['por'] else 0
    print(f"{p['off'] or '':8} {p['de'] or 0:>10.2f} {p['por'] or 0:>10.2f} eco={eco:>8.2f}  {p['nome']}")
print(len(allp))
