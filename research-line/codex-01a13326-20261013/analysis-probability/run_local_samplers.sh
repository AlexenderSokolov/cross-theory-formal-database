#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY=/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python
"$PY" prepare_drops_assets.py icalp2026-109
"$PY" prepare_local_samplers.py
