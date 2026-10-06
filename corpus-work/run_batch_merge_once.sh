#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "${CORPUS_PYTHON:-/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python}" -B "$script_dir/scripts/merge_editable_batch.py" --spec "$1" --semantic-review "$2" --output "$3"
