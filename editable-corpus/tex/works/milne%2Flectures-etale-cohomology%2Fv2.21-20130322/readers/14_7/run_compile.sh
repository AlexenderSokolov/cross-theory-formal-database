#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export PATH="/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:$PATH"
mkdir -p logs render
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
log="logs/latexmk-${stamp}.log"
set +e
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error reader.tex >"$log" 2>&1
code=$?
set -e
printf '%s\n' "$code" >"logs/latexmk-${stamp}.exit-code"
cat "$log"
if [ "$code" -ne 0 ]; then exit "$code"; fi
/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python - <<'PY_RENDER'
from pathlib import Path
import json,pymupdf
p=Path('reader.pdf')
d=pymupdf.open(p)
for n,page in enumerate(d,1):
    page.get_pixmap(matrix=pymupdf.Matrix(150/72,150/72)).save(f'render/reader-{n:02d}.png')
print(json.dumps({'pdf_pages':len(d),'pdf_bytes':p.stat().st_size,'render_dpi':150,'rendered_pages':list(range(1,len(d)+1)),'actual_visual_review':'not established by rendering; writer must inspect each page'}))
PY_RENDER
