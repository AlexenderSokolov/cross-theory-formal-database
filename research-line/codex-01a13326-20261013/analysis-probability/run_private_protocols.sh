#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY=/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python
"$PY" prepare_drops_assets.py icalp2026-79
"$PY" normalize_private_protocol_labels.py
"$PY" prepare_private_protocols.py
