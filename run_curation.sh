#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ -n "${PYTHON:-}" ]]; then
  PYTHON_BIN="$PYTHON"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN=python
else
  PYTHON_BIN=python3
fi
"$PYTHON_BIN" -m unittest discover -s corpus-work/scripts/tests -p test_refresh_catalog.py
"$PYTHON_BIN" -m unittest discover -s corpus-work/scripts/tests -p test_reconcile_research_line.py
"$PYTHON_BIN" -m unittest discover -s corpus-work/scripts/tests -p test_windows_restore_database.py
"$PYTHON_BIN" corpus-work/scripts/reconcile_research_line.py
"$PYTHON_BIN" corpus-work/scripts/refresh_catalog.py
"$PYTHON_BIN" corpus-work/scripts/refresh_catalog.py --check
