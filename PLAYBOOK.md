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
**FLUXO "UM DIA ANTES" (regra do dono):** o post de cada dia é preparado no dia anterior, mostrado ao dono na conversa
e só publicado no dia seguinte, para ele pedir alterações antes.
- Se `posts/$DATE/published.json` já existe, o post de hoje já saiu: pule para a etapa 6.
- Se `posts/$DATE/spec.json` existe e os `slide_*.jpg` estão lá (rascunho feito ontem), **publique esse post sem refazer nada**
  (etapa 5), a menos que o spec tenha `"segurar": true` (então NÃO publique: avise o dono e pule para a etapa 6).
  O dono pode ter mandado alterações: elas já foram aplicadas no rascunho antes deste horário.
- Se não existe rascunho, crie o post do zero (etapas 1 a 4) e publique.
- Depois de publicar, faça a **etapa 6: preparar o post de AMANHÃ**.

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

## 2. VARIE O FORMATO (regra do dono: não repetir "Você ... quando..." todo dia)
O gancho "Você **sabe que...** quando..." é só UM dos formatos. Antes de escrever, olhe `history.json` (campo `formato`)
e escolha um formato DIFERENTE dos 2 últimos posts. "Você ... quando" no máximo 1 vez por semana. Nunca comece
dois posts seguidos com a mesma palavra no gancho. Formatos (todos usam o mesmo layout/estilo do build; muda o texto):
1. **lista** — capa: `kicker` curto + `head` tipo "5 animes para ver quando precisar **chorar**". Slides: `kicker` = "1. Nome do anime"
   (em cada slide, diferente), `head` = 1 frase sobre por que vale. Último: pergunta "qual faltou?".
2. **personagem** — cada slide é um personagem: `kicker` = "o que o **Nome** ensinou sobre ..." e `head` = a lição, curta.
3. **pergunta** — `head` são perguntas que o leitor se faz ("e se você já for **suficiente**?"), sem kicker; o fecho responde.
4. **carta** — "Carta para quem está ...": slides são frases diretas, em sequência, como uma carta (kicker só no primeiro).
5. **frase** — uma frase marcante de personagem (parafraseada, nunca copiada literal) por slide, `kicker` = nome do personagem.
6. **serie** — "Você ... quando..." (limitado a 1 por semana).
Em cada formato o último slide fecha com virada + "Siga @darkgoodvibes". Registre o formato usado em `history.json` (`"formato"`).
Mude também o comprimento: posts de 5, 6, 7 ou 8 slides.

## 2-quater. VARIE O VISUAL ENTRE POSTS (regra do dono: "não é porque um ficou bom que é pra manter todos assim")
Cada post tem um visual PRÓPRIO. Nunca repita o mesmo visual em posts seguidos.
- **Tema visual** (`"tema"` no `spec.json`): `noir` (preto/amarelo, Anton), `sakura` (rosa, Bebas + Cormorant), `oceano` (azul, Archivo Black),
  `ocaso` (laranja, Bebas), `floresta` (verde, Archivo Black + Cormorant), `mono` (preto e branco, Anton + Cormorant).
  Ele troca paleta, fontes e a tonalidade das imagens. **Escolha um tema diferente dos 3 últimos posts** (veja `"tema"` em `history.json`)
  e combine com o assunto (ex.: descanso → oceano/floresta; saudade → ocaso/mono; amor/amizade → sakura; disciplina → noir/mono).
  Domingo cristão: `mono` ou `ocaso`.
- **Combinação de layouts diferente** da dos últimos 2 posts: a capa não pode ter o mesmo layout das 3 últimas capas, e o fechamento
  não precisa ser sempre `frase`. Alterne também a ordem (às vezes comece por `painel`, `quadro` ou `serie`).
- **Quantidade de slides** diferente (5 a 8) e **posição do texto** variando entre `top` e `bottom`.
- Registre `"tema"` e a lista de layouts usados em `history.json` ao publicar.

## 2-ter. LAYOUTS VARIADOS (pedido do dono: nada de moldura/enfeite igual em todos os slides)
Cada slide escolhe um `"layout"` no spec. **Misture pelo menos 3 layouts diferentes por post** e nunca use o mesmo
layout em mais de 2 slides seguidos. A moldura de cantos (`"moldura": true`) só pode aparecer em NO MÁXIMO 1 slide por post.
- `"fantasma"`: imagem inteira + **palavra gigante atrás do personagem** (`"word": "saudade"`, `"outline": true` deixa só
  o contorno, `"wcolor"` muda a cor, `"wk"` 0.6–0.9 = quanto da palavra fica ACIMA da cabeça: maior = mais legível; `"dim"` escurece o fundo, `"headroom": 230` abre espaço de cor em cima da imagem para a palavra ficar acima da cabeça — USE SEMPRE no layout fantasma). A palavra precisa ficar LEGÍVEL: se a cabeça esconder mais de 1 letra, aumente `wk` ou troque a imagem (prefira personagem que não ocupa a imagem toda). O personagem recortado passa NA FRENTE das letras. Legenda embaixo
  (`tag`, `head`, `body`; `"pos": "top"` leva para cima). Use em capas e em imagens com personagem grande no centro.
- `"painel"`: página de **revista/papel** (fundo creme): título condensado em caixa alta (`head`, palavra em `**negrito**`
  fica vermelha), **imagem pequena emoldurada** inclinada (`src`; `fy`/`fx` ajustam o recorte), opcionalmente uma
  **segunda imagem menor** sobreposta (`src2`) e parágrafo serifado justificado (`body`, ~30 a 40 palavras).
- `"quadro"`: imagem inteira + **foto emoldurada (polaroid) sobreposta** num canto (`"side": "left"|"right"`). Sem `src2`, a
  polaroid é um zoom no próprio frame (`zoom`, `zx`, `zy` escolhem o detalhe: olhos, mãos, objeto). Legenda embaixo.
- `"frase"`: imagem escurecida + **aspas gigantes** e frase em serifa itálica (`text`, `autor`). Use no fechamento.
- sem `layout` (ou `"serie"`): o estilo atual com gancho (`kicker`) + frase gigante + `body`. Texto sempre legível (já tem degradê).
Enfeites tipográficos usam fontes diferentes de propósito: Anton (condensada), Playfair (serifa itálica) e Poppins.
Ao escolher imagens para `fantasma`, prefira personagem grande e nítido (o recorte automático precisa separá-lo do fundo).

## 2-bis. Regras de riqueza visual (pedido do dono: menos genérico, mais texto, mais "enfeite")
- **Imagem ESPECÍFICA, nunca genérica:** cada slide mostra o personagem/cena citada (ex.: Frieren diante da estátua do
  Himmel, Luffy segurando o Ace). Busque "<personagem> <anime> <cena> screenshot". Proibido usar wallpaper genérico
  de "garoto olhando o pôr do sol" ou arte de IA sem personagem reconhecível. Só use cena genérica na capa/fechamento.
- **Mais texto:** todo slide (menos a capa) tem `tag` + `head` + `body`.
  - `tag`: etiqueta curta em caixa alta com anime e personagem ("Naruto · Jiraiya"); na capa, "5 histórias sobre ...".
  - `head`: 4 a 7 palavras, com 1 trecho em `**negrito**`.
  - `body`: 2 frases (20 a 35 palavras) com 1 ou 2 trechos em `**negrito**` (viram amarelo).
- **Enfeite opcional** (`"moldura": true`, máx. 1 slide por post): moldura dupla, cantos amarelos, @ no topo, contador 01/07, bolinhas de
  progresso, setinha →, divisor amarelo e degradê escuro atrás do texto. Não use em todos os slides.
- **Posição do texto:** `"pos": "top"` quando o rosto está embaixo; **`"pos": "bottom"` quando o rosto/personagem
  está na parte de cima da imagem** (o degradê escuro acompanha). Nunca deixe o texto cobrir o rosto.
- Com `body`, o efeito de camadas (texto atrás do personagem) é desligado sozinho; sem `body` ele continua valendo.
- Confira no preview: texto legível sobre qualquer fundo (se o fundo for claro e confuso, troque a imagem ou `pos`).

## 2a. Formato dos slides (estilo atual: "serie", inspirado em @psico.tsu)
- Layout "serie" (kicker + head gigante). No formato 6 o `"kicker"` fica no spec e se repete em todos os slides; nos outros
  formatos defina `kicker` slide a slide (ou nenhum). Exemplo do formato 6:
  "Você **sabe que perdeu** quando...", "Você **sabe que está crescendo** quando...", "Sinais de que **você está se curando**...".
  Use `**negrito**` em 2–4 palavras do meio do gancho (o resto sai em letra fina).
- Cada slide tem uma `"head"`: frase curta (3 a 7 palavras), minúscula, que completa o gancho e termina com ponto.
- Último slide: `"no_kicker": true`, `head` de virada ("mas você ainda não perdeu", "e se você tem alguém assim,")
  e `"body"` com 1–2 parágrafos curtos (use `**negrito**` em trechos) + "**Siga @darkgoodvibes** ...". Separe parágrafos com linha em branco (\n\n).
- **Referência aprovada pelo dono:** slide do Zoro amarrado no poste com o Luffy — texto LÁ EM CIMA, muito céu livre,
  e só um pedacinho do objeto/personagem passando na frente da última linha. **Reprovado:** texto descido para o meio
  da imagem, com céu vazio em cima; ou cabeça cobrindo metade de uma palavra.
- Todos os slides com `"pos": "top"`. O texto vai **atrás do personagem**: o build recorta o personagem e posiciona
  o texto sozinho no alto (entre 110 e 300 px do topo) e só ativa a camada se o personagem cobrir de 3% a 12% da
  última linha e nada das outras; senão o texto fica na frente.
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

## 6. Preparar o post de AMANHÃ (1 dia antes) e mostrar ao dono
Depois de publicar o de hoje (ou de decidir segurar), prepare o de amanhã:
```bash
TOM=$(TZ=America/Sao_Paulo date -d "+1 day" +%F); mkdir -p posts/$TOM
```
1. Repita as etapas 1 a 4 para a data `$TOM` (tema = primeiro item da `fila`; **domingo é cristão** — confira o dia da semana
   de `$TOM`; formato e layouts diferentes dos posts recentes). Remova o item usado da `fila` e reponha a fila.
2. Salve `"pronto": true` e `"theme"`/`"formato"` no `spec.json`, apague `work/` e `search/`, faça commit e push
   (`git add -A && git commit -m "rascunho $TOM" && git push origin main`). NÃO publique no Instagram.
3. **Envie ao dono, na conversa** (ferramenta SendUserFile): todos os `slide_*.jpg` de `$TOM` + `caption.txt`, com uma mensagem curta:
   tema, formato, e "sai amanhã às 19h; se quiser mudar algo, me avise antes".
4. Registre em `runs.json` uma linha de status `"rascunho"` para `$TOM`, rode `python3 tools/dashboard.py`, commit e push.
Se o dono pedir alterações (na conversa), aplique no `spec.json` de `$TOM`, rode `tools/build.py` de novo, mostre de novo e faça commit/push.
Se ele pedir para segurar, ponha `"segurar": true` no spec.

## Se algo der errado
**Sempre** registre a execução, mesmo com erro: acrescente em `runs.json`
`{"data": "$DATE", "quando": "...", "status": "erro" | "pulado", "mensagem": "<motivo curto>"}`,
rode `python3 tools/dashboard.py`, faça commit e push. O dono acompanha tudo pelo painel.

- Erro 190 / token inválido ou expirado da API (graph.facebook.com): não tente contornar. Termine relatando
  "TOKEN EXPIRADO — gere um novo token no painel da Meta e atualize o segredo do ambiente".
- Pinterest fora do ar: tente de novo em 2 min; se continuar, relate e pare (não publique nada improvisado).
- Nunca publique duas vezes no mesmo dia. Nunca publique conteúdo que você não conferiu no preview.
