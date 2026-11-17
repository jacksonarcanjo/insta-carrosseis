"""Busca pins no Pinterest e gera uma folha de contato numerada.

uso: python tools/pinsearch.py "consulta" <pasta_saida>
saida: <pasta>/items.json e <pasta>/sheet.jpg (miniaturas numeradas com resolucao)
"""
import json, os, subprocess, sys, urllib.parse
from PIL import Image, ImageDraw

q, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
data = json.dumps({"options": {"query": q, "scope": "pins", "page_size": 25}, "context": {}})
url = 'https://br.pinterest.com/resource/BaseSearchResource/get/?data=' + urllib.parse.quote(data)
raw = subprocess.run(['curl', '-s', '-m', '30', '-A', 'Mozilla/5.0',
                      '-H', 'X-Pinterest-PWS-Handler: www/search/[scope].js', url],
                     capture_output=True, text=True).stdout
res = json.loads(raw)['resource_response']['data']['results']
items = []
for p in res:
    im = p.get('images', {}); o = im.get('orig'); t = im.get('236x')
    if not o or not t:
        continue
    items.append({'id': p['id'], 'w': o['width'], 'h': o['height'], 'orig': o['url'], 'thumb': t['url'],
                  'title': (p.get('grid_title') or p.get('description') or '')[:80]})
items = items[:16]
thumbs = []
for i, it in enumerate(items):
    f = f'{out}/t{i}.jpg'
    subprocess.run(['curl', '-s', '-m', '20', '-o', f, it['thumb']])
    try:
        thumbs.append(Image.open(f).convert('RGB'))
    except Exception:
        thumbs.append(Image.new('RGB', (236, 300), 'gray'))
json.dump({'query': q, 'items': items}, open(f'{out}/items.json', 'w'), indent=1, ensure_ascii=False)
C, W, H = 8, 236, 330
rows = max(1, (len(thumbs) + C - 1) // C)
sheet = Image.new('RGB', (C * W, rows * H), 'white'); d = ImageDraw.Draw(sheet)
for i, t in enumerate(thumbs):
    t.thumbnail((W, H - 24)); x, y = (i % C) * W, (i // C) * H
    sheet.paste(t, (x, y + 24)); d.rectangle([x, y, x + W, y + 22], fill='black')
    d.text((x + 4, y + 4), f"{i}  {items[i]['w']}x{items[i]['h']}", fill='yellow')
sheet.save(f'{out}/sheet.jpg', quality=85)
print(f'{len(items)} resultados -> {out}/sheet.jpg')
