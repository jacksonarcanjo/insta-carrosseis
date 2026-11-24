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

_SEG = None
def cutout(src_jpg, dst_png):
    """Recorta o personagem/objeto principal (isnet-anime) para a camada da frente."""
    global _SEG
    from rembg import new_session, remove
    if _SEG is None:
        _SEG = new_session('isnet-anime')
    im = Image.open(src_jpg).convert('RGB')
    small = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
    mask = remove(small, session=_SEG, only_mask=True).convert('L').resize(im.size, Image.LANCZOS)
    out = im.convert('RGBA'); out.putalpha(mask); out.save(dst_png)
    m = np.asarray(mask.resize((1080, 1350))) > 128
    tops = np.where(m.any(axis=0), np.argmax(m, axis=0), 1350)[::4]
    if (tops < 1350).sum() < 5:
        return None
    return ','.join(str(int(x)) for x in tops)

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
@font-face{font-family:Pp;font-weight:300;src:url(FONTS/poppins-latin-300-normal.woff2),url(FONTS/poppins-latin-ext-300-normal.woff2)}
@font-face{font-family:Pp;font-weight:400;src:url(FONTS/poppins-latin-400-normal.woff2),url(FONTS/poppins-latin-ext-400-normal.woff2)}
@font-face{font-family:Pp;font-weight:600;src:url(FONTS/poppins-latin-600-normal.woff2),url(FONTS/poppins-latin-ext-600-normal.woff2)}
@font-face{font-family:Pp;font-weight:800;src:url(FONTS/poppins-latin-800-normal.woff2),url(FONTS/poppins-latin-ext-800-normal.woff2)}
/* estilo "serie" (psico.tsu): gancho com pesos misturados + frase gigante minuscula apertada, centralizado */
.sr{position:absolute;left:56px;right:56px;z-index:5;color:#fff;text-align:center;
 text-shadow:0 2px 3px rgba(0,0,0,.35),0 0 26px rgba(0,0,0,.35)}
.sr-top{top:215px}.sr-mid{top:50%;transform:translateY(-50%)}.sr-bottom{bottom:120px}
.sr .lg{font:300 32px Pp;letter-spacing:-.02em;margin-bottom:26px;opacity:.95}
.sr .lg b{font-weight:600}
.sr .k{font:300 50px/1.05 Pp;letter-spacing:-.045em}
.sr .k b{font-weight:600}
.sr .hl{font:800 118px/.86 Pp;letter-spacing:-.065em;margin-top:6px;text-transform:lowercase}
.sr .bd{font:300 34px/1.02 Pp;letter-spacing:-.05em;margin-top:26px;padding:0 30px}
.sr .bd b{font-weight:600}
.sr .bd p+p{margin-top:24px}
.fg{z-index:6;filter:saturate(.92) contrast(.96) brightness(1.02)}
/* decoracao: moldura, cantos, contador, etiqueta, divisor */
.dec{position:absolute;inset:0;z-index:7;pointer-events:none;color:#fff}
.dec .fr{position:absolute;inset:24px;border:2px solid rgba(255,255,255,.8);border-radius:4px;box-shadow:0 0 18px rgba(0,0,0,.25),inset 0 0 18px rgba(0,0,0,.18)}
.dec .fr2{position:absolute;inset:36px;border:1px solid rgba(255,255,255,.4)}
.dec .cn{position:absolute;width:54px;height:54px;border:0 solid #ffd23f}
.dec .tl{top:16px;left:16px;border-top-width:6px;border-left-width:6px}.dec .tr{top:16px;right:16px;border-top-width:6px;border-right-width:6px}
.dec .bl{bottom:16px;left:16px;border-bottom-width:6px;border-left-width:6px}.dec .br{bottom:16px;right:16px;border-bottom-width:6px;border-right-width:6px}
.dec .tp{position:absolute;top:52px;left:70px;right:70px;display:flex;justify-content:space-between;font:600 24px Pp;letter-spacing:.12em;text-shadow:0 1px 6px rgba(0,0,0,.6)}
.dec .tp .n b{color:#ffd23f;font-weight:800}
.dec .nx{position:absolute;bottom:52px;right:72px;font:600 26px Pp;letter-spacing:.12em;text-shadow:0 1px 6px rgba(0,0,0,.6)}
.dec .dots{position:absolute;bottom:56px;left:72px;display:flex;gap:10px}.dec .dots i{width:12px;height:12px;border-radius:50%;background:rgba(255,255,255,.45)}.dec .dots i.on{background:#ffd23f}
.scrim{position:absolute;left:0;right:0;top:0;height:900px;z-index:2;background:linear-gradient(180deg,rgba(0,0,0,.66),rgba(0,0,0,.34) 58%,rgba(0,0,0,0))}
.scrim.sb{top:auto;bottom:0;background:linear-gradient(0deg,rgba(0,0,0,.72),rgba(0,0,0,.4) 58%,rgba(0,0,0,0))}
.sr .tag{display:inline-block;background:#fff;color:#111;font:800 23px Pp;letter-spacing:.16em;text-transform:uppercase;padding:9px 22px 8px;border-radius:999px;margin-bottom:22px;text-shadow:none;box-shadow:0 3px 12px rgba(0,0,0,.35)}
.sr .dv{width:96px;height:6px;border-radius:3px;background:#ffd23f;margin:26px auto 0}
.sr.rich .hl{font-size:98px}
.sr.rich .bd{font:600 39px/1.2 Pp;letter-spacing:-.025em;margin-top:26px;padding:0 24px;text-shadow:0 2px 3px rgba(0,0,0,.6),0 0 16px rgba(0,0,0,.5)}
.sr.rich .bd b{font-weight:800;color:#ffd23f}
/* colagem: layouts variados (fantasma, painel, quadro, frase) */
.gw{position:absolute;left:50%;transform:translateX(-50%);z-index:3;font:400 420px/.82 A;text-transform:uppercase;white-space:nowrap;color:#fff;letter-spacing:.01em;text-shadow:0 6px 40px rgba(0,0,0,.25)}
.gw.ol{color:transparent;-webkit-text-stroke:5px #fff;text-shadow:none}
.cshade{position:absolute;inset:0;z-index:2;background:linear-gradient(0deg,rgba(0,0,0,.9) 0%,rgba(0,0,0,.66) 26%,rgba(0,0,0,.25) 46%,rgba(0,0,0,0) 62%)}
.cshade.t{background:linear-gradient(180deg,rgba(0,0,0,.9) 0%,rgba(0,0,0,.66) 26%,rgba(0,0,0,.25) 46%,rgba(0,0,0,0) 62%)}
.ccap{position:absolute;left:72px;right:72px;bottom:92px;z-index:9;color:#fff}
.ccap.t{bottom:auto;top:92px}
.ctag{display:inline-block;background:#ffd23f;color:#111;font:800 22px Pp;letter-spacing:.16em;text-transform:uppercase;padding:8px 20px 7px;margin-bottom:20px}
.ccap .hd{font:italic 500 72px/1.03 PF;letter-spacing:-.012em;text-shadow:0 2px 14px rgba(0,0,0,.6)}
.ccap .bd{font:500 35px/1.26 Pp;letter-spacing:-.015em;margin-top:20px;text-shadow:0 2px 10px rgba(0,0,0,.7)}
.ccap b{color:#ffd23f;font-weight:700}
.cpan{background:#f1ece2;color:#151515}
.cpan .pt{position:absolute;top:60px;left:84px;right:84px;display:flex;justify-content:space-between;font:italic 500 25px PF;letter-spacing:.04em;color:#555}
.cpan .col{position:absolute;left:84px;right:84px;top:112px;bottom:70px;display:flex;flex-direction:column;gap:34px}
.cpan .tt{font:400 124px/.92 A;text-transform:uppercase;letter-spacing:.005em}
.cpan .tt b{color:#b3261e;font-weight:400}
.fbox{position:relative;flex:none}
.cfr{position:absolute;background:#fff;padding:14px;box-shadow:0 14px 34px rgba(0,0,0,.3);z-index:4}
.cfr img{display:block;width:100%;height:100%;object-fit:cover}
.cpan .tx{font:500 40px/1.27 PF;text-align:justify;hyphens:none;color:#1b1b1b}
.cpan .tx b{font-weight:600;background:linear-gradient(transparent 56%,#ffd23f 56%)}
.gm{mix-blend-mode:multiply!important;opacity:.35!important}
.qm{position:absolute;top:40px;left:50px;font:400 640px/1 PF;color:rgba(255,255,255,.22);z-index:3}
.qt{position:absolute;left:92px;right:92px;top:38%;transform:translateY(-50%);font:italic 500 76px/1.14 PF;text-align:center;color:#fff;z-index:5;text-shadow:0 3px 18px rgba(0,0,0,.6)}
.qt b{color:#ffd23f;font-weight:500}
.qa{position:absolute;left:0;right:0;bottom:150px;text-align:center;font:600 27px Pp;letter-spacing:.3em;text-transform:uppercase;color:#ffd23f;z-index:5}
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

def prep_ar(src, key, d, W, H, fx=.5, fy=.5, zoom=1.0, zx=.5, zy=.35):
    """Recorta/amplia uma imagem para um quadro WxH (usado nos layouts de colagem)."""
    raw = f'{d}/work/{key}_raw'
    fetch(src, raw)
    im = trim_bars(Image.open(raw).convert('RGB'))
    c = crop(im, W / H, fx, fy)
    if zoom > 1:
        cw, ch = c.size; w2, h2 = cw / zoom, ch / zoom
        l, tp = (cw - w2) * zx, (ch - h2) * zy
        c = c.crop((round(l), round(tp), round(l + w2), round(tp + h2)))
    c.save(f'{d}/work/{key}_c.png')
    upscale_to(f'{d}/work/{key}_c.png', f'{d}/work/{key}_u.png', H)
    Image.open(f'{d}/work/{key}_u.png').convert('RGB').resize((W, H), Image.LANCZOS).save(f'{d}/work/{key}.jpg', quality=92)
    return f'work/{key}.jpg'


def render_collage(lay, s, i, d, handle, rich, n):
    def caption():
        if not (s.get('head') or s.get('body') or s.get('tag')):
            return ''
        pos = ' t' if s.get('pos') == 'top' else ''
        return (f'<div class="ccap{pos}">' + (f'<div class="ctag">{html.escape(s["tag"])}</div>' if s.get('tag') else '')
                + (f'<div class="hd">{rich(s["head"])}</div>' if s.get('head') else '')
                + (f'<div class="bd">{rich(s["body"])}</div>' if s.get('body') else '') + '</div>')
    shade = '<div class="cshade t"></div>' if s.get('pos') == 'top' else '<div class="cshade"></div>'
    if lay == 'fantasma':
        mode, img, fill = prepare(dict(s, mode='full'), i, d)
        tops = cutout(f'{d}/{img}', f'{d}/work/fg{i}.png')
        off = int(s.get('headroom', 0))
        bgcol, bgmask = '#000', ''
        if off:
            imq = Image.open(f'{d}/{img}').convert('RGB')
            a = np.asarray(imq.crop((0, 0, imq.width, max(2, int(imq.height * .03))))).reshape(-1, 3)
            c = np.median(a, axis=0).astype(int); bgcol = '#%02x%02x%02x' % tuple(int(v) for v in c)
            bgmask = ';-webkit-mask-image:linear-gradient(180deg,transparent 0,#000 150px)'
        fg = (f'<img class="bg fg" src="work/fg{i}.png" data-tops="{tops}" style="top:{off}px">' if tops else '')
        cls = 'gw ol' if s.get('outline') else 'gw'
        col = f' style="color:{s["wcolor"]}"' if s.get('wcolor') and not s.get('outline') else ''
        dim = s.get('dim', 0.62)
        return (f'<section class="slide" id="s{i}" style="background:{bgcol}"><img class="bg photo" src="{img}" '
                f'style="top:{off}px;filter:brightness({dim}) saturate(1.1){bgmask}">{shade}'
                f'<div class="{cls}"{col} data-off="{off}" data-wk="{s.get("wk", 0.72)}">{html.escape(s.get("word", ""))}</div>{fg}{caption()}<div class="grain"></div></section>')
    if lay == 'painel':
        two = bool(s.get('src2'))
        w1, h1 = (800, 470) if two else (900, 600)
        a = prep_ar(s['src'], f'p{i}a', d, int(w1 * 1.5), int(h1 * 1.5), s.get('fx', .5), s.get('fy', .5))
        fr = (f'<div class="fbox" style="height:{h1 + (90 if two else 40)}px"><div class="cfr" style="left:{20 if two else 40}px;top:6px;'
              f'width:{w1}px;height:{h1}px;transform:rotate(-1.3deg)"><img src="{a}"></div>')
        if two:
            b = prep_ar(s['src2'], f'p{i}b', d, 420, 510, s.get('fx2', .5), s.get('fy2', .5))
            fr += (f'<div class="cfr" style="right:6px;top:{h1 - 250}px;width:280px;height:340px;transform:rotate(3.5deg)"><img src="{b}"></div>')
        fr += '</div>'
        return (f'<section class="slide cpan" id="s{i}"><div class="pt"><span>{handle}</span><span>{html.escape(s.get("tag", ""))}</span></div>'
                f'<div class="col"><div class="tt">{rich(s.get("head", ""))}</div>{fr}<div class="tx">{rich(s.get("body", ""))}</div></div>'
                f'<div class="grain gm"></div></section>')
    if lay == 'quadro':
        mode, img, fill = prepare(dict(s, mode='full'), i, d)
        side = s.get('side', 'right')
        src2 = s.get('src2') or s['src']
        ins = prep_ar(src2, f'q{i}', d, 600, 750, s.get('fx2', .5), s.get('fy2', .35), zoom=(1.0 if s.get('src2') else s.get('zoom', 2.0)),
                      zx=s.get('zx', .5), zy=s.get('zy', .35))
        rot = 4 if side == 'right' else -4
        return (f'<section class="slide" id="s{i}"><img class="bg photo" src="{img}">{shade}'
                f'<div class="cfr" style="top:120px;{side}:64px;width:360px;height:450px;transform:rotate({rot}deg);z-index:6"><img src="{ins}"></div>'
                f'{caption()}<div class="grain"></div></section>')
    # frase
    mode, img, fill = prepare(dict(s, mode='full'), i, d)
    return (f'<section class="slide" id="s{i}"><img class="bg photo" src="{img}" style="filter:brightness(.52) saturate(.9)">'
            f'<div class="qm">&ldquo;</div><div class="qt">{rich(s["text"])}</div><div class="qa">{html.escape(s.get("autor", ""))}</div><div class="grain"></div></section>')


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
        if s.get('layout') in ('fantasma', 'painel', 'quadro', 'frase'):
            parts.append(render_collage(s['layout'], s, i, d, handle, rich, len(spec['slides'])))
            continue
        if estilo == 'serie':
            mode, img, fill = prepare(dict(s, mode='full'), i, d)
            fg = ''
            if s.get('camadas', spec.get('camadas', True)):
                top = cutout(f'{d}/{img}', f'{d}/work/fg{i}.png')
                if top is not None:
                    fg = f'<img class="bg fg" src="work/fg{i}.png" data-tops="{top}">'
            pos = {'top': 'sr-top', 'mid': 'sr-mid', 'bottom': 'sr-bottom'}.get(s.get('pos', 'top'), 'sr-top')
            k = s.get('kicker', spec.get('kicker', ''))
            decor = s.get('moldura', spec.get('decor', cfg.get('decor', False)))
            nslides = len(spec['slides'])
            inner = (f'<div class="lg">{handle}</div>' if (i == 1 and not decor) else '')
            inner += (f'<div class="tag">{html.escape(s["tag"])}</div>' if s.get('tag') else '')
            inner += (f'<div class="k">{rich(k)}</div>' if k and not s.get('no_kicker') else '')
            inner += f'<div class="hl">{rich(s.get("head", ""))}</div>'
            if s.get('body'):
                inner += '<div class="dv"></div><div class="bd">' + ''.join(f'<p>{rich(x)}</p>' for x in s['body'].split('\n\n')) + '</div>'
            dec = ''
            if decor:
                dots = ''.join(f'<i class="on"></i>' if j == i else '<i></i>' for j in range(1, nslides + 1))
                dec = (f'<div class="dec"><div class="fr"></div><div class="fr2"></div>'
                       f'<div class="cn tl"></div><div class="cn tr"></div><div class="cn bl"></div><div class="cn br"></div>'
                       f'<div class="tp"><span>{handle}</span><span class="n"><b>{i:02d}</b> / {nslides:02d}</span></div>'
                       f'<div class="dots">{dots}</div>' + ('<div class="nx">→</div>' if i < nslides else '') + '</div>')
            rich_cls = ' rich' if s.get('body') else ''
            parts.append(f'<section class="slide" id="s{i}"><img class="bg photo" src="{img}">'
                         + (f'<div class="scrim{" sb" if s.get("pos") == "bottom" else ""}"></div>' if (decor or s.get('body')) else '') +
                         f'<div class="sr {pos}{rich_cls}" data-pos="{s.get("pos", "top")}">{inner}</div>{fg}{dec}<div class="grain"></div></section>')
            continue
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
    script = """<script>
document.fonts.ready.then(()=>{document.querySelectorAll('.gw').forEach(g=>{
 const sec=g.closest('section'), fg=sec.querySelector('.fg'); let fs=420; g.style.fontSize=fs+'px';
 fs=Math.max(170,Math.min(600,fs*980/g.offsetWidth)); g.style.fontSize=fs+'px';
 const h=g.offsetHeight; let top=200;
 if(fg){const tp=fg.dataset.tops.split(',').map(Number).slice(38,232); const ct=Math.min(...tp)+parseFloat(g.dataset.off||0); top=Math.max(70,Math.min(700,ct-h*parseFloat(g.dataset.wk||0.72)));}
 g.style.top=top+'px';});
 document.querySelectorAll('section').forEach(sec=>{
 const fg=sec.querySelector('.fg'), tx=sec.querySelector('.sr'); if(!fg||!tx) return;
 if(tx.dataset.pos!=='top'){fg.remove();return;}
 const tops=fg.dataset.tops.split(',').map(Number);
 const cover=(el,dy)=>{const r=el.getBoundingClientRect(), s=sec.getBoundingClientRect();
   const x0=r.left-s.left, x1=r.right-s.left, y0=r.top-s.top+dy, y1=r.bottom-s.top+dy; let c=0,n=0,mx=0;
   for(let x=Math.max(0,x0);x<Math.min(1080,x1);x+=4){const t=tops[Math.floor(x/4)]; n++;
     const f=Math.max(0,Math.min(y1,1350)-Math.max(y0,t))/(y1-y0); c+=f; mx=Math.max(mx,f);}
   return {avg:n?c/n:0,max:mx};};
 const hl=tx.querySelector('.hl'), k=tx.querySelector('.k'), bd=tx.querySelector('.bd'), base=tx.offsetTop;
 const lh=parseFloat(getComputedStyle(hl).fontSize)*0.86, hr=hl.getBoundingClientRect();
 const last={getBoundingClientRect:()=>({left:hr.left,right:hr.right,top:hr.bottom-lh,bottom:hr.bottom})};
 const upper={getBoundingClientRect:()=>({left:hr.left,right:hr.right,top:hr.top,bottom:hr.bottom-lh})};
 const clear=(el,dy)=>!el||cover(el,dy).max<0.02;
 let best=null;
 for(let top=110; top<=300; top+=10){const dy=top-base;
   const cl=cover(last,dy);
   if(clear(k,dy) && clear(bd,dy) && (hr.height<lh*1.3 || clear(upper,dy)) && cl.avg>=0.02 && cl.avg<=0.12 && cl.max<=0.35){best=top;break;}}
 if(best!==null){tx.style.top=best+'px';}
 else{tx.style.top='150px'; fg.remove();}   // sem sobreposicao boa: texto no alto, na frente
});document.body.dataset.ready=1;});
</script>"""
    page = (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS.replace("FONTS", fonts)}</style>'
            f'</head><body>{"".join(parts)}{script}</body></html>')
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
