#!/usr/bin/env bash
set -euo pipefail
cd "/home/mainstainee/workspaces/human-proof-corpus/operations/corpus-maintenance-20261015-01a13ff0/processing/independent/claude-books/works/stanley-ch7-supp-20230604/supplements/arxiv-0807.0383v3/editorial"
latexmk -xelatex -interaction=nonstopmode -halt-on-error stanley-ex088.tex
