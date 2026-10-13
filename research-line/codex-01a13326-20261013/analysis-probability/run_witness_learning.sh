#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY=/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python
"$PY" prepare_drops_assets.py ccc2025-34
"$PY" prepare_witness_learning.py
