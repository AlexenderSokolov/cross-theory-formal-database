#!/usr/bin/env bash
set -euo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec /disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python "$here/export_materials.py" "$@"
