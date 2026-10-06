#!/usr/bin/env bash
set -euo pipefail
CORPUS_PYTHON="${1:-python3}"
CORPUS_REPO="$(cd -- "$(dirname -- "$0")/.." && pwd)"
export PYTHONDONTWRITEBYTECODE=1
export CORPUS_TEST_ROOT="${CORPUS_TEST_ROOT:-$CORPUS_REPO/.checks/delivery-reuse}"
mkdir -p -- "$CORPUS_TEST_ROOT"
"$CORPUS_PYTHON" -B "$CORPUS_REPO/corpus-work/scripts/corpus_delivery_tools.py" --help
"$CORPUS_PYTHON" -B -m unittest discover -s "$CORPUS_REPO/corpus-work/tests" -p test_corpus_delivery_tools.py -v
if [ -f "$CORPUS_REPO/corpus-work/tests/test_merge_editable_batch.py" ]; then
  "$CORPUS_PYTHON" -B -m unittest discover -s "$CORPUS_REPO/corpus-work/tests" -p test_merge_editable_batch.py -v
fi
