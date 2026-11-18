# Carrosséis automáticos de anime

Todo dia uma sessão automática do Claude segue o [PLAYBOOK.md](PLAYBOOK.md):
escolhe um tema, escreve os slides e a legenda, busca imagens no Pinterest,
faz upscale (Real-ESRGAN), monta o carrossel no estilo minimalista (V4) e publica
no Instagram pela API oficial.

## Estrutura
- `tools/pinsearch.py`: busca imagens no Pinterest e gera folha de contato
- `tools/build.py`: `spec.json` → slides 1080×1350 + preview
- `tools/upscale.py`: upscale com ncnn/Real-ESRGAN (CPU)
- `tools/publish.py`: publica o carrossel (Graph API, conta @darkgoodvibes ligada à Página Darkgood Vibes)
- `posts/AAAA-MM-DD/`: cada post (spec, slides, legenda, link publicado)
- `history.json`: temas e personagens já usados

## Token
O token do Instagram **não** fica neste repositório: ele é guardado como segredo
do ambiente de nuvem do Claude e injetado nas chamadas a `graph.facebook.com`.
Tokens de longa duração valem cerca de 60 dias. Quando expirar, gere outro no painel
da Meta e atualize o segredo.
