"""Monta um carrossel no estilo V4 (minimalista, estilo @christversions) a partir de um spec.json.

uso: .venv/bin/python tools/build.py posts/AAAA-MM-DD

spec.json:
{
  "handle": "@perfil",                      # opcional; se faltar, usa config.json
  "slides": [
    {"src": "<url ou caminho>", "mode": "full"|"low", "fx": 0.5, "fy": 0.5,
     "title": "...", "subtitle": "..."},    # slide 1 (capa): title + subtitle
    {"src": "...", "mode": "low", "text": "paragrafo justificado"}
  ],
  "caption": "legenda completa"
}
estilo (spec ou config.json, padrao "tarja"): "tarja" = imagem SEMPRE inteira (4:5, sem preenchimento),
  texto branco solto com sombra (sem tarja); cada slide aceita "pos": "top"|"bottom" (onde o texto fica, para nao cobrir
  o rosto) e **palavra** para destacar em amarelo (no title, destaque em laranja). "classico" = layout antigo (mode full/low).
mode "full": imagem 4:5 em tela cheia (use quando o topo da imagem e ceu/fundo limpo).
mode "low":  personagem ancorado embaixo, topo preenchido com a cor do ceu (use quando
             o rosto/personagem ficaria atras do texto).
fx/fy: foco horizontal/vertical do recorte (0 = esquerda/topo, 1 = direita/base).

Saida em posts/AAAA-MM-DD/: slide_01.jpg ... slide_NN.jpg (1080x1350), preview.jpg, caption.txt
"""
import html, json, os, subprocess, sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(ROOT, '.venv/bin/python')
MODELS = os.path.join(ROOT, 'models')
Image.MAX_IMAGE_PIXELS = None

def fetch(src, dst):
    if src.startswith('http'):
        subprocess.run(['curl', '-sL', '-m', '60', '-A', 'Mozilla/5.0', '-o', dst, src], check=True)
    else:
        Image.open(src).save(dst)
    Image.open(dst).verify()

def trim_bars(im, thr=18):
    """Remove faixas pretas (letterbox) em cima/embaixo/laterais de prints de anime."""
    a = np.asarray(im.convert('L')).astype(float)
    rows = np.where(a.mean(axis=1) > thr)[0]; cols = np.where(a.mean(axis=0) > thr)[0]
    if len(rows) < a.shape[0] * .5 or len(cols) < a.shape[1] * .5:
        return im
    return im.crop((cols[0], rows[0], cols[-1] + 1, rows[-1] + 1))

def crop(im, ar, fx, fy):
    w, h = im.size
    if w / h > ar:
        cw = round(h * ar); x = round((w - cw) * fx); return im.crop((x, 0, x + cw, h))
    ch = round(w / ar); y = round((h - ch) * fy); return im.crop((0, y, w, y + ch))

def upscale_to(path_in, path_out, target_h):
    h = Image.open(path_in).size[1]
    need = target_h / h
    if need <= 1.05:
        Image.open(path_in).convert('RGB').save(path_out); return
    scale = 2 if need <= 2 else 4
    model = os.path.join(MODELS, f'realesr-animevideov3-x{scale}')
    subprocess.run([PY, '-I', os.path.join(ROOT, 'tools/upscale.py'), path_in, path_out, model, str(scale)],
                   check=True, stdout=subprocess.DEVNULL)

def prepare(slide, i, d):
    raw = f'{d}/work/src{i}'
    fetch(slide['src'], raw)
    im = trim_bars(Image.open(raw).convert('RGB'))
    mode = slide.get('mode', 'full'); fx = slide.get('fx', .5); fy = slide.get('fy', .5)
    if mode == 'low':
        c = crop(im, 1080 / 900, fx, fy); size = (2160, 1800)
    else:
        c = crop(im, 0.8, fx, fy); size = (2160, 2700)
    c.save(f'{d}/work/crop{i}.png')
    upscale_to(f'{d}/work/crop{i}.png', f'{d}/work/up{i}.png', size[1])
    out = Image.open(f'{d}/work/up{i}.png').convert('RGB').resize(size, Image.LANCZOS)
    out.save(f'{d}/work/img{i}.jpg', quality=92)
    fill = None
    if mode == 'low':
        top = np.array(out.crop((0, 0, size[0], int(size[1] * .04)))).reshape(-1, 3).astype(float)
        col = np.median(top, axis=0)
        y = np.linspace(0, 1, 1350)[:, None, None]
        arr = np.ones((1350, 1080, 3)) * col * (0.9 + 0.1 * y)
        Image.fromarray(arr.clip(0, 255).astype(np.uint8)).save(f'{d}/work/fill{i}.jpg', quality=95)
        fill = f'work/fill{i}.jpg'
    return mode, f'work/img{i}.jpg', fill

CSS = """
@font-face{font-family:T;font-weight:600;src:url(FONTS/inter-tight-latin-600-normal.woff2)}
@font-face{font-family:T;font-weight:700;src:url(FONTS/inter-tight-latin-700-normal.woff2)}
@font-face{font-family:C;font-style:italic;font-weight:500;src:url(FONTS/cormorant-garamond-latin-500-italic.woff2)}
*{margin:0;padding:0;box-sizing:border-box}
body{background:#777;display:flex;flex-direction:column;gap:40px;padding:40px;align-items:center}
.slide{width:1080px;height:1350px;position:relative;overflow:hidden;background:#3d6f92;font-family:T;color:#fff}
.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.photo{filter:saturate(.92) contrast(.96) brightness(1.02)}
.low{position:absolute;left:0;bottom:0;width:1080px;height:900px;object-fit:cover;filter:saturate(.92) contrast(.96);-webkit-mask-image:linear-gradient(180deg,transparent 0,#000 26%)}
.wash{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.22) 0%,rgba(0,0,0,.08) 45%,rgba(0,0,0,0) 60%)}
.grain{position:absolute;inset:0;pointer-events:none;opacity:.32;mix-blend-mode:overlay;z-index:8;
 background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='1.1' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 1.5 0'/></filter><rect width='240' height='240' filter='url(%23n)'/></svg>")}
.txt{position:absolute;top:270px;left:92px;right:92px;z-index:5;text-shadow:0 2px 14px rgba(0,0,0,.28)}
.h{font:italic 500 26px C;opacity:.9;margin-bottom:14px}
.p{font-weight:700;font-size:56px;line-height:1.04;letter-spacing:-.02em;word-spacing:.02em;text-align:justify;text-align-last:left;hyphens:none}
.cover .p{text-align:center;text-align-last:center}
/* estilo "tarja" (nome mantido): imagem inteira, texto branco solto com sombra forte, sem tarja */
.tj{position:absolute;left:72px;right:72px;z-index:5;color:#fff}
.tj-top{top:96px}.tj-bottom{bottom:96px}
.tj .hd{font:italic 500 28px C;margin-bottom:12px;text-shadow:0 1px 3px rgba(0,0,0,.9),0 0 14px rgba(0,0,0,.6)}
.tj .ln{margin:0;font:700 52px/1.18 T;letter-spacing:-.02em;
 text-shadow:0 2px 2px rgba(0,0,0,.55),0 0 6px rgba(0,0,0,.55),0 0 22px rgba(0,0,0,.45);-webkit-text-stroke:.6px rgba(0,0,0,.25)}
.tj .ln b{color:#ffd23f}
.tj .tt{font-size:100px;line-height:1.02;letter-spacing:-.04em}
.tj .tt b{color:#ffd23f}
.tj .st{margin-top:14px;font-size:44px;font-weight:600}
@font-face{font-family:A;src:url(FONTS/anton-latin-400-normal.woff2)}
@font-face{font-family:PF;font-weight:500;src:url(FONTS/playfair-display-latin-500-normal.woff2)}
@font-face{font-family:PF;font-weight:500;font-style:italic;src:url(FONTS/playfair-display-latin-500-italic.woff2)}
/* variante christversions: bloco justificado, sem cor */
.v-cv .ln{font-size:56px;line-height:1.06;text-align:justify;text-align-last:left;letter-spacing:-.025em}
.v-cv .ln b{color:#fff}
.v-cv .tt{font-size:92px;text-align:center;text-align-last:center}.v-cv .st{text-align:center;text-align-last:center}
/* variante poetica (ocnathalie): serifada, palavra-chave em italico */
.v-po .ln{font:500 54px/1.2 PF;letter-spacing:-.01em}
.v-po .ln b{font-style:italic;color:#fff;font-weight:500}
.v-po .tt{font-size:96px;line-height:1.05}.v-po .st{font:italic 500 42px PF}
/* variante poster (frieren): condensada gigante caixa alta, creme + destaque */
.v-ps{color:#f6ecd9}
.v-ps .ln{font:400 64px/1.08 A;text-transform:uppercase;letter-spacing:.005em}
.v-ps .ln b{color:#ff5fa2;font-weight:400}
.v-ps .tt{font-size:150px;line-height:.96}.v-ps .st{font:600 40px/1.2 T;text-transform:none}
"""

def main(d):
    d = os.path.abspath(d)
    spec = json.load(open(f'{d}/spec.json'))
    cfg = json.load(open(os.path.join(ROOT, 'config.json')))
    handle = html.escape(spec.get('handle') or cfg.get('handle') or '')
    os.makedirs(f'{d}/work', exist_ok=True)
    fonts = os.path.relpath(os.path.join(ROOT, 'assets/fonts'), d)
    parts = []
    estilo = spec.get('estilo', cfg.get('estilo', 'tarja'))
    def rich(txt):  # **palavra** vira destaque
        out = html.escape(txt).split('**')
        return ''.join(f'<b>{x}</b>' if k % 2 else x for k, x in enumerate(out))
    for i, s in enumerate(spec['slides'], 1):
        if estilo == 'tarja':
            s = dict(s, mode='full')
            mode, img, fill = prepare(s, i, d)
            pos = 'tj-bottom' if s.get('pos') == 'bottom' else 'tj-top'
            if i == 1 and s.get('title'):
                inner = (f'<p class="ln tt">{rich(s["title"])}</p>'
                         f'<p class="ln st">{rich(s.get("subtitle", ""))}</p>')
            else:
                inner = f'<p class="ln">{rich(s["text"])}</p>'
            parts.append(f'<section class="slide" id="s{i}"><img class="bg photo" src="{img}">'
                         f'<div class="tj {pos} v-{spec.get("variante", cfg.get("variante", "cv"))}"><div class="hd">{handle}</div>{inner}</div><div class="grain"></div></section>')
            continue
        mode, img, fill = prepare(s, i, d)
        bg = (f'<img class="bg" src="{fill}"><img class="low" src="{img}">' if mode == 'low'
              else f'<img class="bg photo" src="{img}">')
        if i == 1 and s.get('title'):
            body = (f'<div class="txt cover" style="top:250px;left:60px;right:60px">'
                    f'<div class="h" style="margin-left:40px">{handle}</div>'
                    f'<div class="p" style="font-size:96px;letter-spacing:-.035em">{html.escape(s["title"])}</div>'
                    f'<div class="p" style="font-size:54px;margin-top:8px">{html.escape(s.get("subtitle", ""))}</div></div>')
        else:
            body = (f'<div class="txt"><div class="h">{handle}</div>'
                    f'<div class="p">{html.escape(s["text"])}</div></div>')
        parts.append(f'<section class="slide" id="s{i}">{bg}<div class="wash"></div>{body}<div class="grain"></div></section>')
    page = (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS.replace("FONTS", fonts)}</style>'
            f'</head><body>{"".join(parts)}</body></html>')
    open(f'{d}/carrossel.html', 'w').write(page)
    n = len(spec['slides'])
    subprocess.run(['node', os.path.join(ROOT, 'tools/render.js'), f'{d}/carrossel.html', f'{d}/work', str(n)], check=True)
    ims = []
    for i in range(1, n + 1):
        im = Image.open(f'{d}/work/raw_{i}.png').convert('RGB').resize((1080, 1350), Image.LANCZOS)
        im.save(f'{d}/slide_{i:02d}.jpg', quality=93); ims.append(im)
    cols = 4; rows = (n + cols - 1) // cols
    sheet = Image.new('RGB', (cols * 540, rows * 675), 'white')
    for i, im in enumerate(ims):
        sheet.paste(im.resize((540, 675)), ((i % cols) * 540, (i // cols) * 675))
    sheet.save(f'{d}/preview.jpg', quality=85)
    open(f'{d}/caption.txt', 'w').write(spec['caption'].strip() + '\n')
    print(f'ok: {n} slides -> {d}/preview.jpg')

if __name__ == '__main__':
    main(sys.argv[1])
