#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:$PATH"
PY=/disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python
"$PY" test_svg_object.py
"$PY" repair_svg_objects.py stifled-lifting-forgetful-parity-trees boundary-expansion-kdnf-resolution parity-discrepancy-direct-sum parity-product-distribution-direct-sum gln-dnf-separating-distribution
