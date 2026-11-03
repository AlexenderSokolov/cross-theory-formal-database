#!/usr/bin/env bash
set -euo pipefail
export PATH=/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:$PATH
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error reader.tex
