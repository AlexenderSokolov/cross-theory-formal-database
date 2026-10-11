#!/usr/bin/env bash
# Existing Python, XeLaTeX, BibTeX/biber and Poppler must be on PATH.
# No installs, source fetching, cleanup, scheduler, or implicit publication.
set -euo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
task_root="$(cd -- "$here/.." && pwd)"
repo_root="$(cd -- "$task_root/../.." && pwd)"
python_bin="${PYTHON:-python3}"
mode="${1:?usage: run_prepared.sh validate-task|assemble|adopt-material|compile-job|qa|verify-job|migrate-db|verify-db|reserve|prepare|resume-prepare|begin-relay|relay|publish|restore [arguments]}"
shift
case "$mode" in
  validate-task|assemble)
    exec "$python_bin" "$repo_root/corpus-work/scripts/prepared_delivery.py" "$mode" --task-root "$task_root" "$@" ;;
  adopt-material|compile-job|qa|verify-job|migrate-db|verify-db)
    exec "$python_bin" "$repo_root/corpus-work/scripts/prepared_delivery.py" "$mode" "$@" ;;
  reserve|prepare|resume-prepare|begin-relay|publish|restore)
    exec "$python_bin" "$repo_root/corpus-work/scripts/prepared_publish.py" "$mode" "$@" ;;
  relay)
    exec "$python_bin" "$repo_root/corpus-work/scripts/prepared_remote.py" "$@" ;;
  *) printf 'Unknown prepared operation: %s\n' "$mode" >&2; exit 2 ;;
esac
