"""Gera um Reels 9:16 (1080x1920, MP4, sem audio) com efeito 2.5D a partir de um spec.json.

uso: .venv/bin/python tools/reel.py <pasta_com_spec.json>

spec.json (mesmo formato do estilo "serie"):
{ "kicker": "Você **sabe que é amizade** quando...",
  "slides": [ {"src": url, "fx": 0.5, "fy": 0.5, "head": "frase."}, ...,
              {"src": url, "no_kicker": true, "head": "virada,", "body": "texto **negrito**"} ] }

Cada cena: fundo com zoom lento, personagem recortado com zoom/deslocamento diferente (profundidade),
gancho + frase aparecendo palavra por palavra ATRAS do personagem (se ele cobrir pouco do texto).
Saida: <pasta>/reel.mp4 e <pasta>/reel_capa.jpg. A musica e colocada pelo dono no app do Instagram.
"""
import html, json, os, subprocess, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402

ROOT = build.ROOT
FPS, SCENE, FADE = 30, 3.4, 0.25


def prep(s, i, d):
    raw = f'{d}/rw/src{i}'
    build.fetch(s['src'], raw)
    im = build.trim_bars(Image.open(raw).convert('RGB'))
    c = build.crop(im, 1080 / 1920, s.get('fx', .5), s.get('fy', .5))
    c.save(f'{d}/rw/crop{i}.png')
    build.upscale_to(f'{d}/rw/crop{i}.png', f'{d}/rw/up{i}.png', 1920)
    Image.open(f'{d}/rw/up{i}.png').convert('RGB').resize((1080, 1920), Image.LANCZOS).save(f'{d}/rw/bg{i}.jpg', quality=92)
    build.cutout(f'{d}/rw/bg{i}.jpg', f'{d}/rw/fg{i}.png')
    m = np.asarray(Image.open(f'{d}/rw/fg{i}.png').split()[-1]) > 128
    band = m[300:760, 60:1020]          # faixa onde o texto fica
    behind = band.mean() < 0.06         # cobre pouco -> texto atras do personagem
    return behind


def rich(t):
    out = html.escape(t).split('**')
    return ''.join(f'<b>{x}</b>' if k % 2 else x for k, x in enumerate(out))


def words(t, cls):
    # cada palavra vira um span animavel (negrito preservado)
    res, bold = [], False
    for part in html.escape(t).split('**'):
        for w in part.split():
            res.append(f'<span class="w {cls}">{"<b>" + w + "</b>" if bold else w}</span>')
        bold = not bold
    return ' '.join(res)


def main(d):
    d = os.path.abspath(d)
    spec = json.load(open(f'{d}/spec.json'))
    cfg = json.load(open(os.path.join(ROOT, 'config.json')))
    handle = html.escape(cfg.get('handle', ''))
    os.makedirs(f'{d}/rw/frames', exist_ok=True)
    fonts = os.path.relpath(os.path.join(ROOT, 'assets/fonts'), d)
    scenes = []
    for i, s in enumerate(spec['slides'], 1):
        behind = prep(s, i, d)
        k = '' if s.get('no_kicker') else f'<div class="k">{words(spec.get("kicker", ""), "kw")}</div>'
        body = ''
        if s.get('body'):
            body = '<div class="bd">' + ''.join(f'<p>{words(x, "bw")}</p>' for x in s['body'].split('\n\n')) + '</div>'
        scenes.append(f'''<section class="sc" id="c{i}">
 <img class="bg" src="rw/bg{i}.jpg">
 <div class="tx" style="z-index:{3 if behind else 5}">{k}<div class="hl">{words(s.get("head", ""), "hw")}</div>{body}</div>
 <img class="fg" src="rw/fg{i}.png" style="z-index:4">
 <div class="hd">{handle}</div></section>''')
    css = ''.join(f"@font-face{{font-family:Pp;font-weight:{w};src:url({fonts}/poppins-latin-{w}-normal.woff2),url({fonts}/poppins-latin-ext-{w}-normal.woff2)}}"
                  for w in (300, 400, 600, 800))
    page = f'''<!doctype html><html><head><meta charset="utf-8"><style>{css}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;background:#000}}
.sc{{position:absolute;inset:0;overflow:hidden;opacity:0}}
.bg,.fg{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transform-origin:50% 60%;
 filter:saturate(.95) contrast(.97)}}
.tx{{position:absolute;top:330px;left:60px;right:60px;text-align:center;color:#fff;
 text-shadow:0 2px 3px rgba(0,0,0,.35),0 0 30px rgba(0,0,0,.35)}}
.k{{font:300 50px/1.1 Pp;letter-spacing:-.045em;margin-bottom:10px}} .k b{{font-weight:600}}
.hl{{font:800 128px/.88 Pp;letter-spacing:-.065em}}
.bd{{font:300 40px/1.08 Pp;letter-spacing:-.045em;margin-top:34px;padding:0 20px}} .bd b{{font-weight:600}} .bd p+p{{margin-top:26px}}
.w{{display:inline-block;opacity:0}}
.hd{{position:absolute;bottom:250px;left:0;right:0;text-align:center;color:#fff;font:400 30px Pp;opacity:.85;z-index:6;
 text-shadow:0 1px 6px rgba(0,0,0,.5)}}
.grain{{position:absolute;inset:-60px;pointer-events:none;opacity:.26;mix-blend-mode:overlay;z-index:9;
 background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='1.1' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 1.5 0'/></filter><rect width='240' height='240' filter='url(%23n)'/></svg>")}}
</style></head><body>{''.join(scenes)}<div class="grain" id="gr"></div>
<script>
const S={SCENE},F={FADE},N={len(scenes)};
const ease=x=>1-Math.pow(1-x,3);
function render(t){{
  const i=Math.min(N-1,Math.floor(t/S)), lt=t-i*S, p=lt/S;
  document.querySelectorAll('.sc').forEach((sc,j)=>{{
    let o=0; if(j===i) o=Math.min(1,lt/F, (S-lt)/F*1.0+ (i===N-1?1:0)); sc.style.opacity=Math.max(0,Math.min(1,o));
    if(j!==i) return;
    sc.querySelector('.bg').style.transform=`scale(${{1.10-0.06*p}}) translateY(${{-10*p}}px)`;
    sc.querySelector('.fg').style.transform=`scale(${{1.10-0.06*p+0.05*ease(p)}}) translateY(${{28*(1-ease(p))}}px)`;
    const ws=[...sc.querySelectorAll('.w')];
    ws.forEach((w,n)=>{{const st=0.25+n*0.09, q=Math.max(0,Math.min(1,(lt-st)/0.32)), e=ease(q);
      w.style.opacity=e; w.style.transform=`translateY(${{(1-e)*26}}px)`; w.style.filter=`blur(${{(1-e)*8}}px)`;}});
  }});
  const g=document.getElementById('gr'); g.style.transform=`translate(${{(Math.floor(t*24)*37)%60-30}}px,${{(Math.floor(t*24)*53)%60-30}}px)`;
}}
window.render=render; window.TOTAL=S*N;
</script></body></html>'''
    open(f'{d}/reel.html', 'w').write(page)
    js = f'''const {{chromium}}=require('playwright');(async()=>{{
const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});
await p.goto('file://{d}/reel.html');await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(400);
const total=await p.evaluate(()=>window.TOTAL);const n=Math.round(total*{FPS});
for(let f=0;f<n;f++){{await p.evaluate(t=>window.render(t),f/{FPS});
 await p.screenshot({{path:`{d}/rw/frames/f${{String(f).padStart(4,'0')}}.jpg`,type:'jpeg',quality:92}});}}
await b.close();}})();'''
    open(f'{d}/rw/rec.js', 'w').write(js)
    subprocess.run(['node', f'{d}/rw/rec.js'], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{d}/rw/frames/f%04d.jpg',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium',
                    '-movflags', '+faststart', f'{d}/reel.mp4'], check=True)
    cover = int((SCENE - 0.6) * FPS)
    Image.open(f'{d}/rw/frames/f{cover:04d}.jpg').save(f'{d}/reel_capa.jpg', quality=92)
    print(f'ok: {d}/reel.mp4')


if __name__ == '__main__':
    main(sys.argv[1])
