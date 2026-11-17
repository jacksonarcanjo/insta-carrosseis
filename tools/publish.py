"""Publica um carrossel no Instagram pela API oficial (Instagram API with Instagram Login).

uso: python3 tools/publish.py posts/AAAA-MM-DD [--dry-run]

- As imagens precisam estar acessiveis publicamente: este script espera que
  posts/AAAA-MM-DD/slide_*.jpg ja tenham sido enviados (git push) para o repositorio
  publico configurado em config.json ("public_repo" e "public_branch").
- O token NAO fica no codigo: o proxy da sessao injeta o header Authorization
  nas chamadas para graph.instagram.com.
Grava posts/AAAA-MM-DD/published.json com o id e o link do post.
"""
import glob, json, os, sys, time, urllib.parse, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = 'https://graph.instagram.com/v23.0'

def call(method, path, params=None):
    url = f'{API}/{path}'
    data = None
    if params:
        enc = urllib.parse.urlencode(params)
        if method == 'GET':
            url += '?' + enc
        else:
            data = enc.encode()
    req = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f'ERRO API {method} {path}: {e.code} {e.read().decode()[:500]}')

def wait_ready(cid, tries=30):
    for _ in range(tries):
        st = call('GET', cid, {'fields': 'status_code'}).get('status_code')
        if st == 'FINISHED':
            return
        if st in ('ERROR', 'EXPIRED'):
            raise SystemExit(f'container {cid} status {st}')
        time.sleep(5)
    raise SystemExit(f'container {cid} nao ficou pronto')

def main(d, dry):
    d = os.path.abspath(d)
    cfg = json.load(open(os.path.join(ROOT, 'config.json')))
    rel = os.path.relpath(d, ROOT)
    slides = sorted(glob.glob(f'{d}/slide_*.jpg'))
    caption = open(f'{d}/caption.txt').read().strip()
    base = f'https://raw.githubusercontent.com/{cfg["public_repo"]}/{cfg.get("public_branch", "main")}/{rel}'
    urls = [f'{base}/{os.path.basename(s)}' for s in slides]
    if not 2 <= len(urls) <= 10:
        raise SystemExit('carrossel precisa de 2 a 10 imagens')
    for u in urls:  # confere que o Instagram vai conseguir baixar
        with urllib.request.urlopen(urllib.request.Request(u, method='HEAD'), timeout=30) as r:
            assert r.status == 200, u
    me = call('GET', 'me', {'fields': 'user_id,username'})
    print('conta:', me.get('username'))
    if dry:
        print('dry-run ok:', urls); return
    children = []
    for u in urls:
        children.append(call('POST', 'me/media', {'image_url': u, 'is_carousel_item': 'true'})['id'])
    for c in children:
        wait_ready(c)
    car = call('POST', 'me/media', {'media_type': 'CAROUSEL', 'children': ','.join(children), 'caption': caption})['id']
    wait_ready(car)
    pub = call('POST', 'me/media_publish', {'creation_id': car})
    info = call('GET', pub['id'], {'fields': 'permalink,timestamp'})
    json.dump({'id': pub['id'], **info, 'username': me.get('username')}, open(f'{d}/published.json', 'w'), indent=1)
    print('publicado:', info.get('permalink'))

if __name__ == '__main__':
    main(sys.argv[1], '--dry-run' in sys.argv)
