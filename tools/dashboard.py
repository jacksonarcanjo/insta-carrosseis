"""Gera o painel de monitoramento em docs/index.html (publicado pelo GitHub Pages).

uso: python3 tools/dashboard.py [--no-api]

Le history.json, runs.json, planejamento.json, config.json e as pastas de posts/,
busca curtidas/comentarios/seguidores na Graph API (token injetado pelo proxy) e
grava docs/data.json + docs/index.html. Se a API falhar, reaproveita os numeros
do data.json anterior.
"""
import datetime as dt, glob, json, os, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = 'https://graph.facebook.com/v23.0'

def load(p, default):
    try:
        return json.load(open(os.path.join(ROOT, p)))
    except Exception:
        return default

def api(path, fields):
    with urllib.request.urlopen(f'{API}/{path}?fields={fields}', timeout=30) as r:
        return json.loads(r.read())

def main(use_api):
    cfg = load('config.json', {})
    old = load('docs/data.json', {})
    raw = f'https://raw.githubusercontent.com/{cfg["public_repo"]}/{cfg.get("public_branch", "main")}'
    posts = []
    for d in sorted(glob.glob(os.path.join(ROOT, 'posts/*/')), reverse=True):
        name = os.path.basename(d.rstrip('/'))
        slides = sorted(os.path.basename(s) for s in glob.glob(d + 'slide_*.jpg'))
        if not slides:
            continue
        pub = load(f'posts/{name}/published.json', None)
        spec = load(f'posts/{name}/spec.json', {})
        cap = open(d + 'caption.txt').read().strip() if os.path.exists(d + 'caption.txt') else ''
        posts.append({'pasta': name, 'slides': [f'{raw}/posts/{name}/{s}' for s in slides],
                      'legenda': cap, 'tema': spec.get('theme', ''), 'publicado': pub})
    hist = load('history.json', [])
    by_link = {h.get('permalink'): h for h in hist}
    for p in posts:
        h = by_link.get((p['publicado'] or {}).get('permalink'))
        if h:
            p['tema'] = p['tema'] or h.get('theme', '')
            p['personagens'] = h.get('characters', [])
    conta = old.get('conta', {})
    metr = old.get('metricas', {})
    erro_api = None
    if use_api:
        try:
            conta = api(cfg['ig_user_id'], 'username,followers_count,media_count,profile_picture_url')
            for p in posts:
                if p['publicado']:
                    m = api(p['publicado']['id'], 'like_count,comments_count')
                    metr[p['publicado']['id']] = {'curtidas': m.get('like_count', 0), 'comentarios': m.get('comments_count', 0)}
        except Exception as e:
            erro_api = str(e)[:200]
    for p in posts:
        if p['publicado']:
            p['metricas'] = metr.get(p['publicado']['id'], {})
    data = {
        'gerado_em': dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'),
        'config': {k: cfg.get(k) for k in ('handle', 'post_time', 'timezone', 'style')},
        'conta': conta, 'metricas': metr, 'erro_api': erro_api,
        'execucoes': load('runs.json', [])[-30:][::-1],
        'fila': load('planejamento.json', {}).get('fila', [])[:7],
        'posts': posts,
    }
    os.makedirs(os.path.join(ROOT, 'docs'), exist_ok=True)
    json.dump(data, open(os.path.join(ROOT, 'docs/data.json'), 'w'), indent=1, ensure_ascii=False)
    tpl = open(os.path.join(ROOT, 'tools/dashboard_template.html')).read()
    blob = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    open(os.path.join(ROOT, 'docs/index.html'), 'w').write(tpl.replace('/*__DATA__*/null', blob))
    print('painel gerado: docs/index.html', '(API falhou: ' + erro_api + ')' if erro_api else '')

if __name__ == '__main__':
    main('--no-api' not in sys.argv)
