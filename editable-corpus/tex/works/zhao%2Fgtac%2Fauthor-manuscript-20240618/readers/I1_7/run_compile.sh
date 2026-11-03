#!/usr/bin/env bash
set -euo pipefail
cd /home/mainstainee/workspaces/human-proof-corpus/operations/corpus-maintenance-20261015-01a13ff0/processing/independent/claude-books/works/zhao-gtac-author-manuscript/readers/I1_7
exec /home/mainstainee/workspaces/human-proof-corpus/.migration/env/run_in_env.sh \
  latexmk -pdf -interaction=nonstopmode -halt-on-error reader.tex
