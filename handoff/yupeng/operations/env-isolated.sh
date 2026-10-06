#!/usr/bin/env bash
set -euo pipefail
root=/disks/sata1/yupeng/human-proof-corpus
exec "$root/runtime/python/bin/python" "$root/operations/env-isolated.py" "$@"
