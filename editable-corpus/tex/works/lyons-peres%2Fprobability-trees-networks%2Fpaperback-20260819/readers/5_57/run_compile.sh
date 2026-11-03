#!/usr/bin/env bash
set -euo pipefail
cd /disks/sata1/yupeng/human-proof-corpus/operations/corpus-maintenance-20261015-01a13ff0/processing/independent/claude-books/works/lyons-peres-prbtree-20260819/readers/5_57
export PATH=/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:"$PATH"
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error reader.tex 2>&1 | tee compile.stdout.log
/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python - <<'PYRENDER' 2>&1 | tee render.stdout.log
from pathlib import Path
import json
import pymupdf
pdf=pymupdf.open('reader.pdf');out=Path('rendered');out.mkdir(exist_ok=True);items=[]
for n,page in enumerate(pdf,1):
    p=out/f'page-{n:02d}.png';page.get_pixmap(matrix=pymupdf.Matrix(150/72,150/72),alpha=False).save(p)
    items.append({'page':n,'path':str(p)})
print(json.dumps({'pdf':'reader.pdf','page_count':len(pdf),'dpi':150,'all_pages':items},indent=2))
PYRENDER
