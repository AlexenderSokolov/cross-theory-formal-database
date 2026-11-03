#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export PATH="/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:$PATH"
mkdir -p logs render
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
log="logs/latexmk-$stamp.log"
set +e
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error reader.tex >"$log" 2>&1
code=$?
set -e
printf '%s\n' "$code" >"logs/latexmk-$stamp.exit-code"
cat "$log"
if [ "$code" -ne 0 ]; then exit "$code"; fi
/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python - <<'PY_RENDER'
from pathlib import Path
import pymupdf,json
d=pymupdf.open('reader.pdf')
for n,p in enumerate(d,1):
    p.get_pixmap(matrix=pymupdf.Matrix(150/72,150/72)).save(f'render/reader-{n:02d}.png')
print(json.dumps({'pages':len(d),'bytes':Path('reader.pdf').stat().st_size,'render_dpi':150,'actual_page_inspection':'not established by rendering'}))
PY_RENDER
