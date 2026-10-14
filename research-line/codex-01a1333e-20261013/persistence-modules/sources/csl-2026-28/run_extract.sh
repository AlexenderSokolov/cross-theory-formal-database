#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python convert_publisher_html.py
