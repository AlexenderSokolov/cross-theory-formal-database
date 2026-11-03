#!/usr/bin/env bash
set -u
set -o pipefail
export PATH=/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:$PATH
cd -- "$(dirname -- "$0")"
mkdir -p logs renders
stamp=$(date -u +%Y%m%dT%H%M%SZ)
log="logs/latexmk-${stamp}.log"
latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error -synctex=1 reader.tex 2>&1 | tee "$log"
status=${PIPESTATUS[0]}
printf '%s\n' "$status" > "logs/latexmk-${stamp}.exit-code.txt"
if [ "$status" -ne 0 ]; then
  exit "$status"
fi
pdfinfo reader.pdf > "logs/pdfinfo-${stamp}.txt"
pdftoppm -png -r 120 reader.pdf renders/reader
