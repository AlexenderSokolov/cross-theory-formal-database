#!/usr/bin/env bash
set -euo pipefail
umask 022
CORPUS_ROOT="${HUMAN_PROOF_ROOT:-/disks/sata1/yupeng/human-proof-corpus}"
exec "$CORPUS_ROOT/runtime/bin/compile-isolated" "$@"
