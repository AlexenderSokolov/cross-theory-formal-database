#!/usr/bin/env bash
set -euo pipefail
cd /disks/sata1/yupeng/human-proof-corpus/operations/corpus-maintenance-20261015-01a13ff0/processing/independent/claude-books/works/etingof-tensor-categories-author-copy/candidates/2_8_5/reader
export PATH=/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:"$PATH"
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error main.tex 2>&1 | tee compile.stdout.log
/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python - <<'PYRENDER' 2>&1 | tee render.stdout.log
import json
from pathlib import Path
import fitz
pdf=fitz.open('main.pdf')
out=Path('rendered');out.mkdir(exist_ok=True)
items=[]
for n,page in enumerate(pdf,1):
    target=out/f'page-{n:02d}.png'
    page.get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False).save(target)
    items.append({'page':n,'path':str(target),'width_points':page.rect.width,'height_points':page.rect.height})
print(json.dumps({'pdf':'main.pdf','page_count':len(pdf),'render_dpi':150,'all_rendered_pages':items},indent=2))
PYRENDER
