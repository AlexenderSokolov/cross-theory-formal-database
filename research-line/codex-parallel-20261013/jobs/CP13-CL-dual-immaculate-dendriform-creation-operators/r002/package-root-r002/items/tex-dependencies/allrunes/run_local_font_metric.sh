#!/usr/bin/env bash
set -euo pipefail
export PATH="/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:$PATH"
export MFINPUTS="/disks/sata1/yupeng/human-proof-corpus/operations/codex-parallel-work-20261013/research-line/codex-parallel-20261013/combinatorics-logic/tex-dependencies/allrunes/fonts/source/public/allrunes//:"
cd "/disks/sata1/yupeng/human-proof-corpus/operations/codex-parallel-work-20261013/research-line/codex-parallel-20261013/combinatorics-logic/tex-dependencies/allrunes/generated"
mf -interaction=nonstopmode '\mode:=ljfour; input frummn;'
