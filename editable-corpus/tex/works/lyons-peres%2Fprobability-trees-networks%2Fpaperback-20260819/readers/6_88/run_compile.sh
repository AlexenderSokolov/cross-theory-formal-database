#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
ENV=/home/mainstainee/workspaces/human-proof-corpus/.migration/env/run_in_env.sh
mkdir -p logs render
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
log="logs/latexmk-$stamp.log"
set +e
"$ENV" latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error reader.tex >"$log" 2>&1
code=$?
set -e
printf '%s\n' "$code" >"logs/latexmk-$stamp.exit-code"
cat "$log"
if [ "$code" -ne 0 ]; then exit "$code"; fi
"$ENV" python -B - <<'PY_RENDER'
from pathlib import Path
import pymupdf, json
d = pymupdf.open('reader.pdf')
for n, p in enumerate(d, 1):
    p.get_pixmap(matrix=pymupdf.Matrix(150/72, 150/72)).save('render/reader-%02d.png' % n)
print(json.dumps({'pages': len(d), 'bytes': Path('reader.pdf').stat().st_size,
                  'render_dpi': 150, 'actual_page_inspection': 'not established by rendering'}))
PY_RENDER
