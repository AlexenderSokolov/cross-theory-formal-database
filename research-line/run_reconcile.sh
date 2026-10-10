#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python -m unittest discover -s corpus-work/scripts/tests -p test_reconcile_research_line.py
python corpus-work/scripts/reconcile_research_line.py
