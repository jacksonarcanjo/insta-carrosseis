# Playbook do post diário

Instruções para a sessão automática que roda todo dia e publica um carrossel no Instagram.
Siga na ordem. Trabalhe sozinho: não há ninguém para responder perguntas.

## 0. Preparar
```bash
cd <raiz deste repositório>
git pull --ff-only
bash setup.sh
DATE=$(TZ=America/Sao_Paulo date +%F); mkdir -p posts/$DATE
```
Se `posts/$DATE/published.json` já existe, o post de hoje já saiu: pare.

## 1. Escolher o tema
- Leia `history.json` (temas e personagens já usados). Não repita um tema dos últimos 30 dias,
  nem o mesmo personagem principal dos últimos 7 dias.
- Escolha um tema da lista abaixo (ou um parecido) e 5–7 personagens de anime que ilustrem bem o tema.
  Prefira animes populares no Brasil (Naruto, One Piece, Dragon Ball, MHA, Black Clover, HxH,
  Demon Slayer, Jujutsu Kaisen, Frieren, Haikyuu, Spy x Family, Attack on Titan, Violet Evergarden,
  Your Lie in April, Fullmetal Alchemist, Bleach, Chainsaw Man, Blue Lock, Solo Leveling…).

Temas: motivação, superação, amizade, ansiedade, autoestima, solidão, recomeços, saudade,
persistência, medo de falhar, comparação com os outros, família, luto, paciência consigo mesmo,
sonhos, disciplina, gratidão, coragem, ser gentil, aceitar ajuda, crescer, perdoar, propósito.

## 2. Escrever o texto (tom: @christversions — segunda pessoa, acolhedor, sem clichê barato)
- Slide 1 (capa): `title` com até ~32 caracteres (pergunta ou afirmação forte) + `subtitle` curto.
- Slides 2..N-1: um personagem por slide (ou uma ideia por slide), **um parágrafo de 18 a 28 palavras**,
  falando do personagem e conectando com quem lê. Nada de listas nem emojis no slide.
- Último slide: chamada para comentar ("E você? … Me conta nos comentários.").
- Total: 6 a 8 slides.
- Legenda: título + 💭, 3–4 parágrafos curtos, pergunta final, depois 3–5 hashtags
  (#anime #animes + temáticas). Português do Brasil correto, com acentos.

## 3. Achar as imagens (uma busca por slide)
```bash
.venv/bin/python -I tools/pinsearch.py "<personagem> anime screenshot aesthetic" posts/$DATE/search/s2
```
Abra `posts/$DATE/search/sN/sheet.jpg` com a ferramenta Read e escolha a melhor miniatura:
- **frame do anime oficial** (print limpo, cores vivas), não fan art pesada, sem marca d'água, sem texto escrito na imagem;
- personagem reconhecível; resolução ≥ 700 px de altura;
- para a capa: personagem olhando para cima/horizonte, céu bonito.
Use a URL `orig` do item escolhido em `items.json` como `src`.
Se nada servir, refaça a busca com outras palavras ("<personagem> <anime> scene", "<personagem> icon sky").

Escolha o `mode`:
- `full` quando a metade de cima da imagem é céu/fundo limpo (o texto vai em cima);
- `low` quando o rosto/personagem ocupa a parte de cima — ele desce e o topo vira a cor do céu.
`fx` (0–1) desloca o recorte para o personagem em imagens horizontais.

## 4. Montar
Escreva `posts/$DATE/spec.json` (formato no topo de `tools/build.py`) e rode:
```bash
.venv/bin/python tools/build.py posts/$DATE
```
Abra `posts/$DATE/preview.jpg` com Read e confira **todos** os slides:
- texto não pode ficar em cima do rosto do personagem → troque para `mode: "low"` ou ajuste `fx`;
- nada de imagem borrada, cortada de forma estranha, com marca d'água ou texto da imagem;
- texto justificado sem buracos enormes (se tiver, reescreva a frase um pouco mais longa ou curta).
Corrija e rode de novo até ficar bom (no máximo 4 tentativas; se uma imagem não presta, troque-a).

## 5. Publicar
```bash
rm -rf posts/$DATE/work posts/$DATE/search
git add posts/$DATE && git commit -m "post $DATE" && git push origin main
sleep 20
python3 tools/publish.py posts/$DATE --dry-run && python3 tools/publish.py posts/$DATE
```
Depois atualize `history.json` com `{"date", "theme", "characters", "permalink"}`, commit e push.

## Se algo der errado
- Erro 190 / token inválido ou expirado da API: não tente contornar. Termine relatando
  "TOKEN EXPIRADO — gere um novo token no painel da Meta e atualize o segredo do ambiente".
- Pinterest fora do ar: tente de novo em 2 min; se continuar, relate e pare (não publique nada improvisado).
- Nunca publique duas vezes no mesmo dia. Nunca publique conteúdo que você não conferiu no preview.
