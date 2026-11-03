#!/usr/bin/env bash
set -euo pipefail
cd /disks/sata1/yupeng/human-proof-corpus/operations/corpus-maintenance-20261015-01a13ff0/processing/independent/claude-books/works/levin-peres-mcmt-second-edition/readers/6_21
export PATH=/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:$PATH
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error reader.tex 2>&1 | tee compile.stdout.log
/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python - <<'PY' | tee render.stdout.log
from pathlib import Path
import json
import pymupdf
root=Path.cwd()
out=root/'rendered'
out.mkdir(exist_ok=True)
doc=pymupdf.open(root/'reader.pdf')
files=[]
for n,page in enumerate(doc,1):
    name=out/f'page-{n:02d}.png'
    page.get_pixmap(matrix=pymupdf.Matrix(150/72,150/72)).save(name)
    files.append(str(name.relative_to(root)))
print(json.dumps({'pdf_pages':len(doc),'dpi':150,'rendered':files}))
PY
