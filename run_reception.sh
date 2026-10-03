#!/usr/bin/env bash
set -euo pipefail
umask 022
CORPUS_ROOT="${HUMAN_PROOF_ROOT:-/disks/sata1/yupeng/human-proof-corpus}"
REPO="$CORPUS_ROOT/repo"
PYTHON="$CORPUS_ROOT/runtime/python/bin/python"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$CORPUS_ROOT/reports/reception-rerun-$STAMP"
mkdir -p "$OUT"
cd "$REPO"
(cd handoff && sha256sum -c SHA256SUMS) > "$OUT/handoff-sha256.txt"
"$PYTHON" editable-corpus/restore_database.py > "$OUT/restore-database.txt"
"$PYTHON" editable-corpus/test_restore_database.py > "$OUT/test-restore.txt" 2>&1
"$PYTHON" editable-corpus/test_chunk_restore_database.py > "$OUT/test-chunks.txt" 2>&1
"$PYTHON" editable-corpus/test_database.py > "$OUT/test-database.txt" 2>&1
echo "Reception checks saved: $OUT"
echo "Pending40 and LOCAL1002 use their pinned, new-destination recovery commands; see handoff and reception receipt."
