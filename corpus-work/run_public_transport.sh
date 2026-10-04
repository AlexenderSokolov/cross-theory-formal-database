#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "${CORPUS_PYTHON:-/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python}" -B "$script_dir/scripts/prepare_public_transport.py" "$@"
