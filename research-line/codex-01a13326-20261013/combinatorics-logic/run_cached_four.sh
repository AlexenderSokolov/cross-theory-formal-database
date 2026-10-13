#!/usr/bin/env bash
set -euo pipefail
LANE=$(cd "$(dirname "$0")" && pwd)
/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python "$LANE/compile_cached_four.py" "$@"
