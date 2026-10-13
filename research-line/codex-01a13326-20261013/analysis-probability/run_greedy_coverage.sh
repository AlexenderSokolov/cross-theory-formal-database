#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY=/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python
"$PY" prepare_drops_assets.py arxiv2604-24884v1
"$PY" prepare_greedy_coverage.py
