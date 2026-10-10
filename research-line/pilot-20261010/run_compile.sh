#!/usr/bin/env bash
set -euo pipefail
pilot_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd -- "$pilot_dir/../.." && pwd)"
python_exe="${PYTHON_EXE:-python}"
export PYTHONUTF8=1
# Local cached author sources only. No download, remote write, admission or publish.
# Existing latexmk_xelatex.cmd invokes latexmk -xelatex -g for real engine passes.
"$python_exe" "$repo_dir/corpus-work/scripts/build_research_pilot.py" \
  --source "${STACKS_SOURCE:?Set STACKS_SOURCE to the complete local Stacks snapshot}" \
  --work "${PILOT_WORK:?Set PILOT_WORK outside the repository for build and receipts}" \
  "$@"
