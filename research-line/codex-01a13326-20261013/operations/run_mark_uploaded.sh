#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
exec /disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python mark_uploaded.py "$@"
