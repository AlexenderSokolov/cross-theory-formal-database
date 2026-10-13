#!/usr/bin/env bash
set -euo pipefail
O="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
P="$(dirname "$O")"
W="$(dirname "$(dirname "$P")")"
export PATH=/disks/sata1/yupeng/human-proof-corpus/runtime/texlive/2025/bin/x86_64-linux:$PATH
# Optional native BibLaTeX backend; all runtime and PAR cache files stay in this line.
if [[ -x "$P/.work/biber-2.21/bin/biber" ]]; then
  export PATH="$P/.work/biber-2.21/bin:$PATH"
  export TMPDIR="$P/.work/biber-2.21/tmp"
  export PAR_GLOBAL_TMPDIR="$TMPDIR"
  mkdir -p -- "$TMPDIR"
fi
exec /disks/sata1/yupeng/human-proof-corpus/runtime/python/bin/python "$O/compile_material.py" "$@"
