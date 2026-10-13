#!/usr/bin/env bash
set -euo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo="$(dirname -- "$(dirname -- "$(dirname -- "$here")")")"
export PATH="/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:$PATH"
exec /disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python "$repo/corpus-work/scripts/prepared_delivery.py" compile-job "$@"
