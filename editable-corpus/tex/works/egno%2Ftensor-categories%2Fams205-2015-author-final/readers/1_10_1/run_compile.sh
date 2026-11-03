#!/usr/bin/env bash
set -euo pipefail
cd /disks/sata1/yupeng/human-proof-corpus/operations/corpus-maintenance-20261015-01a13ff0/processing/independent/claude-books/works/etingof-tensor-categories-author-copy/readers/1_10_1
export PATH=/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:"$PATH"
latexmk -pdf -interaction=nonstopmode -halt-on-error reader.tex
