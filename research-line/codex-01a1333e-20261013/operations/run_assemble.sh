#!/usr/bin/env bash
set -euo pipefail
O="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
P="$(dirname "$O")"
W="$(dirname "$(dirname "$P")")"
export PATH=/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:$PATH
exec /disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python "$W/corpus-work/scripts/prepared_delivery.py" assemble --task-root "$P" --output-root "$P/jobs" --material-only "$@"
