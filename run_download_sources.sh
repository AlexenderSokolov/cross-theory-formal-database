#!/usr/bin/env bash
set -euo pipefail
ROOT="${HUMAN_PROOF_ROOT:-/disks/sata1/yupeng/human-proof-corpus}"
# Acquisition only. The downloader explicitly ignores inherited proxy variables.
# Existing receipts and exact CAS files are reused; interrupted incoming files
# are preserved. Extraction requires a separately completed source batch.
exec "$ROOT/runtime/python/bin/python" "$ROOT/repo/corpus-work/scripts/download_catalog_sources.py" --workers "${DOWNLOAD_WORKERS:-16}" "$@"
