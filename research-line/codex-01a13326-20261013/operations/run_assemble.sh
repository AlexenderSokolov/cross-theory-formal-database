#!/usr/bin/env bash
set -euo pipefail
here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
task_root="$(dirname -- "$here")"
repo="$(dirname -- "$(dirname -- "$task_root")")"
export PATH="/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:$PATH"
exec /disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python "$repo/corpus-work/scripts/prepared_delivery.py" assemble --task-root "$task_root" --output-root "$task_root/jobs" --material-only "$@"
