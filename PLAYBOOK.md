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
Se `posts/$DATE/spec.json` existe com `"pronto": true` e os `slide_*.jpg` estão lá, o post já foi montado e aprovado pelo dono:
pule direto para a etapa 5 (Publicar), sem refazer nada. Sem `"pronto": true`, ignore o rascunho e faça o post do zero.

## 1. Escolher o tema
- **Primeiro olhe `planejamento.json`:** se a `fila` tiver itens, use o **primeiro** (tema + personagens sugeridos + `nota`, se houver — a `nota` é instrução do dono e deve ser seguida;
  pode trocar um personagem se não achar imagem boa). Depois remova esse item da fila e acrescente temas novos
  no final até a fila ter 7 itens (cada item: `{"tema": ..., "personagens": [5 nomes]}`), respeitando as regras abaixo.
- **Domingo é dia de post cristão** (a partir de 29/11/2026): todo domingo o tema deve ser cristão, no estilo
  @christversions (anime como ponte para falar do amor de Deus, fé, graça, perdão, esperança), com 1–2 versículos
  citados com referência exata e texto fiel, tom acolhedor, sem polêmica doutrinária, hashtags #jesus #fé #deus #cristão
  + anime. Nos outros dias, temas não religiosos. Ao completar a fila, posicione os itens cristãos (com `nota`
  explicando isso) nas posições que caem em domingo — a fila corresponde a dias consecutivos a partir do próximo post.
- Leia `history.json` (temas e personagens já usados). Não repita um tema dos últimos 30 dias,
  nem o mesmo personagem principal dos últimos 7 dias.
- Escolha um tema da lista abaixo (ou um parecido) e 5–7 personagens de anime que ilustrem bem o tema.
  Prefira animes populares no Brasil (Naruto, One Piece, Dragon Ball, MHA, Black Clover, HxH,
  Demon Slayer, Jujutsu Kaisen, Frieren, Haikyuu, Spy x Family, Attack on Titan, Violet Evergarden,
  Your Lie in April, Fullmetal Alchemist, Bleach, Chainsaw Man, Blue Lock, Solo Leveling…).

Temas: motivação, superação, amizade, ansiedade, autoestima, solidão, recomeços, saudade,
persistência, medo de falhar, comparação com os outros, família, luto, paciência consigo mesmo,
sonhos, disciplina, gratidão, coragem, ser gentil, aceitar ajuda, crescer, perdoar, propósito.

## 2. Formato dos slides (estilo atual: "serie", inspirado em @psico.tsu)
- O post é uma **série com gancho fixo** (`"kicker"` no spec, repetido em todos os slides), ex.:
  "Você **sabe que perdeu** quando...", "Você **sabe que está crescendo** quando...", "Sinais de que **você está se curando**...".
  Use `**negrito**` em 2–4 palavras do meio do gancho (o resto sai em letra fina).
- Cada slide tem uma `"head"`: frase curta (3 a 7 palavras), minúscula, que completa o gancho e termina com ponto.
- Último slide: `"no_kicker": true`, `head` de virada ("mas você ainda não perdeu", "e se você tem alguém assim,")
  e `"body"` com 1–2 parágrafos curtos (use `**negrito**` em trechos) + "**Siga @darkgoodvibes** ...". Separe parágrafos com linha em branco (\n\n).
- Todos os slides com `"pos": "top"`. O texto vai **atrás do personagem**: o build recorta o personagem e posiciona
  o texto sozinho para a cabeça cobrir só a parte de baixo da última linha.
- **Escolha de imagem é o mais importante:** personagem na METADE DE BAIXO, céu/fundo limpo em cima (cabeça mais ou menos
  no meio da imagem). Personagem que ocupa a imagem inteira até o topo não serve (o build desliga as camadas).
- Revise no preview: o efeito de camadas deve aparecer (cabeça/cabelo na frente de parte da última linha) e o texto
  continuar legível; se a cabeça cobrir mais de ~1/4 da frase, troque a imagem.

## 2b. Escrever o texto (tom: @christversions — segunda pessoa, acolhedor, sem clichê barato)
- Slides 2..N-1: um personagem por slide (ou uma ideia por slide), **um parágrafo de 18 a 28 palavras**,
  falando do personagem e conectando com quem lê. Nada de listas nem emojis no slide.
- Último slide: chamada para comentar ("E você? … Me conta nos comentários.").
- Total: 6 a 8 slides.
- Em cada texto de slide, marque 2 a 5 palavras-chave com `**assim**` (vira destaque amarelo).
- Legenda: siga a seção **"Como escrever a legenda"** abaixo. Português do Brasil correto, com acentos.

### Como escrever a legenda (1.300 a 2.000 caracteres; limite do Instagram: 2.200)
A legenda é onde o post ganha profundidade. **REGRA DO DONO: a legenda NÃO pode repetir o carrossel.**
Os slides contam os personagens; a legenda fala da **vida de quem lê**. Na legenda:
- não reconte as cenas dos slides nem copie frases deles; cite no máximo 1 personagem, de passagem, ou nenhum;
- traga um ângulo novo: uma situação do dia a dia, uma pergunta, um "por quê" psicológico, um conselho prático;
- antes de publicar, compare legenda e slides: se alguma frase da legenda parecer com algum slide, reescreva.
Estrutura:

1. **Gancho (1ª linha, até ~90 caracteres):** é o que aparece antes do "mais". Uma frase que dá vontade de abrir:
   uma verdade incômoda, uma pergunta ou uma cena. Termine com um emoji discreto (💭 🌙 🤍 🍃 ✨).
2. **Identificação (2–3 frases):** descreva o sentimento como a pessoa vive no dia a dia, em segunda pessoa,
   com detalhes concretos ("aquela noite em que você ficou olhando o teto…"). Nada de frase genérica de coach.
3. **Aprofundamento (2–3 parágrafos curtos):** por que esse sentimento acontece, como ele aparece na rotina,
   o que dá pra fazer com ele na prática. Linguagem simples, sem jargão, sem inventar estudo.
4. **Virada / reflexão (2–4 frases):** o que essas histórias ensinam que serve para a vida real. Humana e honesta:
   reconheça que é difícil, sem prometer solução mágica.
5. **Frase de fechamento em destaque:** uma linha sozinha, curta e marcante, que dê vontade de printar.
6. **Chamada para conversar:** uma pergunta específica ("Qual cena de anime te fez chorar sem esperar?"),
   não um "comenta aí" genérico. Na linha seguinte: "Salva para reler num dia difícil e manda para quem precisa ouvir isso hoje."
7. **Hashtags (8 a 12, numa linha separada no fim):** misture amplas (#anime #animes #otaku #animebrasil),
   do tema (#motivação #ansiedade #amizade…) e dos animes citados (#naruto #onepiece…). Nunca repita a mesma
   lista de um dia para o outro.

Recursos que funcionam nas referências do dono (@psico.tsu e @christversions) — use 2 ou 3 por legenda:
- **Contradição na abertura:** "Você pode passar anos tentando X e, no processo, perder justamente Y."
- **Frase isolada de impacto** entre parágrafos ("É uma contradição que passa despercebida.").
- **Base de psicologia em linguagem simples:** "Na psicologia, a gente sabe que…" (sem jargão, sem inventar estudo).
- **Nuance honesta:** "Isso não significa que… Significa reconhecer que…": evita soar como coach.
- **Cadência com "Talvez…"** em duas frases seguidas perto do fim.
- **Antítese no fechamento** (estilo @christversions): "Uma verdade que dói liberta, mas uma mentira aprisiona."
- **Chamada para seguir com propósito** no final: "Siga @darkgoodvibes para continuar encontrando nos animes reflexões sobre a sua própria história."

Nos posts cristãos de domingo, a legenda é mais curta (600 a 1.100 caracteres): título + 💭, 3 ou 4 parágrafos
que terminam com 💭, ✝️ ou ❤️, o versículo citado com a referência, e a última frase em antítese.

Formato: parágrafos de 1 a 3 frases separados por linha em branco; 1 emoji no fim de no máximo 4 parágrafos;
nada de listas com marcadores, nada de CAIXA ALTA, nada de travessão em excesso. Leia em voz alta antes de publicar.

Exemplo (tema "amizade"):
```
Tem gente que entra na nossa vida só pra provar que a gente não precisava enfrentar tudo sozinho 🤍

Talvez você conheça essa sensação: passar tanto tempo resolvendo tudo por conta própria que pedir ajuda parece fraqueza. Até que alguém aparece, senta do seu lado e fica, mesmo quando você não sabe explicar o que está sentindo.

O Naruto passou anos correndo atrás do Sasuke quando todo mundo já tinha desistido dele. Não porque fosse fácil, mas porque entendia uma solidão que ninguém mais via. E o Gon e o Killua mostraram o outro lado: às vezes amizade é deixar o outro seguir o próprio caminho, mesmo doendo 💭

Já o Luffy nunca pediu que o Zoro fosse menos do que era. Confiou nele inteiro, com as cicatrizes e os sonhos, e foi essa confiança que fez um caçador de piratas solitário virar família.

Amizade de verdade não te salva de tudo. Mas te lembra, nos piores dias, que você não está carregando o peso sozinho ✨

Quem chega fica. Quem fica cuida.

Qual dupla de anime te fez acreditar em amizade de verdade? Marca aqui aquela pessoa que é o seu Killua.
Salva para reler num dia difícil e manda para quem precisa ouvir isso hoje.

#anime #animes #animebrasil #otaku #amizade #naruto #sasuke #hunterxhunter #gonandkillua #onepiece #luffy #zoro
```

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

Estilo atual: **"tarja"** — a imagem aparece SEMPRE inteira (sem borrão/preenchimento) e o texto vai solto, branco
com sombra (sem tarja, sem borrão). Para cada slide escolha `pos`:
- `"top"` quando os rostos estão na metade de baixo; `"bottom"` quando os rostos estão em cima.
`fx` (0–1) desloca o recorte horizontal para centralizar o personagem. Faixas pretas de print são cortadas sozinhas.

## 4. Montar
Escreva `posts/$DATE/spec.json` (formato no topo de `tools/build.py`) e rode:
```bash
.venv/bin/python tools/build.py posts/$DATE
```
Abra `posts/$DATE/preview.jpg` com Read e confira **todos** os slides:
- texto não pode ficar em cima do rosto do personagem → troque `pos` (top/bottom) ou ajuste `fx`;
- nada de imagem borrada, cortada de forma estranha, com marca d'água ou texto da imagem;
- o texto deve ter no máximo 5 linhas e ficar legível; se o fundo atrás for muito claro e confuso, troque `pos` ou a imagem.
Corrija e rode de novo até ficar bom (no máximo 4 tentativas; se uma imagem não presta, troque-a).

## 5. Publicar
```bash
rm -rf posts/$DATE/work posts/$DATE/search
git add posts/$DATE && git commit -m "post $DATE" && git push origin main
sleep 20
python3 tools/publish.py posts/$DATE --dry-run && python3 tools/publish.py posts/$DATE
```
Depois:
1. atualize `history.json` com `{"date", "theme", "characters", "permalink"}`;
2. acrescente em `runs.json`: `{"data": "$DATE", "quando": "DD/MM/AAAA HH:MM", "status": "ok", "mensagem": "<tema>", "link": "<permalink>"}`;
3. coloque `"theme": "<tema>"` no `spec.json` do post;
4. rode `python3 tools/dashboard.py` (atualiza o painel em `docs/`);
5. `git add -A && git commit -m "painel $DATE" && git push origin main`.

## Se algo der errado
**Sempre** registre a execução, mesmo com erro: acrescente em `runs.json`
`{"data": "$DATE", "quando": "...", "status": "erro" | "pulado", "mensagem": "<motivo curto>"}`,
rode `python3 tools/dashboard.py`, faça commit e push. O dono acompanha tudo pelo painel.

- Erro 190 / token inválido ou expirado da API (graph.facebook.com): não tente contornar. Termine relatando
  "TOKEN EXPIRADO — gere um novo token no painel da Meta e atualize o segredo do ambiente".
- Pinterest fora do ar: tente de novo em 2 min; se continuar, relate e pare (não publique nada improvisado).
- Nunca publique duas vezes no mesmo dia. Nunca publique conteúdo que você não conferiu no preview.
