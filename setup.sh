#!/usr/bin/env bash
# Prepara o ambiente: venv com ncnn (upscale) e modelos Real-ESRGAN.
# Idempotente: pode rodar toda vez.
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
  .venv/bin/pip -q install ncnn pillow numpy "rembg[cpu]"
fi
if [ ! -f models/realesr-animevideov3-x4.param ]; then
  mkdir -p models
  tmp=$(mktemp -d)
  curl -sL -m 180 -o "$tmp/z.zip" https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-ubuntu.zip
  .venv/bin/python - "$tmp/z.zip" <<'EOF'
import sys, zipfile, os
z = zipfile.ZipFile(sys.argv[1])
for n in z.namelist():
    if n.startswith('models/') and n.endswith(('.param', '.bin')):
        open(os.path.join('models', os.path.basename(n)), 'wb').write(z.read(n))
EOF
  rm -rf "$tmp"
fi
node -e "require('playwright')" && echo "setup ok"
