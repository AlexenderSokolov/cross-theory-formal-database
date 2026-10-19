#!/usr/bin/env bash
# Reproduce only the public reading projections; no admission, build or publish.
set -euo pipefail
cd "$(dirname "$0")"
PYTHON="${PYTHON:-python3}"
case "${1:-check}" in
  generate) "$PYTHON" -B editable-corpus/reader_catalog.py ;;
  check) "$PYTHON" -B editable-corpus/reader_catalog.py --check ;;
  links) "$PYTHON" -B editable-corpus/reader_catalog.py --check --check-links ;;
  test) "$PYTHON" -B -m unittest discover -s corpus-work/tests -p 'test_reader_catalog.py' -v ;;
  *) echo 'Usage: bash run_reader_catalog.sh [generate|check|links|test]' >&2; exit 2 ;;
esac
