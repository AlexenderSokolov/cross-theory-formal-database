#!/usr/bin/env bash
set -euo pipefail
corpus_work_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
corpus_project_root="$(dirname -- "$(dirname -- "$corpus_work_dir")")"
corpus_python="${CORPUS_PYTHON:-$corpus_project_root/runtime/python/bin/python}"
exec "$corpus_python" -B "$corpus_work_dir/scripts/sync_editable_projections.py" "$@"
